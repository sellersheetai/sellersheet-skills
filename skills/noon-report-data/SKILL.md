---
name: noon-report-data
description: Use when working with noon.com (noon Partners) report data that SellerSheet ingests on a schedule — querying noon orders, finance/transactions, FBN inventory aging, or product-views & sales for a connected noon store. Covers the 4 rpt_noon_* warehouse tables, their schedules, grain, and the query nuances (project-scoped, marketplace semantics, snapshot vs incremental).
version: 0.7.0
---

# noon Report Data

SellerSheet's reporting server ingests four noon Export-API reports on a
twice-daily schedule into warehouse tables (`rpt_noon_*`) you query with the **same
`query_report_data` MCP tool** you use for Amazon — just point it at a noon
store and a `rpt_noon_*` table.

## Prerequisites

1. **`get_user_context`** must work (SellerSheet MCP connected). If not, surface
   the setup steps and stop.
2. **A connected noon account.** noon data is keyed to a noon *project*, not an
   Amazon store. The user must have connected a noon account on the dashboard
   (noon section → Connect noon). If `query_report_data` on a `rpt_noon_*` table
   returns *"No connected noon account found"*, tell them to connect one first.

## How noon querying differs from Amazon

| | Amazon `rpt_*` | noon `rpt_noon_*` |
|---|---|---|
| Scope key | `store_id` | `project_code` (resolved from the caller's connected noon accounts — you never pass it) |
| `store` arg | `myStore-AE` (Amazon store) | the **noon** store ref, e.g. `myStore-AE` (account name + CC). Bare name (`myStore`) or omitting it scopes to all your noon projects |
| Access | ownership/share | ownership only (no noon sharing yet) |

You do **not** pass `project_code` — the server resolves it from the `store` ref
against your connected noon accounts and scopes the query for you. Marketplace
filtering is **not** auto-injected for noon (unlike Amazon's `myStore-AE` suffix):
add an explicit filter on `marketplace` / `country_code` when you want one
marketplace (see per-table notes).

Tools: `get_table_schema(table_name)` for live columns; `query_report_data(...)`
to read. Single-table per call (use `joins` to add tables).

## Schedule (twice daily, marketplace-local; UTC cron on the reporting server)

| Table | Report | Cron (UTC) | Lookback | Mode |
|---|---|---|---|---|
| `rpt_noon_orders` | OMS orders export | `0 3,15 * * *` (03:00, 15:00) | 7d, full re-pull each fire | incremental (UPSERT) |
| `rpt_noon_finance` | Transaction view (item level) | `0 4,16 * * *` (04:00, 16:00) | 14d, full re-pull | incremental (UPSERT) |
| `rpt_noon_fbn_aging` | FBN inventory v2 aging | `0 6,18 * * *` (06:00, 18:00) | — | **snapshot** (one full picture per `snapshot_date`) |
| `rpt_noon_product_views` | Catalog product-views & sales | `0 8,20 * * *` (08:00, 20:00) | 14d, full re-pull | incremental (UPSERT) |

The 3 time-based reports re-pull their whole lookback window every run (so late
status/finance/analytics revisions are caught), then UPSERT — no duplicates.
FBN aging is a snapshot: each `snapshot_date` is a complete inventory picture,
and one pull carries ~a year of month-end snapshots. For "current stock" filter
to the **latest `snapshot_date`** (see the `report_date` section) — not `report_date`.

## `report_date` mode — ALWAYS use `'all'` for noon tables

For every noon table, pass **`report_date='all'`** and filter the real date
column yourself. Do **NOT** use `report_date='latest'` on noon tables — it keys
off the injected `report_date` (the *ingestion* stamp), which is the same for
every row in a pull and is **not** the data date you care about.

- **`rpt_noon_fbn_aging` (snapshot) — the trap:** one FBN pull returns **many
  historical `snapshot_date`s** (month-end snapshots going back a year), all
  written with the same `report_date`. So `report_date='latest'` returns **every
  snapshot at once** and summing it massively over-counts. For *current stock*
  you must pick the **latest `snapshot_date`** explicitly:
  1. Find it: query `rpt_noon_fbn_aging` with `aggregations:[{op:max,
     column:rpt_noon_fbn_aging.snapshot_date,alias:d}]`, `report_date='all'`
     (optionally filter `country_code`).
  2. Then filter `snapshot_date = <that value>` with `report_date='all'`.
  Never aggregate aging across snapshot_dates unless you explicitly want a
  time series.
- **orders / finance / product_views (incremental):** filter the **event date**
  (`order_placed_at` / `transaction_date` / `visit_date`) with `report_date='all'`.

---

## Tables

### `rpt_noon_orders` — order items (project-wide, all marketplaces in one report)
- **Grain:** one row per order item. **Key:** `project_code, marketplace, item_nr`.
- **Marketplace:** filter on **`market_place_country_code`** = `AE`/`SA`/`EG` (the `marketplace` column holds the same value — either works).
- **Event date:** `order_placed_at` (timestamptz). Use `report_date='all'` + a filter on `order_placed_at`.
- **Columns:** `id_partner`, `partner_name`, `market_place` (always `noon`), `order_nr`, `market_place_country_code`, `destination_country_code`, `item_nr`, `sku`, `warehouse_code`, `order_placed_at`, `min_expected_delivery_at`, `max_expected_delivery_at`, `item_status` (`delivered`/`shipped`/`cancelled`/…), `shipment_nr`, `awb_nr` (airway bill / tracking), `is_fulfilled_by_noon` (bool — FBN vs partner-fulfilled). Plus injected `project_code`, `marketplace`, `report_date`.

### `rpt_noon_finance` — finance transactions (item level; project-wide, all marketplaces in one report)
- **Grain:** one row per transaction line. **Key:** `project_code, reference_nr, item_nr, transaction_type`.
- **Marketplace:** the report is project-wide but each row carries its market in **`contract_title`** = `NOON-AE`/`NOON-SA`/`NOON-EG`. The `marketplace` column is derived from it (`NOON-AE` → `AE`), so filter `marketplace` = `AE`/`SA`/`EG` (or `contract_title` = `NOON-AE`). (`marketplace='ALL'` only appears on rows whose contract title couldn't be parsed.)
- **Event date:** `transaction_date` (date). `order_date` is also present (NULL for non-order transactions). Use `report_date='all'` + filter `transaction_date`.
- **Columns:** `contract`, `contract_title`, `reference_nr`, `order_nr`, `item_nr`, `order_date`, `transaction_date`, `title`, `skus`, `partner_skus`, `transaction_type` (`Sale`/`Refund`/`balance_transfer`/…), `currency`, and money fields **all VAT-inclusive** `numeric(16,2)`: `net_proceeds`, `referral_fee`, `fulfillment_logistics_fees`, `shipping_credits`, `other_order_fees`, `order_subsidies`, `non_order_fees`, `non_order_subsidies`, `others`, `total`. Sum `total` for net payout over a period.

### `rpt_noon_fbn_aging` — FBN inventory aging (SNAPSHOT; one report per marketplace)
- **Grain:** one row per `snapshot_date, country, sku, partner_barcode, condition, qc_fail`. **Key:** `project_code, snapshot_date, country_code, sku, partner_barcode, inventory_condition, qc_fail_item_identifier` (NULLS NOT DISTINCT).
- **`partner_barcode` is part of the key** — noon ships one row per barcode, so a single `sku` can have **multiple `partner_barcode`** rows, and `sku` can be **empty** while `partner_barcode='UNIDENTIFIED'`. Don't assume one row per sku; aggregate by sku (SUM the buckets) if you want a per-sku total.
- **`marketplace`** and **`country_code`** both = the CC (each marketplace is exported separately). Filter `country_code` for one market.
- **Current stock = the latest `snapshot_date` only.** Always `report_date='all'`; find MAX(`snapshot_date`) then filter to it (see the `report_date` section above). One pull contains ~a year of month-end snapshots, so summing without that filter over-counts ~10–20×.
- **Aging buckets:** `gross_quantity`, `quantity_0_30d`, `quantity_31_60d`, `quantity_61_90d`, `quantity_91_180d`, **`quantity_181_365d`** (single bucket — there is NO 181_270/271_365 split), `quantity_366d`. Also `partner_sku`, `partner_barcode`, `inventory_condition` (`sellable`/`UNSALEABLE`/…), `qc_fail_item_identifier`, `first_received_date`, `last_movement_date`. High `quantity_366d` / `quantity_181_365d` = aged stock at risk.

### `rpt_noon_product_views` — product views & sales (one report per marketplace)
- **Grain:** one row per `visit_date, sku, country`. **Key:** `project_code, visit_date, sku, country_code`.
- **`marketplace`** and **`country_code`** both = the CC (each marketplace is exported separately). Filter `country_code` for one market.
- **Event date:** `visit_date` (date). Use `report_date='all'` + filter `visit_date`.
- **Columns:** `partner_sku`, `mp_code`, `sku_config`, `sku`, `family`, `product_type`, `product_subtype`, `brand`, `currency_code`, `product_title`, `your_visitors`, `total_visitors`, `gross_units`, `shipped_units`, `cancelled_units`, `revenue_shipped`, `buy_box_visitor_percentage`, `conversion_visitors_percentage`, **`asp_shipped`**.
- **Gotchas:** `asp_shipped` is the **average selling PRICE** (currency amount), NOT a percent despite noon's source header. `conversion_visitors_percentage` can exceed 100 (noon's definition). Sales columns (`gross_units`/`shipped_units`/`revenue_shipped`) are sparse — many view-only rows.

---

## Example queries

Current FBN stock at risk (aged) in AE — **two steps**, latest snapshot only:
```json
// 1) find the latest snapshot_date
{ "store": "myStore-AE", "tables": ["rpt_noon_fbn_aging"],
  "columns": ["rpt_noon_fbn_aging.country_code"],
  "aggregations": [{"op":"max","column":"rpt_noon_fbn_aging.snapshot_date","alias":"latest"}],
  "filters": [{"column":"rpt_noon_fbn_aging.country_code","op":"eq","value":"AE"}],
  "report_date": "all" }
// 2) query that snapshot (e.g. latest = 2026-06-14)
{ "store": "myStore-AE", "tables": ["rpt_noon_fbn_aging"],
  "columns": ["rpt_noon_fbn_aging.sku","rpt_noon_fbn_aging.partner_barcode","rpt_noon_fbn_aging.gross_quantity","rpt_noon_fbn_aging.quantity_181_365d","rpt_noon_fbn_aging.quantity_366d"],
  "filters": [{"column":"rpt_noon_fbn_aging.country_code","op":"eq","value":"AE"},
              {"column":"rpt_noon_fbn_aging.snapshot_date","op":"eq","value":"2026-06-14"}],
  "report_date": "all",
  "order_by": [{"column":"rpt_noon_fbn_aging.quantity_366d","dir":"desc"}] }
```

Net payout last 14 days by marketplace (finance — slice via the derived `marketplace`):
```json
{ "store": "myStore", "tables": ["rpt_noon_finance"],
  "aggregations": [{"op":"sum","column":"rpt_noon_finance.total","alias":"net_total"}],
  "group_by": ["rpt_noon_finance.marketplace","rpt_noon_finance.currency"],
  "filters": [{"column":"rpt_noon_finance.transaction_date","op":"gte","value":"2026-06-01"}],
  "report_date": "all" }
```

Cancelled order items in SA this month:
```json
{ "store": "myStore-SA", "tables": ["rpt_noon_orders"],
  "columns": ["rpt_noon_orders.order_nr","rpt_noon_orders.sku","rpt_noon_orders.item_status","rpt_noon_orders.order_placed_at"],
  "filters": [{"column":"rpt_noon_orders.marketplace","op":"eq","value":"SA"},
              {"column":"rpt_noon_orders.item_status","op":"eq","value":"cancelled"},
              {"column":"rpt_noon_orders.order_placed_at","op":"gte","value":"2026-06-01"}],
  "report_date": "all" }
```

Top SKUs by visitors (product views) in AE for a date:
```json
{ "store": "myStore-AE", "tables": ["rpt_noon_product_views"],
  "columns": ["rpt_noon_product_views.sku","rpt_noon_product_views.your_visitors","rpt_noon_product_views.conversion_visitors_percentage","rpt_noon_product_views.asp_shipped"],
  "filters": [{"column":"rpt_noon_product_views.country_code","op":"eq","value":"AE"},
              {"column":"rpt_noon_product_views.visit_date","op":"eq","value":"2026-06-15"}],
  "report_date": "all",
  "order_by": [{"column":"rpt_noon_product_views.your_visitors","dir":"desc"}], "limit": 50 }
```

## Always relay
`query_report_data` returns `{notification, data:{columns,rows,total_count,…}, human_action}`. Relay `notification.message` and `human_action`. If a noon table returns `_no_data`, the ingestion may not have run yet for that project — check that the noon account is connected and at least one daily cycle has passed.

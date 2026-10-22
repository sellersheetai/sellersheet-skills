---
name: noon-report-data
description_zh: "noon 订单、noon 财务/交易明细、FBN 库存账龄、noon 商品浏览与销量、noon 商品目录（价格/库存/在售状态）、noon 店铺报表。"
description_en: "Use when working with noon.com (noon Partners) report data that SellerSheet ingests on a schedule — querying…"
author: SellerSheet AI
description: >-
  Use when working with noon.com (noon Partners) report data that SellerSheet ingests on a schedule — querying noon orders, finance transactions (Transaction View Report, Item Level), FBN inventory aging, product views & sales, the full noon catalog (every listing's prices, stock and live / not-live status) or the FBN catalog (titles and images) for a connected noon store. Covers the 6 rpt_noon_* warehouse tables, the store-ref rule (always myStore-AE), schedules, grain and the query nuances. Do NOT use for Amazon SP-API or Ads report data — use report-data / amazon-report / amazon-ads instead.
  中文触发词：noon 订单、noon 财务/交易明细、FBN 库存账龄、noon 商品浏览与销量、noon 商品目录（价格/库存/在售状态）、noon 店铺报表。
version: 0.17.6
metadata: {apis: [data], pattern: Reference}
---

# noon Report Data

## When to use

Use this skill to read noon data that SellerSheet syncs on a schedule into six warehouse tables:
orders, finance, FBN inventory aging, product views & sales, the catalog export and the FBN
catalog. Read them with the same `query_report_data` tool you use for Amazon (one table per
call, `joins` to add more); `get_table_schema(table_name)` lists the live columns. Run the
preflight in [`sellersheet-shared`](../sellersheet-shared/SKILL.md) first. The user needs a
connected noon account (dashboard → noon section → Connect noon); *"No connected noon account
found"* means connect one first. The SellerSheet sidebar can also create any noon report on demand.

## The store ref: always `myStore-AE`

Pass `store` as the noon store ref **with its marketplace**, e.g. `myStore-AE`, copied verbatim
from `get_user_context`'s store refs, on every call. A ref without a marketplace (`myStore`) is
refused, and so is a marketplace the account does not sell in; the refusal lists the refs that
work. One ref covers one marketplace, so query several marketplaces with one call per ref.

The ref's marketplace is added as a filter for you on every table that carries one:

- `country_code` on the catalog export, FBN aging, product views (one export per marketplace)
  and finance (read from each row's contract title `NOON-AE`, else its currency);
- `market_place_country_code` on orders (rows with a blank country cell are left out).

Only the FBN catalog is account-wide and **not** filtered (the response says so): it has no
marketplace column.

## `report_date`: `'all'`, then filter the real date

Pass `report_date='all'` and filter the table's own date column: `order_placed_at`,
`transaction_date`, `visit_date` or `snapshot_date`. On those tables `report_date` is the sync
stamp, not the data date. The two catalogs are the exception. Their date IS `report_date`, so
`report_date='latest'` returns the current copy (per marketplace for the catalog export).

## Tables

| Table | noon report | Grain | Schedule (UTC) | Kind |
|---|---|---|---|---|
| `rpt_noon_orders` | Orders Export (OMS) | one row per order item | 04:00 + 16:00, last 7 days re-pulled | incremental |
| `rpt_noon_finance` | Transaction View Report (Item Level) | one row per transaction line of an item | 04:00 + 16:00, last 14 days re-pulled | incremental |
| `rpt_noon_fbn_aging` | FBN Inventory Aging | one row per SKU × barcode × condition, per marketplace and snapshot date | 04:00 + 16:00 | snapshot |
| `rpt_noon_product_views` | Product Views and Sales | one row per SKU, per marketplace and visit date | 04:00 + 16:00, last 14 days re-pulled | incremental |
| `rpt_noon_catalog_export` | Catalog Export (live + not live) | one row per partner SKU, per marketplace and day | daily 03:00, marketplaces ~30 min apart | snapshot, 7 days kept |
| `rpt_noon_catalog` | FBN catalog (inbound-eligible items) | one row per partner SKU | daily 05:00 | rolling current list |

The incremental tables re-pull their whole window every run and upsert, so late revisions land
without duplicates.

## Notes that change a query

- **Catalog export.** This is the full catalog: every partner SKU, live and not live, with title,
  brand, prices, sale window and stock. noon shares one listing across its marketplaces, but
  prices and stock differ, so each marketplace has its own copy. A marketplace's newest
  `report_date` is its current catalog, and 7 daily copies are kept (compare two days to see what
  left). The status is `noon_status = 'live'` or `'not_live'`. On a not-live row, `offer_status_reason` says why
  (`Content Issues`, `Invalid Price`, `Stock Issues`, `Deactivated SKU`; sometimes blank).
  Skeleton rows exist: not-live SKUs with no family, brand or title. `noon_price_max = 99999`
  means no cap, not a price.
- **Orders.** The marketplace filter drops rows with a blank `market_place_country_code`.
  `is_fulfilled_by_noon` separates FBN from partner-fulfilled.
- **Finance (Transaction View Report, Item Level).** There is one row per transaction line:
  `reference_nr` × `item_nr` × `transaction_type` (`Sale`, `Refund`, …). Every money column
  includes VAT. Sum `total` for the net payout.
- **FBN aging.** Current stock is the newest `snapshot_date` only: find it with a `max`
  aggregation, then filter on it. The table holds several snapshot dates, so summing across them
  over-counts. One SKU can have several `partner_barcode` rows, so sum per SKU. `sku` is empty
  on `UNIDENTIFIED` barcode rows.
- **Product views.** `asp_shipped` is the average selling price, not a percent.
  `conversion_visitors_percentage` can exceed 100. The sales columns are empty on view-only rows.
- **FBN catalog.** It lists FBN-eligible items only (the catalog export has every listing), with
  `image_url` for `=IMAGE()` thumbnails (the `sellersheet-sheets` image pattern). Join other
  tables on `sku`. A row older than the newest `report_date` has left FBN eligibility.

## Example queries

Not-live listings in AE and why (current catalog):
```json
{ "store": "myStore-AE", "tables": ["rpt_noon_catalog_export"],
  "columns": ["rpt_noon_catalog_export.partner_sku","rpt_noon_catalog_export.noon_title","rpt_noon_catalog_export.offer_status_reason","rpt_noon_catalog_export.price","rpt_noon_catalog_export.stock_fbn_net"],
  "filters": [{"column":"rpt_noon_catalog_export.noon_status","op":"eq","value":"not_live"}],
  "report_date": "latest", "limit": 200 }
```

Net payout in AE since a date (the ref filters finance to AE for you):
```json
{ "store": "myStore-AE", "tables": ["rpt_noon_finance"],
  "aggregations": [{"op":"sum","column":"rpt_noon_finance.total","alias":"net_payout"}],
  "group_by": ["rpt_noon_finance.currency"],
  "filters": [{"column":"rpt_noon_finance.transaction_date","op":"gte","value":"2026-06-01"}],
  "report_date": "all" }
```

Cancelled order items in AE since a date:
```json
{ "store": "myStore-AE", "tables": ["rpt_noon_orders"],
  "columns": ["rpt_noon_orders.order_nr","rpt_noon_orders.sku","rpt_noon_orders.item_status","rpt_noon_orders.order_placed_at"],
  "filters": [{"column":"rpt_noon_orders.item_status","op":"eq","value":"cancelled"},
              {"column":"rpt_noon_orders.order_placed_at","op":"gte","value":"2026-06-01"}],
  "report_date": "all" }
```

## Always relay
`query_report_data` returns `{notification, data:{columns,rows,total_count,…}, human_action}`. Relay `notification.message` and `human_action`. If a noon table returns `_no_data`, the ingestion may not have run yet for that project — check that the noon account is connected and at least one daily cycle has passed.

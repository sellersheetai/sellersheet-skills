---
name: report-data
description: Use when working with Amazon SP-API reports — querying synced report data, checking sync schedules, requesting on-demand reports, polling for completion, downloading TSV data to Drive, or analyzing any report table. Covers inventory, listings, orders, financial, brand analytics, and ad report (SP/SB/SD) tables.
version: 0.8.6
---

# Report Data

## Prerequisites

Run the standard preflight in [`sellersheet-shared`](../sellersheet-shared/SKILL.md) (installed alongside this skill): `get_user_context` succeeds → version check via `data.skills_catalog` → `data.canUseMcp` is true. **Extra auth for this skill:** Ads-API tables (`rpt_sp_*`, `rpt_sb_*`, `rpt_sd_*`) need Amazon Advertising profile access; Brand Analytics tables need Brand Registry.

---

## When To Use

Use this skill when the user asks for:
- Inventory levels, stranded stock, restock needs, storage fees, or fee previews
- Orders, returns, removals, reimbursements, or settlements
- Seller feedback or Brand Analytics search term / market basket / repeat purchase data
- Listing status, images, or catalog state
- Schema-aware querying of any synced report table
- On-demand report creation, polling, or Drive download

## Two Paths

| Path | Use For | Tools |
|------|---------|-------|
| **Cron sync (primary)** | Recurring daily/weekly data — query without hitting Amazon | `query_report_data`, `list_report_syncs` |
| **Manual flow** | On-demand fresh report, Drive TSV output, report type not in cron system | `sp_api_create_report`, `sp_api_get_report`, `sp_api_search_reports` |

**AI permissions:** Query and observe only. **Never call `enable_report_sync`, `trigger_report_sync`, or `disable_report_sync`** — those are admin operations managed server-side.

---

## Path 1: Cron Sync (primary)

Reports sync automatically on schedule and are stored in PostgreSQL `rpt_*` tables. AI queries without hitting Amazon.

**Table names ARE the Amazon report types** (`rpt_` + `report_type` lowercased), so a table you meet in Amazon's docs is the table you query. Old names (`rpt_listings_snapshot`, `rpt_restock_recommendations`, `rpt_account_health`, …) still work as **read-only compat views** — prefer the canonical names. A handful of tables deliberately keep non-Amazon names; see [Deliberate naming exceptions](#deliberate-naming-exceptions).

### Workflow

1. Read `.claude/skills/report-data/_meta.json`.
2. Pick the table that matches the user request.
3. Read `.claude/skills/report-data/reference/<table>.json` for exact column names.
4. Check last sync time, then query data.
5. If no data, tell the user the sync hasn't run yet — do NOT enable or trigger it.

### Step 1: Check last sync time

```
list_report_syncs(store='myStore-AE')
# Returns: is_enabled, last_run_at, next_run_time, consecutive_failures, disabled_reason,
#          disabled_marketplaces per report type
# If stale or consecutive_failures > 0, inform the user — do NOT try to fix it
```

#### Interpreting `disabled_reason` (post-2026-05-07)

| disabled_reason | What it means | What to tell the user |
|---|---|---|
| `null` + `is_enabled=true` | Healthy — running on schedule | nothing |
| `consecutive_failures` | Too many failures in a row, scheduler backed off | Mention the schedule is paused; ops will look at it |
| `auth_revoked` | LWA refresh_token rejected by Amazon (Phase 1 auto-disable) | **User must re-OAuth the store via the OAuth flow** before any `rpt_*` data refreshes. Re-OAuth automatically clears this. |
| `unsupported` | Report type genuinely unavailable for this account (e.g. SP seller reports on a vendor account) | Permanent — will not run. Don't ask ops to retry. |
| `account_suspended` | Whole seller account suspended on Amazon side | User must resolve with Amazon Seller Performance |

If `disabled_reason='auth_revoked'`, the data in `rpt_*` tables will be **stale from the moment of revocation**. Always cite the staleness explicitly: "Last successful sync was YYYY-MM-DD; the auth has since been revoked, so anything since then is missing."

#### Interpreting `disabled_marketplaces` (post-2026-05-07)

For per-mkt schedules, `disabled_marketplaces` is a `text[]` like `['MX', 'BR']`. The scheduler skips listed marketplaces but runs the rest. When you query a `rpt_*` table for a store with disabled marketplaces, those marketplaces will return **zero rows** indefinitely (until ops clears the array). If a `query_report_data` for a specific marketplace returns nothing on a multi-mkt store, check `list_report_syncs` for that mkt being in `disabled_marketplaces` before reporting "no data".

### Step 2: Query the synced data

```json
{
  "store": "myStore-AE",
  "tables": ["rpt_get_afn_inventory_data"],
  "columns": ["rpt_get_afn_inventory_data.seller_sku", "rpt_get_afn_inventory_data.quantity_available"],
  "filters": [],
  "order_by": [{"column": "rpt_get_afn_inventory_data.seller_sku", "dir": "asc"}],
  "limit": 100,
  "report_date": "latest"
}
```

Filter operators: `eq` `neq` `gt` `lt` `gte` `lte` `contains` `in` `not_null`

### Multi-marketplace stores — pick a marketplace via `store_name-country_code`

The `store` argument follows the shared store-reference rules ([`sellersheet-shared`](../sellersheet-shared/SKILL.md)). For a multi-marketplace store, the marketplace you pick in the suffix determines the auto-injected filter per table:

```
query_report_data(store='myStore-US', tables=['rpt_orders'], ...)
# auto-injects: rpt_orders.sales_channel = 'Amazon.com'

query_report_data(store='myStore-US', tables=['rpt_get_merchant_listings_all_data'], ...)
# auto-injects: rpt_get_merchant_listings_all_data.country_code = 'US'

query_report_data(store='myStore-US', tables=['rpt_sp_campaigns'], ...)
# auto-injects: rpt_sp_campaigns.profile_id = <ads profile_id for US>
```

Every ads table (`rpt_sp_*` / `rpt_sb_*` / `rpt_sd_*`) carries both `profile_id`
and a denormalized `country_code` column (added 2026-05-20). `country_code` is
populated on every row, so `country_code = 'US'` is an equivalent, simpler
filter than reverse-mapping `profile_id`.

#### Ads tables are daily performance rows, not a campaign inventory

`rpt_sp_*` / `rpt_sb_*` / `rpt_sd_*` are **DAILY PERFORMANCE rows** — only campaigns with
delivery in the window appear (live count 47 ENABLED vs 21 in the warehouse, observed). For a
complete campaign inventory or count, use the live `ads_sp_campaigns` (`ads_sb_campaigns` /
`ads_sd_campaigns`) API instead. Also: `report_date='latest'` pins to the newest **single** day,
which is often a zero-spend partial day — use `report_date='all'` plus explicit date filters for
any cost or performance analysis.

**Just pass `store='myStore-US'`. Don't filter on the marketplace column directly** — the column name differs per table (`sales_channel` / `country_code` / `marketplace_id` / `profile_id` / `country` / `amazon_store`) and not every table exposes `country_code` (e.g. `rpt_orders` uses `sales_channel='Amazon.com'`, no `country_code` column).

### Aggregations — get totals, not raw rows

For "total revenue by currency", "top 10 SKUs by units", or any grouped summary, pass `aggregations` + `group_by` so the DB does the work:

```json
{
  "store": "myStore-US",
  "tables": ["rpt_orders"],
  "columns": ["rpt_orders.currency", "rpt_orders.sales_channel"],
  "aggregations": [
    {"column": "rpt_orders.item_price", "op": "sum", "alias": "revenue"},
    {"column": "rpt_orders.quantity", "op": "sum", "alias": "units"},
    {"column": "rpt_orders.amazon_order_id", "op": "count", "alias": "order_lines"}
  ],
  "group_by": ["rpt_orders.currency", "rpt_orders.sales_channel"],
  "filters": [
    {"column": "rpt_orders.purchase_date", "op": "gte", "value": "2026-04-01"},
    {"column": "rpt_orders.purchase_date", "op": "lt",  "value": "2026-05-01"}
  ],
  "report_date": "all"
}
```

Allowed ops: `sum`, `count`, `avg`, `min`, `max`. Returns one row per distinct group_by tuple. **Always prefer aggregations over pulling raw rows** for any summary question — a query that would otherwise return 4,000+ rows collapses to a handful.

### Query Rules

- Always use fully-qualified column names: `table_name.column_name`.
- Use the `db_column` values from the reference JSONs exactly as written.
- `report_date` controls the date filter — three modes:
    - `"latest"` (default) → match the most recent date for that table+store. Right for **snapshot tables** (`rpt_get_afn_inventory_data`, `rpt_get_merchant_listings_all_data`, `rpt_get_v2_seller_performance_report`, `rpt_get_fba_myi_all_inventory_data`) where each day overwrites the previous.
    - `"all"` → no date filter. Right for **ID-based lookups** on incremental tables (find a specific `amazon_order_id`, `settlement_id`, `asin`, etc.) where you don't know which date the row was last touched. Mandatory for `rpt_orders`, `rpt_get_v2_settlement_report_data_flat_file_v2`, `rpt_get_flat_file_returns_data_by_return_date`, `rpt_get_fba_fulfillment_removal_order_detail_data`, `rpt_get_ledger_detail_view_data`, `rpt_get_fba_reimbursements_data` lookups by primary key.
    - `"YYYY-MM-DD"` → exact-date match. Right for **historical analysis** ("what was inventory on 2026-04-15?").
- `listing_images` has no date partition — omit `report_date` entirely.
- PII tables are not queryable: `rpt_fba_shipments`, `rpt_seller_feedback`.
- Poll-only tables cannot be manually requested from Amazon: `rpt_get_v2_settlement_report_data_flat_file_v2`.
- **RETIRED 2026-05-04** (skill JSONs marked `_meta.deprecated=true, queryable=false`): `rpt_inventory_age` (data lives in `rpt_get_fba_inventory_planning_data.inv_age_*` and `rpt_get_fba_myi_all_inventory_data.afn-warehouse-quantity`); `rpt_inventory_adjustments` (Amazon report type 2605 throttled — no replacement). Don't query these — they exist only for legacy reads.

### Available rpt_* tables (key ones)

| Table | Report Type | Notes |
|-------|-------------|-------|
| `rpt_get_merchant_listings_all_data` | GET_MERCHANT_LISTINGS_ALL_DATA | daily snapshot; auto-enriches listing_images |
| `rpt_get_afn_inventory_data` | GET_AFN_INVENTORY_DATA | pan-region FBA pool total (lean 6-col schema only — afn-* buckets live in MYI, not here) |
| `rpt_get_afn_inventory_data_by_country` | GET_AFN_INVENTORY_DATA_BY_COUNTRY | per-country FBA split (NARF sellers only) |
| `rpt_get_fba_myi_all_inventory_data` | GET_FBA_MYI_ALL_INVENTORY_DATA | full FBA inventory with afn-* quantity buckets, listing-exists flags, per-unit-volume |
| `rpt_get_v2_seller_performance_report` | GET_V2_SELLER_PERFORMANCE_REPORT | per-marketplace daily AHR score + 9 performance rates + 12 violation defects counts (rewritten 2026-05-04) |
| `rpt_get_fba_inventory_planning_data` | GET_FBA_INVENTORY_PLANNING_DATA | 60+ cols incl. AIS bucket schema, restock-plus, season trio, LTSF (NOT the retired GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT) |
| `rpt_orders` | GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL | **full history retained — never pruned** (append/UPSERT on `amazon_order_id`+`sku`, no rolling deletion). Onboard does a one-shot **30-day backfill**, then an hourly `LAST_UPDATE` incremental appends new orders + folds in status changes forever. So the earliest `purchase_date` reaches back ≈30 days before the store's onboard date — *not* all-time history, and *not* capped at 30 days of retention. Includes `is_business_order` + 6 B2B/locale cols (added 2026-05-04) |
| `rpt_get_fba_storage_fee_charges_data` | GET_FBA_STORAGE_FEE_CHARGES_DATA | monthly; `breakdown_incentive_fee_amount` is a colon-separated str — use derived `incentive_program` + `incentive_amount` |
| `rpt_get_fba_fulfillment_customer_returns_data` | GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA | EU samples populate `status` ('Unit returned to inventory', etc.) |
| `rpt_sales_and_traffic` | GET_SALES_AND_TRAFFIC_REPORT | legacy S&T flat file — page views, sessions, conversions (Brand Analytics permission required) |
| `rpt_dk_sales_traffic_by_date` | Data Kiosk analytics_salesAndTraffic_2024_04_24 (byDate) | store-level daily KPIs; nested Amount objects unwrapped to numeric + shared `currency_code`; `unit_session_percentage` = conversion rate |
| `rpt_dk_sales_traffic_by_asin` | Data Kiosk analytics_salesAndTraffic_2024_04_24 (byAsin) | ASIN-level daily KPIs; same unwrap + conversion-rate semantics as by_date |
| `rpt_search_terms_analytics` | GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT | weekly, brand analytics |
| `rpt_get_merchants_listings_fyp_report` | GET_MERCHANTS_LISTINGS_FYP_REPORT | suppressed SKUs; parser handles English + FR + lowercase header variants |
| `listing_images` | (enriched from rpt_get_merchant_listings_all_data) | persistent image URL cache — see below |

Full index: `.claude/skills/report-data/_meta.json` (45 entries; 2 marked deprecated). S&T now comes from Data Kiosk into `rpt_dk_sales_traffic_by_date` / `rpt_dk_sales_traffic_by_asin`; reference schemas for the Data Kiosk path live in `docs/sp-api-data-kiosk-schemas/` and `docs/sp-api-report-schemas/`.

**Calibration verified 2026-05-04** end-to-end against real Amazon TSV/JSON across 5 stores. See `amz-reporting-server/docs/REPORT_CALIBRATION_STATUS.md` for per-report findings.

### Deliberate naming exceptions

Most `rpt_*` tables are named after the Amazon report type that feeds them. These are not, on purpose:

| Table(s) | Why it keeps a non-Amazon name |
|---|---|
| `rpt_orders` | **Two** report types feed it — `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` (one-shot 30-day backfill at onboard) and `..._BY_LAST_UPDATE_GENERAL` (hourly incremental). No single report type to name it after. |
| `rpt_sp_purchased_products` | Also fed by two report types. |
| `rpt_sp_*`, `rpt_sb_*`, `rpt_sd_*` | Ads-API tables — the names are already Amazon-derived. |
| `rpt_dk_*` | Data Kiosk GraphQL datasets, not SP-API report types. |
| `rpt_noon_*` | noon.com, not Amazon. |
| `listing_images` | Enrichment cache, not a report. |
| `rpt_inventory_age`, `rpt_inventory_adjustments`, `rpt_sales_and_traffic` | Retired — kept under legacy names for legacy reads only. |
| `rpt_fba_shipments`, `rpt_seller_feedback` | PII, frozen — no writes, not renamed. |

Every **renamed** table's old name survives as a read-only compat `VIEW`, so pre-existing SQL keeps working. Write new queries against the canonical name.

### Best Practice: Listings + Images (single LEFT JOIN)

`rpt_get_merchant_listings_all_data` does **not** have `main_image_url` or `listing_status` — those live in
`listing_images`. Pull both in **one query** by LEFT-JOINing `listing_images` on
`(store_id, country_code, seller_sku)`. The image table is a long-lived cache (no `snapshot_date`),
so the join survives across daily snapshots.

```
query_report_data(
    store='myStore-AE',
    tables=['rpt_get_merchant_listings_all_data'],
    joins=[{'table': 'listing_images',
            'on': {'store_id':     'store_id',
                   'country_code': 'country_code',
                   'seller_sku':   'seller_sku'}}],
    columns=[
        'rpt_get_merchant_listings_all_data.*',                # wildcard: every snapshot col
        'listing_images.main_image_url',
        'listing_images.listing_status',
    ],
    report_date='latest',
)
```

`main_image_url` is nullable — NULL means the SKU was first listed within the last 24h and
the next listings cron tick (04:10 marketplace-local) will enqueue enrichment. Don't treat
NULL as "broken"; treat it as "not enriched yet".

The same join works for any consumer that wants thumbnails next to listing-keyed data:
- `tables=['rpt_get_fba_myi_all_inventory_data']` + join `listing_images on (store_id, country_code, sku→seller_sku)`
- `tables=['rpt_orders']` + join `listing_images on (store_id, sku→seller_sku)` (orders is
  cross-marketplace; the LEFT JOIN naturally drops country_code on cross-mkt stores)

### Best Practice: Restock gotchas (`rpt_get_fba_inventory_planning_data`)

Three traps bite anyone querying restock data. All three are silent — the query "succeeds"
and returns wrong or empty-looking results.

1. **Join on `sku` — it is the canonical SKU key.** `sku` matches Amazon's report header
   (`GET_FBA_INVENTORY_PLANNING_DATA`) exactly. The old `merchant_sku` column was a legacy
   alias and was **dropped from `rpt_get_fba_inventory_planning_data` on 2026-07-10** (migration in
   flight). Any older dashboard / SQL still joining or filtering on `merchant_sku` must switch
   to `sku`. (Note: `rpt_get_flat_file_returns_data_by_return_date` legitimately keeps its own `merchant_sku` column — this
   change is scoped to the restock table only.)

2. **`days_of_supply` is NULL for no-sale SKUs — and the two query layers disagree on where
   NULLs sort.** The warehouse (Postgres) sorts NULLs **LAST** on `ORDER BY days_of_supply ASC`
   — that's safe, the urgent low-cover SKUs come first. The **in-sheet `SQL()` / alasql layer
   sorts blanks FIRST** — that is where the unsorted-looking "urgent" lists come from: a wall of
   no-sale rows above the SKUs that actually need attention. Filter `days_of_supply > 0` in
   either layer (it also excludes the no-sale SKUs, which is usually the intent anyway).

3. **Amazon's replenishment columns are `recommended_order_quantity` + `recommended_order_date`.**
   These are what Amazon populates on the live report. The legacy `recommended_replenishment_qty`
   is still a real column, but only pre-migration historical rows populate it (Amazon's current
   report no longer ships that field) — don't rely on it for current data. When `recommended_order_quantity` is
   NULL (Amazon didn't compute a recommendation for that SKU/marketplace), fall back to a
   computed suggestion — see the `sellersheet-dashboard` restock fallback rule
   (`suggested_ship_in = MAX(0, ROUND(units_shipped_t30/30 × target_cover_days) − available −
   inbound)`) and **label it as computed, not Amazon's.**

### Wildcard Columns

`columns` accepts SQL-style wildcards to avoid spelling out every field:

- `'*'`        — every column of the primary table (`tables[0]`)
- `'tbl.*'`    — every column of `tbl` (must be in `tables` or `joins`)
- Mix with explicit columns: `['rpt_get_merchant_listings_all_data.*', 'listing_images.main_image_url']`

Wildcards are ignored when `aggregations` is set — aggregated queries must name
`group_by` columns and aggregation specs explicitly (the SQL `SELECT *, SUM(x)` shape
is rarely meaningful).

### Best Practice: NARF Country-Split FBA Inventory

`rpt_get_afn_inventory_data_by_country` holds country-level FBA inventory for sellers enrolled
in Amazon's NARF (North America Remote Fulfillment) program. Same SKU appears once
per country with the quantity available for local fulfillment.

Pairs with `rpt_get_afn_inventory_data`:
- `rpt_get_afn_inventory_data.afn_fulfillable_quantity` = the pan-NA pool total ("100 units in NA")
- `rpt_get_afn_inventory_data_by_country.quantity_for_local_fulfillment` = how that pool splits
  per country ("70 in US local FCs, 30 in CA local FCs")

For non-NARF sellers, `rpt_get_afn_inventory_data_by_country` will simply be empty — the
upstream Amazon report returns CANCELLED on those accounts and the system treats it
as a successful zero-row result. Don't interpret an empty result as an error; first
check whether the seller is enrolled in NARF.

Sample query — current US local-fulfillable inventory for a store:

```json
{
  "tables": ["rpt_get_afn_inventory_data_by_country"],
  "columns": [
    "rpt_get_afn_inventory_data_by_country.seller_sku",
    "rpt_get_afn_inventory_data_by_country.asin",
    "rpt_get_afn_inventory_data_by_country.quantity_for_local_fulfillment"
  ],
  "filters": [{"column": "rpt_get_afn_inventory_data_by_country.country", "op": "eq", "value": "US"}],
  "order_by": [{"column": "rpt_get_afn_inventory_data_by_country.quantity_for_local_fulfillment", "dir": "desc"}],
  "limit": 50,
  "report_date": "latest"
}
```

Unique key: `(store_id, snapshot_date, fnsku, country, condition_type)`.

---

## Path 2: Manual Flow (on-demand)

Use when you need a fresh report, Drive TSV output, or the type isn't in the cron system.

### Step 1: Identify the Store

```
result = get_user_context()
# Pick from result['data']['ownedStoreInfo']['owned_stores']
# or result['data']['sharedStoreInfo']['shared_stores']
```

### Step 2: Check Sheet for Existing Data

```
rows = read_sheet(spreadsheetId, 'Store Reports!A:Z')
# Look for matching storeName + reportType with a sheetUrl already filled
# If found and recent enough: inform user, skip to analysis
```

### Step 3: Check Amazon for an Existing DONE Report

```
result = sp_api_search_reports(store='myStore-AE',
                               reportType='GET_MERCHANT_LISTINGS_ALL_DATA',
                               processingStatuses=['DONE'],
                               pageSize=5)
if result['data']['reports']:
    latest = result['data']['reports'][0]
    # Use sp_api_get_report with latest['reportId'] — skip create
```

### Step 4: Write Intent Row to Sheet FIRST

```
write_sheet(spreadsheetId, 'Store Reports!A{row}',
    [[storeName, reportType, dataStartTime, dataEndTime, reportPeriod, reportOptionsJson,
      '', '', 'CREATING', '', '']])
```

### Step 5: Create the Report

```
result = sp_api_create_report(store='myStore-AE',
                              reportType='GET_MERCHANT_LISTINGS_ALL_DATA',
                              dataStartTime='2024-01-01T00:00:00Z',   # omit for snapshot reports
                              dataEndTime='2024-01-31T23:59:59Z')
report_id = result['data']['reportId']
```

### Step 6: Write reportId + Status to Sheet

```
write_sheet(spreadsheetId, 'Store Reports!F{row}', [[report_id]])
write_sheet(spreadsheetId, 'Store Reports!G{row}', [['IN_QUEUE']])
```

### Step 7: Poll Until DONE

```
while True:
    result = sp_api_get_report(store='myStore-AE', reportId=report_id)
    status = result['data']['processingStatus']
    write_sheet(spreadsheetId, 'Store Reports!G{row}', [[status]])
    if status == 'DONE':
        break
    elif status in ('CANCELLED', 'FATAL'):
        break   # inform user; retry create if appropriate
    # Wait 2–5 minutes, then poll again
```

### Step 8: Write sheetUrl + Analyze

```
sheet_url = result['data']['sheetUrl']   # Drive configured path
preview   = result['data'].get('preview') # no-Drive fallback

if sheet_url:
    write_sheet(spreadsheetId, 'Store Reports!H{row}',
        [[f'=HYPERLINK("{sheet_url}","View Report")']])
    # Then read_sheet to analyze

elif preview:
    # Analyze preview directly — first 100 rows in data.preview
```

### processingStatus Reference

| Status | Meaning | Action |
|--------|---------|--------|
| DONE | Downloaded | write sheetUrl, analyze |
| IN_QUEUE | Waiting to start | poll again in 2–5 min |
| IN_PROGRESS | Amazon processing | poll again in 2–5 min |
| CANCELLED | Amazon cancelled | retry `sp_api_create_report` |
| FATAL | Amazon error | inform user; retry may not help |

### Drive Folder Requirement

`sp_api_get_report` writes TSV to Drive only if `storeReportsFolderId` is set in `user.workspace_config` (auto-configured when user opens the SellerSheet sidebar). Without it, `data.preview` is returned (first 100 rows) — ask user to open the sidebar, then call `sp_api_get_report` again.

### Typical Processing Times

| Report Type | Typical Wait |
|-------------|-------------|
| Inventory / Listings snapshot | 1–3 min |
| Orders flat file (1 month) | 3–8 min |
| Brand Analytics (quarterly) | 10–15 min |

---

## Tracking Sheet Layout

### Store Reports tab (on-demand)

| Col | Header | Notes |
|-----|--------|-------|
| A | storeName | Store name (e.g. myStore-AE) |
| B | reportType | SP-API reportType constant (e.g. GET_MERCHANT_LISTINGS_ALL_DATA). Legacy sheets carry machine key `reportName` — code accepts both |
| C | dataStartTime | ISO 8601, blank for snapshot reports |
| D | dataEndTime | ISO 8601, blank for snapshot reports |
| E | reportPeriod | WEEK/MONTH/QUARTER for Brand Analytics types; blank otherwise |
| F | reportOptions | Advanced reportOptions JSON (rare extra knobs) |
| G | requestTime | Written on createReport |
| H | reportId | Write immediately after create |
| I | processingStatus | Keep updated while polling; FATAL rows append Amazon's errorDetails |
| J | sheetUrl | Write when DONE (use =HYPERLINK formula) |
| K | folderUrl | Drive folder link (optional) |

Row 1: machine headers (hidden) · Row 2: title banner · Row 3: display labels · Data: row 4+

### Retired: Date Report Scheduler tab

The old GAS-automated scheduler tab (`autoSyncDateReportScheduler` appending
date-range rows and auto-advancing windows) is RETIRED — recurring ingestion
is owned by the server-side cron system (`list_report_syncs` +
`query_report_data` against the `rpt_*` warehouse). The reports spreadsheet
carries exactly three tabs: **Store Reports** (on-demand), **Report Lookup**
(search existing Amazon reports), **Store Report Type** (reference catalog).

-----|--------|-------|
| A | storeName | Store name |
| B | reportName | Must be a date-range report type |
| C | dataStartTime | Start of current window |
| D | dataEndTime | End of current window |
| E | requestTime | Auto-filled on create |
| F | reportId | Auto-filled with Amazon reportId |
| G | processingStatus | IN_QUEUE / IN_PROGRESS / DONE / ERROR / CANCELLED |
| H | lastUpdated | Auto-filled when DONE |
| I | rowsAdded | Count of appended rows |
| J | lastError | Error message if failure |
| K | sheetUrl | =HYPERLINK to cumulative history spreadsheet |
| L | folderUrl | =HYPERLINK to Drive folder |

On success: old `dataEndTime` → `dataStartTime`, today → `dataEndTime`.

---

## Report Types Reference

| Human-Readable Name | SP-API Constant |
|---------------------|-----------------|
| All Listings Report | GET_MERCHANT_LISTINGS_ALL_DATA |
| FBA Inventory | GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA |
| Amazon Search Terms Report | GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT |
| Orders (Flat File) | GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL |
| FBA Restock Inventory | GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT |
| Market Basket Analysis | GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT |
| Repeat Purchase Report | GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT |

Full list of 114 types: `flask/app/shared/report_types.py`, or call `sp_api_search_reports` without `reportType`.

## Date Range Guidelines

- **Snapshot reports** (inventory, listings): omit `dataStartTime` / `dataEndTime`
- **Date-range reports** (orders, analytics): provide both in ISO 8601 (`2024-01-01T00:00:00Z`)
- Most reports: up to 2 years back; Brand Analytics: 90 days max

## Notes

- Snapshot tables use `snapshot_date`; most date-range tables use `report_date`.
- Legacy/deprecated tables remain in `_meta.json` with `deprecated: true`.
- `listing_images` is a persistent cache — one row per `(store_id, country_code, seller_sku)`,
  never reset by daily re-runs. Query without `report_date`.
- `rpt_get_merchant_listings_all_data` does not have `main_image_url` or `listing_status` — use `listing_images`.

---
name: report-data
description: Use when working with Amazon SP-API reports — querying synced report data, checking sync schedules, requesting on-demand reports, polling for completion, downloading TSV data to Drive, or analyzing any report table. Covers inventory, listings, orders, financial, brand analytics, and ad report (SP/SB/SD) tables.
version: 0.5.1
---

# Report Data

## Prerequisites — confirm SellerSheet MCP is connected

Every operation in this skill talks to Amazon report data through the **SellerSheet MCP server**. Before doing anything else:

1. **Try `get_user_context`** (the MCP tool).
   - ❌ Tool not in your catalog OR returns auth error → SellerSheet MCP isn't set up. Surface this to the user verbatim, then STOP until they confirm setup is done:

     > **SellerSheet MCP isn't connected.** To use this skill:
     > 1. Sign up / sign in at [sellersheetai.com](https://sellersheetai.com).
     > 2. Get your API key at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Settings → API.
     > 3. Add the MCP server to your agent's config (see [setup-mcp.md](https://github.com/sellersheetai/sellersheet-skills/blob/main/docs/setup-mcp.md) for per-agent paths).
     > 4. Restart your agent.
     > 5. Reopen this conversation.

   - ✅ Returns a user profile → continue to step 2.

2. **Version check.** `get_user_context` returns `data.skills_catalog` listing the latest public-skill versions. Compare `skills_catalog.skills[name=report-data].latest_version` to the `version:` in this SKILL.md's frontmatter. If yours is older, prompt the user with `data.skills_catalog.install_commands.update`. If `skills_catalog` is missing (older MCP build), skip silently.

3. **Permissions check.** `data.canUseMcp` must be true. If false, surface `data.message` (the blocking issues) and stop. Some report types require additional auth — Ads-API reports (`rpt_sp_*`, `rpt_sb_*`, `rpt_sd_*`) need Amazon Advertising profile access; Brand Analytics reports need Brand Registry.

Only after all three pass: proceed with the skill body below.

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
  "tables": ["rpt_afn_inventory"],
  "columns": ["rpt_afn_inventory.seller_sku", "rpt_afn_inventory.quantity_available"],
  "filters": [],
  "order_by": [{"column": "rpt_afn_inventory.seller_sku", "dir": "asc"}],
  "limit": 100,
  "report_date": "latest"
}
```

Filter operators: `eq` `neq` `gt` `lt` `gte` `lte` `contains` `in` `not_null`

### Multi-marketplace stores — pick a marketplace via `store_name-country_code`

The `store` argument follows the same `store_name + '-' + country_code` rule used by every other tool (see `get_user_context` docstring). For a store whose `country_code` is comma-separated (e.g. `US,CA,MX,BR` or `UK,DE,FR,IT,ES,NL,PL,SE,BE,IE`), pick the target marketplace and the route auto-injects the right marketplace filter per table:

```
query_report_data(store='myStore-US', tables=['rpt_orders'], ...)
# auto-injects: rpt_orders.sales_channel = 'Amazon.com'

query_report_data(store='myStore-US', tables=['rpt_listings_snapshot'], ...)
# auto-injects: rpt_listings_snapshot.country_code = 'US'

query_report_data(store='myStore-US', tables=['rpt_sp_campaigns'], ...)
# auto-injects: rpt_sp_campaigns.profile_id = <ads profile_id for US>
```

Every ads table (`rpt_sp_*` / `rpt_sb_*` / `rpt_sd_*`) carries both `profile_id`
and a denormalized `country_code` column (added 2026-05-20). `country_code` is
populated on every row, so `country_code = 'US'` is an equivalent, simpler
filter than reverse-mapping `profile_id`.

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
    - `"latest"` (default) → match the most recent date for that table+store. Right for **snapshot tables** (afn_inventory, listings_snapshot, account_health, fba_inventory_health) where each day overwrites the previous.
    - `"all"` → no date filter. Right for **ID-based lookups** on incremental tables (find a specific `amazon_order_id`, `settlement_id`, `asin`, etc.) where you don't know which date the row was last touched. Mandatory for `rpt_orders`, `rpt_settlements`, `rpt_returns`, `rpt_removal_orders`, `rpt_inventory_ledger`, `rpt_fba_reimbursements` lookups by primary key.
    - `"YYYY-MM-DD"` → exact-date match. Right for **historical analysis** ("what was inventory on 2026-04-15?").
- `listing_images` has no date partition — omit `report_date` entirely.
- PII tables are not queryable: `rpt_fba_shipments`, `rpt_seller_feedback`.
- Poll-only tables cannot be manually requested from Amazon: `rpt_settlements`.
- **RETIRED 2026-05-04** (skill JSONs marked `_meta.deprecated=true, queryable=false`): `rpt_inventory_age` (data lives in `rpt_restock_recommendations.inv_age_*` and `rpt_fba_inventory_health.afn-warehouse-quantity`); `rpt_inventory_adjustments` (Amazon report type 2605 throttled — no replacement). Don't query these — they exist only for legacy reads.

### Available rpt_* tables (key ones)

| Table | Report Type | Notes |
|-------|-------------|-------|
| `rpt_listings_snapshot` | GET_MERCHANT_LISTINGS_ALL_DATA | daily snapshot; auto-enriches listing_images |
| `rpt_afn_inventory` | GET_AFN_INVENTORY_DATA | pan-region FBA pool total (lean 6-col schema only — afn-* buckets live in MYI, not here) |
| `rpt_afn_inventory_by_country` | GET_AFN_INVENTORY_DATA_BY_COUNTRY | per-country FBA split (NARF sellers only) |
| `rpt_fba_inventory_health` | GET_FBA_MYI_ALL_INVENTORY_DATA | full FBA inventory with afn-* quantity buckets, listing-exists flags, per-unit-volume |
| `rpt_account_health` | GET_V2_SELLER_PERFORMANCE_REPORT | per-marketplace daily AHR score + 9 performance rates + 12 violation defects counts (rewritten 2026-05-04) |
| `rpt_restock_recommendations` | GET_FBA_INVENTORY_PLANNING_DATA | 60+ cols incl. AIS bucket schema, restock-plus, season trio, LTSF (NOT the retired GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT) |
| `rpt_orders` | GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL | rolling 30 days; includes `is_business_order` + 6 B2B/locale cols (added 2026-05-04) |
| `rpt_storage_fees` | GET_FBA_STORAGE_FEE_CHARGES_DATA | monthly; `breakdown_incentive_fee_amount` is a colon-separated str — use derived `incentive_program` + `incentive_amount` |
| `rpt_fba_returns` | GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA | EU samples populate `status` ('Unit returned to inventory', etc.) |
| `rpt_sales_and_traffic` | GET_SALES_AND_TRAFFIC_REPORT | legacy S&T flat file — page views, sessions, conversions (Brand Analytics permission required) |
| `rpt_dk_sales_traffic_by_date` | Data Kiosk analytics_salesAndTraffic_2024_04_24 (byDate) | store-level daily KPIs; nested Amount objects unwrapped to numeric + shared `currency_code`; `unit_session_percentage` = conversion rate |
| `rpt_dk_sales_traffic_by_asin` | Data Kiosk analytics_salesAndTraffic_2024_04_24 (byAsin) | ASIN-level daily KPIs; same unwrap + conversion-rate semantics as by_date |
| `rpt_search_terms_analytics` | GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT | weekly, brand analytics |
| `rpt_suppressed_listings` | GET_MERCHANTS_LISTINGS_FYP_REPORT | suppressed SKUs; parser handles English + FR + lowercase header variants |
| `listing_images` | (enriched from rpt_listings_snapshot) | persistent image URL cache — see below |

Full index: `.claude/skills/report-data/_meta.json` (45 entries; 2 marked deprecated). S&T now comes from Data Kiosk into `rpt_dk_sales_traffic_by_date` / `rpt_dk_sales_traffic_by_asin`; reference schemas for the Data Kiosk path live in `docs/sp-api-data-kiosk-schemas/` and `docs/sp-api-report-schemas/`.

**Calibration verified 2026-05-04** end-to-end against real Amazon TSV/JSON across 5 stores. See `amz-reporting-server/docs/REPORT_CALIBRATION_STATUS.md` for per-report findings.

### Best Practice: Listings + Images (single LEFT JOIN)

`rpt_listings_snapshot` does **not** have `main_image_url` or `listing_status` — those live in
`listing_images`. Pull both in **one query** by LEFT-JOINing `listing_images` on
`(store_id, country_code, seller_sku)`. The image table is a long-lived cache (no `snapshot_date`),
so the join survives across daily snapshots.

```
query_report_data(
    store='myStore-AE',
    tables=['rpt_listings_snapshot'],
    joins=[{'table': 'listing_images',
            'on': {'store_id':     'store_id',
                   'country_code': 'country_code',
                   'seller_sku':   'seller_sku'}}],
    columns=[
        'rpt_listings_snapshot.*',                # wildcard: every snapshot col
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
- `tables=['rpt_fba_inventory_health']` + join `listing_images on (store_id, country_code, sku→seller_sku)`
- `tables=['rpt_orders']` + join `listing_images on (store_id, sku→seller_sku)` (orders is
  cross-marketplace; the LEFT JOIN naturally drops country_code on cross-mkt stores)

### Wildcard Columns

`columns` accepts SQL-style wildcards to avoid spelling out every field:

- `'*'`        — every column of the primary table (`tables[0]`)
- `'tbl.*'`    — every column of `tbl` (must be in `tables` or `joins`)
- Mix with explicit columns: `['rpt_listings_snapshot.*', 'listing_images.main_image_url']`

Wildcards are ignored when `aggregations` is set — aggregated queries must name
`group_by` columns and aggregation specs explicitly (the SQL `SELECT *, SUM(x)` shape
is rarely meaningful).

### Best Practice: NARF Country-Split FBA Inventory

`rpt_afn_inventory_by_country` holds country-level FBA inventory for sellers enrolled
in Amazon's NARF (North America Remote Fulfillment) program. Same SKU appears once
per country with the quantity available for local fulfillment.

Pairs with `rpt_afn_inventory`:
- `rpt_afn_inventory.afn_fulfillable_quantity` = the pan-NA pool total ("100 units in NA")
- `rpt_afn_inventory_by_country.quantity_for_local_fulfillment` = how that pool splits
  per country ("70 in US local FCs, 30 in CA local FCs")

For non-NARF sellers, `rpt_afn_inventory_by_country` will simply be empty — the
upstream Amazon report returns CANCELLED on those accounts and the system treats it
as a successful zero-row result. Don't interpret an empty result as an error; first
check whether the seller is enrolled in NARF.

Sample query — current US local-fulfillable inventory for a store:

```json
{
  "tables": ["rpt_afn_inventory_by_country"],
  "columns": [
    "rpt_afn_inventory_by_country.seller_sku",
    "rpt_afn_inventory_by_country.asin",
    "rpt_afn_inventory_by_country.quantity_for_local_fulfillment"
  ],
  "filters": [{"column": "rpt_afn_inventory_by_country.country", "op": "eq", "value": "US"}],
  "order_by": [{"column": "rpt_afn_inventory_by_country.quantity_for_local_fulfillment", "dir": "desc"}],
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
# Look for matching storeName + reportName with a sheetUrl already filled
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
    [[storeName, reportName, dataStartTime, dataEndTime, '', '', 'CREATING', '', '']])
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
| B | reportName | Human-readable report name |
| C | dataStartTime | ISO 8601, blank for snapshot reports |
| D | dataEndTime | ISO 8601, blank for snapshot reports |
| E | requestTime | Written by SP-API on createReport |
| F | reportId | Write immediately after create |
| G | processingStatus | Keep updated while polling |
| H | sheetUrl | Write when DONE (use =HYPERLINK formula) |
| I | folderUrl | Drive folder link (optional) |

Row 1: machine headers · Row 2: display labels · Data: row 3+

### Date Report Scheduler tab (GAS automated)

Used by `autoSyncDateReportScheduler` for date-range reports — appends rows and auto-advances dates.

| Col | Header | Notes |
|-----|--------|-------|
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
- `rpt_listings_snapshot` does not have `main_image_url` or `listing_status` — use `listing_images`.

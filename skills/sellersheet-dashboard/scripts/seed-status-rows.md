# Seed `_status` rows

Template `_status` rows for the 12 standard `_raw_*` tabs. Substitute `<store>` placeholders for the actual canonical identifier (e.g. `myStore-US`, `myStore-US`, `myStore-CA`, `myStore-UK`).

## Header row (write to `_status!A1:L1`)

```
["raw_tab", "store", "source_rpt_table", "refresh_cadence", "expected_lag_hours", 
 "last_pulled_utc", "source_data_through", "row_count", "status", 
 "last_error", "pull_run_id", "agent_actions_count"]
```

Format: emerald `[0.063, 0.725, 0.506]` bg + white bold. Freeze row 1.

## Data rows — single-store template

Write to `_status!A2:L13`. Each row is `<store>`-scoped. For `_raw_catalog` use `store="ALL"`.

```json
[
  ["_raw_inventory",       "<store>", "rpt_get_fba_myi_all_inventory_data + rpt_get_fba_inventory_planning_data", "6h",        2,   "<real_pull_timestamp>", "<source_data_date>", "=COUNTIF('_raw_inventory'!A:A, B2)",       "<status formula B2 with row 2 refs>",  "",                "<run_id>", "=IFERROR(COUNTIFS(_agent_notes!E:E,A2,_agent_notes!D:D,B2,_agent_notes!L:L,\"\"),0)"],
  ["_raw_listings",        "<store>", "rpt_listings_data + rpt_get_merchants_listings_fyp_report",          "daily",     4,   "<real>",                "<>",                 "=COUNTIF('_raw_listings'!A:A, B3)",        "<status formula row 3>",                "",                "<>",       "=IFERROR(COUNTIFS(...row 3...),0)"],
  ["_raw_account_health",  "<store>", "rpt_get_v2_seller_performance_report",                                   "daily",     24,  "<>",                    "<>",                 "=COUNTIF('_raw_account_health'!A:A, B4)",  "<>",                                     "",                "<>",       "<>"],
  ["_raw_ppc",             "<store>", "rpt_sp_campaigns",                                     "daily 03 UTC", 24, "<>",                  "<>",                 "=COUNTIF('_raw_ppc'!A:A, B5)",             "<>",                                     "",                "<>",       "<>"],
  ["_raw_ppc_attribution", "<store>", "rpt_sp_advertised_products",                           "daily 03 UTC", 24, "<>",                  "<>",                 "=COUNTIF('_raw_ppc_attribution'!A:A, B6)", "<>",                                     "",                "<>",       "<>"],
  ["_raw_ppc_search_terms","<store>", "rpt_sp_search_terms",                                  "daily 03 UTC", 48, "<>",                  "<>",                 "=COUNTIF('_raw_ppc_search_terms'!A:A, B7)","<>",                                     "",                "<>",       "<>"],
  ["_raw_ppc_skus",        "<store>", "rpt_sp_advertised_products",                           "daily 03 UTC", 24, "<>",                  "<>",                 "=COUNTIF('_raw_ppc_skus'!A:A, B8)",        "<>",                                     "",                "<>",       "<>"],
  ["_raw_cogs",            "<store>", "manual entry",                                         "manual",    720, "<>",                    "manual",             "=COUNTIF('_raw_cogs'!A:A, B9)",            "<>",                                     "NO_COGS_ENTERED_YET", "manual",  "<>"],
  ["_raw_catalog",         "ALL",     "catalog enrichment (search_catalog_items)",            "daily",     24,  "<>",                    "<>",                 "=COUNTA('_raw_catalog'!A2:A)",             "<>",                                     "",                "<>",       "<>"],
  ["_raw_returns",         "<store>", "rpt_get_flat_file_returns_data_by_return_date + rpt_get_fba_fulfillment_customer_returns_data",                        "daily",     24,  "<>",                    "<>",                 "=COUNTIF('_raw_returns'!A:A, B11)",        "<>",                                     "NOT_YET_SYNCED",  "scaffold", "<>"],
  ["_raw_buybox",          "<store>", "rpt_competitive_pricing + get_item_offers",            "every 6h",  6,   "<>",                    "<>",                 "=COUNTIF('_raw_buybox'!A:A, B12)",         "<>",                                     "NOT_YET_SYNCED",  "scaffold", "<>"],
  ["_raw_finance",         "<store>", "rpt_financial_event_groups",                           "daily",     24,  "<>",                    "<>",                 "=COUNTIF('_raw_finance'!A:A, B13)",        "<>",                                     "NOT_YET_AGGREGATED","scaffold","<>"]
]
```

Replace `<real_pull_timestamp>` with the actual datetime when you pulled the data (USER_ENTERED format: `"2026-05-12 07:00:00"`). NOT `=NOW()`. NOT `=DATEVALUE(...)+TIME(...)`.

## Status formula (column I, per row)

For row n:
```
=IF(J{n}<>"","RED-error",IF((NOW()-F{n})*24>E{n}*2,"RED-stale",IF((NOW()-F{n})*24>E{n},"AMBER-aging","GREEN-fresh")))
```

Replace `{n}` with the actual row number.

## Multi-store template

For a 2-store workbook (e.g. myStore-US + myStore-CA), duplicate the rows above and add a second batch with `store="<store2>"`. `_raw_catalog` stays as one row with `store="ALL"` (it's a master).

So a 2-store workbook has:
- 11 rows × 2 stores = 22 store-scoped rows
- 1 row for `_raw_catalog` (store="ALL")
- **Total 23 rows** in `_status`

If PPC is only on one store (e.g. myStore-CA has Ads, myStore-US doesn't), skip the `_raw_ppc*` rows for the store without Ads — or include them with `last_error="NO_ADS_ACCESS"` so the status badge shows RED-error.

## Conditional formatting on column I

Three rules on `_status!I2:I100`:

```
Rule 1: =LEFT($I2,5)="GREEN"  → bg [0.776, 0.91, 0.835]
Rule 2: =LEFT($I2,5)="AMBER"  → bg [1, 0.898, 0.6]
Rule 3: =LEFT($I2,3)="RED"    → bg [0.957, 0.78, 0.765]
```

Use `CUSTOM_FORMULA` condition type with the `=LEFT(...)` formulas, which is portable across MCP versions. `TEXT_STARTS_WITH` works on most platforms but has caused errors in some MCP builds.

## Per-tab freshness budgets (column E values)

| `_raw_*` | `expected_lag_hours` |
|---|---|
| `_raw_inventory` | 2 |
| `_raw_listings` | 4 |
| `_raw_account_health` | 24 |
| `_raw_ppc` | 24 (4 if launch-phase store) |
| `_raw_ppc_attribution` | 24 |
| `_raw_ppc_search_terms` | 48 |
| `_raw_ppc_skus` | 24 |
| `_raw_cogs` | 720 (30 days — it's human input) |
| `_raw_catalog` | 24 |
| `_raw_returns` | 24 |
| `_raw_buybox` | 6 |
| `_raw_finance` | 24 |

See `reference/freshness-system.md` for the operator-driven rationale.

## After seeding

1. Apply emerald header bg to row 1.
2. Apply conditional formatting on column I per above.
3. Freeze row 1.
4. Resize columns to ~140px each for readability.
5. Add a note to `_status!A1` summarizing the schema (`formula | live status table | each row = _raw_* × store | see reference/freshness-system.md`).

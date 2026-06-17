---
name: data-kiosk
description: Use when authoring or running an Amazon SP-API Data Kiosk GraphQL query — Sales & Traffic (by date / by ASIN / trends), Economics (per-unit fees, cost, margin, preview, simulation), or Vendor Analytics (manufacturing/sourcing view). Provides the exact versioned root query type, dataset fields, required arguments, enums (DateGranularity/AsinGranularity), and per-field @resultRetention so you write a valid query instead of guessing. NOT for the synced rpt_dk_* warehouse (use report-data).
version: 0.7.0
---

# Data Kiosk

Authoritative **GraphQL schemas** for Amazon SP-API Data Kiosk. Use them to write a
valid `createQuery` GraphQL string — correct versioned root type, dataset field,
required arguments, enum values, and the per-field retention — instead of guessing
field names and discovering errors on poll.

This skill is **reference** material. `report-data` owns the synced
`rpt_dk_sales_traffic_*` warehouse; this skill owns authoring the raw GraphQL query
against the live Data Kiosk endpoints.

## Prerequisites — confirm SellerSheet MCP is connected

1. Call `get_user_context`. If it's missing or returns an auth error, SellerSheet
   MCP isn't connected — tell the user to set it up at
   [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) and stop.
2. `data.canUseMcp` must be true. Vendor Analytics needs a **vendor** account.
   `create_data_kiosk_query` / `cancel_data_kiosk_query` require **SP write** access.

## When to use

- "Write a Data Kiosk query for Sales & Traffic / Economics / Vendor Analytics."
- "What fields/args does dataset X take? Which version is current?"
- "Why did my Data Kiosk query come back FATAL / empty?"

NOT for: querying SellerSheet's already-synced `rpt_dk_*` tables (→ `report-data` +
`query_report_data`).

## Check the warehouse FIRST (before creating a query)

Creating a Data Kiosk query costs Amazon quota and minutes of polling. **Sales &
Traffic is already synced into the SellerSheet warehouse** (`rpt_dk_sales_traffic_by_date`,
`rpt_dk_sales_traffic_by_asin`, and the report-based `rpt_sales_and_traffic`). So:

1. If the user wants **Sales & Traffic**, default to the **`report-data`** skill —
   `list_report_syncs` to confirm the table is synced and fresh, then
   `query_report_data`. Do NOT author a new query for data that's already in the warehouse.
2. Only author a Data Kiosk query here when: the dataset is **not** warehoused
   (**Economics**, **Vendor Analytics**), the sync is stale/disabled for the
   marketplace, or you need an ad-hoc shape the warehouse can't serve.

When unsure whether it's synced, check `report-data`'s `_meta.json` / `list_report_syncs` before creating.

## Workflow

```
0. Check report-data FIRST — if the dataset is synced & fresh, query_report_data and STOP (don't create)
1. Pick area + version from _meta.json   →  get the analytics_<area>_<version> root + dataset
2. read reference/<schema>.graphql        →  confirm dataset args, enums, field names, retention
3. create_data_kiosk_query(query)         →  returns data.result.queryId
4. get_data_kiosk_query(queryId)          →  poll until processingStatus == DONE
5. read result.dataDocumentId             →  (field is dataDocumentId, NOT dataDocument; errorDocumentId on FATAL)
6. get_data_kiosk_document(documentId)    →  fetch the NDJSON/JSON result rows
```

`processingStatus`: `IN_QUEUE | IN_PROGRESS | DONE | CANCELLED | FATAL`.
GraphQL query string max length: **8000 chars**.

## Query shape

Every query wraps one or more datasets under the versioned root:

```graphql
query {
  analytics_salesAndTraffic_2024_04_24 {
    salesAndTrafficByAsin(
      startDate: "2026-05-01"
      endDate: "2026-05-31"
      aggregateBy: CHILD              # AsinGranularity: CHILD | PARENT | SKU
      marketplaceIds: ["ATVPDKIKX0DER"]
    ) {
      childAsin
      parentAsin
      sales { orderedProductSales { amount currencyCode } unitsOrdered }
      traffic { sessions pageViews }
    }
  }
}
```

Read the bundled schema for the exact fields — these are real field names from
`analytics_salesAndTraffic_2024_04_24.graphql`.

## Schema index

Load `_meta.json` for the machine-readable index. Areas:

| Area | Current root type | Datasets | Account |
|---|---|---|---|
| Sales & Traffic | `analytics_salesAndTraffic_2024_04_24` | salesAndTrafficByDate, salesAndTrafficByAsin, salesAndTrafficTrends | seller |
| Economics | `analytics_economics_2024_03_15` | economics, economicsPreview, economicsSimulation | seller |
| Vendor Analytics | `analytics_vendorAnalytics_2024_09_30` | manufacturingView, sourcingView | vendor |

A prior Sales & Traffic version (`2023_11_15`) is bundled too; prefer the
`2024_04_24` root for new queries.

## How to read a schema file

`reference/*.graphql` is the SDL. To find what you need:
- The root type `type Analytics_<Area>_<Version>` lists the dataset fields and
  their required arguments (the `Foo!` types are required).
- `enum DateGranularity` = `DAY | WEEK | MONTH`; `enum AsinGranularity` =
  `CHILD | PARENT | SKU`.
- Each field carries `@resultRetention(duration: "P30D")` — its description sits in
  the `"""…"""` block directly above it.

## Gotchas

- **Retention is per-field; the query takes the SHORTEST.** Selecting any P30D
  field caps the whole result document at 30 days. Don't confuse this with the
  ~2-year queryable history (`startDate` lower bound). The P30D is when the
  *generated document* expires — re-run after that.
- **byDate vs byAsin populate different field sets.** `salesAndTrafficByAsin`
  returns one row per ASIN over the whole range and takes `AsinGranularity`;
  `salesAndTrafficByDate` buckets by `DateGranularity` and has no ASIN columns.
- **Date snapping.** With WEEK/MONTH granularity, a mid-period `startDate`/`endDate`
  snaps to the period boundary (next Sunday / first of month, etc.) — see the arg
  description in the schema.
- **Money fields are objects** (`{ amount, currencyCode }`), not scalars.
- **`marketplaceIds` is required and a list** even for a single marketplace.
- **Result field is `dataDocumentId`** (and `errorDocumentId` on FATAL) — NOT
  `dataDocument`. On multi-document results, follow `pagination.nextToken`.

## Common mistakes

- Selecting a dataset's fields with the wrong `aggregateBy` enum type (passing a
  `DateGranularity` to `salesAndTrafficByAsin`) → query rejected.
- Assuming a query that came back `DONE` with no `dataDocumentId` failed — that
  means zero rows for the window, not an error (errors carry `errorDocumentId`).
- Authoring against `2023_11_15` when you need `salesAndTrafficTrends` (only in
  `2024_04_24`).

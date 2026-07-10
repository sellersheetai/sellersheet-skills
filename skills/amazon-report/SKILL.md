---
name: amazon-report
description: Use when requesting or parsing an Amazon SP-API on-demand report document — Brand Analytics (search query performance, search terms, search catalog performance, market basket, repeat purchase), Sales & Traffic, Promotion/Coupon performance, Vendor (sales, traffic, inventory, forecasting, net pure product margin, real-time), B2B product opportunities, marketplace ASIN page-view, end-user data, account health. Provides the exact reportType, required reportOptions enums, and the full JSON field tree of the returned document so you don't guess field names. NOT for the synced rpt_* warehouse (use report-data).
version: 0.8.6
---

# Amazon Report

Authoritative **document schemas** for Amazon SP-API on-demand reports: the exact
`reportType`, the `reportOptions` each one requires (with enum values), and the
full field tree of the JSON document Amazon returns. Use it so you request the
right report and parse its fields by their real names — no guessing, no "pull one
and inspect."

This skill is **reference** material. `report-data` owns the synced `rpt_*`
warehouse and the generic create→poll→download workflow; this skill owns the
on-demand analytics/Brand-Analytics/Vendor report **content schemas**.

## Prerequisites — confirm SellerSheet MCP is connected

1. Call `get_user_context`. If it's not in your tool catalog or returns an auth
   error, SellerSheet MCP isn't set up — tell the user to connect it at
   [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) and stop.
2. `data.canUseMcp` must be true. Brand Analytics reports (`GET_BRAND_ANALYTICS_*`)
   need **Brand Registry**; Vendor reports (`GET_VENDOR_*`) need a **vendor**
   account. Surface `data.message` if blocked.

## When to use

- "Pull the Search Query Performance / Market Basket / Search Terms report."
- "What `reportOptions` does report X require?"
- "What are the exact field names in report X's document?"
- Parsing a `DONE` report document whose nesting you don't know.

NOT for: querying already-synced data (→ `report-data` + `query_report_data`),
or adding a brand-new report type to the warehouse (→ `add-report-type`).

## Check the warehouse FIRST (before requesting a report)

Requesting a report costs Amazon quota and minutes of polling. Several of these
datasets are **already synced into the SellerSheet warehouse** — query those
instead of re-requesting:

- **Synced → use `report-data` + `query_report_data`** (don't re-request):
  Sales & Traffic (`rpt_sales_and_traffic`, `rpt_dk_sales_traffic_*`), orders
  (`rpt_orders`), inventory (`rpt_get_afn_inventory_data*`, `rpt_inventory_*`,
  `rpt_get_fba_myi_all_inventory_data`), returns/removals (`rpt_get_flat_file_returns_data_by_return_date`, `rpt_get_fba_fulfillment_customer_returns_data`,
  `rpt_get_fba_fulfillment_removal_order_detail_data`). Run `list_report_syncs` to confirm it's synced & fresh.
- **Not synced → request on-demand here** (this skill's purpose): Brand Analytics
  (Market Basket, Search Query/Catalog Performance, Search Terms, Repeat Purchase),
  Promotion/Coupon, all Vendor reports, marketplace ASIN page-view, end-user data.

Rule: check `report-data` (`list_report_syncs` / its `_meta.json` index) first;
only create on-demand when the data isn't warehoused, the sync is stale/disabled,
or you need an ad-hoc window the sync doesn't cover.

## Workflow

```
0. Check report-data FIRST — if the report is synced & fresh, query_report_data and STOP (don't re-request)
1. Look up the report in _meta.json  →  get reportType + reportOptions + schema file
2. read reference/<schema>.json      →  confirm reportOptions enum values + document field tree
3. sp_api_search_reports             →  reuse an existing DONE report if recent enough (saves quota)
4. sp_api_create_report(reportType, reportOptions, dataStartTime, dataEndTime, marketplaceIds)
5. sp_api_get_report(reportId)       →  poll until processingStatus == DONE
6. download the document, parse fields by the names in the schema's top-level data array
```

`processingStatus`: `IN_QUEUE | IN_PROGRESS | DONE | CANCELLED | FATAL`.

## How to read a schema file

Each `reference/*.json` is a JSON-Schema (draft-07) doc with:
- `description` — what the report contains + period constraints.
- `examples[0].reportSpecification` — a real `reportType` + `reportOptions` + date pair.
- `examples[0].<dataKey>` — a real document row, so you see the exact nesting.
- `properties` / `definitions` — every field with its description and type.

The document's rows live under one top-level array key (the `dataKey` column in the
index below) — e.g. `dataByAsin`, `salesAndTrafficByDate`, `salesAggregate`.

## Report index

Load `_meta.json` for the machine-readable index (reportType, reportOptions,
account type, document data key, schema path). Highlights:

| reportType | reportOptions (required) | doc key | schema |
|---|---|---|---|
| GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT | reportPeriod (WEEK/MONTH/QUARTER), asin | dataByAsin | sellingPartnerSearchQueryPerformanceReport.json |
| GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT | reportPeriod | dataByDepartmentAndSearchTerm | sellingPartnerSearchTermsReport.json |
| GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT | reportPeriod, asins | dataByAsin | sellingPartnerSearchCatalogPerformanceReport.json |
| GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT | reportPeriod | dataByAsin | sellingPartnerMarketBasketAnalysisReport.json |
| GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT | reportPeriod | dataByAsin | sellingPartnerRepeatPurchaseReport.json |
| GET_SALES_AND_TRAFFIC_REPORT | dateGranularity, asinGranularity | salesAndTrafficByDate / ByAsin | sellerSalesAndTrafficReport.json |
| GET_PROMOTION_PERFORMANCE_REPORT | promotionStartDateFrom/To | promotions | promotionReport.json |
| GET_COUPON_PERFORMANCE_REPORT (seller) | couponStartDateFrom/To | coupons | sellerCouponReport.json |
| GET_COUPON_PERFORMANCE_REPORT (vendor) | campaignStartDateFrom/To | campaigns | vendorCouponReport.json |
| GET_VENDOR_SALES_REPORT | reportPeriod, sellingProgram, distributorView | salesAggregate / salesByAsin | vendorSalesReport.json |
| GET_VENDOR_TRAFFIC_REPORT | reportPeriod | trafficAggregate / trafficByAsin | vendorTrafficReport.json |
| GET_VENDOR_INVENTORY_REPORT | reportPeriod, sellingProgram, distributorView | inventoryAggregate / inventoryByAsin | vendorInventoryReport.json |
| GET_VENDOR_FORECASTING_REPORT | sellingProgram | forecastByAsin | vendorForecastingReport.json |
| GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT | reportPeriod | netPureProductMargin* | vendorNetPureProductMarginReport.json |
| GET_VENDOR_REAL_TIME_SALES_REPORT | currencyCode | reportData | vendorRealTimeSalesReport.json |
| GET_VENDOR_REAL_TIME_TRAFFIC_REPORT | — | reportData | vendorRealTimeTrafficReport.json |
| GET_VENDOR_REAL_TIME_INVENTORY_REPORT | — | reportData | vendorRealTimeInventoryReport.json |
| MARKETPLACE_ASIN_PAGE_VIEW_METRICS | productType | marketplaceAsinPageViewMetrics | marketplaceAsinPageViewMetrics.json |
| END_USER_DATA_REPORT | reportPeriod | endUserData | endUserDataReport.json |
| GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON ¹ | — | recommendations | b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.json |
| GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU ¹ | — | recommendations | b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.json |
| account health ¹ | — | accountStatuses | accountHealthReport-2020-11-18.json |

¹ reportType inferred (not in the bundled schema example) — confirm via
`sp_api_search_reports` / Amazon docs. The document field schema is authoritative regardless.

## Gotchas

- **reportOptions are per-report and mostly required.** A Brand Analytics report
  without `reportPeriod`, or a Vendor report without `sellingProgram`, returns
  FATAL. Read the schema's example block for the exact keys + enum values.
- **A request cannot span periods.** A `WEEK` report's `dataStartTime`/`dataEndTime`
  must fall inside one Amazon week (search-query perf, market basket, etc.). The
  schema `description` states the period rule.
- **`reportPeriod` values vary by report** — a subset of `DAY | WEEK | MONTH |
  QUARTER | YEAR`. Read the schema's `reportOptions.reportPeriod` enum; don't
  assume. Verified examples: Search Query Performance = `WEEK | MONTH | QUARTER`
  (no DAY); Market Basket & Search Terms = `DAY | WEEK | MONTH | QUARTER`; Vendor
  Sales & Inventory = `DAY | WEEK | MONTH | QUARTER | YEAR`.
- **Money fields are objects**, e.g. `{ "amount": 19.99, "currencyCode": "USD" }`,
  not scalars. Don't write the object into a numeric cell.
- **Vendor `distributorView`** = `MANUFACTURING | SOURCING`. **`sellingProgram`
  varies by report**: Vendor Sales = `RETAIL | BUSINESS | FRESH`; Vendor Inventory
  & Forecasting = `RETAIL | FRESH` (no BUSINESS). Confirm in the schema.
- **Brand Analytics → Brand Registry; Vendor → vendor account.** Missing role =
  access error, not an empty report.

## Common mistakes

- Guessing field names instead of reading the schema's `examples[0]` row — the
  Market Basket combination field is `combinationPct` with `purchasedWithAsin` /
  `purchasedWithRank`, not `purchasedWithRate`.
- Treating Sales & Traffic as one shape — it has BOTH `salesAndTrafficByDate` and
  `salesAndTrafficByAsin`; `asinGranularity`/`dateGranularity` pick which arrays populate.
- Re-creating a report you already have — call `sp_api_search_reports` first.

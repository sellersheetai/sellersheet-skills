# Ads Reporting v3 — Request Configurations (offline report bodies)

Real Amazon Ads **Reporting API v3** `createReport` request bodies, one JSON file per
report type. Use these as copy-paste templates for the `body` argument of
`ads_create_report` (Recipe G). Each file is the exact `{name, startDate, endDate,
configuration}` shape Amazon expects, with the **full, authoritative `columns` list**,
correct `reportTypeId`, `groupBy`, `timeUnit`, and `filters` for that report.

How to use:
1. Pick the row below for the report you need; open that JSON file.
2. Copy its `configuration` (keep `reportTypeId`, `groupBy`, `timeUnit`, `filters`).
3. Trim `columns` to the metrics you actually want (fewer columns = smaller report), or keep all.
4. Set your own `name`, `startDate`, `endDate` (`YYYY-MM-DD`).
5. Pass as `body` to `ads_create_report`.

**These are request specs, not response rows.** The response (after `ads_get_report`
COMPLETES) is a list of row dicts keyed by the `columns` you requested.

> Prefer `query_report_data` on the synced `rpt_*` tables for everyday analysis — it is
> instant. Reach for `ads_create_report` + these configs only when you need a
> column/grain/report type the synced tables don't cover (DSP, Sponsored TV,
> gross-and-invalid traffic, placement breakdowns, custom column sets), and you can wait
> 30 min–several hours.

## Sponsored Products (`adProduct: SPONSORED_PRODUCTS`)

| reportTypeId | groupBy | timeUnit | File |
|---|---|---|---|
| `spCampaigns` | `["campaign"]` | SUMMARY | SponsoredProductsCampaignsSummaryReport.json |
| `spCampaigns` | `["campaign","campaignPlacement"]` | SUMMARY | SponsoredProductsCampaignsWithPlacementSummaryReport.json |
| `spCampaigns` | `["adGroup","campaign"]` | DAILY | SponsoredProductsCampaignsWithAdGroupDailyReport.json |
| `spTargeting` | `["targeting"]` | SUMMARY | SponsoredProductsTargetingSummaryReport.json |
| `spTargeting` (keywords only) | `["targeting"]` | SUMMARY | SponsoredProductsKeywordsSummaryReport.json |
| `spTargeting` (kw + targeting) | `["targeting"]` | SUMMARY | SponsoredProductsKeywordsAndTargetingSummaryReport.json |
| `spSearchTerm` | `["searchTerm"]` | SUMMARY | SponsoredProductsSearchTermSummaryReport.json |
| `spAdvertisedProduct` | `["advertiser"]` | DAILY | SponsoredProductsAdvertisedProductDailyReport.json |
| `spPurchasedProduct` | `["asin"]` | DAILY | SponsoredProductsPurchasedProductDailyReport.json |
| `spGrossAndInvalids` | `["campaign"]` | DAILY | SponsoredProductsGrossAndInvalidTrafficDailyReport.json |

## Sponsored Brands (`adProduct: SPONSORED_BRANDS`)

| reportTypeId | groupBy | timeUnit | File |
|---|---|---|---|
| `sbCampaigns` | `["campaign"]` | DAILY | SponsoredBrandsCampaignDailyReport.json |
| `sbCampaignPlacement` | `["campaignPlacement"]` | DAILY | SponsoredBrandsCampaignPlacementDailyReport.json |
| `sbAdGroup` | `["adGroup"]` | DAILY | SponsoredBrandsAdGroupDailyReport.json |
| `sbAds` | `["ads"]` | DAILY | SponsoredBrandsAdsDailyReport.json |
| `sbTargeting` (keyword) | `["targeting"]` | DAILY | SponsoredBrandsTargetingKeywordDailyReport.json |
| `sbTargeting` (expression) | `["targeting"]` | DAILY | SponsoredBrandsTargetingExpressionDailyReport.json |
| `sbSearchTerm` | `["searchTerm"]` | DAILY | SponsoredBrandsSearchTermDailyReport.json |
| `sbPurchasedProduct` | `["purchasedAsin"]` | DAILY | SponsoredBrandsPurchasedProductDailyReport.json |
| `sbGrossAndInvalids` | `["campaign"]` | DAILY | SponsoredBrandsGrossAndInvalidTrafficDailyReport.json |

## Sponsored Display (`adProduct: SPONSORED_DISPLAY`)

| reportTypeId | groupBy | timeUnit | File |
|---|---|---|---|
| `sdCampaigns` | `["campaign"]` | DAILY | SponsoredDisplayCampaignDailyReport.json |
| `sdCampaigns` (matched target) | `["campaign","matchedTarget"]` | DAILY | SponsoredDisplayCampaignWithMatchedTargetGroupByDailyReport.json |
| `sdAdGroup` | `["adGroup"]` | DAILY | SponsoredDisplayAdGrouptDailyReport.json |
| `sdAdvertisedProduct` | `["advertiser"]` | DAILY | SponsoredDisplayAdvertisedProductDailyReport.json |
| `sdTargeting` | `["targeting"]` | DAILY | SponsoredDisplayTargetingDailyReport.json |
| `sdPurchasedProduct` | `["asin"]` | DAILY | SponsoredDisplayPurchasedProductDailyReport.json |
| `sdGrossAndInvalids` | `["campaign"]` | SUMMARY | SponsoredDisplayGrossAndInvalidTrafficSummaryReport.json |

## Sponsored Television (`adProduct: SPONSORED_TELEVISION`)

| reportTypeId | groupBy | timeUnit | File |
|---|---|---|---|
| `stCampaigns` | `["campaign"]` | DAILY | SponsoredTelevisionCampaignDailyReport.json |
| `stTargeting` | `["targeting"]` | DAILY | SponsoredTelevisionTargetingDailyReport.json |

## Amazon DSP (`adProduct: DEMAND_SIDE_PLATFORM`)

DSP reports require an `advertiserId` filter and use a different (much wider) column set.
These run through the DSP reporting surface, not the SP/SB/SD `createReport` flow — treat
them as column references for what DSP exposes, and confirm DSP access before attempting.

| reportTypeId | groupBy | timeUnit | File |
|---|---|---|---|
| `dspCampaign` | `["creative"]` | SUMMARY | DSPCampaignSummaryReport.json |
| `dspAudience` | `["lineItem"]` | SUMMARY | DSPAudienceSummaryReport.json |
| `dspAudioAndVideo` | `["ad","campaign","content","creative","supplySource"]` | SUMMARY | DSPAudioAndVideoSummaryReport.json |
| `dspGeo` | `["postalCode"]` | SUMMARY | DSPGeoSummaryReport.json |
| `dspInventory` | `["site"]` | SUMMARY | DSPInventorySummaryReport.json |
| `dspProduct` | `["lineItem"]` | SUMMARY | DSPProductSummaryReport.json |
| `dspTech` | `["lineItem"]` | SUMMARY | DSPTechSummaryReport.json |

## Validity (corrected 2026-06-30 against live Amazon createReport)

Amazon's raw "[Preview Only]" sample configs are **column-superset previews and are NOT
all directly submittable** — 11 were rejected by live `createReport` and have been
**corrected here** (verified accepted). The two rules they violated — now enforced
across every file:
1. **`timeUnit` ↔ date column.** `DAILY` must include `date` and must NOT include
   `startDate`/`endDate`; `SUMMARY` must include `startDate`/`endDate` and must NOT
   include `date`. (Mixing → 400 `"… not supported for … time unit"`.)
2. **Filters are groupBy-specific.** A filter field valid for one `groupBy` is rejected
   for another (e.g. `campaignStatus` is invalid for `groupBy: advertiser`; `sbAds`
   accepts no filters; `keywordStatus` is not a valid `sbTargeting`/`sbSearchTerm`
   filter). When adding a filter back, use the allowed set Amazon names in the 400.

**Throttling:** `createReport` is **aggressively rate-limited by Amazon** (429
`Throttled`) — independent of the SellerSheet plan limiter. Submit reports **one at a
time with a few seconds between calls** and back off on 429; do not fan them out.

## Notes & gotchas

- **`timeUnit` controls grain.** `SUMMARY` collapses the whole date range into one row per
  group; `DAILY` returns one row per group per day and **requires a `date` column** in
  `columns` (see the `...Daily*` configs). Mixing `SUMMARY` with a `date` column, or
  `DAILY` without one, is rejected by Amazon.
- **`columns` must be valid for that `reportTypeId` + `groupBy`.** Don't borrow columns
  across report types — each file's list is the allowed set for that combination.
- **`filters` are optional** but when present use the `[{"field": ..., "values": [...]}]`
  shape shown (this is the v3 report-config filter shape — distinct from the entity-list
  `stateFilter` comma-strings used by SD/SB-neg list endpoints).
- **`format`** is `GZIP_JSON` in every sample; the backend decompresses and returns parsed
  rows in `data.report`.
- Same `reportTypeId` can appear with different `groupBy`/`timeUnit` (e.g. `spCampaigns`
  three ways) — the groupBy is what changes the grain, not the type id.

# Amazon Ads API v1 (unified) — FULL request-body field catalogs

Complete leaf-level request-body schemas for the unified v1 MCP tools
(`ads_campaigns`, `ads_ad_groups`, `ads_ads`, `ads_targets`,
`ads_ad_associations`), one file per entity, per ad product × verb
(query/create/update/delete). `*` after a field = required within its object.

These are GENERATED from Amazon's OpenAPI specs vendored at
`docs/ads-api-v1/specs/` in the sellersheet_flask_app repo — regenerate with
`python3 docs/ads-api-v1/tools/gen_field_catalog.py` there and re-copy.

Load the relevant entity file BEFORE composing a create/update payload — the
tool docstrings carry the common fields and live-verified gotchas; these
catalogs are the exhaustive parameter reference.

Live-verified gotchas (2026-07-05, TJ-AE + SML-AU):
- query/campaigns (and most entities) REQUIRES adProductFilter; paginate by
  resending the SAME filters + nextToken (token-only body → 400).
- SP create/campaigns requires marketplaceScope=SINGLE_MARKETPLACE,
  non-empty marketplaces (country codes e.g. ["AE"]), startDateTime,
  autoCreationSettings{autoCreateTargets}, budgets.
- budgets nesting: budgetValue.monetaryBudgetValue.monetaryBudget.value.
- delete = {"<entity>Ids": [...]} ID arrays, NOT filters. Delete = archive.
- Mutations return HTTP 207 {success[],partialSuccess[],error[]} even when
  all items failed; request-level errors are plain 400 {code,message}.
- ad_associations is DSP-scoped: 401 on sponsored-ads profiles.
- SP product ad creative: creative.productCreative.productCreativeSettings
  .advertisedProduct{productId, productIdType: SKU(seller)|ASIN(vendor)}.

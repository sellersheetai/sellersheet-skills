# Amazon Ads API v1 (unified) — FULL request-body field catalogs

Complete leaf-level request-body schemas for the unified v1 MCP tools
(`ads_campaigns`, `ads_ad_groups`, `ads_ads`, `ads_targets`,
`ads_ad_associations`) — one file per entity, covering every ad product
(Sponsored Products / Brands / Display / Television, Amazon DSP) and every
verb (query / create / update / delete). `*` after a field = required within
its object. Enums with more than 15 values are listed in `ENUMS.md`.

Generated from Amazon's official Ads API v1 OpenAPI specifications
(https://advertising.amazon.com/API/docs/en-us/amazon-ads/1-0/apis).

Load the relevant entity file BEFORE composing a create/update payload — the
tool docstrings carry the common fields and key gotchas; these catalogs are
the exhaustive parameter reference.

Verified behavior of the live API (from real calls, not just the spec):

- `query` requires `adProductFilter` on most entities; paginate by resending
  the SAME filters plus `nextToken` (a token-only body returns 400).
- Sponsored Products `create/campaigns` requires
  `marketplaceScope: "SINGLE_MARKETPLACE"`, non-empty `marketplaces`
  (country codes, e.g. `["AE"]`), `startDateTime`,
  `autoCreationSettings{autoCreateTargets}`, and `budgets`.
- Budget nesting: `budgetValue.monetaryBudgetValue.monetaryBudget.value`.
- Delete takes `{"<entity>Ids": [...]}` ID arrays, NOT filters, and archives
  (state -> ARCHIVED; entities stay queryable).
- Mutations return HTTP 207 `{success[], partialSuccess[], error[]}` even
  when every item failed — always inspect `error[]`. Request-level errors
  are plain 400 `{code, message}`.
- `ad_associations` is an Amazon DSP resource: sponsored-ads profiles get
  401 "not authorized to access account".
- Sponsored Products product-ad creative:
  `creative.productCreative.productCreativeSettings.advertisedProduct{productId, productIdType}`
  — `productIdType` is `SKU` for seller accounts, `ASIN` for vendors.
- `productTarget.product` is an OBJECT: `{"productId": "<ASIN>"}` — a bare
  string returns 400 "Expected null".
- An SP ad group is SINGLE-targeting-type: keyword and product targets cannot
  coexist in one ad group. Adding the second type fails with the misleading
  `FIELD_VALUE_NOT_UNIQUE` "Duplicate object found" — use separate ad groups.
- Campaign `stateFilter` also accepts `PROPOSED` (returned by the live enum
  validator alongside ENABLED/PAUSED/ARCHIVED).
- A schema-valid ad create can still fail per-index with `PRODUCT_INELIGIBLE`
  when the product is not currently buyable.

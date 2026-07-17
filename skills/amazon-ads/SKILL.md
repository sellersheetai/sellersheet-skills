---
name: amazon-ads
description: Guide for managing Amazon Advertising (SP, SB, SD) using SellerSheet MCP tools. Use when working with Amazon Ads campaigns, ad groups, keywords, targets, bids, budgets, bulk creation, negative keywords, ad performance data, bulk exports, change history, account management, invoices, or validation configs.
version: 0.11.2
---

# Amazon Ads — SellerSheet MCP Guide

This skill covers what individual tool docstrings cannot: cross-cutting conventions,
workflow sequences, and tool selection. Do NOT repeat body schemas or filter syntax
already documented in each tool's docstring.

**Bundled reference:** `reference/report-configs/` holds real Amazon Ads Reporting API v3
`createReport` request bodies (one per report type, with the full authoritative `columns`
list) for the offline-report path — see `reference/report-configs/README.md`.

**Unified v1 tools (PREFERRED for campaign management):** `ads_campaigns`,
`ads_ad_groups`, `ads_ads`, `ads_targets`, `ads_ad_associations` — one common-model
surface for SP/SB/SD/ST/DSP over Amazon Ads API v1 (`/adsApi/v1/*`). Keywords,
product targets, and ALL negatives are a single `targets` resource (`negative` flag).
**Before composing any v1 create/update payload, read the FULL field catalog for the
entity at `reference/ads-v1/<entity>.md`** — complete leaf-level schema per ad
product × verb, plus live-verified gotchas in `reference/ads-v1/README.md`.
The legacy per-product tools (`ads_sp_*`, `ads_sb_*`, `ads_sd_*`) remain for
entities v1 doesn't cover (portfolios, recommendations, exports, history, reports).

---

## Tier 1: Concepts

### 1. Getting Started

Run the standard preflight + store-reference rules in
[`sellersheet-shared`](../sellersheet-shared/SKILL.md) first. Ads-specific delta:
**every ads tool requires BOTH `store` (in `<name>-<countryCode>` format) and
`countryCode`** (e.g. `store="myStore-US"`, `countryCode="US"`) — a bare store name
is rejected with "Store name '…' is ambiguous" because each marketplace is a
different ad profile. `get_user_context` also returns the workspace config
(spreadsheet ID + Drive folder ID) the recipes below write to.

**Workspace not configured?**
If `get_user_context` returns no spreadsheet ID / folder ID, or `read_sheet` /
`write_sheet` / Drive tools fail to access them, tell the user:
> "Install the SellerSheet sidebar in Google Sheets, open it to initialize your
> workspace, and share your root SellerSheet folder to
> `automation@sellersheetai.com`."

### 2. Sheet as Audit Surface

- **Before mutations** (create/update/delete): write intent to sheet with `write_sheet`
- **After every tool call**: write `data.result` to sheet with `write_sheet`
- **Before reading live state**: check sheet first with `read_sheet` to skip redundant API calls
- **Always relay** `notification.message` and `human_action` to the user
- `human_action` will become automated agent sheet-write actions in a future update

### 3. Two Performance Data Paths

| Situation | Tool |
|---|---|
| All analysis, optimization, daily ops — default | `query_report_data` on `rpt_sp_*` / `rpt_sb_*` / `rpt_sd_*` |
| Last 1-2 days — may be incomplete | Warn user: Amazon attribution not yet finalized |
| Need columns/dimensions not in synced tables, OK to wait hours | `ads_create_report` + `ads_get_report` |

Pass `report_date: "latest"` for the most recent synced date. Use `YYYY-MM-DD` for
historical ranges.

**`query_report_data` is the default.** The offline report path (`ads_create_report`)
takes 30 minutes to several hours — only use it when synced tables genuinely cannot
serve the need.

**The warehouse tables are DAILY PERFORMANCE rows — not a campaign inventory.** Only campaigns
with delivery in the window appear in `rpt_sp_*` / `rpt_sb_*` / `rpt_sd_*` (live count 47
ENABLED vs 21 in the warehouse, observed). For a complete campaign inventory or count, use the
live `ads_sp_campaigns` / `ads_sb_campaigns` / `ads_sd_campaigns` API. And `report_date: "latest"`
pins to the newest **single** day, often a zero-spend partial day — use `report_date: "all"` plus
explicit date filters for any cost or performance analysis.

### 4. Ad Type Hierarchy

```
Campaign → Ad Group → Keywords / Targets → Product Ads
```

- **SP and SB**: full hierarchy
- **SD**: `Campaign → Ad Group → Targets + Product Ads`

Resolve IDs top-down before creating child entities. Use the parent tool with
`action='list'` to get IDs.

### 5. Campaign & Ad Group Naming Convention

Every campaign you create — via the unified `ads_campaigns` (preferred) or the
legacy `ads_sp_campaigns` / `ads_sb_campaigns` / `ads_sd_campaigns` /
`ads_sp_bulk_create` — must follow this format. Audit existing campaigns against
it before any rollout; flag deviations to the user.

```
<Country>_<ProductLine>_<AdType>_<Targeting>_<SKU>
```

| Part | Values | Notes |
|---|---|---|
| `Country` | `AU` `US` `UK` `AE` `CA` `DE` `FR` `ES` `IT` `JP` `SG` | Marketplace short code (matches `countryCode`) |
| `ProductLine` | PascalCase category or product family | e.g. `MattressProtector`, `Towel`, `Luggage`, `Shirt`. No spaces, no underscores inside. |
| `AdType` | `SP` `SB` `SD` | Sponsored Products / Brands / Display |
| `Targeting` | `AUTO` `BROAD` `PHRASE` `EXACT` `PT` `CAT` `COMP` `BD` | See table below |
| `SKU` | Parent SKU when one exists, otherwise ASIN | One campaign per SKU per targeting variant |

**Targeting codes:**

| Code | Meaning | Used by |
|---|---|---|
| `AUTO` | Auto-targeting (Amazon picks keywords/products) | SP only |
| `BROAD` | Manual broad-match keywords | SP, SB |
| `PHRASE` | Manual phrase-match keywords | SP, SB |
| `EXACT` | Manual exact-match keywords | SP, SB |
| `PT` | Product Targeting — specific ASINs | SP, SB, SD |
| `CAT` | Category Targeting — `ASIN_CATEGORY_SAME_AS` | SP, SB, SD |
| `COMP` | Competitor Conquest — competitor ASINs | SP, SB, SD |
| `BD` | Brand Defense — own ASINs / branded keywords | SB, SD |

**Examples (production):**

```
AU_MattressProtector_SP_AUTO_SHBS001013
AU_MattressProtector_SP_PT_SHBS001013
US_Towel_SB_BD_TJ-TOWEL-Q
UK_Luggage_SD_COMP_NS-LG-28
```

**Rules:**

- Underscore `_` is the only separator. Do not use spaces, dashes (except inside
  multi-segment SKUs), slashes, or brackets.
- One Targeting variant per campaign — split `Broad/Phrase` into two separate
  campaigns (`..._SP_BROAD_...` and `..._SP_PHRASE_...`), not one combined.
- **Ad group names are derived, never free-form:** `<CampaignName>_<Role>` —
  the full campaign name plus a short PascalCase role token. Single-ad-group
  campaigns use `_Main`; multi-ad-group campaigns pick intent roles like
  `_TopKW`, `_Winners`, `_Harvest`, `_Comp`, `_Cat`.
  Examples: `AU_MattressProtector_SP_EXACT_SHBS001013_Main`,
  `US_Towel_SB_BD_TJ-TOWEL-Q_TopKW`.
  Because campaign names are unique, this makes every ad group name **globally
  unique across the account** — Amazon does NOT enforce cross-campaign ad-group
  name uniqueness, but sheet templates, Amazon bulksheets, and dedupe checks all
  join by name, so a duplicate ad group name in another campaign silently corrupts
  those joins. Keep one targeting type per ad group (an SP ad group cannot mix
  keyword and product targets — see the ads-v1 reference gotchas).
- **Collision check before every create:** query existing names first —
  `ads_campaigns` action=query with `nameFilter {"include": ["<name>"],
  "queryTermMatchType": "EXACT_MATCH"}` (plus the required adProductFilter) — and
  stop if the name already exists. Never rely on Amazon to reject duplicates (it
  accepts them), and never create a variant by appending `(2)`; fix the segments
  instead.
- When migrating an account to this convention: never rename live campaigns mid-
  flight (breaks history). Apply only to new campaigns; document the legacy ones
  in the audit sheet.

---

## Tier 2: Workflow Recipes

### A. Account Health Check

1. `query_report_data` on `rpt_sp_campaigns`, `rpt_sb_campaigns`, `rpt_sd_campaigns`
   — `report_date: "latest"`, sort by `spend` desc
2. Compute totals: spend, sales_14d, ACoS (`spend / sales_14d * 100`), impressions, clicks
3. Flag campaigns with ACoS above target or zero `sales_14d`
4. Write summary to sheet

### B. Find Wasted Spend

1. `query_report_data` on `rpt_sp_keywords` — filter `cost > threshold AND purchases_14d = 0`
2. `query_report_data` on `rpt_sp_search_terms` — same filter
3. Repeat for SB: `rpt_sb_keywords`, `rpt_sb_search_terms`
4. Repeat for SD: `rpt_sd_targets`
5. Write waste list to sheet → propose negatives to user

### C. Bid Optimization

1. `query_report_data` on `rpt_sp_keywords` — get `cost`, `sales_14d`, `clicks` per keyword
2. Calculate ACoS per keyword; compare to target
3. Over-target: write bid-down intent to sheet → `ads_sp_keywords` action=`update`
4. Under-target with good volume: write bid-up intent → `ads_sp_keywords` action=`update`
5. Repeat for SB keywords (`ads_sb_keywords`) and SD targets (`ads_sd_targets`)

### D. Launch New Campaign (Bulk SP)

1. `ads_sp_recommendations` — ranked or suggested keywords for target ASINs
2. `ads_sp_bid_recommendations` — suggested bids for selected keywords/targets
3. Write full campaign spec to sheet for user review
4. `ads_sp_bulk_create` — creates campaign + ad groups + keywords + product ads atomically
5. Write returned campaign ID and ad group IDs to sheet

### E. Negative Keyword Mining

1. `query_report_data` on `rpt_sp_search_terms` — filter `cost > threshold AND purchases_14d = 0`
2. Group by campaign / ad group; review candidates with user
3. Write negatives intent to sheet
4. Ad group level: `ads_sp_neg_keywords` action=`create`
5. Campaign level (blocks all ad groups): `ads_sp_campaign_neg_keywords` action=`create`
6. Repeat for SB via `ads_sb_neg_keywords` (note: SB neg keywords use comma-string filters — see tool docstring)

### F. Budget Management

1. `query_report_data` on `rpt_sp_campaigns` — identify campaigns near or hitting daily budget cap
2. `ads_sp_campaigns` action=`list` — get current budget amounts for candidates
3. Write budget-change intent to sheet
4. `ads_sp_campaigns` action=`update` — apply new daily budgets
5. `ads_sp_portfolios` for portfolio-level budget caps if needed

### G. On-Demand Offline Report

_Only when synced tables cannot serve the need (DSP, Sponsored TV, gross-and-invalid
traffic, placement breakdowns, or a column set the `rpt_*` tables don't carry)._

1. Confirm with user: this will take **30 minutes to several hours**
2. Build the report body from a ready-made template in
   **`reference/report-configs/`** — one JSON file per report type with the exact
   `reportTypeId`, `groupBy`, `timeUnit`, `filters`, and full `columns` list. See
   `reference/report-configs/README.md` for the lookup table (SP, SB, SD, Sponsored TV,
   DSP). Copy the `configuration`, trim `columns` to what you need, set your own `name` /
   `startDate` / `endDate`. The `ads_create_report` docstring only documents SP types —
   the reference folder is the authoritative full catalog.
3. `ads_create_report` → write `data.reportId` to sheet immediately (do not lose it)
4. Notify user the report is in progress — do not block waiting
5. When user returns: `ads_get_report` → if `COMPLETED`, write `data.report` rows to sheet and summarize; if still `IN_PROGRESS`, check again later

**`timeUnit` rule:** `DAILY` reports must include a `date` column (NOT
`startDate`/`endDate`); `SUMMARY` reports must include `startDate`/`endDate` (NOT `date`).
The bundled templates were corrected against live Amazon validation (2026-06-30) and
pair these correctly — don't re-add the wrong one. Filters are **groupBy-specific**:
if Amazon 400s `"filters includes fields …"`, drop the offending field.

**Throttling:** Amazon throttles `createReport` hard (429 `Throttled`), separate from
the SellerSheet rate limit. Submit reports **one at a time, a few seconds apart**, and
back off on 429 — never fan out a batch of `ads_create_report` calls.

### H. Bulk Entity Export (Snapshot of Live Structure)

Use when you need a full snapshot of campaign structure — IDs, states, budgets, bid strategies — without pagination limits. Faster than listing entity by entity.

1. Fire all 4 in parallel: `ads_sp_export` with operations `campaigns_export`, `adgroups_export`, `targets_export`, `ads_export`
   - Body: `{"adProductFilter": ["SPONSORED_BRANDS","SPONSORED_DISPLAY","SPONSORED_PRODUCTS"], "stateFilter": ["ENABLED","PAUSED"]}`
2. Poll all 4 in parallel with `get_export` using the returned `exportId` + correct `typeExport`
   - `campaigns_export` → `typeExport: "campaigns"` · `adgroups_export` → `"adGroups"` · `targets_export` → `"targets"` · `ads_export` → `"ads"`
3. When `status=COMPLETED`, `data.result.exportData` is auto-downloaded — no extra step
4. Write each export to its own sheet tab for analysis

**When to use export vs. list:**
- Export: full account snapshot, cross-campaign analysis, audit, or when you need all entities without 500-item pagination
- List: targeted operations on a specific campaign/ad group (create, update, delete)

### I. Change History Audit

1. `ads_sp_history` — body: `{"fromDate": <ms>, "toDate": <ms>, "eventTypes": {"CAMPAIGN": true, "KEYWORD": true}}`
   - `eventTypes` must be an object `{"TYPE": true}`, NOT an array
   - Dates are millisecond Unix timestamps (13 digits); range must be within last 90 days
2. Write history to sheet; filter for unexpected state changes or bid changes
3. Cross-reference with `rpt_sp_campaigns` performance to correlate changes with metrics

### J. Campaign Optimization Recommendations

1. `ads_sp_campaign_recommendations` operation=`list` → Amazon-generated recommendations (budget, bid, targeting)
2. Review `data.result.items` with user — each item has `type` and proposed change
3. For accepted recommendations: `ads_sp_campaign_recommendations` operation=`apply`
4. Write applied recommendation IDs to sheet for audit

**Note:** This is NOT keyword suggestions. For keyword suggestions use `ads_sp_recommendations`.

---

## Tier 3: Tool Reference

_Quick lookup only. Body schemas, filter syntax, and per-tool best practices are in
each tool's docstring. This table covers: supported actions and cross-cutting gotchas._

### Sponsored Products (SP)

| Tool | Actions | Cross-cutting notes |
|---|---|---|
| `ads_sp_campaigns` | list / create / update / delete | |
| `ads_sp_ad_groups` | list / create / update / delete | Needs campaignId |
| `ads_sp_keywords` | list / create / update / delete | Needs campaignId + adGroupId |
| `ads_sp_neg_keywords` | list / create / update / delete | Ad group level |
| `ads_sp_campaign_neg_keywords` | list / create / delete | Campaign level — blocks all ad groups; no update |
| `ads_sp_targets` | list / create / update / delete | ASIN / category targeting |
| `ads_sp_neg_targets` | list / create / update / delete | Ad group level |
| `ads_sp_campaign_neg_targets` | list / create / delete | Campaign level; no update |
| `ads_sp_product_ads` | list / create / update / delete | Links ASIN or SKU to ad group |
| `ads_sp_portfolios` | list / create / update | Delete not supported; state only ENABLED via API |
| `ads_sp_recommendations` | — | Pass `type="ranked_keywords"` (preferred) or `type="suggested_keywords"`. ⚠️ The tool's documented default `type="ranked"` / `"suggested"` is **rejected by the route** — use the `_keywords` suffix or the call errors |
| `ads_sp_bid_recommendations` | — | |
| `ads_sp_bulk_create` | — | Full campaign structure atomically |

### SP Analytics & Advanced SP

| Tool | Operations | Cross-cutting notes |
|---|---|---|
| `ads_sp_export` | campaigns_export / adgroups_export / targets_export / ads_export / get_export | Async: submit → poll. When COMPLETED, `data.result.exportData` auto-downloaded. typeExport: "campaigns"\|"adGroups"\|"targets"\|"ads" |
| `ads_sp_history` | — (single call) | `eventTypes` must be object `{"CAMPAIGN": true}` not array. Dates in ms (13 digits). Max 90 days |
| `ads_sp_insights` | — | Requires adType=SD/DSP — may return "Unsupported Media Type" for SP-only accounts |
| `ads_sp_brand_metrics` | post_report / get_report / download_report | Async. Not supported in all marketplaces (e.g. AE) |
| `ads_sp_bid_rules` | create / update / associate / delete | Associate rule to campaign via `campaignId` param |
| `ads_sp_campaign_recommendations` | list / apply / update | Amazon-generated recommendations only — NOT keyword suggestions (use `ads_sp_recommendations` for those) |

### Sponsored Brands (SB)

| Tool | Actions | Cross-cutting notes |
|---|---|---|
| `ads_sb_campaigns` | list / create / update / delete | delete = list of campaignId strings |
| `ads_sb_ad_groups` | list / create / update / delete | |
| `ads_sb_keywords` | list / create / update / delete | |
| `ads_sb_neg_keywords` | list / create / update / delete | **Filter format: comma-strings** — see docstring |
| `ads_sb_targets` | list / create / update / delete | |
| `ads_sb_neg_targets` | list / create / update / delete | |
| `ads_sb_ads` | list / create / update / delete | Creatives (V4) |
| `ads_sb_bid_recommendations` | — | |
| `ads_sb_keyword_recommendations` | — | |

**SB list-filter formats differ by tool** — check each docstring, don't assume:
- Most SB tools (campaigns, ad_groups, keywords, targets, ads): `{"stateFilter": {"include": ["ENABLED"]}}` object form
- `ads_sb_neg_keywords`: comma-strings — `{"stateFilter": "enabled,archived"}`
- `ads_sb_neg_targets`: filters-array — `{"filters": [{"filterType": ..., "values": [...]}]}`

No `ads_sb_portfolios` tool. Assign portfolios via `portfolioId` on create/update; manage in Seller Central.

### Sponsored Display (SD)

**All SD tools use comma-string filters** (e.g. `"stateFilter": "enabled,paused"`) — see each tool's docstring.

| Tool | Actions | Cross-cutting notes |
|---|---|---|
| `ads_sd_campaigns` | list / create / update / delete | delete = archives |
| `ads_sd_ad_groups` | list / create / update / delete | delete = archives |
| `ads_sd_targets` | list / create / update / delete | delete = archives |
| `ads_sd_neg_targets` | list / create / update / delete | delete = archives |
| `ads_sd_product_ads` | list / create / update / delete | delete = archives |
| `ads_sd_bid_recommendations` | — | Body needs `bidOptimization`, `costType`, `targetingClauses` |
| `ads_sd_budget_recommendations` | — | Takes `campaignIds` (list, **max 100**) directly — not a `body` dict |
| `ads_sd_targeting_recommendations` | — | Body needs `tactic`, `products`, `typeFilter` |

### Ads Account Management

| Tool | Operations | Cross-cutting notes |
|---|---|---|
| `ads_account` | list / get / create | Use `list` to discover advertisingAccountIds and profile mappings |
| `ads_invoices` | list / get | `invoiceId` required for `get` |
| `ads_localization` | currency / currency_extended / products / keywords / targeting | `products`/`keywords`/`targeting` require source + target marketplaceId in body |
| `ads_manager_accounts` | list / create / associate / disassociate | Most accounts return empty list — normal for non-agency accounts |
| `ads_metadata` | — (single call) | Body: `{"asins": [...], "adType": ...}` or `{"skus": [...], "adType": ...}`. `adType` required; max **100** per request |
| `ads_dsp_advertisers` | — (single call) | Lists DSP advertisers → `advertiserId` for DSP report filters. **Requires an AGENCY-type profile**; seller/vendor profiles return 400 "not agency" (no DSP seat) |
| `ads_brand_home` | — (single call) | Returns `{brandId, brandEntityId, brandRegistryName}` for every brand under this profile |
| `ads_stores` | — (asset library) | GET `/stores/assets`. Use the **ads-account entityId** from `ads_account.alternateIds` (not a per-brand ID from `ads_brand_home`). Assets at brand-level return empty; `mediaType` filter effectively accepts only `brandLogo` |
| `ads_store_insights` | `type='asin_metrics'` (engagement) / `'insights'` (traffic & SQS) | Requires `brandEntityId` from `ads_brand_home`. Store-aggregate `asin_metrics` only accepts `TOTAL_VIEWS`/`TOTAL_CLICKS`; `insights` accepts exactly one non-SQS metric per call |
| `ads_streams` | list / create / update / get | `subscriptionId` required for `get`/`update`. Most accounts return empty list |
| `ads_validation_configs` | campaigns / targeting | Large payload (~200KB+). Use before building campaign creation bodies |

### Performance Data Tools

| Tool | When |
|---|---|
| `query_report_data` | Default for all analysis |
| `ads_create_report` | Offline report — 30 min to hours; write reportId to sheet immediately. Build `body` from `reference/report-configs/` (full SP/SB/SD/STV/DSP catalog) |
| `ads_get_report` | Poll when user returns; write rows when COMPLETED |

### Synced Report Tables

**SP:** `rpt_sp_campaigns`, `rpt_sp_ad_groups`, `rpt_sp_keywords`, `rpt_sp_targets`,
`rpt_sp_search_terms`, `rpt_sp_advertised_products`, `rpt_sp_purchased_products`,
`rpt_sp_campaign_placement`, `rpt_sp_negative_keywords`,
`rpt_sp_campaign_negative_keywords`, `rpt_sp_negative_targets`,
`rpt_sp_campaign_negative_targets`

**SB:** `rpt_sb_campaigns`, `rpt_sb_ad_groups`, `rpt_sb_keywords`, `rpt_sb_targets`,
`rpt_sb_search_terms`, `rpt_sb_advertised_products`, `rpt_sb_purchased_products`,
`rpt_sb_negative_keywords`

**SD:** `rpt_sd_campaigns`, `rpt_sd_ad_groups`, `rpt_sd_targets`,
`rpt_sd_advertised_products`, `rpt_sd_negative_targets`

The negative-entity and placement tables let you audit current negatives and
placement-level performance without an entity-list call.

These are **daily performance rows** — a campaign with no delivery in the window has no row, so
never derive "how many campaigns exist" from them; call `ads_sp_campaigns` (or the SB/SD
equivalent) for that. Prefer `report_date: "all"` + date filters over `"latest"` when analysing
cost or performance, since `"latest"` may land on a zero-spend partial day.

Common SP column names (verify others in the reference json before filtering): `cost`,
`clicks`, `impressions`, `purchases_14d`, `sales_14d`, `acos_clicks_14d`,
`acos_clicks_7d`. **Column names are snake_case** — not the camelCase used in
`ads_create_report` columns (e.g. warehouse `sales_14d` vs report-config `sales14d`).

For column names: load the `report-data` skill or read
`.claude/skills/report-data/reference/<table>.json`.

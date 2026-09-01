---
name: amazon-ads
description: Guide for managing Amazon Advertising (SP, SB, SD) using SellerSheet MCP tools. Use when working with Amazon Ads campaigns, ad groups, keywords, targets, bids, budgets, bulk creation, negative keywords, ad performance data, bulk exports, change history, account management, invoices, or validation configs.
version: 0.11.8
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
surfaces v1 doesn't cover: portfolios, every recommendation endpoint, exports,
change history, brand metrics, budget rules / budget usage, and offline
reports. **Rule of thumb: entity CRUD (campaigns, ad groups, ads, targets
incl. keywords + negatives) goes through v1; everything else is legacy by
necessity, not preference.** `ads_sp_bulk_create` is v1 too — it orchestrates
the v1 creates server-side (campaign → ad group → targets → ads, ids chained,
per-step results).

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
ENABLED vs 21 in the warehouse, observed). For a complete campaign inventory or count, query the
live API — `ads_campaigns` action=query (v1, all products in one call via
`adProductFilter`). And `report_date: "latest"`
pins to the newest **single** day, often a zero-spend partial day — use `report_date: "all"` plus
explicit date filters for any cost or performance analysis.

### 4. Ad Type Hierarchy

```
Campaign → Ad Group → Keywords / Targets → Product Ads
```

- **SP and SB**: full hierarchy
- **SD**: `Campaign → Ad Group → Targets + Product Ads`

Resolve IDs top-down before creating child entities — `ads_campaigns` /
`ads_ad_groups` action=query to get IDs.

### 5. Campaign & Ad Group Naming Convention

Every campaign you create — via `ads_campaigns` or `ads_sp_bulk_create` —
must follow this format. Audit existing campaigns against it before any
rollout; flag deviations to the user.

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

### 6. Budget Rule Naming Convention

Budget rules are **permanent objects** (Amazon has no rule-delete API) that
stack additively when satisfied together — an anonymous rule is an
unattributable budget multiplier. Every rule the agent creates follows:

```
BR_<Country>_<SCH|PERF>_<Trigger>_P<Pct>_<Window>
```

- `Trigger`: event tag (`PRIMEDAY`, `BFCM`, …) or `DTRANGE` for SCHEDULE; the
  metric (`ACOS` `ROAS` `IS` …) for PERFORMANCE.
- `Window`: `YYYYMMDD-YYYYMMDD`, or `YYYYMMDD-OPEN` when open-ended.
- Examples: `BR_US_SCH_PRIMEDAY_P30_20260713-20260714`,
  `BR_AE_PERF_ACOS_P20_20260801-OPEN` (this shape is live-verified accepted).
- Track every created rule in the workbook's `Budget Rules Registry` tab keyed
  by `ruleId` — the name is the human handle, the registry is the identity
  system. Full artifact schemas: `reference/budget-rules.md` §10.

### 7. Budget Autonomy Boundaries

Applies on top of the global sheet-approval convention (§2):

- **Read freely, then report** — usage polling, recommendations, rule
  list/get/list_for_campaign, registry reconciliation: no approval needed;
  nothing changes on Amazon.
- **Every mutation waits for the sheet** — base-budget edits, portfolio caps,
  rule create/update/associate, and pause/disassociate of rules the agent
  created: write the intent row (`approval=PENDING`) with before/after values
  and evidence to `Budget Change Log`, relay `human_action`, and do not call
  the mutating tool until the operator approves.
- **Never touch rules you don't own** — a rule found on Amazon that is not in
  the registry (`created_by` console/unknown) may be a load-bearing manual
  control: flag it, propose, let the operator act.
- **`Budget Caps` is the operator's envelope** — max budget, max single
  increase %, max stacked rule %, target ACOS per scope. Discuss and set it
  WITH the operator on first budget engagement; any proposal exceeding a cap is
  flagged, never applied; an absent cap row is never an approval.

---

## Tier 2: Workflow Recipes

### A. Account Health Check

1. `query_report_data` on `rpt_sp_campaigns`, `rpt_sb_campaigns`, `rpt_sd_campaigns`
   — `report_date: "all"` plus a trailing-N-day date filter (never `"latest"`
   for cost totals — it can land on a zero-spend partial day), sort by `cost`
   desc (`cost` is the one spend column present on all three tables)
2. Compute totals — **the metric columns differ by product**: SP has
   `cost`/`spend` + `sales_14d` + `purchases_14d`; SB and SD have `cost` +
   `sales` + `purchases` (no `_14d`-suffixed columns at all). ACoS =
   `cost / sales * 100` on the product's own sales column; plus impressions, clicks
3. Flag campaigns with ACoS above target or zero sales (SP: `sales_14d = 0`;
   SB/SD: `sales = 0`)
4. Write summary to sheet

### B. Find Wasted Spend

1. `query_report_data` on `rpt_sp_keywords` — filter `cost > threshold AND purchases_14d = 0`
2. `query_report_data` on `rpt_sp_search_terms` — same filter
3. Repeat for SB: `rpt_sb_keywords`, `rpt_sb_search_terms` — filter
   `cost > threshold AND purchases = 0` (SB/SD tables carry no 14d-suffixed
   columns)
4. Repeat for SD: `rpt_sd_targets` — `cost > threshold AND purchases = 0`
5. Write waste list to sheet → propose negatives to user

### C. Bid Optimization

1. `query_report_data` on `rpt_sp_keywords` — get `cost`, `sales_14d`, `clicks` per keyword
2. Calculate ACoS per keyword; compare to target
3. Resolve each keyword's `targetId`: `ads_targets` action=query (v1) with
   `adProductFilter` + `keywordFilter` (keywords ARE targets in v1)
4. Over-target: write bid-down intent to sheet; under-target with good volume:
   write bid-up intent → `ads_targets` action=update, items
   `{targetId, bid: {bid: <amount>}}` — read `reference/ads-v1/targets.md` first
5. Same v1 tool covers SB keywords and SD targets (change `adProductFilter`)

### D. Launch New Campaign (Bulk SP)

1. `ads_sp_recommendations` — ranked keywords (`type="ranked_keywords"`, the
   default) for target ASINs
   (product-target ideas: `ads_sp_product_suggestions` /
   `ads_sp_category_suggestions` + `ads_sp_category_refinements`)
2. `ads_sp_bid_recommendations` — suggested bids for selected keywords/targets;
   starting daily budget from `ads_sp_initial_budget_recommendation`
3. Write full campaign spec to sheet for user review
4. `ads_sp_bulk_create` — the whole structure in one call on the unified v1
   API: campaign + ad groups + product ads + targets. **The spec is
   v1-native**: every target item is `{targetType, targetDetails, bid?,
   state?}` with `targetDetails` exactly as `ads_targets` takes them
   (keywords are `KEYWORD` targets; negatives are `negativeTargets` lists;
   campaign-level negatives sit on the spec root). The request is strictly
   validated and preflighted (name collisions, ASIN→SKU) BEFORE anything is
   created — a bad payload is rejected whole with a field path, never
   part-created. Ids are chained server-side with per-step results per
   campaign (`SUCCESS`/`PARTIAL`/`ERROR`).
5. Write returned campaignId + adGroupIds to sheet. A `PARTIAL` row is
   resumed by re-calling with that row's `campaignId` (and each created
   `adGroupId` with its `defaultBid`) — creation is skipped for anything
   carrying an id and only missing children are created. Building
   entity-by-entity instead? `ads_campaigns` → `ads_ad_groups` →
   `ads_targets` → `ads_ads`, reading `reference/ads-v1/` first — SP creates
   require `marketplaceScope`/`marketplaces`/`startDateTime`, budget nests as
   `budgetValue.monetaryBudgetValue.monetaryBudget.value`, and an SP ad group
   cannot mix keyword and product targets

### E. Negative Keyword Mining

1. `query_report_data` on `rpt_sp_search_terms` — filter `cost > threshold AND purchases_14d = 0`
2. Group by campaign / ad group; review candidates with user
3. Write negatives intent to sheet
4. Create negatives with `ads_targets` action=create (v1): items carry
   `negative: true` + `keywordTarget {keyword, matchType}`; scope with
   `adGroupId` (ad-group negative) or `campaignId` alone (campaign negative —
   blocks all ad groups). One tool for SP and SB; audit existing negatives
   first with action=query + `negativeFilter {include: [true]}` (or the
   synced `rpt_*_negative_*` warehouse tables). Read
   `reference/ads-v1/targets.md` before composing.

### F. Budget Management

**Read `reference/budget-rules.md` before any budget work** — payload shapes
(create vs update are asymmetric), per-product deltas, the rule status
lifecycle, live-verified behaviors, guardrail numbers, and the standing sheet
tabs (`Budget Rules Registry` / `Budget Change Log` / `Budget Caps`). Budget
management is four sub-recipes on different cadences (v1 is operator-invoked —
run when asked; once the routine stabilizes, suggest scheduling, don't set it
up unprompted):

| Sub-recipe | Cadence | Standing artifact |
|---|---|---|
| F1 Pacing & budget changes | morning ask (+ optional afternoon) / weekly review | `Budget Change Log` |
| F2 Event rule lifecycle | T-14 plan → T-3 arm → T-0 verify → T+1 teardown | `Budget Rules Registry` |
| F3 Performance rules | set once, review monthly | `Budget Rules Registry` |
| F4 Rule audit & reconciliation | monthly + after every event | `Budget Rules Registry` |

First budget engagement on a store: probe capabilities (SB event recs are
marketplace-gated, bulk association 401s, intraday is 5-marketplace-only — see
reference §8) and **discuss `Budget Caps` with the operator** — propose values,
write the tab together; it is human-owned and re-read every mutating run.

**F1 — Pacing & budget changes**

1. `ads_budget_usage` on the top ~20 campaigns by trailing-7d spend AND
   adProduct=`PORTFOLIOS` in the same sweep (a bound portfolio silently stops
   every member campaign). Judge `usage% ÷ expected-by-this-local-hour`, never
   raw % — curve in reference §9. Relay `usageUpdatedTimestamp`: it can lag
   hours, and zero-spend campaigns report a synthetic midnight stamp.
2. For flagged campaigns, `query_report_data` on `rpt_*_campaigns`
   (`report_date: "all"` + date filter) for trailing-7d ACOS.
3. **Route by the 2×2 + preflight (reference §1)** — hot AND unprofitable is a
   bid problem (Recipe C), never a raise; usage <85% EOD means budget is not
   the limiter regardless of what `ads_*_budget_recommendations` suggests.
4. A permanent constraint gets a base-budget edit (`ads_campaigns` action=update
   (v1) — budget nests as
   `budgets[0].budgetValue.monetaryBudgetValue.monetaryBudget.value`; +20–30%
   steps); a
   temporary/conditional one gets a rule (F2/F3). Write the intent row
   (`approval=PENDING`) to `Budget Change Log`, wait for operator approval,
   apply, read back, record the result.

**F2 — Event rule lifecycle (Prime Day, BFCM, …)**

1. **T-14:** `ads_budget_rules_recommendation` per candidate campaign (SP|SB,
   one campaignId per call; empty list = no upcoming events, normal). Plan
   uplifts with the operator — and plan the **bid** raises too: event CPCs run
   30–60% over baseline, budget-only uplift on a non-capped campaign does
   nothing.
2. **T-3:** per approved campaign: `list_for_campaign` (stack check, reference
   §7) → `ads_budget_rules` create (SCHEDULE + `eventTypeRuleDuration
   {eventId}`, name per the BR_ convention) → `associate` per campaign →
   read back status: `PENDING_START` is the healthy pre-window state — never
   re-create because it isn't `ACTIVE` yet.
3. **T-0:** verify `ACTIVE` + `ads_budget_usage` shows the raised budget; write
   a sheet snapshot each poll — **for SB/SD this snapshot is the only audit
   record that will ever exist** (no report columns).
4. **T+1:** confirm `EXPIRED`, measure the revert, disassociate + pause (no
   delete API), **revert the manual event bid raises** (bids don't
   auto-revert), run the F4 orphan sweep.

**F3 — Performance rules**

Only on proven winners: ≥14 days delivery, volume above the reference §9
floors, campaign comfortably above Amazon's minimum budget. Threshold at
0.75–0.85 × target ACOS (never AT target — the trailing-7d window whipsaws),
increase +25% default. Metric enums differ by product (SP/SD ACOS|CTR|CVR|ROAS,
SB IS|NTB|ROAS; `EQUAL_TO` SP-only; SP recurrence DAILY-only). After create +
associate, read back status — `BUDGET_THRESHOLD_NOT_MET` means the rule is
silently inert. Never use a performance rule to rehabilitate a loser: the
budget cap is what limits the loss.

**F4 — Rule audit & reconciliation**

Monthly + after every event: `ads_budget_rules` list (page to exhaustion) ×
SP/SB/SD, reconcile against `Budget Rules Registry`, classify orphans (active
with zero associations, rules on archived campaigns, expired-still-associated).
Rules not created by this agent or the operator are flag-only — never touch
them. For month close, SP's v3 `spCampaigns` report rule columns attribute
spend to rules day-by-day (SP only; SB/SD reconstruct from the sheet ledger).
For a NOT-yet-created SP campaign's starting budget use
`ads_sp_initial_budget_recommendation` (launch flow, Recipe D).

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

### Unified v1 — PREFERRED for entity CRUD

_One common-model surface over `/adsApi/v1/*` for SP / SB / SD / Sponsored TV /
DSP. Read `reference/ads-v1/<entity>.md` before composing any create/update
body; live-verified gotchas in `reference/ads-v1/README.md`._

| Tool | Actions | Cross-cutting notes |
|---|---|---|
| `ads_campaigns` | query / create / update / delete | `query` requires `adProductFilter`; paginate by resending the SAME filters + `nextToken`. SP create requires `marketplaceScope`, `marketplaces`, `startDateTime`, `autoCreationSettings`, `budgets`; budget nests `budgetValue.monetaryBudgetValue.monetaryBudget.value` |
| `ads_ad_groups` | query / create / update / delete | |
| `ads_ads` | query / create / update / delete | SP creative: `productIdType` = `SKU` (sellers) / `ASIN` (vendors). A schema-valid create can still fail per-index `PRODUCT_INELIGIBLE` |
| `ads_targets` | query / create / update / delete | Keywords, product/category targets, AND all negatives in one resource (`negative` flag; campaign-level negative = `campaignId` without `adGroupId`). `productTarget.product` is an OBJECT `{productId}`. An SP ad group cannot mix keyword and product targets. Bid update = `{targetId, bid: {bid}}` |
| `ads_ad_associations` | query / create / update / delete | Amazon DSP only — sponsored-ads profiles get 401 |

Shared v1 gotchas: mutations return 207 `{success[], partialSuccess[], error[]}`
even when everything failed — always read `error[]`; `delete` takes
`{"<entity>Ids": [...]}` and ARCHIVES (entities stay queryable).

### Sponsored Products (SP)

| Tool | Actions | Cross-cutting notes |
|---|---|---|
| `ads_sp_portfolios` | list / create / update | Delete not supported; state only ENABLED via API |
| `ads_sp_recommendations` | — | Use `type="ranked_keywords"` — the deployed default; returns ranked keywords with per-match-type suggested bids. `type="suggested_keywords"` hits endpoints Amazon shut off 2026-06-15 → 403, **never use** |
| `ads_sp_bid_recommendations` | — | |
| `ads_sp_product_suggestions` | — | Suggested target ASINs (competitor/complementary) for your advertised ASINs, with the theme that produced each |
| `ads_sp_category_suggestions` | — | Category targets recommended for a list of ASINs — the coarse half of product targeting |
| `ads_sp_category_refinements` | — | Brand / age-range / genre facets targetable WITHIN one category (narrow a category target) |
| `ads_sp_negative_brands` | recommendations / search | Brands to exclude as negative brand targets — Amazon's recommended exclusions, or search by keyword |
| `ads_sp_bulk_create` | — | Full campaign structure in one call — v1-native spec (Recipe D) |

_SP entity CRUD (campaigns, ad groups, keywords, targets, negatives, product
ads) is the Unified v1 table above — there are no per-product CRUD tools._

### SP Analytics & Advanced SP

| Tool | Operations | Cross-cutting notes |
|---|---|---|
| `ads_sp_export` | campaigns_export / adgroups_export / targets_export / ads_export / get_export | Async: submit → poll. When COMPLETED, `data.result.exportData` auto-downloaded. typeExport: "campaigns"\|"adGroups"\|"targets"\|"ads" |
| `ads_sp_history` | — (single call) | `eventTypes` must be object `{"CAMPAIGN": true}` not array. Dates in ms (13 digits). Max 90 days |
| `ads_sp_insights` | — | Requires adType=SD/DSP — may return "Unsupported Media Type" for SP-only accounts |
| `ads_sp_brand_metrics` | post_report / get_report / download_report | Async. Not supported in all marketplaces (e.g. AE) |
| `ads_sp_bid_rules` | create / update / associate / list / delete | Run `list` first to see existing rules. Associate rule to campaign via `campaignId` param |
| `ads_sp_campaign_recommendations` | list / apply / update | Amazon-generated recommendations only — NOT keyword suggestions (use `ads_sp_recommendations` for those) |

### Sponsored Brands (SB)

| Tool | Actions | Cross-cutting notes |
|---|---|---|
| `ads_sb_bid_recommendations` | — | |
| `ads_sb_keyword_recommendations` | — | |

_SB entity CRUD (campaigns, ad groups, keywords, targets, negatives, ad
creatives) is the Unified v1 table above._ No `ads_sb_portfolios` tool —
assign portfolios via `portfolioId` on campaign create/update; manage in
Seller Central.

### Sponsored Display (SD)

| Tool | Actions | Cross-cutting notes |
|---|---|---|
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

### Budget Tools

_Before composing any budget-rule payload or proposing a budget change, read
`reference/budget-rules.md` — create/update shape asymmetry, per-product enum
deltas, rule status lifecycle, stacking guardrails, and the standing sheet
artifacts._

| Tool | Operations | Cross-cutting notes |
|---|---|---|
| `ads_budget_usage` | — (adProduct SP\|SB\|SD\|PORTFOLIOS) | Live intraday % of budget consumed, 1-100 ids, 207 success[]/error[] envelope |
| `ads_budget_rules` | list / create / update / get / list_campaigns / list_for_campaign / associate / disassociate / bulk_associate / bulk_disassociate | One tool for SP\|SB\|SD via adProduct. bulk_* are SP-only and return 401 — the bulk surface is not granted (verified on every tested account/marketplace), so always use per-campaign associate/disassociate; do not retry per account. Create body = FLAT rule details; update body = {ruleId, ruleDetails, ruleState} wrappers with ONLY mutable ruleDetails fields. ≤25 rules/assoc ids, ≤50 bulk pairs. Mutating ops need ads write access |
| `ads_budget_rules_recommendation` | — (adProduct SP\|SB) | Special-event suggestions for ONE campaignId; response eventId feeds eventTypeRuleDuration. SD not supported by Amazon; some marketplaces reject SB event rules |
| `ads_sp_budget_recommendations` / `ads_sb_budget_recommendations` / `ads_sd_budget_recommendations` | — | Suggested daily budget + missed-opportunity estimates per campaign; 1-100 ids (SD takes `campaignIds` directly, not a `body` dict) |
| `ads_sp_initial_budget_recommendation` | — | Budget suggestion BEFORE campaign creation; targetingExpressions are objects and each requires a `bid`; targetingType is lowercase 'auto'\|'manual' |

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
never derive "how many campaigns exist" from them; query the live `ads_campaigns`
tool for that. Prefer `report_date: "all"` + date filters over `"latest"` when analysing
cost or performance, since `"latest"` may land on a zero-spend partial day.

Common SP column names (verify others in the reference json before filtering): `cost`,
`clicks`, `impressions`, `purchases_14d`, `sales_14d`, `acos_clicks_14d`,
`acos_clicks_7d`. **Column names are snake_case** — not the camelCase used in
`ads_create_report` columns (e.g. warehouse `sales_14d` vs report-config `sales14d`).

For column names: load the `report-data` skill or read
`.claude/skills/report-data/reference/<table>.json`.

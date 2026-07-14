---
name: sellersheet-dashboard
description: Use when building or maintaining an Amazon operator dashboard on Google Sheets via SellerSheet MCP — multi-tab status views for inventory, PPC, account health, listings, profit/margin, returns, buy box, cash conversion. Triggers on phrases like "build a dashboard", "operator dashboard", "FBA dashboard", "PPC dashboard", "Amazon overview sheet", "seller dashboard", and on follow-ups like "refresh the dashboard", "add an insight", "the freshness is wrong". Composes the tab plan, applies SellerSheet brand visuals, wires `rpt_*` warehouse data → `_raw_*` tabs → `SQL()` spill → visible tabs with thumbnails, and instruments each cell with provenance + freshness so the dashboard self-explains. Builds on `sellersheet-sheets` (sheet primitives + brand palette + SQL() patterns) and `report-data` (rpt_* tables). NOT for one-off reports — use `sellersheet-sheets` directly for those.
version: 0.8.6
---

# SellerSheet Operator Dashboard

## Prerequisites

Run the standard preflight in [`sellersheet-shared`](../sellersheet-shared/SKILL.md) (installed alongside this skill): `get_user_context` succeeds → version check via `data.skills_catalog` → `data.canUseMcp` is true. **Extra auth for this skill:** full dashboards need **Amazon Advertising profile access** on the store (otherwise PPC tabs render as scaffolds) — verify per the Requirements block below.

---

> **Author**: sellersheetai.com
> **Built for**: Amazon sellers running SellerSheet MCP with their own SellerSheet account
> **Required dependencies**: see Requirements below — read the whole block before starting a build

## Requirements

This skill assumes the operator has all of the following. If any is missing, surface it to the user before building — they need to fix the gap at sellersheetai.com/dashboard first, or accept reduced functionality.

### 1. SellerSheet MCP installed

The full set of `mcp__claude_ai_sellersheet_<env>__*` tools must be available (`<env>` is `prod` or `test` depending on which SellerSheet MCP connector is attached) — see [sellersheetai.com](https://sellersheetai.com) for setup. Confirm by attempting `get_user_context` — should return the user profile + store list.

### 2. At least one Amazon store connected

The user has connected at least one Amazon seller account in their SellerSheet workspace. Each store is identified as `storename-countrycode` (e.g. `myStore-US`, `myStore-UK`, `myStore-DE`).

If `get_user_context` returns zero stores: stop and tell the user to connect a store at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) before this skill can build anything meaningful.

### 3. Ad profile access (Amazon Advertising)

For PPC tabs and ad-attribution columns to populate with real data, the connected store must have **Amazon Advertising profile access** authorized in SellerSheet. Without it, `rpt_sp_campaigns`, `rpt_sp_advertised_products`, `rpt_sp_search_terms` will be empty.

**How to check**: `list_report_syncs(store='<store>')` — if SP-Ads reports are missing or marked `NOT_CONNECTED`, ad profile isn't authorized.

**If missing**: alert the user with this exact message before building:

> ⚠️ **No Amazon Advertising profile access detected for `<store>`.**
>
> The PPC Command tab and ad-attribution columns on Profit and Cash will be scaffolds only — no real campaign data, no ROAS, no per-SKU ad cost. To unlock them, authorize Amazon Ads at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Stores → `<store>` → Connect Advertising profile.
>
> Want me to:
> (a) build the dashboard now with ad sections as scaffolds (operator can add ad access later and the data flows through), or
> (b) wait until you've added ad access at sellersheetai.com/dashboard?

If the user picks (a), proceed but populate ad-related `_raw_*` tabs with sentinel rows (see scaffold pattern in `reference/freshness-system.md`).

### 4. Other tables (optional, alert if missing)

- **Brand Analytics** (`rpt_brand_analytics_*`) — only for Brand Registry sellers. If missing, the Search & Share tab stays as a placeholder.
- **Vendor Retail reports** — only for Vendor accounts. Skip the Vendor section.

## What a SellerSheet operator dashboard looks like

A single Google Sheet, one tab per business function. Every visible tab surfaces **decisions** the operator must make today, not raw data. Every row earns its place by changing a behavior. The whole workbook reads as one brand: emerald `[0.063, 0.725, 0.506]` titles, navy `[0.157, 0.2, 0.318]` column headers, red/amber/green status chips. Hidden `_raw_*` tabs back the visible spills.

**Three layers, one contract:**

```
rpt_* warehouse tables (your SellerSheet data warehouse)
        │  query_report_data() MCP
        ▼
_raw_*   hidden Sheets tabs (one row per source rpt_*)
        │  SQL() function (SellerSheet GAS add-on, browser-side)
        ▼
visible tabs   (emerald + navy + chips + agent insights)
        │  =HYPERLINK("#gid=...")
        ▼
operator reads & decides
```

**`SQL()` only works in a provisioned workbook.** It is a SellerSheet add-on custom function — it
only evaluates in workbooks where the add-on is enabled (a human opened **Extensions → SellerSheet
→ Open** once in *that* workbook). Arbitrary MCP-created spreadsheets show `#NAME?` forever; for
those, write pre-computed values or plain formulas instead. After writing a `SQL()` formula, a
spill cell may read back empty for a few seconds while Sheets recalculates — re-read before
concluding failure.

**`IMAGE()` caveat.** Under some conditions an `IMAGE()` cell written by the service account
renders as `#REF!` ("use desktop browser") for the human until they open the workbook in a desktop
browser. Reading such a cell back via MCP requires `value_render_option='FORMULA'`.

`_status`, `_agent_notes`, `_agent_log` tabs cross-cut the three layers — they record where every cell came from, when, and by whom. See `reference/freshness-system.md` and `reference/agent-insights.md`.

## The standard 8 visible tabs (in order)

| Tab | Business question | Refresh | Source rpt_* tables |
|---|---|---|---|
| **README** | What is this workbook and how do I read it? | Manual | (none) — live freshness table mirrors `_status` |
| **HOME** | What blew up overnight, what do I touch today? | Daily | `rpt_orders`, `rpt_get_v2_seller_performance_report`, `rpt_get_fba_inventory_planning_data`, `rpt_sp_campaigns`, `rpt_get_merchants_listings_fyp_report`, `rpt_get_fba_myi_all_inventory_data` |
| **Inventory and Restock** | What do I reorder, what do I remove? | Every 6h | `rpt_get_fba_inventory_planning_data` + `rpt_get_fba_myi_all_inventory_data` + `listing_images` |
| **PPC Command** | Where is ad money leaking? What's winning? | Daily 03 UTC | `rpt_sp_campaigns`, `rpt_sp_search_terms`, `rpt_sp_advertised_products`, `rpt_sp_ad_groups` · **requires ad profile access** |
| **Account Health** | AHR / ODR / VTR / OTDR / Invoice Defect — am I at risk? | Daily 07 UTC | `rpt_get_v2_seller_performance_report` |
| **Listing Health** | Suppressed / inactive / stranded + buy box | Daily | `rpt_get_merchant_listings_all_data` + `rpt_get_merchants_listings_fyp_report` + `rpt_get_stranded_inventory_ui_data` + `listing_images` + competitive_pricing |
| **Profit and Cash** | Margin after fees + ads + COGS + cash conversion pipeline | Weekly + manual COGS | `rpt_orders`, `rpt_get_flat_file_returns_data_by_return_date`, `rpt_sp_campaigns`, `rpt_get_fba_storage_fee_charges_data`, financial_event_groups + user `_raw_cogs` · **net-of-ads requires ad profile access** |
| **Returns and Refunds** | Return rate, top return SKUs, refund value | Daily | `rpt_get_flat_file_returns_data_by_return_date` + `rpt_get_fba_fulfillment_customer_returns_data` |

Plus **Search & Share** (Brand Analytics: search-term rank, market basket, repeat purchase) — placeholder if BA not enabled.

## Column order — Image, Store, SKU, then everything else

**Every SKU/ASIN table on every visible tab follows this:**

```
A = Image (thumbnail via =IMAGE() — joined from _raw_catalog)
B = Store (canonical storename-countrycode, e.g. "myStore-US")
C = SKU
D = ASIN
E = Product (truncated)
F+  = the rest (qty, price, sales, ACoS, decision, ...)
```

In `_raw_*` tabs the corresponding column order is: `store, sku, asin, image_url, product, ...`. **Set `store` at write time** — the MCP `query_report_data` doesn't echo it back; the caller adds it.

## Layout grammar — every visible tab follows this

```
Row 1     Title (emerald, white bold 18pt)
Row 2     Freshness pill (live formula resolving from _status)
Row 3     Spacer
Row 4+    AT-A-GLANCE / rollup sections (emerald section bands, navy sub-headers)
Row N     Section band for the growable table (the LAST section)
Row N+1   Summary line ABOVE the table
Row N+2   Callout / notes ABOVE the table (yellow background)
Row N+3   Spacer
Row N+4   Image header (A) + SQL() header spill (B onward) — navy bold bg
Row N+5+  Image cells (A) + SQL data (B onward) — open-ended, grows up to LIMIT
Row 215   Overflow footer (1 row below max spill extent if LIMIT 200 is in effect)
Row 150 OR 400   AGENT INSIGHTS section (anchor depends on overflow guard — see reference/agent-insights.md)
```

**Footers never go below the table.** The growable table is always the last data element. AGENT INSIGHTS goes **below the spill with overflow buffer**.

**Every SQL-spilled header row gets a navy background + white bold.** Apply with `format_sheet_range(... background_color=[0.157, 0.2, 0.318], font_color=[1,1,1], bold=True)` to the cell range where the spill's header row lands.

**Every SQL spill MUST end with `LIMIT N`** matching the row budget — see `reference/sql-limits.md` for the per-data-scope defaults.

## Build workflow

When asked to build a dashboard:

1. **`get_user_context`** — confirm store ownership + Brand Analytics + ad profile availability per store. Capture canonical `storename-countrycode` for each store in scope. **If any required dependency is missing, surface to user per the Requirements block above.**
2. **`list_report_syncs(store='<store>')`** — identify which `rpt_*` tables have fresh data; flag disabled ones for README and for scaffold-row decisions.
3. **`list_sheet_tabs(spreadsheet_id)`** — check the target sheet's starting state.
4. **Create tabs in order:** README, HOME, Inventory and Restock, PPC Command, Account Health, Listing Health, Profit and Cash, Returns and Refunds, (Search & Share if BA enabled), then hidden tabs `_raw_inventory`, `_raw_listings`, `_raw_account_health`, `_raw_ppc`, `_raw_ppc_attribution`, `_raw_ppc_search_terms`, `_raw_ppc_skus`, `_raw_cogs`, `_raw_catalog`, `_raw_returns`, `_raw_buybox`, `_raw_finance`, `_config`, `_status`, `_agent_notes`, `_agent_log`.
5. **Build `_status` first** (it's referenced by every visible tab's row-2 pill). See `reference/freshness-system.md` for the schema + how to seed.
6. **Probe each rpt_* table** with a small `query_report_data` aggregation to learn exact column names (`sku` vs `seller_sku` vs `advertised_sku` — they differ; `rpt_get_fba_inventory_planning_data` uses `sku`, the legacy `merchant_sku` was dropped 2026-07-10).
7. **For each non-HOME visible tab:** create the `_raw_<topic>` tab with canonical left-five columns. Populate. Anchor SQL() at the end of the visible tab with the appropriate `LIMIT N` from `reference/sql-limits.md`. Apply navy bg to the spill's header row. Use the Image-at-A JOIN pattern. Apply provenance fills from `reference/provenance-colors.md`. Add the AGENT INSIGHTS section at the right row anchor (row 150 for bounded tabs, row 400 for catalog-scaling tabs). Add the overflow footer right below the max spill extent.
8. **HOME tab:** hand-lay KPI tiles + TOP 3 FIRES section at rows 4-8. Add `=HYPERLINK("#gid=<sheet_id>", "→ Open X")` to drill tabs (pull real `sheetId` from `list_sheet_tabs`).
9. **Seed `_agent_notes`** with 5-10 real insights based on the data you pulled. Three top fires get `scope_key = "fire-1"`, `"fire-2"`, `"fire-3"` so they spill into HOME's TOP 3 FIRES section.
10. **Verify** — run `scripts/post-build-checklist.md` (server-side sweep). Then hand the user the one-time browser approval steps for the final `SQL()` + image-alignment check — **you never open the browser yourself**; that confirmation is theirs.

## Maintenance workflow (refresh, update, alert)

After the dashboard exists, the agent maintains it. See `reference/agent-maintenance.md` for the full loop:

- **Daily refresh** — pull fresh data for each `_raw_*`, update `_status.last_pulled_utc`, regenerate `_agent_notes` for today's fires, append delta-only rows to `_agent_log`.
- **Threshold-triggered alerts** — when status badges flip RED-stale or RED-error, surface to operator.
- **Insight supersession** — when conditions change (threshold no longer breached, fire resolved), mark prior insights `superseded_by` so they drop out of the visible FILTER spills automatically.

## Reference index

Detailed specs live in `reference/`. Always load the relevant file before implementing that part — don't guess from memory.

| File | What's in it |
|---|---|
| `reference/freshness-system.md` | `_status` tab schema, status formula, NOW() incompatibility with SQL(), row-2 freshness pill, `last_pulled_utc` must-be-real rule, per-tab budget table |
| `reference/provenance-colors.md` | 5-color provenance fills (raw / formula / agent / user / config), cell-note JSON-prefix format, visual rules palette (chips, gradients, freshness border) |
| `reference/agent-insights.md` | `_agent_notes` + `_agent_log` schemas, FILTER pattern for inline insights, TOP 3 FIRES on HOME, AGENT INSIGHTS row-150 vs row-400 overflow guard, threshold-triggered self-pruning |
| `reference/agent-maintenance.md` | Daily refresh loop, supersession rules, scheduled-maintenance recipe, alert thresholds |
| `reference/sql-limits.md` | Default `LIMIT N` per `_raw_*` data scope; overflow footer pattern; how to size anchors against spill growth |
| `reference/cogs-schema.md` | Canonical 18-column `_raw_cogs` schema with yellow inputs F/H/J/K, currency suffix rule, common breakages |
| `reference/error-semantics.md` | `#NAME?` (pending) vs `#REF!` (real bug) vs `#ERROR!` vs `#VALUE!`; how to diagnose spill collisions |
| `reference/image-catalog.md` | Single-source `_raw_catalog`, the JOIN-based Image column pattern, bracket-quote rule for SQL() column names + aliases |
| `reference/multi-store.md` | Single-store / multi-store / multi-marketplace modes, locale-required tiles by marketplace (MENA/AU/US/EU), Brand Analytics gating, ad-profile gating |
| `reference/lint-and-rules.md` | 11 mandatory rules (ad cost in margin, FX freshness, concentration risk, dead capital, ...) + 10 lint rules + common mistakes table |
| `reference/grow.md` | Grow checklists: adding a new domain (Returns/Buy Box/Cash), adding a new store |
| `reference/sparklines-deferred.md` | Sparkline pattern (deferred until upstream snapshot retention improves); when to add, wide-format `_raw_*_daily`, per-row sparkline recipe |

## Scripts index

Copy-paste templates and verification routines live in `scripts/`.

| File | What it gives you |
|---|---|
| `scripts/formula-templates.md` | Tested formula library: freshness pill, status formula, FILTER for agent insights, TOP 3 FIRES regex filter, README freshness ARRAYFORMULA spill, image MAP+JOIN, overflow footer |
| `scripts/post-build-checklist.md` | Read-back verification routine — specific cells/ranges to check before declaring done, error-class triage |
| `scripts/seed-status-rows.md` | Template `_status` rows for the 12 standard `_raw_*` tabs with budgets pre-filled |

## Common pitfalls (and where to read more)

- **Row 2 hardcoded date** ("Refreshed 2026-05-12") → must be live formula → `reference/freshness-system.md`
- **`last_pulled_utc` faked** with `=NOW()` or `=DATEVALUE(...)+TIME(...)` → defeats the system → `reference/freshness-system.md`
- **AGENT INSIGHTS placed at row 60** → SQL spill collides → `#REF!` everywhere → `reference/agent-insights.md`
- **`_status` read by SQL()** → fails because column I has `NOW()` → use ARRAYFORMULA per column → `reference/freshness-system.md`
- **`_raw_cogs!F1` mislabeled** as anything other than `selling_price_{ccy}` → Profit and Cash SQL silently returns empty → `reference/cogs-schema.md`
- **Bare-word SQL column names** (`SELECT store AS Store`) → `SQL()` parser error → bracket-quote everything → `reference/image-catalog.md`
- **Spill exceeds AGENT INSIGHTS anchor** → `#REF!` → add `LIMIT N` per `reference/sql-limits.md` and overflow footer
- **Ad profile not connected** but PPC tab built without alerting user → operator confused why ad data is empty → check + alert per Requirements block

## When NOT to use this skill

- A one-off CSV-to-Sheets report — use `sellersheet-sheets` primitives directly.
- A report that should be a Docs page, not a Sheets workbook — use the docs-* MCP tools instead.
- A sheet that lives entirely server-side and is never opened in a browser — the `SQL()` pattern doesn't render.
- A `.xlsx` file download (not Drive) — use the `xlsx` skill.

## Building for first-time users

When working with an operator who's never used this dashboard pattern:

1. Show them the **Requirements** block above and confirm all four dependencies before starting.
2. Ask which **stores** they want in scope. If multi-store, plan for currency-normalized HOME tiles.
3. Ask which **time horizons** matter to them (default: 7d, 30d, T30 trailing).
4. Confirm they understand the **first-open** prompt: Sheets will ask "Allow access to external images" once — needed for product thumbnails. The SellerSheet add-on must be enabled (Extensions → SellerSheet → Open) for `SQL()` to evaluate.
5. After build, walk them through the README — especially the live freshness table (so they see how staleness surfaces) and the color legend (so they decode the cells they look at).

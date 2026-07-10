# Lint rules + mandatory rules

Hard constraints every dashboard must satisfy. Failing any of these makes the dashboard misleading or unmaintainable.

## 11 mandatory rules (codified from operator + engineering critique)

These are non-negotiable. The dashboard is misleading without them.

### 1. Ad cost MUST flow into margin

Never show profit or margin in Profit and Cash without subtracting per-SKU ad cost. A SKU at +7% gross margin can be 0% or negative net once PPC is included. The COGS table must SELECT both `profit_marketplace` (gross of ads) and `net_margin_after_ads` (gross − `ad_cost_per_unit_t30`) so the operator sees the gap.

Join `_raw_ppc` to `_raw_cogs` on SKU/ASIN. Ad-cost-per-unit ≈ `_raw_ppc.cost_<window> / max(_raw_ppc.purchases_<window>, 1)`. Use the longest available window (30d preferred).

### 2. FX rate freshness + staleness alert

Every FX rate in `_config!fx_rates` has an `as_of` column. The HOME tab includes a freshness tile:

- `=MAX(_config!C2:C)` → "FX last refreshed: <date>"
- Conditional red if older than 14 days
- Optional: `=GOOGLEFINANCE("CURRENCY:CNY<MKT>")` next to stored rates for drift comparison

AUD swings 0.62–0.71 USD over 12 months → a 7% gross margin flips negative on a 3% AUD drop. Static rates kill margins silently.

### 3. Currency-normalize HOME tiles

Where two stores' revenue appear side-by-side (AE + AU, US + EU, etc.) the operator can't compare AED vs AUD directly. Add a synthetic comparable column — USD equivalent or RMB equivalent — using rates from `_config!fx_rates`. **Never display two different currencies in the same KPI column** without a normalized companion.

### 4. Concentration risk tile

For each store, compute `MAX(sku_revenue_t30) / SUM(store_revenue_t30)` from `_raw_inventory.sales_t30`. If >70%, surface as a red HOME LEAD tile: `Concentration: SKU X = NN% of <store> revenue — single point of failure`.

### 5. Dead-capital tile

For each store on HOME: `SUM(available × landed_<currency>)` over SKUs with `units_t30 = 0 AND available > 0`. That's the marketplace-currency value of dormant inventory. Where COGS is missing, fall back to `your_price × 0.4` and mark the cell yellow.

### 6. Inbound visibility

`_raw_inventory.inbound` must surface in the visible Inventory table after `available`. EXCESS / restock decisions on `available` alone are dangerous when 200 units are already on the water. Decision logic should consider `available + inbound` as effective stock.

**Restock-qty null fallback.** Amazon's replenishment columns on `rpt_get_fba_inventory_planning_data` are `recommended_order_quantity` + `recommended_order_date` (join on `sku` — the legacy `merchant_sku` was dropped 2026-07-10; `recommended_replenishment_qty` exists only for pre-migration historical rows). `recommended_order_quantity` is frequently NULL — Amazon didn't compute a recommendation for that SKU/marketplace, or a data gap. When it is NULL, do NOT show a blank reorder cell: compute your own suggestion from velocity —

```
suggested_ship_in = MAX(0, ROUND(units_shipped_t30 / 30 × target_cover_days) − available − inbound)
```

— and **label it as computed, not Amazon's** (e.g. tag the cell `computed` in its provenance note, or suffix the header "(est.)"). Never present a computed reorder number as an Amazon recommendation.

**`days_of_supply` NULL sorting.** `days_of_supply` is NULL for no-sale SKUs. The warehouse (Postgres) sorts NULLs LAST on ASC — safe. The in-sheet `SQL()`/alasql layer sorts blanks FIRST — that's where unsorted-looking "urgent" lists come from. Filter `days_of_supply > 0` in either layer (also excludes no-sale SKUs, usually the intent).

### 7. Per-store subtotal rows on Inventory

Above the SQL spill, place two computed rows showing per-store SKU count and at-risk capital. SUMIFS or QUERY against `_raw_inventory`, scoped by Store. Operators budget removal orders per market, not in aggregate.

### 8. README must reflect what exists

Never list a tab in README that isn't built. Never list color chips that aren't used in the current decision set. README lies erode trust in everything else. If a tab is BA-gated and not built, mention it as a future state in the freshness model section, not as a real tab.

### 9. HOME hyperlinks must be real

`=HYPERLINK("#gid=<sheet_id>", "→ Open X")` — pull the actual `sheetId` from `list_sheet_tabs`. Plain-text arrows aren't clickable.

### 10. Regional seasonality + tax-defect surfacing

See `reference/multi-store.md` for the full locale-required tile table. Highlights:
- MENA: Ramadan + Eid calendar; HOME LEAD tile "Days to next peak event"
- AU/NZ: Boxing Day, Click Frenzy, Black Friday, LTSF aging buckets at 181/271/365d
- VAT/GST defect surfacing must name the Seller Central setting that fixes it

### 11. COGS coverage gate

If `_raw_cogs` rows cover <80% of T30 revenue, the Profit and Cash net-margin column is misleading. Surface a banner "COGS coverage: X% of T30 revenue. Numbers below are partial until you fill yellow cells."

## 10 lint rules (operational guardrails)

Every dashboard PR runs against these. Codified from build failures we've actually hit.

1. **One tile, one source.** HOME's "Top SKU 30d" must not compute the same number from a different time window than Inventory and Restock's `sales_t30`. If they differ, the lower-fidelity tile gets a `(rough — see <tab>)` suffix automatically.

2. **No hardcoded numbers.** Row 2 of every visible tab references `_status`, never a literal date. No hardcoded "fresh 2026-05-11" strings.

3. **No hardcoded `:1000` ranges.** All SQL spills use open-ended `A:Z` / `A2:A`. Locked row counts silently truncate at multi-store growth.

4. **AGENT INSIGHTS below the spill, with overflow guard.** Row 150 for bounded tabs (<130 rows); row 400 for catalog-scaling tabs (Inventory, Listings, Profit and Cash). See `reference/agent-insights.md`.

5. **No carpet cell notes.** One note per provenance-tinted cell; raw data tabs get one note on A1 only.

6. **`last_pulled_utc` is a real ISO timestamp** — never `=NOW()`, never `=DATEVALUE(...)+TIME(...)`, never a future date. See `reference/freshness-system.md`.

7. **`_raw_cogs` headers match the canonical 18-column schema** — column F is `selling_price_{ccy}`, not anything else. See `reference/cogs-schema.md`.

8. **`_status` is never read by `SQL()`** — column I contains `NOW()` and breaks the SQL function. Use `ARRAYFORMULA` per-column or array literals. See `reference/error-semantics.md`.

9. **`#REF!` and `#ERROR!` are real bugs.** Only `#NAME?` on `=SQL(` cells is the documented pending state. See `reference/error-semantics.md`.

10. **Scaffold raw tabs carry an A2 sentinel row** with `NOT_YET_SYNCED` / `NO_COGS_ENTERED_YET` marker.

## Image / SQL alignment rules

### Image spills track SQL order, not raw order

Image column on every visible SKU/ASIN table must consume the SQL output's row order, not the `_raw_*` natural order. If the operator ever sorts a `_raw_*` tab manually, the raw-anchored FILTER+MAP image column silently desyncs from the visible SQL rows.

**Canonical pattern:** see `reference/image-catalog.md`. The visible table's data SQL and the image MAP+SQL must use the **same** `ORDER BY`, `WHERE`, and `LIMIT`.

### The user's one-time browser approval is mandatory before declaring done — you never open the browser

Server-side `read_sheet` cannot catch two classes of bugs:

1. **SQL() syntax errors from reserved-word column names.** Cells show `#NAME?` server-side regardless — both correct and broken SQL render identically until the add-on evaluates them in a browser.
2. **Image-column off-by-one alignment.** `IMAGE()` cells are blank pre-Allow-Access, so alignment with SKU rows can't be visually verified until after the consent prompt.

**Rule:** before declaring a dashboard done, hand the user the one-time browser approval steps — **Extensions → SellerSheet → Open**, click "Allow access to external images" once, and Allow access on any `IMPORTRANGE` prompt — and ask them to walk every SKU table to confirm Image-Store-SKU rows align. Never open or drive the browser yourself; that render check is the user's.

### `_config` cells must be named ranges before any consumer reference

Direct `_config!$B$2`-style references are banned. Define named ranges (`cfg_fx`, `cfg_fx_asof`, `cfg_ship_rmb_kg`, `cfg_referral_pct`) and use those everywhere. A single row insert in `_config` will silently break every `$A$1`-style reference; named ranges survive.

### Wildcard SUMIFS for cost attribution is forbidden

Never use `SUMIFS(spend, name, "*"&REGEXEXTRACT(sku,...)&"*")` to attribute ad cost (or any per-SKU cost) to a SKU. The wildcard matches campaign names containing the SKU prefix — which over-attributes when one campaign promotes multiple sizes/variants (e.g., `KW_SKU-A` matches SKU-A-Queen, -King, -Single — each row eats the full spend, triple-counted).

**Rule:** any per-SKU cost must come from a precomputed attribution table with explicit `(store, sku, value)` keys. For PPC, that means a `_raw_ppc_attribution` tab populated from `rpt_sp_advertised_products` (real SKU-level attribution), not derived from campaign-name regex.

## Common mistakes table

| Mistake | Symptom | Fix |
|---|---|---|
| Title bar navy instead of emerald | Visual inconsistency across tabs | `[0.063, 0.725, 0.506]` on row 1 of every visible tab |
| Image column NOT at column A on a SKU table | Operator can't recognize SKUs quickly | Move image to A, push SKU to B |
| `IMAGE()` inside `ARRAYFORMULA` | `#REF!` even after Allow Access | Use `MAP(FILTER(...), LAMBDA(url, IF(url="","",IMAGE(url))))` |
| Closed SQL range `_raw_x!A1:M77` | Table doesn't grow when raw data is appended | Open range `_raw_x!A1:M` |
| Footer / summary BELOW the table | Growth collides; user has to manually push notes down | Always put footers ABOVE the table |
| Decision color chips on fixed cell range (`B6:B31`) | Chips don't move when sorting changes | Conditional formatting on open range (`B9:B1000`) keyed to cell value |
| `=` or `+` as first char of a plain-text cell | Renders as `#ERROR!` | Drop the leading char or prefix with apostrophe |
| Date format on a column that holds numbers (after layout shift) | Numbers render as `1899-12-30` | Reset to NUMBER format |
| Per-column array formulas (`={"Decision";...}` × 13) | Verbose, multiple sources of truth, drift risk | Replace with ONE `SQL("SELECT ... FROM ?", _raw_*!A1:M)` |
| Missing Store column on a SKU/ASIN table | Row scope ambiguous; AI can't echo store back | Always include `store` in `_raw_*` (col A) and visible tab (col B) |
| Querying for one store but forgetting to populate `store` column on rows | `_raw_*` rows arrive without the identifier | Set Store value on each row at write time |
| Hardcoded "Refreshed YYYY-MM-DD" in row 2 | Dashboard pretends to be live | Replace with `TEXTJOIN` referencing `_status` |
| `=DATEVALUE("2026-05-12")+TIME(7,0,0)` in `_status!F` | Looks like a formula, is a frozen literal | Write actual datetime values |
| `=SQL("...", _status!A1:L)` on README | `#ERROR!` because column I has `NOW()` | Use per-column `ARRAYFORMULA` |
| `_raw_cogs!F1 = "AED→RMB"` | Profit and Cash SQL queries `selling_price_aed`, gets empty | Rename to `selling_price_aed` |
| AGENT INSIGHTS at row 60 with 200-row spill | `#REF!` everywhere on the tab | Move to row 400; or `LIMIT 200` the SQL + overflow footer |

## See also

- `reference/freshness-system.md`, `reference/agent-insights.md`, `reference/error-semantics.md`, `reference/cogs-schema.md`, `reference/image-catalog.md` — most of these rules are codified there with concrete pattern code
- `scripts/post-build-checklist.md` — automated lint sweep

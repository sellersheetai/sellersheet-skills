# Post-build verification checklist

Run this routine before declaring a dashboard build done. Every check is a specific MCP tool call against the freshly-built spreadsheet — no "looks right" allowed.

> Tool prefix below is `mcp__claude_ai_sellersheet_<env>__` where `<env>` is `prod` or `test` depending on which SellerSheet MCP connector is attached.

## Pre-flight

1. `mcp__claude_ai_sellersheet_<env>__list_sheet_tabs(spreadsheet_id)` — confirm the expected tab list:
   - **8 visible:** README, HOME, Inventory and Restock, PPC Command, Account Health, Listing Health, Profit and Cash, Returns and Refunds (+ Search & Share if BA enabled)
   - **12 hidden raw:** `_raw_inventory`, `_raw_listings`, `_raw_account_health`, `_raw_ppc`, `_raw_ppc_attribution`, `_raw_ppc_search_terms`, `_raw_ppc_skus`, `_raw_cogs`, `_raw_catalog`, `_raw_returns`, `_raw_buybox`, `_raw_finance`
   - **5 infrastructure:** `_config`, `_status`, `_agent_notes`, `_agent_log` (and optionally `_agent_log_archive`)

## P0 verification (must-pass)

### 1. `_status` is the canonical freshness source

- `read_sheet(..., "_status!A1:L20")` — verify the 12-column schema (raw_tab, store, source_rpt_table, refresh_cadence, expected_lag_hours, last_pulled_utc, source_data_through, row_count, status, last_error, pull_run_id, agent_actions_count).
- `get_sheet_cell(..., "_status!F2")` — `value` is a real datetime number or ISO string, NOT `=NOW()`, NOT `=DATEVALUE(...)+TIME(...)`. `formula` field should be null (literal).
- `get_sheet_cell(..., "_status!I2")` — `formula` matches the canonical status formula `=IF(J2<>"","RED-error",IF((NOW()-F2)*24>E2*2,"RED-stale",IF((NOW()-F2)*24>E2,"AMBER-aging","GREEN-fresh")))`.
- `read_sheet(..., "_status!I2:I20")` — values should show a MIX of GREEN-fresh / AMBER-aging / RED-stale / RED-error. If all uniform, timestamps are probably faked.

### 2. Row-2 pills resolve from `_status`

For each visible tab (HOME, Inventory and Restock, PPC Command, Account Health, Listing Health, Profit and Cash, Returns and Refunds):

- `get_sheet_cell(..., "<tab>!A2")` — `formula` starts with `=TEXTJOIN(`, references `_status!I:I` and `_status!F:F`. NOT a hardcoded "Refreshed YYYY-MM-DD" string.
- `effective_value` should be a non-error string showing the resolved freshness pill ("Inventory RED-stale · oldest 2026-05-12 07:00 UTC · ...").

### 3. README live freshness table

- `read_sheet(..., "README!A14:I30")` — should show the live spill from `_status` (rows 16+ are data, row 15 is the navy header).
- `get_sheet_cell(..., "README!A16")` — `formula` is `=ARRAYFORMULA(_status!A2:A<N>)` or similar. NOT `=SQL(...)` (which fails because `_status!I` has `NOW()`).
- `read_sheet(..., "README!F16:F25")` — last_pulled_utc column shows real datetime strings, not `#ERROR!`.

### 4. No spill collisions

For each visible tab with a SQL spill (Inventory and Restock, Listing Health, Profit and Cash, PPC Command, Returns and Refunds):

- `get_sheet_cell(..., "<tab>!A<spill_anchor>")` and `<tab>!B<spill_anchor>` — `effective_value` should NOT be `{error: REF, message: "Array result was not expanded because it would overwrite data in <cell>"}`.
- If `#REF!` is found: diagnose what's at the collision cell. If it's the AGENT INSIGHTS section, move it to row 400. If it's leftover content from a prior layout, clear it.
- `read_sheet(..., "<tab>!A150:F165")` — for bounded tabs, AGENT INSIGHTS section should be here (section header at 150, col header at 151, FILTER spill at 152+).
- `read_sheet(..., "<tab>!A400:F405")` — for catalog-scaling tabs (Inventory, Listing, Profit), AGENT INSIGHTS should be at row 400.

### 5. `_raw_cogs` schema is canonical

- `read_sheet(..., "_raw_cogs!A1:R1")` — headers must be: store, sku, asin, image_url, product, **selling_price_{ccy}** (NOT `AED→RMB`), **referral_fee_{ccy}** (NOT `AED/RMB`), fba_fee_{ccy}, total_fees_{ccy}, product_cost_rmb, weight_kg, shipping_rmb, total_cost_rmb, landed_{ccy}, profit_{ccy}, margin_pct, breakeven_{ccy}, suggested_{ccy}.
- `get_sheet_cell(..., "Profit and Cash!B<spill_anchor>")` — `formula` references `[selling_price_aed]` (or whatever ccy matches the COGS tab). The formula's column refs must match the COGS headers.

### 6. Scaffold tabs have sentinel rows

For each `_raw_*` that's scaffolded but not yet wired (typically `_raw_buybox`, `_raw_finance`, sometimes `_raw_cogs` if operator hasn't filled COGS):

- `read_sheet(..., "_raw_buybox!A1:H3")` — row 1 is header, row 2 is sentinel `["<store>", "NOT_YET_SYNCED", "<reason>", "", "", "", "", ""]`.
- Corresponding `_status` row has `last_error="NOT_YET_SYNCED"` and status badge shows RED-error.

## P1 verification (should-pass)

### 7. 5-color provenance fills applied

Sample at least one cell from each provenance class via `get_sheet_cell` → check `effective_format.backgroundColor`:

- **Raw white** `[1, 1, 1]` — `_raw_inventory!A2` (default fill).
- **Formula cool-gray** `[0.953, 0.961, 0.973]` — somewhere on HOME or another visible tab.
- **Agent cream** `[0.996, 0.973, 0.890]` — HOME's TOP 3 FIRES section, or an inline agent narrative cell.
- **User yellow** `[1, 0.949, 0.8]` — `_raw_cogs!F2` (a yellow input cell).
- **Config mint** `[0.953, 0.973, 0.961]` — `_config!B2` or a cell on Profit and Cash that displays config value.

### 8. Cell notes with structured prefix

For 5+ high-value cells, verify `note` field starts with `agent | ` / `formula | ` / `config | ` / `user | ` / `raw | `:

- `get_sheet_cell(..., "HOME!A2")` — `note` should start with `formula | live freshness pill | depends=_status!I:I,F:F | ...`
- `get_sheet_cell(..., "HOME!F<fire_narrative_row>")` — `note` should start with `agent | <timestamp> | source=... | confidence=0.X | "..."`
- Etc. Run `mcp__claude_ai_sellersheet_<env>__get_sheet_notes` if available to batch-check.

### 9. Header backgrounds on every spilled table

For each SQL spill, verify the header row has navy background + white bold:

- `get_sheet_cell(..., "Inventory and Restock!A14")` — `effective_format.backgroundColor` = `{red: 0.157, green: 0.2, blue: 0.318}` (approximately — within rounding).
- Same for `Listing Health!A<header_row>`, `PPC Command!A<header_row>`, `Profit and Cash!A<header_row>`, `Returns and Refunds!A<header_row>`.

### 10. SQL spills use open-ended ranges

For each spill, `get_sheet_cell(..., "<tab>!B<spill_anchor>")` and inspect `formula`. Search for `:1000` or any hardcoded row count — fail if found. Should see `'_raw_inventory'!A1:R` (open-ended).

### 11. Image MAP+SQL alignment

For each tab with an Image-at-A column, both A and B spills must share:
- Same `WHERE` clause
- Same `ORDER BY` clause
- Same `LIMIT` (if any)

`get_sheet_cell(..., "Inventory and Restock!A14")` and `!B14` — compare the SQL strings. If they diverge on WHERE/ORDER BY/LIMIT, image and data columns will desync.

### 12. TOP 3 FIRES on HOME

- `read_sheet(..., "HOME!A4:F8")` — row 4 is the red banner, row 5 the column header, rows 6-8 are the 3 fires.
- `get_sheet_cell(..., "HOME!A6")` — `formula` is the FILTER with `REGEXMATCH(_agent_notes!F2:F100, "^fire-")`.
- `effective_value` shows 3 specific fires (not "no fires — enjoy the morning" unless the store really has none).

## P2 verification (polish)

### 13. AGENT INSIGHTS sections present on every visible tab

For each visible tab except `_config`:
- `read_sheet(..., "<tab>!A<150 or 400>:F<+5>")` — section header + col header + FILTER spill (or "No active insights for this tab.").

### 14. Number formats applied

- AGENT INSIGHTS date column (col A of each spill) — `DATE_TIME` format, not raw serial.
- Margin % columns — `0.0%` format.
- Currency columns — appropriate currency format with thousands separator.

### 15. Conditional formatting on `_status.status`

- `read_sheet_format(..., "_status!I2:I100")` — verify 3 conditional rules (GREEN/AMBER/RED backgrounds).

### 16. Freeze panes

- HOME, README, `_agent_notes`, `_agent_log`, `_status` — freeze row 1.
- Visible tabs with column headers — freeze through the header row (row 5 or wherever the column headers sit).

## Error class triage

If any check fails, categorize:

| Symptom | Class | Action |
|---|---|---|
| `#NAME?` on a `=SQL(...)` / `=IMAGE(...)` / `=IMPORTRANGE(...)` cell | Pending | Expected — user opens browser + grants approval once |
| `#REF!` on a `=SQL(...)` cell with `effective_value.error.message` mentioning "Array result was not expanded" | Real bug | Move AGENT INSIGHTS row anchor down or add `LIMIT 200` |
| `#ERROR!` mentioning "function not allowed to reference a cell with NOW()" | Real bug | Replace `SQL(_status!A1:L)` with per-column `ARRAYFORMULA` |
| `#VALUE!` on a formula | Real bug | Schema drift — check column labels match formula refs |
| `#DIV/0!` on a margin cell | Tolerable | Wrap in `IFERROR(..., "")` if user input is empty |
| Hardcoded "Refreshed 2026-05-12" in row 2 | Lint fail | Replace with `TEXTJOIN` referencing `_status` |
| `_raw_cogs!F1 = "AED→RMB"` or anything other than `selling_price_aed` | Lint fail | Rename column F |
| `_status!F2 = =DATEVALUE("2026-05-12")+TIME(7,0,0)` | Lint fail | Replace with literal datetime value |
| All `_status!I` rows show GREEN-fresh OR all RED-stale uniformly | Likely faked timestamps | Verify F column has varied real datetimes |

## Final browser check — the user does this once. You never open the browser.

Server-side checks cannot verify:
1. SQL() syntax errors from reserved-word column names — only browser eval catches these.
2. Image-column off-by-one alignment.
3. `IMPORTRANGE()` cross-workbook pulls — blocked until the user grants the one-time access prompt.

Your verification ends at the server-side sweep above. **Never open or drive a browser to "finish" the dashboard.** Hand the user the one-time approval steps and what to confirm:

> The `=SQL()` / `=IMAGE()` / `=IMPORTRANGE()` cells show `#NAME?` until you approve them **once** in a browser:
> 1. **Extensions → SellerSheet → Open** — loads the add-on so `SQL()` evaluates (wait 10–30s).
> 2. Click **"Allow access to external images"** when prompted — for product thumbnails.
> 3. Click **Allow access** on any `IMPORTRANGE` prompt — for cross-workbook pulls.
>
> Then please confirm: every SKU table's Image-Store-SKU rows align row-for-row, and no `#ERROR!` cells remain. After this one approval the cells stay live on every future open.

If the user reports a `SQL()` parse error after browser eval, check `reference/image-catalog.md` for the bracket-quote rule.

## Sign-off criteria

- All P0 checks pass.
- ≥10 of the 13 P1 checks pass.
- You have handed the user the one-time browser approval steps and what to confirm. The final render check (`SQL()` + `IMAGE()`) is **theirs to perform** — you never open the browser, and you don't claim those cells render correctly on a server-side read alone.
- TOP 3 FIRES has 3 specific fires (not boilerplate) OR explicit "no fires — enjoy the morning" with operator agreement that the store really is clean today.

Document any P2 deferrals in `_agent_log` with rationale.

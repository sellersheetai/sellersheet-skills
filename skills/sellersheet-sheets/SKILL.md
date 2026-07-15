---
name: sellersheet-sheets
description: Use whenever Google Sheets is the deliverable surface and SellerSheet MCP is the tool for sheet I/O. Reads, writes, formats, builds reports, dashboards, financial models, and live-data tables in Google Sheets via SellerSheet MCP endpoints (read_sheet, write_sheet, write_sheet_formula, format_sheet_range, set_sheet_number_format, add_sheet_chart, add_sheet_conditional_format, add_sheet_dropdown, etc.). Trigger when the user references a docs.google.com/spreadsheets URL, asks to publish output to a Google Sheet, builds anything in the SellerSheet workbook ecosystem, needs the live SQL() spill + image-thumbnail patterns, or builds an operator action surface (filter rows, Amazon enum dropdowns, status chips). Do NOT trigger for local .xlsx files — that's a different skill. This skill is self-contained — no need to load xlsx or any other sheet skill alongside; xlsx-style conventions (financial color coding, number formats, formula best practices) are adapted inline.
version: 0.10.0
---

# SellerSheet Google Sheets — via MCP

## Prerequisites

Run the standard preflight in [`sellersheet-shared`](../sellersheet-shared/SKILL.md) (installed alongside this skill): `get_user_context` succeeds → version check via `data.skills_catalog` → `data.canUseMcp` is true.

---

> **Author**: sellersheetai.com
> **Requirements**: SellerSheet MCP tools (`mcp__claude_ai_sellersheet_<env>__*` — `<env>` is `prod` or `test` depending on which SellerSheet MCP connector is attached). For live `SQL()` and `IMAGE()` to render, the operator opens the workbook in a browser with the SellerSheet GAS add-on enabled (Extensions → SellerSheet → Open).
> **Scope**: this skill is self-contained — production-quality conventions for color, number formats, formulas, and layout are codified across this file + `reference/` + `scripts/`. No external xlsx skill required.

### `SQL()` needs the add-on provisioned in *that* workbook

`SQL()` is a **SellerSheet add-on custom function** — it only evaluates in workbooks where the
add-on is enabled (a human opened **Extensions → SellerSheet → Open** once in that workbook).
Arbitrary MCP-created spreadsheets show `#NAME?` forever; for those, write **pre-computed values
or plain formulas** instead. After writing a `SQL()` formula, a spill cell may read back empty for
a few seconds while Sheets recalculates — **re-read before concluding failure**.

### `IMAGE()` renders differently for the service account and the human

Under some conditions an `IMAGE()` cell written by the service account renders as `#REF!` with a
"use desktop browser" message for the human until they open the workbook in a **desktop browser**.
Reading such a cell back via MCP requires `value_render_option='FORMULA'` — the default rendering
returns the error, not the formula you wrote.

The SellerSheet MCP wraps Google's `spreadsheets.batchUpdate` server-side; everything you do is a tool call, not a Python edit, not a manual click. This skill covers:

1. **Brand visuals** — color palette, number formats, professional output standards (see `reference/brand-standards.md`)
2. **Formula conventions** — always-formulas-not-hardcoded, source documentation, verification checklist (see `reference/formula-conventions.md`)
3. **Growable tables** (read-mode) — the `_raw_*` + `SQL()` spill pattern with image-at-A thumbnails (see `reference/growable-tables.md`, `reference/sql-function.md`, `reference/image-pattern.md`)
4. **Action sheets** (operator input surfaces) — 2-row vs 4-row header conventions, emerald-vs-navy bands, Amazon enum dropdowns, status chips (see `reference/action-sheets.md`)
5. **Workflow recipes** — build-a-report-from-scratch + starter recipes for common report shapes (see `scripts/starter-recipes.md`)
6. **MCP gotchas** — quirks learned from live builds (see `reference/mcp-gotchas.md`)
7. **Verification** — read-back patterns and error class triage (see `reference/error-semantics.md` + `scripts/verify-after-write.md`)

For full operator dashboards (multi-tab status views, freshness instrumentation, agent insights), load the `sellersheet-dashboard` skill — it builds on top of this one.

## Quick reference — what every Sheet must have

These rules apply to every sheet this skill produces. Detailed explanations live in `reference/`.

1. **Professional font**: Arial 10pt default. Override only for headers and titles.
2. **Zero formula errors**: scan the output for `#REF!`, `#VALUE!`, `#N/A`, `#ERROR!` — these are real bugs, fix them. `#DIV/0!` is tolerable *only if* wrapped in `IFERROR`/`IF(denom=0,…)`; an unwrapped one is a bug. `#NAME?` on `=SQL(` and `=IMAGE(` cells is the documented browser-pending state — not a bug. Full triage: `reference/error-semantics.md`.
3. **Use formulas, never hardcoded values** for any calculated number — `=SUM(B2:B10)`, not `=23456`. See `reference/formula-conventions.md` for the WRONG/CORRECT pattern.
4. **Apostrophe-escape literal text that starts with `=`** (or `+`). `write_sheet` is USER_ENTERED — any string beginning with `=` becomes a live formula, so documentation text like `= ordered − refunded` or `= date` lands as a broken formula (`#ERROR!` / `#NAME?`). Write `'= ordered − refunded` instead; the apostrophe doesn't render. **Scan every 2D values array for leading-`=` cells BEFORE writing** — notes/derivation columns in schema docs are the classic trap. Full gotcha + repair recipe: `reference/mcp-gotchas.md`.
5. **Identifiers stay text.** USER_ENTERED auto-parses SKUs/UPCs/postal codes into numbers and dates (`"0012345678905"` loses its zeros; SKU `"10-1"` becomes a date). Apostrophe-prefix identifier cells, or set the column to `@` text format before the first write. Full table: `reference/mcp-gotchas.md`.
6. **Open-range SQL spills** with `LIMIT N` per data scope — see `reference/sql-function.md`.
7. **Emerald = where the operator acts; Navy = where the operator reads.** Never both on the same row. See `reference/brand-standards.md` for the action-vs-read rule.
8. **Verify with a read-back** before declaring done — the mandatory **Final review gate** below; full routine in `scripts/verify-after-write.md`.

For action sheets (operator inputs into the data) the additional 9-rule checklist lives in `reference/action-sheets.md`.

## SellerSheet brand palette (RGB 0–1 floats — what the MCP accepts)

| Use | Color name | RGB |
|---|---|---|
| **Banner row** (row 2; row 1 is the hidden machine row) | SellerSheet emerald | `[0.063, 0.725, 0.506]` |
| **Section band** | Same emerald | `[0.063, 0.725, 0.506]` |
| **Sub-header / column header / SQL-spilled table header** | Navy | `[0.157, 0.2, 0.318]` |
| **Status chip RED** | Red | `[0.929, 0.451, 0.431]` |
| **Status chip AMBER** | Amber-orange | `[1.0, 0.847, 0.42]` |
| **Status chip GREEN** | Green | `[0.557, 0.792, 0.58]` |
| **Footer callout / overflow notice** | Soft yellow | `[1.0, 0.949, 0.8]` |
| **Metadata / subtext bar** | Light gray-blue | `[0.929, 0.945, 0.961]` |

Title bars on **every visible tab** wear emerald — that's how a workbook reads as one brand.

The MCP color format is `[r, g, b]` floats in `[0.0, 1.0]`. Not the openpyxl-style hex string. Convert `#0000FF` → `[0.0, 0.0, 1.0]`.

For the financial-model color coding (blue inputs / black formulas / green internal links / red external / yellow assumptions) + number-format patterns + currency / percent / multiples standards — see `reference/brand-standards.md`.

## Three request modes — answer, edit, or build

Classify the request before touching the sheet; each mode has a different contract.

**Answer (read-only question).** "What does this column mean?", "why is B12 negative?" →
`read_sheet` the relevant range (add `value_render_option='FORMULA'` to see formulas), trace
the formula back to its labeled inputs instead of stopping at an intermediate total, and
answer in the reply. **No writes.** Don't "fix" things the user only asked about.

**Edit (existing sheet).** The sheet already has a layout the user lives in — your change
must land invisibly inside its conventions:
1. Inspect first: `read_sheet` + `read_sheet_format` the target area; note fonts, band colors, number formats, existing dropdowns/conditional formats.
2. Make the **smallest change that satisfies the request** — match the tab's existing style even where it differs from this skill's brand defaults.
3. Appending rows/columns to a table? Extend what the table already carries: fill the new cells' formulas from the neighboring pattern, and re-anchor conditional formats, dropdowns, and the basic filter to cover the added range.
4. Never restyle beyond the requested range; leave unrelated pre-existing errors in place unless they break your change or the user asked for an audit (note them in the reply instead).

**Build (new tab / new workbook).** The workflow below + Final review gate. Brand defaults apply in full.

## Build workflow

When asked to build a Google Sheet report:

1. **Inspect what's there** — `list_sheet_tabs`, `get_sheet_metadata`, `read_sheet` a sample range to discover existing conventions.
2. **Provision tabs** — `add_sheet_tab` for each new tab. Hidden data tabs prefixed `_raw_*`; configuration on `_config`.
3. **Setup tab structure** — `setup_sheet` for the standard 2-row header convention, or manually `write_sheet` + `format_sheet_range` + `freeze_sheet_panes`.
4. **Write data + formulas** — `write_sheet` for values (USER_ENTERED parses `=` as formula too), `write_sheet_formula` for explicit single-cell intent. Before every `write_sheet`, sweep the values array for literal text starting with `=`/`+` and prefix those cells with `'` (Quick-reference rule 4). Per `reference/formula-conventions.md`: cell references, not hardcoded numbers.
5. **Format numbers + headers** — `set_sheet_number_format` for currency / percent / dates. `format_sheet_range` for header bands. See `reference/brand-standards.md`.
6. **Visualize** — `add_sheet_chart` (design rules, type selection, anchor placement: `reference/charts.md`), `add_sheet_conditional_format` for gradients and value-based chips (`reference/conditional-formatting.md`).
7. **Polish** — `resize_sheet_columns` for deliberate fixed widths (the default; size to the header, not the data), `add_sheet_filter`, `protect_sheet_range`. Use `autofit_sheet_columns` only as a final touch on short/structured columns (codes, KPIs, statuses) and only **after** the filter — it doesn't reserve room for the filter arrow, so autofit-before-filter clips headers. Never autofit column A or long free-text columns (images, product titles, descriptions) — keep those fixed. See `reference/brand-standards.md` → Column widths.
8. **Verify** — run the Final review gate below. Do not declare the build done until it passes.

## Final review gate — do NOT skip

Every build ends here. Create a TodoWrite item per line, work through them, and only then report. The full routine (exact tool calls per step) is `scripts/verify-after-write.md`; this is the checklist that must be ticked.

- [ ] **Error sweep, all visible tabs.** `read_sheet` each tab; scan for `#REF!`, `#ERROR!`, `#VALUE!`, `#N/A`, unwrapped `#DIV/0!`. Each is a real bug — `get_sheet_cell` → read `effective_value.error.message`, triage per `reference/error-semantics.md`, fix.
- [ ] **`#NAME?` is pending ONLY on `=SQL(` / `=IMAGE(` cells.** `#NAME?` on any other formula (`=ARRAYFORMULA`, `=FILTER`, `=VLOOKUP`, …) is a real bug — fix it. Never wave a `#REF!`/`#ERROR!` through as "the add-on will fix it on open" — that is the #1 builder mistake (`error-semantics.md` Golden Rule).
- [ ] **Spot-check server-side formulas evaluate.** 2–3 `=SUM`/`=VLOOKUP`/`=ARRAYFORMULA` cells: `effective_value` is the computed result, not the formula string and not `None`.
- [ ] **Row counts match.** Wrote N rows → `_raw_*` has N+1 (with header). A shortfall signals chunked-write truncation or empty-string masquerading (`reference/mcp-gotchas.md`).
- [ ] **Number formats + brand colors applied.** Sample a currency/percent/date cell and a header cell; confirm `effective_format` matches intent (navy header ≈ `[0.157, 0.2, 0.318]`).
- [ ] **Growth test** (growable tables only). Append one `_raw_*` row, confirm the SQL spill + chips + image join expand, then remove it.

### Server-side can't see everything — the user finishes it, once

`read_sheet` cannot evaluate `SQL()`, `IMAGE()`, or `IMPORTRANGE()` — these are add-on / browser-side functions. So three error classes stay invisible to you (`SQL()` parse errors, image-column off-by-one alignment, merged-cell-eaten spills), and the cells show `#NAME?` pending state until the **user** opens the workbook and grants the one-time approvals.

**Never open or drive the browser yourself.** Your job ends at the server-side sweep. Close the build by telling the user the one-time steps in your final message:

> Verified server-side: no `#REF!` / `#ERROR!` / `#VALUE!`. The `=SQL()` / `=IMAGE()` cells show the expected `#NAME?` pending state. To make them render, please do this **once** in a browser:
> 1. **Extensions → SellerSheet → Open** (loads the add-on so `SQL()` evaluates).
> 2. Click **"Allow access to external images"** when prompted (for `IMAGE()` thumbnails).
> 3. If the sheet pulls from another workbook, click **Allow access** on the `IMPORTRANGE` prompt.
>
> After that one approval the live cells populate (10–30s) and stay live on every future open.

Never report a build as fully verified on a server-side read alone — flag the pending cells and hand the one-time approval to the user.

## Header grammar (v2) — build it in one pass

> **Already have a styled tab to clone?** `copy_sheet_tab` an existing well-formatted tab and
> rename it — formatting, notes, conditional formats, dropdowns, frozen panes and image
> formulas come for free in one call. Build from this grammar when you're laying out a tab
> from scratch.

Every SellerSheet tab is a stack of typed **header bands** above a data zone. The band
*order* never changes; a sheet just includes the bands it needs. This lets you lay a sheet
out in one pass without probing it.

### The five bands

| Band | Role | Style | Hidden? |
|---|---|---|---|
| **machine** | code-contract keys (`store`, `asn_nr`, `imageUrl`, lowerCamelCase) — code reads/writes by name via a header-map lookup, so columns can be reordered later | Arial 7pt, grey `#A8AEB8`, white bg, normal weight | **yes — `hideRows(1)`** |
| **banner** | brand band `SellerSheet • <Sheet>` | Arial 14pt bold white on emerald `#10B981`, left-aligned, **never merged** | no |
| **bands** *(opt)* | section spans (STA metadata, noon Inbound ①②③) | navy `#28334F` spans, label in first cell of each span | no |
| **controls** *(opt)* | a **label row + a value row** — operator inputs (Store/Status/filters) | label: navy bg + font-color semantics; value: input-bg `#EDF1F5` | no |
| **display** | the human-read column header | navy `#28334F` bg, **slate `#8CA0B3`** font, **EN·CN cell notes** | no |

**Input semantics live in the label font-color** (not background): gold `#FFD86B` = required
input, white = optional input, slate `#8CA0B3` = button/sync-filled. Editable label cells
carry a trailing **`✎`** (monochrome glyph, inherits color — never the emoji `✏️`), and only
on display/label rows, never on the machine row.

**Always:** never merge (breaks freeze panes); keep default row heights everywhere (including image/thumbnail rows — a thumbnail is just a quick SKU reminder, not a detail view), the only sanctioned custom row height is the emerald banner (~34 px);
`setFrozenRows(<display row>)`; basic filter on the display row where useful (skip on audit
logs); EN·CN cell notes on the display row so the operator knows each column's logic.

### The three shapes — pick before writing

| Shape | When | Bands (top→down) | Data starts | Frozen |
|---|---|---|---|---|
| **action** | operator types **into the data rows** (Ack codes, overrides) | machine · banner · display | row 4 | 3 |
| **filter+browse** | operator scans a list, narrows via top filters | machine · banner · filter-labels · filter-inputs · display | row 6 | 5 |
| **control-block** | a Store/Status/page-size control block above a list | machine · banner · label-row · value-row · display | row 6 | 5 |

`control-block` worked example — **noon Shipments**: row 1 keys (hidden) · row 2 emerald
banner · row 3 labels `Store ✎ · Status ✎ · Page Size ✎` · row 4 values (Store input,
Status dropdown, 200) · row 5 navy display header with EN·CN notes · row 6+ ASN list.

Quick decision: *type into data rows?* → **action**. *narrow a list via top filters?* →
**filter+browse**. *set a few controls (store/status/qty) that drive one list?* →
**control-block**. *neither type nor filter, just scan a live spill?* → **growable table**
(`reference/growable-tables.md`).

NOT for any: single-cell KPI tiles, fixed-shape sections ≤3 rows, data-value-driven
cell styling beyond conditional-format reach.

Deep dive (per-band helper code, narrowing-band rule, IMAGE arrayformula slot, dropdown
warning mode, status-chip map, idempotent re-setup): `reference/action-sheets.md`.

## Reference index

Detailed specs live in `reference/`. Load the relevant file before implementing that part — don't guess from memory.

| File | What's in it |
|---|---|
| `reference/brand-standards.md` | Color palette, **emerald-vs-navy action/read rule**, professional font, financial-model color coding (blue/black/green/red/yellow), number format patterns (currency / percent / multiples / dates), zero-formula-errors policy |
| `reference/action-sheets.md` | 3-row vs 5-row header conventions, the five row bands (HIDDEN code-contract row 1 / emerald title row 2 / emerald label / filter input / navy display), narrowing emerald band rule, IMAGE arrayformula slot (A3 / A5), Amazon enum dropdowns in warning mode, **basic-filter-on-display-header convention** (apply where useful, skip on audit logs), status chip mapping table for SP-API enums, editable-cell ✏️ marker, column-reorder discipline, idempotent re-setup |
| `reference/formula-conventions.md` | Use-formulas-not-hardcoded-values rule with WRONG/CORRECT examples, source documentation for hardcodes via cell notes, formula error prevention checklist, common pitfalls (NaN, division-by-zero, cross-sheet refs, edge cases) |
| `reference/growable-tables.md` | The four rules, layout shape, store column as multi-store identifier, when NOT to use this pattern |
| `reference/sql-function.md` | SQL() signature, bracket-quote-every-column-and-alias rule, multi-table JOINs, default LIMITs per data scope, overflow footer pattern |
| `reference/image-pattern.md` | Image-at-A canonical formula, MAP+LAMBDA header detection, JOIN with `_raw_catalog`, alignment constraints (same WHERE/ORDER BY/LIMIT) |
| `reference/charts.md` | `add_sheet_chart` contract (column→series mapping, explicit anchor, no axis-format param), chart type selection table, formula-backed helper ranges, placement/sizing, server-side verification limits |
| `reference/conditional-formatting.md` | Open-range conditional formatting, **soft-vs-bold chip palette** decision, gradient rules, value-based chips, **Amazon SP-API enum chip reference table**, number-format application strategies |
| `reference/error-semantics.md` | `#NAME?` (pending) vs `#REF!` (real bug) vs `#ERROR!` (NOW collision) vs `#VALUE!` (schema drift) vs `#DIV/0!` (tolerable), diagnostic recipe |
| `reference/mcp-gotchas.md` | `&` in tab names, USER_ENTERED parses `=` as formula, merged-cell side effects, NULL vs empty-string in numeric `_raw_*`, chunked write recipe for large payloads |
| `reference/config-tab.md` | `_config` separation, named ranges (`cfg_fx`, `cfg_ship_rmb_kg`, `cfg_referral_pct`), FX as-of freshness rule |
| `reference/openpyxl-mcp-mapping.md` | Translation table for users coming from openpyxl / Excel macros / Google Apps Script, with known-limitations table |

## Scripts index

Copy-paste templates and verification routines live in `scripts/`.

| File | What it gives you |
|---|---|
| `scripts/formula-templates.md` | Tested formula library: SQL spill with LIMIT, image MAP+JOIN, overflow footer, conditional gradient, HYPERLINK to drill tabs, FX VLOOKUP |
| `scripts/verify-after-write.md` | Read-back verification routine after each build step — what to scan for, error class triage |
| `scripts/starter-recipes.md` | Common report patterns: simple findings tab, multi-store list with thumbnails, financial model with assumption inputs, list+detail drill pattern |

## When NOT to use this skill

- **Local `.xlsx` file deliverables** (downloads, not Drive) → use the `xlsx` skill instead.
- **A Docs page, not a Sheets workbook** → use the docs-* MCP tools.
- **A sheet that lives entirely server-side and is never opened in a browser** — the `SQL()` and `IMAGE()` patterns require a browser session with the SellerSheet add-on.
- **Multi-tab operator dashboards** with freshness instrumentation + agent insights → use `sellersheet-dashboard` (it builds on top of this skill).
- **Amazon business operations** (orders, listings, ads) → use `sellersheet`.
- **Choosing which Amazon `rpt_*` table to query** → use `report-data`.

## First-time setup for users

When working with someone who's never published a SellerSheet-styled report:

1. Confirm SellerSheet MCP is installed and the user has at least one connected store at sellersheetai.com/dashboard.
2. Confirm they'll open the resulting workbook in a browser (the `SQL()` + `IMAGE()` patterns don't render server-side).
3. On first open: Sheets prompts "Allow access to external images" once — required for product thumbnails. The SellerSheet add-on must be enabled (Extensions → SellerSheet → Open) for `SQL()` to evaluate.
4. The first `read_sheet` after publishing will show `#NAME?` on every `SQL()` cell — that's expected pending state, not a bug. See `reference/error-semantics.md`.

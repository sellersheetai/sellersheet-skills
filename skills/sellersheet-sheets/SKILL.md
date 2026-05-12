---
name: sellersheet-sheets
description: Use whenever Google Sheets is the deliverable surface and SellerSheet MCP is the tool for sheet I/O. Reads, writes, formats, builds reports, dashboards, financial models, and live-data tables in Google Sheets via SellerSheet MCP endpoints (read_sheet, write_sheet, write_sheet_formula, format_sheet_range, set_sheet_number_format, add_sheet_chart, add_sheet_conditional_format, etc.). Trigger when the user references a docs.google.com/spreadsheets URL, asks to publish output to a Google Sheet, builds anything in the SellerSheet workbook ecosystem, or needs the live SQL() spill + image-thumbnail patterns specific to the SellerSheet GAS add-on. Do NOT trigger for local .xlsx files — that's a different skill. This skill is self-contained — no need to load xlsx or any other sheet skill alongside; xlsx-style conventions (financial color coding, number formats, formula best practices) are adapted inline.
version: 0.1.0
---

# SellerSheet Google Sheets — via MCP

> **Author**: sellersheetai.com
> **Requirements**: SellerSheet MCP tools (`mcp__claude_ai_sellersheet_mcp__*`). For live `SQL()` and `IMAGE()` to render, the operator opens the workbook in a browser with the SellerSheet GAS add-on enabled (Extensions → SellerSheet → Open).
> **Scope**: this skill is self-contained — production-quality conventions for color, number formats, formulas, and layout are codified across this file + `reference/` + `scripts/`. No external xlsx skill required.

The SellerSheet MCP wraps Google's `spreadsheets.batchUpdate` server-side; everything you do is a tool call, not a Python edit, not a manual click. This skill covers:

1. **Brand visuals** — color palette, number formats, professional output standards (see `reference/brand-standards.md`)
2. **Formula conventions** — always-formulas-not-hardcoded, source documentation, verification checklist (see `reference/formula-conventions.md`)
3. **Growable tables** — the `_raw_*` + `SQL()` spill pattern with image-at-A thumbnails (see `reference/growable-tables.md`, `reference/sql-function.md`, `reference/image-pattern.md`)
4. **Workflow recipes** — build-a-report-from-scratch + starter recipes for common report shapes (see `scripts/starter-recipes.md`)
5. **MCP gotchas** — quirks learned from live builds (see `reference/mcp-gotchas.md`)
6. **Verification** — read-back patterns and error class triage (see `reference/error-semantics.md` + `scripts/verify-after-write.md`)

For full operator dashboards (multi-tab status views, freshness instrumentation, agent insights), load the `sellersheet-dashboard` skill — it builds on top of this one.

## Quick reference — what every Sheet must have

These five rules apply to every report this skill produces. Detailed explanations live in `reference/`.

1. **Professional font**: Arial 10pt default. Override only for headers and titles.
2. **Zero formula errors**: scan the output for `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`. (`#NAME?` on `=SQL(` and `=IMAGE(` cells is the documented browser-pending state — not a bug.)
3. **Use formulas, never hardcoded values** for any calculated number — `=SUM(B2:B10)`, not `=23456`. See `reference/formula-conventions.md` for the WRONG/CORRECT pattern.
4. **Open-range SQL spills** with `LIMIT N` per data scope — see `reference/sql-function.md`.
5. **Verify with a read-back** before declaring done — see `scripts/verify-after-write.md`.

## SellerSheet brand palette (RGB 0–1 floats — what the MCP accepts)

| Use | Color name | RGB |
|---|---|---|
| **Title bar (row 1)** | SellerSheet emerald | `[0.063, 0.725, 0.506]` |
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

## Build workflow

When asked to build a Google Sheet report:

1. **Inspect what's there** — `list_sheet_tabs`, `get_sheet_metadata`, `read_sheet` a sample range to discover existing conventions.
2. **Provision tabs** — `add_sheet_tab` for each new tab. Hidden data tabs prefixed `_raw_*`; configuration on `_config`.
3. **Setup tab structure** — `setup_sheet` for the standard 2-row header convention, or manually `write_sheet` + `format_sheet_range` + `freeze_sheet_panes`.
4. **Write data + formulas** — `write_sheet` for values (USER_ENTERED parses `=` as formula too), `write_sheet_formula` for explicit single-cell intent. Per `reference/formula-conventions.md`: cell references, not hardcoded numbers.
5. **Format numbers + headers** — `set_sheet_number_format` for currency / percent / dates. `format_sheet_range` for header bands. See `reference/brand-standards.md`.
6. **Visualize** — `add_sheet_chart`, `add_sheet_conditional_format` for gradients and value-based chips. See `reference/conditional-formatting.md`.
7. **Polish** — `resize_sheet_columns`, `add_sheet_filter`, `protect_sheet_range`.
8. **Verify** — run `scripts/verify-after-write.md` — read back the just-written range, scan for errors, triage per `reference/error-semantics.md`.

## When to use the `_raw_*` + `SQL()` pattern (the live growable table)

Default for any list-style report that grows as data is appended — inventory, ad performance, listings, financials, anything operator-facing where new rows arrive over time.

NOT for: single-cell KPI tiles, small fixed-shape sections (≤3 rows), cell-level styling that varies with data values beyond conditional formatting reach.

Full pattern in `reference/growable-tables.md`. SQL() syntax, JOIN rules, bracket-quote requirement in `reference/sql-function.md`. Image column at column A in `reference/image-pattern.md`.

## Reference index

Detailed specs live in `reference/`. Load the relevant file before implementing that part — don't guess from memory.

| File | What's in it |
|---|---|
| `reference/brand-standards.md` | Color palette, professional font, financial-model color coding (blue/black/green/red/yellow), number format patterns (currency / percent / multiples / dates), zero-formula-errors policy |
| `reference/formula-conventions.md` | Use-formulas-not-hardcoded-values rule with WRONG/CORRECT examples, source documentation for hardcodes via cell notes, formula error prevention checklist, common pitfalls (NaN, division-by-zero, cross-sheet refs, edge cases) |
| `reference/growable-tables.md` | The four rules, layout shape, store column as multi-store identifier, when NOT to use this pattern |
| `reference/sql-function.md` | SQL() signature, bracket-quote-every-column-and-alias rule, multi-table JOINs, default LIMITs per data scope, overflow footer pattern |
| `reference/image-pattern.md` | Image-at-A canonical formula, MAP+LAMBDA header detection, JOIN with `_raw_catalog`, alignment constraints (same WHERE/ORDER BY/LIMIT) |
| `reference/conditional-formatting.md` | Open-range conditional formatting, gradient rules, value-based chips, number-format application strategies |
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

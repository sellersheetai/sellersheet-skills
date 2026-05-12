# Brand standards + output quality

The visual + numeric conventions every Google Sheet from this skill must satisfy. Mirrors and adapts the openpyxl/xlsx financial-model conventions for the SellerSheet MCP color format (RGB 0-1 floats).

## Professional font

Default to **Arial 10pt** (Google Sheets' default). Use `format_sheet_range` with explicit `font_size` only when overriding for headers / titles:

```javascript
format_sheet_range(..., font_size=18, bold=true)   // title bar
format_sheet_range(..., font_size=11, bold=true)   // section band
format_sheet_range(..., font_size=10, bold=true)   // sub-header
format_sheet_range(..., font_size=9)               // metadata / freshness pill
```

Don't mix fonts within a workbook. Don't switch to a stylized font without operator request.

## Zero formula errors

Every published Sheet MUST be free of `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`. A `read_sheet` after writing catches them. `#NAME?` on `=SQL(` and `=IMAGE(` cells is the documented browser-pending state (see `reference/error-semantics.md`) — not a bug.

Triage approach for each error class is in `reference/error-semantics.md`.

## Preserve existing templates (when updating, not creating)

Before writing into an existing sheet, run `list_sheet_tabs` + `read_sheet` on a sample range to discover existing conventions (header row count, color palette, number formats). **Existing template conventions ALWAYS override these guidelines.** Match them.

If asked to "update" a sheet that has a different font, color scheme, or layout: keep theirs. The standards here are for new builds.

## SellerSheet brand palette

| Use | RGB | Hex |
|---|---|---|
| **Title bar (row 1)** | `[0.063, 0.725, 0.506]` | `#10B981` SellerSheet emerald |
| **Section band** | `[0.063, 0.725, 0.506]` | same emerald, merged across width |
| **Sub-header / column header / SQL-spilled table header** | `[0.157, 0.2, 0.318]` | `#283351` navy |
| **Status chip RED** | `[0.929, 0.451, 0.431]` | `#ED736E` |
| **Status chip AMBER** | `[1.0, 0.847, 0.42]` | `#FFD86B` |
| **Status chip GREEN** | `[0.557, 0.792, 0.58]` | `#8ECA94` |
| **Status chip GRAY** | `[0.78, 0.78, 0.78]` | `#C7C7C7` |
| **Footer callout / overflow notice** | `[1.0, 0.949, 0.8]` | `#FFF2CC` soft yellow |
| **Metadata / subtext bar** | `[0.929, 0.945, 0.961]` | `#EDF1F5` light gray-blue |
| **Status badge GREEN-fresh** (on `_status.status`) | `[0.776, 0.91, 0.835]` | `#C6E8D5` |
| **Status badge AMBER-aging** | `[1, 0.898, 0.6]` | `#FFE599` |
| **Status badge RED-stale / RED-error** | `[0.957, 0.78, 0.765]` | `#F4C7C3` |

Title bars on **every visible tab** wear emerald — the workbook reads as one brand.

The MCP color format is `[r, g, b]` floats in `[0.0, 1.0]`. Not the openpyxl-style hex string. Convert by dividing 0-255 ints by 255.

## Financial-model color coding

When the sheet is a financial model (not a status dashboard), adopt the industry-standard finance color convention used in openpyxl/xlsx workflows. Lets a reviewer scan a model in 10 seconds and know which cells are inputs vs derived vs cross-referenced.

| Meaning | Apply via | Color |
|---|---|---|
| Hardcoded inputs / scenario knobs / numbers users will change | `font_color` | `[0.0, 0.0, 1.0]` blue (`#0000FF`) |
| Formulas / calculations | (default — don't override) | `[0.0, 0.0, 0.0]` black |
| Internal worksheet links | `font_color` | `[0.0, 0.5, 0.0]` green (`#008000`) |
| External links (other workbooks, GOOGLEFINANCE, IMPORTRANGE) | `font_color` | `[1.0, 0.0, 0.0]` red (`#FF0000`) |
| Key assumptions needing attention / TODO | `background_color` | `[1.0, 1.0, 0.0]` yellow (`#FFFF00`) |

Apply assumption-yellow sparingly — its purpose is to draw the eye. If half the model is yellow, the signal is lost.

## Number formatting standards

Use `set_sheet_number_format` with these patterns. Apply to whole open ranges (`E51:H300`) — number formats are idempotent and cheap.

| Type | Pattern | Notes |
|---|---|---|
| Years (rendered as text) | `@` | Write the value as a string `"2024"` not `2024` |
| Currency (positive only) | `$#,##0;($#,##0);-` | Always specify units in headers — "Revenue ($mm)" |
| Currency with cents | `$#,##0.00;($#,##0.00);-` | For unit prices / fees |
| Percent (1 decimal — default) | `0.0%;(0.0%);-` | |
| Percent (no decimal) | `0%;(0%);-` | |
| Multiples (ROAS, P/E, EV/EBITDA) | `0.0"x"` | |
| Date (ISO-ish) | `yyyy-mm-dd` | |
| DateTime (UTC log) | `yyyy-mm-dd hh:mm` | |
| Zero rendered as `-` | wrap any of above with `;-` | Industry convention |
| Negatives as parens | `(123)` not `-123` | wrap with `;()` |

Apply consistently: don't mix `$#,##0` and `$#,##0.00` within the same column.

## Visual rules — what NOT to do

| Anti-pattern | Why it's bad | Do instead |
|---|---|---|
| Title bar navy instead of emerald | Visual inconsistency across tabs | Emerald `[0.063, 0.725, 0.506]` on row 1 of every visible tab |
| Image column placed at column G or later | Operator can't scan SKUs quickly | Image always at column A |
| Closed SQL range `_raw_x!A1:M77` | Table doesn't grow when raw data is appended | Open range `_raw_x!A1:M` |
| Footer / summary BELOW the growable table | Growth collides; user has to push notes down | Always put footers ABOVE the table |
| Decision color chips on a fixed cell range | Chips don't move when sorting changes | Conditional formatting on open range keyed to cell value |
| Leading `=` or `+` in a plain-text cell | Renders as `#ERROR!` (parsed as formula) | Drop the leading char or prefix with apostrophe |
| Date format on a column that holds numbers | Numbers render as `1899-12-30` | Reset to NUMBER format |
| Per-column array formulas (`={"Decision";...}` × 13) | Verbose, multiple sources of truth, drift risk | One `SQL("SELECT ... FROM ?", _raw_*!A1:M)` |

## Row heights + column widths

- **KPI / data rows** (no thumbnails): default ~21 px.
- **Data rows with thumbnails**: **38 px** (`resize_sheet_rows(..., start_row=8, end_row=300, height=38)`). Set out to row 300+ ahead of growth.
- **Image column width**: **50 px** (`resize_sheet_columns(..., start_col=0, end_col=1, width=50)`).
- **Standard data columns**: **140-180 px** for general columns; narrower for codes (Store ~80 px, SKU ~120 px).

## See also

- `reference/formula-conventions.md` — formula construction rules + verification
- `reference/conditional-formatting.md` — open-range gradients + chips
- `scripts/verify-after-write.md` — error scanning routine

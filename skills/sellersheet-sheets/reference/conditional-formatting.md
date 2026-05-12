# Conditional formatting

Value-based formatting on open ranges so chips and gradients track row content as the table grows. Fixed-range color rules break when data grows or is sorted.

## Value-based chips on open ranges

Fixed-range color chips (e.g., `A6:A31` red) break when the table grows. Use **value-based conditional formatting** on an open range:

```javascript
// REORDER chip — red background where Decision column = "REORDER"
add_sheet_conditional_format(
    spreadsheet_id, range_="Inventory!B9:B1000",
    condition_type="TEXT_EQ", values=["REORDER"],
    background_color=[0.929, 0.451, 0.431])

// SOON chip — amber
add_sheet_conditional_format(
    spreadsheet_id, range_="Inventory!B9:B1000",
    condition_type="TEXT_EQ", values=["SOON"],
    background_color=[1, 0.65, 0.42])

// HOLD chip — green
add_sheet_conditional_format(
    spreadsheet_id, range_="Inventory!B9:B1000",
    condition_type="TEXT_EQ", values=["HOLD"],
    background_color=[0.557, 0.792, 0.58])
```

## Numeric gradient (red-amber-green)

For WoC, margin, or any numeric column where the operator wants visual gradient:

```javascript
add_sheet_conditional_format(
    spreadsheet_id, range_="Inventory!I9:I1000",
    gradient=True,
    min_color=[0.929, 0.451, 0.431],   // red at low
    mid_color=[1, 0.847, 0.42],         // amber midpoint
    max_color=[0.557, 0.792, 0.58],     // green at high
    min_value=0, mid_value=8, max_value=20)
```

Apply over the same open range as the chips. The gradient evaluates per-cell; new rows pick up the gradient automatically.

## Threshold-based highlighting

```javascript
// Red background for percentages over 5%
add_sheet_conditional_format(
    spreadsheet_id, range_="Account Health!D6:D20",
    condition_type="NUMBER_GREATER", value=0.05,
    background_color=[1, 0.8, 0.8])

// Bold red text for negative margins
add_sheet_conditional_format(
    spreadsheet_id, range_="Profit and Cash!P9:P1000",
    condition_type="NUMBER_LESS", value=0,
    font_color=[1, 0, 0], bold=True)
```

## CUSTOM_FORMULA — the portable fallback

If `TEXT_EQ`, `TEXT_STARTS_WITH`, or `NUMBER_GREATER` condition types error on your MCP version, fall back to `CUSTOM_FORMULA` — universally supported:

```javascript
// "GREEN-fresh" status badge
add_sheet_conditional_format(
    spreadsheet_id, range_="_status!I2:I100",
    condition_type="CUSTOM_FORMULA", value='=LEFT($I2,5)="GREEN"',
    background_color=[0.776, 0.91, 0.835])

// "AMBER-aging"
add_sheet_conditional_format(
    spreadsheet_id, range_="_status!I2:I100",
    condition_type="CUSTOM_FORMULA", value='=LEFT($I2,5)="AMBER"',
    background_color=[1, 0.898, 0.6])

// "RED-stale" or "RED-error" (starts with "RED")
add_sheet_conditional_format(
    spreadsheet_id, range_="_status!I2:I100",
    condition_type="CUSTOM_FORMULA", value='=LEFT($I2,3)="RED"',
    background_color=[0.957, 0.78, 0.765])
```

CUSTOM_FORMULA also handles compound conditions:

```javascript
// Margin < 0% AND ad cost > 0 → flag the negative-after-ads SKUs
condition_type="CUSTOM_FORMULA", value='=AND($P9<0, $T9>0)'

// Cell empty AND not in a header row
condition_type="CUSTOM_FORMULA", value='=AND(ISBLANK(A9), ROW()>=9)'
```

## Number formats — apply to open ranges too

`set_sheet_number_format` is idempotent and cheap to apply over wide open ranges:

```javascript
// All currency columns — open range
set_sheet_number_format(
    spreadsheet_id, range_="Profit and Cash!E9:E1000",
    format_pattern="$#,##0;($#,##0);-")

// All percent columns
set_sheet_number_format(
    spreadsheet_id, range_="Profit and Cash!P9:P1000",
    format_pattern="0.0%;(0.0%);-")

// Date column
set_sheet_number_format(
    spreadsheet_id, range_="Returns and Refunds!F9:F1000",
    format_pattern="yyyy-mm-dd")
```

Apply at build time after the spill anchors are placed. The formats persist as rows are appended.

## When NOT to use conditional formatting

- **Status badges that change shape with the row** (e.g., a multi-state chip with N variants where N grows). Hand-format chip cells via `write_sheet_formula` returning a `=IFS(...)` switch + per-chip `format_sheet_range` calls — too many CF rules slow Sheets.
- **Layouts where the row meaning shifts** (a totals row that mixes formats with the data rows above it). Hand-format the totals row separately.
- **One-shot reports** that don't grow. Closed-range bg fills are fine.

## Limits

Google Sheets allows ~50 conditional-format rules per sheet before performance degrades. Combine related rules when possible:

```javascript
// Instead of N separate TEXT_EQ rules for chip colors, use one CUSTOM_FORMULA per state
condition_type="CUSTOM_FORMULA", value='=$B9="REORDER"', background_color=[...]
condition_type="CUSTOM_FORMULA", value='=$B9="SOON"', background_color=[...]
// ...4 rules total for 4 chip states
```

For high-cardinality state variables, switch to a chip-emoji + plain-text approach instead of relying on conditional formatting.

## See also

- `reference/brand-standards.md` — chip and gradient color palette
- `scripts/formula-templates.md` — common gradient + chip recipes

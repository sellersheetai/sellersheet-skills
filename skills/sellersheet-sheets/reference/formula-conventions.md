# Formula conventions

Adapted from the openpyxl/xlsx financial-modeling standard for the Google Sheets / SellerSheet MCP context. These rules make every Sheet from this skill maintainable, auditable, and trustworthy.

## CRITICAL: Use formulas, not hardcoded values

**Always use Sheets formulas instead of calculating values in your head / via tool and hardcoding them.** This ensures the spreadsheet remains dynamic and updateable — when source data changes, the calculated cells re-evaluate.

### WRONG — hardcoding calculated values

```
// Bad: computing the sum yourself and writing the number
write_sheet(spreadsheet_id, "Findings!B10", [[5000]])   // hardcodes 5000

// Bad: computing growth rate before writing
growth_rate = (latest - earliest) / earliest
write_sheet(spreadsheet_id, "Findings!C5", [[0.15]])    // hardcodes 0.15

// Bad: averaging in code, writing the result
avg = sum(values) / len(values)
write_sheet(spreadsheet_id, "Findings!D20", [[42.5]])   // hardcodes 42.5
```

### CORRECT — using Sheets formulas

```
// Good: let Sheets calculate the sum
write_sheet_formula(spreadsheet_id, "Findings!B10", "=SUM(B2:B9)")

// Good: growth rate as a formula
write_sheet_formula(spreadsheet_id, "Findings!C5", "=(C4-C2)/C2")

// Good: average using a Sheets function
write_sheet_formula(spreadsheet_id, "Findings!D20", "=AVERAGE(D2:D19)")
```

This applies to ALL calculations — totals, percentages, ratios, differences, ranks, lookups, etc. The spreadsheet should recalculate when source data changes; if you bake the answer in, the operator's edit to the inputs does nothing.

## Use cell references, not literal numbers

Place assumptions / inputs in their own cells. Formulas reference those cells.

```
// Bad — magic number 0.05 buried in a formula
write_sheet_formula(spreadsheet_id, "Model!B5", "=B4*1.05")

// Good — growth rate input in its own cell, formula references it
write_sheet(spreadsheet_id, "Model!B6", [["Growth rate"]])
write_sheet(spreadsheet_id, "Model!C6", [[0.05]])      // formatted as 0.0%
write_sheet_formula(spreadsheet_id, "Model!B5", "=B4*(1+$C$6)")
```

Why: the operator can change growth rate once in C6 and the entire projection updates. With the magic number, they have to find every formula and edit.

## Document hardcoded values with cell notes

When a number genuinely is a hardcoded input (not a calculation), add a cell note explaining its source so a reviewer 6 months later knows where it came from.

```
update_sheet_note(spreadsheet_id, "Model!C6",
  "Source: 2025 budget assumptions, finalized 2025-Q4 ops review")

update_sheet_note(spreadsheet_id, "Inputs!B3",
  "Source: Amazon FBA fee schedule, effective 2026-01-15")
```

Format: `Source: [System/Document], [Date], [Specific reference if applicable]`.

Examples:
- `"Source: Company 10-K, FY2024, Page 45, Revenue Note"`
- `"Source: Bloomberg Terminal, 8/15/2025, AAPL US Equity"`
- `"Source: operator manual entry, 2026-03-10, verified against vendor invoice #INV-4521"`

## Formula error prevention checklist

Run through this before bulk-writing a model's formulas. Most issues caught here.

### Essential verification
- **Test 2-3 sample references first.** Verify they pull correct values before building the full model.
- **Column mapping.** Confirm columns line up after any layout shift. After deleting column D, what was column E becomes the new column D.
- **Row offset.** Header row(s) consume rows 1-2 typically; data starts at row 3. Off-by-one is the #1 source of `#REF!`.
- **Cross-sheet references** use the correct format: `'Sheet Name'!A1` (single quotes if name has spaces).
- **Open-range refs** (`'_raw_*'!A:Z`) instead of locked-row refs (`A2:Z1000`).

### Common pitfalls
- **NaN / empty-string handling**: an empty cell behaves differently from `""`. For numeric `_raw_*` columns, write `None` (blank), never `""`. See `reference/mcp-gotchas.md` for the `SQL()` implication.
- **Division by zero**: wrap with `IFERROR(numerator/denom, "")` or `IF(denom=0, "—", numerator/denom)`. Don't ship a model that returns `#DIV/0!` on day-1 with empty inputs.
- **Wrong references** after rearranging columns: do a final sweep — does B5 still mean what you think it means?
- **Cross-sheet references** break if the source tab is renamed. Use named ranges for stable cross-references (`cfg_fx` not `_config!$B$2`).

### Formula testing strategy
- **Start small**: test formulas on 2-3 cells before applying broadly.
- **Verify dependencies**: every cell referenced in a formula must exist and contain the expected type.
- **Test edge cases**: include zero, negative, very large values, empty inputs.
- **Verify no unintended circular references** — Sheets surfaces these as `#REF!` with a circular-dependency message.

## Formulas vs hardcoded values — table

| Scenario | Hardcode? | Use formula? |
|---|---|---|
| Sum of a column | NO | `=SUM(B2:B100)` |
| Growth rate from two cells | NO | `=(B100-B2)/B2` |
| FX rate from `_config` | NO | `=VLOOKUP("USD", cfg_fx, 2, FALSE)` |
| Reference value snapshot at a point in time | YES — with note | Hardcode + `update_sheet_note` documenting the snapshot date and source |
| Today's date when the report was generated | depends | If "as-of" cell that must freeze: hardcode with `TEXT(NOW(),"yyyy-mm-dd")` evaluated once at write time. If "current date" that should update: `=TODAY()` formula. |
| Yearly fiscal-year label `"2025"` | YES — as text | Format col as `@`, write `"2025"` |
| Constants the formula uses (referral fee 13%) | NO | Put 13% in `_config`, named range `cfg_referral_pct`, reference it |

## Formula construction — best practices

- **Cell references, not literals**: `=B5*(1+$B$6)`, not `=B5*1.05`.
- **Absolute vs relative refs**: dollar-sign anchor (`$B$6`) when the formula will be copied across rows and you want a fixed reference; relative (`B6`) when you want it to shift.
- **`IFERROR` wrapper** for any formula that could legitimately fail: `=IFERROR(VLOOKUP(...), "")`. Prevents `#N/A` propagation.
- **Named ranges** for stable cross-references: `=VLOOKUP("USD", cfg_fx, 2, FALSE)` is more robust than `=VLOOKUP("USD", _config!$A$2:$B$5, 2, FALSE)`.
- **`write_sheet_formula` for single-cell formula writes**. Both `write_sheet` and `write_sheet_formula` parse `=` as formula (USER_ENTERED) so `write_sheet` works for bulk multi-cell formula writes — see `reference/mcp-gotchas.md` for the batching difference.

## Numeric column rule — blank, never empty-string

`SQL()` evaluates `WHERE col > 4` against literal cell contents. If a cell holds `""` (empty string) instead of being blank, comparisons silently fail. For `_raw_*` numeric columns:

- Real number → write the number directly (`3.14`, `0`, `100`).
- Missing / N/A → write **blank** (omit from row, or write `None` in Python which becomes blank), NOT `""`.

Same for `ORDER BY`: text-zero `"0"` sorts after numeric `100`. If unsure, `clear_sheet_range` first then write only populated rows.

## See also

- `reference/sql-function.md` — SQL() column-name and alias bracket-quoting rule
- `reference/mcp-gotchas.md` — NULL vs empty-string + USER_ENTERED parsing
- `reference/error-semantics.md` — diagnosing each error class
- `scripts/verify-after-write.md` — the read-back routine

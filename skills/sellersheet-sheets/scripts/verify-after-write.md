# Verify after write — the read-back routine

Mandatory before declaring a Sheets build done. Every check is a specific MCP tool call against the freshly-written cells.

## Step 1: Scan for error cells

```python
read_sheet(spreadsheet_id, "Tab!A1:Z<last_row>")
```

Look at the returned JSON for any cell value containing:
- `#REF!` — real bug (spill collision or invalid reference)
- `#ERROR!` — real bug (formula syntax or NOW-collision)
- `#VALUE!` — real bug (type mismatch / schema drift)
- `#N/A` — usually real bug (failed VLOOKUP/MATCH)
- `#DIV/0!` — tolerable, but should be wrapped in IFERROR for production
- `#NAME?` — see Step 2 (often pending state, sometimes real bug)

For each error found, drill in:

```python
get_sheet_cell(spreadsheet_id, range_="Tab!<cell>")
# Read effective_value.error.message for the specific reason
```

Triage per `reference/error-semantics.md`.

## Step 2: Distinguish pending vs real `#NAME?`

`#NAME?` on `=SQL(...)` or `=IMAGE(...)` cells is **expected pending state** (server-side can't evaluate browser-side custom functions). Not a bug.

`#NAME?` on any other formula type is **real bug** — typo or undefined named range.

For each `#NAME?` cell:

```python
get_sheet_cell(spreadsheet_id, range_="Tab!<cell>")
# Inspect the formula field — does it start with =SQL( or =IMAGE( ?
```

- Starts with `=SQL(` or `=IMAGE(` → pending state, expected. Move on.
- Anything else → real bug. Fix the formula.

## Step 3: Verify formulas evaluate (server-side functions)

For formulas that DO evaluate server-side (`=SUM`, `=COUNTIF`, `=VLOOKUP`, `=ARRAYFORMULA`, `=FILTER`, `=TEXTJOIN`, etc.), spot-check 2-3 cells:

```python
get_sheet_cell(spreadsheet_id, range_="Tab!<cell>")
# Read effective_value — should be the computed result, not the formula string
```

If `effective_value` is `None` or an error object → real bug; fix.

## Step 4: Verify row counts match expectation

If you wrote N data rows, confirm:

```python
read_sheet(spreadsheet_id, "_raw_<tab>!A1:A1000")
# Count non-empty values — should be N+1 (data rows + header)
```

A row count significantly lower than expected often signals:
- Chunked-write payload truncation (see `reference/mcp-gotchas.md`).
- Sentinel rows getting filtered.
- Empty-string `""` cells masquerading as data.

## Step 5: Verify number formats applied

```python
get_sheet_cell(spreadsheet_id, range_="Tab!<currency_cell>")
# Read effective_format.numberFormat — should match the pattern you set
```

For currency cells: `"$#,##0;($#,##0);-"` or similar.
For percent cells: `"0.0%;(0.0%);-"`.
For date cells: `"yyyy-mm-dd"`.

If the format is just `"GENERAL"` or `"NUMBER"`, `set_sheet_number_format` may have errored silently — re-apply.

## Step 6: Verify color formatting applied

For SQL-spill header rows (navy bg + white bold):

```python
get_sheet_cell(spreadsheet_id, range_="Tab!<header_cell>")
# Check effective_format.backgroundColor — should be approximately [0.157, 0.2, 0.318]
# Check effective_format.textFormat.foregroundColor — should be approximately [1, 1, 1]
# Check effective_format.textFormat.bold — should be true
```

For status badges and chips:

```python
read_sheet_format(spreadsheet_id, "Tab!<chip_range>")
# Inspect — chip cells should have appropriate background_color
```

If chips show wrong color: check the conditional formatting rules via `list_sheet_conditional_formats` (where available) or re-apply.

## Step 7: Verify open ranges + conditional formats work as data grows

If the table is growable, write one extra row to confirm:
- The SQL spill expands to include it.
- The chip / gradient applies to the new row.
- The Image column joins correctly (if applicable).

```python
# Append a test row
append_sheet_rows(spreadsheet_id, "_raw_<tab>!A:Z", [[test_row_data]])
# Re-read the visible tab
read_sheet(spreadsheet_id, "Tab!A1:Z<extended_row>")
# Verify the test row appears with correct chips/colors
```

Then remove the test row (write blank values, OR `clear_sheet_range` if only this row was added).

## Step 8: Final error sweep across all tabs

For each tab in the workbook:

```python
list_sheet_tabs(spreadsheet_id)
# Then for each visible tab:
read_sheet(spreadsheet_id, "<tab>!A1:Z<reasonable_extent>")
# Sweep for #REF!, #ERROR!, #VALUE!, #N/A
```

`#NAME?` is acceptable on `=SQL(` and `=IMAGE(` cells only.

## Browser open — what server-side can't catch

Server-side `read_sheet` cannot verify:

1. **SQL() syntax errors from reserved-word column names.** Cells show `#NAME?` server-side regardless — both correct and broken SQL render identically until a browser opens the sheet.
2. **Image-column off-by-one alignment.** `IMAGE()` cells are blank pre-Allow-Access, so alignment with SKU rows can't be visually verified until after the consent prompt.
3. **Merged-cell side effects** that silently eat SQL spills.

**Rule:** before declaring a Sheets build done, open it in a real browser as a user with the SellerSheet add-on. Wait for `SQL()` to evaluate (10-30 seconds). Click "Allow access to external images" once. Walk every spill and confirm:
- Image column aligns row-for-row with SKU column.
- No `#ERROR!` cells (alasql parse errors only surface in browser).
- Conditional chips render with correct colors.
- Number formats display correctly.

## Quick verification cheat sheet

| What to check | How |
|---|---|
| All formulas evaluate without error | `read_sheet` whole tab, scan for `#REF!` / `#ERROR!` / `#VALUE!` / `#N/A` |
| `=SQL(` cells are pending, not broken | `get_sheet_cell` on the cell; confirm formula starts with `=SQL(` and `effective_value.error.type` is `NAME` not `REF` |
| Number formats applied | `get_sheet_cell` on sample cells; check `effective_format.numberFormat.pattern` |
| Header rows have navy bg | `get_sheet_cell` on header cell; check `effective_format.backgroundColor` ≈ [0.157, 0.2, 0.318] |
| Spills don't collide with footers/sections | spill anchor cell's `effective_value` is non-error; `effective_value.error.message` if present mentions specific overflow cell |
| Open ranges grow correctly | append one test row to `_raw_*`; re-read visible tab |
| Conditional formats applied | check the conditional-format list or visually inspect |
| Image alignment correct | (browser-only) open in browser, walk SKU table, confirm thumbnails match rows |

## What "done" means

- Step 1-7 passed with no real bugs.
- Step 8 surfaces only `#NAME?` on `=SQL(` / `=IMAGE(` cells (pending — expected).
- Browser open confirms SQL() + IMAGE() render correctly.

Document any deferred items in cell notes so the operator and future-you know about them.

## See also

- `reference/error-semantics.md` — error class triage
- `scripts/formula-templates.md` — patterns to verify against
- `reference/mcp-gotchas.md` — common quirks that produce false errors

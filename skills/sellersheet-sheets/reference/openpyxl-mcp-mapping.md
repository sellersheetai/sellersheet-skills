# openpyxl / Excel / Apps Script → SellerSheet MCP mapping

Translation table for users coming from openpyxl, Excel macros, or Google Apps Script. The conventions you know still apply; only the call surface changes.

## Workbook + sheet lifecycle

| openpyxl / Excel idiom | SellerSheet MCP equivalent |
|---|---|
| `wb = Workbook()` | `create_spreadsheet_in_folder(folder_id, name)` |
| `wb = load_workbook('file.xlsx')` | (not needed — sheets are addressed by `spreadsheet_id`) |
| `wb.save('output.xlsx')` | (not needed — every MCP call writes to Drive immediately) |
| `wb.create_sheet("X")` | `add_sheet_tab(spreadsheet_id, "X")` |
| `wb.remove(wb["X"])` | `delete_sheet_tab(spreadsheet_id, "X")` |
| `wb["X"].title = "Y"` | `rename_sheet_tab(spreadsheet_id, "X", "Y")` |
| `wb.sheetnames` | `list_sheet_tabs(spreadsheet_id)` |

## Cell-level operations

| openpyxl idiom | SellerSheet MCP equivalent |
|---|---|
| `sheet['A1'] = 'foo'` | `write_sheet(spreadsheet_id, "Sheet!A1", [["foo"]])` |
| `sheet['B2'] = '=SUM(A1:A10)'` | `write_sheet_formula(spreadsheet_id, "Sheet!B2", "=SUM(A1:A10)")` |
| `sheet.append([...])` | `append_sheet_rows(spreadsheet_id, "Sheet!A:E", [[...]])` |
| `sheet.insert_rows(idx)` | `insert_sheet_rows_cols(... dimension="ROWS", start_index=idx, end_index=idx+1)` |
| `sheet.delete_cols(col)` | `sheet_batch_update` with `deleteDimension` request |
| `value = sheet['A1'].value` | `read_sheet(spreadsheet_id, "Sheet!A1")` |
| `value = sheet['A1'].formula` | `get_sheet_cell(spreadsheet_id, "Sheet!A1")` (returns `formula` field) |

## Formatting

| openpyxl idiom | SellerSheet MCP equivalent |
|---|---|
| `Font(bold=True, color='FF0000')` | `format_sheet_range(... font_color=[1,0,0], bold=True)` |
| `Font(italic=True)` | `format_sheet_range(... italic=True)` |
| `Font(size=14)` | `format_sheet_range(... font_size=14)` |
| `PatternFill('solid', start_color='FFFF00')` | `format_sheet_range(... background_color=[1,1,0])` |
| `Alignment(horizontal='center')` | `format_sheet_range(... horizontal_alignment="CENTER")` |
| `Border(...)` | `set_sheet_borders(...)` (where available) |
| `sheet.column_dimensions['A'].width = 20` | `resize_sheet_columns(... start_col=0, end_col=1, width=140)` (px, not chars) |
| `sheet.row_dimensions[1].height = 30` | `resize_sheet_rows(... start_row=0, end_row=1, height=30)` |
| `sheet.merge_cells('A1:C1')` | `merge_sheet_cells(spreadsheet_id, "Sheet!A1:C1")` |
| `sheet.unmerge_cells('A1:C1')` | `unmerge_sheet_cells(spreadsheet_id, "Sheet!A1:C1")` |
| `sheet.freeze_panes = 'B2'` | `freeze_sheet_panes(... rows=1, cols=1)` |
| Number format `'$#,##0'` | `set_sheet_number_format(... format_pattern="$#,##0;($#,##0);-")` |

## Conditional formatting + charts

| openpyxl idiom | SellerSheet MCP equivalent |
|---|---|
| `ColorScaleRule(...)` | `add_sheet_conditional_format(... gradient=True, min_color=..., max_color=...)` |
| `CellIsRule(operator='greaterThan', formula=['0.05'], ...)` | `add_sheet_conditional_format(... condition_type="NUMBER_GREATER", value=0.05, ...)` |
| `FormulaRule(formula=['=$A2="REORDER"'], ...)` | `add_sheet_conditional_format(... condition_type="CUSTOM_FORMULA", value='=$A2="REORDER"', ...)` |
| `chart = BarChart()` | `add_sheet_chart(... chart_type="COLUMN", ...)` |
| `chart = LineChart()` | `add_sheet_chart(... chart_type="LINE", ...)` |
| `sheet.add_chart(chart, "G3")` | (anchor_cell parameter on `add_sheet_chart`) |

## Images, notes, filters

| openpyxl idiom | SellerSheet MCP equivalent |
|---|---|
| `wb.add_image(Image('logo.png'), 'A1')` | `write_sheet_formula(... "=IMAGE(\"https://...\")")` (Sheets-native — URL required, not local file) |
| `cell.comment = Comment("...", "author")` | `update_sheet_note(spreadsheet_id, range_, "...")` |
| `sheet.auto_filter.ref = "A1:E20"` | `set_sheet_basic_filter(spreadsheet_id, "Sheet!A1:E20")` or `create_sheet_filter(...)` |
| Defined name | `add_sheet_named_range(spreadsheet_id, name, range_)` |

## Reading / verification

| openpyxl idiom | SellerSheet MCP equivalent |
|---|---|
| `wb = load_workbook('file.xlsx', data_only=True)` | `read_sheet(spreadsheet_id, range_)` returns formatted values; `get_sheet_cell` returns both `value` (raw) and `formatted_value` |
| `recalc.py output.xlsx` | (not needed — Sheets evaluates server-side immediately) |
| `for row in sheet.iter_rows(...)` | `read_sheet(spreadsheet_id, range_)` returns 2D array |

## Known limitations vs openpyxl

These don't have direct MCP endpoints yet — work around or check your MCP version:

| Capability | MCP gap | Workaround |
|---|---|---|
| Pivot tables | not exposed | Build a flat aggregation with `=QUERY()` formula |
| Sparklines | exposed via `insert_sheet_sparkline` (varies by MCP version) | Use `=SPARKLINE(...)` via `write_sheet_formula` |
| Cell borders | partial (depends on MCP version; `set_sheet_borders` may exist) | Use `format_sheet_range` with bg color as visual border surrogate |
| Bulk paste with inline format | 2 calls | `write_sheet` then `format_sheet_range` — trivial overhead |
| Auto-fit columns | `autofit_sheet_columns(spreadsheet_id, sheet, start_col, end_col)` — wraps Sheets' native `autoResizeDimensions` | Measures real rendered glyphs server-side (CJK/RTL/bold, any language), beating a `len × px` estimate. But it's a **final polish for short/structured columns only** — run it LAST, **after `set_sheet_basic_filter`** (it doesn't reserve room for the filter arrow, so autofit-before-filter clips headers), and **never on column A or long free-text columns** (keep those fixed). Fixed widths are the safer default. See `reference/brand-standards.md` |
| Data validation (dropdowns) | `add_sheet_data_validation` / `add_sheet_dropdown` (where available) | Use those when present |
| Protected ranges | `protect_sheet_range(spreadsheet_id, range_)` | Lock headers + config |
| Group / collapse rows | `group_sheet_rows_cols` | Use for collapsible sections |
| Hide / show rows | `hide_sheet_rows` | Hide raw tabs from operators (also: just leave them un-hidden — they're prefixed `_raw_*` so they sort to the bottom anyway) |

## Differences in mental model

A few patterns differ enough between openpyxl and Sheets-via-MCP that they warrant calling out:

### 1. Width units

openpyxl uses character widths (`width = 20` means "20 chars wide"). The MCP uses pixels (`width = 140` means "140 px") — and **pixels are Google Sheets' *native* width unit** (the API's `pixelSize`), so this is the correct, best-practice unit here, not a workaround. The char unit is the foreign one. You only need the conversion when porting an openpyxl width: `pixels = chars × 7 + 16`, so openpyxl `width=20` ≈ MCP `width=156`. When you don't have a legacy width to port, don't compute pixels at all — call `autofit_sheet_columns` and let Sheets size to the rendered text.

### 2. Colors

openpyxl uses ARGB hex strings (`'FFFF0000'`, `'FF0000FF'`). MCP uses RGB float tuples in [0,1] (`[1,0,0]`, `[0,0,1]`). Convert:
- Hex char positions 3-4 = R, 5-6 = G, 7-8 = B (skip the AA alpha prefix).
- `int_val / 255` = float.
- `'FF0000FF'` → R=0x00, G=0x00, B=0xFF = `[0, 0, 1]`.

### 3. No save step

openpyxl requires `wb.save('output.xlsx')` to persist. The MCP writes immediately on each tool call. No save step.

### 4. No recalculate step

openpyxl creates formulas as strings; values aren't computed until `recalc.py output.xlsx`. Sheets evaluates formulas server-side immediately. A `read_sheet` after `write_sheet_formula` returns the evaluated result. (Exception: `SQL()` and `IMAGE()` browser-side custom functions — see `reference/error-semantics.md`.)

### 5. Concurrent edits

Multiple agents can edit the same Sheet at the same time (it's a live cloud document). Each MCP call is atomic and persists immediately. If two writes target the same cell, last-write-wins. Be careful with parallel writes to overlapping ranges.

## See also

- `reference/brand-standards.md` — color palette in MCP float form
- `reference/formula-conventions.md` — formula construction conventions
- `reference/mcp-gotchas.md` — MCP-specific quirks

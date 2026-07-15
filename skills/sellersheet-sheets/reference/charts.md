# Charts — design rules for `add_sheet_chart`

Use a chart only when it makes a trend, comparison, ranking, or distribution easier to read
than a compact table. One chart = one takeaway. If the exact values are the point (few items),
use a table; if it's a single metric over time inside a row, use `=SPARKLINE()`
(templates: `scripts/formula-templates.md`).

## Tool contract (what `add_sheet_chart` actually does)

```
add_sheet_chart(spreadsheet_id, dataRange, chartType, title,
                anchorRange?, widthPixels=600, heightPixels=371,
                legendPosition='BOTTOM_LEGEND', xAxisTitle?, yAxisTitle?, stackedType?)
```

- `chartType` ∈ `BAR | COLUMN | LINE | AREA | SCATTER | COMBO | PIE`.
- `dataRange` first column = categories (x-axis / pie labels); **each remaining column = one series**; first row = series headers (`headerCount=1` is hard-coded). Shape the range before calling — the tool cannot pick non-adjacent columns.
- `PIE` uses exactly the first two columns (labels, values).
- Omitting `anchorRange` drops the chart **one column right of `dataRange`** — usually on top of live data. Always pass an explicit `anchorRange`.
- There is no per-axis number-format parameter. Axis labels inherit the **source cells' number format** — apply `set_sheet_number_format` to the data columns *before* adding the chart.

## Source data rules

- **Chart a helper range, not the raw table**, when the table isn't already `categories | series…` adjacent columns. Helper ranges live on the same tab (right of the data, or on the `_raw_*` tab) and must be **formula-backed** (`=A2`, `=SUM(...)`, `=TEXT(date,"mmm yyyy")`) so the chart updates when source data changes — never pasted copies.
- **Dates**: convert to text labels in the helper range — `=TEXT(B2,"yyyy-mm")` or `"mmm yyyy"` — rather than trusting raw date cells; grouped labels (month/week) beat crowded daily ticks.
- **Growable tables**: anchor the range over the expected spill extent (`_raw_x!A1:C32`); a `SQL()` spill area works as chart source once the browser has evaluated it, but the chart is built against the *grid range*, so size it to the LIMIT, not the current row count.
- Blanks for unknown values, not invented zeroes (`reference/mcp-gotchas.md` NULL rule).

## Type selection

| Takeaway | Type | Notes |
|---|---|---|
| Trend over time | `LINE` | `AREA` only when the filled volume means something |
| Category comparison / ranking | `COLUMN` (few) / `BAR` (many or long labels) | Sort the source rows descending first — the tool won't sort |
| Part-to-whole, ≤5 slices | `PIE` | More slices → sorted `BAR` instead |
| Two-metric relationship | `SCATTER` | |
| Mixed magnitude (revenue + rate) | `COMBO` | |
| Composition over time | `COLUMN` + `stackedType` | |

## Placement + sizing

- Reserve a rectangle **clear of data, controls, and notes**, with one blank gutter row/column around it. Standard slot: right of the table starting 2 columns past its last column, or a dedicated section below the KPI band.
- Default 600×371 px ≈ 6 columns × 18 rows. Two charts side by side: shrink to ~460 px wide and align their top rows. Comparable charts get the same size and scale.
- Charts float over the grid (overlay position) — they don't push cells, and `clear_sheet_range` does NOT remove them. Delete/re-add via `sheet_batch_update` `deleteEmbeddedObject` when rebuilding a layout.

## Title + labels

- Title states the takeaway with units, ≤ ~60 chars: `Revenue by Marketplace ($, T30D)` — not `Chart 1`.
- Axis titles only when the unit isn't already in the chart title or obvious from labels.
- `legendPosition='NO_LEGEND'` for single-series charts; `BOTTOM_LEGEND` otherwise.
- Emerald `#10B981` is the brand accent — Sheets assigns default series colors and this tool doesn't override them; don't fight it, mention recoloring as a browser-side option only if the user asks.

## Verify (server-side limits)

`read_sheet` cannot render a chart. After `add_sheet_chart`:

1. Confirm the tool response reports the created chart (id / anchor).
2. Re-read the source/helper range — headers in row 1, no error cells, no header row landing in the data (a numeric first row silently becomes a series point).
3. Confirm the anchor rectangle is empty grid (no data underneath).

The visual pass (clipped labels, wrong series pickup) happens when the user opens the workbook — include the chart in the final-message pending list alongside `SQL()`/`IMAGE()` if its source is a spill.

## Editing existing charts

Inspect before touching: `get_sheet_metadata` for existing chart objects and their anchors. Preserve the existing size/position unless it overlaps something you added. Leave unrelated pre-existing chart defects alone unless they break the requested change or the user asked for an audit.

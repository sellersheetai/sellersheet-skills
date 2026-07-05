# Starter recipes — common report patterns

Assembled from `reference/` patterns + `scripts/formula-templates.md`. Copy a recipe, adapt to the specific report, ship.

## Recipe 1: Findings tab with conditional gradient

When to use: audit results, QA checks, anomaly reports — a list of issues each scored on severity.

```python
# 1. Provision tab
add_sheet_tab(spreadsheet_id, "Findings")

# 2. Title + freshness
write_sheet(spreadsheet_id, "Findings!A1", [["Audit Findings — <subject>"]])
format_sheet_range(spreadsheet_id, "Findings!A1",
    background_color=[0.063, 0.725, 0.506], font_color=[1,1,1], bold=True, font_size=18)

write_sheet(spreadsheet_id, "Findings!A2",
    [["Generated " + iso_timestamp + " · " + str(n_findings) + " findings · severity gradient on column D"]])
format_sheet_range(spreadsheet_id, "Findings!A2",
    background_color=[0.929, 0.945, 0.961], font_color=[0.4,0.4,0.4], font_size=9, italic=True)

# 3. Header row
write_sheet(spreadsheet_id, "Findings!A4:F4",
    [["Report Type", "Region", "Column", "Severity", "Drift %", "Recommended Fix"]])
format_sheet_range(spreadsheet_id, "Findings!A4:F4",
    background_color=[0.157, 0.2, 0.318], font_color=[1,1,1], bold=True)
freeze_sheet_panes(spreadsheet_id, "Findings", rows=4)

# 4. Write findings rows
write_sheet(spreadsheet_id, "Findings!A5:F<n+4>", findings_rows)

# 5. Format severity column with red-amber-green gradient
set_sheet_number_format(spreadsheet_id, "Findings!E5:E1000", "0.0%;(0.0%);-")
add_sheet_conditional_format(spreadsheet_id, "Findings!E5:E1000",
    gradient=True,
    min_color=[0.557, 0.792, 0.58],   # green low drift
    mid_color=[1, 0.847, 0.42],        # amber midpoint
    max_color=[0.929, 0.451, 0.431],   # red high drift
    min_value=0, mid_value=0.05, max_value=0.20)

# 6. Filter for sorting
set_sheet_basic_filter(spreadsheet_id, "Findings!A4:F<n+4>")

# 7. Verify
verify_per_scripts/verify-after-write.md
```

## Recipe 2: Multi-store list with thumbnails

When to use: any SKU/ASIN list where operators benefit from visual product recognition. Inventory, listings, PPC by SKU, returns, etc.

```python
# 1. Provision the visible tab + _raw_<topic> companion
add_sheet_tab(spreadsheet_id, "Inventory")
add_sheet_tab(spreadsheet_id, "_raw_inventory")
add_sheet_tab(spreadsheet_id, "_raw_catalog")  # if not already present

# 2. Pull data via query_report_data, populate _raw_inventory
# (Set store value on each row at write time)
write_sheet(spreadsheet_id, "_raw_inventory!A1:R1", [canonical_headers])
write_sheet(spreadsheet_id, "_raw_inventory!A2:R<n+1>", inventory_rows)

# 3. Populate _raw_catalog (one row per (store, sku), 5 columns)
write_sheet(spreadsheet_id, "_raw_catalog!A1:E1",
    [["store", "sku", "asin", "image_url", "product"]])
write_sheet(spreadsheet_id, "_raw_catalog!A2:E<m+1>", catalog_rows)

# 4. Build the visible tab — title + freshness + spill
write_sheet(spreadsheet_id, "Inventory!A1", [["Inventory — multi-store"]])
format_sheet_range(spreadsheet_id, "Inventory!A1",
    background_color=[0.063, 0.725, 0.506], font_color=[1,1,1], bold=True, font_size=18)

write_sheet(spreadsheet_id, "Inventory!A2", [[freshness_pill_text]])

# 5. Anchor SQL spill at row 8 (image at A8, data at B8)
write_sheet_formula(spreadsheet_id, "Inventory!A8",
    """=MAP(SQL("SELECT cat.[image_url] FROM ? AS data LEFT JOIN ? AS cat
                  ON data.[store]=cat.[store] AND data.[sku]=cat.[sku]
                  WHERE data.[afn_warehouse_quantity] > 0
                  ORDER BY data.[afn_warehouse_quantity] DESC, data.[sku] ASC
                  LIMIT 200",
                 '_raw_inventory'!A1:R, '_raw_catalog'!A1:E),
            LAMBDA(url, IF(url="image_url", "Image",
                           IF(url="", "", IMAGE(url)))))""")

write_sheet_formula(spreadsheet_id, "Inventory!B8",
    """=SQL("SELECT [store] AS [Store], [sku] AS [SKU], [asin] AS [ASIN],
              [product] AS [Product], [your_price] AS [Price],
              [afn_fulfillable_quantity] AS [Fulfillable], [inbound_total] AS [Inbound],
              [afn_warehouse_quantity] AS [Warehouse Qty]
           FROM ?
           WHERE [afn_warehouse_quantity] > 0
           ORDER BY [afn_warehouse_quantity] DESC, [sku] ASC
           LIMIT 200",
          '_raw_inventory'!A1:R)""")

# 6. Format the spilled header row (row 8, where SQL output's header lands)
format_sheet_range(spreadsheet_id, "Inventory!A8:H8",
    background_color=[0.157, 0.2, 0.318], font_color=[1,1,1], bold=True)

# 7. Image column width (fixed 50 px). Do NOT set a row height — the thumbnail
#    renders at the default ~21 px row, which is all a quick SKU reminder needs.
resize_sheet_columns(spreadsheet_id, "Inventory", start_col=0, end_col=1, width=50)

# 8. Overflow footer at row 209 (8 anchor + 200 LIMIT + 1 buffer)
write_sheet_formula(spreadsheet_id, "Inventory!A209",
    '="Showing first 200 of " & (COUNTA(\'_raw_inventory\'!A:A) - 1) & " rows. See _raw_inventory for full list."')
format_sheet_range(spreadsheet_id, "Inventory!A209:H209",
    background_color=[1, 0.949, 0.8], italic=True)

# 9. Verify
verify_per_scripts/verify-after-write.md
```

## Recipe 3: Financial model with assumption inputs

When to use: ROI calculator, scenario model, breakeven analysis — anything with operator-tunable inputs feeding computed outputs.

```python
# 1. Two tabs: Model (formulas) + Assumptions (yellow input cells)
add_sheet_tab(spreadsheet_id, "Model")
add_sheet_tab(spreadsheet_id, "Assumptions")

# 2. Assumptions tab — yellow input cells (financial-model color coding)
write_sheet(spreadsheet_id, "Assumptions!A1:C5",
    [["Assumption", "Value", "Notes"],
     ["Growth rate Y1", 0.15, "Source: 2025 budget"],
     ["Growth rate Y2-Y5", 0.08, "Source: 5yr plan"],
     ["Discount rate", 0.10, "WACC FY25"],
     ["Terminal multiple", 8, "Industry median EV/EBITDA"]])
format_sheet_range(spreadsheet_id, "Assumptions!B2:B5",
    background_color=[1,1,0], font_color=[0,0,1])   # yellow bg + blue text = inputs
set_sheet_number_format(spreadsheet_id, "Assumptions!B2:B4", "0.0%;(0.0%);-")
set_sheet_number_format(spreadsheet_id, "Assumptions!B5:B5", "0.0\"x\"")

# 3. Document hardcodes with cell notes
update_sheet_note(spreadsheet_id, "Assumptions!B2",
    "Source: 2025 budget assumptions, finalized 2025-Q4 ops review")
update_sheet_note(spreadsheet_id, "Assumptions!B3",
    "Source: 5-year strategic plan, 2025-09-15")

# 4. Define named ranges for the assumptions
add_sheet_named_range(spreadsheet_id, "growth_y1", "Assumptions!B2")
add_sheet_named_range(spreadsheet_id, "growth_y2_5", "Assumptions!B3")
add_sheet_named_range(spreadsheet_id, "discount_rate", "Assumptions!B4")
add_sheet_named_range(spreadsheet_id, "terminal_mult", "Assumptions!B5")

# 5. Model tab — formulas reference named ranges
write_sheet(spreadsheet_id, "Model!A1:F1",
    [["Year", "Revenue", "Growth", "EBITDA", "Margin", "PV"]])
format_sheet_range(spreadsheet_id, "Model!A1:F1",
    background_color=[0.063, 0.725, 0.506], font_color=[1,1,1], bold=True)

# Year 1 — formula references named range
write_sheet_formula(spreadsheet_id, "Model!B2", "=B1*(1+growth_y1)")
# Years 2-5
for y in range(3, 7):
    write_sheet_formula(spreadsheet_id, f"Model!B{y}", f"=B{y-1}*(1+growth_y2_5)")

set_sheet_number_format(spreadsheet_id, "Model!B2:B10", "$#,##0;($#,##0);-")
set_sheet_number_format(spreadsheet_id, "Model!C2:C10", "0.0%;(0.0%);-")
set_sheet_number_format(spreadsheet_id, "Model!E2:E10", "0.0%;(0.0%);-")

# 6. Verify (especially: change an assumption and confirm the model updates)
```

Operator workflow: edit one yellow cell on Assumptions → entire Model recalculates.

## Recipe 4: List + detail drill pattern (HOME + drill tabs)

When to use: high-level summary on one tab, with hyperlinks to detail tabs.

```python
# 1. Get sheet IDs (needed for HYPERLINK)
tabs = list_sheet_tabs(spreadsheet_id)
home_id = next(t["sheetId"] for t in tabs if t["title"] == "HOME")
inventory_id = next(t["sheetId"] for t in tabs if t["title"] == "Inventory")
ppc_id = next(t["sheetId"] for t in tabs if t["title"] == "PPC")

# 2. HOME tiles — each row is a KPI band with a HYPERLINK to drill
write_sheet(spreadsheet_id, "HOME!A4", [["WHAT TO TOUCH TODAY"]])
format_sheet_range(spreadsheet_id, "HOME!A4",
    background_color=[0.063, 0.725, 0.506], font_color=[1,1,1], bold=True)

write_sheet(spreadsheet_id, "HOME!A5:E5",
    [["Indicator", "Value", "Status", "Subtext", "Drill"]])
format_sheet_range(spreadsheet_id, "HOME!A5:E5",
    background_color=[0.157, 0.2, 0.318], font_color=[1,1,1], bold=True)

write_sheet(spreadsheet_id, "HOME!A6:D6",
    [["Inventory at risk", "=COUNTIFS('_raw_inventory'!A:A, \"<store>\", '_raw_inventory'!<woc_col>, \"<4\")",
      "AMBER", "SKUs with WoC<4 weeks"]])
write_sheet_formula(spreadsheet_id, "HOME!E6",
    f'=HYPERLINK("#gid={inventory_id}", "→ Open Inventory")')

write_sheet(spreadsheet_id, "HOME!A7:D7",
    [["PPC waste T7", "=SUMIFS('_raw_ppc'!<spend_col>, '_raw_ppc'!<acos_col>, \">0.5\")",
      "RED", "Spend with ACoS > 50%"]])
write_sheet_formula(spreadsheet_id, "HOME!E7",
    f'=HYPERLINK("#gid={ppc_id}", "→ Open PPC")')

# 3. Status chip colors via conditional format
add_sheet_conditional_format(spreadsheet_id, "HOME!C6:C100",
    condition_type="CUSTOM_FORMULA", value='=$C6="RED"',
    background_color=[0.929, 0.451, 0.431], font_color=[1,1,1])
add_sheet_conditional_format(spreadsheet_id, "HOME!C6:C100",
    condition_type="CUSTOM_FORMULA", value='=$C6="AMBER"',
    background_color=[1, 0.847, 0.42])
add_sheet_conditional_format(spreadsheet_id, "HOME!C6:C100",
    condition_type="CUSTOM_FORMULA", value='=$C6="GREEN"',
    background_color=[0.557, 0.792, 0.58], font_color=[1,1,1])
```

Operators click the drill links → land on the detail tab.

## Recipe 5: README + tabs index

When to use: any workbook with 3+ tabs needs a README so new operators know where things are.

```python
add_sheet_tab(spreadsheet_id, "README")

write_sheet(spreadsheet_id, "README!A1",
    [["<Report name> — <store(s)>"]])
format_sheet_range(spreadsheet_id, "README!A1",
    background_color=[0.063, 0.725, 0.506], font_color=[1,1,1], bold=True, font_size=14)

write_sheet(spreadsheet_id, "README!A2",
    [["Built <date> · <one-line description>. First open: Sheets will prompt 'Allow access to external images' — required for product thumbnails. Enable SellerSheet add-on (Extensions → SellerSheet → Open) for SQL() to evaluate."]])

write_sheet(spreadsheet_id, "README!A4", [["TABS IN THIS WORKBOOK"]])
format_sheet_range(spreadsheet_id, "README!A4",
    background_color=[0.157, 0.2, 0.318], font_color=[1,1,1], bold=True)

write_sheet(spreadsheet_id, "README!A5:D5",
    [["Tab", "Business question", "Refresh", "Notes"]])
format_sheet_range(spreadsheet_id, "README!A5:D5",
    background_color=[0.157, 0.2, 0.318], font_color=[1,1,1], bold=True)

write_sheet(spreadsheet_id, "README!A6:D<n>", tab_rows)

# Color legend section
write_sheet(spreadsheet_id, "README!A<n+2>", [["COLOR LEGEND"]])
# ... legend rows showing what each fill color means
```

Keep README simple — one paragraph + tab table + color legend.

## See also

- `scripts/formula-templates.md` — the formulas these recipes assemble
- `scripts/verify-after-write.md` — verify before declaring any recipe done
- `reference/brand-standards.md` — colors and formats used throughout

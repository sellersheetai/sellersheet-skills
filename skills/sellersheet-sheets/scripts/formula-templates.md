# Formula templates

Copy-paste formula library tested in production builds. Substitute placeholders in `<angle brackets>`.

## SQL spill — open range, with LIMIT and ORDER BY

Default catalog-data spill (200 row cap):

```javascript
=SQL("SELECT [store] AS [Store], [sku] AS [SKU], [asin] AS [ASIN], 
              [product] AS [Product], [your_price] AS [Price], 
              [afn_fulfillable_quantity] AS [Fulfillable], 
              [afn_reserved_quantity] AS [Reserved], [inbound_total] AS [Inbound], 
              [afn_warehouse_quantity] AS [Warehouse Qty] 
       FROM ? 
       WHERE [afn_warehouse_quantity] > 0 
       ORDER BY [afn_warehouse_quantity] DESC, [sku] ASC 
       LIMIT 200", 
     '_raw_inventory'!A1:R)
```

Small-dataset spill (50 row cap):

```javascript
=SQL("SELECT [store] AS [Store], [metric] AS [Metric], 
              [value] AS [Value], [threshold] AS [Threshold] 
       FROM ? 
       ORDER BY [store], [metric] 
       LIMIT 50", 
     '_raw_account_health'!A1:F)
```

Top-N spill (20 row cap):

```javascript
=SQL("SELECT [store] AS [Store], [sku] AS [SKU], 
              [sales_30d] AS [30d Sales], [units_30d] AS [Units 30d] 
       FROM ? 
       WHERE [sales_30d] > 0 
       ORDER BY [sales_30d] DESC 
       LIMIT 20", 
     '_raw_inventory'!A1:R)
```

## SQL spill with JOIN

Join one `_raw_*` table to another (e.g., PPC × COGS for margin-net columns):

```javascript
=SQL("SELECT s.[store] AS [Store], s.[sku] AS [SKU], s.[asin] AS [ASIN],
              s.[spend_30d] AS [Spend (30d)], s.[purchases_30d] AS [Purchases (30d)],
              s.[sales_30d] AS [Sales (30d)],
              c.[margin_net] AS [Margin Net %], c.[profit_net_per_unit] AS [Profit Net/unit]
       FROM ? s LEFT JOIN ? c
         ON s.[store] = c.[store] AND s.[sku] = c.[sku]
       ORDER BY s.[spend_30d] DESC
       LIMIT 200",
     '_raw_ppc_attribution'!A1:I, '_raw_cogs'!A1:V)
```

## Canonical Image-at-A formula (with `_raw_catalog` JOIN)

```javascript
=MAP(SQL("SELECT cat.[image_url] 
          FROM ? AS data LEFT JOIN ? AS cat 
            ON data.[store]=cat.[store] AND data.[sku]=cat.[sku] 
          <WHERE clause matching the data SQL> 
          ORDER BY <same as data SQL>
          <LIMIT N matching data SQL>",
         '_raw_<self>'!A1:<lastcol>, '_raw_catalog'!A1:E),
     LAMBDA(url, IF(url="image_url", "Image",
                    IF(url="", "", IMAGE(url)))))
```

Concrete example for Inventory and Restock:

```javascript
=MAP(SQL("SELECT cat.[image_url] 
          FROM ? AS data LEFT JOIN ? AS cat 
            ON data.[store]=cat.[store] AND data.[sku]=cat.[sku] 
          WHERE data.[afn_warehouse_quantity] > 0 
          ORDER BY data.[afn_warehouse_quantity] DESC, data.[sku] ASC 
          LIMIT 200", 
         '_raw_inventory'!A1:R, '_raw_catalog'!A1:F),
     LAMBDA(url, IF(url="image_url", "Image", IF(url="", "", IMAGE(url)))))
```

## Overflow footer (1 row below max spill extent)

When the spill is anchored at row N with LIMIT M, the data ends at row N+M. Footer at row N+M+1:

```javascript
="Showing first 200 of " 
  & COUNTIFS('_raw_inventory'!A:A, "<store>", '_raw_inventory'!<filter_col>:<filter_col>, ">0") 
  & " rows (LIMIT 200 guard). See _raw_inventory tab for the full list."
```

Simpler version (no WHERE filter):

```javascript
="Showing first 200 of " 
  & (COUNTA('_raw_inventory'!A:A) - 1) 
  & " rows. See _raw_inventory tab for the full catalog list."
```

Format with soft yellow `[1, 0.949, 0.8]` bg + italic.

## Conditional gradient (red → amber → green)

```python
add_sheet_conditional_format(
    spreadsheet_id, range_="Inventory!I9:I1000",
    gradient=True,
    min_color=[0.929, 0.451, 0.431],
    mid_color=[1, 0.847, 0.42],
    max_color=[0.557, 0.792, 0.58],
    min_value=0, mid_value=8, max_value=20)
```

## Value-based chip (TEXT_EQ)

```python
add_sheet_conditional_format(
    spreadsheet_id, range_="Inventory!B9:B1000",
    condition_type="TEXT_EQ", values=["REORDER"],
    background_color=[0.929, 0.451, 0.431], font_color=[1,1,1])
```

## CUSTOM_FORMULA — portable fallback

When the simpler condition types error on your MCP version:

```python
# Status badge GREEN-fresh
add_sheet_conditional_format(
    spreadsheet_id, range_="_status!I2:I100",
    condition_type="CUSTOM_FORMULA", value='=LEFT($I2,5)="GREEN"',
    background_color=[0.776, 0.91, 0.835])

# Compound condition: negative margin AND ad cost > 0
add_sheet_conditional_format(
    spreadsheet_id, range_="Profit and Cash!P9:P1000",
    condition_type="CUSTOM_FORMULA", value='=AND($P9<0, $T9>0)',
    background_color=[0.957, 0.78, 0.765])
```

## FX VLOOKUP in `_raw_cogs`

```javascript
// Landed cost in marketplace currency (e.g. USD) from total RMB
=M2 / VLOOKUP("USD", cfg_fx, 2, FALSE)

// Profit (marketplace currency) = price - fees - landed
=F2 - I2 - N2

// Margin %
=IFERROR(O2/F2, "")

// Suggested price (target ~37% gross margin)
=Q2 * 1.6
```

`cfg_fx` is the named range pointing at `_config!A2:B5` (currency, rate-per-RMB columns).

## `=HYPERLINK` to drill tabs from a HOME tab

```javascript
=HYPERLINK("#gid=" & <sheet_id>, "→ Open <Tab Name>")
```

Pull real `<sheet_id>` from `list_sheet_tabs` — never hardcode plain text arrows like `"→ Open"` without the hyperlink.

## Sparkline patterns

30-day line:

```javascript
=SPARKLINE(_raw_metric_daily!B2:B31, {"charttype","line"; "color1","#10B981"; "linewidth",2})
```

Win/loss for binary daily state:

```javascript
=SPARKLINE(_raw_buybox_daily!B2:B31, {"charttype","winloss"; "color1","#10B981"; "negcolor","#EE7370"})
```

Bounded axis (e.g. AHR with 0-1000 range):

```javascript
=SPARKLINE(_raw_ahr_daily!B2:B31, {"charttype","line"; "color1","#10B981"; "ymin",0; "ymax",1000})
```

## Common aggregations on HOME

Concentration risk (top SKU as % of store revenue):

```javascript
="Top SKU 30d = " 
  & TEXT(MAX(SUMIFS('_raw_inventory'!<sales_col>, '_raw_inventory'!A:A, "<store>")) 
       / SUM(SUMIFS('_raw_inventory'!<sales_col>, '_raw_inventory'!A:A, "<store>")), "0%") 
  & " of <store> revenue"
```

Dead capital (per store):

```javascript
=SUMPRODUCT(
  ('_raw_inventory'!A:A="<store>") * 
  ('_raw_inventory'!<units_t30_col>=0) * 
  ('_raw_inventory'!<available_col>) * 
  ('_raw_inventory'!<your_price_col>) * 0.4)
```

(0.4 multiplier is a fallback when COGS isn't populated — conservative dead-capital estimate.)

FX freshness alert (HOME):

```javascript
="FX last refreshed: " & TEXT(MAX(_config!C2:C), "yyyy-mm-dd")
  & IF((TODAY() - MAX(_config!C2:C)) > 14, " ⚠️ STALE (>14d)", " ✓ fresh")
```

## TEXTJOIN for inline freshness pills

```javascript
=TEXTJOIN(" · ", TRUE,
  "<purpose>",
  "<source1> " & IFERROR(<status lookup>, "?"),
  "<source2> " & IFERROR(<status lookup>, "?"),
  "as of " & TEXT(<oldest timestamp lookup>, "yyyy-mm-dd hh:mm") & " UTC")
```

Useful for any "live freshness pill" row 2 above a growable table.

## IFERROR wrapping

Always wrap formulas that could legitimately fail (VLOOKUP, MATCH, division):

```javascript
=IFERROR(VLOOKUP(B5, _raw_catalog!A:E, 4, FALSE), "")
=IFERROR(O2/F2, 0)
=IFERROR(SUMPRODUCT(...) / COUNTIF(...), "—")
```

Prevents `#N/A`, `#DIV/0!` from propagating into the visible tab.

## See also

- `scripts/verify-after-write.md` — verify formulas after writing
- `scripts/starter-recipes.md` — common report patterns assembled from these templates
- `reference/sql-function.md`, `reference/image-pattern.md` — pattern specs

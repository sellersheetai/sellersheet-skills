# Growable tables — `_raw_*` + `SQL()` pattern

The default for any list-style report — inventory, ad performance, listings, financials, anything that grows as data is appended. Hidden `_raw_<topic>` tabs hold data; visible tabs spill it via `SQL()`.

## The four rules

1. **Visible tabs never hold data.** They hold one anchor formula per column block. Data lives in hidden `_raw_<topic>` tabs.
2. **`SQL()` is one formula per table** — not one per column. `SQL("SELECT col AS [Friendly Name], ... FROM ?", _raw_<topic>!A1:<lastcol>)` spills both the header row and all rows in a single anchor cell.
3. **Use open-ended ranges** like `_raw_<topic>!A1:M` (no end row). `SQL()` internally filters blank rows, so trailing empties don't pollute output. As you append rows to `_raw_*`, the visible table grows automatically — up to the `LIMIT N` cap (see `reference/sql-function.md`).
4. **The growable table is the LAST element on its sheet.** Footers, notes, and summary lines go ABOVE the table — never below — so growth doesn't collide.

## The shape

```
Visible tab "Inventory":
  Row 1   Title (merged, SellerSheet emerald)
  Row 2   Freshness line (light gray, 9pt)
  Row 3   spacer
  Row 4   Section band (emerald, merged)
  Row 5   Summary / notes (above the table)
  Row 6   "Top X at risk:" callout (yellow background)
  Row 7   spacer
  Row 8   Image header (A) + SQL spill headers (B onward) — navy bg, white bold
  Row 9+  Image cells (A) + SQL data spill (B onward) — open-ended, grows up to LIMIT
  Row 209 Overflow footer (1 row below max spill extent if LIMIT 200 in effect)

Hidden tab "_raw_inventory":
  Row 1   machine-named headers (store, sku, asin, image_url, product, ...)
  Row 2+  data
```

Footers never go below the table. The growable table is always the last element.

## Store column — the multi-store identifier (leads SKU)

**Every `_raw_*` tab and every visible SKU/ASIN table includes a `store` column right before `sku`.** Canonical form: `storename-countrycode` — e.g. `myStore-US`, `myStore-UK`, `myStore-DE`. Same identifier shape the SellerSheet sidebar and MCP tools use.

Visible column order: `Image | Store | SKU | ASIN | Product | ...rest`. The Store column is short (~80 px wide — codes like `myStore-AE` fit) and gives operators immediate scoping context BEFORE the product identifier — the natural grouping order when rows span multiple stores.

Why this matters:
- Any report that aggregates across multiple stores becomes ambiguous without a Store column.
- Even a single-store dashboard should include it from day one — free defense against future multi-store expansion.
- Multi-marketplace EU stores get distinct `store` values per marketplace (`myStore-UK`, `myStore-DE`, ...) — the same row format works for single-mkt and multi-mkt.

In `_raw_*` tabs the corresponding column order is: `store, sku, asin, image_url, product, ...`. **Set `store` on every row at write time** — the MCP `query_report_data` doesn't echo it back; the caller adds it.

```javascript
=SQL("SELECT [store] AS [Store], [sku] AS [SKU], [asin] AS [ASIN], [product] AS [Product],
              [sales_30d] AS [30d Sales], [woc_t30] AS [WoC T30], [note] AS [Note]
      FROM ?
      ORDER BY [store], [sku]
      LIMIT 200",
     '_raw_inventory'!A1:N)
```

When the visible table may show rows from multiple stores, sort by store first to keep them clustered. To filter to one store inside a multi-store `_raw_*` tab, the WHERE clause lives in SQL:

```javascript
=SQL("SELECT ... FROM ? WHERE [store] = 'myStore-UK' ORDER BY [sku] LIMIT 200",
     '_raw_inventory'!A1:N)
```

## When NOT to use the `_raw_*` + `SQL()` pattern

- **Single-cell KPI tiles** (a HOME dashboard's lag/lead grid). Use `write_sheet` direct — one value per cell.
- **Small fixed-shape sections** (≤3 rows, sandwiched between other sections above and below). Use closed ranges + per-cell formulas.
- **Cell-level styling that varies with data values** in ways not captured by conditional formatting (e.g., highlighting based on a complex multi-cell calculation). Hand-format the cells; don't try to drive it from SQL.
- **Server-side-only consumers** that never open the workbook in a browser. `SQL()` doesn't render server-side.

## Multi-store / multi-marketplace patterns

| Scope | Approach |
|---|---|
| Single store | Hardcode the store in queries. Still write the `store` value into `_raw_*` Store column on every row. |
| Multi-store same workbook | N queries — one per store. Union into a single `_raw_*` tab. Visible SQL sorts by store first. |
| Multi-marketplace store (one seller_id, many marketplaces — EU) | One query per marketplace (passing each as `myStore-UK`, `myStore-DE`, ...). Union into `_raw_*`. Each row's Store cell carries the marketplace — the level operators actually decide on. |

In all three cases the visible-tab column order stays `A=Image, B=Store, C=SKU, D=ASIN, ...` — uniform shape regardless of single/multi scope.

## Data flow

```
rpt_<topic> table (your SellerSheet data warehouse)
        │  query_report_data() MCP
        ▼
_raw_<topic> hidden Sheets tab    
  - one row per source rpt_* row
  - first 5 cols: store, sku, asin, image_url, product
  - then domain-specific columns
        │  alasql SQL() function (SellerSheet GAS add-on, browser-side)
        ▼
visible "<Tab>" Sheets tab
  - row 1: emerald title
  - row 2: live freshness pill
  - row 4+: rollup sections (formulas pointing at _raw_*)
  - row N: section band + SQL anchor (the growable spill, with LIMIT)
        │  =HYPERLINK("#gid=...")
        ▼
operator reads & decides
```

For each growable section in step 4 of the build workflow:

1. **Query** `query_report_data(...)` against the relevant `rpt_*` table.
2. **Write** the result to a hidden `_raw_<topic>` tab. Headers in row 1 (machine names: `sku`, `asin`, `image_url`, `product`, `sales_30d`, `woc_t30`...), data rows 2+.
3. **Mark user-input cells yellow** in `_raw_*` (e.g. `_raw_cogs` selling-price / FBA-fee / product-cost / weight columns). Computed columns get formulas referencing config cells.
4. **Anchor the visible table at the end of its tab.** Image column at A via the `MAP+LAMBDA+IMAGE` pattern. `SQL("SELECT col AS [Friendly Name] FROM ? ... LIMIT N", _raw_<topic>!A1:<lastcol>)` at B for the rest.
5. **Format the spilled header row** with navy bg + white bold so it stands out from data rows.
6. **Add an overflow footer** if `LIMIT N` is in effect — 1 row below the maximum spill extent — see `reference/sql-function.md`.

## See also

- `reference/sql-function.md` — SQL() syntax, bracket-quoting, JOIN rules, LIMIT defaults
- `reference/image-pattern.md` — Image-at-A canonical formula
- `reference/conditional-formatting.md` — open-range gradients + value-based chips
- `reference/mcp-gotchas.md` — chunked writes for large query payloads

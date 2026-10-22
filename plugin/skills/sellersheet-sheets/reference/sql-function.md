# `SQL()` function — the SellerSheet add-on custom function

Defined in the SellerSheet GAS add-on (browser-side). Powers every growable table in this skill. Server-side reads cannot evaluate it — `#NAME?` is the expected pending state until first browser-side eval.

## Signature

```
=SQL(sqlAsString, dataAsArray1, ...dataAsArrays)
```

- First row of each range = headers (becomes the `SQL()` column names).
- `?` in the SQL string is the placeholder for the first range; repeat `?` for additional ranges.
- Output: 2D array — header row first, then data rows. Spills from the anchor cell.

## Bracket-quote every column reference AND every alias

The `SQL()` engine treats many common words as reserved keywords — `store`, `status`, `date`, `index`, `order`, `year`, `month`, `decision`, `action`, `currency`, `unique`, `column`, `select`, `from`, `where`, `group`, `having`, `count`. Bare `SELECT store AS Store` throws:

```
SyntaxError: Parse error... Expecting 'LITERAL', 'BRALITERAL', ... got 'STORE'
```

**Rule:** wrap **every** column name AND **every alias** in square brackets, in SELECT, ORDER BY, WHERE, GROUP BY, HAVING — even ones that look safe.

Empirically — `AS [Store], AS [SKU], AS [Spend], AS [Margin Net %]` works; `AS Store, AS SKU` returns `#ERROR!`. The percent sign needs brackets too (acts as escape).

```javascript
=SQL("SELECT [store] AS [Store], [sku] AS [SKU], [asin] AS [ASIN], 
              [product] AS [Product], [sales_30d] AS [30d Sales], 
              [woc_t30] AS [WoC T30], [note] AS [Note] 
       FROM ? 
       ORDER BY [store], [sku]
       LIMIT 200", 
     '_raw_inventory'!A1:N)
```

## Multi-table JOINs — same bracketing rule

`FROM ? s LEFT JOIN ? c ON ...` and `FROM ? as s LEFT JOIN ? as c ON ...` both parse. The `as` keyword is optional. Table-alias-prefix syntax is valid: `s.[bracketedColumn]`.

```javascript
=SQL("SELECT s.[store] AS [Store], s.[sku] AS [SKU], s.[spend_30d] AS [Spend],
              c.[margin_net] AS [Margin Net %]
       FROM ? s LEFT JOIN ? c
         ON s.[store] = c.[store] AND s.[sku] = c.[sku]
       ORDER BY s.[spend_30d] DESC
       LIMIT 200",
       '_raw_ppc'!A1:I, '_raw_cogs'!A1:V)
```

`COALESCE(l.[sku], r.[sku])` with `FULL OUTER JOIN` works too — useful when one side has rows the other doesn't.

## Always `LIMIT` SQL spills that scale with data size

A growing catalog can push a SQL spill to thousands of rows. Two failure modes:
1. **Spill collision** — the spill grows past whatever sits below it (next section, AGENT INSIGHTS block, footer) and aborts with `#REF! "Array result was not expanded because it would overwrite data in <cell>"`.
2. **Browser performance** — thousands of IMAGE() cells stall the tab.

**Rule:** every SQL spill that scales with data size MUST end with `LIMIT N` where N matches the row budget reserved for that section.

## Minimum gap before the next section

A SQL() spill at row R with `LIMIT N` occupies rows R through R+N (1 header row + N data rows). Any content — a section band, a note, another SQL anchor — placed at row R+N or earlier causes:

```
#REF! Array result was not expanded because it would overwrite data in <cell>
```

**Rule:** place the next content at row R + N + 2 minimum (the +2 gives one overflow footer row and one spacer).

```
Row R      SQL() anchor   ← header lands here
Row R+1    data row 1
...
Row R+N    data row N
Row R+N+1  overflow footer (soft yellow note)
Row R+N+2  spacer
Row R+N+3  ← safe to start the next section band
```

For a tab with multiple SQL() sections, compute the anchor for each section from the previous section's end:

| Section | Anchor | LIMIT | Overflow footer | Next section |
|---|---|---|---|---|
| 1 | row 6 | 20 | row 27 | row 28+ |
| 2 | row 29 | 15 | row 45 | row 46+ |
| 3 | row 47 | 10 | row 58 | row 59+ |

If you get a `#REF!` on a SQL() formula, the first thing to check is whether the next non-empty row above the error is within LIMIT rows of the anchor.

## Default LIMITs per data scope

| Data scope | Default LIMIT | Why |
|---|---|---|
| Catalog data (inventory, listings, COGS, returns, buy box) | **200** | Operators act on top-200; long tail is review-by-export |
| Time-series detail (PPC campaigns, attribution, search terms, advertised products) | **200** | Same reasoning |
| Catalog master (product image catalog) | **500** | Joined by every Image column; most catalogs are 100-500 active |
| Small datasets (account health, finance summary) | **50** | Bounded by metric count × stores |
| Top-N reports (top SKUs, top campaigns) | **20** | One-screen visibility |
| Findings tables (audit results, qa) | **100** | Reviewer scope |

These defaults apply per **data scope**, not per visible tab. A single visible tab may have multiple spills — each gets its own LIMIT.

## Overflow footer — mandatory companion to `LIMIT`

When the LIMIT may truncate, surface it. Place an overflow footer **1 row below the maximum spill extent**.

If the spill is anchored at row N with LIMIT M, the data ends at row `N+M`. The footer goes at row `N+M+1`.

```javascript
="Showing first 200 of " 
  & COUNTIFS('_raw_<tab>'!A:A, "<store>", '_raw_<tab>'!<filter_col>:<filter_col>, ">0") 
  & " rows (LIMIT 200 guard). See _raw_<tab> tab for the full list."
```

Or simpler (no WHERE filter):

```javascript
="Showing first 200 of "
  & (COUNTA('_raw_<tab>'!A:A) - 1)
  & " rows. See _raw_<tab> for the full list."
```

Format with soft yellow `[1, 0.949, 0.8]` bg + italic so it reads as a notice, not a data row.

## Image column LIMIT must match data column LIMIT

The image MAP+SQL formula at column A and the data SQL at column B must have **identical** `WHERE`, `ORDER BY`, and `LIMIT`. Otherwise image rows desync from data rows row-for-row.

See `reference/image-pattern.md` for the full canonical image formula.

## Server-side behavior

Server-side `read_sheet` returns `#NAME?` on every `=SQL(...)` cell until the workbook is opened in a browser with the SellerSheet add-on. That's expected — see `reference/error-semantics.md`. Don't rewrite a formula thinking it's broken because a server read shows `#NAME?`.

## Open-range data tabs

Always reference `_raw_*` with an open-ended range:

| ❌ Don't | ✅ Do |
|---|---|
| `'_raw_inventory'!A1:R1000` | `'_raw_inventory'!A1:R` |
| `'_raw_cogs'!A2:R500` | `'_raw_cogs'!A2:R` |

`SQL()` ignores trailing blank rows. The closed-range form silently truncates when the source grows past the locked row count.

## WHERE clause patterns

```javascript
// Single-store filter
WHERE [store] = 'myStore-UK'

// Multi-store inclusion
WHERE [store] IN ('myStore-US', 'myStore-UK')

// Numeric threshold (column must be numeric — see reference/mcp-gotchas.md)
WHERE [woc_t30] > 4
WHERE [afn_warehouse_quantity] > 0 AND [units_t30] = 0

// Text matching (regex via REGEXP_LIKE)
WHERE [decision] = 'DEAD'
WHERE REGEXP_LIKE([sku], '^SKU-A')
```

Comparisons on numeric columns silently fail if the cell holds `""` instead of being blank. See `reference/mcp-gotchas.md`.

## ORDER BY patterns

```javascript
// Group by store first
ORDER BY [store], [sku]

// Top-N by spend descending
ORDER BY [spend_30d] DESC

// Multi-key sort
ORDER BY [store] ASC, [decision] ASC, [sku] ASC

// Mix with JOIN — qualify the table alias
ORDER BY s.[store], s.[sku]
```

## Post-anchor number formatting

**SQL() outputs raw numbers. It never applies number formatting to the cells it writes into.** After anchoring every SQL() formula, apply `numberFormat` to each numeric output column in the spill zone.

Without this step:
- ACoS stored as `0.141` renders as `0.141` not `14.1%`
- ROAS stored as `7.1` renders as `7.1` not `7.1x`
- Spend stored as `20.48` renders as `20.48` not `$20.48`

**How to apply:** use `sheet_batch_update` with `repeatCell` + `userEnteredFormat.numberFormat`. One call covers all numeric columns across all SQL anchors on a tab. Never use individual `set_sheet_number_format` calls for this — each one is a separate HTTP request and will hit the rate limit on accounts with multiple SQL sections.

```python
# After anchoring SQL() at row R (1-indexed), LIMIT N, for sheetId SID:
# Apply to rows R through R+N (header + all data rows = R-1 to R+N in 0-indexed)
sheet_batch_update(spreadsheet_id, [
    # Currency column at index COL (0-indexed from A)
    {"repeatCell": {
        "range": {"sheetId": SID,
                  "startRowIndex": R-1, "endRowIndex": R+N,
                  "startColumnIndex": COL, "endColumnIndex": COL+1},
        "cell": {"userEnteredFormat": {
            "numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}
        }},
        "fields": "userEnteredFormat.numberFormat"
    }},
    # Percent column — NOTE: stores fraction (0.141), PERCENT format multiplies ×100
    {"repeatCell": {
        "range": {"sheetId": SID,
                  "startRowIndex": R-1, "endRowIndex": R+N,
                  "startColumnIndex": COL, "endColumnIndex": COL+1},
        "cell": {"userEnteredFormat": {
            "numberFormat": {"type": "NUMBER", "pattern": "0.0%"}
        }},
        "fields": "userEnteredFormat.numberFormat"
    }},
    # ROAS / multiples column
    {"repeatCell": {
        "range": {"sheetId": SID,
                  "startRowIndex": R-1, "endRowIndex": R+N,
                  "startColumnIndex": COL, "endColumnIndex": COL+1},
        "cell": {"userEnteredFormat": {
            "numberFormat": {"type": "NUMBER", "pattern": "0.0\"x\""}
        }},
        "fields": "userEnteredFormat.numberFormat"
    }},
])
```

**Column index from SELECT order:** the first column in the SELECT is index 0 (column A), the second is index 1 (column B), etc. Map each alias to its 0-indexed column position to know which `startColumnIndex` to use.

**Also applies to SUMIF/COUNTIF KPI tile cells.** Formula cells that compute totals (not SQL spills) also return raw numbers. Apply the same `numberFormat` treatment to them directly — especially ROAS tiles which need `0.0"x"`, not CURRENCY.

**Common format patterns for Amazon ad metrics:**

| Metric | Stored as | Pattern | Type |
|---|---|---|---|
| Spend, Sales, CPC, Budget | decimal (`20.48`) | `$#,##0.00` | CURRENCY |
| ACoS, CTR, CVR, utilisation | fraction (`0.141`) | `0.0%` | NUMBER |
| ROAS | multiple (`7.1`) | `0.0"x"` | NUMBER |
| Impressions, Clicks, Orders | integer (`1260`) | `#,##0` | NUMBER |

## See also

- `reference/image-pattern.md` — Image MAP+SQL alignment with data SQL
- `reference/growable-tables.md` — when this pattern applies
- `reference/error-semantics.md` — `#NAME?` is pending; `#REF!` is real bug
- `scripts/formula-templates.md` — copy-paste SQL + overflow footer
- `reference/mcp-gotchas.md` — rate limit and why `sheet_batch_update` beats individual format calls

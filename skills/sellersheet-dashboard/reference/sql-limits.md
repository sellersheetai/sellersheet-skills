# SQL spill LIMITs + overflow guard

Every `SQL()` spill that reads from a `_raw_*` tab must end with `LIMIT N` matching the row budget for that section. Without it, two failure modes:

1. **Spill collision** — the spill grows past whatever sits below it (next section, AGENT INSIGHTS, footer) and aborts with `#REF! "Array result was not expanded because it would overwrite data in <cell>"`. The whole tab then shows `#REF!`.
2. **Browser performance** — thousands of `IMAGE()` cells stall the tab; a 5,000-row inventory spill makes the dashboard unusable.

## Default LIMITs per `_raw_*` data scope

These defaults apply per **data scope**, not per visible tab. A single visible tab may have multiple spills (e.g. Listing Health has both a Listings spill AND a Buy Box spill) — each gets its own LIMIT.

| `_raw_*` tab | Default `LIMIT` | Why this number |
|---|---|---|
| `_raw_inventory` | **200** | Operators act on the top-200 active SKUs by warehouse qty; long tail is review-by-export |
| `_raw_listings` | **200** | Suppressed + stranded count rarely exceeds 100; 200 leaves headroom |
| `_raw_account_health` | **20** | Small dataset — 1 row per store × component; even 5 stores = 10 rows |
| `_raw_ppc` | **100** | Campaign count rarely exceeds 50 per store; 100 covers 2-store launches |
| `_raw_ppc_attribution` | **200** | Per-SKU ad attribution — bounded by SKU count of advertised products |
| `_raw_ppc_search_terms` | **200** | Top 200 by ACoS or spend; rest aren't actionable |
| `_raw_ppc_skus` | **200** | Same as attribution |
| `_raw_cogs` | **500** | User-entered table; bounded by manual data-entry capacity |
| `_raw_catalog` | **500** | Master table joined by every Image column — most catalogs are 100-500 active SKUs |
| `_raw_returns` | **200** | T30 returns rarely exceed 100 per store |
| `_raw_buybox` | **200** | One row per ASIN with buy-box state; bounded by catalog |
| `_raw_finance` | **50** | Aggregated settlements — N rows per store per period |

**These are minimums for the SQL spill, not the underlying `_raw_*` row count.** The `_raw_*` tab can hold thousands of rows; the spill just truncates the visible projection to the top N.

## When to deviate from the default

- **Increase LIMIT** when the catalog actually exceeds it AND operators need to see all rows on the dashboard (rare). Then move AGENT INSIGHTS to row 600+ to accommodate.
- **Decrease LIMIT** when the spill is on a constrained tab (HOME with multiple sections stacked). Use `LIMIT 20` for Top-N tile sections.
- **No LIMIT** is acceptable only when:
  1. The data scope is provably bounded (e.g., `_raw_account_health` with one row per store per component — at most ~20 rows for a 5-store seller), AND
  2. AGENT INSIGHTS is anchored at row 150+ with overflow buffer.

## Overflow footer (mandatory companion to `LIMIT`)

Every LIMITed spill gets a footer 1 row below the maximum spill extent telling operators when truncation is active.

**Position:** if the spill anchor is at row `N` and `LIMIT = M`, the data ends at row `N + M`. Place the footer at row `N + M + 1`.

**Format:** soft yellow background `[1, 0.949, 0.8]`, italic font.

**Content:**

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

## Image column LIMIT must match data column LIMIT

The Image MAP+SQL at column A and the data SQL at column B must have **identical** `WHERE`, `ORDER BY`, and `LIMIT`. Otherwise image rows desync from data rows.

```javascript
// Column A — image with JOIN
=MAP(SQL("SELECT cat.[image_url]
          FROM ? AS data LEFT JOIN ? AS cat
            ON data.[store]=cat.[store] AND data.[sku]=cat.[sku]
          WHERE data.[afn_warehouse_quantity] > 0
          ORDER BY data.[afn_warehouse_quantity] DESC, data.[sku] ASC
          LIMIT 200",
         '_raw_inventory'!A1:R, '_raw_catalog'!A1:F),
     LAMBDA(url, IF(url="image_url", "Image", IF(url="", "", IMAGE(url)))))

// Column B — data
=SQL("SELECT [store] AS [Store], [sku] AS [SKU], ...
      FROM ?
      WHERE [afn_warehouse_quantity] > 0
      ORDER BY [afn_warehouse_quantity] DESC, [sku] ASC
      LIMIT 200",
     '_raw_inventory'!A1:R)
```

Same `WHERE`, same `ORDER BY`, same `LIMIT`. If you change one, change both.

## AGENT INSIGHTS row anchor sizing

The LIMIT determines the maximum spill extent, which determines where AGENT INSIGHTS can land safely.

| Spill anchor row | LIMIT | Max spill extent | Min AGENT INSIGHTS anchor |
|---|---|---|---|
| Row 8 | 20 | Row 28 | Row 40 |
| Row 8 | 50 | Row 58 | Row 70 |
| Row 8 | 100 | Row 108 | Row 120 |
| Row 8 | 200 | Row 208 | Row 220 |
| Row 14 | 200 | Row 214 | Row 230 |
| Row 14 | 500 | Row 514 | Row 530 |

**Default anchor convention:**
- **Row 150** for tabs with LIMIT ≤ 100 (HOME, PPC Command, Account Health, Returns and Refunds).
- **Row 400** for tabs with LIMIT 200-500 (Inventory and Restock, Listing Health, Profit and Cash with COGS spill).

When in doubt, anchor at row 400+ — the cost of an extra 250 empty rows is zero; the cost of a spill collision is the entire tab going `#REF!`.

## Multi-store impact on LIMITs

When `_raw_*` carries rows for N stores, the SQL spill returns rows for all N stores by default. Two patterns:

**Pattern A — single spill, sorted by store:**
```javascript
=SQL("SELECT [store] AS [Store], [sku] AS [SKU], ... FROM ? ORDER BY [store], [sku] LIMIT 200", _raw_inventory!A1:R)
```
LIMIT 200 split across 2 stores = ~100 rows per store visible. Fine for cross-store comparison views.

**Pattern B — store-scoped spill (one section per store):**
```javascript
=SQL("SELECT [sku] AS [SKU], ... FROM ? WHERE [store] = 'myStore-US' ORDER BY ... LIMIT 200", _raw_inventory!A1:R)
```
Full LIMIT 200 per store. Use when each store gets its own section on a tab.

Pattern A is the default; pattern B is for HOME-style per-store bands.

## When the underlying `_raw_*` exceeds the LIMIT

The overflow footer surfaces this to the operator. The full data lives in `_raw_*` (unfiltered) so a click-into-raw-tab gives the long tail.

If operators routinely need more than 200 rows on a visible tab, that's a signal to:
1. Add a more aggressive `WHERE` filter to the spill (e.g., `WHERE [woc] < 4` for restock-only view), OR
2. Add a separate visible tab for the long tail (e.g., "Inventory Full" with no filter), OR
3. Increase the LIMIT and re-anchor AGENT INSIGHTS.

Don't quietly raise LIMITs without re-anchoring AGENT INSIGHTS — that's how `#REF!` cascades happen.

## See also

- `reference/agent-insights.md` — AGENT INSIGHTS row anchor rule
- `reference/image-catalog.md` — Image MAP+SQL pattern with matching LIMIT
- `reference/error-semantics.md` — diagnosing `#REF!` spill collisions
- `scripts/formula-templates.md` — copy-paste SQL spills + overflow footer

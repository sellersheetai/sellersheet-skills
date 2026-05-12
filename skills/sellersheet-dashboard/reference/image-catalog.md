# Single-source image catalog + SQL() patterns

`image_url` lives in exactly one tab — `_raw_catalog`. Every visible SKU table joins to it for the Image column. Also covers the alasql bracket-quote rule and the canonical Image-at-A formula.

## `_raw_catalog` schema

5 columns. One row per `(store, sku)` pair across the dashboard's stores. Populate from `listing_images` for image_url and `rpt_listings_snapshot` for product display name:

| Col | Header | Notes |
|---|---|---|
| A | `store` | canonical storename-countrycode: myStore-US, myStore-US, myStore-UK, ... |
| B | `sku` | canonical seller_sku |
| C | `asin` | |
| D | `image_url` | URL from listing_images.main_image_url; blank if not yet enriched |
| E | `product` | truncated display name, ~80 chars max |

Refresh cadence: daily. Image enrichment in `listing_images` is itself a long-lived cache; the catalog inherits that stability.

## Why single-source over duplication

- **Single refresh target.** Update `_raw_catalog` once; every visible Image column updates. Adding a new tab is one JOIN, not a new image_url column to populate.
- **No drift.** When `listing_images` enriches a previously-blank SKU, `_raw_catalog` reflects it on next refresh; every dashboard tab gets the new thumbnail simultaneously.
- **Smaller per-tab `_raw_*` payloads.** PPC SKUs goes from ~12 cols to ~11; COGS goes from ~22 to ~21.
- **Sparse coverage handled gracefully.** Missing image (NULL in catalog) → blank cell via the LAMBDA guard.

Same logic applies to `product` display name and `asin` — any SKU master attribute that's identical across data tabs and changes rarely.

## Canonical Image-at-A formula (with JOIN)

Every visible SKU/ASIN table puts the Image column at A via a JOIN against `_raw_catalog`:

```javascript
=MAP(SQL("SELECT cat.[image_url] 
          FROM ? AS data LEFT JOIN ? AS cat 
            ON data.[store] = cat.[store] AND data.[sku] = cat.[sku] 
          ORDER BY <same ORDER BY as the visible data SQL>
          [LIMIT <same LIMIT as the visible data SQL>]", 
         '_raw_<self>'!A1:<lastcol>, '_raw_catalog'!A1:E),
     LAMBDA(url, IF(url="image_url", "Image",
                    IF(url="", "", IMAGE(url)))))
```

**Three alignment constraints** the image SQL must satisfy:

1. **Same `ORDER BY` as the data SQL** on the same tab — otherwise image rows desync from data rows.
2. **Same `WHERE` clause** as the data SQL — same row count.
3. **Same `LIMIT`** (if any) as the data SQL — image column truncates at the same point.

Examples:

| Visible tab | Data SQL `ORDER BY` | Image SQL `ORDER BY` |
|---|---|---|
| Inventory and Restock | `[afn_warehouse_quantity] DESC, [sku] ASC` | `data.[afn_warehouse_quantity] DESC, data.[sku] ASC` |
| PPC Command Top SKUs | `[spend_30d] DESC` | `data.[spend_30d] DESC` |
| Listing Health | `[store], [status_change_date]` | `data.[store], data.[status_change_date]` |
| Profit and Cash | `[store], [sku]` | `data.[store], data.[sku]` |

## Header detection inside LAMBDA — the off-by-one fix

`IF(url="image_url", "Image", ...)` is what makes the first MAP iteration render the column header at the same row as the visible SQL's header row.

**Without it** you get an off-by-one — `={"Image"; MAP(SQL(...), ...)}` shifts every image down one row because the SQL output already includes its own header row.

**With it** (canonical pattern above), the header detection kicks in for the first row of the SQL output (which is the literal string `"image_url"` — the column header from `_raw_catalog`), substitutes `"Image"`, and the data rows fall through to the `IMAGE(url)` branch.

## Bracket-quote every column name AND alias in SQL()

alasql reserves many common words: `store`, `status`, `date`, `index`, `order`, `year`, `month`, `decision`, `action`, `currency`, `column`, `unique`, etc. Bare `SELECT store AS ...` throws `SyntaxError: Parse error ... got 'STORE'`.

**Rule:** wrap **every** column name AND **every alias** in square brackets in `SELECT`, `ORDER BY`, `WHERE`, `GROUP BY`, `HAVING`. Even ones that look safe. Uniform style, future-safe.

Bare-word aliases break even on simple-looking names. Tested empirically in the SellerSheet `SQL()` build:

| Alias form | Result |
|---|---|
| `AS Store, AS SKU, AS Spend, AS MarginNetPct` | `#ERROR!` (parser collides on bare `Store`) |
| `AS [Store], AS [SKU], AS [Spend], AS [Margin Net Pct]` | ✓ works |
| `AS [Margin Net %]` | ✓ works (brackets escape the `%`) |

JOIN column references too — `s.[store] = c.[store]` works; `s.store = c.store` may collide.

```javascript
=SQL("SELECT [store] AS [Store], [sku] AS [SKU], [asin] AS [ASIN], [product] AS [Product], 
              [decision] AS [Decision], [excess_qty] AS [Excess Qty] 
       FROM ? 
       ORDER BY [store], [decision], [sku]", 
      '_raw_inventory'!A1:P)
```

## JOIN syntax — verified working

Empirically tested in the SellerSheet `SQL()` build:

- ✅ `FROM ? AS data LEFT JOIN ? AS cat ON data.[store]=cat.[store] AND data.[sku]=cat.[sku]`
- ✅ `FROM ? data LEFT JOIN ? cat ON ...` (the `AS` keyword is optional)
- ✅ `FULL OUTER JOIN` with `COALESCE(l.[k], r.[k])` for sparse-vs-dense joins
- ✅ Multiple `?` placeholders bind to the multiple ranges passed in argument order
- ❌ Bare unquoted column refs in JOIN — may collide

When to JOIN at view time vs denormalize at write time:

- **Single source of truth.** If `_raw_*` already has the joined columns (added at write time), the visible tab is a thin projection — fewer moving parts.
- **Refresh model.** If both source `rpt_*` tables refresh on different cadences, JOIN at view time avoids stale-after-one-refresh-but-not-the-other states. Denormalize at write time freezes both sides to the write timestamp.

**Default:** denormalize into `_raw_*` for standard tabs (it's the simpler model). Reach for in-`SQL()` JOIN when you have a sparse-vs-dense relationship (FULL OUTER) or when the join key isn't stable enough for write-time denormalization.

## Open-range tables (no `:1000`)

All SQL spills use open-ended `A:Z` / `A2:A` ranges. Locked row counts like `A1:M77` silently truncate at multi-store growth.

| ❌ Don't | ✅ Do |
|---|---|
| `'_raw_inventory'!A1:R1000` | `'_raw_inventory'!A1:R` |
| `'_raw_cogs'!A2:R500` | `'_raw_cogs'!A2:R` |

alasql's `SQL()` ignores trailing blank rows, so open-range is safe.

## Same shared attributes belong in `_raw_catalog` too

Same JOIN logic for: `product` display name, `asin` (canonical), base category, brand. Any SKU master attribute identical across data tabs and changing rarely. Tab-specific metrics (units_t30, spend_30d, decision, etc.) stay in their respective `_raw_*` tabs.

## See also

- `reference/agent-insights.md` — `LIMIT 200` + overflow footer pattern that must match data and image SQL
- `reference/error-semantics.md` — diagnosing alasql parse errors
- `scripts/formula-templates.md` — copy-paste image MAP+JOIN + Profit-and-Cash SQL spill

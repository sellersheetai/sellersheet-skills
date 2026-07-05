# Image column at column A — canonical pattern

Any row whose primary identity is a SKU or ASIN must lead with an `=IMAGE()` thumbnail at column A. Column order: `A=Image, B=Store, C=SKU, D=ASIN, E=Product, ...`. Thumbnails let operators recognize products faster than reading codes.

## The canonical formula

```javascript
=MAP(SQL("SELECT [image_url] FROM ? ORDER BY [store], [sku] LIMIT 200", '_raw_inventory'!A1:N),
     LAMBDA(url, IF(url="image_url", "Image",
                    IF(url="", "", IMAGE(url)))))
```

How this works:
- `SQL()` returns a 2D array with the header row first (the literal string `"image_url"`) then URLs in the visible SQL's `ORDER BY`.
- `MAP` walks every element. The first element is the literal string `"image_url"` — the inner LAMBDA detects it and returns `"Image"` so the column header lands at the right row.
- Subsequent elements are URLs → `IMAGE(url)`.
- Empty URLs → `""` (blank cell), via the inner `IF(url="", "", ...)`.
- No `{"Image"; ...}` outer concatenation needed; no off-by-one.

## Image SQL must match data SQL — three constraints

The image MAP+SQL formula at column A and the data SQL at column B must share:

1. **Same `WHERE` clause** — same row inclusion criteria.
2. **Same `ORDER BY` clause** — same row order.
3. **Same `LIMIT N`** — same truncation point.

If any of the three differ, image rows desync from data rows.

| Visible tab | Data SQL `ORDER BY` | Image SQL `ORDER BY` (mirror) |
|---|---|---|
| Inventory and Restock | `[afn_warehouse_quantity] DESC, [sku] ASC` | `data.[afn_warehouse_quantity] DESC, data.[sku] ASC` |
| PPC Top SKUs | `[spend_30d] DESC` | `data.[spend_30d] DESC` |
| Listing Health | `[store], [status_change_date]` | `data.[store], data.[status_change_date]` |
| Profit and Cash | `[store], [sku]` | `data.[store], data.[sku]` |

## Joining `_raw_catalog` — single-source image URL

When `image_url` lives in a separate `_raw_catalog` tab (recommended — single source of truth across all visible tabs), the image SQL does a JOIN:

```javascript
=MAP(SQL("SELECT cat.[image_url]
          FROM ? AS data LEFT JOIN ? AS cat
            ON data.[store]=cat.[store] AND data.[sku]=cat.[sku]
          WHERE <same WHERE as data SQL>
          ORDER BY <same ORDER BY as data SQL>
          LIMIT 200",
         '_raw_<self>'!A1:<lastcol>, '_raw_catalog'!A1:E),
     LAMBDA(url, IF(url="image_url", "Image",
                    IF(url="", "", IMAGE(url)))))
```

Why JOIN beats duplicating `image_url` into every `_raw_*`:

- **Single refresh target.** Update `_raw_catalog` once; every visible Image column updates.
- **No drift.** When a previously-blank SKU's image becomes available, every tab gets the new thumbnail simultaneously.
- **Smaller per-tab `_raw_*` payloads.** PPC SKUs goes from ~12 cols to ~11; COGS goes from ~22 to ~21.
- **Sparse coverage handled gracefully.** Missing image (NULL in catalog) → blank cell via the LAMBDA guard. No `#REF!`.

## `_raw_catalog` schema

5 columns. One row per `(store, sku)` pair across the workbook's stores.

| Col | Header | Notes |
|---|---|---|
| A | `store` | canonical storename-countrycode |
| B | `sku` | canonical seller_sku |
| C | `asin` | |
| D | `image_url` | URL from `listing_images.main_image_url`; blank if not yet enriched |
| E | `product` | truncated display name, ~80 chars max |

Refresh cadence: daily. Image enrichment is a long-lived cache; the catalog inherits that stability.

## Common off-by-one bug to avoid

The earlier pattern `={"Image"; MAP(SQL(...), LAMBDA(...))}` puts `"Image"` in row N AND MAP also yields a value for the SQL header row → image cell 1 row below where it should be. The canonical pattern above (no outer `{"Image"; ...}`, header-detection inside LAMBDA) is the only stable form.

If you see image rows mis-aligned by one against SKU rows, this is the cause. Remove the outer `{"Image"; ...}` wrapper.

## `MAP` + `LAMBDA` is required for `IMAGE()`

`IMAGE()` does NOT iterate inside plain `ARRAYFORMULA`. Wrap with `IF(url="","",...)` so empty URLs render as blank cells, not `#VALUE!`.

```javascript
// ❌ broken — IMAGE doesn't iterate
=ARRAYFORMULA(IMAGE(_raw_inventory!D2:D))

// ✅ works
=MAP(SQL("SELECT [image_url] FROM ? ORDER BY ...", _raw_inventory!A1:N),
     LAMBDA(url, IF(url="", "", IMAGE(url))))
```

## First-open prompt

Sheets prompts **"Allow access to external images"** once on first open — expected, not an error. Until the user clicks Allow, IMAGE cells render blank. After Allow, they populate within seconds. Mention this in your README so operators don't panic on first open.

## Row height and column width

For SKU/ASIN tables with thumbnails:

- **Row height: leave the default (~21 px). Do NOT call `resize_sheet_rows`.** The thumbnail is a quick "which SKU is this" reminder, not a detail view — the default height is all it needs, and the only sanctioned custom row height anywhere is the ~34 px emerald banner.
- **Image column width: 50 px, fixed** (`resize_sheet_columns(..., start_col=0, end_col=1, width=50)`). **Never autofit column A** (it collapses/distorts an image column) **or the Product/description column** (autofit blows it out to the full title width — keep it fixed ~240 px). Autofit is optional on the short/structured columns only (codes, KPIs, status), and only **after** `set_sheet_basic_filter` — autofit doesn't reserve room for the filter arrow, so autofit-before-filter clips the headers. See `reference/brand-standards.md` → Column widths.

Thumbnails render fine in a 50 px column at the default row height — the preview is there to confirm "is this the right ASIN", not to zoom into; operators click out to the catalog for detail.

## See also

- `reference/sql-function.md` — bracket-quote rule, JOIN syntax, LIMIT defaults
- `reference/growable-tables.md` — the four rules, layout shape
- `reference/error-semantics.md` — `#NAME?` on IMAGE() is pending state until Allow Access
- `scripts/formula-templates.md` — copy-paste image MAP+JOIN

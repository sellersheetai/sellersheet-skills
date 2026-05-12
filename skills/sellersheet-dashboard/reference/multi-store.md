# Multi-store, multi-marketplace, locale tiles, BA gating

Three operating modes for the same dashboard pattern, plus the marketplace-specific tiles each store needs and the Brand Analytics gating rule.

## Three modes

### Single-store dashboard

Hardcode the store name in every query. Still write the `store` value into the `_raw_*` Store column on every row — it costs nothing now and protects you if the dashboard ever expands.

Example: myStore-US dashboard. Every `query_report_data` call uses `store="myStore-US"`. Every `_raw_*` row has `store="myStore-US"` in column A. `_status` has 1 row per `_raw_*` tab. HOME shows myStore-US-only tiles without per-store comparison columns.

### Multi-store dashboard (same workbook)

N queries — one per store — and **union the rows** into a single `_raw_*` tab, with the Store column distinguishing them. Visible SQL spill sorts by store first (`ORDER BY [store], [sku]`).

Example: myStore-US + myStore-CA dashboard. `_raw_inventory` has both stores' rows. `_status` has 2 rows per `_raw_*` (one per store). HOME has per-store tile bands. Currency-normalized USD-equivalent columns let operators compare side-by-side.

The Image, Decision/Status, and chip-based conditional formatting still works because Sheets evaluates row-by-row on cell value.

### Multi-marketplace store (one seller_id, many marketplaces — EU consolidations)

The store has a comma-separated `country_code` like `'UK,DE,FR,IT,ES,NL,PL,SE,BE,IE'`. Run one query per marketplace, passing the specific marketplace form (`'myStore-UK'`, `'myStore-DE'`, etc.), and union into `_raw_*`. The route auto-filters per table; each row's Store cell carries the marketplace, which is the level operators actually decide on.

`_status` gets one row per `_raw_* × marketplace` — so a 10-marketplace EU store generates 10 rows per `_raw_*` × however many raw tabs. Use per-store rollups with drill-down rather than 10 columns on HOME.

## Column order stays uniform

In all three modes the visible-tab column order is `A=Image, B=Store, C=SKU, D=ASIN, E=Product, ...`. Same shape regardless of single/multi scope. The Store column is the disambiguator at row scan time.

## Currency normalization

When two stores' revenue appear side-by-side (AE + AU, US + EU, etc.) the operator can't compare AED vs AUD directly. Add a synthetic comparable column — USD equivalent or RMB equivalent — using rates from `_config!fx_rates`.

Pattern on HOME:

```
Store     | Indicator       | Value      | USD eq | ...
myStore-US    | Revenue T30     | AED 8,376  | $2,280 | ...
myStore-CA    | Revenue T30     | AUD 5,084  | $3,284 | ...
```

Where USD eq column = `=Value / VLOOKUP(currency, cfg_fx, 2, FALSE) * cfg_fx_usd_rate`.

**Never display two different currencies in the same KPI column** without a normalized companion.

## Locale-required tiles by marketplace

The dashboard isn't complete without these for each store's marketplace:

| Marketplace | Required tiles |
|---|---|
| AE / SA / KW / BH / OM | Ramadan + Eid calendar (next-peak countdown), GCC `ship_to_country` split from `rpt_orders`, VAT settings link if invoice-defect > 0% |
| AU / NZ | LTSF aging buckets (181 / 271 / 365 d) from `rpt_fba_inventory_health`, GST registration threshold tracker (AUD 75k), Boxing Day / Click Frenzy / EOFY calendar |
| US / CA / MX / BR | Prime Day / Black Friday / Cyber Monday calendar, state-level demand (US) |
| UK / DE / FR / IT / ES / NL / PL / SE / BE / IE | Prime Day / Black Friday / Christmas calendar, VAT-OSS reconciliation row if EU operator |
| JP | Rakuten Super Sale / Amazon Tokimeki / Golden Week calendar, JCT registration tracker |

If the marketplace requires a tile and it's absent, the dashboard is not feature-complete. Surface a stub at minimum and put `NOT_YET_WIRED` on the value cell so operators know it's coming.

### MENA-specific anti-pattern

**Tax / invoice-defect surfacing**: VAT/GST defect rates on Account Health must call out the exact Seller Central setting that fixes them (e.g., UAE VAT defect → "enable Tax Settings → VAT Calculation Service"). Don't just report the rate. AE B2B-heavy stores get the highest leverage from this single VCS toggle.

### AU-specific anti-pattern

**LTSF aging**: Australia has a 181-day LTSF charge (not 271 like US/EU). Aging buckets must be 181 / 271 / 365 specifically; default US buckets miss the AU charge entirely.

## Multi-store HOME structure

For 2-3 stores, use a per-store row band:

```
Section: LAG — yesterday + last 7d
  myStore-US | Orders T7 | 9 | ... | USD eq |
  myStore-CA | Orders T7 | 10 | ... | USD eq |

Section: LEAD — forward risk
  myStore-US | Suppressed listings | 6 SKUs | ... |
  myStore-CA | Excess inventory | 13 SKUs | ... |
```

For 6+ stores (EU consolidation), use a **per-store rollup** with drill-down tab — one row per store, summary metrics only. HOME breaks above 5 stores.

## Brand Analytics gating

If `list_report_syncs(store='...')` shows BA reports disabled, the **Search & Share tab stays as a placeholder**:

- Note in README under "Tabs in this workbook": refresh `Weekly (BA gated)`, decision `Strategic — not yet wired for this store`.
- Don't build broken queries against empty tables.
- The tab title can read "Search & Share (BA-GATED)" so an operator knows it's intentionally inactive, not broken.

## Store identifier — canonical form

`storename-countrycode` always — `myStore-US`, `myStore-US`, `myStore-CA`, `myStore-UK`, `myStore-DE`. This is the form:

- GAS sidebar uses for store selection
- MCP tools accept as the `store=` argument
- `_raw_*` Store column carries on every row
- `_status` Store column carries

When the user asks "look at this row in Seller Central", the AI already has the store identifier — no re-resolution needed.

## See also

- `reference/freshness-system.md` — multi-store `_status` rows
- `reference/cogs-schema.md` — currency suffix `_aed` / `_aud` / `_usd` per marketplace
- `reference/grow.md` — adding a new store checklist
- `reference/lint-and-rules.md` — locale-required tiles enforcement

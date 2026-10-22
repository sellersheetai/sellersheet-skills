# `_raw_cogs` canonical 18-column schema

User-input table powering the Profit and Cash visible tab. Headers MUST match these names exactly — Profit and Cash's SQL spill queries them by bracket-quoted name, so any drift makes Margin and Profit columns render blank (or worse, the whole spill fails silently).

## Schema

| Col | Header | Type | Notes |
|---|---|---|---|
| A | `store` | text | `myStore-US` form |
| B | `sku` | text | merchant SKU |
| C | `asin` | text | Amazon ASIN |
| D | `image_url` | text | empty if catalog JOIN provides it |
| E | `product` | text | display name |
| **F** | **`selling_price_{ccy}`** | **yellow input** | e.g. `selling_price_aed` — list price in mkt currency |
| **G** | **`referral_fee_{ccy}`** | formula | `=F × cfg_referral_pct` |
| **H** | **`fba_fee_{ccy}`** | **yellow input** | per-unit FBA fulfillment fee in mkt currency |
| I | `total_fees_{ccy}` | formula | `=G + H` |
| **J** | **`product_cost_rmb`** | **yellow input** | factory cost in RMB (or origin currency) |
| **K** | **`weight_kg`** | **yellow input** | shipping weight kg |
| L | `shipping_rmb` | formula | `=K × cfg_ship_rmb_kg` |
| M | `total_cost_rmb` | formula | `=J + L` |
| N | `landed_{ccy}` | formula | `=M / VLOOKUP({ccy}, cfg_fx, 2, FALSE)` |
| O | `profit_{ccy}` | formula | `=F - I - N` |
| P | `margin_pct` | formula | `=O / F` |
| Q | `breakeven_{ccy}` | formula | `=N + I` |
| R | `suggested_{ccy}` | formula | `=Q × 1.6` (target ~37% gross margin) |

## Currency suffix rule

**`{ccy}` is the store's mkt currency suffix**: `aed`, `aud`, `usd`, `gbp`, `eur`. A multi-store workbook either:

(a) Uses one `_raw_cogs` per store with the appropriate suffix everywhere — e.g. `selling_price_aed`, `landed_aed` on myStore-US's tab.

(b) Uses a `mkt_currency` column F and renames F-R to neutral names — `selling_price`, `landed`, etc. — and the SQL VLOOKUPs FX based on the per-row mkt_currency cell.

**Pick one and stay consistent.** The Profit and Cash SQL must match. Switching mid-build forces rewriting both the schema and the consuming SQL.

For a US store sourcing from China:
- Mkt currency suffix: `_usd`
- Origin currency: RMB → `product_cost_rmb`, `weight_kg`, `shipping_rmb` columns stay as-is
- Pick column labels that name the currencies in the visible spill — e.g. `Cost (¥)`, `Profit ($)`.

## Yellow input columns

**Only F, H, J, K** get the user-input yellow fill `[1, 0.949, 0.8]`. These are the four numbers an operator types in per SKU; everything else auto-computes.

| Yellow column | What the operator enters |
|---|---|
| F `selling_price_{ccy}` | List price on Amazon (mkt currency) |
| H `fba_fee_{ccy}` | Per-unit FBA fee from Revenue Calculator |
| J `product_cost_rmb` | Factory cost per unit (origin currency) |
| K `weight_kg` | Shipping weight per unit |

Never apply yellow to formula columns (G, I, L, M, N, O, P, Q, R) — operator typing into a formula cell silently destroys the calculation. Apply cool-gray `[0.953, 0.961, 0.973]` to formula columns instead.

## Common breakages caught by audit

These have all happened in real builds — verify against them before declaring a COGS tab done.

| Breakage | What you'll see | Root cause | Fix |
|---|---|---|---|
| Column F mislabeled `AED→RMB` | Profit and Cash margin column empty after add-on loads | Builder put FX rate into F, used the label `AED→RMB` | Rename F1 to `selling_price_aed`, clear F2:F∞, prompt operator to fill in actual selling prices |
| Column G mislabeled `AED/RMB` | Referral fee column shows shipping data (6 RMB/kg) | Shipping rate bleed-through | Rename G1 to `referral_fee_aed` with formula `=F × cfg_referral_pct` |
| Yellow fills applied to formula columns | Operator types into N, silently breaks margin | Wrong fill applied during build | Reset N, O, P, Q, R fills to cool-gray; only F, H, J, K are yellow |
| FX rate hardcoded into formula instead of referencing `cfg_fx` | Margins go negative when FX shifts and operator can't tell why | Builder shortcut | Use `VLOOKUP(mkt_currency, cfg_fx, 2, FALSE)` so a single edit in `_config!B2` propagates |
| `cfg_ship_rmb_kg` hardcoded as 12 in formulas | Sea freight at 6 RMB/kg looks like air at 12 | Outdated example value | Reference named range, edit in `_config` only |

## Sentinel row when no COGS data

If the operator hasn't entered any COGS yet, the tab should self-document:

```
_raw_cogs!A2:R2 = ["myStore-US", "NO_COGS_ENTERED_YET", "operator fills yellow columns F, H, J, K", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
```

And `_status!J` for the `_raw_cogs` row contains `NO_COGS_ENTERED_YET` so the status badge goes RED-error and the row-2 freshness pill on Profit and Cash shows the gap.

## See also

- `reference/freshness-system.md` — `_status` integration (`refresh_cadence="manual"`, `expected_lag_hours=720`)
- `reference/multi-store.md` — currency suffix per marketplace
- `reference/provenance-colors.md` — yellow vs cool-gray application
- `scripts/formula-templates.md` — the FX VLOOKUP formula + Profit and Cash SQL spill

# `_config` tab — configuration values + named ranges

Configuration values (FX rates, shipping rates, referral fee defaults — anything the operator might tune) live on a dedicated `_config` tab. They do NOT colocate with `_raw_*` data tabs.

## Standard `_config` structure

```
_config tab:
  A1:C1     headers: Currency, RatePerRMB, AsOf
  A2:C5+    one row per currency (USD, GBP, EUR, AUD, AED, ...) with rate and as-of date
  E1:E2     shipping_rate_rmb_kg label + value
  G1:G2     referral_default_pct label + value
  I1:K1     headers: Threshold name, Value, Notes (operator-tunable thresholds)
  I2:K20    one row per threshold (e.g., WoC danger, margin floor)
```

Adapt the columns to the operator's actual needs — but keep the structure of "tunable inputs in one tab, formulas reference them via named ranges."

## Why a separate tab + named ranges (not inline)

If config sits inside `_raw_cogs` (or any data tab), inserting a new data row shifts the config cells and silently breaks every margin formula. A separate tab + named ranges is the safe pattern.

| ❌ Inline config | ✅ Separate `_config` tab |
|---|---|
| `=B5 / _raw_cogs!$V$1` | `=B5 / cfg_fx_rate` |
| Row insert in `_raw_cogs` breaks formulas | Row insert anywhere is safe |
| Reviewer must hunt for the FX rate cell | One place to look |

## Named ranges to define

After populating `_config`, define these named ranges via `add_sheet_named_range`:

| Named range | Points at | Used by |
|---|---|---|
| `cfg_fx` | `_config!A1:C5` (whole FX table — used in VLOOKUP) | every margin / landed-cost formula |
| `cfg_fx_asof` | `_config!C1:C5` (the AsOf column — used for staleness checks) | HOME "FX last refreshed" tile |
| `cfg_ship_rmb_kg` | `_config!E2` (single cell — shipping rate) | landed-cost formulas |
| `cfg_referral_pct` | `_config!G2` (single cell — referral fee %) | referral-fee formulas |
| `cfg_thresholds` | `_config!I1:K20` (table of operator-tunable thresholds) | dashboard chip logic |

Direct `_config!$B$2`-style references are **banned**. They break silently when a row is inserted in `_config`. Named ranges survive.

## FX rate freshness — `AsOf` column is mandatory

Every FX rate cell must have an `as_of` column. Surface "FX last refreshed" on the dashboard with conditional red if `max(as_of)` is older than 14 days:

```javascript
// HOME freshness tile
="FX last refreshed: " & TEXT(MAX(_config!C2:C), "yyyy-mm-dd")
  & IF((TODAY() - MAX(_config!C2:C)) > 14, " ⚠️ STALE (>14d)", " ✓ fresh")
```

Currency moves matter — a 3% AUD drop flips a 7% gross margin to negative. Static rates kill margins silently.

## Cell notes on rate cells

Add a cell note on each rate cell explaining the direction:

```
"Stored as 1 <Currency> = X RMB. Divide cost-in-RMB by this rate to get cost-in-marketplace-currency."
```

Currency-math direction is the #1 source of silent margin destruction. Document it where the rate lives.

## Drift comparison with GOOGLEFINANCE

Optional but useful — pull a live rate next to the stored rate so the operator can see when they're out of sync:

```javascript
// Live USD/CNY from GOOGLEFINANCE
=GOOGLEFINANCE("CURRENCY:USDCNY")
```

GOOGLEFINANCE is rate-limited and not real-time, but it's accurate enough for drift detection. Put the live cell next to your stored value with a delta:

| Currency | RatePerRMB (stored) | AsOf | Live (GOOGLEFINANCE) | Delta % |
|---|---|---|---|---|
| USD | 7.20 | 2026-05-12 | =1/GOOGLEFINANCE("CURRENCY:USDCNY") | =ABS(stored-live)/live |

## Threshold cells in `_config`

Operator-tunable thresholds (WoC danger zones, margin floors, ACoS targets) belong in `_config`, not buried in formulas:

```
_config!I1:K1   headers: Threshold name | Value | Notes
_config!I2:K2   WoC danger floor | 4 | weeks; restock advised below
_config!I3:K3   WoC excess ceiling | 20 | weeks; outlet candidates above
_config!I4:K4   ACoS target max | 0.30 | flag campaigns above
_config!I5:K5   Margin floor net | 0.20 | minimum acceptable net margin
```

Then formulas reference them:

```javascript
=IF(woc_cell < VLOOKUP("WoC danger floor", cfg_thresholds, 2, FALSE), "REORDER", "HOLD")
```

When the operator wants to tighten ACoS target from 30% to 25%, they edit one cell. The dashboard updates everywhere.

## Cell formats on `_config`

- **Rate cells** (numeric): format with appropriate decimal precision — `0.0000` for FX, `0` for shipping RMB/kg.
- **AsOf cells** (date): format `yyyy-mm-dd`.
- **Percent thresholds**: format `0.0%`.
- **Yellow background** on operator-editable cells per the financial-model convention — see `reference/brand-standards.md`.

## See also

- `reference/brand-standards.md` — yellow background for user-input cells
- `reference/formula-conventions.md` — using named ranges instead of cell-letter refs
- `scripts/formula-templates.md` — FX VLOOKUP patterns

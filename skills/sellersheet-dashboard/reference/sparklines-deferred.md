# Sparkline trend indicators (DEFERRED)

> **Status: deferred until reporting-server retention improves.** The patterns below are codified for future reference. **Do not implement on a new dashboard yet** — most snapshot tables (`rpt_fba_inventory_health`, `rpt_restock_recommendations`, `rpt_account_health`) currently retain only 2-5 days of history per store, which makes 14d/30d sparklines render as flat lines or stubbed values that mislead more than they help.

## Upstream data prerequisites for re-enabling sparklines

1. `rpt_fba_inventory_health` must retain ≥14 daily rows per (store, sku) — today it shows the alternating-day gap pattern caused by MYI's `cancel_means_empty=True` swallowing Amazon regen-cooldown cancellations as empty completions.
2. `rpt_account_health` must retain ≥30 daily rows per (store, marketplace) — today it's similarly sparse.
3. A `rpt_fba_woc_daily` materialized view (or equivalent) would be the right target — purpose-built for trend queries instead of relying on snapshot accumulation.
4. See investigation findings: MCP cron healthy + `consecutive_failures=0`, but data gaps real. Root cause is Amazon-side cancellation classification, not retention.

When the upstream side ships these, return to this file.

---

Sparklines turn a static "AHR: 258" into a 30-day shape that tells the operator whether the score is drifting or stable. They're cheap to add, hard to misread, and the dashboard's single biggest "morning-glance" upgrade — once the underlying data exists.

## When to add a sparkline

The bar is high. Every sparkline costs visual attention. Only add one when the **shape changes the operator's decision** in a way the static number doesn't.

| Add a sparkline for | Don't sparkline |
|---|---|
| AHR (slope matters more than current value) | Daily GMV (the number IS the headline) |
| WoC per SKU (trajectory predicts stockout 3 weeks out) | Storage fees (monthly cadence, sparse) |
| TACoS per store (drift signals ad efficiency loss) | Settlements (biweekly, volatile) |
| Per-campaign ACoS (one bad day vs real shift?) | Per-SKU ACoS (too noisy at SKU-day grain) |
| Net contribution % (catches fee creep + ad inefficiency in one shape) | FBA fees (step functions, not trends) |
| Return rate per SKU (spikes flag quality regressions) | |

Rule of thumb: if the shape doesn't change the decision vs the static number, don't draw it.

## Wide-format `_raw_*_daily` tab is the right data shape

For HOME-tile sparklines (one line per store, one cell on the dashboard):

```
_raw_ahr_daily:
  A      B            C
  date   myStore-US_ahr   myStore-CA_ahr
  d-29   258          200
  d-28   258          200
  ...    ...          ...
```

The sparkline cell: `=SPARKLINE(_raw_ahr_daily!B2:B31, {"charttype","line"; ...})` — trivial.

Long-format (`date, store, metric, value`) is more flexible but every sparkline cell needs a FILTER expression — unnecessary complexity for a fixed set of metrics.

## Per-row sparkline in a SQL-spilled visible table

The hard case: each SKU/campaign row has its own mini-trend, the visible table is a SQL spill, the trend data lives in a separate `_raw_*_daily` tab keyed by (store, sku) or (store, campaign_id).

```javascript
=IFERROR(SPARKLINE(
   INDEX(_raw_woc_daily!$C$2:$P$200,
         MATCH($B9&"|"&$C9, ARRAYFORMULA(_raw_woc_daily!$A$2:$A$200&"|"&_raw_woc_daily!$B$2:$B$200), 0),
         0),
   {"charttype","line"; "color1","#10B981"}),
"")
```

Key tricks:
- `INDEX(range, row, 0)` returns the whole row as a 1D array — exactly what `SPARKLINE` wants.
- Composite key `MATCH($B9&"|"&$C9, A&"|"&B, 0)` matches (store, sku) tuples.
- `IFERROR` wraps the whole thing so SKUs without trend data render blank, not `#N/A`.
- `$B9` / `$C9` reference the visible row's Store / SKU columns (positions vary per tab).

Bulk-write the column with one `write_sheet` call — USER_ENTERED parses every `=SPARKLINE(...)` string as a live formula.

## SPARKLINE() option recipes

```javascript
// 30d line chart, emerald
{"charttype","line"; "color1","#10B981"; "linewidth",2}

// AHR-style with implied threshold (use ymin/ymax to fix the axis)
{"charttype","line"; "color1","#10B981"; "linewidth",2; "ymin",0; "ymax",1000}

// Per-day pass/fail columns (TACoS, ACoS, daily target metrics)
{"charttype","column"; "color1","#10B981"; "negcolor","#EE7370"; "axis",TRUE; "axiscolor","#888888"}

// Win/loss for binary daily state (buy box won/lost, listing active/inactive)
{"charttype","winloss"; "color1","#10B981"; "negcolor","#EE7370"}
```

SPARKLINE has no native threshold-line option. Workaround: a sidecar text cell "Floor: 200" next to AHR sparklines, or color-driven conditional formatting on the cell when `MIN(range) < threshold`.

## Stub strategy when daily history is sparse

`rpt_fba_inventory_health` and `rpt_restock_recommendations` retain only 2-5 days of snapshot history on most stores. Two paths:

1. **Stub (honest):** populate the `_raw_*_daily` tab with the current value repeated N times. Sparkline renders as a flat horizontal line. Flag the limitation in README explicitly: "WoC sparklines pending — needs snapshot retention extended to 14d on the warehouse side."
2. **Derive (more work):** reconstruct an approximate history from related deltas (e.g., compute implied WoC backwards from `units_sold_t1` running over `available_qty_today` + sold-since values).

Default to (1) for prototypes — operators can see the column exists and the metric framework works; the data layer is the next refresh target. Never silently hide a column waiting for data — always show the stub with the README annotation.

## Region-aware sparkline windows

For seasonality-driven marketplaces, the sparkline window should extend during peak windows:

- AE: 60d from Feb 1 covers Ramadan + Eid lead-in.
- AU: 60d from Oct 15 covers Click Frenzy → Boxing Day → mid-Jan.
- Default 14d/30d outside those windows.

Store the per-(store, metric) override in `_config`:

```
_config!H1   "Sparkline window overrides"
_config!I1:K1  store, metric, window_days
_config!I2:K2  myStore-US, all, 60 (Feb 1 → May 31)
_config!I3:K3  myStore-CA, all, 60 (Oct 15 → Jan 15)
```

Sparkline range becomes `OFFSET(_raw_*_daily!B$2, -<window_days>, 0, <window_days>, 1)` instead of a fixed `B2:B31`. Trades simplicity for marketplace-correct trend windows.

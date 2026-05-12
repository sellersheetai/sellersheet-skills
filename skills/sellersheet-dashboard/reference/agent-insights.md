# Agent insights loop

Two tabs (`_agent_notes`, `_agent_log`) plus a FILTER pattern give the dashboard a place for AI commentary that's inline with operator actions, auditable, and self-pruning when conditions change.

## `_agent_notes` — inline insights, never inside `_raw_*`

Agent analysis lives in a dedicated `_agent_notes` tab and surfaces on visible tabs via `FILTER`. **Never** inside `_raw_*` tabs (refresh wipes them). **Never** on a separate digest tab (operators won't context-switch to read it).

### Schema

```
A=row_id (e.g. "N001", "F001" for fires)
B=timestamp_utc
C=agent_id (e.g. "claude-opus-4-7")
D=store
E=scope_tab (visible tab name: "HOME" / "Inventory and Restock" / etc — matched by the FILTER on each tab)
F=scope_key (sku | asin | campaign_id | "global" | "fire-1" / "fire-2" / "fire-3" | cluster name)
G=severity (info | amber | red)
H=insight (one sentence — the "what")
I=recommended_action (one sentence — the "do")
J=supporting_cells (A1 refs comma-separated)
K=confidence (0-1)
L=superseded_by (row_id, blank if current — non-blank rows are hidden by the FILTER)
```

### Header row format

Apply emerald `[0.063, 0.725, 0.506]` bg + white bold + freeze row 1.

## `_agent_log` — append-only delta audit

Sister tab to `_agent_notes`. Append a row **only when a value changes**, not every re-evaluation. Three weeks from now the operator asks "why did SCALE flip to HOLD on Queen?" — this is where they read.

### Schema

```
A=timestamp_utc
B=agent_id
C=tab
D=cell (A1 ref)
E=prior_value
F=new_value
G=rationale (one sentence)
H=supporting_cells
```

No-change passes don't write. Otherwise the log balloons and becomes unreadable.

## Inline FILTER on each visible tab

On each visible tab (not on HOME — HOME gets the TOP 3 FIRES pattern below), add an AGENT INSIGHTS section. **Anchor row depends on the spill size** (see overflow guard below).

```
Row N    Section band: "AGENT INSIGHTS — <tab name>"  (emerald, white bold)
Row N+1  Column header:  Date | Store | Severity | Insight | Recommended action | Supporting cells  (navy, white bold)
Row N+2  FILTER spill:
         =IFERROR(FILTER({_agent_notes!B2:B100, _agent_notes!D2:D100, _agent_notes!G2:G100, 
                          _agent_notes!H2:H100, _agent_notes!I2:I100, _agent_notes!J2:J100},
                         _agent_notes!E2:E100="<tab name>",
                         _agent_notes!L2:L100=""),
                  "No active insights for this tab.")
```

Format the date column (A) with `DATE_TIME` number format (otherwise it shows as serial like `46154.25`).

## AGENT INSIGHTS row anchor — the overflow guard

The SQL spill on a visible tab grows downward indefinitely. If AGENT INSIGHTS sits at row 60 and the spill needs row 60, Sheets aborts with:

```
#REF! "Array result was not expanded because it would overwrite data in A60"
```

The whole tab then shows `#REF!` instead of data — total breakage from one collision. **This is a real bug, not a pending state.** See `reference/error-semantics.md`.

### Overflow-guard sizing rule (mandatory)

1. **Estimate `max_expected_rows`** for the spill — for catalogs use the `_raw_*` row count plus 20% headroom. Empirical anchors:
   - myStore-US inventory had **203 rows after `WHERE [afn_warehouse_quantity] > 0` filtering** → broke at row 150.
   - A smaller-catalog inventory spill of ~86 rows fits comfortably at row 150.
   - Catalogs of 1000+ SKUs are common — plan for it.
2. **AGENT INSIGHTS anchor must be `≥ spill_start_row + max_expected_rows + 10` buffer rows.**
3. **Default anchors:**
   - **Row 150** — bounded tabs whose spill is consistently <130 rows: HOME, PPC Command, Account Health, Returns and Refunds.
   - **Row 400** — catalog-scaling tabs: Inventory and Restock, Listing Health, Profit and Cash.
4. **If you cannot bound the spill, cap the SQL with `LIMIT 200`** and add an overflow footer (next section).

Never trust "150 is fine because the smaller test build didn't break" — small catalogs (under 100 rows) fit at row 150; large ones break it. The convention only works inside its row budget.

## SQL `LIMIT 200` + overflow footer

When a spill could exceed 200 rows in production, cap it and surface the truncation:

```javascript
=SQL("SELECT [store] AS [Store], [sku] AS [SKU], ...
      FROM ? 
      WHERE [afn_warehouse_quantity] > 0 
      ORDER BY [afn_warehouse_quantity] DESC, [sku] ASC 
      LIMIT 200", 
     '_raw_inventory'!A1:R)
```

Then write an overflow footer 1 row below the maximum spill extent (anchor row 14 + 200 data rows + 1 buffer = row 215):

```javascript
="Showing first 200 of " 
  & COUNTIFS('_raw_inventory'!A:A, "myStore-US", '_raw_inventory'!M:M, ">0") 
  & " active SKUs (LIMIT 200 guard). See _raw_inventory tab for the full catalog list."
```

Format the footer with soft yellow `[1, 0.949, 0.8]` bg + italic.

The image MAP+SQL formula at A14 must use the **same `LIMIT 200`** so image and data columns stay aligned row-for-row.

## TODAY'S TOP 3 FIRES on HOME

Insert 6 rows at HOME!A4 (after the title row 1 and freshness pill row 2, with row 3 as spacer) to host the ranked action list before LAG section.

```
A4: "TODAY'S TOP 3 FIRES — ranked by urgency × recoverable revenue"  (red banner [0.815, 0.220, 0.220])
A5: Rank | Store | Insight | Action | Confidence | Supporting cells  (navy header)
A6: =IFERROR(FILTER({_agent_notes!F2:F100, _agent_notes!D2:D100, _agent_notes!H2:H100, 
                     _agent_notes!I2:I100, _agent_notes!K2:K100, _agent_notes!J2:J100},
                    REGEXMATCH(_agent_notes!F2:F100, "^fire-"),
                    _agent_notes!L2:L100=""), 
              "no fires — enjoy the morning")
A6:F8 background: agent cream [0.996, 0.973, 0.890]
```

Agent populates `_agent_notes` rows with `scope_key = "fire-1"`, `"fire-2"`, `"fire-3"` daily. The regex `^fire-` matches all three and the order in `_agent_notes` determines the rank.

## Threshold-triggered self-pruning blocks

Agent insight cells that **only matter while a threshold is breached** should self-prune. Wrap in `IF`:

```javascript
=IF(AccountHealth!B11 > 0.05, "AE Invoice Defect 97.92% — activate VCS, set up auto-invoicing", "")
```

When defect rate drops below 5%, the callout disappears automatically — the dashboard self-cleans instead of growing infinite stale callouts. The cell stays present (so the layout doesn't shift), but renders empty.

Sticky variant for "last-known-good" semantics:

```javascript
=IF(<threshold met>, "<callout>", <previous value cell>)
```

## Agent commentary cadence

Different cells need different agent-touch cadences. The Workflow Architect's freshness color encodes the *age* of an agent note; the cadence column below sets the budget. Operator-perspective budgets:

| Cell / section | Cadence | Trigger to refresh sooner |
|---|---|---|
| HOME · Net-after-ads narrative | Daily | Any SKU crosses 0% margin boundary OR new attributed purchase shifts unit math |
| HOME · Concentration risk | Weekly | Top-SKU % shifts >5pp |
| HOME · Suppressed cluster narrative | Per-refresh | New suppression OR count drops to 0 (self-prune block) |
| HOME · Next demand event | Weekly | T-90 / T-60 / T-30 to peak — escalates |
| Inventory · DEAD-catalog rollup | Weekly | DEAD count moves ±5 SKUs |
| Inventory · Removal sequence top-3 | Weekly | New SKU enters EXCESS or LTSF aging crosses 181d |
| PPC · per-SKU SCALE/HOLD/PAUSE override | Daily (launch) / Weekly (mature) | ≥10 incremental clicks since last touch |
| PPC · scale-winner search terms | Weekly | New term crosses orders ≥1 AND ACoS <25% |
| Account Health · Invoice Defect remediation | Threshold-triggered | Defect rate moves >5pp |
| Listing Health · suppressed-cluster narrative | Per-refresh | New cluster forms |
| Profit and Cash · negative-margin callout | Daily | Any SKU crosses 0% margin |
| Profit and Cash · COGS coverage banner | Weekly | Coverage % moves ≥10pp |

**Threshold-triggered is the highest-leverage cadence** — don't waste agent attention on cells that haven't changed.

## See also

- `reference/freshness-system.md` — `_status` integration with `_agent_notes.scope_tab` for the `agent_actions_count` column
- `reference/provenance-colors.md` — the agent-cream fill that distinguishes these cells
- `reference/error-semantics.md` — `#REF!` diagnostics when the FILTER section collides with a spill
- `scripts/formula-templates.md` — copy-paste FILTER + TOP 3 FIRES + overflow footer templates

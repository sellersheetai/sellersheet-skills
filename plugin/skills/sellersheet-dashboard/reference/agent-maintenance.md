# Agent maintenance workflow

After a dashboard exists, the agent maintains it. This is the loop: refresh data, update freshness markers, regenerate insights, log changes. The dashboard self-explains because every cell carries provenance and freshness — the agent's job is to keep that truth current.

## The four maintenance modes

### 1. Daily refresh (scheduled)

Trigger: scheduled cron, typically 04:00–08:00 UTC depending on store timezone.

For each `_raw_*` tab with a non-manual `refresh_cadence`:

1. **Read `_status` row** to find `last_pulled_utc`, `expected_lag_hours`, and `pull_run_id`.
2. **Call `query_report_data(rpt_table, store, ...)`** for the source rpt_* table(s).
3. **Clear `_raw_<tab>!A2:Z`** (preserve header row).
4. **`write_sheet(_raw_<tab>!A2, rows)`** with the fresh data. Set `store` value on every row at write time.
5. **Update `_status` row**:
   - `F: last_pulled_utc` = real datetime when the data pull completed (or `dataEndTime` from the SP-API response).
   - `G: source_data_through` = the data window end.
   - `J: last_error` = empty if successful; otherwise the error code (`NOT_YET_SYNCED`, `RATE_LIMITED`, etc.).
   - `K: pull_run_id` = new trace id for this run.
6. **Update cell note on `_status!F<row>`** with the JSON: `{"run_id":"...","rows_in":N,"rows_skipped":M,"duration_s":X}`.
7. **Append a row to `_agent_log`**: `timestamp_utc, agent_id, "_status", "F<row>", prior_last_pulled, new_last_pulled, "scheduled refresh", "_raw_<tab>"`.

The visible tab's SQL spills automatically pick up the new rows. The freshness pill on row 2 automatically updates because it reads from `_status`.

### 2. Threshold-triggered alert (event-driven)

Trigger: any `_status.status` value flips from GREEN-fresh / AMBER-aging to RED-stale or RED-error.

1. **Detect the flip** via a `_status` scan: `FILTER(_status!A:I, _status!I:I = "RED-stale")` or `... = "RED-error"`.
2. **Append a row to `_agent_log`** documenting the state change.
3. **Optionally write an `_agent_notes` row** with severity=red if the operator should know. Use `scope_tab = "HOME"` and `scope_key = "fire-N"` only when this rises to a top-3 fire; otherwise scope to the relevant visible tab.
4. **Surface to operator** via notification channel (out of scope for this skill — but the dashboard row-2 pill will already show RED on next open).

### 3. Insight refresh (daily, after data refresh completes)

Trigger: after step 1 (daily refresh) finishes for all `_raw_*` tabs.

1. **Read every visible tab's underlying `_raw_*` data** to detect changes vs the prior day.
2. **For each existing active row in `_agent_notes`** (`L: superseded_by = ""`):
   - Re-evaluate the underlying condition. Did the threshold cross? Did the cluster resolve? Did the supporting numbers change materially (>10%)?
   - If condition no longer applies → mark `L: superseded_by = <new row_id>` (or simply set it to a sentinel like `"resolved"` if no replacement). The FILTER on visible tabs drops the row automatically.
   - If condition still applies but numbers changed → write a new `_agent_notes` row with the updated insight, and set the OLD row's `superseded_by` to the new `row_id`.
3. **Generate today's TOP 3 FIRES**:
   - Rank all active insights by `(severity_weight × recoverable_revenue_estimate × urgency)`.
   - Top 3 get `scope_key = "fire-1"`, `"fire-2"`, `"fire-3"` and `scope_tab = "HOME"`.
   - If there are no real fires, do NOT manufacture them — the HOME spill shows "no fires — enjoy the morning" automatically via the `IFERROR` fallback.
4. **Append a row to `_agent_log` for each insight write/supersede**: prior_value, new_value, rationale.

### 4. On-demand update (operator request)

Trigger: operator asks "add an insight about X" or "the dashboard says Y but I just fixed Z, refresh it".

1. **Confirm the scope** with the operator — which tab, which scope_key, which severity.
2. **Write the insight row to `_agent_notes`** with current timestamp.
3. **Supersede any conflicting prior rows** by setting their `superseded_by` to the new row_id.
4. **Append to `_agent_log`** with rationale "operator request: <verbatim quote>".

## Supersession rules

The `_agent_notes.L: superseded_by` column is what makes the AGENT INSIGHTS sections self-prune. Without supersession, the FILTER would keep showing every insight ever written.

**Supersede when:**
- The underlying threshold is no longer breached (e.g., Invoice Defect Rate drops below 5%).
- The recommended action has been taken AND the operator marked it done (out-of-band; agent assumes done if the threshold also resolved).
- A newer insight on the same `scope_key` carries more current information.
- The insight scope is no longer relevant (e.g., a SKU was discontinued).

**Do NOT supersede when:**
- The data refreshed but the situation didn't change. The insight is still current.
- The insight is informational (severity=info) and time-bound (e.g., "Ramadan T-90 days"). Let it auto-resolve when the date passes — use a threshold-triggered IF wrap on the visible cell instead.

The `superseded_by` value can be a `row_id` (preferred — points to the replacement) or a sentinel string like `"resolved"` / `"discontinued"` / `"operator_dismissed"` (when there's no replacement).

## `_agent_log` append-only rules

Every state change writes one row. Three append patterns:

| Trigger | log row |
|---|---|
| Scheduled refresh completes | `tab=_status, cell=F<n>, prior=<old ts>, new=<new ts>, rationale="scheduled refresh <rpt_table>"` |
| Insight written or superseded | `tab=_agent_notes, cell=A<n>, prior=<old row_id or empty>, new=<new row_id>, rationale=<one sentence>` |
| Cell-level value change on visible tab | `tab=<visible>, cell=<a1>, prior=<old>, new=<new>, rationale=<why>` |

**Don't log no-op passes.** If the agent re-evaluated and nothing changed, no row goes to the log. The log is for *deltas*, not for *evaluations*.

The log fills quickly under daily refresh — that's expected. Archive at quarter boundaries (move rows > 90 days to a `_agent_log_archive` tab to keep the active log scannable).

## Conflict resolution

When two agents (or two passes of the same agent) write conflicting insights:

1. **Latest write wins.** The newer row's timestamp is authoritative.
2. **Supersede the older row** by setting its `L: superseded_by` to the newer row's id.
3. **Log both** in `_agent_log` with rationale explaining which agent / pass produced the winning insight.

If two insights are genuinely concurrent (same timestamp), use `row_id` lexicographic order as the tiebreaker. The lower row_id wins.

## What the agent does NOT do during maintenance

- **Does NOT change visible tab layouts.** The dashboard structure (tab list, section bands, column orders) is operator-stable. Layout changes are explicit user requests, not maintenance.
- **Does NOT rewrite the `_status` schema.** New `_raw_*` tabs may add rows; the schema is immutable.
- **Does NOT delete `_agent_notes` rows.** Supersede instead (set `L: superseded_by`). Deletion breaks the audit trail.
- **Does NOT delete `_agent_log` rows.** Archive only.
- **Does NOT modify `_config` named ranges.** Operator-only.
- **Does NOT touch user-input yellow cells** in `_raw_cogs`. Operator-only.

## Scheduling — recommended cron pattern

```
00:30 UTC   _raw_account_health refresh (Amazon snapshots at ~00:00 UTC)
03:00 UTC   _raw_ppc, _raw_ppc_attribution, _raw_ppc_search_terms, _raw_ppc_skus
04:00 UTC   _raw_listings, _raw_catalog
04:30 UTC   _raw_returns
05:00 UTC   _raw_finance (after settlement events post)
06:00 UTC   Insight refresh — re-evaluate all _agent_notes, regenerate TOP 3 FIRES
06:30 UTC   `_raw_inventory` (high freshness cadence; also at 12, 18, 00 UTC)
*/15 *      Status sweep — scan _status for newly RED-stale rows; alert if any
```

Adjust to operator timezone — sellers like the dashboard fresh by 08:00 local.

## Operator-visible side effects

After a maintenance pass:

- **Row-2 freshness pills** flip from RED-stale → GREEN-fresh as data lands.
- **TOP 3 FIRES on HOME** may reorder, drop a resolved fire, or surface a new one.
- **AGENT INSIGHTS sections** on each tab gain new rows or lose superseded ones.
- **`_agent_log`** grows by 1-N rows per maintenance pass.
- **`_status.row_count`** updates for each refreshed `_raw_*`.

Operator opens the dashboard at their morning hour and sees:
- Live freshness pills showing GREEN.
- A clean list of today's actionable fires.
- Per-tab AGENT INSIGHTS reflecting current state, not last week's.

That's the contract.

## See also

- `reference/freshness-system.md` — `_status` schema, last_pulled_utc rules
- `reference/agent-insights.md` — `_agent_notes` schema, FILTER pattern, TOP 3 FIRES
- `reference/error-semantics.md` — diagnosing what happened when a refresh fails
- `scripts/post-build-checklist.md` — verification after a maintenance pass

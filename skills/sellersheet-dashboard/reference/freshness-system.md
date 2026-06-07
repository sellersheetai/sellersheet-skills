# Freshness system

Defines how the dashboard knows what's fresh, what's stale, and what's broken — and how every visible tab surfaces that to the operator.

## `_status` tab — canonical freshness source

Every workbook has a `_status` tab. **One row per `_raw_*` × store** (so single-store dashboards have 1 row per raw tab, two-store dashboards have 2 rows per raw tab, except for `_raw_catalog` which is `store="ALL"` because it's a master).

### Schema

| Col | Field | Source |
|---|---|---|
| A | `raw_tab` | static, e.g. `_raw_inventory` |
| B | `store` | `myStore-US` / `myStore-US` / `myStore-CA` / `ALL` for master tables |
| C | `source_rpt_table` | comma-separated rpt_* names |
| D | `refresh_cadence` | `6h` / `daily` / `daily 03 UTC` / `manual` |
| E | `expected_lag_hours` | decision-tolerable staleness (see budgets table below) |
| F | `last_pulled_utc` | **REAL ISO timestamp** written at pull time — see "last_pulled_utc must be real" |
| G | `source_data_through` | data window end from SP-API response |
| H | `row_count` | `=COUNTIF('_raw_xxx'!A:A, B{n})` formula |
| I | `status` | formula: GREEN-fresh / AMBER-aging / RED-stale / RED-error |
| J | `last_error` | text — non-empty triggers RED-error |
| K | `pull_run_id` | trace id for `_agent_log` joins |
| L | `agent_actions_count` | `COUNTIFS` against `_agent_notes` |

### Status formula (per row)

```
=IF(J{n}<>"","RED-error",
  IF((NOW()-F{n})*24>E{n}*2,"RED-stale",
    IF((NOW()-F{n})*24>E{n},"AMBER-aging","GREEN-fresh")))
```

`NOW()` is volatile by design — freshness must recompute on every open. Apply conditional formatting on column I so the badge cell goes green/amber/red automatically. Use `CUSTOM_FORMULA` condition `=$I2="GREEN-fresh"` etc., or `TEXT_STARTS_WITH` if your MCP supports it.

### SQL() incompatibility with NOW() — IMPORTANT

The `SQL()` add-on function **refuses to read any range that touches a cell containing `NOW()`, `RAND()`, `RANDARRAY()`, or `RANDBETWEEN()`**. This means `=SQL("SELECT ... FROM ?", '_status'!A1:L)` ERRORS with:

```
"This function is not allowed to reference a cell with NOW(), RAND(), RANDARRAY(), or RANDBETWEEN()"
```

Because column I (`status`) contains `NOW()` in its formula.

**Consequences for consumers of `_status`:**

- **README live freshness table** — must NOT use `SQL()` to read `_status`. Use direct array references instead:
  - Per-column `ARRAYFORMULA`: write `=ARRAYFORMULA(_status!A2:A14)` per column on adjacent cells. This is the tested working pattern.
  - Or array literal: `={_status!A2:E14, _status!I2:I14}` (works on small ranges).
- **Visible-tab freshness pills** — `INDEX/MATCH` on `_status!I:I` works fine (cell-level access, not full-range SQL ingestion).
- If you genuinely need SQL() over `_status`, restrict the range to columns A:H (skip status formula): `'_status'!A1:H`.

## `last_pulled_utc` must be real, never faked

The freshness system breaks the moment column F lies. Strict rules:

✅ **DO:**
- Write a real datetime when the data pull completes: `"2026-05-12 07:00:00"` as a USER_ENTERED value (Sheets parses to native datetime).
- Write the SP-API `dataEndTime` if returned in the response payload.

❌ **NEVER:**
- `=NOW()` — recomputes on every open; every cell shows the current moment; every status reads GREEN-fresh; system is broken.
- `=DATEVALUE("2026-05-12")+TIME(7,0,0)` — looks like a formula but is a frozen literal. Defeats the entire freshness system while pretending to be live.
- A far-future date to "make it always GREEN" — operator will trust stale data into the ground.

If the dashboard is a demo snapshot, the README's row-2 subtitle should say so explicitly ("Snapshot built 2026-05-12 — not live") instead of dressing static data as live.

## Row-2 freshness pill on every visible tab

Replace any hardcoded `Refreshed YYYY-MM-DD` string with a live `TEXTJOIN` formula that resolves from `_status`. Pattern:

```javascript
=TEXTJOIN(" · ", TRUE,
  "<tab purpose phrase>",
  "Inventory " & IFERROR(INDEX(_status!I:I, MATCH("_raw_inventory", _status!A:A, 0)), "?"),
  "Catalog "   & IFERROR(INDEX(_status!I:I, MATCH("_raw_catalog",   _status!A:A, 0)), "?"),
  "oldest "    & TEXT(MINIFS(_status!F:F, _status!A:A, "_raw_inventory"), "yyyy-mm-dd hh:mm") & " UTC",
  "budget "    & INDEX(_status!E:E, MATCH("_raw_inventory", _status!A:A, 0)) & "h")
```

Each visible tab references the raw tabs its content depends on. The pill is the operator's read on "is what I'm about to act on still trustworthy?"

For multi-store rows in `_status`, use `MATCH(1, (_status!A:A="_raw_X")*(_status!B:B="<store>"), 0)` array-match syntax instead of single-criterion MATCH.

## Per-tab freshness budgets (decision-tolerable staleness)

| Raw tab | `expected_lag_hours` | Why |
|---|---|---|
| `_raw_inventory` | **2** | Restock decisions die on stale data |
| `_raw_listings` | **4** | Image-fix verification needs same-day signal |
| `_raw_account_health` | **24** | Amazon's own daily snapshot |
| `_raw_ppc` | **24** (4 launch-phase) | Bid moves; tighten during launch |
| `_raw_ppc_attribution` | **24** | Powers Profit and Cash net margin |
| `_raw_ppc_search_terms` | **48** | Negative-kw decisions need ≥7d evidence anyway |
| `_raw_ppc_skus` | **24** | — |
| `_raw_cogs` | **720** (30d) | Human input; surface per-row last_edited_at |
| `_raw_catalog` | **24** | Thumbnail cache; never blocks a decision |
| `_raw_returns` | **24** | Top-leverage missing tab — masks margin lies |
| `_raw_buybox` | **6** | Hijacker windows; AE marketplace is exposed |
| `_raw_finance` | **24** | Cash on hand, not P&L |

These are decision budgets — operators acting on data older than `2× budget` are at risk. The status formula encodes the 1× / 2× thresholds.

## Scaffold tabs must carry an in-cell sentinel row

When a `_raw_*` tab is scaffolded (schema defined but data not yet synced), the tab itself MUST show why. The `_status.last_error` marker is the canonical signal, but an operator who clicks directly into the raw tab won't see `_status`. Put a sentinel row at A2:

```
_raw_buybox!A2:H2 = ["myStore-US", "NOT_YET_SYNCED", "rpt_competitive_pricing not yet wired — see _status row", "", "", "", "", ""]
_raw_finance!A2:I2 = ["myStore-US", "NOT_YET_AGGREGATED", "rpt_financial_event_groups not yet aggregated", "", "", "", "", "", ""]
_raw_cogs!A2:R2   = ["myStore-US", "NO_COGS_ENTERED_YET", "operator fills yellow columns F, H, J, K", ...]
```

The sentinel uses column B (or wherever `store` isn't) to carry the marker text. This way:
- An operator who lands on the raw tab sees the gap immediately.
- The `_status.row_count` formula still works (sentinel counts as 1 row of "data") — adjust with `-1` if you want the count to exclude sentinels.
- The visible-tab SQL spill includes the sentinel — wrap with `WHERE [store] = '<store>' AND [<col>] <> 'NOT_YET_SYNCED'` to skip it on visible tabs.

## See also

- `scripts/seed-status-rows.md` — template `_status` rows for the 12 standard `_raw_*` tabs
- `scripts/formula-templates.md` — the row-2 pill, status formula, README spill formulas
- `reference/error-semantics.md` — what to do when `_status` shows `#ERROR!` (the SQL/NOW collision)

# Budget Rules & Budget Tools — deep reference

Read this BEFORE composing any `ads_budget_rules` payload or proposing a budget
change. It covers what the tool docstrings cannot: cross-product asymmetries,
the rule status lifecycle, live-verified behaviors that differ from Amazon's
published spec, decision guardrails, and the standing sheet artifacts that make
budget runs repeatable. Examples use demo refs (`MYSTORE-AE`); substitute the
operator's real store ref.

---

## 1. Three budget levers — pick the right one first

| Lever | Tool | Semantics | Use when |
|---|---|---|---|
| **Base daily budget** | `ads_sp/sb/sd_campaigns` action=`update` | Permanent until changed again | The constraint is permanent (a capped winner) |
| **Budget rule** | `ads_budget_rules` | Temporary **% increase only**, auto-reverts outside its window/condition | The raise is temporary or conditional (event, peak days, metric-gated) |
| **Portfolio cap** | `ads_sp_portfolios` | A **ceiling** over member campaigns (often monthly/date-range) | Enforcing a spend envelope — it never raises anything |

Decision boundary (memorize):

> **Fix bids and negatives when efficiency is wrong. Edit the base budget when
> the constraint is permanent. Add a rule only when the raise is temporary,
> conditional, and you want it to revert itself — then read its status back,
> because Amazon returns 200/207-Ok either way.**

The 2×2 that routes every "should I raise?" question (evaluate on trailing-7d
data with adequate volume — see §9 floors):

| | ACOS ≤ target | ACOS > target |
|---|---|---|
| **EOD usage ≥95%** | **BUDGET** — raise base (stepwise), or a rule if temporary/conditional | **BIDS + NEGATIVES** — never raise; the cap is limiting the loss |
| **EOD usage <85%** | **BIDS up / expand targeting** — budget isn't binding | Neither — targeting/creative/listing problem |

### Pre-raise preflight (all must pass before proposing ANY increase)

1. **Actually capped?** usage ≥95% on ≥3 of the last 7 days. No → bids. Stop.
2. **Efficient?** trailing-7d ACOS ≤ 0.85 × target on adequate volume. No → negatives/bids. Stop.
3. **In stock?** ≥21 days of cover for the advertised SKUs (check inventory tools). No → don't fund a stockout. Stop.
4. **Portfolio headroom?** The campaign's portfolio is not on track to exhaust its cap. A campaign raise under a bound portfolio is a no-op.
5. **Rule stack sane?** `list_for_campaign` first — see §7.

A campaign that is hot AND unprofitable is a **bid problem** (Recipe C), not a
budget problem. `ads_*_budget_recommendations` models top-of-funnel missed
opportunity — it knows nothing about margin or ACOS targets; treat it as a
sizing sanity-check, never as the decision.

---

## 2. Payload shapes — create vs update are NOT symmetric

**Create** (`operation=create`, body = list of 1–25 **flat** rule details):

```json
[{
  "name": "BR_AE_SCH_DTRANGE_P20_20261201-20261215",
  "ruleType": "SCHEDULE",
  "duration": {"dateRangeTypeRuleDuration": {"startDate": "20261201", "endDate": "20261215"}},
  "recurrence": {"type": "DAILY"},
  "budgetIncreaseBy": {"type": "PERCENT", "value": 20}
}]
```

Event-based SCHEDULE: `duration: {"eventTypeRuleDuration": {"eventId": "<from
ads_budget_rules_recommendation>"}}` — the rule follows Amazon's event dates.

PERFORMANCE adds: `"performanceMeasureCondition": {"metricName": "ACOS",
"comparisonOperator": "LESS_THAN_OR_EQUAL_TO", "threshold": 20}`.

**Update** (`operation=update`, body = list of **wrappers**, not flat):

```json
[{
  "ruleId": "<uuid>",
  "ruleState": "ACTIVE",
  "ruleDetails": {"name": "...", "budgetIncreaseBy": {"type": "PERCENT", "value": 25}}
}]
```

- `ruleDetails` on update may contain ONLY the mutable fields: `name`,
  `duration`, `budgetIncreaseBy`, `performanceMeasureCondition`. Including
  `ruleType` or `recurrence` → Amazon 400 `{"Message": "Expected null"}`
  (live-verified).
- `budgetIncreaseBy.type` is always `PERCENT`. There is no absolute-amount
  rule; "set budget to 80" is a base-budget edit, not a rule.

## 3. Per-product deltas — never assume symmetry

| | SP | SB | SD |
|---|---|---|---|
| PERFORMANCE `metricName` | `ACOS,CTR,CVR,ROAS` | **`IS,NTB,ROAS`** (never ACOS/CTR/CVR) | `ACOS,CTR,CVR,ROAS` |
| `comparisonOperator` | 5 values incl. `EQUAL_TO` | 4 (no `EQUAL_TO`) | 4 (no `EQUAL_TO`) |
| `recurrence.type` | **`DAILY` only** (create AND update) | `DAILY,WEEKLY` | `DAILY,WEEKLY` |
| Event recommendations | ✓ | ✓ marketplace-gated (§8) | **✗ none** |
| Bulk (dis)associate | endpoint exists, 401 (§5) | ✗ | ✗ |
| Report rule-audit columns (§6) | ✓ v3 `spCampaigns` | ✗ | ✗ |

**SP weekly patterns workaround:** SP has no `WEEKLY` recurrence. For
weekend-only uplift, batch-create dated date-range rules a quarter ahead (12
Sat/Sun windows fit in one ≤25-item create call + one associate pass). Do NOT
substitute a `DAILY` rule — that is a hidden permanent raise.

Metrics evaluate on **trailing 7 days for sellers** (14 for vendors). Amazon
requires a minimum daily budget for a performance rule to activate — on a small
campaign it silently sits at `BUDGET_THRESHOLD_NOT_MET` while every API call
returns success.

## 4. Rule state vs rule status — two different fields

- `ruleState` — what YOU set: `ACTIVE` | `PAUSED`.
- `ruleStatus` — what AMAZON reports: `PENDING_START` → `ACTIVE` → `EXPIRED`,
  plus `ON_HOLD`, `PAUSED`, `BUDGET_THRESHOLD_NOT_MET`.

Agent interpretation:

| Status | Meaning | Action |
|---|---|---|
| `PENDING_START` | Window hasn't begun **in marketplace-local time** | **Healthy.** Never re-create — that's how stacks happen |
| `ACTIVE` | Raising budget now | Verify with `ads_budget_usage` |
| `BUDGET_THRESHOLD_NOT_MET` | Perf rule: campaign below Amazon's minimum budget | Healthy mechanism, inert rule — tell the operator |
| `ON_HOLD` | Condition not met / superseded | Investigate if unexpected |
| `EXPIRED` | Past end date | Teardown: disassociate + pause |
| `PAUSED` | You paused it | — |

**Live-observed (2026-08-07):** a rule whose `startDate` is "today" in the
operator's timezone shows `PENDING_START` until **marketplace-local midnight**
— budgets, rule windows, and daily resets all run on the marketplace clock, not
yours or UTC. Always reason about "today" in the profile's timezone. And the
`PENDING_START → ACTIVE` flip is **not instantaneous at window open**: on a
live delivering campaign it took 2.5–5 hours after marketplace midnight
(measured). Do not re-create or "fix" a rule that is still `PENDING_START` in
the first hours of its window — verify at T-24h and re-check later on T-0.
**Disassociation, by contrast, takes effect promptly**: removing the rules
reverted the effective budget on the next usage read.

## 5. Live-verified behaviors (differ from or absent in the published spec)

- **207 per-item success code is `"Ok"`**, not `SUCCESS` — match either,
  case-insensitively. Always read `error[]` alongside `success[]`; `index` maps
  to your request order. Report BOTH counts ("38 of 44 ok; 6 errors — see
  sheet"). Request-level failures are plain 400/429.
- **`bulk_associate` / `bulk_disassociate` return 401** on accounts where the
  bulk surface isn't granted — verified across three separate ads accounts and
  marketplaces. Treat as unavailable; per-campaign `associate` / `disassociate`
  is the working path. Do not report the 401 as an account problem.
- **SB `ads_budget_rules_recommendation` is marketplace-gated** ("Unsupported
  Marketplace for Budget Event Rules") — confirmed rejected on AE and AU,
  confirmed working on US. The gate fires before campaign validation. An EMPTY
  event list on a supported marketplace is normal (no upcoming events).
- **`ads_sp_initial_budget_recommendation` targetingExpressions are objects and
  each requires a `bid`** even though the spec omits it; `targetingType` is
  lowercase `auto`/`manual`.
- **`usageUpdatedTimestamp` semantics (measured on live campaigns):** the stamp
  can lag the wall clock by **hours** (≈7h observed on a low-spend campaign),
  and campaigns with zero spend today report a synthetic `T00:00:00Z` midnight
  stamp. Always phrase a reading "as of <stamp>"; never treat the midnight-zero
  stamp as fresh; never trigger a change off a reading older than the account's
  observed update cadence. Campaign mutations (state change, rule
  associate/disassociate) trigger a prompt usage re-evaluation — after an
  approved change, read usage once more to capture the fresh post-change figure
  for the sheet.
- **`ads_budget_usage.budget` is the budget in force under the current policy**
  — while a rule is satisfied it exceeds the campaign's base `dailyBudget`.
  Never derive a base-budget change from it while any rule on the campaign is
  ACTIVE; read the base from `ads_*_campaigns` list.
- **Rule names:** ~40-char names with underscores and hyphens (the `BR_`
  convention) are accepted. Amazon does not meaningfully surface duplicates —
  the sheet registry, keyed by `ruleId`, is your real identity system.
- **Campaign responses carry the rule effect:** SD v0 campaign list returns a
  `ruleBasedBudget` object; SP v3 list returns `effectiveBudget`. Presence
  means rules applied — but the authoritative "which rules" view is always
  `list_for_campaign` (the single applicable-rule field can be incomplete when
  rules stack).

## 6. Caps, limits, audit paths

| Limit | Value |
|---|---|
| Rules per create/update call | 25 |
| Rule ids per associate call | 25 |
| Rules per campaign (Amazon max) | 250 — a ceiling, not a safety margin |
| `pageSize` on rule list ops | required, 1–30 |
| Ids per `ads_budget_usage` call | 100 — chunk larger sets |
| Ids per SB budget-recommendations call | 100 |
| Intraday windows per rule | 1; **US/CA/UK/IN/JP marketplaces only** |

**No delete API.** Retirement = `disassociate` from every campaign + update
`ruleState=PAUSED`. Rules are permanent objects; hygiene (below) keeps
`list_for_campaign` legible.

**Historical audit:** SP only — v3 `spCampaigns` report (groupBy `campaign`)
columns `campaignRuleBasedBudgetAmount`, `campaignApplicableBudgetRuleId`,
`campaignApplicableBudgetRuleName` show which budget was in force day by day
(30min–hours latency; throttled — submit one at a time). **SB/SD have no report
columns**: the sheet snapshots you write during the rule window are the ONLY
audit trail that will ever exist for them — writing them is mandatory, not a
nicety. Amazon's Snapshots API is retired; never reach for it.

## 7. Stacking — the top-severity failure

Every satisfied rule applies **additively**: effective = `base × (1 + Σ pct/100)`.
**Measured live (2026-08-07):** two rules (+5% and +10%) on a 4.00-budget
campaign produced an effective budget of exactly **4.60** (= 4.00 × 1.15,
additive), not 4.62 (multiplicative), during the active window — and
`ads_budget_usage.budget` reported the raised figure. A +40% performance rule
during a +100% event rule = +140%, on the year's most expensive clicks.
Guardrails:

1. **`list_for_campaign` before every create/associate** — the authoritative view.
2. Refuse to create a rule overlapping an existing one of the same type +
   trigger whose window intersects.
3. Sum every rule that could be satisfied simultaneously; keep worst-case
   effective budget ≤ **2.5 × base** (or the operator's `Budget Caps` value)
   unless the operator explicitly signs off higher.
4. Practical max **2 active rules per campaign** unless deliberately designed.

## 8. Marketplace / product gating matrix

| Capability | Available | Not available |
|---|---|---|
| Intraday (`intraDaySchedule`) | US, CA, UK, IN, JP | everywhere else — day-parting there = bid/placement adjustments |
| SB event recommendations | US (verified) | AE, AU (verified rejections); gate precedes campaign validation |
| SD event recommendations | — | nowhere (Amazon has none; hand-build date-range rules from SP/SB event dates) |
| SP bulk (dis)associate | — | 401 on all tested accounts; use per-campaign ops |

Probe once per store × marketplace (cheap reads: rules `list` per product, one
recommendation call, one usage call) and record the answers in the workbook's
`Budget Capabilities` tab so gates become lookups instead of recurring errors.

## 9. Operating defaults (operator-tunable — confirm targets before first use)

**Intraday pacing curve** (consumer marketplaces, marketplace-local time; judge
`usage% ÷ expected%`, never raw usage):

| Local time | On-pace | Investigate above |
|---|---|---|
| 09:00 | 15–20% | 35% |
| 12:00 | 35–40% | 60% |
| 15:00 | 50–60% | 80% |
| 18:00 | 70–75% | 95% |
| EOD | 85–95% | — |

Pace ratio ≥1.4 → about to cap. EOD usage <85% → budget is NOT the limiter —
do not raise regardless of recommendations. Usage >100% is legal: daily budget
is a **monthly average** (Amazon may overspend a day and offset later); never
alarm on a single day's overage.

**Minimum data before trusting a metric (trailing 7d, sellers):** ACOS/ROAS
≥10 orders AND ≥100 clicks · CVR ≥100 clicks · CTR ≥5,000 impressions · SB IS
≥10,000 impressions · SB NTB ≥20 orders. Below the floor, a performance rule
automates noise.

**Sizing defaults:** performance-rule threshold at **0.75–0.85 × target ACOS**
(never AT target — the trailing-7d window whipsaws around it), increase +25%
(ceiling +50%); major event +50–100%; minor event +25–50%; intraday window
+30–60%; base-budget steps +20–30% re-evaluated after 7 days (a >50% jump makes
Amazon re-learn pacing). Break-even check on any recommendation: assume marginal
ACOS ≈ **1.4 × blended**.

**Cadence (v1 = operator-invoked):** run the pacing check when the operator
asks (a morning ask and an optional afternoon ask are the natural rhythm);
event lifecycle at T-14 / T-3 / T-0 / T+1; rule hygiene after every event and
monthly. Once the routine has stabilized for an operator, SUGGEST automating
the cadence (scheduled agent runs) — do not set up automation unprompted.

## 10. Standing sheet artifacts

Create these tabs in the store's SellerSheet workbook on first budget
engagement (headers exactly as below; append-only where noted). They are what
make runs idempotent, auditable, and safely autonomous.

**`Budget Rules Registry`** — one row per rule we know about; the local
authority. Columns: `rule_id` (key) · `rule_name` · `store` · `country_code` ·
`ad_product` · `rule_type` · `increase_pct` · `duration_kind` · `start_date` ·
`end_date` · `event_id` · `metric` · `operator` · `threshold` · `rule_state` ·
`rule_status` (two columns on purpose — see §4) · `associated_campaign_ids` ·
`created_by` (`agent`|`operator`|`console`|`unknown`) · `created_at` ·
`last_verified_at` · `teardown_due` · `notes`.

**`Budget Change Log`** — append-only ledger; intent AND result in one row.
Columns: `intent_id` (`<store>-<cc>-<campaignId>-<action>-<YYYYMMDDTHHMM>` —
the idempotency key; Amazon has none, so a retried run double-applies without
it) · `logged_at_utc` · `action` · `ad_product` · `campaign_id` ·
`campaign_name` · `rule_id` · `before_value` · `proposed_value` · `evidence` ·
`approval` (`PENDING`|`APPROVE`|`REJECT`) · `approved_by` · `result`
(`APPLIED`|`FAILED`|`PARTIAL`|`SKIPPED`) · `amazon_code` · `verified_at` ·
`verified_state`. The agent writes `PENDING` and stops; the operator flips the
cell; the agent applies and writes the read-back.

**`Budget Caps`** — the operator's standing envelope. **Discuss the values with
the operator and write the tab together on first budget engagement; the tab is
human-owned** — the agent proposes values and edits only on the operator's
word, and re-reads it at the start of every mutating run (never cache).
Columns: `scope` (`CAMPAIGN`|`PRODUCT_LINE`|`PORTFOLIO`|`STORE`) ·
`scope_value` · `max_daily_budget` · `max_single_increase_pct` ·
`max_stacked_rule_pct` · `max_active_rules` · `target_acos` · `set_by` ·
`set_at` · `expires_at`. Any proposal exceeding a cap is flagged, never
auto-applied; an absent cap row is never an approval.

Optional as the practice matures: `Budget Watch` (append-only usage log — one
row per campaign per observation with `usage_updated_timestamp` and status
`OK|PACING_HOT|CAPPED_LIKELY|STALE_FEED|ERROR`), `Budget Event Plan` (the
T-14→T+1 state machine: `gate_status`
`PLANNED|APPROVED|ARMED|VERIFIED|TORN_DOWN`), `Budget Capabilities` (§8 probe
results).

## 11. Rule ownership discipline

- Register every rule the agent creates (`created_by=agent`) with
  `teardown_due = end_date + 1 day`.
- Rules found on Amazon but not in the registry are `UNTRACKED` — **never
  pause, update, or disassociate them**; they may be a load-bearing manual
  control. Report them and let the operator decide (then register them
  `created_by=operator` if kept).
- After every event and monthly: sweep for orphans (ACTIVE/PENDING_START with
  zero associations, rules on archived campaigns, EXPIRED still associated) and
  propose cleanup.
- T+1 after every event rule: confirm `EXPIRED`, **measure** that the budget
  actually reverted (compare `ads_budget_usage.budget` to the registry's base),
  disassociate + pause, and — the classic omission — **revert any manual event
  bid raises**: budget rules auto-revert, bids do not.

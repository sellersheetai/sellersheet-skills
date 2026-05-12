# Grow checklists

How to expand an existing dashboard without breaking what's there. Two scenarios: adding a new domain, and adding a new store.

## Grow checklist — adding a new domain (e.g. "Returns")

When a dashboard needs a new domain tab (Returns, Buy Box, Cash Conversion, Vendor Retail, etc.):

1. **Create `_raw_<domain>` tab** with the canonical left-five columns:
   ```
   store, sku, asin, image_url, product, ...domain-specific cols
   ```
   Open-range, single header row at A1.
2. **Add 1 row per store to `_status`** (so a 2-store workbook gets 2 rows for the new domain). Populate:
   - `source_rpt_table` — comma-separated rpt_* names
   - `refresh_cadence` — `6h` / `daily` / etc.
   - `expected_lag_hours` — see `reference/freshness-system.md` budget table
   - `last_pulled_utc` — real timestamp (if data exists) OR `NOT_YET_SYNCED` in `last_error`
3. **If data isn't yet wired:** add the A2 sentinel row to `_raw_<domain>`:
   ```
   _raw_<domain>!A2:Z2 = ["<store>", "NOT_YET_SYNCED", "<rpt_table> not yet wired — see _status", "", ...]
   ```
4. **Build the visible tab** using the layout grammar:
   - Row 1: emerald title
   - Row 2: live `TEXTJOIN` freshness pill referencing the new `_status` row
   - Row 4+: AT-A-GLANCE rollup section (formula-driven)
   - Last section: section band + SQL spill from `_raw_<domain>` + image MAP+JOIN at col A
   - Row 150 or 400 (per overflow guard): AGENT INSIGHTS FILTER scoped to `_agent_notes.scope_tab = "<new tab name>"`
5. **Update README tabs list** — add the new tab with refresh cadence and stores in scope.
6. **Add an agent note in `_agent_notes`** documenting the scaffold + activation path:
   ```
   N00X | <ts> | claude-... | ALL | <new tab> | scaffold | info | "<domain> tab scaffolded; <rpt_*> not yet synced" | "Activate via /report-data skill: trigger <rpt_table>" | "<new tab>!A4,_status!A<row>" | 0.9 | ""
   ```
7. **Verify** via `scripts/post-build-checklist.md` that:
   - Row 2 pill resolves cleanly (no `#REF!` / `#ERROR!`)
   - AGENT INSIGHTS spill renders or shows "No active insights"
   - Sentinel row (if used) renders distinctly

## Grow checklist — adding a new store (e.g. myStore-DE)

When a single-store dashboard needs to expand to multi-store, or a multi-store dashboard adds a third+ marketplace:

1. **Add the new currency to `_config`** if not present:
   - `cfg_fx[USD]` row (rate + as_of date)
   - Verify `cfg_ship_rmb_kg` and `cfg_referral_pct` still apply (referral may differ per marketplace — usually 13% but some categories vary)
2. **For every `_raw_*` tab**: the refresh agent appends new rows scoped to the new store. Use the same `query_report_data(..., store='myStore-DE')` pattern that exists for existing stores.
3. **Add one row per `_raw_* × new-store` to `_status`** — preserve all existing rows; just append new ones with appropriate budgets.
4. **Each visible tab's SQL spill is store-agnostic by design** — no changes needed. The spill grows naturally.
5. **HOME's per-store tiles get a duplicate row band** for the new store. Currency-normalize the comparable columns (USD eq). Don't add a 3rd or 4th currency to existing tile columns without normalizing.
6. **Multi-marketplace EU expansion** (one seller_id across UK + DE + FR + ...): use the comma-separated `country_code` query pattern. Each marketplace gets its own Store identifier (`myStore-UK`, `myStore-DE`). `_status` grows to N rows per `_raw_*` × marketplace. Consider switching HOME to per-store-rollup-with-drill-down above 5 marketplaces.
7. **Locale-required tiles**: check `reference/multi-store.md` for the marketplace's required tiles (Ramadan calendar for MENA, LTSF aging for AU, Prime Day for US, VAT-OSS for EU). Surface stubs at minimum.

## The contract — what guarantees the dashboard absorbs growth

> **`_raw_*` tabs are the API.**

If a new domain or store preserves these five columns in this order, the dashboard pattern absorbs it without rebuilding anything visible:

```
A=store, B=sku, C=asin, D=image_url, E=product, F+=...
```

Anything else is a breaking change. Specifically:

- ✅ Adding new domain-specific columns to F+ — fine.
- ✅ Adding new stores to the existing column structure — fine.
- ✅ Adding new `_raw_*` tabs — fine.
- ❌ Changing column A's semantic from `store` to anything else — breaks every COUNTIF, every FILTER, every Store column on every visible tab.
- ❌ Splitting `store` into `store_name` + `country_code` columns — breaks every existing `MATCH("myStore-US", _status!A:A, ...)`.
- ❌ Renaming `image_url` to `thumbnail_url` — breaks every Image MAP+JOIN.

## Post-grow verification

After adding a new domain or store:

1. `scripts/post-build-checklist.md` — full read-back sweep.
2. Verify no spill collisions (`#REF!`) on the existing tabs — the new domain's spill could push the AGENT INSIGHTS row anchor.
3. Open in browser; check Image-Store-SKU alignment on the new tab.
4. Confirm `_status` shows the new rows with correct status (GREEN-fresh if data wired, RED-error if scaffold).
5. Add a row to `_agent_log` documenting the grow event (`prior_value`: tab list before, `new_value`: tab list after, `rationale`: why this grew).

## See also

- `reference/freshness-system.md` — `_status` schema for new rows
- `reference/multi-store.md` — marketplace-specific rules + canonical store identifier form
- `reference/agent-insights.md` — how to scope AGENT INSIGHTS sections per tab
- `scripts/seed-status-rows.md` — template `_status` rows for common new domains

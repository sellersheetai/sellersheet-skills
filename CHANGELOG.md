# Changelog

All notable changes to SellerSheet Skills are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Planned for upcoming releases (under review):
- `sellersheet` — Amazon business operations orchestrator
- `amazon-api` — Amazon SP-API guide
- `fba-inbound` — FBA inbound shipment workflow
- `listing-optimizer` — Full agent-orchestrated listing optimization
- `listing-refurbish` — FBA ASIN migration
- `amazon-listing-optimizer` — Multi-market listing optimization

## [0.11.0] — 2026-07-16

### Added

- **The plugin now bundles the SellerSheet MCP server.** A keyless remote-HTTP `.mcp.json`
  (`https://sellersheetai.com/mcp`) ships at the plugin root, so on Claude Code and Codex
  **one plugin install delivers skills + MCP** — authenticate once via browser OAuth
  (`/mcp` in Claude Code; `codex mcp login sellersheet` in Codex), no API key. A
  manually-added `sellersheet` server shadows the plugin copy on both agents, so existing
  setups keep working unchanged. This restores what ≤0.5.0 attempted with a broken *local
  stdio* bundle (removed in 0.5.1) — the difference is nothing runs locally. lint now
  enforces the bundle contract: `type: http`, the exact hosted URL, keyless, never a
  local `command`.

### Documentation

- Install docs rewritten plugin-first: Claude Code and Codex get the one-step story
  (install → sign in); the manual per-agent MCP table in `setup-mcp.md` now serves agents
  without a plugin system. OpenClaw added to the README install section (its plugin
  system accepts the Claude/Codex bundle layout). Codex prerequisites trimmed to a
  one-liner per operator direction.

## [0.10.2] — 2026-07-16

### Added

- **`sellersheet-sheets`** — the Codex-spreadsheets-style **local build → one-shot import**
  pipeline is now a first-class build route (`reference/local-build-import.md`): heavy
  net-new builds author the whole workbook locally with openpyxl and land it as a native
  Google Sheet via a single `start_drive_upload(convertTo=…)` call (optionally
  `copy_sheet_tab` into an existing workbook, `_raw_*` tabs first), instead of dozens of
  MCP round-trips. Includes the verified fidelity list (`=SQL()` verbatim, conditional
  formats applied, charts, dropdowns, hidden tabs) and the hard-won gotchas (explicit
  Arial 10 + column widths, DataBarRule dropped, `SQL()` ranges as args, upload
  Content-Type match). Held until the `convertTo` server support reached production —
  it deployed 2026-07-16. Hosted agents without a filesystem keep the MCP workflow.

### Fixed

- **`image-gen`** — `reference/aplus-modules.md` referenced the retired
  `submit_aplus_document` tool; the approval submission tool is
  `post_content_document_approval_submission` (recovered from the 2026-06-25 operationId
  reconciliation that never crossed into this repo).

## [0.10.1] — 2026-07-16

### Fixed

- **`versions.json` `install_commands` caught up to the plugin-only story** — the catalog
  MCP serves via `get_user_context.skills_catalog` was steering plugin users at
  `install.sh --update`, which installs a second skill copy next to the plugin (the exact
  dual-source mess the plugin path exists to avoid), and had no Codex entry at all. Now:
  complete per-agent pairs — `claude-code`/`claude-code-update`,
  `codex`/`codex-update`, `other`/`other-update` (npx skills) — and `update` is a routing
  note instead of an `install.sh` command.
- **`sellersheet-shared`** — preflight step 2 now uses the server-computed
  `data.skills_update` verdict (one bundle-level comparison, per-agent update commands)
  instead of teaching agents to diff `skills_catalog` per-skill; explicitly forbids
  suggesting `install.sh` to plugin users. Falls back to `skills_catalog` on older MCP
  builds.
- **lint** — new skills_catalog contract checks: all seven `install_commands` keys must
  exist, update commands must not reference `install.sh`, every catalog skill needs a
  non-empty description.

## [0.10.0] — 2026-07-16

> This release was originally tagged with a hand-edited `plugin.json` bump only; the full
> version fan-out + this entry were repaired after the fact. See the new AGENTS.md release
> protocol — releases go through `promote.sh`, never hand edits.

### Changed

- **`sellersheet-sheets`** — new `reference/charts.md` (`add_sheet_chart` contract: column→series,
  explicit anchor, type selection, placement, server-side verification limits); SKILL.md gains
  three request modes (answer/edit/build) with an edit-discipline recipe and an
  identifier-coercion quick-reference; `mcp-gotchas.md` documents USER_ENTERED coercing
  identifiers (leading-zero UPC, date-shaped SKU) — apostrophe or @ text format.
- **`report-data`** — query semantics synced with the 2026-07-15 server hardening: strict spec
  keys, `dir|direction`, `is_null`, NULLS LAST, registry-derived `report_date` default,
  AUTO-OVERRIDE rule, date-grain guidance, aggregation (op/alias/having/bucketing),
  page-1-only COUNT, offset cap, retention-horizon note. DK example queries fixed
  (`report_date 'all'` + date filter). 5 zombie BA/S&T reference JSONs + `_meta` entries
  removed (tables dropped server-side); `_meta.cron` synced to the 01:00–01:19 local band
  (39 tables); vendor-truth nullable date columns declared (9 tables);
  `rpt_sp_targets`/`rpt_sp_keywords` calibration sync (dead columns dropped, dedup notes).

### Documentation

- Claude Code + Codex install paths are **plugin-only** — direct `install.sh`/manual-copy
  alternatives removed for the two agents with a plugin system.

## [0.9.0] — 2026-07-15

### Added

- **`sellersheet-shared`** — a companion skill that is the single source of truth for what
  every skill used to copy: the MCP preflight protocol (`get_user_context` → `skills_catalog`
  version check → `canUseMcp`), store-reference rules (`name-country`, multi-marketplace
  suffix), the MCP response contract (always relay `notification.message` + `human_action`),
  and a troubleshooting table. All 8 skills now open with a 2–4 line pointer to it instead of
  a ~1.4 KB copied block — the copies had already drifted (3 skills still told users the
  API key lived at "Settings → API", a page that doesn't exist).

### Changed

- **The bundle now always installs as a whole set.** Skills cross-reference
  `sellersheet-shared`, so partial installs are no longer supported or documented:
  `install.sh` drops the `--skills` flag (always installs everything under `skills/`), and
  the "Selective install" / single-skill `npx skills -s` examples are removed from README
  and the per-agent guides.

### Fixed

- **`image-gen`** — SKILL.md frontmatter `description` was an unquoted YAML scalar containing
  `Triggers: "…"`; the embedded `: ` breaks strict YAML parsers (js-yaml, used by `npx skills`),
  which silently skipped the skill — `npx skills add` installed only 7 of 8 skills. The
  description is now a `>-` folded block scalar, so all install channels see the full bundle.

### Documentation

- README + install docs caught up to the 8-skill bundle: `amazon-ads`, `amazon-report`, and
  `data-kiosk` added to the skill table (they shipped in 0.8.x but the README still said
  "five skills" / "three skills"); `npx skills` examples now cover global (`-g`) installs.
- **MCP setup docs rewritten for the hosted remote server.** Every reference to the retired
  `npx @sellersheet/mcp-server` stdio package (npm 404 — removed in 0.5.1) is gone from
  README, `mcp/sellersheet.json`, `setup-mcp.md`, and the per-agent install guides; they now
  point at `https://sellersheetai.com/mcp` with OAuth (Claude Desktop connectors,
  `codex mcp add`) or Bearer-key configs. The stale "plugin auto-registers MCP via
  `.mcp.json`" claim (false since 0.5.1) is corrected everywhere: **MCP and skills are two
  independent install steps.** API-key path fixed to Dashboard → MCP & API keys → Create
  Key; ads authorization fixed to My Stores → Authorize Ads.
- **Codex plugin install documented** (live-verified on codex-cli 0.144.2): Codex reads
  `.claude-plugin/marketplace.json` directly, so `codex plugin marketplace add
  sellersheetai/sellersheet-skills` + `codex plugin add sellersheet-skills@sellersheet-marketplace`
  installs the same bundle — one repo serves Claude Code and Codex. `install-codex.md`
  rewritten around this path, including the `config.toml` gotcha (`http_headers`, not
  `headers`, for manual Bearer setups).

## [0.8.6] — 2026-07-10

### Changed

- **`report-data`** — **`rpt_*` table names are now the Amazon report types.** 17 physical
  tables were renamed server-side (migration `d5f7a9c1e3b5`) so the table name is `rpt_` +
  the `report_type` that feeds it, lowercased — an agent reading Amazon's docs recognises the
  table without a lookup. Highlights: `rpt_listings_snapshot` → `rpt_get_merchant_listings_all_data`,
  `rpt_restock_recommendations` → `rpt_get_fba_inventory_planning_data`, `rpt_account_health` →
  `rpt_get_v2_seller_performance_report`, `rpt_fba_inventory_health` →
  `rpt_get_fba_myi_all_inventory_data`, `rpt_settlements` →
  `rpt_get_v2_settlement_report_data_flat_file_v2`. **Every old name still resolves as a
  read-only compat `VIEW`,** so existing SQL keeps working — but new queries should use the
  canonical name. The 17 reference JSONs were renamed to match, and each carries a
  `_meta.naming_note`. A new **Deliberate naming exceptions** section documents the tables that
  keep non-Amazon names on purpose: `rpt_orders` (fed by **two** order report types),
  `rpt_sp_purchased_products`, all ads `rpt_sp_*`/`rpt_sb_*`/`rpt_sd_*`, `rpt_dk_*`,
  `rpt_noon_*`, retired tables, PII tables, and `listing_images`.
  Swept across `report-data`, `sellersheet-dashboard`, and `amazon-report`.

### Fixed

- **`report-data`, `sellersheet-dashboard`** — the `days_of_supply` NULL-sorting gotcha was
  **misattributed to Postgres**. Postgres sorts NULLs **LAST** on `ORDER BY ... ASC` — the
  warehouse layer is safe. It is the **in-sheet `SQL()`/alasql layer that sorts blanks FIRST**,
  which is where the unsorted-looking "urgent" restock lists actually come from. Corrected in
  `report-data/SKILL.md`, `reference/rpt_get_fba_inventory_planning_data.json` (`_meta.gotchas`
  + the `days_of_supply` column note), and `sellersheet-dashboard/reference/lint-and-rules.md`.
  Guidance unchanged in effect: filter `days_of_supply > 0` in either layer.
- **`report-data`, `amazon-ads`** — documented that `rpt_sp_*` / `rpt_sb_*` / `rpt_sd_*` are
  **daily performance rows, not a campaign inventory**. Only campaigns with delivery in the
  window get a row (live count 47 ENABLED vs 21 present in the warehouse, observed), so never
  derive a campaign count from them — call the live `ads_sp_campaigns` / `ads_sb_campaigns` /
  `ads_sd_campaigns` API. Also: `report_date='latest'` pins to the newest **single** day, often
  a zero-spend partial day — use `report_date='all'` + date filters for cost/perf analysis.
- **`sellersheet-sheets`, `sellersheet-dashboard`** — added the **`SQL()` provisioning caveat**:
  `SQL()` is a SellerSheet add-on custom function and only evaluates in workbooks where a human
  has opened Extensions → SellerSheet → Open at least once. Arbitrary MCP-created spreadsheets
  show `#NAME?` permanently — write pre-computed values or plain formulas there instead. Also
  noted that a freshly written `SQL()` spill cell can read back empty for a few seconds during
  recalc; re-read before concluding failure.
- **`sellersheet-sheets`, `sellersheet-dashboard`** — added the **`IMAGE()` caveat**: under some
  conditions a service-account-written `IMAGE()` cell renders as `#REF!` ("use desktop browser")
  for the human until the workbook is opened in a desktop browser, and reading it back via MCP
  requires `value_render_option='FORMULA'`.
- **`report-data`** — `_meta.json` listed `rpt_fba_inventory_health` with report type
  `GET_FBA_INVENTORY_PLANNING_DATA`, copied from the restock entry. It is
  `GET_FBA_MYI_ALL_INVENTORY_DATA`; the two reports ship different column sets and must never be
  cross-pollinated. Exposed by the rename sweep.
- **`report-data`** — dropped the stale "`recommended_replenishment_qty` falls into `extra` JSON"
  wording left in `reference/rpt_get_fba_inventory_planning_data.json` after 0.8.5 established
  that it is a real column.

## [0.8.5] — 2026-07-10

### Fixed

- **`report-data`** — added a **"Restock gotchas"** best-practice block for
  `rpt_restock_recommendations` covering the three silent traps: (1) join on `sku` — the
  canonical key matching Amazon's `GET_FBA_INVENTORY_PLANNING_DATA` header; the legacy
  `merchant_sku` alias was **dropped from this table 2026-07-10**, so older dashboards/SQL
  joining on it must switch to `sku`; (2) `days_of_supply` is NULL for no-sale SKUs and Postgres
  sorts NULLs FIRST, so `ORDER BY days_of_supply ASC` buries urgent low-cover SKUs — filter
  `days_of_supply > 0` or use `NULLS LAST`; (3) Amazon's replenishment columns are
  `recommended_order_quantity` + `recommended_order_date` — the legacy
  `recommended_replenishment_qty` exists only for pre-migration historical rows. Mirrored these
  into `reference/rpt_restock_recommendations.json` (`_meta.gotchas`, `unique_key` and column
  `merchant_sku`→`sku`, `nullable`/notes on `days_of_supply`, `recommended_order_quantity`,
  `recommended_ship_in_quantity`).
- **`sellersheet-dashboard`** — added a restock-qty null-fallback rule to
  `reference/lint-and-rules.md`: when Amazon's recommended-qty columns are all NULL, compute
  `suggested_ship_in = MAX(0, ROUND(units_shipped_t30/30 × target_cover_days) − available −
  inbound)` and label it as **computed, not Amazon's**.
- **`sellersheet-sheets`, `sellersheet-dashboard`** — corrected the stale MCP tool prefix
  `mcp__claude_ai_sellersheet_mcp__*` to `mcp__claude_ai_sellersheet_<env>__*` (`<env>` is
  `prod` or `test` depending on which SellerSheet MCP connector is attached) across `SKILL.md`
  and `scripts/post-build-checklist.md`.

## [0.8.4] — 2026-07-06

### Changed

- **`sellersheet-sheets`** — reconciled the row-height rule across `SKILL.md`,
  `brand-standards.md`, `image-pattern.md`, `action-sheets.md`, and `starter-recipes.md`.
  Previously the docs contradicted themselves (38 px thumbnail rows vs. "never set row
  heights"). Now uniform: **keep Sheets' default (~21 px) on every row, including
  image/thumbnail rows — a thumbnail is a quick "which SKU" reminder, not a detail view.
  The only sanctioned custom row height is the emerald title banner (~34 px).**
- **`sellersheet-sheets`** — rewrote the column-width guidance. Pixels are called out as
  Google Sheets' *native* width unit (not a workaround). Deliberate **fixed widths are the
  default** for operator tables (size to the header, not the data); `autofit_sheet_columns`
  is demoted to a **narrow final polish** for short/structured columns with three hard rules:
  run it **LAST — after `set_sheet_basic_filter`** (autofit doesn't reserve room for the
  filter arrow, so autofit-before-filter clips every header — verified on a live build);
  **never autofit column A or long free-text columns** (images, product titles, descriptions);
  and accept its zero-padding hug (bump a few px if a header still clips). Documented the
  live `autofit_sheet_columns` route (replacing the outdated "exists in some MCP builds" hedge
  and the inferior `len × px` estimate).

## [0.8.3] — 2026-07-01

### Added

- **`amazon-ads`** — DSP advertiser discovery: documented the new `ads_dsp_advertisers`
  tool (GET `/dsp/advertisers`) for pulling the real `advertiserId` that DSP offline
  reports require (the bundled DSP report-configs carry a placeholder). Notes the
  hard requirement that DSP needs an **AGENCY-type ad profile** — seller/vendor profiles
  return 400 "Selected profile type is not agency" (verified live). Added to the account
  tool table + the report-configs DSP section.

## [0.8.2] — 2026-06-30

### Changed

- **`amazon-ads`** — §1 now states the `store` param norm explicitly: always pass
  `<name>-<countryCode>` (e.g. `store="myStore-US"`). A bare name is ambiguous when the
  same brand exists in multiple marketplaces (different stores / ad profiles) and is now
  rejected server-side; the cc-qualified `store` is what disambiguates.

## [0.8.1] — 2026-06-30

### Fixed

- **`amazon-ads` report-configs** — corrected 11 of the 35 bundled v3 `createReport`
  templates that Amazon's live `createReport` rejects: SB `*Daily` configs dropped the
  `startDate`/`endDate` columns (DAILY requires `date`); `SponsoredProductsKeywordsSummaryReport`
  dropped its `date` column (SUMMARY requires `startDate`/`endDate`); both Sponsored TV
  `*Daily` configs gained a `date` column; and groupBy-invalid filters/columns were
  removed (spAdvertisedProduct `campaignStatus`, sbAds filters, sbTargeting `keywordStatus`,
  sbSearchTerm `keywordStatus`/`query`). All verified accepted live. README + Recipe G
  hardened with the timeUnit↔date rule, groupBy-specific-filters rule, and the
  `createReport` throttling guidance (submit one-at-a-time, back off on 429).

## [0.8.0] — 2026-06-30

### Added

- **`amazon-ads`** — Amazon Advertising (SP, SB, SD) operations guide for SellerSheet MCP: cross-cutting conventions, campaign naming, two performance-data paths (warehouse vs offline report), and workflow recipes (account health, waste mining, bid/budget optimization, bulk launch, negatives, export, change history, recommendations). Bundles `reference/report-configs/` — 35 real Amazon Ads Reporting API v3 `createReport` request bodies (SP/SB/SD/Sponsored TV/DSP) with full authoritative column sets, plus a lookup index.

## [0.7.1] — 2026-06-19

### Changed

- **`noon-report-data`** — all 4 noon reports (orders, finance, FBN aging, product views) now run on `0 4,16 * * *` (04:00 + 16:00 UTC); the schedule table was previously staggered (03/04/06/08). Matches the reporting-server registry.

## [0.7.0] — 2026-06-17

### Added

- **`amazon-report`** skill — authoritative DOCUMENT schemas for 22 Amazon SP-API on-demand reports (Brand Analytics: search query/catalog performance, search terms, market basket, repeat purchase; Sales & Traffic; Promotion/Coupon; all Vendor reports; marketplace ASIN page-view; end-user data; account health). Bundles each report's JSON-Schema under `reference/`, plus a `_meta.json` index mapping `reportType` → required `reportOptions` (with enums) → document data-key → schema file, so agents request the right report and parse fields by their real names instead of guessing. Includes a warehouse-first routing gate (check `report-data` before requesting on-demand).
- **`data-kiosk`** skill — authoritative GraphQL schemas for Amazon SP-API Data Kiosk (Sales & Traffic, Economics, Vendor Analytics). Bundles the SDL under `reference/`, plus a `_meta.json` index of versioned root query types, datasets, required args, enums (`DateGranularity`/`AsinGranularity`), and per-field `@resultRetention`, so agents author a valid `createQuery` string instead of guessing. Same warehouse-first routing gate (`report-data` → `query_report_data` before authoring a query).

## [0.6.0] — 2026-06-17

### Added

- **`noon-report-data`** skill — query the 4 `rpt_noon_*` noon (noon Partners) warehouse tables (orders, finance/transactions, FBN inventory aging, product-views & sales) for a connected noon store, via the same `query_report_data` MCP tool. Covers the twice-daily ingestion schedule, project-scoped (owner-only) access, per-marketplace semantics (orders by `market_place_country_code`, finance by `contract_title`→`marketplace`, aging/views per-marketplace), the `partner_barcode` grain on aging, and the snapshot-vs-incremental `report_date` rules (FBN current stock = latest `snapshot_date`, never `report_date='latest'`).

## [0.5.1] — 2026-06-15

A packaging fix. No skill content changes — every skill's `version` bumps to 0.5.1 with the plugin per single-source versioning.

### Fixed

- Removed the broken bundled MCP server (`.mcp.json`). It pointed at `npx @sellersheet/mcp-server`, which is not published to the npm registry (404), and also required an unset `SELLERSHEET_API_KEY` — so the plugin's stdio MCP server failed to start on every load (JSON-RPC `-32000`). The plugin ships **skills only**; users connect the hosted SellerSheet MCP via the remote connector. The setup template at `mcp/sellersheet.json` is retained as documentation.

## [0.5.0] — 2026-06-09

Adds the **image-gen** skill — the fourth production skill. (Per single-source versioning, every skill's `version` bumps to 0.5.0 with the plugin.)

### Added

- **image-gen** — Amazon listing image + A+ Content suite, generated with gpt-image-2 via the SellerSheet MCP. Learns mature competitors' image style (`reverse_prompt`), generates and recolors product-faithful images (`generate_image` / `edit_image`), enforces Amazon main-image compliance, builds A+ modules, scores them, builds review previews, and records to the operator's 'Images Generation' sheet. 9 reference files (slot canon s0–s8, amazon-compliance + QA gate, A+ modules incl. the Amazon SP-API Basic A+ spec, OpenAI gpt-image prompting fundamentals, provider matrix, multi-turn chain, gotchas, sheet contract) + 1 preview-builder script. Universal-install ready — no harness- or backend-specific coupling.

### Changed

- Marketplace/plugin description now mentions gpt-image-2 listing/A+ image generation; added `image-generation` + `a-plus-content` keywords.

## [0.4.0] — 2026-06-07

A docs-hardening pass on the `SQL()` / `IMAGE()` sheet workflow, plus the cross-agent installer guide.

### Changed
- **`sellersheet-sheets` / `sellersheet-dashboard`** — clarified `SQL()` / `IMAGE()` / `IMPORTRANGE()` error semantics: the browser-pending `#NAME?` state (expected — it renders once the SellerSheet add-on loads in a browser) is now clearly separated from real bugs (`#REF!`, `#ERROR!`, `#VALUE!`, unwrapped `#DIV/0!`). Golden Rule: a `#REF!` is always a real bug, never "pending."
- **Browser-handoff rule** — the agent never opens or drives a browser to "finish" a build. The one-time approval (Extensions → SellerSheet → Open, allow external images, allow `IMPORTRANGE`) and the final Image-Store-SKU render check are the user's; server-side verification ends at the read-back sweep.
- **Final review gate** — every `sellersheet-sheets` build now ends with a mandatory checklist (error sweep across all tabs, row-count match, number-format/brand-color spot check, growth test) before the build is declared done.
- Reserved-word bracket-quoting guidance for `SQL()` column names (`store`, `status`, `date`, `order`, …).

### Documentation
- `docs/install-npx-skills.md` — install guide for the [`npx skills`](https://github.com/vercel-labs/skills) cross-agent installer, now the recommended path for Codex, Cursor, Gemini, Antigravity, and 50+ other agents. README + per-agent docs updated to surface it ahead of the `install.sh` fallback.

## [0.3.0] — 2026-05-21

A plugin-standard and auto-update hardening pass, plus the accumulated `report-data` calibration work since 0.2.0.

### Changed

- **Single-source versioning.** `.claude-plugin/plugin.json` `version` is now the one canonical version. `marketplace.json` no longer carries a duplicate `version` on the plugin entry — Claude Code lets `plugin.json` win silently, so a duplicate only invites drift. `versions.json`, every `SKILL.md` frontmatter, `install.sh`, and `README.md` are mirrors, enforced by CI.
- `report-data` skill description converted from a YAML folded scalar (`description: >`) to a single-line string for frontmatter-parser robustness.

### Added

- **`.mcp.json`** at the plugin root — installing the plugin now auto-registers the SellerSheet MCP server. Users only set the `SELLERSHEET_API_KEY` environment variable instead of hand-editing agent config JSON.
- **GitHub Actions CI** (`.github/workflows/`): `lint.yml` validates plugin structure, version consistency, and the privacy/ASIN scans on every push and PR; `auto-tag.yml` creates a release tag whenever `plugin.json` `version` changes on `main`.
- **Auto-update documentation** — `docs/auto-update.md` plus a README section covering how to enable marketplace auto-update (third-party marketplaces are opt-in by default) and the `extraKnownMarketplaces` settings snippet.

### report-data calibration (since 0.2.0)

- `rpt_orders` +13 promoted columns; `rpt_settlements` +9 typed breakdown columns; `rpt_fba_fee_preview` +7 future-fee columns; `rpt_restock_recommendations` +17 calibration columns; `rpt_listings_snapshot` +4 calibration columns.
- `rpt_sb_purchased_products` calibrated to the Ads API v3 schema; ads tables now document the `country_code` column; `rpt_ltsf_charges` dropped a dead `snapshot_date`; phantom restock columns removed; ads `_meta.report_type` drift corrected.

## [0.2.0] — 2026-05-13

### Added

- **report-data** — Amazon SP-API + Ads-API report querying via the SellerSheet warehouse. 50+ `rpt_*` table schema references (one JSON per table with `db_column`, `amazon_header`, `type`, business notes, calibration provenance, example query). SKILL.md covers cron-sync vs manual-flow paths, multi-marketplace store resolution, `disabled_reason` interpretation, and the create-poll-download workflow.

## [0.1.0] — 2026-05-12

Initial public release. Two production-ready skills for working in Google Sheets via SellerSheet MCP, both validated end-to-end with live builds.

### Added

- **sellersheet-sheets** — Google Sheets I/O via SellerSheet MCP. Self-contained — production-quality conventions for color, number formats, formulas, and layout inlined. 10 reference files + 3 scripts files.
- **sellersheet-dashboard** — Multi-tab operator dashboards with freshness/provenance/agent-insight system. 12 reference files + 3 scripts files, including agent-maintenance workflow and per-data-scope SQL LIMITs. Builds on `sellersheet-sheets`.
- **Cross-platform install script** (`install.sh`) — auto-detects Claude Code, Claude Desktop, Codex, Gemini CLI, Antigravity; supports generic `--target` + `--path` flags for Openclaw, Hermes, and custom agents.
- **Claude Code plugin marketplace manifest** (`.claude-plugin/marketplace.json`).
- **MCP server config snippet** (`mcp/sellersheet.json`) for Claude Desktop / Codex / Gemini / Antigravity.
- **Per-platform install docs** for Claude Code, Claude Desktop, Codex, Gemini CLI, Antigravity, and generic agents (Openclaw, Hermes, etc.).

### Sanitized

- All examples use generic placeholders (`myStore-US`, `SKU-ABC`, `B0ABCDEFGH`) — no real store IDs, SKUs, ASINs, or workbook URLs from the development builds.

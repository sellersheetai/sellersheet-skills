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

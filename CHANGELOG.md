# Changelog

All notable changes to SellerSheet Skills are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Planned for upcoming releases (under review):
- `sellersheet` — Amazon business operations orchestrator
- `amazon-api` — Amazon SP-API guide
- `amazon-ads` — Amazon Advertising operations
- `fba-inbound` — FBA inbound shipment workflow
- `listing-optimizer` — Full agent-orchestrated listing optimization
- `listing-refurbish` — FBA ASIN migration
- `amazon-listing-optimizer` — Multi-market listing optimization

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

# Changelog

All notable changes to SellerSheet Skills are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Planned for upcoming releases (under review):
- `sellersheet` — Amazon business operations orchestrator
- `amazon-api` — Amazon SP-API guide
- `amazon-ads` — Amazon Advertising operations
- `report-data` — SP-API report querying + 40+ rpt_* table schemas
- `fba-inbound` — FBA inbound shipment workflow
- `listing-optimizer` — Full agent-orchestrated listing optimization
- `listing-refurbish` — FBA ASIN migration
- `amazon-listing-optimizer` — Multi-market listing optimization

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

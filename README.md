# SellerSheet Skills

> Production-ready agent skills for Amazon sellers using [SellerSheet](https://sellersheetai.com). Skills work across Claude Code, Claude Desktop, Codex, Gemini CLI, Antigravity, Openclaw, Hermes, and any agent that scans a skill directory.

**Author**: [sellersheetai.com](https://sellersheetai.com)
**License**: Apache-2.0
**Latest release**: v0.1.0 ([changelog](./CHANGELOG.md))

## What's in here

Three production-ready skills for working with the SellerSheet MCP. More skills coming after their reviews complete.

| Skill | What it does |
|---|---|
| **sellersheet-sheets** | Google Sheets I/O via SellerSheet MCP — reads, writes, formats, builds reports, dashboards, financial models with brand palette + live `SQL()` + image-thumbnail patterns. Self-contained — production-quality conventions for color, number formats, formulas, and layout are inlined. |
| **sellersheet-dashboard** | Multi-tab operator dashboards with freshness instrumentation, agent insights, status tabs — for inventory, PPC, account health, listings, profit/margin, returns, buy box, cash conversion. Builds on `sellersheet-sheets`. |
| **report-data** | Amazon SP-API + Ads-API report querying — 50+ `rpt_*` tables in the SellerSheet warehouse (inventory, listings, orders, returns, financial, brand analytics, ads SP/SB/SD), sync-schedule monitoring, on-demand report flow (create → poll → download to Drive). Use for inventory levels, restock needs, search terms, settlements, listing status, and any synced-report question. |

### Coming soon (under review)

- `sellersheet` — Amazon business operations orchestrator
- `amazon-api` — Amazon SP-API guide
- `amazon-ads` — Amazon Advertising operations
- `fba-inbound` — FBA inbound shipment workflow
- `listing-optimizer` — Full listing optimization
- `listing-refurbish` — FBA ASIN migration
- `amazon-listing-optimizer` — Multi-market listing optimization

These will land in subsequent releases once review completes. Track [CHANGELOG](./CHANGELOG.md) for additions.

## Prerequisites

Before installing, confirm:

1. **A SellerSheet account** at [sellersheetai.com](https://sellersheetai.com).
2. **At least one Amazon store connected** in your SellerSheet workspace.
3. **SellerSheet MCP** configured in your agent. See `mcp/sellersheet.json` for the config snippet.

For the dashboard skill specifically, if you want PPC tabs to populate with real data, the connected store needs **Amazon Advertising profile access** authorized in SellerSheet at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Stores → Connect Advertising. Without it, ad-related sections render as scaffolds.

## Install

### Claude Code (recommended)

```
/plugin marketplace add sellersheetai/sellersheet-skills
/plugin install sellersheet-sheets@sellersheet-skills
/plugin install sellersheet-dashboard@sellersheet-skills
/plugin install report-data@sellersheet-skills
```

Or install all three at once via the marketplace UI (`/plugin` → SellerSheet Skills).

### Claude Desktop

1. Add the SellerSheet MCP server to your config:

```bash
# macOS
cat mcp/sellersheet.json >> ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Linux
cat mcp/sellersheet.json >> ~/.config/Claude/claude_desktop_config.json
# Windows (PowerShell)
Get-Content mcp\sellersheet.json >> "$env:APPDATA\Claude\claude_desktop_config.json"
```

2. Restart Claude Desktop.

3. Install skills:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target claude-desktop
```

### Codex, Gemini CLI, Antigravity

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target <agent>
```

Where `<agent>` is `codex`, `gemini`, or `antigravity`. The install script auto-detects the agent's skill directory; pass `--path <dir>` to override.

### Openclaw, Hermes, custom agents

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target openclaw --path /your/openclaw/skills/dir
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target hermes  --path /your/hermes/skills/dir
```

For any agent that scans a directory for skill folders (each containing a `SKILL.md`), point `--path` at that directory.

### Selective install — only one skill

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --skills "sellersheet-sheets"
```

### Manual install (any platform)

```bash
git clone https://github.com/sellersheetai/sellersheet-skills.git
cp -r sellersheet-skills/skills/* <your-agent-skills-directory>/
```

## Update

```bash
# Claude Code
/plugin update sellersheet-skills

# Anywhere else (re-runs install with current latest)
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --update
```

## Version compatibility

| Skill release | SellerSheet MCP minimum | Agent compatibility |
|---|---|---|
| v0.1.x | 2025-Q4 build | Claude Code 1.0+, Claude Desktop 0.10+, Codex CLI any, Gemini CLI 0.5+, Antigravity any |

Each individual skill carries its own version in its `SKILL.md` frontmatter for skill-level pinning.

## Documentation

- [Install on Claude Code](./docs/install-claude-code.md)
- [Install on Claude Desktop](./docs/install-claude-desktop.md)
- [Install on Codex](./docs/install-codex.md)
- [Install on Gemini CLI](./docs/install-gemini.md)
- [Install on Antigravity](./docs/install-antigravity.md)
- [Install on Openclaw / Hermes / generic agents](./docs/install-generic.md)

## Contributing

Issues and PRs welcome. Skills follow these conventions:

- **`SKILL.md` at root** with frontmatter (`name`, `description`, optional `version`).
- **`reference/`** for heavy detail (schemas, error tables, color palettes) — files referenced from `SKILL.md`.
- **`scripts/`** for copy-paste templates and verification routines.
- Examples should be **generic** — use `myStore-US` placeholders, not real store IDs; `SKU-ABC` not real seller SKUs; `B0ABCDEFGH` not real ASINs.
- Test against the latest SellerSheet MCP build before submitting.

## Support

- Issues: [github.com/sellersheetai/sellersheet-skills/issues](https://github.com/sellersheetai/sellersheet-skills/issues)
- Discussions: [github.com/sellersheetai/sellersheet-skills/discussions](https://github.com/sellersheetai/sellersheet-skills/discussions)
- Email: support@sellersheetai.com

## License

Apache-2.0 — see [LICENSE](./LICENSE).

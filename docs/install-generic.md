# Install on Openclaw / Hermes / generic agents

This guide covers any agent platform that:

1. Scans a directory for skill folders, where each folder contains a `SKILL.md` with YAML frontmatter (`name`, `description`).
2. Connects to MCP servers via a `mcpServers` JSON config.

Openclaw, Hermes, and most newer agent platforms fit this pattern.

## Prerequisites

- Your agent's skill-scan directory (e.g., `/opt/openclaw/skills/`, `/srv/hermes/skills/`)
- Your agent's MCP config file
- SellerSheet API key from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Step 1: Add the MCP server

Add this to your agent's MCP config:

```json
{
  "mcpServers": {
    "sellersheet": {
      "command": "npx",
      "args": ["-y", "@sellersheet/mcp-server"],
      "env": {
        "SELLERSHEET_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

## Step 2: Install the skills to your agent's path

```bash
# Openclaw example
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) \
  --target openclaw --path /opt/openclaw/skills

# Hermes example
bash <(curl -fsSL ...install.sh) --target hermes --path /srv/hermes/skills

# Any directory
bash <(curl -fsSL ...install.sh) --target generic --path /your/custom/path
```

This copies all 10 skills to the specified directory. Each lands as its own folder:

```
/your/path/
├── sellersheet/
├── sellersheet-sheets/
├── sellersheet-dashboard/
├── amazon-api/
├── amazon-ads/
├── report-data/
├── fba-inbound/
├── listing-optimizer/
├── listing-refurbish/
└── amazon-listing-optimizer/
```

## Step 3: Restart your agent

Restart so it scans the skill directory and registers the new skills.

## Selective install

Install only specific skills:

```bash
bash <(curl -fsSL ...install.sh) \
  --target openclaw \
  --path /opt/openclaw/skills \
  --skills "sellersheet sellersheet-sheets sellersheet-dashboard"
```

## Update

```bash
bash <(curl -fsSL ...install.sh) --target openclaw --path /opt/openclaw/skills --update
```

Updates re-pull the latest from GitHub and overwrite the installed skill folders.

## What if my agent doesn't auto-load MCP servers from a file?

Some agents require runtime registration. Consult your agent's docs for the MCP setup procedure. The `sellersheet` MCP server is provided as the same npm package across all agents — the only difference is where the registration lives.

## What if my agent expects a different skill format?

The standard format here is:
- `<skill-name>/SKILL.md` — YAML frontmatter (`name`, `description`) + markdown body
- `<skill-name>/reference/` — heavy reference files (optional)
- `<skill-name>/scripts/` — copy-paste templates and routines (optional)

If your agent expects a different layout (e.g., a single `skill.yaml` file, or skills bundled into one file), you can:
1. Convert manually — copy the relevant `SKILL.md` content into your agent's required format
2. Open an issue at [github.com/sellersheetai/sellersheet-skills/issues](https://github.com/sellersheetai/sellersheet-skills/issues) requesting a build target

## Notes for multi-agent project repos (e.g., Openclaw)

If you're running an internal multi-agent project (sub-agents like fba-agent, ppc-agent, etc.), point each sub-agent's skill-scan path at the same `/your/path/` directory so they all benefit from the same skill base. Sub-agents can use selective `--skills` install if they only need a subset.

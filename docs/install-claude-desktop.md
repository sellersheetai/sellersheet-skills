# Install on Claude Desktop

## Prerequisites

- Claude Desktop 0.10+
- A SellerSheet account with at least one Amazon store connected — no API key needed

## Step 1: Add the MCP server (custom connector)

SellerSheet MCP is a hosted remote server — nothing to install locally.

1. Claude Desktop → **Settings → Connectors → Add custom connector**
2. URL: `https://sellersheetai.com/mcp`
3. Sign in via the OAuth prompt and approve — access is scoped to your stores.

## Step 2: Install the skills

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target claude-desktop
```

This auto-detects the skills directory:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/skills/` |
| Linux | `~/.config/Claude/skills/` |
| Windows | `%APPDATA%/Claude/skills/` |

## Step 3: Restart Claude Desktop

Fully quit Claude Desktop (not just close the window) and relaunch.

## Verify

In a new conversation, ask:

> "What skills do you have available for Amazon ops?"

Claude should list `sellersheet-sheets`, `sellersheet-dashboard`, and `report-data`.

Try a real test:

> "Pull my inventory health for myStore-US and tell me which SKUs need restocking."

Claude should call `get_user_context`, then `query_report_data` via the `report-data` skill.

## Selective install

```bash
bash <(curl -fsSL ...install.sh) --target claude-desktop --skills "sellersheet-dashboard report-data"
```

## Update

```bash
bash <(curl -fsSL ...install.sh) --target claude-desktop --update
```

## Troubleshooting

- **MCP server not connecting**: remove and re-add the connector (Settings → Connectors), completing the OAuth sign-in.
- **Skills don't appear**: confirm Claude Desktop scans the path above. Some Claude Desktop versions require enabling skills in Settings → Features → Skills.
- **Connector authorization revoked**: re-add the connector, or manage access at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → **MCP & API keys**.

# Install on Claude Desktop

## Prerequisites

- Claude Desktop 0.10+
- SellerSheet API key from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Step 1: Add the MCP server config

Open your Claude Desktop config file:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%/Claude/claude_desktop_config.json` |

Merge this block into the `mcpServers` section (or add the section if missing):

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

Replace `YOUR_API_KEY` with your key from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard).

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

- **MCP server not connecting**: check that `npx @sellersheet/mcp-server --help` runs in your terminal. If not, install Node.js 18+.
- **Skills don't appear**: confirm Claude Desktop scans the path above. Some Claude Desktop versions require enabling skills in Settings → Features → Skills.
- **API key rejected**: regenerate at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Settings → API.

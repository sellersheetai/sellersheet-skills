# Install on Codex CLI

## Prerequisites

- Codex CLI installed
- SellerSheet API key from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Step 1: Add the MCP server

Open or create `~/.codex/mcp.json` and add:

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

## Step 2: Install the skills

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target codex
```

This copies skills to `~/.codex/skills/`.

If your Codex install uses a different path, override:

```bash
bash <(curl -fsSL ...install.sh) --target codex --path /your/path
```

## Step 3: Restart Codex

```bash
codex restart
```

(Or close and reopen if running interactively.)

## Verify

```
codex run "list available skills"
```

Should include the sellersheet-* skills.

## Update

```bash
bash <(curl -fsSL ...install.sh) --target codex --update
```

## Troubleshooting

- **Codex doesn't see the skills**: check Codex's documented skill discovery path; pass it via `--path`.
- **MCP server fails to start**: confirm Node.js 18+ is installed and `npx @sellersheet/mcp-server` runs from a normal terminal.

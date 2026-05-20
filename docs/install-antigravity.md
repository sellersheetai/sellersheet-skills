# Install on Antigravity

> **Recommended:** the quickest install is [`npx skills`](./install-npx-skills.md) — `npx skills add sellersheetai/sellersheet-skills -a antigravity`, one command across 50+ agents. The `install.sh` steps below are the no-Node fallback.

## Prerequisites

- Antigravity agent runtime installed
- SellerSheet API key from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Step 1: Add the MCP server

Open or create `~/.antigravity/mcp.json` (or wherever your Antigravity install reads MCP servers from):

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
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target antigravity
```

This copies skills to `~/.antigravity/skills/`.

If Antigravity uses a different path, override:

```bash
bash <(curl -fsSL ...install.sh) --target antigravity --path /your/path
```

## Step 3: Restart Antigravity

Restart the agent runtime to pick up the new skills.

## Verify

Trigger any sellersheet skill via a natural-language phrase ("build me an operator dashboard for myStore-US"). The agent should load the relevant skill from the installed directory.

## Update

```bash
bash <(curl -fsSL ...install.sh) --target antigravity --update
```

## Notes

Antigravity is a newer agent platform — its skill discovery mechanism may evolve. If the default path isn't where your install scans, pass `--path <correct/path>` to the installer. The skill format (`SKILL.md` + `reference/` + `scripts/`) is portable across any agent that reads markdown skill files.

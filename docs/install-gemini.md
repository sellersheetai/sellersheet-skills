# Install on Gemini CLI

> **Recommended:** the quickest install is [`npx skills`](./install-npx-skills.md) — `npx skills add sellersheetai/sellersheet-skills -a gemini`, one command across 50+ agents. The `install.sh` steps below are the no-Node fallback.

## Prerequisites

- Gemini CLI 0.5+
- SellerSheet API key from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Step 1: Add the MCP server

Open or create `~/.gemini/mcp.json`:

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
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target gemini
```

This copies skills to `~/.gemini/skills/`.

## Step 3: Activate skills

Gemini CLI loads skill metadata at session start. You may need to register the skill directory:

```bash
gemini config set skills.path ~/.gemini/skills
```

Then activate per skill via Gemini's `activate_skill` tool when you want it loaded, or set auto-activate on triggering phrases:

```bash
gemini config set skills.auto_activate true
```

## Verify

```
gemini chat "list active skills"
```

Should include `sellersheet-sheets`, `sellersheet-dashboard`, and `report-data`.

## Update

```bash
bash <(curl -fsSL ...install.sh) --target gemini --update
```

## Troubleshooting

- **Skills don't activate**: confirm `~/.gemini/config.json` has `skills.path` set correctly.
- **MCP server not detected by Gemini**: some Gemini CLI versions need an explicit `--mcp-config ~/.gemini/mcp.json` flag.

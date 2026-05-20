# Setting up SellerSheet MCP

The SellerSheet skills (`sellersheet-sheets`, `sellersheet-dashboard`, `report-data`, …) all run through the **SellerSheet MCP server**. Without it, none of these skills can call Amazon or write to your Google Sheets. This page is the canonical walkthrough.

## Three things you need

1. **A SellerSheet account.** Free trial at [sellersheetai.com](https://sellersheetai.com).
2. **An API key.** From [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Settings → API → "Create new key". Copy it. Treat it like a password — anyone with this key can call SP-API on your stores.
3. **MCP server registered in your agent.** Configuration shape (same across all agents):

```json
{
  "mcpServers": {
    "sellersheet": {
      "command": "npx",
      "args": ["-y", "@sellersheet/mcp-server"],
      "env": {
        "SELLERSHEET_API_KEY": "PASTE_YOUR_KEY_HERE"
      }
    }
  }
}
```

The location of this config differs per agent:

| Agent | Config file path |
|---|---|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Linux) | `~/.config/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%/Claude/claude_desktop_config.json` |
| Claude Code | `~/.claude/mcp.json` or `/mcp add` interactive command |
| Codex CLI | `~/.codex/mcp.json` |
| Gemini CLI | `~/.gemini/mcp.json` |
| Antigravity | `~/.antigravity/mcp.json` |
| Openclaw / Hermes / generic | per the agent's docs — the `mcpServers` block is universal |

> **Claude Code shortcut:** if you install `sellersheet-skills` as a plugin (`/plugin install sellersheet-skills@sellersheet-marketplace`), the plugin ships its own `.mcp.json` and registers the `sellersheet` server for you — you skip the manual config above. Just expose your key as an environment variable instead of pasting it into JSON: `export SELLERSHEET_API_KEY="your-key"`. See [install-claude-code.md](./install-claude-code.md).

## After installing MCP — install the skills

Skills are a separate artifact from the MCP server. Pick the path that fits your agent:

| Agent | Install command |
|---|---|
| **Claude Code** | `/plugin marketplace add sellersheetai/sellersheet-skills` then `/plugin install sellersheet-skills@sellersheet-marketplace` (one bundle, all three skills) |
| **Other agents** | `bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target <agent>` |

After both MCP and skills are installed, restart your agent.

## Verify

In your agent, ask: *"Show me my SellerSheet user context."*

Expected outcome: the agent calls `get_user_context`, returns your profile, stores, plan, and `skills_catalog`. If you see this, MCP is working.

If you instead see "tool not found" or "unauthorized": one of the three setup pieces is incomplete. The most common cause is forgetting to restart the agent after editing the MCP config.

## Keeping skills up to date

**Claude Code** — enable marketplace auto-update once (third-party marketplaces are opt-in), then new releases install themselves:

```
/plugin   →   Marketplaces tab   →   sellersheet-marketplace   →   Enable auto-update
```

Or update on demand: `/plugin marketplace update sellersheet-marketplace` then `/plugin update sellersheet-skills`.

**Other agents** — re-run the installer with `--update`, or `--check` to compare installed vs latest:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --update
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --check
```

The full mechanism — version resolution, the `extraKnownMarketplaces` snippet, and the maintainer release flow — is in [auto-update.md](./auto-update.md).

## Common setup failures

| Symptom | Fix |
|---|---|
| Agent says "SellerSheet MCP isn't connected" right after restart | Re-check the config file is in the right path for your agent (table above). Some Claude Desktop installs use a different path on Windows than expected. |
| `get_user_context` returns "unauthorized" | API key is wrong or has been revoked. Generate a new one at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Settings → API. |
| `get_user_context` returns "tool not found" | The MCP server didn't start. Check `npx @sellersheet/mcp-server` runs from your terminal; install Node.js 18+ if missing. |
| `get_user_context` succeeds but says "no stores" | Connect at least one Amazon store at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Stores → Connect Amazon. |
| Agent says skill is outdated every session even after updating | Some agents cache the skill index. Run `/skills refresh` (Claude Code) or fully restart the agent. |
| PPC sections show as scaffolds (empty) | Authorize Amazon Advertising profile access at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Stores → Connect Advertising. |

## Support

- Issues: [github.com/sellersheetai/sellersheet-skills/issues](https://github.com/sellersheetai/sellersheet-skills/issues)
- Email: support@sellersheetai.com
- Dashboard: [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

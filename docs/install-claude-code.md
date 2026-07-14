# Install on Claude Code

## Prerequisites

- Claude Code 1.0+
- A SellerSheet API key from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → **MCP & API keys** → **Create Key**
- At least one Amazon store connected at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Option A — Plugin marketplace (recommended)

```
/plugin marketplace add sellersheetai/sellersheet-skills
/plugin install sellersheet-skills@sellersheet-marketplace
```

`sellersheet-skills` is a single plugin that bundles every skill in the repo (see the [README skill table](../README.md#whats-in-here)). There is no per-skill install; one `/plugin install` gets the whole bundle.

The plugin installs **skills only** — it does **not** register the MCP server (versions ≤0.5.0 bundled a broken `.mcp.json`; it was removed in 0.5.1). Register the MCP server as a separate step:

```bash
claude mcp add-json sellersheet '{"type":"http","url":"https://sellersheetai.com/mcp","headers":{"Authorization":"Bearer YOUR_API_KEY"}}'
```

SellerSheet MCP is a hosted remote server — nothing runs locally. The dashboard's **Use key** dialog renders this command with your key filled in.

### Keep it current

Third-party marketplaces don't auto-update by default. Enable it once:

```json
// ~/.claude/settings.json
{
  "extraKnownMarketplaces": {
    "sellersheet-marketplace": {
      "source": { "source": "github", "repo": "sellersheetai/sellersheet-skills" },
      "autoUpdate": true
    }
  }
}
```

Or update on demand: `/plugin marketplace update sellersheet-marketplace` then `/plugin update sellersheet-skills`. Full detail in [auto-update.md](./auto-update.md).

## Option B — Direct install (no marketplace)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh)
```

This auto-detects `~/.claude/skills/` and copies the skill folders into it. It does **not** register the MCP server — add it yourself per [setup-mcp.md](./setup-mcp.md). Restart Claude Code to pick up the new skills.

## Option C — Manual install

```bash
git clone https://github.com/sellersheetai/sellersheet-skills.git ~/projects/sellersheet-skills
cp -r ~/projects/sellersheet-skills/skills/* ~/.claude/skills/
```

## Verify

In Claude Code, the available-skills list should now include `sellersheet-sheets`, `sellersheet-dashboard`, and `report-data`.

Run `/mcp` — `sellersheet` should appear as a connected server. Then try a triggering phrase:

```
"build me an FBA dashboard for myStore-US"
```

Claude Code should invoke `sellersheet-dashboard` via the `Skill` tool.

## Troubleshooting

- **Skill not appearing**: restart Claude Code or run `/reload-plugins`. The skill index is built on startup.
- **`sellersheet` MCP not connected**: the plugin doesn't register it — run the `claude mcp add-json` command above, then restart Claude Code.
- **`get_user_context` returns "no stores"**: connect a store at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard).
- **PPC tabs are empty**: authorize Amazon Advertising profile access at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → My Stores → the **Authorize Ads** button on the store's row.

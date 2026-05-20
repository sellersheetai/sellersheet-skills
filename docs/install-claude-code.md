# Install on Claude Code

## Prerequisites

- Claude Code 1.0+
- A SellerSheet API key from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Settings → API
- At least one Amazon store connected at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Option A — Plugin marketplace (recommended)

```
/plugin marketplace add sellersheetai/sellersheet-skills
/plugin install sellersheet-skills@sellersheet-marketplace
```

`sellersheet-skills` is a single plugin that bundles all three skills — `sellersheet-sheets`, `sellersheet-dashboard`, and `report-data`. There is no per-skill install; one `/plugin install` gets the whole bundle.

The plugin also ships a `.mcp.json`, so installing it **auto-registers the SellerSheet MCP server**. You only need to expose your API key to Claude Code's environment:

```bash
# add to ~/.zshrc / ~/.bashrc, then restart your shell + Claude Code
export SELLERSHEET_API_KEY="your-key-from-sellersheetai.com/dashboard"
```

If you previously added a `sellersheet` MCP server to `~/.claude/mcp.json` by hand, you can remove that entry — the plugin now provides it.

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
- **`sellersheet` MCP not connected**: confirm `SELLERSHEET_API_KEY` is exported in the environment Claude Code launched from (`echo $SELLERSHEET_API_KEY`). Restart Claude Code after setting it.
- **`get_user_context` returns "no stores"**: connect a store at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard).
- **PPC tabs are empty**: authorize Amazon Advertising profile access at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Stores → Connect Advertising.

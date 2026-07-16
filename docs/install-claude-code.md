# Install on Claude Code

## Prerequisites

- Claude Code 1.0+
- At least one Amazon store connected at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Install (plugin marketplace)

```
/plugin marketplace add sellersheetai/sellersheet-skills
/plugin install sellersheet-skills@sellersheet-marketplace
```

`sellersheet-skills` is a single plugin that bundles every skill in the repo (see the [README skill table](../README.md#whats-in-here)). There is no per-skill install; one `/plugin install` gets the whole bundle.

Since v0.11.0 the plugin also bundles the **SellerSheet MCP server** (a keyless remote-HTTP
`.mcp.json` — nothing runs locally), so one install gets skills + MCP. Authenticate once:
run `/mcp`, select the `sellersheet` server (listed as `plugin:sellersheet-skills:sellersheet`),
and sign in via the browser OAuth prompt. No API key needed.

If you already added a `sellersheet` MCP server manually, yours wins — the plugin's copy is
shadowed automatically, nothing breaks. Prefer a static API key instead of OAuth? Keep your
manual entry (dashboard → **MCP & API keys** → **Use key** renders it with the key filled in).

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

## Verify

In Claude Code, the available-skills list should now include `sellersheet-sheets`, `sellersheet-dashboard`, and `report-data`.

Run `/mcp` — `sellersheet` should appear as a connected server. Then try a triggering phrase:

```
"build me an FBA dashboard for myStore-US"
```

Claude Code should invoke `sellersheet-dashboard` via the `Skill` tool.

## Troubleshooting

- **Skill not appearing**: restart Claude Code or run `/reload-plugins`. The skill index is built on startup.
- **`sellersheet` MCP shows Needs authentication**: run `/mcp`, select it, complete the browser sign-in.
- **`get_user_context` returns "no stores"**: connect a store at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard).
- **PPC tabs are empty**: authorize Amazon Advertising profile access at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → My Stores → the **Authorize Ads** button on the store's row.

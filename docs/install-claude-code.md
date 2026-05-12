# Install on Claude Code

## Prerequisites

- Claude Code 1.0+
- SellerSheet MCP server installed and connected (`get_user_context` returns your profile)
- At least one Amazon store connected at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Option A — Plugin Marketplace (recommended)

```
/plugin marketplace add sellersheetai/sellersheet-skills
/plugin install sellersheet sellersheet-sheets sellersheet-dashboard
```

To install all skills at once:

```
/plugin install sellersheet sellersheet-sheets sellersheet-dashboard \
                amazon-api amazon-ads report-data fba-inbound \
                listing-optimizer listing-refurbish amazon-listing-optimizer
```

Updates:

```
/plugin update sellersheet-skills
```

## Option B — Direct install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh)
```

This auto-detects `~/.claude/skills/` and copies the skill folders into it. Restart Claude Code or run `/skills refresh` to pick up new skills.

## Option C — Manual install

```bash
git clone https://github.com/sellersheetai/sellersheet-skills.git ~/projects/sellersheet-skills
cp -r ~/projects/sellersheet-skills/skills/* ~/.claude/skills/
```

## Verify

In Claude Code, the available-skills list should now include `sellersheet`, `sellersheet-sheets`, `sellersheet-dashboard`, etc.

Try a triggering phrase:

```
"build me an FBA dashboard for myStore-US"
```

Claude Code should invoke `sellersheet-dashboard` via the `Skill` tool.

## Selective install

If you only want specific skills:

```bash
bash <(curl -fsSL ...install.sh) --skills "sellersheet sellersheet-sheets sellersheet-dashboard"
```

## Update vs reinstall

```bash
# Update to latest
bash <(curl -fsSL ...install.sh) --update

# Or via Claude Code if installed as plugin
/plugin update sellersheet-skills
```

## Troubleshooting

- **Skill not appearing**: restart Claude Code. The skill index is built on startup.
- **SellerSheet MCP not connected**: check `~/.claude/mcp.json` has the SellerSheet entry. See `mcp/sellersheet.json` in the repo for the snippet.
- **`get_user_context` returns "no stores"**: connect a store at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard).
- **PPC tabs are empty**: authorize Amazon Advertising profile access at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → Stores → Connect Advertising.

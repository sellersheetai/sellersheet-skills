# Install on Codex CLI / ChatGPT desktop

Codex reads the same plugin marketplace format as Claude Code (`.claude-plugin/marketplace.json`), so the native plugin install is the recommended path — one repo serves both agents.

## Prerequisites

- Codex CLI (standalone, or the one bundled in the ChatGPT desktop app)
- A SellerSheet account with at least one Amazon store connected — no API key needed for the OAuth path below

## Step 1: Install the skills (plugin)

```bash
codex plugin marketplace add sellersheetai/sellersheet-skills
codex plugin add sellersheet-skills@sellersheet-marketplace
```

Verify with `codex plugin list` — you should see `sellersheet-skills@sellersheet-marketplace  installed, enabled`.

## Step 2: Add the MCP server

One command — no API key, no config editing:

```bash
codex mcp add sellersheet --url https://sellersheetai.com/mcp
```

A browser window opens — sign in to SellerSheet and approve. `codex mcp list` should then show `sellersheet | enabled | Auth: OAuth`.

<details>
<summary>Alternative: Bearer key instead of OAuth</summary>

If you prefer a static API key (from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → **MCP & API keys** → **Create Key**), edit `~/.codex/config.toml`:

```toml
[mcp_servers.sellersheet]
url = "https://sellersheetai.com/mcp"
http_headers = { "Authorization" = "Bearer YOUR_API_KEY" }
```

Note the field is **`http_headers`** — `headers` is silently ignored. Or keep the key out of the file entirely: `codex mcp add sellersheet --url https://sellersheetai.com/mcp --bearer-token-env-var SELLERSHEET_API_KEY`.

</details>

## Step 3: Restart Codex

Start a new session (or restart the ChatGPT desktop app) so the plugin's skills load.

## Verify

Ask Codex: *"Show me my SellerSheet user context."* It should call `get_user_context` and return your stores and plan.

## Update

```bash
codex plugin marketplace upgrade sellersheet-marketplace
```

## Troubleshooting

- **`get_user_context` not found**: the MCP server isn't registered — re-run Step 2, then start a new session.
- **Manual `config.toml` entry not picked up**: check you used `http_headers`, not `headers`.
- **Plugin installed but skills don't trigger**: start a fresh session; plugins load at session start.

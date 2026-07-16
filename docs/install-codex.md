# Install on Codex CLI / ChatGPT desktop

Codex reads the same plugin marketplace format as Claude Code (`.claude-plugin/marketplace.json`), so the native plugin install is the recommended path — one repo serves both agents.

## Prerequisites

- Codex CLI (`npm i -g @openai/codex`) — shares `~/.codex` with the ChatGPT desktop app
- A SellerSheet account with at least one Amazon store connected — no API key needed

## Step 1: Install the plugin (skills + MCP in one)

```bash
codex plugin marketplace add sellersheetai/sellersheet-skills
codex plugin add sellersheet-skills@sellersheet-marketplace
```

The plugin bundles the SellerSheet MCP server (keyless remote-HTTP `.mcp.json`), so
`codex mcp list` now shows `sellersheet | enabled | Not logged in` with no extra step.
Verify skills with `codex plugin list` — `sellersheet-skills@sellersheet-marketplace  installed, enabled`.

## Step 2: Sign in

```bash
codex mcp login sellersheet
```

A browser window opens — sign in to SellerSheet and approve. No API key.

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

# Setting up SellerSheet MCP

The SellerSheet skills (`sellersheet-sheets`, `sellersheet-dashboard`, `report-data`, …) all run through the **SellerSheet MCP server**. Without it, none of these skills can call Amazon or write to your Google Sheets. This page is the canonical walkthrough.

## Three things you need

1. **A SellerSheet account.** Free trial at [sellersheetai.com](https://sellersheetai.com).
2. **A connection credential.** OAuth clients (Claude Desktop connectors, `codex mcp add`) need **no key** — a browser sign-in scopes access to your stores. Every other client needs an **API key** from [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → **MCP & API keys** → **Create Key**. Treat it like a password — anyone with this key can call SP-API on your stores.
3. **MCP server registered in your agent.** SellerSheet MCP is a **hosted remote server** (streamable HTTP) at `https://sellersheetai.com/mcp` — there is nothing to install locally. Generic configuration shape:

```json
{
  "mcpServers": {
    "sellersheet": {
      "type": "http",
      "url": "https://sellersheetai.com/mcp",
      "headers": { "Authorization": "Bearer YOUR_API_KEY" }
    }
  }
}
```

Per-agent registration:

| Agent | How to register |
|---|---|
| Claude Desktop | Settings → Connectors → **Add custom connector** → URL `https://sellersheetai.com/mcp` (OAuth — no key needed) |
| Claude Code | `claude mcp add-json sellersheet '{"type":"http","url":"https://sellersheetai.com/mcp","headers":{"Authorization":"Bearer YOUR_API_KEY"}}'` |
| Codex CLI / ChatGPT desktop | `codex mcp add sellersheet --url https://sellersheetai.com/mcp` — a browser window opens for OAuth on first use; **no key needed**. (Manual `config.toml`: the header field is `http_headers`, not `headers`.) |
| Cursor | `~/.cursor/mcp.json` — the JSON block above without the `"type"` field |
| Windsurf / Antigravity | Same block but with `"serverUrl"` instead of `"url"` |
| Gemini CLI | `~/.gemini/settings.json` — `httpUrl` + `headers` |
| Openclaw / Hermes / generic | Any MCP client with streamable-HTTP support: URL + `Authorization: Bearer` header |

The dashboard's **Use key** dialog ([sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → MCP & API keys) renders a ready-to-paste snippet for each of these clients with your key filled in.

> **Note:** installing the `sellersheet-skills` plugin does **not** register the MCP server — MCP and skills are two independent steps, in every agent. (Versions ≤0.5.0 bundled a broken `.mcp.json`; it was removed in 0.5.1.)

## After installing MCP — install the skills

Skills are a separate artifact from the MCP server. Pick the path that fits your agent:

| Agent | Install command |
|---|---|
| **Claude Code** | `/plugin marketplace add sellersheetai/sellersheet-skills` then `/plugin install sellersheet-skills@sellersheet-marketplace` (one bundle, all skills) |
| **Codex CLI / ChatGPT desktop** | `codex plugin marketplace add sellersheetai/sellersheet-skills` then `codex plugin add sellersheet-skills@sellersheet-marketplace` — Codex reads the same marketplace format, so one repo serves both |
| **Other agents** | `npx skills add sellersheetai/sellersheet-skills` — recommended; see [install-npx-skills.md](./install-npx-skills.md). No-Node fallback: `bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target <agent>` |

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
| `get_user_context` returns "unauthorized" | API key is wrong or has been revoked. Generate a new one at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → **MCP & API keys** → **Create Key**. |
| `get_user_context` returns "tool not found" | The server wasn't registered (wrong config path or field name — e.g. Codex `config.toml` needs `http_headers`, not `headers`), or the agent wasn't restarted after the config change. |
| `get_user_context` succeeds but says "no stores" | Connect at least one Amazon store at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → My Stores → Connect Amazon. |
| Agent says skill is outdated every session even after updating | Some agents cache the skill index. Run `/skills refresh` (Claude Code) or fully restart the agent. |
| PPC sections show as scaffolds (empty) | Authorize Amazon Advertising profile access at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → My Stores → the **Authorize Ads** button on the store's row. |

## Support

- Issues: [github.com/sellersheetai/sellersheet-skills/issues](https://github.com/sellersheetai/sellersheet-skills/issues)
- Email: support@sellersheetai.com
- Dashboard: [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

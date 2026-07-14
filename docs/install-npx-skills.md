# Install via `npx skills`

[`npx skills`](https://github.com/vercel-labs/skills) is the open cross-agent
skill installer. It installs SellerSheet skills into Codex, Cursor, Gemini CLI,
Antigravity, and 50+ other coding agents from one command — no per-agent setup
script needed.

For **Claude Code** and **Codex**, the plugin marketplace is the best path —
one bundle with built-in update flow; see [install-claude-code.md](./install-claude-code.md)
and [install-codex.md](./install-codex.md). For every other agent, `npx skills`
is the recommended installer; the repo's `install.sh` is the no-Node fallback.

## Prerequisites

- Node.js 18+ (for `npx`)
- A SellerSheet API key — [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard)

## Install the skills

```bash
# Install the full skill bundle, auto-detecting your agent
npx skills add sellersheetai/sellersheet-skills

# Preview what would be installed, without installing
npx skills add sellersheetai/sellersheet-skills --list

# Target a specific agent (codex, cursor, gemini, claude-code, …)
npx skills add sellersheetai/sellersheet-skills -a codex
```

`npx skills` discovers every skill in the repo's `skills/` directory —
`sellersheet-sheets`, `sellersheet-dashboard`, `report-data`, `image-gen`,
`noon-report-data`, `amazon-ads`, `amazon-report`, `data-kiosk`, plus the
`sellersheet-shared` companion — and installs each as a `SKILL.md` skill folder
into your agent's skill path. **Install the whole bundle, not a subset** — the
skills reference `sellersheet-shared` for the common preflight and conventions.

## Register the MCP server

Skills are a separate artifact from the MCP server. `npx skills` installs the
skill *instructions*, not the SellerSheet MCP *connection* — and every skill
needs that connection. Follow [setup-mcp.md](./setup-mcp.md) for the per-agent
`mcpServers` config.

(This applies to every agent — the Claude Code plugin also installs skills
only. See [install-claude-code.md](./install-claude-code.md).)

## Update

Re-run `add` to pull the latest published version:

```bash
npx skills add sellersheetai/sellersheet-skills
```

`npx skills` reads each skill's `SKILL.md` `version:` (mirrored from the
plugin's canonical version). See [auto-update.md](./auto-update.md)
for how versioning works across all install channels.

## Remove

```bash
npx skills remove --all        # remove every installed skill
npx skills remove report-data  # or remove one at a time
```

## When to use `install.sh` instead

If Node.js isn't available, the repo's bundled installer does the same job:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target <agent>
```

See the per-agent guides — [Codex](./install-codex.md), [Gemini](./install-gemini.md),
[Antigravity](./install-antigravity.md), [Openclaw / Hermes / generic](./install-generic.md)
— for `install.sh` details and custom skill-directory paths.

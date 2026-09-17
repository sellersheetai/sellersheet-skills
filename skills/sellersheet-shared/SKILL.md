---
name: sellersheet-shared
description_zh: "所有 SellerSheet 技能的公共约定（MCP 预检、店铺引用格式、响应契约、语言规则、故障排查），运行本套件任一技能前先读本文件。"
description_en: "Common conventions for ALL SellerSheet skills — read this FIRST when running any other skill from this bundle…"
author: SellerSheet AI
description: >-
  Common conventions for ALL SellerSheet skills — read this FIRST when running any other skill from this bundle (sellersheet-sheets, sellersheet-dashboard, report-data, amazon-ads, amazon-report, data-kiosk, noon-report-data, image-gen). Contains the MCP preflight protocol (get_user_context → version check → canUseMcp), store reference rules (name-country format, multi-marketplace stores), the MCP response contract (always relay notification.message + human_action), and setup/troubleshooting. Not a standalone skill — it has no workflows of its own.
  中文说明：所有 SellerSheet 技能的公共约定（MCP 预检、店铺引用格式、响应契约、语言规则、故障排查），运行本套件任一技能前先读本文件。
version: 0.11.12
---

# sellersheet-shared — common conventions

Every SellerSheet skill talks to Amazon, Google Sheets, or noon through the hosted
**SellerSheet MCP server**. This file is the single source of truth for what they
all share; each skill keeps only its own auth deltas (Brand Registry, vendor
account, ads profile, noon account) and domain content.

## Preflight — run before any skill's workflow

1. **Try `get_user_context`** (the MCP tool).
   - ❌ Not in your tool catalog, OR returns an auth error → SellerSheet MCP isn't connected. Surface this to the user verbatim, then STOP until they confirm setup is done:

     > **SellerSheet MCP isn't connected.** To use this skill:
     > 1. Sign in at [sellersheetai.com](https://sellersheetai.com).
     > 2. Follow Setup step 4 on the [dashboard](https://sellersheetai.com/dashboard) — one command per client (Claude, Claude Code, Codex, CodeBuddy Code, and more). OAuth clients need no API key; others create one under **MCP & API keys → Create Key**.
     > 3. Restart your agent and reopen this conversation.

     Per-agent walkthrough: [setup-mcp.md](https://github.com/sellersheetai/sellersheet-skills/blob/main/docs/setup-mcp.md).
   - ✅ Returns a user profile → continue.

2. **Version check.** `get_user_context` returns `data.skills_update` (server-computed). Compare `skills_update.latest` to this bundle's frontmatter `version:` — the whole bundle shares one version, so one comparison covers every skill. If yours is older, tell the user and give them the update command **matching their agent** from `skills_update.commands`: `claude-code-update` (Claude Code), `codex-update` (Codex / ChatGPT desktop), `codebuddy-update` (Tencent CodeBuddy Code / 腾讯云 CodeBuddy), `other-update` (npx-skills agents). Never suggest `install.sh` to a plugin user — it creates a duplicate skill source. Older MCP builds without `skills_update`: fall back to `data.skills_catalog.skills[].latest_version`; missing both → skip silently.

3. **Permissions.** `data.canUseMcp` must be true. If false, surface `data.message` (the blocking issues) and stop.

Then apply the skill's own **extra auth** notes (if any) and proceed.

## Language · 语言规则

- **Reply in the user's language.** A user who writes in Chinese gets Chinese explanations, summaries, and questions (用户用中文提问就用中文回答); a user who writes in English gets English. The skill files are written in English — that is not a signal to answer in English.
- **Keep the machine-facing parts in English, unchanged:** MCP tool names (`get_user_context`, `query_report_data`), store refs (`myStore-US`), table and column names (`rpt_*`), Amazon nouns (SKU, ASIN, FBA, A+, Buy Box, PPC), report and enum values, and every Google Sheet tab name and header. The server reads sheets by their English header names — a translated header breaks the workflow.
- **Relay `notification.message` and `human_action` verbatim** (they arrive in English), then add a one-line explanation in the user's language when it helps.

## Store references

- Always pass `store` as **`store_name-country_code`** (e.g. `myStore-US`). A bare name is ambiguous when the same brand exists in multiple marketplaces.
- Multi-marketplace stores have a comma-separated `country_code` (e.g. `US,CA,MX,BR` or `UK,DE,FR,IT,ES,NL,PL,SE,BE,IE`) — pick ONE target marketplace for the suffix; routes auto-scope data to it.
- `get_user_context` lists every valid store name and its marketplaces — never guess.

## MCP response contract

Every SellerSheet MCP tool returns `{notification, data, human_action}`:

- **Always relay `notification.message` and `human_action` to the user** — they carry Amazon's actual outcome and the expected next step.
- `notification.type: "error"` with a 4xx-style message is usually user-fixable (permissions, bad store ref, missing auth) — surface it, don't retry blindly.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `get_user_context` not found | MCP not registered, or agent not restarted after config change. Redo Preflight step 1's setup. |
| "unauthorized" | API key wrong/revoked → [dashboard](https://sellersheetai.com/dashboard) → **MCP & API keys** → **Create Key**. |
| "no stores" | Connect an Amazon store: dashboard → My Stores → Connect Amazon. |
| Ads tools fail / PPC sections empty | Authorize Amazon Advertising: dashboard → My Stores → **Authorize Ads** on the store's row. |
| Skill flagged outdated every session | Agent caches the skill index — `/reload-plugins` (Claude Code, CodeBuddy Code), new session (Codex), or restart. |

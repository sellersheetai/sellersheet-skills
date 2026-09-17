# Install on Tencent CodeBuddy Code · 腾讯云 CodeBuddy Code 安装指南

CodeBuddy Code reads the same plugin layout as Claude Code — it looks for `.codebuddy-plugin/`, then `.workbuddy-plugin/`, then `.claude-plugin/` — so this repo installs on CodeBuddy unchanged: skills + the SellerSheet MCP server in one step. Verified on CodeBuddy Code 2.151.0.

CodeBuddy Code 与 Claude Code 使用同一套插件目录结构（依次识别 `.codebuddy-plugin/`、`.workbuddy-plugin/`、`.claude-plugin/`），因此本仓库无需改动即可在 CodeBuddy 中安装：一步装好全部技能和 SellerSheet MCP 服务器。已在 CodeBuddy Code 2.151.0 上验证。

## Prerequisites · 前置条件

- CodeBuddy Code installed and signed in (`npm i -g @tencent-ai/codebuddy-code`, then `codebuddy`). If `/plugin` is missing, update CodeBuddy to the latest version.
- A [SellerSheet](https://sellersheetai.com) account with at least one Amazon store connected. No API key is needed for the plugin route.

- 已安装并登录 CodeBuddy Code（`npm i -g @tencent-ai/codebuddy-code`，然后运行 `codebuddy`）。若没有 `/plugin` 命令，请升级到最新版。
- 一个已连接至少一家亚马逊店铺的 [SellerSheet](https://sellersheetai.com) 账号。插件方式安装无需 API key。

## Step 1 — Install the plugin (skills + MCP) · 安装插件（技能 + MCP 一步到位）

Inside a CodeBuddy session · 在 CodeBuddy 会话中输入：

```
/plugin marketplace add sellersheetai/sellersheet-skills
/plugin install sellersheet-skills@sellersheet-marketplace
/reload-plugins
```

Or from a shell, non-interactively · 或在终端中非交互执行：

```bash
codebuddy plugin marketplace add sellersheetai/sellersheet-skills
codebuddy plugin install sellersheet-skills@sellersheet-marketplace
codebuddy plugin list        # → sellersheet-skills@sellersheet-marketplace  Version: 0.11.x  Status: enabled
```

The plugin bundles a keyless remote-HTTP `.mcp.json`, so the `sellersheet` MCP server is registered automatically — nothing runs locally.

插件自带免密的远程 HTTP `.mcp.json`，安装后 `sellersheet` MCP 服务器自动注册，本机不需要运行任何进程。

## Step 2 — Sign in to the MCP server · 登录 MCP 服务器

Run `/mcp`, pick `sellersheet`, and complete the browser sign-in (OAuth — no API key).

运行 `/mcp`，选择 `sellersheet`，在浏览器中完成 SellerSheet 登录授权（OAuth，无需 API key）。

<details>
<summary>Alternative: Bearer API key · 备选：使用 API key</summary>

Create a key at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → **MCP & API keys** → **Create Key**, then:

在 [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → **MCP & API keys** → **Create Key** 创建密钥，然后执行：

```bash
codebuddy mcp add-json --scope user sellersheet '{"type":"http","url":"https://sellersheetai.com/mcp","headers":{"Authorization":"Bearer YOUR_API_KEY"}}'
```

A manually added server with the same name shadows the plugin's copy, so both setups coexist.

手动添加的同名服务器会覆盖插件自带的那一份，两种方式可以共存。

</details>

## Step 3 — Verify · 验证

Ask CodeBuddy · 对 CodeBuddy 说：

> Show me my SellerSheet user context. / 显示我的 SellerSheet 用户信息。

It should call `get_user_context` and return your stores, plan and `skills_catalog`. Plugin skills are namespaced — `/help` lists them as `/sellersheet-skills:report-data`, `/sellersheet-skills:sellersheet-sheets`, and so on. You rarely type these: the skills are model-invoked, so a plain request such as “查一下上周的库存报告” or “build a PPC dashboard” triggers the right one.

它应调用 `get_user_context` 并返回你的店铺、套餐和 `skills_catalog`。插件技能带命名空间前缀，`/help` 中显示为 `/sellersheet-skills:report-data`、`/sellersheet-skills:sellersheet-sheets` 等。通常不需要手动输入：技能由模型按需触发，直接说“查一下上周的库存报告”或“做一个广告看板”即可。

## Update · 更新

```
/plugin marketplace update sellersheet-marketplace
/plugin update sellersheet-skills
/reload-plugins
```

Or enable auto-update once: `/plugin` → **Marketplaces** → **sellersheet-marketplace** → **Enable auto-update**. When `get_user_context` reports a newer bundle, the skills relay the matching `codebuddy-update` command.

也可以一次性开启自动更新：`/plugin` → **Marketplaces** → **sellersheet-marketplace** → **Enable auto-update**。当 `get_user_context` 检测到新版本时，技能会给出对应的 `codebuddy-update` 命令。

## Skills only, no plugin manager · 仅安装技能（不走插件管理器）

If you prefer loose skill folders under `~/.codebuddy/skills/` (no automatic updates, MCP registered by hand per Step 2's alternative):

如果只想把技能放到 `~/.codebuddy/skills/`（无自动更新，MCP 需按上面的备选方式手动注册）：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target codebuddy
```

Do not combine this with the plugin install — two copies of the same skills confuse the model.

不要与插件安装方式同时使用，两份相同的技能会让模型产生混淆。

## Language · 语言

The skill files are written in English, but every skill follows the shared rule: **reply in the user's language.** Ask in Chinese and you get Chinese explanations; tool names, store refs (`myStore-US`), `rpt_*` table names, Amazon nouns (SKU / ASIN / FBA / A+) and Google Sheet headers stay in English because the server reads them by name.

技能文件以英文编写，但所有技能遵循同一条规则：**用用户的语言回答。** 用中文提问就得到中文说明；工具名、店铺引用（`myStore-US`）、`rpt_*` 表名、亚马逊术语（SKU / ASIN / FBA / A+）以及 Google 表格表头保持英文，因为服务器按这些名字读取数据。

## Troubleshooting · 故障排查

| Symptom · 现象 | Fix · 处理 |
|---|---|
| `/plugin` command missing · 没有 `/plugin` 命令 | Update CodeBuddy Code to the latest version. · 升级 CodeBuddy Code 到最新版。 |
| Marketplace add fails · 添加市场失败 | Check network access to github.com; retry with `--debug` for details. · 检查能否访问 github.com；用 `--debug` 查看详细日志。 |
| Skills installed but do not trigger · 技能已安装但不触发 | Run `/reload-plugins` or start a new session; confirm the plugin is enabled under `/plugin` → Installed. · 运行 `/reload-plugins` 或新开会话；在 `/plugin` → Installed 中确认插件已启用。 |
| `get_user_context` not found · 找不到 `get_user_context` | The MCP server is not registered or not signed in — run `/mcp` and complete the OAuth sign-in. · MCP 服务器未注册或未登录，运行 `/mcp` 完成授权。 |
| "unauthorized" | Sign in again via `/mcp`, or create a new key under **MCP & API keys → Create Key**. · 通过 `/mcp` 重新登录，或在 **MCP & API keys → Create Key** 新建密钥。 |
| "no stores" · 没有店铺 | Connect an Amazon store: dashboard → My Stores → Connect Amazon. · 在控制台 My Stores → Connect Amazon 连接店铺。 |

## WorkBuddy

Tencent WorkBuddy (the desktop office agent) installs SellerSheet as a **connector** from its own marketplace, not through `/plugin`. See [install-workbuddy.md](./install-workbuddy.md).

腾讯 WorkBuddy（桌面办公智能体）通过其自带的连接器市场安装 SellerSheet，不走 `/plugin`。见 [install-workbuddy.md](./install-workbuddy.md)。

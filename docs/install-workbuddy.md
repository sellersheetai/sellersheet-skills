# Install on Tencent WorkBuddy · 腾讯 WorkBuddy 安装指南

WorkBuddy is Tencent's desktop office agent. It installs the SellerSheet plugin — the skills **and** the MCP server — from a plugin marketplace: add this GitHub repository as a marketplace, then install the plugin from it.

WorkBuddy 是腾讯的桌面办公智能体。它从插件市场安装 SellerSheet 套件，技能**和** MCP 服务器一起装好：先把本 GitHub 仓库添加为市场，再从中安装套件。

## Prerequisites · 前置条件

- The WorkBuddy desktop app (these steps were checked on 5.9.4).
- A [SellerSheet](https://sellersheetai.com) account with at least one store connected.

- WorkBuddy 桌面客户端（以下步骤在 5.9.4 上核对过）。
- 一个已连接至少一家店铺的 [SellerSheet](https://sellersheetai.com) 账号。

## Install · 安装

1. Open **专家·技能·连接器**, go to the **技能** tab and select **套件**.
2. Click **+** (添加市场). As 市场源, enter `sellersheetai/sellersheet-skills` and click **提交**.
3. **sellersheet-marketplace** now appears under 套件. Click **+** (安装) on **sellersheet-skills**.

1. 打开 **专家·技能·连接器**，进入 **技能** 标签页，选择 **套件**。
2. 点击 **+**（添加市场），「市场源」填入 `sellersheetai/sellersheet-skills`，点击 **提交**。
3. 套件下会出现 **sellersheet-marketplace**。在 **sellersheet-skills** 上点击 **+**（安装）。

## Connect · 连接

1. Go to the **连接器** tab and open **自定义连接器**. In the MCP list (MCP 服务管理), **sellersheet** shows "来自插件 sellersheet-skills" and 需要认证: click **连接**.
2. Your browser opens SellerSheet. Sign in if asked, then click **Allow** (允许).

1. 进入 **连接器** 标签页，打开 **自定义连接器**。MCP 服务管理列表里的 **sellersheet** 显示“来自插件 sellersheet-skills”和「需要认证」：点击 **连接**。
2. 浏览器会打开 SellerSheet，按提示登录，然后点击「允许」。

## Verify · 验证

Say to WorkBuddy · 对 WorkBuddy 说：

> 你能看到哪些店铺？ / Which stores can you see?

It should call `get_user_context` and list your store refs (such as `myStore-US`) with your plan and each store's status.

它应调用 `get_user_context`，列出你的店铺标识（例如 `myStore-US`）、套餐和每个店铺的状态。

## Troubleshooting · 故障排查

| Symptom · 现象 | Fix · 处理 |
|---|---|
| No 套件 tab or no **+** to add a marketplace · 看不到「套件」或添加市场的 + | Update WorkBuddy to the latest version, then reopen 专家·技能·连接器 → 技能. · 把 WorkBuddy 升级到最新版本，再打开 专家·技能·连接器 → 技能。 |
| 启用工具数量过多 (too many tools enabled) · 提示「启用工具数量过多」 | Shown above 80 enabled tools; the plugin brings more. It's advice, not an error — click **知道了**, or turn off tools you don't use under **sellersheet** in the MCP list. · 启用的工具超过 80 个时会提示，这是建议，不是错误：点 **知道了**，或在 MCP 列表里展开 **sellersheet** 关掉用不到的工具。 |
| **sellersheet** still shows 需要认证 · 仍显示「需要认证」 | The sign-in didn't finish. Click **连接** again and **Allow** in the browser. · 登录没有完成，再点一次 **连接**，在浏览器里点「允许」。 |
| Connected but "no stores" · 已连接但没有店铺 | Connect a store at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → My Stores. · 在 [控制台](https://sellersheetai.com/dashboard) → My Stores 连接店铺。 |

## For maintainers · 维护者说明

The repository root also doubles as a WorkBuddy connector package: `connector-meta.json`, `mcp.json` and `icon.svg` at the root, plus the plugin's skills. Run `python3 .maintainers/sync_workbuddy.py --zip` to build `dist/sellersheet-workbuddy-connector-<version>.zip` for submission at [open.workbuddy.cn](https://open.workbuddy.cn).

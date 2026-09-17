# Install on Tencent WorkBuddy · 腾讯 WorkBuddy 连接器安装

WorkBuddy is Tencent's desktop office agent. It does not read plugin marketplaces; SellerSheet is published to WorkBuddy's **connector marketplace**, so there is nothing to download and no command to run.

WorkBuddy 是腾讯的桌面办公智能体，不读取插件市场。SellerSheet 以**连接器**形式发布在 WorkBuddy 连接器市场，无需下载文件、无需执行命令。

## Prerequisites · 前置条件

- WorkBuddy 4.24 or newer (macOS or Windows).
- A [SellerSheet](https://sellersheetai.com) account with at least one Amazon store connected. Registration is with Google; afterwards you can sign in with Google **or** an email code.

- WorkBuddy 4.24 及以上（macOS 或 Windows）。
- 一个已连接至少一家亚马逊店铺的 [SellerSheet](https://sellersheetai.com) 账号。注册需使用 Google 登录一次，之后可用 Google **或** 邮箱验证码登录。

## Install · 安装

1. In WorkBuddy open **专家·技能·连接器 → 连接器** (Experts · Skills · Connectors → Connectors).
2. Find **SellerSheet** and click **连接 / Connect**.
3. A browser window opens on sellersheetai.com. Sign in (Google, or email + the 6-digit code we send you), then click **Authorize**.
4. Back in WorkBuddy the connector shows **已连接 / Connected**. The SellerSheet skills load with it.

1. 在 WorkBuddy 中打开 **专家·技能·连接器 → 连接器**。
2. 找到 **SellerSheet**，点击 **连接**。
3. 浏览器会打开 sellersheetai.com，登录（Google，或邮箱 + 我们发送的 6 位验证码），然后点击 **Authorize**。
4. 回到 WorkBuddy，连接器显示 **已连接**，SellerSheet 技能随之加载。

## Verify · 验证

Say to WorkBuddy · 对 WorkBuddy 说：

> 显示我的 SellerSheet 用户信息。 / Show me my SellerSheet user context.

It should call `get_user_context` and list your stores and plan. Then try one of the marketplace examples, e.g. "查一下 myStore-US 上周的库存和补货需求".

它应调用 `get_user_context` 并列出你的店铺与套餐。然后可以试试示例，例如“查一下 myStore-US 上周的库存和补货需求”。

## Update · 更新

WorkBuddy notifies you when a new connector version is approved; update from the same connector page. The connector always ships the same skills as the plugin release of the same version.

有新版本通过审核时 WorkBuddy 会提示，在同一连接器页面更新即可。连接器与同版本的插件发布始终包含同一套技能。

## Troubleshooting · 故障排查

| Symptom · 现象 | Fix · 处理 |
|---|---|
| Connector not listed · 市场里没有 SellerSheet | Update WorkBuddy to 4.24+; the listing needs it. · 升级 WorkBuddy 到 4.24 及以上。 |
| Browser sign-in says the email is not registered · 提示邮箱未注册 | Sign in with Google once to create the account, then retry. · 先用 Google 登录一次完成注册，再重试。 |
| Connected but "no stores" · 已连接但没有店铺 | Connect an Amazon store: sellersheetai.com/dashboard → My Stores → Connect Amazon. · 在控制台 My Stores → Connect Amazon 连接店铺。 |
| Authorization expired · 授权失效 | Click **连接** again; the browser sign-in repeats. · 再次点击 **连接** 重新授权。 |

## For maintainers · 维护者说明

The package WorkBuddy reviews is this repository root: `connector-meta.json`, `mcp.json`, `icon.svg`, `skills/`. Run `python3 .maintainers/sync_workbuddy.py --zip` to build `dist/sellersheet-workbuddy-connector-<version>.zip` for submission at [open.workbuddy.cn](https://open.workbuddy.cn).

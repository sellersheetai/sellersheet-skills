# SellerSheet 技能包（SellerSheet Skills）

**[English → README.md](./README.md)**

> **不用 ERP，对 AI 说需求就能运营亚马逊店铺。** 本插件把你的智能体接到 [SellerSheet](https://sellersheetai.com)：
> 由它调用亚马逊官方接口（Amazon SP-API、Amazon Ads API），结果全部写进 Google 表格，你审核后再提交。
> 一次安装 = 技能包 + 托管的 SellerSheet MCP（350+ 个工具）。OAuth 登录，无需 API key。

支持 Claude Code、Claude Desktop、Codex、腾讯云 CodeBuddy Code、Gemini CLI、Antigravity、Openclaw、Hermes，以及任何会扫描技能目录的智能体。

**作者**：[sellersheetai.com](https://sellersheetai.com)
**许可证**：Apache-2.0
**最新版本**：见 [README.md](./README.md) 顶部与 [更新日志](./CHANGELOG.md)

## 能做什么

| 领域 | 示例 |
|---|---|
| **订单与财务** | 按时段拉订单、单笔订单费用拆解、结算周期汇总、发送 Request a Review |
| **Listing 管理** | 从表格批量改价格、库存和属性，上架限制检查，类目模板，Listing 报错排查 |
| **FBA 入库** | 建计划 → 装箱 → 分仓 → 运输 → 箱标 → 跟踪，全流程 |
| **广告（SP / SB / SD）** | 广告活动、关键词、竞价、预算、否定词、搜索词挖掘、广告报表 |
| **定价与费用** | Buy Box 与最低价、Featured Offer 建议价、佣金与 FBA 费用估算 |
| **报表与数据仓库** | 50+ 张已同步报表、品牌分析、Sales & Traffic、Data Kiosk |
| **买家洞察** | ASIN 或类目的好评/差评主题、退货原因、6 个月趋势 |
| **商品图与 A+** | 合规主图、学竞品风格换场景、变体改色、A+ 模块 |
| **noon 中东站** | 订单、财务、FBN 库存账龄、商品浏览与销量 |

支持多店铺、多站点（美国、欧洲、日本、中东等），同一段对话里可以切换店铺。

## 直接这样问 AI

- "把 myStore-US 最近 7 天的订单拉到表格里，按 SKU 汇总销量和销售额"
- "订单 112-XXXXXXX-XXXXXXX 亚马逊到底扣了哪些费用？"
- "列出 ACoS 高于 40% 的 SP 广告活动，把关键词和竞价拉出来"
- "把这批关键词竞价上调 10%，先写到表格我确认再提交"
- "用表格里的箱规建一个 FBA 货件，并下载箱标"
- "列出所有可售库存低于 30 天的 SKU"
- "B0XXXXXXXX 的买家最常夸的和最常抱怨的点是什么？"
- "参考这张竞品图的风格，给我的产品生成一张白底主图"

**表格就是审核台。** AI 把结果写进表格，带表头、格式和筛选；你在表格里改完，对 AI 说"把我改过的行提交到亚马逊"即可。

AI 生图、生成文案和买家洞察按次从 SellerSheet 账户 Credits 扣费，失败自动退回。

## 技能包内容

九个技能，教你的智能体用好 SellerSheet MCP。技能文件以英文编写，但会**用你的语言回答**：用中文提问就得到中文说明（工具名、店铺引用、表名、亚马逊术语和表格表头保持英文，服务器按这些名字读取数据）。

| 技能 | 作用 |
|---|---|
| **sellersheet-sheets** | 通过 SellerSheet MCP 读写 Google 表格：报表、看板、财务模型、表格格式化、品牌配色、`SQL()` 实时数据、图片缩略图。自包含，无需其他表格技能。 |
| **sellersheet-dashboard** | 多页签运营看板：库存、广告（PPC）、账户健康、listing、利润率、退货、Buy Box、现金周转，带数据新鲜度标注和智能体洞察。基于 `sellersheet-sheets`。 |
| **report-data** | 亚马逊 SP-API 与广告 API 报表数据：查询 SellerSheet 数据仓库中 50+ 张 `rpt_*` 表（库存、listing、订单、退货、财务、品牌分析、SP/SB/SD 广告），查看同步计划，按需报告的 创建 → 轮询 → 下载 流程。库存水位、补货需求、搜索词、结算、listing 状态等问题都用它。 |
| **image-gen** | 用 gpt-image-2 生成亚马逊 listing 图片与 A+ 页面：学习成熟竞品的图片风格，生成/改色产品图，检查主图合规，搭建 A+ 模块并评分，记录到「Images Generation」表格。 |
| **noon-report-data** | noon.com（noon Partners）报表数据：5 张 `rpt_noon_*` 表（订单、财务/交易、FBN 库存账龄、商品浏览与销量、FBN 商品目录），每日两次同步，按项目范围与市场语义查询。 |
| **amazon-ads** | 亚马逊广告（SP、SB、SD）操作：广告活动、广告组、关键词/投放、竞价、预算、批量创建、否定词、导出、变更历史、推荐。内置 35 个真实的广告报表 API v3 `createReport` 请求体。 |
| **amazon-report** | 亚马逊 SP-API 按需报告文档：22 种报告（品牌分析、销售与流量、促销/优惠券、Vendor、账户健康）的精确 `reportType`、必填 `reportOptions` 枚举与完整 JSON 字段树。不用于已同步的 `rpt_*` 仓库，那是 `report-data` 的事。 |
| **data-kiosk** | 亚马逊 SP-API Data Kiosk GraphQL 查询编写：带版本的根查询类型、数据集字段、必填参数、枚举和逐字段 `@resultRetention`，覆盖销售与流量、经济性、Vendor 分析。 |
| **fba-inbound** | FBA 入仓全流程：先收集必要信息（发货地址、产品与箱规、承运方式、日期），再建计划、装箱、分仓方案、由你选择运输方案与送达窗口、确认、箱标、装箱单、上传物流单号、货件状态，另有刷美西仓循环。模式 A 直接用 SellerSheet FBA 表格和插件的计划工作簿（STA-Options、Inbound PL、箱标链接由服务器写入）；模式 B 不需要 SellerSheet 表格，结果输出到对话、HTML、你的表格或 Excel。除非你指定规则，否则绝不替你选方案。 |

另有 **`sellersheet-shared`**：所有技能引用的公共约定（MCP 预检流程、店铺引用规则、响应契约、语言规则、故障排查），随技能包自动安装。

### 即将推出（审核中）

`sellersheet`（亚马逊业务操作编排）、`amazon-api`、`listing-optimizer`、`listing-refurbish`、`amazon-listing-optimizer`。进展见 [CHANGELOG](./CHANGELOG.md)。

## 前置条件

1. 一个 [sellersheetai.com](https://sellersheetai.com) 账号。
2. 在 SellerSheet 工作区中至少连接一家亚马逊店铺。
3. 在你的智能体中连接 **SellerSheet MCP 服务器**。它是托管的远程服务（`https://sellersheetai.com/mcp`），本地无需安装。**插件方式安装（Claude Code、Codex、CodeBuddy Code）会自动注册**，首次使用通过浏览器 OAuth 登录即可，无需 API key。没有插件系统的智能体需手动注册（OAuth 连接器，或在 [控制台](https://sellersheetai.com/dashboard) → **MCP & API keys** → **Create Key** 创建密钥）。详见 [docs/setup-mcp.md](./docs/setup-mcp.md)。

如需看板中的广告（PPC）页签有真实数据，店铺还需授权亚马逊广告：[控制台](https://sellersheetai.com/dashboard) → My Stores → 店铺所在行的 **Authorize Ads**。未授权时广告相关区域只显示框架。

## 安装

### 腾讯云 CodeBuddy Code

CodeBuddy Code 识别与 Claude Code 相同的插件目录结构，一步装好技能与 MCP。在 CodeBuddy 会话中：

```
/plugin marketplace add sellersheetai/sellersheet-skills
/plugin install sellersheet-skills@sellersheet-marketplace
/reload-plugins
```

然后运行 `/mcp`，选择 `sellersheet`，在浏览器中登录授权。完整中英双语指南：[docs/install-codebuddy.md](./docs/install-codebuddy.md)。

### 腾讯 WorkBuddy

WorkBuddy 不读取插件市场，SellerSheet 以**连接器**形式发布到 WorkBuddy 连接器市场。在 WorkBuddy 内安装：专家·技能·连接器 → 连接器 → SellerSheet → 连接，按提示登录即可，无需下载任何文件。本仓库根目录同时就是 WorkBuddy 连接器包（`connector-meta.json`、`mcp.json`、`icon.svg` 与同一套 `skills/`），因此连接器与插件永远是同一版技能。详见 [docs/install-workbuddy.md](./docs/install-workbuddy.md)。

### Claude Code

```
/plugin marketplace add sellersheetai/sellersheet-skills
/plugin install sellersheet-skills@sellersheet-marketplace
```

一步安装全部技能与 SellerSheet MCP 服务器。首次使用运行 `/mcp`，选择 `sellersheet`，浏览器登录（OAuth，无需 API key）。指南：[docs/install-claude-code.md](./docs/install-claude-code.md)。

### Codex CLI / ChatGPT 桌面版

```bash
codex plugin marketplace add sellersheetai/sellersheet-skills
codex plugin add sellersheet-skills@sellersheet-marketplace
codex mcp login sellersheet     # 浏览器 OAuth，无需 API key
```

指南：[docs/install-codex.md](./docs/install-codex.md)。

### Claude Desktop

1. 注册 MCP 服务器：**Settings → Connectors → Add custom connector** → URL `https://sellersheetai.com/mcp`，按提示 OAuth 登录。
2. 安装技能：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target claude-desktop
```

### Cursor、Gemini 及 50+ 其他智能体 —— `npx skills`

```bash
npx skills add sellersheetai/sellersheet-skills            # 安装完整技能包
npx skills add sellersheetai/sellersheet-skills --list     # 先预览
npx skills add sellersheetai/sellersheet-skills -a codex   # 指定目标智能体
npx skills add sellersheetai/sellersheet-skills -g         # 用户级（全局）安装
```

技能**始终作为一个整体安装**（它们互相引用 `sellersheet-shared`），不支持部分安装。技能与 MCP 服务器是两个独立的部分，仍需按 [docs/setup-mcp.md](./docs/setup-mcp.md) 注册 MCP。

### 没有 Node.js —— `install.sh`

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --target <agent>
```

`<agent>` 可为 `gemini`、`antigravity`、`codebuddy`（仅技能，MCP 需手动注册）。Openclaw / Hermes / 自定义智能体加 `--path <目录>` 指向其技能扫描目录。Claude Code、Codex、CodeBuddy Code 用户请使用上面的插件方式，它自带更新机制。

## 更新与自动更新

**Claude Code / CodeBuddy Code**：第三方市场默认不自动更新，需开启一次：`/plugin` → **Marketplaces** → **sellersheet-marketplace** → **Enable auto-update**。手动更新：

```
/plugin marketplace update sellersheet-marketplace
/plugin update sellersheet-skills
```

**Codex**：`codex plugin marketplace upgrade sellersheet-marketplace`。

**其他智能体**：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --update   # 重新安装到最新版
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --check    # 只比较版本，不做改动
```

机制详解：[docs/auto-update.md](./docs/auto-update.md)。

## 验证

对智能体说：**“显示我的 SellerSheet 用户信息。”** 它应调用 `get_user_context` 并返回你的账户、店铺、套餐和 `skills_catalog`。若提示 “tool not found” 或 “unauthorized”，说明三项前置条件有一项未完成，最常见的原因是改完 MCP 配置后没有重启智能体。

## 文档

- [在 CodeBuddy Code 上安装（中英双语）](./docs/install-codebuddy.md)
- [在腾讯 WorkBuddy 中安装连接器](./docs/install-workbuddy.md)
- [通过 `npx skills` 安装（Codex、Cursor、Gemini 等）](./docs/install-npx-skills.md)
- [在 Claude Code 上安装](./docs/install-claude-code.md)
- [在 Claude Desktop 上安装](./docs/install-claude-desktop.md)
- [在 Codex 上安装](./docs/install-codex.md)
- [在 Gemini CLI 上安装](./docs/install-gemini.md)
- [在 Antigravity 上安装](./docs/install-antigravity.md)
- [在 Openclaw / Hermes / 通用智能体上安装](./docs/install-generic.md)
- [SellerSheet MCP 设置](./docs/setup-mcp.md)
- [自动更新](./docs/auto-update.md)

## 数据发送说明

- **发送了什么。** 每次调用工具时，只发送该动作需要的请求——操作类型（查询、创建、更新……）、标识符（店铺引用、ASIN、SKU、广告活动/计划 ID）、以及你或 AI 提供的值（出价、预算、地址、表格/标签页名称）——从你的智能体发往托管的 SellerSheet MCP 服务器，再由它代表你调用 Amazon 的 SP-API / Ads API、noon 的 Partner API 和 Google 的 Sheets/Drive API。
- **返回了什么。** Amazon、noon 或 Google Sheets 的响应——订单、Listing、广告表现数据、FBA 计划状态、生成的图片——被写入你的 Google 表格，或返回给你的智能体供 AI 总结。除 Amazon、noon、Google，以及仅在生成图片/文案时使用的 AI 图像/文本服务商外，不会发给任何第三方。
- **授权与范围。** 每次调用都在你自己的 SellerSheet OAuth 授权或 API Key 下运行，范围限定在你已连接的店铺和已授权的站点（广告相关调用还需要在"我的店铺"中单独授权广告）。只读 Key 只能读不能写；受限 Key 只能看到被授权的店铺。
- **绝不会发送的内容。** 你的 Amazon 或 Google 密码（SellerSheet 使用 OAuth，从不接触凭证）、支付信息，或你未连接店铺的数据。技能文件本身不发送任何数据——它们只是给你的智能体看的说明，不是数据通道。
- **完整政策：** [sellersheetai.com/privacy-policy](https://sellersheetai.com/privacy-policy)。

## 支持

- Issues：[github.com/sellersheetai/sellersheet-skills/issues](https://github.com/sellersheetai/sellersheet-skills/issues)
- 讨论区：[github.com/sellersheetai/sellersheet-skills/discussions](https://github.com/sellersheetai/sellersheet-skills/discussions)
- 邮箱：support@sellersheetai.com
- 隐私政策：[sellersheetai.com/privacy-policy](https://sellersheetai.com/privacy-policy)

## 许可证

Apache-2.0，见 [LICENSE](./LICENSE)。

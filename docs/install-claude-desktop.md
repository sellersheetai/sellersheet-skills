# Install on Claude (claude.ai and the desktop app)

The SellerSheet plugin gives Claude the skills **and** the MCP server in one step. Add it once in claude.ai or the Claude desktop app: it's saved to your Claude account, so Cowork and Claude Code get it too.

## Prerequisites

- A SellerSheet account with at least one store connected — no API key needed
- A Claude account. On a Team or Enterprise plan, an Owner may need to add the connector for your organization first.

## Step 1: Add the plugin

1. Open **Customize → Plugins**.
2. Select **Add → Add marketplace** and enter the repository:

   ```text
   sellersheetai/sellersheet-skills
   ```

3. Find **SellerSheet Skills** among the plugins, open it and select **Add**.

## Step 2: Connect SellerSheet

Adding the plugin loads the skills but doesn't connect the server.

1. Open the plugin's **Connectors** tab. SellerSheet shows **Not added**: add it, then select **Connect**.
2. Your browser opens SellerSheet. Click **Allow**, and you're back in Claude. Access is scoped to your stores.

**Server only, by hand** (no skills): **Customize → Connectors → Add custom connector**, name it `SellerSheet`, paste `https://sellersheetai.com/mcp` as the server URL, select **Add**, then **Connect**.

## Verify

Ask:

> "Which stores can you see?"

Claude should call `get_user_context` and list your store refs (such as `myStore-US`) with your plan and each store's status. Type `/` in the message box to see the plugin's skills.

In Claude Code, the plugin downloads the next time you start a session signed in to the same account; run `/reload-plugins` to load it.

## Update

In **Customize → Plugins**, turn on **Sync automatically** for the marketplace, or select **Check for updates** to pull the latest now.

## Troubleshooting

- **You can't add the marketplace or the connector**: on a Team or Enterprise plan, an Owner decides which sources members can add and adds custom connectors for the organization. Ask an Owner to add SellerSheet, then connect it with your own account.
- **Skills work but tools don't**: the connector isn't **Connected** yet — finish Step 2.
- **"Unauthorized" or access revoked**: select **Connect** again, or manage access at [sellersheetai.com/dashboard](https://sellersheetai.com/dashboard) → **MCP & API keys**.

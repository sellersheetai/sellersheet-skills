# Auto-update

How `sellersheet-skills` stays current after you install it.

## Claude Code

### How updates are detected

`sellersheet-skills` is published as a **git-based marketplace**. Claude Code resolves the plugin's version from the first of these that is set:

1. `version` in `.claude-plugin/plugin.json` ← **this plugin uses this**
2. `version` in the marketplace entry (this plugin intentionally omits it)
3. the git commit SHA

This plugin sets an explicit semver `version` in `plugin.json` and bumps it on every release (CI tags each bump — see [for maintainers](#for-maintainers)). When the version string changes, Claude Code treats it as a new release.

### Enable auto-update (recommended)

Third-party marketplaces are **not** auto-updated by default — only Anthropic's official marketplace is. You opt in once, two ways:

**Interactive:** run `/plugin` → **Marketplaces** tab → select **sellersheet-marketplace** → **Enable auto-update**.

**Settings file** — add to `~/.claude/settings.json` (user scope) or `.claude/settings.json` (project scope):

```json
{
  "extraKnownMarketplaces": {
    "sellersheet-marketplace": {
      "source": { "source": "github", "repo": "sellersheetai/sellersheet-skills" },
      "autoUpdate": true
    }
  }
}
```

With auto-update enabled, Claude Code refreshes the marketplace at startup and updates the plugin whenever a newer version is published. If the plugin updated, you'll see a notification to run `/reload-plugins` to activate it in the current session.

### Update manually

Without auto-update, refresh on demand:

```
/plugin marketplace update sellersheet-marketplace   # pull the latest catalog
/plugin update sellersheet-skills                    # update the plugin
```

`/plugin marketplace update` with no name updates every marketplace; `/plugin update` with no name updates every plugin.

### Disable auto-update

`/plugin` → **Marketplaces** → select the marketplace → **Disable auto-update**, or set `"autoUpdate": false`. To disable *all* auto-updates (Claude Code itself included): `export DISABLE_AUTOUPDATER=1`.

## Other agents (Codex, Gemini CLI, Antigravity, Openclaw, Hermes, …)

These agents install skills via `install.sh`, which clones this repo into `~/.cache/sellersheet-skills` and copies the skill folders. Re-run with `--update`:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --update
```

Check what's installed vs. the latest published version without changing anything:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh) --check
```

`--check` compares the `version:` in each installed `SKILL.md` against this repo. To automate it, add the `--update` command to a cron job or your shell startup.

## For maintainers

A release is a single version bump that fans out everywhere:

1. Bump `version` in `.claude-plugin/plugin.json`.
2. Mirror it into `versions.json` (`marketplace_version` + every `skills[].latest_version`), every `skills/*/SKILL.md` frontmatter `version:`, and `install.sh` `VERSION`.
3. Add a `## [x.y.z]` entry to `CHANGELOG.md` and reference the version in `README.md`.
4. Push to `main`.

`.github/workflows/lint.yml` fails the build if any of those fall out of sync. `.github/workflows/auto-tag.yml` creates and pushes the `vX.Y.Z` git tag automatically once `plugin.json` changes on `main`. `.maintainers/promote.sh` performs steps 1–3 in one command.

**Key rule:** pushing new commits *without* bumping `plugin.json` `version` does nothing for installed users — Claude Code sees the same version and keeps the cached copy. Always bump the version on a content release.

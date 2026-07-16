# sellersheet-skills — contributor protocol (humans AND agents)

This repo is ONE plugin serving two ecosystems from the same files: **Claude Code** and
**Codex** both read `.claude-plugin/marketplace.json`; `npx skills` and `install.sh` read
`skills/*/SKILL.md` directly. A broken frontmatter or a half-done version bump ships to
every channel at once. Follow this protocol exactly.

## Before EVERY push — no exceptions

```bash
./.maintainers/lint.sh   # must print "All checks passed ✓"
```

Install the pre-push hook once so this is automatic:

```bash
./.maintainers/install-hooks.sh
```

CI runs the same script on every push/PR (`.github/workflows/lint.yml` calls `lint.sh` —
never inline checks in the workflow). **A red lint run on main is an incident, not noise** —
fix it before doing anything else.

## Releasing — ONLY via promote.sh

```bash
# 1. Write the CHANGELOG entry first: "## [X.Y.Z] — YYYY-MM-DD"
# 2. Then:
./.maintainers/promote.sh X.Y.Z
git push origin main        # CI auto-tags vX.Y.Z from plugin.json
```

**NEVER hand-edit a version number anywhere.** The version lives in 14 files
(plugin.json, versions.json ×10 fields, every SKILL.md frontmatter, install.sh, README
badge) — `promote.sh` fans it out atomically and runs lint. The v0.10.0 release was
originally a hand-edited plugin.json bump that left 13 files behind and main's lint red;
it had to be repaired after the fact. Don't repeat it.

New skill? Drop `skills/<name>/SKILL.md`, add the entry to `versions.json .skills[]`,
then release via promote.sh.

## Frontmatter rules (the image-gen lesson)

- `description:` MUST parse under **strict YAML** (js-yaml — used by `npx skills` and
  plugin loaders). Any `: ` inside an unquoted scalar breaks it and the skill **silently
  vanishes from installs**. Use a `>-` folded block scalar for long descriptions.
- Keep descriptions under ~1536 chars — Claude Code truncates the skill listing there.
- `name:` must equal the folder name; `version:` must equal plugin.json's.
- lint.sh enforces all of this — that's why you run it.

## Content rules

- Skills cross-reference [`skills/sellersheet-shared/SKILL.md`](skills/sellersheet-shared/SKILL.md)
  (preflight, store refs, response contract). Don't re-copy that content into skills; don't
  break the `../sellersheet-shared/SKILL.md` relative links (lint checks them).
- The bundle installs as a WHOLE — never document partial/selective installs.
- Claude Code + Codex user docs are **plugin-only** (no install.sh/manual-copy paths for
  those two agents). `npx skills`/`install.sh` serve agents without a plugin system.
- No real store names, seller IDs, or ASINs — lint's privacy scan enforces the list.
- Stale facts lint guards against (don't reintroduce): `@sellersheet/mcp-server` (npm 404),
  "Settings → API" (page doesn't exist; it's **MCP & API keys → Create Key**),
  ".mcp.json auto-registers MCP" (dead since 0.5.1 — MCP and skills are two separate steps),
  "Stores → Connect Advertising" (real UI: My Stores → **Authorize Ads**).

## Compatibility smoke tests (run after structural changes)

```bash
# npx skills channel — must find every skill in skills/
npx -y skills add "$(pwd)" --list

# Codex plugin channel — local-path marketplace install
codex plugin marketplace add "$(pwd)"
codex plugin add sellersheet-skills@sellersheet-marketplace
codex plugin list | grep sellersheet    # installed, enabled
codex plugin marketplace remove sellersheet-marketplace   # clean up

# Claude Code channel: /plugin marketplace add <this dir> in a Claude Code session
```

## Maintainer-machine caveat

On the maintainer's dev machine, these skills load via repo symlinks (`.claude/skills/` in
the monorepo) and the plugin is deliberately **disabled** locally — don't "fix" that. The
plugin is the user-facing channel.

# SellerSheet Skills — Maintainer Tooling

Maintenance scripts for the public `sellersheet-skills` repo. Committed since v0.10.0 so CI, the pre-push hook, and maintainers all run the SAME `lint.sh` (it was gitignored before, which forced CI to carry a drifting inline copy).

| File | Purpose |
|---|---|
| `promote.sh` | Release a new version: bump the canonical version in `plugin.json` and fan it out to `versions.json`, every `SKILL.md`, `install.sh`, and `README.md`; verify the `CHANGELOG.md` entry; run lint; commit. |
| `lint.sh` | Local mirror of `.github/workflows/lint.yml` — JSON validity, SKILL.md frontmatter, version-consistency, marketplace ↔ repo sync, privacy + ASIN scan. Run before pushing. |

## Architecture: single-plugin model

The whole repo is **one Claude Code plugin** (`sellersheet-skills`). Skills are auto-discovered from `skills/*/SKILL.md` — there is no per-skill plugin entry. `.claude-plugin/marketplace.json` has exactly one plugin entry with `"source": "./"`.

**Versioning** — the single source of truth is `.claude-plugin/plugin.json` `version`. Every other version string mirrors it:
`versions.json` (`marketplace_version` + each `skills[].latest_version`), each `skills/*/SKILL.md` frontmatter `version:`, `install.sh` `VERSION`, and the `README.md` "Latest release" line + compat table. `lint.sh` and CI fail if any of these drift.

Claude Code reads `plugin.json` `version` for update detection — **pushing content without bumping it does nothing for installed users.**

## Workflow

### One-time: the privacy-scan inputs (private, never committed)

`lint.sh` refuses to run without them. Create `.maintainers/private-patterns.local`
(gitignored) as a shell snippet setting two variables:

```bash
SS_PRIVACY_PATTERNS='(<one extended regex of real store refs, brands, hostnames, mailboxes>)'
SS_INTERNAL_STRINGS=$'<internal repo name>\n<internal source tree>\n<internal doc path>'
```

CI reads the same two values from the repository secrets `SS_PRIVACY_PATTERNS` and
`SS_INTERNAL_STRINGS` (`gh secret set SS_PRIVACY_PATTERNS < file`). Ask a maintainer for
the current values; they are deliberately not in this repo.

### Before any push

```bash
./.maintainers/lint.sh
```

Exits non-zero on any violation. CI runs the same checks on every push and PR.

### Cut a release

1. Land your content changes on `main` (or a branch).
2. Add a `## [X.Y.Z]` section to `CHANGELOG.md` with the release notes.
3. Bump + fan out the version, lint, and commit:

   ```bash
   ./.maintainers/promote.sh X.Y.Z            # or --dry-run to preview
   ```

4. Push:

   ```bash
   git push origin main
   ```

`.github/workflows/auto-tag.yml` creates and pushes the `vX.Y.Z` git tag automatically once the new `plugin.json` lands on `main`.

### Add a new skill to the bundle

1. Drop the skill folder into `skills/<name>/` with a `SKILL.md` (frontmatter: `name` matching the folder, `description`, `version`).
2. Add it to `versions.json` `.skills[]`.
3. Move it from "Coming soon" to the "What's in here" table in `README.md`.
4. Cut a release with `promote.sh` (step above).

### Install lint as a pre-commit hook (optional)

```bash
ln -s ../../.maintainers/lint.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## CI

`.github/workflows/` is committed and active:

- `lint.yml` — validates structure, versioning, and the privacy/ASIN scans on every push + PR.
- `auto-tag.yml` — tags `vX.Y.Z` when `plugin.json` `version` changes on `main`.

## Requirements

- `git`
- `jq` (`brew install jq` / `apt install jq`)
- `bash` 4+
- `sed` (BSD/macOS — `promote.sh` uses `sed -i ''`)

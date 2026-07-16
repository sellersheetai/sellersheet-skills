#!/usr/bin/env bash
# Release a new version of the sellersheet-skills plugin.
#
# Single-plugin model: the whole repo is ONE plugin. Skills are auto-discovered
# from skills/*/. A release is just a version bump fanned out to every file that
# mirrors the canonical version in .claude-plugin/plugin.json.
#
# Usage:
#   ./.maintainers/promote.sh <new-version>            # e.g. 0.4.0
#   ./.maintainers/promote.sh <new-version> --dry-run
#
# What it does:
#   1. Validates <new-version> is semver and greater than the current version
#   2. Bumps .version in plugin.json
#   3. Mirrors it into versions.json (marketplace_version + every skill), each
#      skills/*/SKILL.md frontmatter, install.sh VERSION, and README.md
#   4. Verifies CHANGELOG.md has a '## [<new-version>]' entry (you write the notes)
#   5. Runs lint.sh
#   6. Commits "Release v<new-version>" (push manually; CI auto-tags from plugin.json)
#
# To add a NEW skill to the bundle: drop the folder into skills/<name>/ with a
# SKILL.md, add it to versions.json .skills[], then run this script to release.
#
# Prerequisites: jq, git

set -euo pipefail

NEW=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --help|-h) sed -n '2,23p' "$0"; exit 0 ;;
    *) if [[ -z "$NEW" ]]; then NEW="$1"; shift; else echo "Unknown arg: $1"; exit 1; fi ;;
  esac
done
[[ -z "$NEW" ]] && { echo "Usage: $0 <new-version> [--dry-run]"; exit 1; }

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

log() { echo "[promote] $*"; }
err() { echo "[promote] ERROR: $*" >&2; exit 1; }
run() { if [[ $DRY_RUN -eq 1 ]]; then echo "  DRY: $*"; else eval "$*"; fi; }

command -v jq  >/dev/null || err "jq is required (brew install jq / apt install jq)"
command -v git >/dev/null || err "git is required"

[[ "$NEW" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || err "'$NEW' is not semver (X.Y.Z)"

CUR=$(jq -r '.version' .claude-plugin/plugin.json)
log "Current version: $CUR"
log "New version:     $NEW"
if [[ "$CUR" == "$NEW" || "$(printf '%s\n%s\n' "$CUR" "$NEW" | sort -V | tail -1)" != "$NEW" ]]; then
  err "$NEW must be strictly greater than the current version $CUR"
fi

MAJOR_MINOR="${NEW%.*}"

log "Bumping version across all files..."

# 1. plugin.json (canonical)
run "jq --arg v '$NEW' '.version = \$v' .claude-plugin/plugin.json > .claude-plugin/plugin.json.tmp && mv .claude-plugin/plugin.json.tmp .claude-plugin/plugin.json"

# 2. versions.json
TODAY=$(date -u +%Y-%m-%d)
run "jq --arg v '$NEW' --arg d '$TODAY' '.marketplace_version = \$v | .updated_at = \$d | .skills = [.skills[] | .latest_version = \$v]' versions.json > versions.json.tmp && mv versions.json.tmp versions.json"

# 3. each SKILL.md frontmatter
for d in skills/*/; do
  f="${d}SKILL.md"
  if grep -qE '^version:' "$f"; then
    run "sed -i '' -E 's/^version:.*/version: $NEW/' '$f'"
  else
    err "$f has no 'version:' line in frontmatter — add one first"
  fi
done

# 4. install.sh
run "sed -i '' -E 's/^VERSION=\"[0-9.]+\"/VERSION=\"$NEW\"/' install.sh"

# 5. README.md — 'Latest release' line + version-compat table row
run "sed -i '' -E 's/\*\*Latest release\*\*: v[0-9]+\.[0-9]+\.[0-9]+/**Latest release**: v$NEW/' README.md"
run "sed -i '' -E 's/\| v[0-9]+\.[0-9]+\.x \|/| v$MAJOR_MINOR.x |/' README.md"

# 6. CHANGELOG must have an entry — the maintainer writes the notes
if [[ $DRY_RUN -eq 0 ]] && ! grep -qE "^## \[$NEW\]" CHANGELOG.md; then
  err "CHANGELOG.md has no '## [$NEW]' entry. Add the release notes, then re-run."
fi

# 7. lint
log "Running lint..."
if [[ $DRY_RUN -eq 1 ]]; then
  echo "  DRY: ./.maintainers/lint.sh"
else
  ./.maintainers/lint.sh
fi

if [[ $DRY_RUN -eq 1 ]]; then
  log "Dry run complete — nothing written."
  exit 0
fi

# 8. commit
log "Committing release..."
git add -A
git commit -m "Release v$NEW"

log ""
log "Done. Push to publish:"
log "  git push origin main"
log ""
log "CI (.github/workflows/auto-tag.yml) tags v$NEW automatically once plugin.json lands on main."

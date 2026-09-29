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
#   SS_SKIP_PLUGIN_EVAL=1 ./.maintainers/promote.sh <new-version>   # skip the eval gate
#   SS_PLUGIN_EVAL_MAX_COST_USD=5 ./.maintainers/promote.sh <new-version>   # lower the cap
#
# What it does:
#   1. Validates <new-version> is semver and greater than the current version
#   2. Bumps .version in plugin.json
#   3. Mirrors it into versions.json (marketplace_version + every skill), each
#      skills/*/SKILL.md frontmatter, install.sh VERSION, README.md, and the
#      WorkBuddy connector-meta.json (via sync_workbuddy.py)
#   4. Verifies CHANGELOG.md has a '## [<new-version>]' entry (you write the notes)
#   5. Runs lint.sh
#   5b. Runs `claude plugin eval` on evals/ (--threshold 0.8) — refuses the release
#       if any case scores below it. See .maintainers/README.md for cost + how to
#       run one case; skip with SS_SKIP_PLUGIN_EVAL=1, cap spend with
#       SS_PLUGIN_EVAL_MAX_COST_USD.
#   6. Commits "Release v<new-version>" (push manually; CI auto-tags from plugin.json)
#
# To add a NEW skill to the bundle: drop the folder into skills/<name>/ with a
# SKILL.md, add it to versions.json .skills[], then run this script to release.
#
# Prerequisites: jq, git, and (for the eval gate) the claude CLI + model credentials

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

# 5b. WorkBuddy connector files (connector-meta.json version + derived SKILL.md keys)
run "python3 .maintainers/sync_workbuddy.py"

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

# 7b. plugin evals (evals/ — amazon-ads + fba-inbound routing/safety/autopilot suites).
# SS_SKIP_PLUGIN_EVAL=1 skips this step (offline machine, no model credentials, or a
# maintainer who already ran it separately); SS_PLUGIN_EVAL_MAX_COST_USD caps the
# list-price spend (default 20 — see .maintainers/README.md for the per-run cost and
# how to run a single case). Refuses the release on a non-zero exit.
EVAL_MAX_COST="${SS_PLUGIN_EVAL_MAX_COST_USD:-20}"
if [[ "${SS_SKIP_PLUGIN_EVAL:-0}" == "1" ]]; then
  log "Skipping plugin evals (SS_SKIP_PLUGIN_EVAL=1)."
elif [[ $DRY_RUN -eq 1 ]]; then
  echo "  DRY: claude plugin eval . --trust-plugin --json evals/results/promote-gate.json --threshold 0.8 --no-publish --max-cost-usd $EVAL_MAX_COST"
else
  log "Running plugin evals (max-cost-usd \$$EVAL_MAX_COST — set SS_PLUGIN_EVAL_MAX_COST_USD to change, SS_SKIP_PLUGIN_EVAL=1 to skip)..."
  command -v claude >/dev/null || err "claude CLI not found — required for the plugin-eval gate (or set SS_SKIP_PLUGIN_EVAL=1)"
  claude plugin eval . --trust-plugin --json evals/results/promote-gate.json \
    --threshold 0.8 --no-publish --max-cost-usd "$EVAL_MAX_COST" \
    || err "plugin evals scored below threshold (or failed to run) — see evals/results/promote-gate.json. Fix the regression, or SS_SKIP_PLUGIN_EVAL=1 if you already verified this separately."
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

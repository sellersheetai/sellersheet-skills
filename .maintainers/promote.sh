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
#   SS_RUN_PLUGIN_EVAL=1 ./.maintainers/promote.sh <new-version>    # ALSO run the eval gate (opt-in)
#   SS_PLUGIN_EVAL_MAX_COST_USD=5 ./.maintainers/promote.sh <new-version>   # lower its cap
#
# What it does:
#   1. Validates <new-version> is semver and greater than the current version
#   2. Bumps .version in plugin.json
#   3. Mirrors it into versions.json (marketplace_version + every skill), each
#      skills/*/SKILL.md frontmatter, install.sh VERSION, README.md, and the
#      WorkBuddy connector-meta.json (via sync_workbuddy.py)
#   5c. OPT-IN: with SS_TOOLS_JSON=<path>, refreshes .maintainers/tool-names.txt
#       (the live tool-name allowlist lint.sh checks skills/** against) from that
#       mcp-tools.json. Unset (the default) leaves the committed list untouched —
#       there is no safe default path to guess (see the comment at the step).
#   4. Verifies CHANGELOG.md has a '## [<new-version>]' entry (you write the notes)
#   5. Runs lint.sh
#   7b. OPT-IN (SS_RUN_PLUGIN_EVAL=1): runs `claude plugin eval` on evals/ (--threshold 0.8)
#       and refuses the release if any case scores below it. Off by default since
#       2026-10-08 (operator ruling: the ~50 agent runs draw on the account's usage);
#       see .maintainers/README.md for cost + how to run one case; cap spend with
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

# 5c. Live tool-name allowlist (.maintainers/tool-names.txt) — names only, one per
# line, read by lint.sh's backticked-tool-name check (any `ads_…`/`noon_…`/`sp_api_…`
# name in skills/** must be in this list, so a rename or retirement in the main
# monorepo can't silently ship a dead name in the public docs). OPT-IN ONLY: set
# SS_TOOLS_JSON to the path of a main-repo checkout's marketing-site/src/_data/
# mcp-tools.json that is ACTUALLY AT the commit this release's skill text matches —
# there is no safe default path to guess, because a sibling checkout that merely
# EXISTS can be on an older commit with stale (pre-rename) names, which would
# silently overwrite a correct, hand-verified list with a wrong one and then fail
# lint for the wrong reason (this happened once — see the 0.13.0 release notes).
# Leave SS_TOOLS_JSON unset to keep the committed list as-is (the default and the
# safe choice for a routine release with no tool-name changes).
if [[ -n "${SS_TOOLS_JSON:-}" ]]; then
  [[ -f "$SS_TOOLS_JSON" ]] || err "SS_TOOLS_JSON='$SS_TOOLS_JSON' does not exist"
  run "python3 -c \"import json,sys; names=sorted(t['name'] for t in json.load(open('$SS_TOOLS_JSON'))); open('.maintainers/tool-names.txt','w').write('\\n'.join(names) + '\\n')\""
else
  log "Keeping the committed .maintainers/tool-names.txt as-is (set SS_TOOLS_JSON=<path to mcp-tools.json AT THE MATCHING COMMIT> to refresh it)"
fi

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
# OPT-IN since 2026-10-08: runs only with SS_RUN_PLUGIN_EVAL=1 (the operator ruled the
# ~50 agent runs per gate are not worth the usage on every release — run it when a skill's
# behaviour changed, not for text syncs); SS_PLUGIN_EVAL_MAX_COST_USD caps the
# list-price spend (default 20 — see .maintainers/README.md for the per-run cost and
# how to run a single case). Refuses the release on a non-zero exit.
EVAL_MAX_COST="${SS_PLUGIN_EVAL_MAX_COST_USD:-20}"
if [[ "${SS_RUN_PLUGIN_EVAL:-0}" != "1" || "${SS_SKIP_PLUGIN_EVAL:-0}" == "1" ]]; then
  log "Skipping plugin evals (opt-in: SS_RUN_PLUGIN_EVAL=1 runs them)."
elif [[ $DRY_RUN -eq 1 ]]; then
  echo "  DRY: claude plugin eval . --trust-plugin --json evals/results/promote-gate.json --threshold 0.8 --no-publish --max-cost-usd $EVAL_MAX_COST"
else
  log "Running plugin evals (max-cost-usd \$$EVAL_MAX_COST — set SS_PLUGIN_EVAL_MAX_COST_USD to change)..."
  command -v claude >/dev/null || err "claude CLI not found — required for the plugin-eval gate (unset SS_RUN_PLUGIN_EVAL to skip it)"
  claude plugin eval . --trust-plugin --json evals/results/promote-gate.json \
    --threshold 0.8 --no-publish --max-cost-usd "$EVAL_MAX_COST" \
    || err "plugin evals scored below threshold (or failed to run) — see evals/results/promote-gate.json. Fix the regression, or release without SS_RUN_PLUGIN_EVAL if you verified it separately."
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

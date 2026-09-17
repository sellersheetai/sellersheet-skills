#!/usr/bin/env bash
# Local lint for the sellersheet-skills public repo.
# Mirrors .github/workflows/lint.yml so you can catch failures before pushing.
# Run from anywhere: ./.maintainers/lint.sh
# Exits non-zero on any violation — wire as a pre-commit hook if you want.

set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

FAIL=0
log() { echo "[lint] $*"; }
err() { echo "[lint] ERROR: $*" >&2; FAIL=1; }

command -v jq >/dev/null || { echo "jq required (brew install jq / apt install jq)"; exit 2; }

# ---------- 1. manifests are valid JSON ----------
log "Validating JSON manifests..."
for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json versions.json docs/mcp-config/sellersheet.json .mcp.json; do
  jq empty "$f" 2>/dev/null || err "$f is not valid JSON"
done

# ---------- 2. SKILL.md frontmatter ----------
log "Checking SKILL.md frontmatter..."
for d in skills/*/; do
  name="$(basename "$d")"
  f="${d}SKILL.md"
  [[ -f "$f" ]] || { err "$d missing SKILL.md"; continue; }
  fm=$(awk '/^---$/{c++; next} c==1{print}' "$f")
  echo "$fm" | grep -q '^name:'        || err "$f missing 'name:' in frontmatter"
  echo "$fm" | grep -q '^description:' || err "$f missing 'description:' in frontmatter"
  fm_name=$(echo "$fm" | awk '/^name:/{sub(/^name:[ \t]*/,""); gsub(/['\''" ]/,""); print; exit}')
  [[ "$fm_name" == "$name" ]] || err "$f frontmatter name '$fm_name' != folder name '$name'"
done

# ---------- 2b. STRICT YAML frontmatter parse ----------
# grep-parsing is not enough: an unquoted "foo: bar" inside a description breaks
# js-yaml (used by npx skills AND plugin loaders) and the skill silently vanishes
# from installs — the image-gen 0.8.x lesson. Parse every frontmatter strictly.
log "Strict-YAML parsing frontmatter..."
YAML_CMD=""
if command -v python3 >/dev/null && python3 -c "import yaml" 2>/dev/null; then
  YAML_CMD="py"
elif command -v npx >/dev/null; then
  YAML_CMD="npx"
fi
if [[ -z "$YAML_CMD" ]]; then
  err "no strict YAML parser available (need python3+PyYAML or node/npx for js-yaml)"
else
  for d in skills/*/; do
    f="${d}SKILL.md"
    [[ -f "$f" ]] || continue
    awk '/^---$/{c++; next} c==1{print}' "$f" > /tmp/ss-fm.yaml
    if [[ "$YAML_CMD" == "py" ]]; then
      python3 -c "import yaml,sys; yaml.safe_load(open('/tmp/ss-fm.yaml'))" 2>/dev/null || err "$f frontmatter fails STRICT YAML parse (quote it or use >- block scalar)"
    else
      npx -y js-yaml /tmp/ss-fm.yaml >/dev/null 2>&1 || err "$f frontmatter fails STRICT YAML parse (quote it or use >- block scalar)"
    fi
    # Claude Code truncates listing descriptions at ~1536 chars — warn, don't fail
    dlen=$(awk '/^---$/{c++; next} c==1 && /^description:/{f=1} c==1 && f{print}' "$f" | wc -c | tr -d " ")
    [[ "$dlen" -le 1700 ]] || log "WARN: $f description ~${dlen} chars — Claude Code truncates the listing at 1536"
  done
fi

# ---------- 2c. cross-skill relative links resolve ----------
log "Checking cross-skill links..."
while IFS= read -r line; do
  src="${line%%:*}"
  link="${line#*:}"
  link="${link#](}"; link="${link%)}"
  [[ -e "$(dirname "$src")/$link" ]] || err "$src links to missing $link"
done < <(grep -rHoE '\]\(\.\./[a-z-]+/SKILL\.md\)' skills/*/SKILL.md 2>/dev/null)

# ---------- 2d. stale/forbidden strings (docs drift guard) ----------
log "Stale-string guard..."
# Private inputs (never committed — this file is public):
#   SS_INTERNAL_STRINGS  newline-separated fixed strings that must not appear in
#                        public content (internal repo / path / tool names)
#   SS_PRIVACY_PATTERNS  one extended regex of private identifiers (real store
#                        refs, brands, hostnames, mailboxes)
# Locally they come from .maintainers/private-patterns.local (gitignored); in CI
# from repository secrets of the same names (lint.yml). Missing = lint FAILS —
# a silent skip would let a leak through.
PRIVATE_LOCAL=".maintainers/private-patterns.local"
[[ -f "$PRIVATE_LOCAL" ]] && source "$PRIVATE_LOCAL"
declare -a FORBIDDEN=(
  "@sellersheet/mcp-server"                # npm package is a 404, removed 0.5.1
  "Settings → API"                         # dashboard page does not exist; real path: MCP & API keys
  "Stores → Connect Advertising"           # real UI: My Stores → Authorize Ads
  # -- drifted design constants purged 2026-08-15: must never reappear --
  "#10B881"
  "#283351"
  "#25314B"
  "#FFD76B"
  "#8B9FB3"
  "[0.063, 0.725, 0.506]"                  # 3-decimal floats truncate one RGB step low
  "[0.157, 0.2, 0.318]"
  "[1, 0.847, 0.42]"
  "[1.0, 0.847, 0.42]"
  "[0.549, 0.627, 0.702]"
  "[0.063,0.725,0.506]"                    # no-space variants of the same drifted floats
  "[0.157,0.2,0.318]"
  "[1,0.847,0.42]"
  "[0.549,0.627,0.702]"
  "OPTIONAL · 选填"                        # canonical tag is OPTIONAL · 可选
)
# -- internal-reference strings: public skills must be self-contained (2026-08-15) --
if [[ -z "${SS_INTERNAL_STRINGS:-}" ]]; then
  err "SS_INTERNAL_STRINGS not set — create $PRIVATE_LOCAL (see .maintainers/README.md) or the CI secret"
else
  while IFS= read -r pat; do
    [[ -n "$pat" ]] && FORBIDDEN+=("$pat")
  done <<< "$SS_INTERNAL_STRINGS"
fi
for pat in "${FORBIDDEN[@]}"; do
  H=$(grep -rFn "$pat" skills/ docs/ README.md README.zh-CN.md install.sh 2>/dev/null || true)
  [[ -z "$H" ]] || { err "forbidden stale string \"$pat\":"; echo "$H" | head -5 >&2; }
done

# ---------- 3. version unified across every file ----------
log "Checking version is unified..."
PV=$(jq -r '.version' .claude-plugin/plugin.json)
[[ "$PV" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || err "plugin.json version '$PV' is not semver"
if [[ "$(jq -r '.plugins[0] | has("version")' .claude-plugin/marketplace.json)" == "true" ]]; then
  err "marketplace.json plugin entry has a 'version' field — remove it; plugin.json is the single source of truth"
fi
for d in skills/*/; do
  sv=$(awk '/^---$/{c++; if(c==2)exit; next} c==1 && /^version:/{sub(/^version:[ \t]*/,""); gsub(/['\''" ]/,""); print; exit}' "${d}SKILL.md")
  [[ "$sv" == "$PV" ]] || err "${d}SKILL.md version '$sv' != plugin.json '$PV'"
done
[[ "$(jq -r '.marketplace_version' versions.json)" == "$PV" ]] || err "versions.json marketplace_version != $PV"
while read -r sv; do
  [[ "$sv" == "$PV" ]] || err "versions.json skill latest_version '$sv' != $PV"
done < <(jq -r '.skills[].latest_version' versions.json)
iv=$(awk -F'"' '/^VERSION=/{print $2; exit}' install.sh)
[[ "$iv" == "$PV" ]] || err "install.sh VERSION '$iv' != $PV"
grep -qF "v$PV" README.md          || err "README.md has no 'v$PV' reference"
grep -qE "^## \[$PV\]" CHANGELOG.md || err "CHANGELOG.md has no '## [$PV]' entry"

# ---------- 4. marketplace.json matches the repo ----------
log "Checking marketplace.json..."
[[ "$(jq '.plugins | length' .claude-plugin/marketplace.json)" == "1" ]] || err "expected exactly 1 plugin entry"
[[ "$(jq -r '.plugins[0].name' .claude-plugin/marketplace.json)" == "sellersheet-skills" ]] || err "plugin entry name != sellersheet-skills"
[[ "$(jq -r '.plugins[0].source' .claude-plugin/marketplace.json)" == "./" ]] || err "plugin source != ./"
[[ "$(jq -r '.name' .claude-plugin/plugin.json)" == "sellersheet-skills" ]] || err "plugin.json name != sellersheet-skills"
vj=$(jq -r '.skills[].name' versions.json | sort | tr '\n' ' ')
fs=$(ls -1 skills/ | sort | tr '\n' ' ')
[[ "$vj" == "$fs" ]] || err "versions.json skills ($vj) != skills/ folder ($fs)"

# ---------- 4b. skills_catalog contract (consumed by MCP get_user_context) ----------
log "Checking skills_catalog contract..."
for k in claude-code claude-code-update codex codex-update codebuddy codebuddy-update other other-update update; do
  v=$(jq -r --arg k "$k" '.install_commands[$k] // empty' versions.json)
  [[ -n "$v" ]] || err "versions.json install_commands missing '$k'"
done
for k in claude-code-update codex-update codebuddy-update; do
  v=$(jq -r --arg k "$k" '.install_commands[$k] // empty' versions.json)
  [[ "$v" != *install.sh* ]] || err "install_commands.$k points plugin users at install.sh (duplicate-source hazard)"
done
jq -e '[.skills[] | select((.description // "") == "")] | length == 0' versions.json >/dev/null \
  || err "versions.json has a skill with an empty description"

# ---------- 4c. plugin-bundled MCP contract ----------
# Flat shape (no mcpServers wrapper) — the shape Claude Code and Codex example
# plugins use; both loaders verified live 2026-07-16 (wrapped also parses, but
# flat is the convention we standardize on).
log "Checking plugin .mcp.json contract..."
[[ "$(jq -r '.sellersheet.type' .mcp.json)" == "http" ]]  || err ".mcp.json sellersheet type must be http (remote — never a local command)"
[[ "$(jq -r '.sellersheet.url' .mcp.json)" == "https://sellersheetai.com/mcp" ]] || err ".mcp.json sellersheet url drifted"
[[ "$(jq -r '.sellersheet | has("command")' .mcp.json)" == "false" ]] || err ".mcp.json must not bundle a local command (the 0.5.0 lesson)"
[[ "$(jq -r 'has("mcpServers")' .mcp.json)" == "false" ]] || err ".mcp.json must be the FLAT plugin shape — no mcpServers wrapper"
grep -qiE "bearer|api_key|token" .mcp.json && err ".mcp.json must stay keyless (OAuth on first use)" || true

# ---------- 5. privacy + ASIN scan ----------
log "Privacy + ASIN scan..."
if [[ -z "${SS_PRIVACY_PATTERNS:-}" ]]; then
  err "SS_PRIVACY_PATTERNS not set — create $PRIVATE_LOCAL (see .maintainers/README.md) or the CI secret"
else
  HITS=$(grep -rEn "$SS_PRIVACY_PATTERNS" skills/ docs/ README.md README.zh-CN.md CHANGELOG.md 2>/dev/null || true)
  [[ -z "$HITS" ]] || { err "private identifiers detected:"; echo "$HITS" | head -20 >&2; }
fi
ASIN=$(grep -rEn '\bB0[A-Z0-9]{8}\b' skills/ docs/ README.md CHANGELOG.md 2>/dev/null | grep -vE '(B0ABCDEFGH|B0ABCDEFG[0-9]|B0XXXXXXXX)' || true)
[[ -z "$ASIN" ]] || { err "real-looking ASINs detected (use B0ABCDEFGH):"; echo "$ASIN" | head -10 >&2; }

# ---------- 6. Tencent WorkBuddy connector files (dual-format root) ----------
# The repo root is ALSO a WorkBuddy "MCP + Skill" connector: connector-meta.json,
# mcp.json, icon.svg + description_zh/description_en/author in every SKILL.md.
# Plugin loaders ignore those extras (verified on CodeBuddy, Codex, npx skills
# 2026-09-17). sync_workbuddy.py derives them; nothing here is hand-edited.
log "Checking WorkBuddy connector files..."
for f in connector-meta.json mcp.json; do
  jq empty "$f" 2>/dev/null || err "$f is not valid JSON"
done
[[ -f icon.svg ]] || err "icon.svg missing at the repo root (WorkBuddy marketplace icon, hand-maintained)"
[[ "$(jq -r '.version' connector-meta.json)" == "$PV" ]] || err "connector-meta.json version != $PV"
[[ "$(jq -r '.source' connector-meta.json)" == "sellersheet" ]] || err "connector-meta.json source must stay 'sellersheet' (global id on WorkBuddy)"
[[ "$(jq -r '.mcpServers | length' mcp.json)" == "1" ]] || err "mcp.json must declare exactly one server (WorkBuddy rule)"
[[ "$(jq -r '.mcpServers.sellersheet.type' mcp.json)" == "streamableHttp" ]] || err "mcp.json type must be streamableHttp"
[[ "$(jq -r '.mcpServers.sellersheet.url' mcp.json)" == "https://sellersheetai.com/mcp" ]] || err "mcp.json url drifted"
grep -qiE "bearer|api_key|token" mcp.json && err "mcp.json must stay keyless (WorkBuddy runs the OAuth flow)" || true
for d in skills/*/; do
  fm=$(awk '/^---$/{c++; next} c==1{print}' "${d}SKILL.md")
  for k in description_zh description_en author; do
    echo "$fm" | grep -q "^$k:" || err "${d}SKILL.md frontmatter missing '$k:' (WorkBuddy requires it — run sync_workbuddy.py)"
  done
done
[[ -d mcp ]] && err "a top-level mcp/ directory is read by CodeBuddy as plugin MCP config — keep snippets under docs/mcp-config/" || true
python3 .maintainers/sync_workbuddy.py --check >/dev/null 2>&1 || err "WorkBuddy connector files stale — run python3 .maintainers/sync_workbuddy.py"

# ---------- summary ----------
echo ""
if [[ $FAIL -eq 0 ]]; then
  log "All checks passed ✓"
  exit 0
else
  log "Lint FAILED — fix the issues above before pushing."
  exit 1
fi

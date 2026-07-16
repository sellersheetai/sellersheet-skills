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
for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json versions.json mcp/sellersheet.json; do
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
declare -a FORBIDDEN=(
  "@sellersheet/mcp-server"                # npm package is a 404, removed 0.5.1
  "Settings → API"                         # dashboard page does not exist; real path: MCP & API keys
  "auto-registers the SellerSheet MCP"     # .mcp.json auto-register died in 0.5.1
  "Stores → Connect Advertising"           # real UI: My Stores → Authorize Ads
)
for pat in "${FORBIDDEN[@]}"; do
  H=$(grep -rFn "$pat" skills/ docs/ README.md mcp/ install.sh 2>/dev/null || true)
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
for k in claude-code claude-code-update codex codex-update other other-update update; do
  v=$(jq -r --arg k "$k" '.install_commands[$k] // empty' versions.json)
  [[ -n "$v" ]] || err "versions.json install_commands missing '$k'"
done
for k in claude-code-update codex-update; do
  v=$(jq -r --arg k "$k" '.install_commands[$k] // empty' versions.json)
  [[ "$v" != *install.sh* ]] || err "install_commands.$k points plugin users at install.sh (duplicate-source hazard)"
done
jq -e '[.skills[] | select((.description // "") == "")] | length == 0' versions.json >/dev/null \
  || err "versions.json has a skill with an empty description"

# ---------- 5. privacy + ASIN scan ----------
log "Privacy + ASIN scan..."
PAT='(\bSS-[A-Z]{2}\b|\bTJ-[A-Z]{2}\b|\bSML-[A-Z]{2}\b|\bSmilee\b|\bYumLock\b|\bSpireHues\b|sellersheet0430|sellersheet-bot@|tjme-amz|test\.sellersheetai|/home/claude/listing-optimizer-workspace)'
HITS=$(grep -rEn "$PAT" skills/ docs/ README.md CHANGELOG.md 2>/dev/null || true)
[[ -z "$HITS" ]] || { err "private identifiers detected:"; echo "$HITS" | head -20 >&2; }
ASIN=$(grep -rEn '\bB0[A-Z0-9]{8}\b' skills/ docs/ README.md CHANGELOG.md 2>/dev/null | grep -vE '(B0ABCDEFGH|B0ABCDEFG[0-9]|B0XXXXXXXX)' || true)
[[ -z "$ASIN" ]] || { err "real-looking ASINs detected (use B0ABCDEFGH):"; echo "$ASIN" | head -10 >&2; }

# ---------- summary ----------
echo ""
if [[ $FAIL -eq 0 ]]; then
  log "All checks passed ✓"
  exit 0
else
  log "Lint FAILED — fix the issues above before pushing."
  exit 1
fi

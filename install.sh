#!/usr/bin/env bash
# SellerSheet Skills installer
# https://github.com/sellersheetai/sellersheet-skills
#
# Usage:
#   bash <(curl -fsSL https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main/install.sh)
#   bash <(curl -fsSL ...) --target claude-code
#   bash <(curl -fsSL ...) --target openclaw --path /your/openclaw/skills
#   bash <(curl -fsSL ...) --skills "sellersheet sellersheet-sheets"
#   bash <(curl -fsSL ...) --update

set -euo pipefail

REPO_URL="https://github.com/sellersheetai/sellersheet-skills.git"
REPO_RAW="https://raw.githubusercontent.com/sellersheetai/sellersheet-skills/main"
VERSION="0.8.4"

# ---------- args ----------
TARGET=""
PATH_OVERRIDE=""
SKILLS=""
UPDATE=0
DRY_RUN=0
CHECK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)    TARGET="$2"; shift 2 ;;
    --path)      PATH_OVERRIDE="$2"; shift 2 ;;
    --skills)    SKILLS="$2"; shift 2 ;;
    --update)    UPDATE=1; shift ;;
    --check)     CHECK=1; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    --version)   echo "sellersheet-skills installer $VERSION"; exit 0 ;;
    --help|-h)   cat <<EOF
SellerSheet Skills installer v$VERSION

Usage: install.sh [OPTIONS]

OPTIONS:
  --target <agent>     One of: claude-code, claude-desktop, codex, gemini,
                       antigravity, openclaw, hermes, generic. Auto-detected
                       if omitted.
  --path <dir>         Override the default skills directory for the target.
                       Required for openclaw, hermes, generic.
  --skills "<list>"    Space-separated skill names to install. Default: all.
                       Available skills:
                         sellersheet-sheets sellersheet-dashboard report-data image-gen
  --update             Pull the latest version and re-install.
  --check              Compare installed skill versions vs the latest available;
                       print a status table and exit (no install/update).
  --dry-run            Show what would happen without making changes.
  --version            Print installer version.
  --help               This help.

EXAMPLES:
  install.sh                                  # auto-detect + install all
  install.sh --target claude-code             # global ~/.claude/skills
  install.sh --target codex                   # ~/.codex/skills
  install.sh --target openclaw --path /opt/openclaw/skills
  install.sh --skills "sellersheet-sheets report-data"
EOF
                exit 0 ;;
    *)           echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# ---------- helpers ----------
log()  { echo "[sellersheet-skills] $*"; }
warn() { echo "[sellersheet-skills] WARN: $*" >&2; }
err()  { echo "[sellersheet-skills] ERROR: $*" >&2; exit 1; }
run()  { if [[ $DRY_RUN -eq 1 ]]; then echo "  DRY: $*"; else eval "$*"; fi; }

detect_os() {
  case "$(uname -s)" in
    Darwin*)   echo "macos" ;;
    Linux*)    echo "linux" ;;
    MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
    *)         echo "unknown" ;;
  esac
}

OS=$(detect_os)
log "Detected OS: $OS"

# ---------- target paths per agent ----------
default_path_for_target() {
  local t="$1"
  case "$t" in
    claude-code)
      echo "$HOME/.claude/skills" ;;
    claude-desktop)
      case "$OS" in
        macos)   echo "$HOME/Library/Application Support/Claude/skills" ;;
        linux)   echo "$HOME/.config/Claude/skills" ;;
        windows) echo "$APPDATA/Claude/skills" ;;
      esac ;;
    codex)
      echo "$HOME/.codex/skills" ;;
    gemini)
      echo "$HOME/.gemini/skills" ;;
    antigravity)
      echo "$HOME/.antigravity/skills" ;;
    openclaw|hermes|generic)
      echo ""  # requires --path
      ;;
  esac
}

detect_target() {
  # Auto-detect by which agent's config dir exists
  if [[ -d "$HOME/.claude" ]];      then echo "claude-code"; return; fi
  if [[ -d "$HOME/.codex" ]];       then echo "codex"; return; fi
  if [[ -d "$HOME/.gemini" ]];      then echo "gemini"; return; fi
  if [[ -d "$HOME/.antigravity" ]]; then echo "antigravity"; return; fi
  echo "claude-code"  # default
}

# ---------- helper: read SKILL.md version frontmatter ----------
read_skill_version() {
  local dir="$1"
  awk '
    /^---$/  { count++; if (count==2) exit; next }
    count==1 && /^version:/ {
      sub(/^version:[ \t]*/, "")
      gsub(/[ '\''"]/, "")
      print
      exit
    }
  ' "$dir/SKILL.md" 2>/dev/null
}

# ---------- --check mode ----------
if [[ $CHECK -eq 1 ]]; then
  log "Checking installed vs available skill versions..."
  CACHE_DIR="$HOME/.cache/sellersheet-skills"
  if [[ ! -d "$CACHE_DIR/.git" ]]; then
    mkdir -p "$CACHE_DIR"
    git clone --quiet "$REPO_URL" "$CACHE_DIR"
  else
    (cd "$CACHE_DIR" && git pull --quiet 2>/dev/null || true)
  fi
  printf "\n%-30s  %-12s  %-12s  %s\n" "SKILL" "INSTALLED" "AVAILABLE" "STATUS"
  printf "%-30s  %-12s  %-12s  %s\n" "------------------------------" "------------" "------------" "----------"
  # Check each installed location: claude-code default, codex, gemini, etc.
  for default_target in claude-code codex gemini antigravity; do
    dir=$(default_path_for_target "$default_target" 2>/dev/null)
    [[ -z "$dir" ]] && continue
    [[ ! -d "$dir" ]] && continue
    for skill_dir in "$CACHE_DIR/skills"/*/; do
      name=$(basename "$skill_dir")
      latest=$(read_skill_version "$skill_dir")
      installed=$(read_skill_version "$dir/$name")
      if [[ -z "$installed" ]]; then
        installed="(missing)"; status="NOT INSTALLED — run install.sh"
      elif [[ "$installed" == "$latest" ]]; then
        status="up to date ✓"
      else
        status="OUTDATED — run install.sh --update"
      fi
      printf "%-30s  %-12s  %-12s  %s  [%s]\n" "$name" "$installed" "$latest" "$status" "$default_target"
    done
    break  # only show first detected target
  done
  echo ""
  log "Done."
  exit 0
fi

# ---------- resolve target + path ----------
if [[ -z "$TARGET" ]]; then
  TARGET=$(detect_target)
  log "Auto-detected target: $TARGET"
fi

if [[ -z "$PATH_OVERRIDE" ]]; then
  SKILLS_DIR=$(default_path_for_target "$TARGET")
  if [[ -z "$SKILLS_DIR" ]]; then
    err "Target '$TARGET' requires --path <dir>. See --help."
  fi
else
  SKILLS_DIR="$PATH_OVERRIDE"
fi

log "Target: $TARGET"
log "Skills directory: $SKILLS_DIR"

# ---------- clone / update the repo into a cache dir ----------
CACHE_DIR="$HOME/.cache/sellersheet-skills"
run "mkdir -p '$CACHE_DIR'"

if [[ -d "$CACHE_DIR/.git" ]]; then
  if [[ $UPDATE -eq 1 ]]; then
    log "Updating cached repo..."
    run "cd '$CACHE_DIR' && git pull --quiet"
  fi
else
  log "Cloning sellersheet-skills..."
  run "git clone --quiet '$REPO_URL' '$CACHE_DIR'"
fi

# ---------- determine skills to install ----------
if [[ -z "$SKILLS" ]]; then
  SKILLS=$(cd "$CACHE_DIR/skills" && ls -d */ 2>/dev/null | sed 's:/::g' | tr '\n' ' ')
  log "Installing all skills: $SKILLS"
else
  log "Installing selected skills: $SKILLS"
fi

# ---------- install ----------
run "mkdir -p '$SKILLS_DIR'"
INSTALL_COUNT=0
SKIP_COUNT=0

for s in $SKILLS; do
  SRC="$CACHE_DIR/skills/$s"
  DEST="$SKILLS_DIR/$s"
  if [[ ! -d "$SRC" ]]; then
    warn "Skill '$s' not found in repo, skipping."
    SKIP_COUNT=$((SKIP_COUNT+1))
    continue
  fi
  if [[ -e "$DEST" || -L "$DEST" ]]; then
    if [[ $UPDATE -eq 1 ]]; then
      run "rm -rf '$DEST'"
    else
      log "  $s — already installed (use --update to refresh)"
      SKIP_COUNT=$((SKIP_COUNT+1))
      continue
    fi
  fi
  # Copy not symlink so the install is portable + survives cache deletion
  run "cp -R '$SRC' '$DEST'"
  log "  installed $s"
  INSTALL_COUNT=$((INSTALL_COUNT+1))
done

log ""
log "Installed $INSTALL_COUNT skill(s), skipped $SKIP_COUNT."
log "Skills directory: $SKILLS_DIR"

# ---------- target-specific post-install hints ----------
case "$TARGET" in
  claude-desktop)
    log ""
    log "NEXT: copy the MCP config snippet from mcp/sellersheet.json into"
    log "your claude_desktop_config.json and restart Claude Desktop."
    log "  Config example: $CACHE_DIR/mcp/sellersheet.json" ;;
  claude-code)
    log ""
    log "NEXT: restart Claude Code or run /skills refresh to pick up the new skills." ;;
  codex|gemini|antigravity)
    log ""
    log "NEXT: restart your agent CLI to pick up the new skills." ;;
  openclaw|hermes|generic)
    log ""
    log "NEXT: configure your agent to scan $SKILLS_DIR for skill folders." ;;
esac
log "Done."

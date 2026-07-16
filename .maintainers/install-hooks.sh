#!/usr/bin/env bash
# Install the repo's git hooks. Run once per clone:
#   ./.maintainers/install-hooks.sh
#
# pre-push → runs .maintainers/lint.sh and BLOCKS the push on any failure.
# This is the local half of the guarantee; CI (lint.yml) is the remote half —
# both run the exact same script.

set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$REPO/.git/hooks/pre-push"

cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
# Auto-installed by .maintainers/install-hooks.sh — do not edit here.
echo "[pre-push] running .maintainers/lint.sh ..."
if ! "$(git rev-parse --show-toplevel)/.maintainers/lint.sh"; then
  echo ""
  echo "[pre-push] BLOCKED — lint failed. Fix the issues (see .maintainers/README.md) and retry."
  exit 1
fi
EOF
chmod +x "$HOOK"
echo "[install-hooks] pre-push hook installed at $HOOK"

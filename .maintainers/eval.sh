#!/usr/bin/env bash
# Run `claude plugin eval` on the plugin with the repo's evals/ suite.
#
# Since 0.17.0 the installed plugin is plugin/ and evals/ stays at the repo root so it never
# ships to users. `claude plugin eval` reads cases only from inside the plugin folder
# (`--eval-dir` refuses `..`), so this assembles a throwaway copy — plugin/ + evals/ — runs
# the eval there, and copies the run output back into evals/results/.
#
# Usage (every argument goes straight to `claude plugin eval`):
#   ./.maintainers/eval.sh --trust-plugin --threshold 0.8 --no-publish --max-cost-usd 20
#   ./.maintainers/eval.sh --case ads-list-campaigns-routes --runs 1 --ablation none --trust-plugin --max-cost-usd 2
# A relative --json path is relative to the repo root.

set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
command -v claude >/dev/null || { echo "[eval] claude CLI not found" >&2; exit 2; }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/sellersheet-eval.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
cp -R plugin/. "$TMP/"
rm -rf "$TMP/skills" && cp -RL plugin/skills "$TMP/skills"
mkdir -p "$TMP/evals" && (cd evals && tar --exclude ./results -cf - .) | (cd "$TMP/evals" && tar -xf -)

status=0
claude plugin eval "$TMP" "$@" || status=$?

if [[ -d "$TMP/evals/results" ]]; then
  mkdir -p evals/results
  cp -R "$TMP/evals/results/." evals/results/
fi
exit $status

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

python -m codex_runner --help >/dev/null

if command -v codexrun >/dev/null 2>&1; then
  codexrun --help >/dev/null
else
  echo "codexrun is not installed in the active environment; skipping CLI smoke check." >&2
fi

for path in \
  "$ROOT/README.md" \
  "$ROOT/SAFETY.md" \
  "$ROOT/EVALUATION-LICENSE.md"
do
  test -f "$path"
done

test -d "$ROOT/src/codex_runner/prompts"
test -d "$ROOT/src/codex_runner/schemas"

find "$ROOT/src/codex_runner/prompts" -type f | grep -q .
find "$ROOT/src/codex_runner/schemas" -type f | grep -q .

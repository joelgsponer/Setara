#!/bin/sh
# Run every test script headless. Fails if any prints an error.
#   tools/test.sh [speed]
# Needs built packs and a card folder (builder build, then image/make_card.py).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SAVE="$(mktemp -d)"
fail=0
for script in "$ROOT"/tests/*.lua; do
  work="$SAVE/$(basename "$script" .lua)"
  mkdir -p "$work/love/setara"
  cp -r "$ROOT/dist/card/setara/data/love/setara/packs" "$work/love/setara/"
  out="$("$ROOT/tools/shoot.sh" "$script" "${1:-6}" "$work" 2>&1)"
  if echo "$out" | grep -q -E "ERROR|Error|stack traceback"; then
    echo "FAIL $(basename "$script")"
    echo "$out" | head -20
    fail=1
  else
    echo "ok   $(basename "$script")"
  fi
done
echo "screenshots: $SAVE/*/love/setara/shots"
exit $fail

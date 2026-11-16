#!/bin/sh
# Run every test script headless. Fails if any prints an error.
#   tools/test.sh [speed]
# Needs built packs and a card folder (builder build, then image/make_card.py).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# The save folders sit beside the card folder so that the packs can be hard
# links: with every pack built, fourteen copies would fill the disk.
mkdir -p "$ROOT/dist/test-work"
SAVE="$(mktemp -d "$ROOT/dist/test-work/run.XXXXXX")"
find "$ROOT/dist/test-work" -mindepth 1 -maxdepth 1 -type d ! -path "$SAVE" -exec rm -r {} + 2>/dev/null
fail=0
for script in "$ROOT"/tests/*.lua; do
  work="$SAVE/$(basename "$script" .lua)"
  mkdir -p "$work/love/setara"
  cp -al "$ROOT/dist/card/setara/data/love/setara/packs" "$work/love/setara/" 2>/dev/null ||
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
if "$ROOT/tests/update/run.sh" >/dev/null 2>&1; then echo "ok   update"; else echo "FAIL update"; fail=1; fi
echo "screenshots: $SAVE/*/love/setara/shots"
exit $fail

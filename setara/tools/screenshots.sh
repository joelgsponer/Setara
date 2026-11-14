#!/bin/sh
# Retake the README screenshots into docs/img/: Dari (as on the device) and English mode.
#   tools/screenshots.sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/docs/img"
for mode in fa en; do
  SAVE="$(mktemp -d)"
  mkdir -p "$SAVE/love/setara"
  cp -r "$ROOT/dist/card/setara/data/love/setara/packs" "$SAVE/love/setara/"
  SETARA_LOCALE="$mode" "$ROOT/tools/shoot.sh" "$ROOT/tools/screenshots.lua" 4 "$SAVE"
  for f in "$SAVE"/love/setara/shots/*.png; do
    cp "$f" "$ROOT/docs/img/$(basename "$f" .png)-$mode.png"
  done
done
ls "$ROOT/docs/img" | wc -l

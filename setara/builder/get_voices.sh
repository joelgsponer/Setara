#!/bin/sh
# Download the local speech models used for building and testing (about 190 MB).
# They are stand-ins: the spec's production voices are ElevenLabs, and the
# Persian model is Iranian, not Afghan. See docs/speech.md.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)/voices"
mkdir -p "$DIR"
BASE=https://huggingface.co/rhasspy/piper-voices/resolve/main
for v in en/en_US/amy/medium/en_US-amy-medium en/en_US/ryan/medium/en_US-ryan-medium fa/fa_IR/amir/medium/fa_IR-amir-medium; do
  for e in onnx onnx.json; do
    f="$DIR/$(basename "$v").$e"
    [ -s "$f" ] || curl -fL -o "$f" "$BASE/$v.$e"
  done
done
echo "voices in $DIR"

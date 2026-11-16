#!/bin/sh
# Run the app headless with a test script and collect its screenshots.
#   tools/shoot.sh <script.lua> [speed] [save-dir]
# Screenshots land in <save-dir>/love/setara/shots/ (default: the card folder).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOVE="${SETARA_LOVE:-/opt/tools/squashfs-root/AppRun}"
export XDG_DATA_HOME="${3:-$ROOT/dist/card/setara/data}"
export SETARA_SCRIPT="$(realpath "$1")" SETARA_SPEED="${2:-6}" SETARA_SEED="${SETARA_SEED:-7}"
export ALSOFT_DRIVERS=null SDL_AUDIODRIVER=dummy LIBGL_ALWAYS_SOFTWARE=1
xvfb-run -a -s "-screen 0 ${SETARA_SCREEN:-1280x1024x24}" "$LOVE" "$ROOT/app" 2>&1 | grep -v -E "ALSA|ALSOFT|^$"
exit 0

#!/usr/bin/env python3
"""Assemble the SD card folder: the app, every built pack, and launchers.

  python3 image/make_card.py [--out dist/card]

Result:
  setara/
    setara.love         the app (a zip of app/)
    Setara.sh           launcher for the handheld firmware (and any Linux PC)
    Setara.bat          launcher for a Windows PC
    update/             drop new packs here; installed at the next start
    data/love/setara/   packs/, progress and counts (survives every update)

Copy the setara folder to the card. The same folder runs on a PC.
"""

import argparse
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SH = """#!/bin/sh
# Setara launcher. Keeps everything on the card, next to this script.
DIR="$(cd "$(dirname "$0")" && pwd)"
export XDG_DATA_HOME="$DIR/data"
mkdir -p "$DIR/data/love/setara/update" "$DIR/update"
# Packs dropped into update/ are handed to the app, which checks and installs them.
for f in "$DIR"/update/*.zip; do
  [ -f "$f" ] && mv "$f" "$DIR/data/love/setara/update/"
done
LOVE="${SETARA_LOVE:-}"
if [ -z "$LOVE" ]; then
  LOVE=love
  for c in "$DIR/love" "$DIR/bin/love" /usr/bin/love /usr/local/bin/love; do
    if [ -x "$c" ]; then LOVE="$c"; break; fi
  done
fi
exec "$LOVE" "$DIR/setara.love"
"""

BAT = """@echo off
rem Setara launcher for a Windows PC. Needs LOVE 11 (love2d.org) installed.
set DIR=%~dp0
set APPDATA=%DIR%data
if not exist "%DIR%data\\LOVE\\setara\\update" mkdir "%DIR%data\\LOVE\\setara\\update"
if exist "%DIR%update\\*.zip" move /y "%DIR%update\\*.zip" "%DIR%data\\LOVE\\setara\\update\\" >nul
"%ProgramFiles%\\LOVE\\love.exe" "%DIR%setara.love"
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "dist" / "card")
    ap.add_argument("--packs", type=Path, default=ROOT / "packs")
    args = ap.parse_args()

    card = args.out / "setara"
    save = card / "data" / "love" / "setara"
    # Progress and counts in data/ are never touched; only packs are replaced.
    (save / "packs").mkdir(parents=True, exist_ok=True)
    for old in (save / "packs").glob("*.zip"):
        old.unlink()
    (save / "update").mkdir(exist_ok=True)
    (card / "update").mkdir(exist_ok=True)

    with zipfile.ZipFile(card / "setara.love", "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted((ROOT / "app").rglob("*")):
            if path.is_file() and path.name != ".gitkeep":
                z.write(path, path.relative_to(ROOT / "app").as_posix())

    count = 0
    for pack in sorted(args.packs.glob("*.zip")):
        with zipfile.ZipFile(pack) as z:
            manifest = json.loads(z.read("manifest.json"))
        shutil.copy(pack, save / "packs" / f"{manifest['pack']}.v{manifest['version']}.zip")
        count += 1

    (card / "Setara.sh").write_text(SH)
    (card / "Setara.sh").chmod(0o755)
    (card / "Setara.bat").write_text(BAT.replace("\n", "\r\n"))
    version = (ROOT / "app" / "version.lua").read_text().split('"')[1]
    (card / "VERSION.txt").write_text(f"Setara {version}\n{count} packs\n")
    size = sum(f.stat().st_size for f in card.rglob("*") if f.is_file()) / 1e6
    print(f"card folder: {card}  ({count} packs, {size:.0f} MB)")


if __name__ == "__main__":
    main()

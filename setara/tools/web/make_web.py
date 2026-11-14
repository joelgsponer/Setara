#!/usr/bin/env python3
"""Build the browser version: the same app, compiled to run on a web page.

  python3 tools/web/make_web.py [--dari] [--out dist/web]

Needs the built packs (packs/*.zip), Node.js and the love.js package
(npm install love.js; set LOVEJS to its folder or install it next to this
repository). The result is a folder of static files: any web server can
serve it. It starts in English mode unless --dari is given.

The browser build is for trying the app and showing it. The product is the
handheld; nothing here changes what runs on the device.
"""
import argparse
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def find_lovejs() -> Path:
    for cand in (os.environ.get("LOVEJS"), ROOT / "node_modules" / "love.js", ROOT / "tools" / "web" / "node_modules" / "love.js",
                 "/opt/tools/web/node_modules/love.js"):
        if cand and (Path(cand) / "index.js").exists():
            return Path(cand)
    raise SystemExit("love.js not found: run `npm install love.js` in tools/web, or set LOVEJS")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "dist" / "web")
    ap.add_argument("--dari", action="store_true", help="start in Dari instead of English mode")
    ap.add_argument("--only", action="append", help="include only these packs (smaller download)")
    args = ap.parse_args()

    work = ROOT / "dist" / "web-work"
    love = work / "setara-web.love"
    work.mkdir(parents=True, exist_ok=True)
    packs = sorted((ROOT / "packs").glob("*.zip"))
    if not any(p.stem == "core" for p in packs):
        raise SystemExit("no core pack in packs/: run the builder first")
    # The .love holds the app and every pack, unpacked. Audio and pictures are
    # already compressed, so they are stored as they are.
    with zipfile.ZipFile(love, "w") as z:
        for path in sorted((ROOT / "app").rglob("*")):
            if path.is_file() and path.name != ".gitkeep":
                z.write(path, path.relative_to(ROOT / "app").as_posix(), zipfile.ZIP_DEFLATED)
        if not args.dari:
            z.writestr("english", "")
        for pack in packs:
            if args.only and pack.stem not in args.only and pack.stem != "core":
                continue
            with zipfile.ZipFile(pack) as src:
                for name in src.namelist():
                    kind = zipfile.ZIP_DEFLATED if name.endswith(".json") else zipfile.ZIP_STORED
                    z.writestr(zipfile.ZipInfo(f"webpacks/{pack.stem}/{name}"), src.read(name), kind)
    size = love.stat().st_size
    if args.out.exists():
        shutil.rmtree(args.out)
    # memory: the whole game file is held in memory, plus room for the app itself
    memory = (size + 160 * 1024 * 1024) // (1 << 20) * (1 << 20)
    subprocess.run(["node", str(find_lovejs() / "index.js"), "-c", "-t", "Setara", "-m", str(memory), str(love), str(args.out)],
                   check=True)
    page = (Path(__file__).parent / "index.html").read_text("utf-8").replace("__MEMORY__", str(memory))
    (args.out / "index.html").write_text(page, "utf-8")
    shutil.rmtree(args.out / "theme", ignore_errors=True)
    version = (ROOT / "app" / "version.lua").read_text().split('"')[1]
    (args.out / "version.json").write_text(json.dumps({"version": version, "packs": [p.stem for p in packs]}))
    total = sum(f.stat().st_size for f in args.out.rglob("*") if f.is_file()) / 1e6
    print(f"web build: {args.out}  ({total:.0f} MB)")
    print("try it:  cd", args.out, "&& python3 -m http.server 8000")


if __name__ == "__main__":
    main()

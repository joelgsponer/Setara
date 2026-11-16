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
import hashlib
import subprocess
from concurrent.futures import ThreadPoolExecutor
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def find_lovejs() -> Path:
    for cand in (os.environ.get("LOVEJS"), ROOT / "node_modules" / "love.js", ROOT / "tools" / "web" / "node_modules" / "love.js",
                 "/opt/tools/web/node_modules/love.js"):
        if cand and (Path(cand) / "index.js").exists():
            return Path(cand)
    raise SystemExit("love.js not found: run `npm install love.js` in tools/web, or set LOVEJS")


PREVIEW = ["en-1", "fa-1", "fa-1-alphabet", "math-1", "garden-1", "garden-4", "garden-4-world",
           "teacher-en-1", "guide-math-1", "guide-garden-1"]


def lighter(data: bytes, cache: Path) -> bytes:
    """A speech clip at a lower rate for the browser (16 kHz, low quality): about
    a third of the size. The card keeps the full clips. Cached by content."""
    cache.mkdir(parents=True, exist_ok=True)
    # the settings are part of the name: the cache outlives builds (Dockerfile)
    settings = ["-ar", "16000", "-ac", "1", "-c:a", "libvorbis", "-q:a", "0"]
    out = cache / (hashlib.sha1(data + repr(settings).encode()).hexdigest() + ".ogg")
    if not out.exists():
        tmp = out.with_suffix(f".{os.getpid()}.{hashlib.sha1(os.urandom(8)).hexdigest()[:6]}.ogg")
        done = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "pipe:0", *settings, str(tmp)], input=data)
        if done.returncode != 0 or not tmp.exists():
            return data
        tmp.replace(out)
    small = out.read_bytes()
    return small if 0 < len(small) < len(data) else data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "dist" / "web")
    ap.add_argument("--dari", action="store_true", help="start in Dari instead of English mode")
    ap.add_argument("--headroom", type=int, default=160, help="memory beyond the game file, in MB")
    ap.add_argument("--slow", action="store_true", help="include the slow speech variants (much larger)")
    ap.add_argument("--light-audio", action="store_true", help="re-encode speech at 16 kHz: a smaller download, duller sound")
    ap.add_argument("--only", action="append", help="include only these packs (smaller download)")
    ap.add_argument("--all", action="store_true", help="every pack (well over a gigabyte: too much for a browser)")
    args = ap.parse_args()
    if not args.only and not args.all:
        # The whole content is far too large for one download. The preview
        # carries level 1 of every subject, the Dari alphabet, health 4 with the
        # geography pack, the first lesson book and two guides: about 185 MB.
        args.only = PREVIEW

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
                names = [n for n in src.namelist() if args.slow or not n.endswith(".slow.ogg")]
                # X then repeats at normal speed without the slow variants; halves the download
                blobs = {n: src.read(n) for n in names}
            if args.light_audio:
                oggs = [n for n in names if n.endswith(".ogg")]
                with ThreadPoolExecutor(os.cpu_count() or 4) as pool:
                    for n, small in zip(oggs, pool.map(lambda n: lighter(blobs[n], work / "audio"), oggs)):
                        blobs[n] = small
            for name in names:
                kind = zipfile.ZIP_DEFLATED if name.endswith(".json") else zipfile.ZIP_STORED
                z.writestr(zipfile.ZipInfo(f"webpacks/{pack.stem}/{name}"), blobs[name], kind)
    size = love.stat().st_size
    if args.out.exists():
        shutil.rmtree(args.out)
    # memory: the whole game file is held in memory, plus room for the app itself
    memory = (size + args.headroom * 1024 * 1024) // (1 << 20) * (1 << 20)
    subprocess.run(["node", str(find_lovejs() / "index.js"), "-c", "-t", "Setara", "-m", str(memory), str(love), str(args.out)],
                   check=True)
    # The stock loader also stores the whole data file in the browser's
    # database after the download. With a large file that write never returns
    # and the app never starts, so the data goes straight to the app; the
    # browser's ordinary cache still keeps it for the next visit.
    loader = (args.out / "game.js").read_text("utf-8")
    start = loader.index("cacheRemotePackage(db, PACKAGE_PATH + PACKAGE_NAME, packageData")
    end = loader.index("}", loader.index("processPackageData(packageData);", start)) + 1
    end = loader.index(");", end) + 2
    loader = loader[:start] + "processPackageData(packageData);" + loader[end:]
    (args.out / "game.js").write_text(loader, "utf-8")
    page = (Path(__file__).parent / "index.html").read_text("utf-8").replace("__MEMORY__", str(memory))
    (args.out / "index.html").write_text(page, "utf-8")
    shutil.rmtree(args.out / "theme", ignore_errors=True)
    assets = Path(__file__).parent / "assets"      # logo and fonts of the host page
    if assets.is_dir():
        shutil.copytree(assets, args.out / "assets")
    version = (ROOT / "app" / "version.lua").read_text().split('"')[1]
    (args.out / "version.json").write_text(json.dumps({"version": version, "packs": [p.stem for p in packs if not args.only or p.stem in args.only or p.stem == "core"]}))
    total = sum(f.stat().st_size for f in args.out.rglob("*") if f.is_file()) / 1e6
    print(f"web build: {args.out}  ({total:.0f} MB)")
    print("try it:  cd", args.out, "&& python3 -m http.server 8000")


if __name__ == "__main__":
    main()

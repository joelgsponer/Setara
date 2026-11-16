#!/usr/bin/env python3
"""Write dist/mobile/setara.love: the app with a choice of packs inside, for
the iOS build (it goes into the Xcode project as a resource) and for anyone
who wants one file to run with LÖVE.

  python3 tools/mobile/make_love.py [--all | --only <pack> ...] [--english] [--slow]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bundle import ROOT, STARTER, write_love   # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--out", type=Path, default=ROOT / "dist" / "mobile" / "setara.love")
ap.add_argument("--all", action="store_true")
ap.add_argument("--only", action="append")
ap.add_argument("--slow", action="store_true")
ap.add_argument("--english", action="store_true")
args = ap.parse_args()
inside = write_love(args.out, None if args.all else (args.only or STARTER), args.slow, args.english)
print(f"{args.out}  ({args.out.stat().st_size / 1e6:.0f} MB, {len(inside) - 1} packs)")

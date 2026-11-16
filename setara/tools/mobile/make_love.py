#!/usr/bin/env python3
"""Write dist/mobile/setara.love: the app with a choice of packs inside, for
the iOS build (it goes into the Xcode project as a resource) and for trying
the phone version on a PC.

  python3 tools/mobile/make_love.py [--all | --only <pack> ...] [--english]
                                    [--packs-url http://host/path]

With --packs-url the app can fetch the packs it does not carry: every pack
is also written to dist/mobile/store/, to be put on a web server at that
address, and the list of them is baked into the app.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bundle import ROOT, STARTER, write_love, write_store   # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--out", type=Path, default=ROOT / "dist" / "mobile" / "setara.love")
ap.add_argument("--all", action="store_true")
ap.add_argument("--only", action="append")
ap.add_argument("--english", action="store_true")
ap.add_argument("--packs-url")
args = ap.parse_args()
catalogue = write_store(args.out.parent / "store", args.packs_url) if args.packs_url else None
inside = write_love(args.out, None if args.all else (args.only or STARTER), args.english, catalogue)
print(f"{args.out}  ({args.out.stat().st_size / 1e6:.0f} MB, {len(inside) - 1} packs inside)")
if catalogue:
    total = sum(p["size"] for p in catalogue["packs"]) / 1e6
    print(f"{args.out.parent / 'store'}  ({len(catalogue['packs'])} packs to fetch, {total:.0f} MB): serve it at {catalogue['base']}")

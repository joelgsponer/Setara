"""Command line entry point of the Setara pack builder.

  python3 -m setara_builder.cli validate      check every sheet, write nothing
  python3 -m setara_builder.cli build         validate, then write packs/*.zip

Building generates missing speech, shapes the Dari text, renders the pictures
and writes one checksummed zip per pack.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .build import build

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="setara-build", description="Setara pack builder")
    parser.add_argument("command", choices=("validate", "build"))
    parser.add_argument("--content", type=Path, default=ROOT / "content", help="authoring sources")
    parser.add_argument("--out", type=Path, default=ROOT / "packs", help="where packs are written")
    parser.add_argument("--tts", choices=("piper", "espeak", "elevenlabs", "silent"), help="speech provider")
    parser.add_argument("--only", action="append", help="build only this pack id (repeatable)")
    parser.add_argument("--strict", action="store_true", help="treat missing pictures as errors")
    parser.add_argument("--quiet", action="store_true", help="do not list warnings")
    args = parser.parse_args(argv)

    out = args.out if args.command == "build" else None
    report = build(args.content, out, tts=args.tts, only=args.only, strict=args.strict)
    if not args.quiet:
        for w in report.warnings:
            print(f"warning: {w}")
    else:
        print(f"{len(report.warnings)} warnings")
    for e in report.errors:
        print(f"ERROR: {e}", file=sys.stderr)
    if report.errors:
        print(f"{len(report.errors)} errors. Packs with errors were not written.", file=sys.stderr)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

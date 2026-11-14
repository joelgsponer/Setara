"""Command line entry point. Scaffold only: the steps are named, none is built.

Planned pipeline (spec section 9), one command end to end:
  validate  every row of every authoring sheet
  speech    generate missing audio (ElevenLabs), cached
  shape     reshape and reorder Dari text into draw order, pre-break lines
  images    compress pictures to small PNGs
  pack      write level files, manifest and checksums into one zip per pack
"""

import argparse
import sys

STEPS = ("validate", "speech", "shape", "images", "pack")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="setara-build", description=__doc__.split("\n")[0])
    parser.add_argument("step", choices=(*STEPS, "all"), help="pipeline step to run")
    parser.add_argument("--content", default="../content", help="authoring sources")
    parser.add_argument("--out", default="../packs", help="where packs are written")
    args = parser.parse_args(argv)
    print(f"setara-build: step '{args.step}' is not implemented yet", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

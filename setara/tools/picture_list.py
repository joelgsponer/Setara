#!/usr/bin/env python3
"""List every picture the content uses, with its drawing brief, and whether it is drawn.

  python3 tools/picture_list.py            all pictures
  python3 tools/picture_list.py --missing  only the ones without an SVG
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "builder"))
from setara_builder import build as B  # noqa: E402
from setara_builder.tts import Speech  # noqa: E402

content = ROOT / "content"
briefs = {}
for f in sorted(content.rglob("pictures.txt")):
    for line in f.read_text("utf-8").splitlines():
        m = re.match(r"^([a-z0-9_]+):\s*(.+)$", line.strip())
        if m:
            briefs.setdefault(m.group(1), m.group(2))

used = {}
report, speech = B.Report(), Speech("silent")
for src in B.find_packs(content):
    pack = B.Pack(src, content, speech, report, make_audio=False)
    kind = pack.meta.get("kind", "learner")
    {"learner": B.build_learner, "teacher": B.build_teacher, "core": B.build_core}[kind](pack)
    for name in pack.pictures:
        used.setdefault(name, []).append(pack.id)

missing_only = "--missing" in sys.argv
for name in sorted(used):
    drawn = (content / "pictures" / f"{name}.svg").exists()
    if missing_only and drawn:
        continue
    print(f"{name}: {briefs.get(name, '(no brief)')}  [{', '.join(sorted(used[name]))}]")
print(f"# {len(used)} pictures used, {sum((content / 'pictures' / (n + '.svg')).exists() for n in used)} drawn", file=sys.stderr)

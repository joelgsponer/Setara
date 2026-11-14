#!/usr/bin/env python3
"""Rewrite the content table in README.md from the built packs."""
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = ["| Pack | Games | Rounds | Size |", "| --- | --- | --- | --- |"]
total = 0
for z in sorted((ROOT / "packs").glob("*.zip")):
    m = json.loads(zipfile.ZipFile(z).read("manifest.json"))
    size = f"{z.stat().st_size / 1e6:.0f} MB"
    if m["kind"] == "learner":
        n = sum(len(g["rounds"]) for g in m["games"])
        total += n
        rows.append(f"| `{m['pack']}` {m['title_en']} | {len(m['games'])} | {n} | {size} |")
    elif m["kind"] == "teacher":
        rows.append(f"| `{m['pack']}` {m['title_en']} | {len(m.get('lessons', []))} lessons, Phrase Board, tips | | {size} |")
    else:
        rows.append(f"| `{m['pack']}` app strings and tutorial | | | {size} |")
rows.append(f"| **Total** | | **{total}** | |")
pictures = len(list((ROOT / "content" / "pictures").glob("*.svg")))
readme = ROOT / "README.md"
text = readme.read_text("utf-8")
text = re.sub(r"<!-- content -->.*?<!-- /content -->", "<!-- content -->\n" + "\n".join(rows) + "\n<!-- /content -->", text, flags=re.S)
text = re.sub(r"\| Pictures \| \S+ drawn", f"| Pictures | {pictures} drawn", text)
readme.write_text(text, "utf-8")
print("\n".join(rows))

#!/usr/bin/env python3
"""Print the teacher's guides: one HTML file per guide pack, for paper.

  python3 tools/guide_book.py [--out dist/guide] [--english]

Reads content/guide/*/guide.csv (the same sheets the device shows), puts the
figures in as pictures, and writes Dari from right to left. With --english
the AI's English of every page is printed under it, for reviewers. Open the
file in a browser and print it, or save it as PDF.
"""

import argparse
import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"goal": ("هدف درس", "Goal"), "know": ("دانستنی برای معلم", "What the teacher should know"),
         "explain": ("چطور توضیح بدهیم", "How to explain it"), "figure": ("شکل", "Figure"),
         "example": ("مثال", "Example"), "mistake": ("اشتباه‌های معمول", "Common mistakes"),
         "activity": ("فعالیت در صنف", "Activity in class"), "games": ("بازی‌های دستگاه", "Games on the device"),
         "check": ("ارزیابی", "How to check")}
CSS = """
body { font: 16px/1.9 'Noto Naskh Arabic', 'Noto Sans Arabic', serif; color: #3b2f2f; max-width: 46em; margin: 2em auto; padding: 0 1em; }
h1 { font-size: 1.7em; border-bottom: 3px solid #2f6f73; padding-bottom: .2em; }
h2 { font-size: 1.3em; margin-top: 2em; color: #2f6f73; page-break-after: avoid; }
.page { margin: .7em 0; padding: .5em .9em; border-right: 5px solid #d8cbb0; page-break-inside: avoid; }
.page b { display: block; color: #2f6f73; }
.goal { border-color: #4e9a51; } .mistake { border-color: #e0483f; } .activity { border-color: #4e9a51; }
.figure, .example { border-color: #f2b705; } .games { border-color: #e07a3f; }
.fig { display: flex; flex-wrap: wrap; gap: 6px; margin: .4em 0; }
.fig svg { width: 84px; height: 84px; } .fig.scene svg { width: 260px; height: 195px; }
.fig.word { font-size: 3em; line-height: 1.4; padding: 0 .3em; border: 2px solid #d8cbb0; border-radius: 10px; display: inline-block; }
.en { direction: ltr; text-align: left; font: 13px/1.5 system-ui, sans-serif; color: #6b5d4f; margin-top: .3em; }
@media print { body { margin: 0; } h2 { page-break-before: auto; } }
"""


def figure(spec: str) -> str:
    # written things: a Dari word, a Latin word, one form of a letter
    if spec.startswith("f:") or spec.startswith("t:"):
        return f'<div class="fig word">{html.escape(spec[2:])}</div>'
    if spec.startswith("lf:"):
        _, letter, form = (spec.split(":") + ["alone"])[:3]
        join = "\u0640"   # a joining stroke shows the start, middle and end forms
        shown = {"alone": letter, "start": letter + join, "middle": join + letter + join, "end": join + letter}.get(form, letter)
        return f'<div class="fig word">{html.escape(shown)}</div>'
    m = re.fullmatch(r"p:([a-z0-9_]+)\*(\d+)", spec)
    name, count = (m.group(1), int(m.group(2))) if m else (spec, 1)
    svg = ROOT / "content" / "pictures" / f"{name}.svg"
    if not svg.exists():
        return ""
    body = re.sub(r"<\?xml[^>]*\?>", "", svg.read_text("utf-8"))
    kind = "fig scene" if name.startswith("scene_") else "fig"
    return f'<div class="{kind}">' + body * count + "</div>"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "dist" / "guide")
    ap.add_argument("--english", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    en = {}
    if args.english:
        for f in sorted((ROOT / "content" / "i18n").glob("*.csv")):
            with open(f, encoding="utf-8", newline="") as fh:
                for row in csv.DictReader(fh):
                    if row.get("fa") and row.get("en"):
                        en[row["fa"].strip()] = row["en"].strip()
    for pack_json in sorted((ROOT / "content" / "guide").glob("*/pack.json")):
        meta = json.loads(pack_json.read_text("utf-8"))
        out = [f"<!doctype html><html lang='fa' dir='rtl'><meta charset='utf-8'><title>{html.escape(meta['title_en'])}</title>",
               f"<style>{CSS}</style><h1>{html.escape(meta['title_fa'])}</h1>"]
        if args.english:
            out.append(f"<div class='en'>{html.escape(meta['title_en'])}</div>")
        with open(pack_json.parent / "guide.csv", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                if not (row.get("chapter") or "").strip() or row["chapter"].startswith("#"):
                    continue
                if row.get("title_fa"):
                    out.append(f"<h2>{html.escape(row['chapter'])}. {html.escape(row['title_fa'])}</h2>")
                    if args.english:
                        out.append(f"<div class='en'>{html.escape(row.get('title_en', ''))}</div>")
                kind = row.get("kind") or "explain"
                fa, eng = KINDS.get(kind, (kind, kind))
                text = (row.get("text_fa") or "").strip()
                part = f"<div class='page {kind}'><b>{fa}</b>"
                if row.get("picture"):
                    part += figure(row["picture"].strip())
                part += html.escape(text)
                if args.english:
                    part += f"<div class='en'><i>{eng}.</i> {html.escape(en.get(text, '(no English yet)'))}</div>"
                out.append(part + "</div>")
        target = args.out / f"{meta['pack']}{'-en' if args.english else ''}.html"
        target.write_text("\n".join(out), "utf-8")
        print(target)


if __name__ == "__main__":
    main()

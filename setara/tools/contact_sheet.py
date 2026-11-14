#!/usr/bin/env python3
"""Render pictures to one labelled sheet, to look at them the size a child sees.

  python3 tools/contact_sheet.py out.png name1 name2 ...     (or: --file list.txt)
"""
import io
import sys
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
out, names = sys.argv[1], sys.argv[2:]
if names and names[0] == "--file":
    names = [l.split(":")[0].strip() for l in Path(names[1]).read_text().splitlines() if l.strip() and not l.startswith("#")]
font = ImageFont.truetype(str(ROOT / "app/assets/fonts/Andika-Regular.ttf"), 13)
cell_w, cell_h, cols = 170, 150, 6
rows = (len(names) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "#fffbf0")
draw = ImageDraw.Draw(sheet)
for i, name in enumerate(names):
    x, y = (i % cols) * cell_w, (i // cols) * cell_h
    svg = ROOT / "content/pictures" / f"{name}.svg"
    scene = name.startswith("scene_")
    w, h = (160, 120) if scene else (120, 120)
    try:
        png = cairosvg.svg2png(url=str(svg), output_width=w, output_height=h)
        img = Image.open(io.BytesIO(png)).convert("RGBA")
        sheet.paste(img, (x + (cell_w - w) // 2, y + 4), img)
    except Exception as exc:
        draw.text((x + 6, y + 50), "MISSING/BROKEN", fill="red", font=font)
        print(f"{name}: {exc}", file=sys.stderr)
    draw.text((x + 6, y + 128), name[:24], fill="#3b2f2f", font=font)
sheet.save(out)
print(out)

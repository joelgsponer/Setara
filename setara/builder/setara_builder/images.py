"""Pictures: SVG sources in content/pictures to small PNGs inside packs."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "img"

OBJECT_SIZE = (160, 160)  # single things: choices, tiles, cards
SCENE_SIZE = (400, 300)  # names starting with scene_: story pages


def size_for(name: str) -> tuple[int, int]:
    return SCENE_SIZE if name.startswith("scene_") else OBJECT_SIZE


def _quantize(png: bytes) -> bytes:
    """Flat-colour drawings compress far better with a small palette."""
    from PIL import Image

    img = Image.open(io.BytesIO(png)).convert("RGBA")
    out = io.BytesIO()
    img.quantize(colors=64, method=Image.Quantize.FASTOCTREE).save(out, "PNG", optimize=True)
    return out.getvalue()


def render(name: str, svg: Path) -> Path:
    import cairosvg

    data = svg.read_bytes()
    w, h = size_for(name)
    out = CACHE / f"{hashlib.sha1(data + f'{w}x{h}'.encode()).hexdigest()}.png"
    if not out.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        png = cairosvg.svg2png(bytestring=data, output_width=w, output_height=h)
        out.write_bytes(_quantize(png))
    return out


def placeholder(name: str) -> Path:
    """A plain card with the picture's name, so a pack builds before art exists."""
    from PIL import Image, ImageDraw, ImageFont

    w, h = size_for(name)
    out = CACHE / f"placeholder-{name}-{w}x{h}.png"
    if not out.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((4, 4, w - 5, h - 5), 16, fill=(236, 230, 214), outline=(120, 110, 95), width=4)
        font_path = ROOT.parent / "app" / "assets" / "fonts" / "Andika-Bold.ttf"
        label = name.replace("scene_", "").replace("_", " ")
        size = 30
        while size > 10:
            font = ImageFont.truetype(str(font_path), size)
            if d.textlength(label, font=font) < w - 20:
                break
            size -= 2
        d.text((w / 2, h / 2), label, font=font, fill=(70, 62, 52), anchor="mm")
        img.save(out, "PNG", optimize=True)
    return out

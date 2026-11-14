"""Drawing helpers for the Logic puzzles pack (used by make_puzzles.py).

Every picture this pack needs is a series: rows with a gap, grids, figures to
count, a balance, a river with two banks. Drawing them by rule keeps a series
alike, so that only the meaningful difference changes. Pictures of the shared
library (apple, cat, ...) are copied INTO the new file, never referenced.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PICS = ROOT / "content" / "pictures"
MARK = "<!-- drawn by content/math/2-puzzles/make_puzzles.py -->"

INK = "#3b2f2f"
COL = {"red": "#e0483f", "blue": "#3f7fbf", "yellow": "#f2b705", "green": "#4e9a51",
       "orange": "#e07a3f", "purple": "#8e5bb5"}
CREAM, SAND, WHITE, GREY, SKY, WATER = "#fff6dc", "#e8d2a6", "#ffffff", "#b9ae9b", "#bfe3f0", "#5da9d6"
GOLD = "#f2b705"
G5 = f'stroke="{INK}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"'

briefs: dict[str, str] = {}   # name -> what the picture shows (pictures.txt)
written: list[str] = []
skipped: list[str] = []


def save(name: str, viewbox: str, body: str, brief: str) -> str:
    """Write one picture. Only files this script made are ever replaced."""
    assert name.startswith(("puz_", "scene_puz_")), name
    assert name not in briefs, f"picture drawn twice: {name}"
    briefs[name] = brief
    path = PICS / f"{name}.svg"
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">\n{MARK}\n{body}\n</svg>\n'
    if path.exists():
        old = path.read_text("utf-8")
        if MARK not in old:
            skipped.append(name)
            return name
        if old == svg:
            return name
    path.write_text(svg, "utf-8")
    written.append(name)
    return name


def obj(name: str, body: str, brief: str) -> str:
    return save(name, "0 0 128 128", body, brief)


def scene(name: str, body: str, brief: str, bg: str = CREAM) -> str:
    return save(name, "0 0 400 300", f'<rect width="400" height="300" fill="{bg}"/>\n{body}', brief)


# -- the shared library, copied in ---------------------------------------------

_inner: dict[str, str] = {}


def lib_inner(name: str) -> str:
    if name not in _inner:
        text = (PICS / f"{name}.svg").read_text("utf-8")
        text = re.sub(r"<\?xml[^>]*\?>", "", text)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        m = re.search(r"<svg[^>]*>(.*)</svg>", text, flags=re.S)
        assert m and 'viewBox="0 0 128 128"' in text, f"{name}: not a 128 picture"
        _inner[name] = m.group(1).strip()
    return _inner[name]


def embed(name: str, x: float, y: float, size: float, flip: bool = False, recolor: dict | None = None) -> str:
    """A library picture drawn into the square (x, y, size)."""
    inner = lib_inner(name)
    for a, b in (recolor or {}).items():
        inner = inner.replace(a, b)
    s = size / 128
    if flip:
        return f'<g transform="translate({x + size:.1f} {y:.1f}) scale({-s:.4f} {s:.4f})">{inner}</g>'
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">{inner}</g>'


def shadow_of(name: str) -> str:
    """The same drawing, all in one dark colour."""
    inner = lib_inner(name)
    inner = re.sub(r'fill="(?!none)[^"]*"', f'fill="{INK}"', inner)
    inner = re.sub(r'stroke="(?!none)[^"]*"', f'stroke="{INK}"', inner)
    inner = re.sub(r'opacity="[^"]*"', "", inner)
    return f'<g fill="{INK}">{inner}</g>'


# -- numerals, as outlines of the app's own Latin font ---------------------------

_font = None


def _glyph(ch: str):
    global _font
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.ttLib import TTFont
    if _font is None:
        _font = TTFont(str(ROOT / "app" / "assets" / "fonts" / "Andika-Bold.ttf"))
    gs = _font.getGlyphSet()
    gname = _font.getBestCmap()[ord(ch)]
    pen = SVGPathPen(gs)
    gs[gname].draw(pen)
    return pen.getCommands(), gs[gname].width


def numeral(n: int | str, cx: float, cy: float, height: float, max_w: float | None = None, fill: str = INK) -> str:
    """A number centred on (cx, cy); height is the height of the digits."""
    upm = 2048 if _font is None else _font["head"].unitsPerEm
    glyphs = [_glyph(c) for c in str(n)]
    upm = _font["head"].unitsPerEm
    cap = _font["OS/2"].sCapHeight or upm * 0.7
    s = height / cap
    total = sum(w for _, w in glyphs)
    if max_w and total * s > max_w:
        s = max_w / total
    x = cx - total * s / 2
    y = cy + cap * s / 2
    out = []
    for d, w in glyphs:
        out.append(f'<path transform="translate({x:.1f} {y:.1f}) scale({s:.5f} {-s:.5f})" d="{d}" fill="{fill}"/>')
        x += w * s
    return "".join(out)


# -- plain shapes ---------------------------------------------------------------

def _star_points(cx: float, cy: float, R: float, r: float) -> str:
    import math
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rad = R if i % 2 == 0 else r
        pts.append(f"{cx + rad * math.cos(a):.1f},{cy + rad * math.sin(a):.1f}")
    return " ".join(pts)


def shape(kind: str, color: str, cx: float, cy: float, size: float, sw: float = 5) -> str:
    """circle, square, triangle or star inside a square of `size` centred on (cx, cy)."""
    fill = COL.get(color, color)
    h = size / 2
    st = f'fill="{fill}" stroke="{INK}" stroke-width="{sw:.1f}" stroke-linejoin="round"'
    if kind == "circle":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{h * 0.92:.1f}" {st}/>'
    if kind == "square":
        a = h * 0.84
        return f'<rect x="{cx - a:.1f}" y="{cy - a:.1f}" width="{2 * a:.1f}" height="{2 * a:.1f}" {st}/>'
    if kind == "triangle":
        return (f'<path d="M{cx:.1f} {cy - h * 0.9:.1f}L{cx + h * 0.98:.1f} {cy + h * 0.8:.1f}'
                f'H{cx - h * 0.98:.1f}z" {st}/>')
    if kind == "star":
        return f'<polygon points="{_star_points(cx, cy + h * 0.06, h * 1.02, h * 0.44)}" {st}/>'
    raise ValueError(kind)


def tower(n: int, cx: float, bottom: float, bw: float, bh: float, sw: float = 5, color: str = "orange") -> str:
    out = []
    for i in range(n):
        y = bottom - (i + 1) * bh
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
                   f'fill="{COL[color]}" stroke="{INK}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>')
    return "".join(out)


def dots(n: int, cx: float, cy: float, size: float, sw: float = 4, color: str = "blue") -> str:
    """n dots in two rows (pairs stand above each other), inside a square of `size`."""
    cols = (n + 1) // 2
    step = min(size * 0.3, size / max(cols, 2))
    r = step * 0.38
    x0 = cx - (cols - 1) * step / 2
    out = []
    for i in range(n):
        c, rw = i // 2, i % 2
        single = n == 1 or (n % 2 == 1 and i == n - 1)
        y = cy if (n == 1) else cy + (rw - 0.5) * step * 1.1
        if single and n > 1:
            y = cy - 0.5 * step * 1.1
        out.append(f'<circle cx="{x0 + c * step:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{COL[color]}" '
                   f'stroke="{INK}" stroke-width="{sw:.1f}"/>')
    return "".join(out)


def arrow(direction: str, cx: float, cy: float, size: float, sw: float = 5, color: str = "green") -> str:
    rot = {"up": 0, "right": 90, "down": 180, "left": 270}[direction]
    s = size / 128
    d = "M64 10L112 62H84V116H44V62H16z"
    return (f'<g transform="translate({cx - size / 2:.1f} {cy - size / 2:.1f}) scale({s:.4f}) rotate({rot} 64 64)">'
            f'<path d="{d}" fill="{COL[color]}" stroke="{INK}" stroke-width="{sw / s:.1f}" stroke-linejoin="round"/></g>')


def blocks(cells, cx: float, cy: float, size: float, color: str, sw: float = 5) -> str:
    """A figure of unit squares (list of (col, row)) centred in a square of `size`."""
    w = max(c for c, _ in cells) + 1
    h = max(r for _, r in cells) + 1
    u = size / max(w, h)
    x0, y0 = cx - w * u / 2, cy - h * u / 2
    return "".join(
        f'<rect x="{x0 + c * u:.1f}" y="{y0 + r * u:.1f}" width="{u:.1f}" height="{u:.1f}" fill="{COL[color]}" '
        f'stroke="{INK}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>' for c, r in cells)


def norm(cells):
    mx, my = min(c for c, _ in cells), min(r for _, r in cells)
    return sorted((c - mx, r - my) for c, r in cells)


def rot90(cells):      # a quarter turn to the right
    return norm([(-r, c) for c, r in cells])


def mirror(cells):     # as seen in a mirror standing beside it
    return norm([(-c, r) for c, r in cells])


def gap_box(x: float, y: float, w: float, h: float) -> str:
    """The empty place of a puzzle: a pale yellow box with a broken gold border."""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="#ffe9a8" '
            f'stroke="{GOLD}" stroke-width="5" stroke-dasharray="9 7" stroke-linecap="round"/>'
            f'<circle cx="{x + w / 2:.1f}" cy="{y + h / 2:.1f}" r="{min(w, h) * 0.09:.1f}" fill="{GOLD}"/>')


def card(x: float, y: float, w: float, h: float, fill: str = WHITE, sw: float = 3) -> str:
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="{fill}" '
            f'stroke="{INK}" stroke-width="{sw}"/>')

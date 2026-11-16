#!/usr/bin/env python3
"""Draws the picture series of the math packs into content/pictures/:
the fraction circles (frac_<k>_<n>), the third of a naan and of a circle, the
half, third and quarter of an orange and of a pomegranate (for sorting whole,
half and quarter), and the charts of Tables and Charts, whose numbers come
from CHARTS in generate.py so that picture and questions cannot drift apart.

    python3 content/math/draw_pictures.py            # draw what is missing
    python3 content/math/draw_pictures.py --force    # redraw this series

Never overwrites a picture without --force. Standard library only.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import CHARTS, PIES4, PIES5  # noqa: E402

PICTURES = Path(__file__).resolve().parents[1] / "pictures"
INK, BLUE, WHITE, CREAM, GREY = "#3b2f2f", "#3f7fbf", "#ffffff", "#fff6dc", "#b9ae9b"
HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">\n'
GROUP = f'<g stroke="{INK}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">\n'


def n2(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


def rim(i: int, n: int, r: float = 54, cx: float = 64, cy: float = 64) -> tuple[float, float]:
    """Point i of n on the circle, from the top, going left (as shape_quarter_circle does)."""
    a = 2 * math.pi * i / n
    return cx - r * math.sin(a), cy - r * math.cos(a)


def pie(k: int, n: int) -> str:
    """A circle in n equal parts, k of them blue."""
    out = HEAD + GROUP
    for i in range(n):
        (x1, y1), (x2, y2) = rim(i, n), rim(i + 1, n)
        out += (f'<path d="M64 64L{n2(x1)} {n2(y1)}A54 54 0 0 0 {n2(x2)} {n2(y2)}z" '
                f'fill="{BLUE if i < k else WHITE}" stroke-width="4"/>\n')
    out += '<circle cx="64" cy="64" r="54" fill="none"/>\n</g>\n</svg>\n'
    return out


def third_circle() -> str:
    x, y = rim(1, 3)
    return (HEAD + GROUP + '<circle cx="64" cy="64" r="54" fill="none" stroke-dasharray="1 11"/>\n'
            f'<path d="M64 64V10A54 54 0 0 0 {n2(x)} {n2(y)}z" fill="{BLUE}"/>\n</g>\n</svg>\n')


def third_bread() -> str:
    """One of three equal wedges of a round naan, drawn like bread_half and bread_quarter."""
    def arc(r, half, cy):
        a = math.radians(half)
        return (64 - r * math.sin(a), cy - r * math.cos(a)), (64 + r * math.sin(a), cy - r * math.cos(a))

    (lx, ly), (rx, ry) = arc(64, 60, 106)
    (ix, iy), (jx, jy) = arc(50, 52, 99)
    out = HEAD + GROUP
    out += f'<path d="M64 106L{n2(lx)} {n2(ly)}A64 64 0 0 1 {n2(rx)} {n2(ry)}z" fill="#e3a857"/>\n'
    out += f'<path d="M64 99L{n2(ix)} {n2(iy)}A50 50 0 0 1 {n2(jx)} {n2(jy)}z" fill="#f2cd85" stroke="none"/>\n'
    for r in (26, 38):
        (ax, ay), (bx, by) = arc(r, 44, 99)
        out += (f'<path d="M{n2(ax)} {n2(ay)}A{r} {r} 0 0 1 {n2(bx)} {n2(by)}" fill="none" stroke="#9a6b3f" '
                f'stroke-width="4" stroke-dasharray="1 9"/>\n')
    out += f'<path d="M{n2(lx)} {n2(ly)}L64 106L{n2(rx)} {n2(ry)}" fill="none"/>\n</g>\n</svg>\n'
    return out


def polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def wedge(cx: float, cy: float, r: float, a0: float, a1: float, **attrs) -> str:
    """The piece of a disc between the angles a0 and a1 (degrees, anticlockwise from the right)."""
    (x0, y0), (x1, y1) = polar(cx, cy, r, a0), polar(cx, cy, r, a1)
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="M{n2(cx)} {n2(cy)}L{n2(x0)} {n2(y0)}A{n2(r)} {n2(r)} 0 0 0 {n2(x1)} {n2(y1)}z"{extra}/>\n'


# Where the piece sits in the picture, as bread_half, bread_third and bread_quarter do: centre, radius, angles.
PIECES = {"half": (64, 92, 56, 0, 180), "third": (64, 106, 64, 30, 150), "quarter": (92, 92, 56, 90, 180)}


def fruit_piece(fruit: str, part: str) -> str:
    """A piece of a round fruit cut through the middle: the rind along the arc, the flesh inside."""
    cx, cy, r, a0, a1 = PIECES[part]
    out = HEAD + GROUP
    if fruit == "orange":
        out += wedge(cx, cy, r, a0, a1, fill="#f0923a")
        out += wedge(cx, cy, r - 9, a0, a1, fill="#fff1c9", stroke="none")
        out += wedge(cx, cy, r - 14, a0, a1, fill="#ffbe55", stroke="none")
        step = 30
        for deg in range(int(a0) + step, int(a1), step):   # the segments
            x, y = polar(cx, cy, r - 14, deg)
            out += f'<path d="M{n2(cx)} {n2(cy)}L{n2(x)} {n2(y)}" fill="none" stroke="#fff1c9" stroke-width="4"/>\n'
    else:
        out += wedge(cx, cy, r, a0, a1, fill="#e0483f")
        out += wedge(cx, cy, r - 10, a0, a1, fill="#fff6dc", stroke="none")
        for ring, count in ((0.34, 2), (0.62, 4)):   # the seeds
            n = max(1, round(count * (a1 - a0) / 180))
            for i in range(n):
                deg = a0 + (a1 - a0) * (i + 0.5) / n
                x, y = polar(cx, cy, r * ring, deg)
                out += f'<circle cx="{n2(x)}" cy="{n2(y)}" r="5" fill="#e0483f" stroke-width="2"/>\n'
    out += wedge(cx, cy, r, a0, a1, fill="none")
    return out + "</g>\n</svg>\n"


def small(name: str, x: float, y: float, size: float) -> str:
    """A library picture drawn small, as plain shapes inside this picture."""
    svg = (PICTURES / f"{name}.svg").read_text("utf-8")
    assert 'viewBox="0 0 128 128"' in svg and "<use" not in svg and "<image" not in svg, name
    body = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", svg, flags=re.S).strip()
    return f'<g transform="translate({n2(x)} {n2(y)}) scale({size / 128:.4f})">\n{body}\n</g>\n'


def bars(rows) -> str:
    """Three columns of blocks, one block per unit, the thing under its column."""
    assert len(rows) == 3
    out = HEAD + f'<rect x="1.5" y="1.5" width="125" height="125" rx="6" fill="{CREAM}" stroke="{INK}" stroke-width="3"/>\n'
    for i, (name, _, count) in enumerate(rows):
        x = 4 + i * 40
        if i:
            out += f'<path d="M{x} 5V123" stroke="{GREY}" stroke-width="2"/>\n'
        for j in range(count):
            out += (f'<rect x="{x + 8}" y="{n2(86 - (j + 1) * 16.4 + 1.5)}" width="24" height="13.4" rx="2" '
                    f'fill="{BLUE}" stroke="{INK}" stroke-width="2.5"/>\n')
        out += small(name, x + 2, 88, 36)
    out += f'<path d="M4 86H124" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>\n</svg>\n'
    return out


def table(rows) -> str:
    """Three rows read from the right: the thing, then one dot per unit."""
    assert len(rows) == 3
    out = HEAD + f'<rect x="1.5" y="1.5" width="125" height="125" rx="6" fill="{CREAM}" stroke="{INK}" stroke-width="3"/>\n'
    for i, (name, _, count) in enumerate(rows):
        y = 4 + i * 40
        if i:
            out += f'<path d="M5 {y}H123" stroke="{GREY}" stroke-width="2"/>\n'
        for j in range(count):
            out += (f'<circle cx="{n2(86 - (j + 0.5) * 16.4)}" cy="{y + 20}" r="6.6" fill="{BLUE}" stroke="{INK}" '
                    f'stroke-width="2.5"/>\n')
        out += small(name, 88, y + 2, 36)
    out += f'<path d="M86 4V124" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>\n</svg>\n'
    return out


def main() -> None:
    force = "--force" in sys.argv
    todo = {f"frac_{k}_{n}": pie(k, n) for k, n in sorted({kn for kn, _, _ in PIES4} | set(PIES5))}
    todo["shape_third_circle"] = third_circle()
    todo["bread_third"] = third_bread()
    for fruit in ("orange", "pomegranate"):
        for part in PIECES:
            todo[f"{fruit}_{part}"] = fruit_piece(fruit, part)
    for name, rows in CHARTS.items():
        todo[name] = bars(rows) if "bars" in name else table(rows)
    for name, svg in todo.items():
        path = PICTURES / f"{name}.svg"
        if path.exists() and not force:
            print(f"kept   {name} (exists)")
            continue
        path.write_text(svg, encoding="utf-8", newline="\n")
        print(f"drew   {name}")


if __name__ == "__main__":
    main()

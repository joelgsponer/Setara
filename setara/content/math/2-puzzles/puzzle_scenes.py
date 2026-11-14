"""The picture series of the Logic puzzles pack: tokens, rows, grids, figures,
the balance, the river, the children. Used by make_puzzles.py."""
from __future__ import annotations

import itertools
import math

import puzzle_draw as D
from puzzle_draw import COL, CREAM, GREY, INK, SAND, SKY, WATER, WHITE

SHAPES = ("circle", "square", "triangle", "star")
COLORS = ("red", "blue", "yellow", "green")
SHAPE_EN = {"circle": "circle", "square": "square", "triangle": "triangle", "star": "five-pointed star"}

# -- tokens: one small thing in a row, a grid, a pan ------------------------------
#   circle_red, small_circle_red, n:12, tower_3, dots_4, size_3, arrow_up,
#   kid:<id>, house_red, or the name of a library picture


def _parse_shape(tok: str):
    small = tok.startswith("small_")
    parts = (tok[6:] if small else tok).split("_")
    if len(parts) == 2 and parts[0] in SHAPES and parts[1] in COL:
        return parts[0], parts[1], small
    return None


def tok_draw(tok: str, x: float, y: float, size: float) -> str:
    """Draw a token into the square (x, y, size)."""
    cx, cy = x + size / 2, y + size / 2
    sw = max(2.5, min(5, size / 22))
    sh = _parse_shape(tok)
    if sh:
        kind, color, small = sh
        return D.shape(kind, color, cx, cy, size * (0.5 if small else 0.94), sw)
    if tok.startswith("n:"):
        return D.numeral(tok[2:], cx, cy, size * 0.5, max_w=size * 0.86)
    if tok.startswith("tower_"):
        n = int(tok[6:])
        return D.tower(n, cx, y + size * 0.97, size * 0.42, size * 0.155, sw)
    if tok.startswith("dots_"):
        return D.dots(int(tok[5:]), cx, cy, size * 0.96, max(2, sw - 1))
    if tok.startswith("size_"):
        k = int(tok[5:])
        return D.shape("circle", "blue", cx, cy, size * (0.16 + 0.17 * k), sw)
    if tok.startswith("arrow_"):
        return D.arrow(tok[6:], cx, cy, size * 0.92, sw)
    if tok.startswith("kid:"):
        return kid(tok[4:], x, y, size)
    if tok.startswith("house_"):
        return house(tok[6:], x, y, size)
    return D.embed(tok, x, y, size)


def tok_thing(tok: str) -> str:
    """The 'thing' a sheet writes for this token; draws its picture when new."""
    if tok.startswith("n:"):
        return "t:" + tok[2:]
    sh = _parse_shape(tok)
    name = None
    if sh:
        kind, color, small = sh
        name = f"puz_{'small_' if small else ''}{kind}_{color}"
        brief = (f"A {'SMALL ' if small else ''}{color} {SHAPE_EN[kind]}, flat colour, dark outline"
                 + (", about half the size of the other puz_ shapes, centred." if small else ", filling the square."))
    elif tok.startswith("tower_"):
        name, brief = f"puz_{tok}", f"A tower of {tok[6:]} orange blocks, one on top of the other, standing at the bottom."
    elif tok.startswith("dots_"):
        name, brief = f"puz_{tok}", f"{tok[5:]} blue dots in pairs (two rows), like a domino."
    elif tok.startswith("size_"):
        name, brief = f"puz_{tok}", f"A blue circle, size {tok[5:]} of 5 (1 is the smallest, 5 fills the square)."
    elif tok.startswith("arrow_"):
        name, brief = f"puz_{tok}", f"A fat green arrow pointing {tok[6:]}."
    elif tok.startswith("kid:"):
        name, brief = f"puz_kid_{tok[4:]}", KID_BRIEF[tok[4:]]
    elif tok.startswith("house_"):
        name, brief = f"puz_{tok}", f"A small flat-roofed house with {tok[6:]} walls, a brown door and one window."
    if name is None:
        assert (D.PICS / f"{tok}.svg").exists(), f"no library picture {tok}"
        return tok
    if name not in D.briefs:
        D.obj(name, tok_draw(tok, 6, 6, 116), brief)
    return name


# -- children: the library's girl and boy in other colours -----------------------

KIDS = {
    "girl_blue": ("girl", {}),
    "girl_red": ("girl", {"#3f7fbf": "#e0483f", "#8e5bb5": "#e07a3f"}),
    "girl_green": ("girl", {"#3f7fbf": "#4e9a51", "#8e5bb5": "#f2b705"}),
    "boy_green": ("boy", {}),
    "boy_blue": ("boy", {"#9ccb7a": "#3f7fbf"}),
    "boy_orange": ("boy", {"#9ccb7a": "#e07a3f"}),
}
KID_BRIEF = {
    "girl_blue": "The library girl (head and shoulders): blue headscarf, purple dress.",
    "girl_red": "The library girl with a red headscarf and an orange dress.",
    "girl_green": "The library girl with a green headscarf and a yellow dress.",
    "boy_green": "The library boy (head and shoulders): white cap, green shirt.",
    "boy_blue": "The library boy with a blue shirt.",
    "boy_orange": "The library boy with an orange shirt.",
}


def kid(kid_id: str, x: float, y: float, size: float) -> str:
    base, recolor = KIDS[kid_id]
    return D.embed(base, x, y, size, recolor=recolor)


def house(color: str, x: float, y: float, size: float) -> str:
    s = size / 128
    body = (f'<g {D.G5}><rect x="14" y="46" width="100" height="70" fill="{COL[color]}"/>'
            f'<path d="M6 46h116l-10-22H16z" fill="{SAND}"/>'
            f'<rect x="30" y="70" width="28" height="46" rx="3" fill="#6b4a2b"/>'
            f'<rect x="74" y="64" width="26" height="24" fill="{WHITE}"/><path d="M87 64v24M74 76h26" fill="none" stroke-width="3"/></g>')
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">{body}</g>'


# -- a row with an empty place ----------------------------------------------------

def pattern(name: str, toks: list, gap: int, rtl: bool, brief: str) -> str:
    n = len(toks)
    sp = 6
    cw = min(74, (384 - (n - 1) * sp) / n)
    x0 = (400 - (n * cw + (n - 1) * sp)) / 2
    y = 138 - cw / 2
    out = [f'<rect x="0" y="{y - 26:.1f}" width="400" height="{cw + 52:.1f}" fill="{SAND}"/>']
    for i, t in enumerate(toks):
        x = x0 + ((n - 1 - i) if rtl else i) * (cw + sp)
        if i == gap:
            out.append(D.gap_box(x, y, cw, cw))
        else:
            out.append(D.card(x, y, cw, cw))
            pad = cw * 0.08
            out.append(tok_draw(t, x + pad, y + pad, cw - 2 * pad))
    # which way the row runs
    ay = y + cw + 56
    a, b = (330, 70) if rtl else (70, 330)
    d = -1 if rtl else 1
    out.append(f'<path d="M{a} {ay}H{b}M{b - d * 16} {ay - 11}L{b} {ay}L{b - d * 16} {ay + 11}" fill="none" '
               f'stroke="{GREY}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    return D.scene(name, "\n".join(out), brief)


# -- a square grid with an empty place ---------------------------------------------

def grid(name: str, rows: list, gap: tuple, brief: str) -> str:
    n = len(rows)
    cell = 84 if n == 3 else 66
    sp = 6
    side = n * cell + (n - 1) * sp
    x0, y0 = (400 - side) / 2, (300 - side) / 2
    out = [f'<rect x="{x0 - 12:.1f}" y="{y0 - 12:.1f}" width="{side + 24:.1f}" height="{side + 24:.1f}" rx="12" fill="{SAND}"/>']
    for r in range(n):
        for c in range(n):
            x, y = x0 + c * (cell + sp), y0 + r * (cell + sp)
            if (r, c) == gap:
                out.append(D.gap_box(x, y, cell, cell))
                continue
            out.append(D.card(x, y, cell, cell))
            if rows[r][c]:
                pad = cell * 0.1
                out.append(tok_draw(rows[r][c], x + pad, y + pad, cell - 2 * pad))
    return D.scene(name, "\n".join(out), brief)


def latin_answers(rows: list, gap: tuple, symbols: list) -> set:
    """Every value the empty place can take when each symbol stands once in every row and column."""
    n = len(rows)
    found = set()

    def fill(g, k):
        if k == n * n:
            found.add(g[gap[0]][gap[1]])
            return
        r, c = divmod(k, n)
        if g[r][c]:
            return fill(g, k + 1)
        for s in symbols:
            if all(g[r][j] != s for j in range(n)) and all(g[i][c] != s for i in range(n)):
                g[r][c] = s
                fill(g, k + 1)
                g[r][c] = None
    g = [list(r) for r in rows]
    g[gap[0]][gap[1]] = None
    for r in range(n):          # the givens themselves must be a legal start
        for c in range(n):
            s = g[r][c]
            if s:
                assert [g[r][j] for j in range(n)].count(s) == 1 and [g[i][c] for i in range(n)].count(s) == 1
    fill(g, 0)
    return found


# -- figures to count ---------------------------------------------------------------

def _pt(x, y):
    return (round(x, 4), round(y, 4))


def _on(p, s):
    (x1, y1, x2, y2) = s
    cross = (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1)
    if abs(cross) > 1e-3 * max(1, math.hypot(x2 - x1, y2 - y1)):
        return False
    return min(x1, x2) - 1e-3 <= p[0] <= max(x1, x2) + 1e-3 and min(y1, y2) - 1e-3 <= p[1] <= max(y1, y2) + 1e-3


def _points(segs):
    pts = set()
    for s in segs:
        pts.add(_pt(s[0], s[1]))
        pts.add(_pt(s[2], s[3]))
    for a, b in itertools.combinations(segs, 2):
        x1, y1, x2, y2 = a
        x3, y3, x4, y4 = b
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-9:
            continue
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
        p = _pt(px, py)
        if _on(p, a) and _on(p, b):
            pts.add(p)
    return sorted(pts)


def _joined(p, q, segs):
    return any(_on(p, s) and _on(q, s) for s in segs)


def count_triangles(segs) -> int:
    pts = _points(segs)
    n = 0
    for a, b, c in itertools.combinations(pts, 3):
        area = abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]))
        if area > 1 and _joined(a, b, segs) and _joined(b, c, segs) and _joined(a, c, segs):
            n += 1
    return n


def count_rects(segs, squares_only: bool) -> int:
    pts = set(_points(segs))
    n = 0
    for a in pts:
        for c in pts:
            if c[0] > a[0] + 1 and c[1] > a[1] + 1:
                b, d = (c[0], a[1]), (a[0], c[1])
                if squares_only and abs((c[0] - a[0]) - (c[1] - a[1])) > 1e-3:
                    continue
                if b in pts and d in pts and all(_joined(p, q, segs) for p, q in ((a, b), (b, c), (c, d), (d, a))):
                    n += 1
    return n


def figure(name: str, segs: list, fill: list, brief: str) -> str:
    """A line figure. `fill` is the outline polygon, tinted so the figure reads as one thing."""
    out = []
    for poly in fill:
        out.append(f'<polygon points="{" ".join(f"{x},{y}" for x, y in poly)}" fill="#bfe3f0"/>')
    for x1, y1, x2, y2 in segs:
        out.append(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    return D.scene(name, "\n".join(out), brief)


# -- the balance ---------------------------------------------------------------------

def _balance(cx: float, base_y: float, left: list, right: list, tilt: int, half: float, item: float) -> str:
    """tilt: -1 the left pan is down, 0 level, 1 the right pan is down."""
    ang = math.radians(13) * tilt
    drop = item * 1.05 + 14
    py = base_y - drop - half * math.sin(math.radians(13)) - 16
    dx, dy = half * math.cos(ang), half * math.sin(ang)
    lx, ly, rx, ry = cx - dx, py - dy, cx + dx, py + dy
    pan_w = min(max(item * 1.25, item * max(len(left), len(right)) * 0.98 + 10), half * 1.75)
    out = [f'<path d="M{cx - 34} {base_y}H{cx + 34}L{cx + 10} {base_y - 16}H{cx - 10}z" fill="#9a6b3f" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>',
           f'<path d="M{cx} {base_y - 16}V{py}" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>',
           f'<path d="M{lx:.1f} {ly:.1f}L{rx:.1f} {ry:.1f}" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>',
           f'<circle cx="{cx}" cy="{py:.1f}" r="7" fill="{D.GOLD}" stroke="{INK}" stroke-width="4"/>']
    for ex, ey, items in ((lx, ly, left), (rx, ry, right)):
        pany = ey + drop
        out.append(f'<path d="M{ex:.1f} {ey:.1f}L{ex - pan_w / 2:.1f} {pany:.1f}M{ex:.1f} {ey:.1f}L{ex + pan_w / 2:.1f} {pany:.1f}" '
                   f'fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
        w = min(item, (pan_w - 6) / max(1, len(items)))
        x = ex - w * len(items) / 2
        for t in items:
            out.append(tok_draw(t, x, pany - w + 3, w))
            x += w
        out.append(f'<path d="M{ex - pan_w / 2 - 4:.1f} {pany:.1f}H{ex + pan_w / 2 + 4:.1f}C{ex + pan_w / 2:.1f} {pany + 16:.1f} '
                   f'{ex - pan_w / 2:.1f} {pany + 16:.1f} {ex - pan_w / 2 - 4:.1f} {pany:.1f}z" fill="{D.GOLD}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    return "".join(out)


def scales(name: str, sets: list, brief: str, aside: list | None = None) -> str:
    """One or two balances side by side. sets: [(left, right, tilt), ...]"""
    out = [f'<rect x="0" y="262" width="400" height="38" fill="{SAND}"/>']
    if len(sets) == 1:
        cx = 200 if not aside else 150
        out.append(_balance(cx, 266, sets[0][0], sets[0][1], sets[0][2], 96 if not aside else 84, 66 if not aside else 60))
        for i, t in enumerate(aside or []):
            out.append(tok_draw(t, 316, 196 - i * 70, 70))
    else:
        out.append(f'<path d="M200 20V250" stroke="{GREY}" stroke-width="4" stroke-dasharray="4 10" stroke-linecap="round"/>')
        for k, (l, r, tilt) in enumerate(sets):
            out.append(_balance(102 + 196 * k, 266, l, r, tilt, 56, 50))
    return D.scene(name, "\n".join(out), brief)


# -- the river: the near bank is on the right ----------------------------------------

def _boat(cx: float, y: float, w: float = 96) -> str:
    return (f'<path d="M{cx - w / 2} {y}H{cx + w / 2}L{cx + w / 2 - 16} {y + 26}H{cx - w / 2 + 16}z" fill="#9a6b3f" '
            f'stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')


def river(name: str, near: list, far: list, boat: str, brief: str, cargo: str | None = None) -> str:
    """near/far: who stands on each bank; boat: 'near' or 'far' (the farmer sits in it)."""
    out = [f'<rect x="0" y="0" width="400" height="300" fill="#9ccb7a"/>',
           f'<path d="M132 0C120 80 150 200 128 300H268C290 200 256 90 272 0z" fill="{WATER}" stroke="{INK}" stroke-width="4"/>',
           f'<path d="M160 40q10-8 20 0t20 0M190 120q10-8 20 0t20 0M170 270q10-8 20 0t20 0" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".7"/>']
    for bank, x0 in ((near, 276), (far, 6)):
        for i, t in enumerate(bank):
            out.append(D.embed(t, x0 + (i % 2) * 58, 14 + (i // 2) * 84, 62))
    bx = 226 if boat == "near" else 172
    out.append(D.embed("father", bx - 34, 150, 64))
    if cargo:
        out.append(D.embed(cargo, bx - 2, 172, 44))
    out.append(_boat(bx, 206))
    return D.scene(name, "\n".join(out), brief, bg="#9ccb7a")


# -- who has what ----------------------------------------------------------------------

def who_all(name: str, kids: list, items: list, brief: str) -> str:
    out = [f'<rect x="0" y="0" width="400" height="300" fill="{SKY}"/>',
           f'<rect x="0" y="150" width="400" height="150" fill="{SAND}"/>']
    for i, k in enumerate(kids):
        out.append(tok_draw(k, 30 + i * 120, 34, 104))
    out.append(D.card(86, 178, 228, 96, fill=CREAM, sw=4))
    for i, t in enumerate(items):
        out.append(tok_draw(t, 98 + i * 70, 190, 68))
    return D.scene(name, "\n".join(out), brief, bg=SKY)


def who_clue(name: str, k: str, item: str, has: bool, brief: str) -> str:
    out = [f'<rect x="0" y="0" width="400" height="300" fill="{SKY}"/>',
           f'<rect x="0" y="210" width="400" height="90" fill="{SAND}"/>',
           tok_draw(k, 214, 60, 170),
           D.card(34, 78, 150, 150, fill=CREAM, sw=4),
           tok_draw(item, 49, 93, 120)]
    out.append(D.embed("yes" if has else "no", 110, 22 if has else 150, 92))
    return D.scene(name, "\n".join(out), brief, bg=SKY)


def who_final(name: str, pairs: list, brief: str) -> str:
    out = [f'<rect x="0" y="0" width="400" height="300" fill="{SKY}"/>']
    for i, (k, item) in enumerate(pairs):
        x = 14 + i * 129
        out.append(D.card(x, 26, 114, 248, fill=CREAM, sw=4))
        out.append(tok_draw(k, x + 7, 34, 100))
        out.append(tok_draw(item, x + 12, 156, 90))
    return D.scene(name, "\n".join(out), brief, bg=SKY)


def portrait(name: str, toks: list, brief: str) -> str:
    out = [f'<rect x="0" y="0" width="400" height="300" fill="{SKY}"/>',
           f'<rect x="0" y="232" width="400" height="68" fill="#9ccb7a"/>']
    n = len(toks)
    size = 200 if n == 1 else 160 if n == 2 else 118
    x0 = (400 - n * size - (n - 1) * 10) / 2
    for i, t in enumerate(toks):
        out.append(tok_draw(t, x0 + i * (size + 10), 250 - size, size))
    return D.scene(name, "\n".join(out), brief, bg=SKY)


# -- ways: stepping stones from the house (right) to the goal (left) -------------------

def _along(points: list, n: int) -> list:
    lens = [math.dist(points[i], points[i + 1]) for i in range(len(points) - 1)]
    total = sum(lens)
    out = []
    for k in range(n):
        d = total * (k + 0.5) / n
        for i, ln in enumerate(lens):
            if d <= ln or i == len(lens) - 1:
                t = d / ln
                out.append((points[i][0] + (points[i + 1][0] - points[i][0]) * t,
                            points[i][1] + (points[i + 1][1] - points[i][1]) * t))
                break
            d -= ln
    return out


def ways(name: str, start: str, goal: str, paths: list, brief: str, extra: list | None = None) -> str:
    """paths: [(color, [points...], stones)]; extra: [(picture, x, y, size)]"""
    out = [f'<rect x="0" y="0" width="400" height="300" fill="#9ccb7a"/>']
    for color, pts, n in paths:
        for x, y in _along(pts, n):
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{COL[color]}" stroke="{INK}" stroke-width="4"/>')
    out.append(D.embed(start, 318, 108, 80))
    out.append(D.embed(goal, 2, 108, 80))
    for pic, x, y, size in extra or []:
        out.append(D.embed(pic, x, y, size))
    return D.scene(name, "\n".join(out), brief, bg="#9ccb7a")

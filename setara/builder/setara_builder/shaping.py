"""Dari text shaping, done once at build time.

LÖVE does not join Arabic-script letters or lay text out right to left. The
builder therefore turns every Dari string into ready-to-draw lines: letters
replaced by their joined presentation forms, order reversed into visual
(left-to-right) order, and lines broken for the 640 px screen. The device only
draws the glyphs it is given.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import arabic_reshaper
from bidi import get_display
from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).resolve().parents[2] / "app" / "assets" / "fonts"
DARI_FONT = FONT_DIR / "NotoNaskhArabic-Medium.ttf"
LATIN_FONT = FONT_DIR / "Andika-Regular.ttf"

# Body text on the device: 30 px Dari (spec minimum), inside a 600 px column.
# Lines are measured in the regular weight and drawn in several places, some
# bold and some a little narrower, so the column is kept well inside the
# screen. The app never re-wraps: a line that is still too wide is narrowed.
BODY_SIZE = 30
BODY_WIDTH = 550

_reshaper = arabic_reshaper.ArabicReshaper(
    {
        "language": "Farsi",
        "delete_harakat": False,
        "support_ligatures": True,
        # Only the mandatory lam-alef ligatures; optional ones need glyphs the
        # font may not have as single code points.
        "ARABIC LIGATURE ALLAH": False,
    }
)

_ARABIC = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
ZWNJ = "‌"


def has_arabic(text: str) -> bool:
    return bool(_ARABIC.search(text))


@lru_cache(maxsize=None)
def _metrics(path: Path):
    font = TTFont(str(path))
    return font.getBestCmap(), font["hmtx"].metrics, font["head"].unitsPerEm


def missing_glyphs(shaped: str) -> list[str]:
    """Characters of a shaped string that neither device font can draw."""
    dari, _, _ = _metrics(DARI_FONT)
    latin, _, _ = _metrics(LATIN_FONT)
    return sorted({c for c in shaped if not c.isspace() and ord(c) not in dari and ord(c) not in latin})


def width(shaped: str, size: int = BODY_SIZE) -> float:
    """Approximate drawn width in pixels of an already shaped line."""
    total = 0.0
    for ch in shaped:
        for path in (DARI_FONT, LATIN_FONT):
            cmap, hmtx, upm = _metrics(path)
            glyph = cmap.get(ord(ch))
            if glyph:
                total += hmtx[glyph][0] / upm * size
                break
        else:
            total += size * 0.5
    return total


def shape_line(text: str) -> str:
    """One logical-order line to one visual-order line. No wrapping."""
    text = " ".join(text.split())
    if not has_arabic(text):
        return text
    reshaped = _reshaper.reshape(text)
    visual = get_display(reshaped, base_dir="R")
    return visual.replace(ZWNJ, "")


def shape(text: str, size: int = BODY_SIZE, max_width: int = BODY_WIDTH) -> list[str]:
    """Logical-order text to a list of visual-order lines that fit max_width.

    Explicit line breaks in the source ("\\n" or " / ") are kept.
    """
    lines: list[str] = []
    for para in re.split(r"\n|\s/\s", text.strip()):
        words = para.split()
        if not words:
            continue
        current: list[str] = []
        for word in words:
            trial = shape_line(" ".join(current + [word]))
            if current and width(trial, size) > max_width:
                lines.append(shape_line(" ".join(current)))
                current = [word]
            else:
                current.append(word)
        lines.append(shape_line(" ".join(current)))
    return lines


# The four positional forms of a letter, for the Letter Shapes game.
# "ـ" (tatweel) on a side asks for a join on that side.
def letter_form(letter: str, form: str) -> str:
    """form is one of alone, start, middle, end. Returns the shaped glyph string."""
    tatweel = "ـ"
    logical = {
        "alone": letter,
        "start": letter + tatweel,
        "middle": tatweel + letter + tatweel,
        "end": tatweel + letter,
    }[form]
    return shape_line(logical)

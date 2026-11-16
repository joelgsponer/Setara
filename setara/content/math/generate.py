#!/usr/bin/env python3
"""Generates the math packs (levels 1 to 6): every CSV sheet, pack.json and
pictures.txt in this folder, and the English of every Dari text in them
(content/i18n/math.csv, for the English mode of the app).

    python3 content/math/generate.py            # write the files
    python3 content/math/generate.py --check    # write nothing: run the self-check and print its table

Standard library only. Deterministic: every round has its own fixed random
seed, so running it twice writes identical files. Do not edit the CSV files by
hand; change this script and run it again.

Every round is a POOL (pack.json: "draw": 8): 16 to 24 questions of which a
play asks eight, so that a round is not the same twice. The answers of a pool
are spread over the round's number range, and no answer is right more than
three times in a pool (see pick_even, build and self_check).

Every answer is computed, never typed, and checked again by assertions before
anything is written.
"""

from __future__ import annotations

import csv
import io
import math
import sys
from collections import Counter
from fractions import Fraction
import itertools
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
Z = "\u200c"  # zero-width non-joiner, as in می‌شود

# ---------------------------------------------------------------------------
# Numbers in Dari
# ---------------------------------------------------------------------------

ONES = ["صفر", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"]
TEENS = {10: "ده", 11: "یازده", 12: "دوازده", 13: "سیزده", 14: "چهارده", 15: "پانزده",
         16: "شانزده", 17: "هفده", 18: "هژده", 19: "نزده"}
TENS = {2: "بیست", 3: "سی", 4: "چهل", 5: "پنجاه", 6: "شصت", 7: "هفتاد", 8: "هشتاد", 9: "نود"}
# Afghan Dari hundreds (دوصد، سه‌صد، پنج‌صد), not Iranian (دویست، سیصد، پانصد).
HUNDREDS = {1: "یکصد", 2: "دوصد", 3: "سه" + Z + "صد", 4: "چهارصد", 5: "پنج" + Z + "صد",
            6: "شش" + Z + "صد", 7: "هفت" + Z + "صد", 8: "هشت" + Z + "صد", 9: "نه" + Z + "صد"}
DARI_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


def fa(n: int) -> str:
    """0..99,999,999 in Afghan Dari words."""
    assert isinstance(n, int) and 0 <= n < 100_000_000, n
    if n == 1000:
        return "هزار"
    if n > 1000:
        # یک هزار و دوصد، ده هزار، صد هزار، یک میلیون (levels 4 and 5)
        m, rest = divmod(n, 1_000_000)
        th, low = divmod(rest, 1000)
        groups = sum(1 for g in (m, th, low) if g)

        def part(k: int) -> str:
            return HUNDREDS[1] if k == 100 and groups > 1 else fa(k)

        parts = []
        if m:
            parts.append(part(m) + " میلیون")
        if th:
            parts.append(part(th) + " هزار")
        if low:
            parts.append(part(low))
        return " و ".join(parts)
    if n == 100:
        return "صد"
    parts = []
    h, r = divmod(n, 100)
    if h:
        parts.append(HUNDREDS[h])
    if r >= 20:
        t, o = divmod(r, 10)
        parts.append(TENS[t])
        if o:
            parts.append(ONES[o])
    elif r >= 10:
        parts.append(TEENS[r])
    elif r or not parts:
        parts.append(ONES[r])
    return " و ".join(parts)


def dari(n: int) -> str:
    return "".join(DARI_DIGITS[int(c)] for c in str(n))


def W(n: int) -> str:
    """A Western numeral tile."""
    return f"t:{n}"


def D(n: int) -> str:
    """A Dari numeral tile."""
    return f"f:{dari(n)}"


def num(n: int, script: str) -> str:
    return W(n) if script == "W" else D(n)


def value(thing: str) -> int:
    """The number a numeral tile shows (either digit system)."""
    assert thing[:2] in ("t:", "f:"), thing
    body = thing[2:]
    if thing.startswith("f:"):
        body = "".join(str(DARI_DIGITS.index(c)) for c in body)
    return int(body)


def _test_numbers() -> None:
    expect = {
        0: "صفر", 1: "یک", 2: "دو", 3: "سه", 4: "چهار", 5: "پنج", 6: "شش", 7: "هفت", 8: "هشت",
        9: "نه", 10: "ده", 11: "یازده", 12: "دوازده", 13: "سیزده", 14: "چهارده", 15: "پانزده",
        16: "شانزده", 17: "هفده", 18: "هژده", 19: "نزده", 20: "بیست", 21: "بیست و یک",
        25: "بیست و پنج", 30: "سی", 34: "سی و چهار", 40: "چهل", 50: "پنجاه", 60: "شصت",
        70: "هفتاد", 80: "هشتاد", 90: "نود", 99: "نود و نه", 100: "صد", 101: "یکصد و یک",
        110: "یکصد و ده", 115: "یکصد و پانزده", 120: "یکصد و بیست", 200: "دوصد",
        245: "دوصد و چهل و پنج", 300: "سه\u200cصد", 307: "سه\u200cصد و هفت", 400: "چهارصد",
        500: "پنج\u200cصد", 512: "پنج\u200cصد و دوازده", 600: "شش\u200cصد", 700: "هفت\u200cصد",
        800: "هشت\u200cصد", 900: "نه\u200cصد", 999: "نه\u200cصد و نود و نه", 1000: "هزار",
    }
    for n, words in expect.items():
        assert fa(n) == words, (n, fa(n), words)
    assert len({fa(n) for n in range(1001)}) == 1001, "two numbers share a name"
    for n in range(1001):
        assert "  " not in fa(n) and fa(n).strip() == fa(n)
    assert dari(0) == "۰" and dari(1000) == "۱۰۰۰" and dari(907) == "۹۰۷"
    for n in (0, 7, 20, 345, 1000):
        assert value(W(n)) == n and value(D(n)) == n
    big = {
        1001: "یک هزار و یک", 1100: "یک هزار و یکصد", 1500: "یک هزار و پنج\u200cصد", 2000: "دو هزار",
        2345: "دو هزار و سه\u200cصد و چهل و پنج", 10000: "ده هزار", 12500: "دوازده هزار و پنج\u200cصد",
        100000: "صد هزار", 100500: "یکصد هزار و پنج\u200cصد", 250000: "دوصد و پنجاه هزار",
        1000000: "یک میلیون", 1100000: "یک میلیون و یکصد هزار", 2000001: "دو میلیون و یک",
    }
    for n, words in big.items():
        assert fa(n) == words, (n, fa(n), words)
    assert len({fa(n) for n in range(1001, 20001)}) == 19000, "two numbers share a name"


# ---------------------------------------------------------------------------
# English (for the English mode of the app: content/i18n/math.csv)
# ---------------------------------------------------------------------------
#
# Every Dari text is built together with its English twin: tr(dari, english)
# records the pair and gives the Dari back, so the two cannot drift apart.
# Numbers are digits in the English. Sheet.add refuses a Dari text that has
# no English, and main() writes the table.

I18N = HERE.parent / "i18n" / "math.csv"
EN: dict[str, str] = {}     # Dari text -> English, every pair made
USED_EN: set[str] = set()   # the Dari texts that reached a sheet or a pack.json
HAS_DARI = re.compile("[؀-ۿ]")
DARI_LETTER = re.compile("[؀-ۯۺ-ۿ]")  # not the digits ۰ to ۹


def tr(dari_text: str, english: str) -> str:
    """Record the English of a Dari text. Returns the Dari text unchanged."""
    key, english = " ".join(dari_text.split()), " ".join(english.split())
    assert key and english and HAS_DARI.search(key) and not HAS_DARI.search(english), (dari_text, english)
    assert EN.setdefault(key, english) == english, f"two English texts for {key!r}: {EN[key]!r} and {english!r}"
    return dari_text


def used_en(row: dict) -> None:
    """Note the Dari texts of a row; each must have been made with tr()."""
    texts = [v for c, v in row.items() if c.endswith("_fa") and v]
    for col in ("show", "answer", "distractors", "thing", "basket", "tiles", "extra", "a", "b", "targets", "others"):
        texts += [t[2:] for t in row.get(col, "").split("|") if t.startswith("f:") and DARI_LETTER.search(t)]
    for text in texts:
        key = " ".join(text.split())
        assert key in EN, f"Dari text without English: {key!r}"
        USED_EN.add(key)


def english_table() -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["fa", "en"])
    for key in sorted(USED_EN):
        w.writerow([key, EN[key]])
    return buf.getvalue()


# Dari word -> English: one word when the plural only adds an s, or
# (uncounted, one of it, several of it).
WORD_EN = {
    "گوسفند": ("sheep", "sheep", "sheep"), "مرغ": "hen", "سیب": "apple", "تخم": "egg",
    "نان": ("bread", "loaf of bread", "loaves of bread"), "بز": "goat", "گل": "flower",
    "ماهی": ("fish", "fish", "fish"), "پیاله": "cup", "ستاره": "star",
    "کچالو": ("potato", "potato", "potatoes"), "پیاز": "onion", "انار": "pomegranate", "چهارمغز": "walnut",
    "زردک": "carrot", "پنسل": "pencil", "صابون": ("soap", "bar of soap", "bars of soap"), "کتابچه": "notebook",
    "چای": "tea", "شیر": "milk", "نمک": "salt", "بوره": "sugar", "برنج": "rice",
    "بوری آرد": ("sack of flour", "sack of flour", "sacks of flour"), "روغن": "oil",
    "بوت": ("shoes", "pair of shoes", "pairs of shoes"), "کمپل": "blanket",
    "بوری برنج": ("sack of rice", "sack of rice", "sacks of rice"),
    "دایره": "circle", "مربع": "square", "مثلث": "triangle", "مستطیل": "rectangle",
    "توپ": "ball", "بشقاب": "plate", "چرخ": "wheel", "سکه": "coin", "مالته": "orange", "آفتاب": "sun",
    "دکمه": "button", "کلکین": "window", "صندوق": ("box", "box", "boxes"), "دستمال": "handkerchief",
    "سمبوسه": "samosa", "خیمه": "tent", "کوه": "mountain", "دروازه": "door", "کتاب": "book", "قالین": "carpet",
    "تربوز": "watermelon", "جفت": "even", "طاق": "odd", "پوره": "whole", "نیم": "half", "چارک": "quarter",
    "ریسمان": "rope", "درخت": "tree", "چوب": "stick", "تکه": "piece", "دیوار": "wall", "جوی": "stream",
    "سرک": "road", "سیم": "wire", "گوشه": "corner", "ضلع": "side",
    "درازتر": "longer", "بلندتر": "taller", "کوتاه" + Z + "تر": "shorter",
    "متر": "metre", "سانتی" + Z + "متر": "centimetre",
}
PLURAL_WORDS = {"بوت"}  # "the shoes are", not "is"


def _word(word: str) -> tuple[str, str, str]:
    en = WORD_EN[word]
    return (en, en, en + "s") if isinstance(en, str) else en


def bare(word: str) -> str:
    return _word(word)[0]


def one(word: str) -> str:
    return _word(word)[1]


def many(word: str) -> str:
    return _word(word)[2]


def cnt(n: int, word: str) -> str:
    """'1 apple', '3 apples'."""
    return f"{n} {one(word) if n == 1 else many(word)}"


def nn(n: int, english: str) -> str:
    """'1 ten', '3 tens', '0 ones'."""
    return f"{n} {english}" if n == 1 else f"{n} {english}s"


def there(n: int, word: str) -> str:
    return f"There {'is' if n == 1 else 'are'} {cnt(n, word)}"


def was(n: int, word: str) -> str:
    return f"There {'was' if n == 1 else 'were'} {cnt(n, word)}"


def costs(word: str, afghani: int) -> str:
    return f"the {bare(word)} {'are' if word in PLURAL_WORDS else 'is'} {afghani} afghani"


def art(english: str) -> str:
    return "an" if english[0] in "aeiou" else "a"


def cap(text: str) -> str:
    return text[0].upper() + text[1:]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def rng_for(*key) -> random.Random:
    return random.Random("setara-math-" + "-".join(str(k) for k in key))


def digit_perms(n: int) -> list[int]:
    """Other numbers written with the same digits (34 -> 43, 345 -> 354, 435...)."""
    s = str(n)
    out = []
    for p in itertools.permutations(s):
        if p[0] == "0":
            continue
        m = int("".join(p))
        if m != n and m not in out:
            out.append(m)
    return out


def near(ans: int, rng: random.Random, lo: int, hi: int, prefer=(), k: int = 3) -> list[int]:
    """k plausible wrong numbers: the given typical mistakes first, then
    neighbours, digit swaps and ten more or less. Never the answer, never twice."""
    out: list[int] = []

    def add(x) -> None:
        if len(out) < k and isinstance(x, int) and lo <= x <= hi and x != ans and x not in out:
            out.append(x)

    for p in prefer:
        add(p)
    tiers = [[ans - 1, ans + 1], digit_perms(ans)[:2], [ans - 2, ans + 2, ans - 10, ans + 10],
             [ans - 3, ans + 3, ans - 20, ans + 20, ans - 100, ans + 100]]
    for tier in tiers:
        tier = list(tier)
        rng.shuffle(tier)
        for x in tier:
            add(x)
    d = 4
    while len(out) < k:
        add(ans + d)
        add(ans - d)
        d += 1
        assert d < 2000, (ans, lo, hi)
    return out


def spread(values: list, rng: random.Random) -> list:
    """Shuffle so that no two neighbours are equal."""
    values = list(values)
    for _ in range(1000):
        rng.shuffle(values)
        if all(a != b for a, b in zip(values, values[1:])):
            return values
    raise AssertionError(values)


def reachable(target: int, units: list[int]) -> bool:
    ok = [True] + [False] * target
    for t in range(1, target + 1):
        ok[t] = any(u <= t and ok[t - u] for u in units)
    return target > 0 and ok[target]


def greedy(target: int, units: list[int]) -> list[int]:
    parts, rest = [], target
    for u in sorted(units, reverse=True):
        while rest >= u:
            parts.append(u)
            rest -= u
    assert rest == 0 and sum(parts) == target, (target, units)
    return parts


# Things to count: picture name, Dari noun.
OBJS = [("sheep", "گوسفند"), ("hen", "مرغ"), ("apple", "سیب"), ("egg", "تخم"), ("bread", "نان"),
        ("goat", "بز"), ("flower", "گل"), ("fish", "ماهی"), ("cup", "پیاله"), ("star", "ستاره")]


class Sheet:
    def __init__(self, columns: list[str]):
        self.columns = columns
        self.rows: list[dict] = []
        self.few: dict[str, int] = {}    # round -> how many different answers exist at all (shapes, yes/no ...)
        self.small: dict[str, str] = {}  # round -> why its pool has fewer than 16 items
        self.intro: dict[str, str] = {}  # round -> its spoken instruction (market sheets)

    def add(self, **row) -> dict:
        assert set(row) <= set(self.columns), set(row) - set(self.columns)
        row = {c: str(row.get(c, "")) for c in self.columns}
        used_en(row)
        self.rows.append(row)
        return row

    def text(self) -> str:
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=self.columns, lineterminator="\n")
        w.writeheader()
        intro_seen = set()
        for row in self.rows:
            row = dict(row)
            if "intro_fa" in row:  # only on the first row of a round
                if row["round"] in intro_seen:
                    row["intro_fa"] = ""
                intro_seen.add(row["round"])
            w.writerow(row)
        return buf.getvalue()


LP_COLS = ["round", "intro_fa", "say_en", "say_fa", "show", "answer", "distractors", "help_fa", "hop"]


TRUTH: list[tuple[dict, object]] = []   # a row and the test that only its right choice passes


def lp(sheet: Sheet, rnd: str, intro: str, say: str, answer: str, wrong: list[str],
       show: str = "", help_fa: str = "", hop: str = "", truth=None) -> dict:
    """One listen-and-pick / journey question. Always three wrong choices, so
    the builder never fills in choices of its own. truth: a test on a choice
    that only the right one may pass (checked again by the self-check)."""
    assert len(wrong) == 3, (say, wrong)
    assert answer not in wrong and len(set(wrong)) == 3, (say, answer, wrong)
    assert help_fa, ("every question explains its answer", say)
    row = sheet.add(round=rnd, intro_fa=intro, say_fa=say, show=show, answer=answer,
                    distractors="|".join(wrong), help_fa=help_fa, hop=hop)
    if truth is not None:
        assert truth(answer) and not any(truth(w) for w in wrong), (say, answer, wrong)
        TRUTH.append((row, truth))
    return row


# ---------------------------------------------------------------------------
# 1. Count the Flock (listen_pick)
# ---------------------------------------------------------------------------

I_COUNT = tr("بشمار و عدد درست را انتخاب کن.", "Count and choose the right number.")
I_COUNT_D = tr("بشمار و عدد دری را انتخاب کن.", "Count and choose the Dari number.")
I_HEAR = tr("گوش کن و عدد را پیدا کن.", "Listen and find the number.")
I_MATCH = tr("همین عدد را به شکل دیگر پیدا کن.", "Find this same number in its other form.")
I_MORE = tr("ببین کدام از همه بیشتر است.", "See which one is the most.")
I_COMPARE = tr("خوب ببین و مقایسه کن.", "Look carefully and compare.")
I_PLACE = tr("ده" + Z + "ها و یک" + Z + "ها را یکجا کن.", "Put the tens and the ones together.")
I_PLACE3 = tr("صدها، ده" + Z + "ها و یک" + Z + "ها را یکجا کن.", "Put the hundreds, the tens and the ones together.")
I_DIGIT = tr("ببین در عدد چند ده و چند یک است.", "See how many tens and how many ones are in the number.")
I_NEXT = tr("عدد پیش و عدد بعد را پیدا کن.", "Find the number before and the number after.")
I_MIX = tr("حالا همه را با هم تمرین کن.", "Now practise them all together.")


def count_item(s, rnd, intro, n, obj, script, rng, hi=20, w=0):
    pic, noun = obj
    say = [tr(f"چند {noun} است؟", f"How many {many(noun)} are there?"),
           tr(f"بشمار: چند {noun} می{Z}بینی؟", f"Count: how many {many(noun)} do you see?"),
           tr(f"اینجا چند {noun} است؟", f"How many {many(noun)} are here?")][w % 3]
    assert 1 <= n <= 20
    if n <= 10:
        help_fa = tr("، ".join(fa(i) for i in range(1, n + 1)) + f". {fa(n)} {noun} است.", ", ".join(str(i) for i in range(1, n + 1)) + f". {there(n, noun)}.")
    else:
        help_fa = tr(f"{fa(n)} {noun} است.", f"{there(n, noun)}.")
    wrong = near(n, rng, 0, hi)
    row = lp(s, rnd, intro, say, num(n, script), [num(x, script) for x in wrong], show=f"p:{pic}*{n}", help_fa=help_fa)
    m = re.match(r"p:\w+\*(\d+)$", row["show"])
    assert int(m.group(1)) == value(row["answer"]) == n


def hear_item(s, rnd, intro, n, script, rng, lo, hi, prefer=(), w=0):
    wrong = near(n, rng, lo, hi, prefer)
    say = [tr(f"عدد {fa(n)} کدام است؟", f"Which one is the number {n}?"),
           tr(f"{fa(n)} را پیدا کن.", f"Find {n}."),
           tr(f"کدام یک {fa(n)} است؟", f"Which one is {n}?")][w % 3]
    if script == "D":
        help_fa = tr(f"{fa(n)} با عدد دری این طور نوشته می{Z}شود.", f"This is how {n} is written in Dari numbers.")
    else:
        help_fa = tr(f"{fa(n)} این طور نوشته می{Z}شود.", f"This is how {n} is written.")
    row = lp(s, rnd, intro, say, num(n, script), [num(x, script) for x in wrong], help_fa=help_fa)
    assert value(row["answer"]) == n


def match_item(s, rnd, intro, n, to_script, rng, lo, hi, prefer=()):
    """Show the number in one digit system, pick it in the other."""
    from_script = "D" if to_script == "W" else "W"
    wrong = near(n, rng, lo, hi, prefer)
    row = lp(s, rnd, intro, tr(f"{fa(n)}. همین عدد را پیدا کن.", f"{n}. Find this same number."), num(n, to_script),
             [num(x, to_script) for x in wrong], show=num(n, from_script),
             help_fa=tr(f"این عدد {fa(n)} است.", f"This number is {n}."))
    assert value(row["show"]) == value(row["answer"]) == n
    assert row["show"][0] != row["answer"][0]


def flock_compare_item(s, rnd, intro, obj, counts, most: bool):
    """Four groups of the same thing: which has the most (or the fewest)?"""
    pic, noun = obj
    assert len(set(counts)) == 4 and all(1 <= c <= 20 for c in counts)
    ans = max(counts) if most else min(counts)
    wrong = [c for c in counts if c != ans]
    word = "بیشتر" if most else "کمتر"
    row = lp(s, rnd, intro, tr(f"در کدام دسته {noun} از همه {word} است؟", f"In which group are there the {'most' if most else 'fewest'} {many(noun)}?"), f"p:{pic}*{ans}", [f"p:{pic}*{c}" for c in wrong],
             help_fa=tr(f"{fa(ans)} {noun} از همه {word} است.", f"{cnt(ans, noun)} is the {'most' if most else 'fewest'}."))
    got = int(row["answer"].split("*")[1])
    others = [int(x.split("*")[1]) for x in row["distractors"].split("|")]
    assert all(got > o for o in others) if most else all(got < o for o in others)


def numeral_compare_item(s, rnd, intro, numbers, biggest: bool, script="W"):
    assert len(set(numbers)) == 4
    ans = max(numbers) if biggest else min(numbers)
    wrong = [n for n in numbers if n != ans]
    word = "بزرگتر" if biggest else "کوچکتر"
    d, e = said_list(numbers, spoken_number)
    row = lp(s, rnd, intro, tr(f"{d}. کدام عدد از همه {word} است؟", f"{e}. Which number is the {'biggest' if biggest else 'smallest'}?"), num(ans, script), [num(n, script) for n in wrong],
             help_fa=tr(f"{fa(ans)} از همه {word} است.", f"{ans} is the {'biggest' if biggest else 'smallest'}."))
    got = value(row["answer"])
    others = [value(x) for x in row["distractors"].split("|")]
    assert all(got > o for o in others) if biggest else all(got < o for o in others)


def next_item(s, rnd, intro, n, after: bool, rng, lo, hi):
    if after:
        ans, say = n + 1, tr(f"بعد از {fa(n)} کدام عدد می{Z}آید؟", f"Which number comes after {n}?")
        prefer = [n, n - 1, n + 2, n + 11]
        help_fa = tr(f"بعد از {fa(n)}، {fa(ans)} می{Z}آید.", f"After {n} comes {ans}.")
    else:
        ans, say = n - 1, tr(f"پیش از {fa(n)} کدام عدد است؟", f"Which number is before {n}?")
        prefer = [n, n + 1, n - 2, n - 11]
        help_fa = tr(f"پیش از {fa(n)}، {fa(ans)} است.", f"Before {n} is {ans}.")
    wrong = near(ans, rng, lo, hi, prefer)
    row = lp(s, rnd, intro, say, W(ans), [W(x) for x in wrong], help_fa=help_fa)
    assert value(row["answer"]) == (n + 1 if after else n - 1)


def place2_item(s, rnd, intro, t, o, rng):
    """'Three tens and four ones' -> 34."""
    assert 1 <= t <= 9 and 0 <= o <= 9
    ans = 10 * t + o
    if o:
        say = tr(f"{ONES[t]} ده و {ONES[o]} یک، چند می{Z}شود؟", f"{nn(t, 'ten')} and {nn(o, 'one')} make how many?")
        prefer = [10 * o + t, t + o]
    else:
        say = tr(f"{ONES[t]} ده، چند می{Z}شود؟", f"{nn(t, 'ten')} {'makes' if t == 1 else 'make'} how many?")
        prefer = [t, 10 + t]
    wrong = near(ans, rng, 0, 100, prefer)
    row = lp(s, rnd, intro, say, W(ans), [W(x) for x in wrong], help_fa=tr(f"{ONES[t]} ده یعنی {fa(10 * t)}. جواب {fa(ans)} است.", f"{nn(t, 'ten')} means {10 * t}. The answer is {ans}."))
    assert value(row["answer"]) == t * 10 + o


def digit_item(s, rnd, intro, n, ask_tens: bool, rng):
    """Show 34: how many tens? how many ones?"""
    t, o = divmod(n, 10)
    assert 1 <= t <= 9 and t != o
    ans = t if ask_tens else o
    what = "ده" if ask_tens else "یک"
    wrong = near(ans, rng, 0, 9, [o if ask_tens else t])
    row = lp(s, rnd, intro, tr(f"در عدد {fa(n)}، چند {what} است؟", f"In the number {n}, how many {'tens' if ask_tens else 'ones'} are there?"), W(ans), [W(x) for x in wrong], show=W(n),
             help_fa=tr(f"{fa(n)} یعنی {ONES[t]} ده و {ONES[o]} یک.", f"{n} means {nn(t, 'ten')} and {nn(o, 'one')}."))
    shown = value(row["show"])
    assert value(row["answer"]) == (shown // 10 if ask_tens else shown % 10)


def place3_item(s, rnd, intro, h, t, o, rng):
    """'Two hundreds, four tens and five ones' -> 245."""
    assert 1 <= h <= 9 and (t or o)
    ans = 100 * h + 10 * t + o
    bits = [f"{ONES[h]} صد"]
    en_bits = [nn(h, 'hundred')]
    if t:
        bits.append(f"{ONES[t]} ده")
        en_bits.append(nn(t, 'ten'))
    if o:
        bits.append(f"{ONES[o]} یک")
        en_bits.append(nn(o, 'one'))
    say = tr((bits[0] + " و " + bits[1] if len(bits) == 2 else f"{bits[0]}، {bits[1]} و {bits[2]}") + f"، چند می{Z}شود؟", (en_bits[0] + " and " + en_bits[1] if len(en_bits) == 2 else f"{en_bits[0]}, {en_bits[1]} and {en_bits[2]}") + " make how many?")
    prefer = digit_perms(ans)[:2]
    if not t:
        prefer = [100 * h + 10 * o, 10 * h + o] + prefer
    if not o:
        prefer = [100 * h + t, 10 * h + t] + prefer
    wrong = near(ans, rng, 0, 1000, prefer)
    row = lp(s, rnd, intro, say, W(ans), [W(x) for x in wrong], help_fa=tr(f"جواب {fa(ans)} است.", f"The answer is {ans}."))
    assert value(row["answer"]) == 100 * h + 10 * t + o


def similar_numbers(x: int, rng: random.Random, lo: int, hi: int) -> list[int]:
    """Four different numbers that look alike, x among them."""
    cands = [c for c in digit_perms(x) + [x - 1, x + 1, x - 10, x + 10, x - 100, x + 100, x + 9, x - 9]
             if lo <= c <= hi and c != x]
    cands = list(dict.fromkeys(cands))
    assert len(cands) >= 3, x
    return [x] + rng.sample(cands, 3)


# ---------------------------------------------------------------------------
# 2. Number Hop (journey)
# ---------------------------------------------------------------------------

OP_WORD = {"+": "جمع", "-": "منفی", "*": "ضرب"}
OP_EN = {"+": "plus", "-": "minus", "*": "times"}
I_ADD = tr("جمع کن و جواب را انتخاب کن.", "Add and choose the answer.")
I_SUB = tr("کم کن و جواب را انتخاب کن.", "Take away and choose the answer.")
I_BOTH = tr("خوب گوش کن: جمع است یا منفی؟", "Listen carefully: is it plus or minus?")
I_STORY = tr("قصه را گوش کن و حساب کن.", "Listen to the story and work it out.")
I_TENS = tr("ده" + Z + "ها را جمع و منفی کن.", "Add and subtract the tens.")
I_MUL = tr("ضرب کن و جواب را انتخاب کن.", "Multiply and choose the answer.")

# picture, noun, "... more came", "... went" (each with its English)
STORY_OBJS = [
    ("sheep", "گوسفند", ("{b} تای دیگر آمد", "{b} more came"), ("{b} تا رفت", "{b} went away")),
    ("apple", "سیب", ("{b} تای دیگر آوردند", "they brought {b} more"), ("{b} تا را خوردند", "they ate {b}")),
    ("hen", "مرغ", ("{b} تای دیگر آمد", "{b} more came"), ("{b} تا رفت", "{b} went away")),
    ("bread", "نان", ("{b} تای دیگر پختند", "they baked {b} more"), ("{b} تا را خوردند", "they ate {b}")),
    ("goat", "بز", ("{b} تای دیگر آمد", "{b} more came"), ("{b} تا رفت", "{b} went away")),
    ("egg", "تخم", ("{b} تای دیگر آوردند", "they brought {b} more"), ("{b} تا شکست", "{b} broke")),
]

HOP_META: list[tuple[dict, int, str, int]] = []


def calc(a: int, op: str, b: int) -> int:
    return a + b if op == "+" else a - b if op == "-" else a * b


def hop_item(s, rnd, intro, a, op, b, rng, hi, say=None, show="", extra_prefer=(), script="W", why=None, w=0):
    """why: (Dari, English) said before the sum in the help: the way to the answer."""
    ans = calc(a, op, b)
    assert ans >= 0 and a >= 0 and b >= 0
    if say is None:
        say = [tr(f"{fa(a)} {OP_WORD[op]} {fa(b)} چند می{Z}شود؟", f"{a} {OP_EN[op]} {b} makes how many?"),
               tr(f"{fa(a)} {OP_WORD[op]} {fa(b)} مساوی چند است؟", f"{a} {OP_EN[op]} {b} equals how many?")][w % 2]
    help_fa = tr(f"{fa(a)} {OP_WORD[op]} {fa(b)} مساوی {fa(ans)}.", f"{a} {OP_EN[op]} {b} equals {ans}.")
    if why:
        help_fa = tr(f"{why[0]} {help_fa}", f"{why[1]} {EN[help_fa]}")
    prefer = list(extra_prefer)
    if op == "+":
        if a % 10 + b % 10 >= 10 and ans > 20:
            prefer.append(ans - 10)  # forgot to carry
        if a % 10 == 0 and b % 10 == 0 and a >= 10 and b >= 10:
            prefer += [ans // 10, ans + 10, ans - 10]
        prefer.append(abs(a - b))  # took away instead
    elif op == "-":
        if a % 10 < b % 10 and a > 20:
            prefer.append(ans + 10)  # forgot the borrowed ten
            prefer.append((a // 10 - b // 10) * 10 + (b % 10 - a % 10))  # smaller from larger digit
        if a % 10 == 0 and b % 10 == 0 and b >= 10:
            prefer += [ans // 10, ans + 10, ans - 10]
        prefer.append(a + b)  # added instead
    else:
        prefer += [(a + 1) * b, a + b, a * (b - 1)]
    wrong = near(ans, rng, 0, hi, prefer)
    hop = f"{a}{op}{b}" if op in "+-" and max(a, b, ans) <= 20 else ""
    row = lp(s, rnd, intro, say, num(ans, script), [num(x, script) for x in wrong], show=show, help_fa=help_fa, hop=hop)
    HOP_META.append((row, a, op, b))
    return row


def story_item(s, rnd, intro, a, op, b, rng, hi, k, with_picture):
    assert a >= 1 and b >= 1
    pic, noun, came, went = STORY_OBJS[k % len(STORY_OBJS)]
    if op == "+":
        say = tr(f"{fa(a)} {noun} بود، {came[0].format(b=fa(b))}. چند تا شد؟", f"{was(a, noun)}, {came[1].format(b=b)}. How many are there now?")
    else:
        say = tr(f"{fa(a)} {noun} بود، {went[0].format(b=fa(b))}. چند تا ماند؟", f"{was(a, noun)}, {went[1].format(b=b)}. How many are left?")
    show = f"p:{pic}*{a}" if with_picture and a <= 20 else ""
    hop_item(s, rnd, intro, a, op, b, rng, hi, say=say, show=show, why=WHY[op])


def money_story(s, rnd, intro, a, op, b, rng, hi):
    if op == "+":
        say = tr(f"{fa(a)} افغانی داشتی، {fa(b)} افغانی دیگر گرفتی. چند افغانی شد؟", f"You had {a} afghani, you got {b} afghani more. How many afghani is it now?")
    else:
        say = tr(f"{fa(a)} افغانی داشتی، {fa(b)} افغانی خرج کردی. چند افغانی ماند؟", f"You had {a} afghani, you spent {b} afghani. How many afghani are left?")
    hop_item(s, rnd, intro, a, op, b, rng, hi, say=say, why=WHY[op])


# ---------------------------------------------------------------------------
# 3. Market Scales (market)
# ---------------------------------------------------------------------------

MARKET_COLS = ["round", "intro_fa", "say_en", "say_fa", "goods", "target", "units", "mode", "help_fa"]
GOODS = [("apple", "سیب"), ("bread", "نان"), ("egg", "تخم"), ("potato", "کچالو"), ("onion", "پیاز"),
         ("pomegranate", "انار"), ("walnut", "چهارمغز"), ("carrot", "زردک")]
SHOP = [("bread", "نان"), ("egg", "تخم"), ("pencil", "پنسل"), ("soap", "صابون"), ("notebook", "کتابچه"),
        ("tea", "چای"), ("milk", "شیر"), ("salt", "نمک"), ("sugar", "بوره"), ("rice", "برنج")]
BIG = [("flour_sack", "بوری آرد"), ("oil_can", "روغن"), ("shoes", "بوت"), ("blanket", "کمپل"),
       ("hen", "مرغ"), ("rice_sack", "بوری برنج")]
AFN = "افغانی"
MARKET_META: list[tuple[dict, int]] = []


def market_row(s, rnd, say, goods, target, units, mode, help_fa):
    units = sorted(units)
    # The screen holds six kinds of coin or note: drop the small ones that
    # this price does not need.
    while len(units) > 6:
        for u in units:
            rest = [x for x in units if x != u]
            if reachable(target, rest):
                units = rest
                break
        else:
            raise AssertionError((target, units))
    assert reachable(target, units), (target, units)
    row = s.add(round=rnd, intro_fa=s.intro[rnd], say_fa=say, goods=goods, target=target, units="|".join(map(str, units)),
                mode=mode, help_fa=help_fa)
    MARKET_META.append((row, target))


def pay_help(target, units) -> str:
    parts = greedy(target, units)
    if len(parts) == 1:
        return tr(f"{fa(target)} {AFN} بده.", f"Give {target} afghani.")
    return tr(" جمع ".join(fa(p) for p in parts) + f" مساوی {fa(target)}.", " plus ".join(str(p) for p in parts) + f" equals {target}.")


# ---------------------------------------------------------------------------
# 4. Carpet Weaver (builder)
# ---------------------------------------------------------------------------

BUILDER_COLS = ["round", "intro_fa", "say_en", "say_fa", "tiles", "extra", "rtl", "done_en", "done_fa", "help_fa"]
I_SEQ = tr("عددها را به ترتیب درست بگذار.", "Put the numbers in the right order.")
WEAVE_META: list[tuple[dict, list[int], list[int], str]] = []


def seq_item(s, rnd, start, step, count, extra=(), script="W", intro=I_SEQ, table=None):
    """A run of numbers: start, start+step, ... (step may be negative)."""
    seq = [start + i * step for i in range(count)]
    assert all(0 <= x <= 10_000_000 for x in seq) and step != 0
    a, b, k = fa(seq[0]), fa(seq[-1]), fa(abs(step))
    if step == 1:
        say, help_fa = tr(f"از {a} تا {b} به ترتیب بشمار.", f"Count in order from {seq[0]} to {seq[-1]}."), tr("هر بار یک زیاد کن.", "Add 1 each time.")
    elif step == -1:
        say, help_fa = tr(f"از {a} تا {b}، یکی یکی کم کن.", f"From {seq[0]} to {seq[-1]}, take away one at a time."), tr("هر بار یک کم کن.", "Take away 1 each time.")
    elif step > 1:
        say, help_fa = f"{k} تا {k} تا بشمار، از {a} تا {b}.", tr(f"هر بار {k} زیاد کن.", f"Add {abs(step)} each time.")
        en = f"Count in {abs(step)}s, from {seq[0]} to {seq[-1]}."
        if table:
            say = f"جدول ضرب {fa(table)}: " + say
            en = f"The {table} times table: " + en
        say = tr(say, en)
    else:
        say, help_fa = tr(f"از {a} تا {b}، {k} تا {k} تا کم کن.", f"From {seq[0]} to {seq[-1]}, take away {abs(step)} at a time."), tr(f"هر بار {k} کم کن.", f"Take away {abs(step)} each time.")
    _weave(s, rnd, intro, say, seq, list(extra), script, help_fa, "seq")


def order_item(s, rnd, numbers, up=True, intro=I_SEQ):
    seq = sorted(numbers, reverse=not up)
    assert len(set(seq)) == len(seq)
    d, e = said_list(seq, spoken_number)
    if up:
        say, help_fa = tr(f"{d}. این عددها را از کوچک به بزرگ بچین.", f"{e}. Arrange these numbers from small to big."), tr(f"اول کوچکترین عدد را پیدا کن: {fa(seq[0])}.", f"First find the smallest number: {seq[0]}.")
    else:
        say, help_fa = tr(f"{d}. این عددها را از بزرگ به کوچک بچین.", f"{e}. Arrange these numbers from big to small."), tr(f"اول بزرگترین عدد را پیدا کن: {fa(seq[0])}.", f"First find the biggest number: {seq[0]}.")
    _weave(s, rnd, intro, say, seq, [], "W", help_fa, "up" if up else "down")


def _weave(s, rnd, intro, say, seq, extra, script, help_fa, kind):
    assert 2 <= len(seq) and len(seq) + len(extra) <= 8, (seq, extra)
    assert not set(seq) & set(extra) and len(set(extra)) == len(extra)
    if kind == "seq":  # an extra tile must never continue the run at either end
        step = seq[1] - seq[0]
        assert seq[0] - step not in extra and seq[-1] + step not in extra, (seq, extra)
    row = s.add(round=rnd, intro_fa=intro, say_fa=say, tiles="|".join(num(x, script) for x in seq),
                extra="|".join(num(x, script) for x in extra), rtl="yes" if script == "D" else "",
                done_fa=tr("، ".join(fa(x) for x in seq) + ".", ", ".join(str(x) for x in seq) + "."), help_fa=help_fa)
    WEAVE_META.append((row, seq, extra, kind))


# ---------------------------------------------------------------------------
# 5. Share the Bread (sorter)
# ---------------------------------------------------------------------------

SORTER_COLS = ["round", "intro_fa", "thing", "say_en", "say_fa", "basket", "basket_say_fa"]
SHAPES = {"circle": ("shape_circle", "دایره"), "square": ("shape_square", "مربع"),
          "triangle": ("shape_triangle", "مثلث"), "rectangle": ("shape_rectangle", "مستطیل")}
SHAPED = {
    "circle": [("shape_circle", "دایره"), ("ball", "توپ"), ("plate", "بشقاب"), ("wheel", "چرخ"),
               ("coin", "سکه"), ("orange", "مالته"), ("sun", "آفتاب"), ("button", "دکمه")],
    "square": [("shape_square", "مربع"), ("window", "کلکین"), ("box", "صندوق"), ("handkerchief", "دستمال")],
    "triangle": [("shape_triangle", "مثلث"), ("samosa", "سمبوسه"), ("tent", "خیمه"), ("mountain", "کوه")],
    "rectangle": [("shape_rectangle", "مستطیل"), ("door", "دروازه"), ("book", "کتاب"), ("carpet", "قالین")],
}
EVEN, ODD = ("f:جفت", "جفت"), ("f:طاق", "طاق")
WHOLE, HALF, QUARTER = ("f:پوره", "پوره"), ("f:نیم", "نیم"), ("f:چارک", "چارک")
FRACTIONS = {
    "whole": [("bread", "نان پوره"), ("apple", "سیب پوره"), ("watermelon", "تربوز پوره"), ("shape_circle", "دایره پوره")],
    "half": [("bread_half", "نیم نان"), ("apple_half", "نیم سیب"), ("watermelon_half", "نیم تربوز"), ("shape_half_circle", "نیم دایره")],
    "quarter": [("bread_quarter", "چارک نان"), ("apple_quarter", "چارک سیب"), ("watermelon_quarter", "چارک تربوز"),
                ("shape_quarter_circle", "چارک دایره")],
}
FRACTION_NOUNS = ["نان", "سیب", "تربوز", "دایره"]  # same order as the lists above
FRAC_BASKET = {"whole": WHOLE, "half": HALF, "quarter": QUARTER}
FRACTION_EN = {"whole": "whole {x}", "half": "half {a} {x}", "quarter": "quarter of {a} {x}"}
I_SHAPES = tr("هر چیز را در سبد شکل خودش بینداز.", "Put each thing in the basket of its own shape.")
I_PARITY = tr("عددهای جفت و طاق را جدا کن.", "Separate the even and the odd numbers.")
I_FRACTION = tr("پوره، نیم یا چارک؟ هر کدام را در سبد خودش بینداز.", "Whole, half or quarter? Put each one in its own basket.")
I_500 = tr("عدد از پنج" + Z + "صد کمتر است یا بیشتر؟", "Is the number less than 500 or more?")
SORT_META: list[tuple[dict, str, object]] = []

# ---------------------------------------------------------------------------
# 6. Shape Mason (listen_pick)
# ---------------------------------------------------------------------------

I_SHAPE = tr("شکل درست را پیدا کن.", "Find the right shape.")
I_SHAPE_OBJ = tr("ببین هر چیز چه شکلی دارد.", "See what shape each thing has.")
I_LONG = tr("ببین کدام درازتر و کدام کوتاه" + Z + "تر است.", "See which one is longer and which one is shorter.")
I_CORNER = tr("گوشه" + Z + "ها و ضلع" + Z + "ها را بشمار.", "Count the corners and the sides.")
I_CLOCK = tr("گوش کن و ساعت درست را پیدا کن.", "Listen and find the right clock.")
I_CLOCK_READ = tr("ساعت را ببین و بگو ساعت چند است.", "Look at the clock and say what time it is.")
I_CLOCK_LATER = tr("ساعت را ببین و فکر کن.", "Look at the clock and think.")
I_LENGTH = tr("متر و سانتی" + Z + "متر را حساب کن.", "Work out the metres and the centimetres.")
CM = "سانتی" + Z + "متر"
M = "متر"

# noun, the two pictures, the word for the long one, the word for the short one
LENGTHS = [
    ("ریسمان", "rope_long", "rope_short", "درازتر", "کوتاه" + Z + "تر"),
    ("پنسل", "pencil_long", "pencil_short", "درازتر", "کوتاه" + Z + "تر"),
    ("درخت", "tree_tall", "tree_short", "بلندتر", "کوتاه" + Z + "تر"),
    ("چوب", "stick_long", "stick_short", "درازتر", "کوتاه" + Z + "تر"),
]
MASON_META: list[tuple[dict, int]] = []

# ---------------------------------------------------------------------------
# Levels 4 and 5: shared pieces
# ---------------------------------------------------------------------------
#
# Level 4: all tables to 10, division as sharing, halves, quarters and thirds;
# weight and volume, perimeter, calendar.
# Level 5: large numbers, multi-digit multiplication, comparing and adding
# fractions, decimals through money; area, reading tables and simple charts.
#
# Sums are written left to right in Western digits only (3 × 4 = 12, 1/5,
# 2.50): a Dari-digit sum inside right-to-left text would be drawn in the
# wrong order, and "/" between Dari digits reads as a decimal mark. Single
# numbers still appear in both digit systems.

OP_WORD["/"] = "تقسیم"
OP_EN["/"] = "divided by"
WORD_EN.update({
    "یک بر سه": "1/3", "دو بر سه": "2/3", "سه چارک": "three quarters", "گاو": "cow",
    "کیلو": "kilo", "لیتر": "litre", "گرام": "gram",
})
CHECK_META: list[tuple[dict, Fraction]] = []   # a row and the value its answer must have
SENT_META: list[dict] = []                     # builder rows that spell a sum
ORDER_META: list[tuple[dict, bool]] = []       # builder rows in rising (or falling) order
PAIR_META: list[tuple[dict, str]] = []
CATCH_META: list[tuple[dict, object]] = []
SORT2_META: list[tuple[dict, str]] = []
PAIRS_COLS = ["round", "intro_fa", "a", "b", "say_en", "say_fa"]
CATCH_COLS = ["round", "intro_fa", "say_en", "say_fa", "targets", "others", "need", "help_fa"]


def val(thing: str):
    """The value a choice shows: a numeral in either digit system, a written
    fraction (t:3/4), a decimal (t:2.50) or a fraction picture (frac_3_4).
    None for anything else."""
    m = re.fullmatch(r"frac_(\d+)_(\d+)", thing)
    if m:
        return Fraction(int(m.group(1)), int(m.group(2)))
    if thing[:2] not in ("t:", "f:"):
        return None
    body = "".join(str(DARI_DIGITS.index(c)) if c in DARI_DIGITS else c for c in thing[2:])
    if re.fullmatch(r"\d+", body):
        return Fraction(int(body))
    if re.fullmatch(r"\d+/\d+", body):
        k, n = body.split("/")
        return Fraction(int(k), int(n))
    if re.fullmatch(r"\d+\.\d+", body):
        return Fraction(body)
    return None


def fr(k: int, n: int) -> str:
    """A written fraction tile."""
    return f"t:{k}/{n}"


def pie(k: int, n: int) -> str:
    """The picture of a circle cut into n equal parts, k of them coloured."""
    assert 0 < k < n and n in (2, 3, 4, 5, 6, 8), (k, n)
    return f"frac_{k}_{n}"


def fa_frac(k: int, n: int) -> str:
    return f"{fa(k)} بر {fa(n)}"


def fa_dec(text: str) -> str:
    """'0.5' -> صفر اعشاریه پنج, '2.05' -> دو اعشاریه صفر پنج."""
    whole, part = text.split(".")
    words = fa(int(part)) if part[0] != "0" else "صفر " + fa(int(part))
    return f"{fa(int(whole))} اعشاریه {words}"


def money(pul: int) -> str:
    """An amount of money as a decimal tile: 250 pul -> t:2.50."""
    return f"t:{pul // 100}.{pul % 100:02d}"


def money_fa(pul: int) -> str:
    a, p = divmod(pul, 100)
    assert pul > 0
    if a and p:
        return f"{fa(a)} {AFN} و {fa(p)} پول"
    return f"{fa(a)} {AFN}" if a else f"{fa(p)} پول"


def money_en(pul: int) -> str:
    a, p = divmod(pul, 100)
    if a and p:
        return f"{a} afghani and {p} pul"
    return f"{a} afghani" if a else f"{p} pul"


def numq(s, rnd, intro, say, ans, prefer, help_fa, rng, hi, lo=0, script="W", show=""):
    """A question whose answer is a whole number."""
    wrong = near(ans, rng, lo, hi, prefer)
    row = lp(s, rnd, intro, say, num(ans, script), [num(x, script) for x in wrong], show=show, help_fa=help_fa)
    CHECK_META.append((row, Fraction(ans)))
    return row


def pick_wrong(ans, candidates, k=3):
    """The first k candidate things whose values differ from the answer's and
    from each other."""
    out, seen = [], {val(ans)}
    for c in candidates:
        v = val(c)
        assert v is not None, c
        if v > 0 and v not in seen and c not in out:
            out.append(c)
            seen.add(v)
        if len(out) == k:
            return out
    raise AssertionError((ans, candidates))


def div_item(s, rnd, intro, a, b, rng, hi, say=None, show="", extra_prefer=(), script="W", why=None, w=0):
    assert b > 0 and a % b == 0, (a, b)
    ans = a // b
    if say is None:
        say = [tr(f"{fa(a)} تقسیم {fa(b)} چند می{Z}شود؟", f"{a} divided by {b} makes how many?"),
               tr(f"{fa(a)} تقسیم {fa(b)} مساوی چند است؟", f"{a} divided by {b} equals how many?")][w % 2]
    help_fa = tr(f"{fa(a)} تقسیم {fa(b)} مساوی {fa(ans)}.", f"{a} divided by {b} equals {ans}.")
    if why:
        help_fa = tr(f"{why[0]} {help_fa}", f"{why[1]} {EN[help_fa]}")
    wrong = near(ans, rng, 0, hi, list(extra_prefer) + [ans + 1, ans - 1, b, a - b])
    row = lp(s, rnd, intro, say, num(ans, script), [num(x, script) for x in wrong], show=show, help_fa=help_fa)
    HOP_META.append((row, a, "/", b))


# ---------------------------------------------------------------------------
# Levels 4 and 5: Count the Flock (listen_pick)
# ---------------------------------------------------------------------------

I_SHARE = tr("بین همه برابر تقسیم کن.", "Share equally among everyone.")
I_GROUPS = tr("سبدها را ببین و حساب کن که همه چند تا می" + Z + "شود.", "Look at the baskets and work out how many there are altogether.")
I_HALF = tr("نیم هر عدد را پیدا کن.", "Find half of each number.")
I_PARTS = tr("عدد را به حصه" + Z + "های برابر تقسیم کن.", "Divide the number into equal parts.")
I_PIE = tr("شکل را ببین: چند حصه از چند حصه رنگ شده است؟", "Look at the picture: how many parts out of how many are coloured?")
I_THOUSANDS = tr("هزارها را گوش کن و عدد را پیدا کن.", "Listen to the thousands and find the number.")
I_BIG = tr("عددهای بزرگ را گوش کن و پیدا کن.", "Listen to the big numbers and find them.")
I_PLACE4 = tr("هزارها، صدها، ده" + Z + "ها و یک" + Z + "ها را یکجا کن.", "Put the thousands, the hundreds, the tens and the ones together.")
SHARE_OBJS = [("apple", "سیب"), ("bread", "نان"), ("egg", "تخم"), ("walnut", "چهارمغز"), ("pomegranate", "انار"),
              ("carrot", "زردک"), ("pencil", "پنسل"), ("flower", "گل")]
# The fraction words of level 4, each with the picture that shows it.
PIES4 = [((1, 2), "نیم", "half"), ((1, 3), "یک بر سه", "1/3"), ((2, 3), "دو بر سه", "2/3"),
         ((1, 4), "چارک", "quarter"), ((3, 4), "سه چارک", "three quarters")]


def share_item(s, rnd, intro, n, k, obj, rng):
    pic, noun = obj
    assert n % k == 0 and n <= 20
    c = n // k
    say = tr(f"{fa(n)} {noun} را بین {fa(k)} نفر برابر تقسیم کن. به هر نفر چند {noun} می{Z}رسد؟",
             f"Share {cnt(n, noun)} equally among {k} people. How many {many(noun)} does each person get?")
    numq(s, rnd, intro, say, c, [k, c + 1, c - 1], tr(f"{fa(n)} تقسیم {fa(k)} مساوی {fa(c)}.", f"{n} divided by {k} equals {c}."),
         rng, c + 3, lo=1, show=f"p:{pic}*{n}")
    assert c * k == n


def group_item(s, rnd, intro, k, m, obj, rng):
    pic, noun = obj
    say = tr(f"{fa(k)} سبد است. در هر سبد {fa(m)} {noun} است. همه چند {noun} می{Z}شود؟",
             f"There are {k} baskets. In each basket there are {cnt(m, noun)}. How many {many(noun)} is that altogether?")
    numq(s, rnd, intro, say, k * m, [k * m + 1, (k + 1) * m, k + m, k * m - m],
         tr(f"{fa(k)} ضرب {fa(m)} مساوی {fa(k * m)}.", f"{k} times {m} equals {k * m}."), rng, 120, show=f"p:{pic}*{m}")


def half_item(s, rnd, intro, n, rng, obj=None, script="W"):
    assert n % 2 == 0
    h = n // 2
    help_fa = tr(f"نیم یعنی یک حصه از دو حصه برابر. {fa(n)} تقسیم دو مساوی {fa(h)}.",
                 f"Half means one of 2 equal parts. {n} divided by 2 equals {h}.")
    if obj:
        pic, noun = obj
        say = tr(f"نیم {fa(n)} {noun} چند {noun} است؟", f"How many {many(noun)} is half of {cnt(n, noun)}?")
        numq(s, rnd, intro, say, h, [h + 1, h - 1, n - 2], help_fa, rng, 100, lo=1, script=script, show=f"p:{pic}*{n}")
    else:
        say = tr(f"نیم {fa(n)} چند می{Z}شود؟", f"Half of {n} makes how many?")
        numq(s, rnd, intro, say, h, [h + 10, h - 1, h + 1, n - 2], help_fa, rng, 200, lo=1, script=script)


def quarter_item(s, rnd, intro, n, rng):
    assert n % 4 == 0
    c = n // 4
    numq(s, rnd, intro, tr(f"چارک {fa(n)} چند می{Z}شود؟", f"A quarter of {n} makes how many?"), c, [n // 2, c + 1, c - 1],
         tr(f"چارک یعنی یک حصه از چهار حصه برابر. {fa(n)} تقسیم چهار مساوی {fa(c)}.",
            f"A quarter means one of 4 equal parts. {n} divided by 4 equals {c}."), rng, 100, lo=1)


def third_item(s, rnd, intro, n, rng):
    assert n % 3 == 0
    c = n // 3
    numq(s, rnd, intro, tr(f"{fa(n)} را سه حصه برابر کن. یک حصه چند می{Z}شود؟", f"Make {n} into 3 equal parts. How many is one part?"),
         c, [n // 2 if n % 2 == 0 else c + 2, c + 1, c - 1],
         tr(f"یک حصه از سه حصه برابر را یک بر سه می{Z}گوییم. {fa(n)} تقسیم سه مساوی {fa(c)}.",
            f"One of 3 equal parts is called 1/3. {n} divided by 3 equals {c}."), rng, 100, lo=1)


def parts_item(s, rnd, intro, k, n, rng):
    numq(s, rnd, intro, tr("این دایره چند حصه برابر شده است؟", "Into how many equal parts is this circle divided?"), n, [k, n + 1, n - 1],
         tr(f"دایره {fa(n)} حصه برابر شده است.", f"The circle is divided into {n} equal parts."), rng, 9, lo=1, show=pie(k, n))


def place4_item(s, rnd, intro, n, rng):
    """'Two thousands, three hundreds, four tens and five ones' -> 2345."""
    th, h, t, o = (int(c) for c in f"{n:04d}")
    assert th and (h or t or o)
    bits = [(th, "هزار", "thousand"), (h, "صد", "hundred"), (t, "ده", "ten"), (o, "یک", "one")]
    bits = [b for b in bits if b[0]]
    fa_bits = [f"{ONES[d]} {w}" for d, w, _ in bits]
    en_bits = [nn(d, e) for d, _, e in bits]
    say = tr("، ".join(fa_bits[:-1]) + " و " + fa_bits[-1] + f"، چند می{Z}شود؟", ", ".join(en_bits[:-1]) + " and " + en_bits[-1] + " make how many?")
    digits = [d for d, _, _ in bits]
    squeezed = int("".join(str(d) for d in digits))      # the zeros left out
    prefer = [squeezed if squeezed != n else None, int(str(n)[0] + str(n)[2] + str(n)[1] + str(n)[3]), n * 10 if len(digits) < 4 else None]
    row = numq(s, rnd, intro, say, n, [p for p in prefer if p] + digit_perms(n)[:2],
               tr(f"جواب {fa(n)} است.", f"The answer is {n}."), rng, 100000)
    assert val(row["answer"]) == 1000 * th + 100 * h + 10 * t + o


# ---------------------------------------------------------------------------
# Levels 4 and 5: Number Hop (journey)
# ---------------------------------------------------------------------------

I_DIV = tr("تقسیم کن و جواب را انتخاب کن.", "Divide and choose the answer.")
I_MUL_D = tr("ضرب کن و جواب را با عدد دری انتخاب کن.", "Multiply and choose the answer in Dari numbers.")
I_THOUSAND_SUM = tr("هزارها و صدها را جمع و منفی کن.", "Add and subtract the thousands and the hundreds.")
I_TEN_TIMES = tr("ضرب در ده و صد را تمرین کن.", "Practise multiplying by 10 and by 100.")
I_MUL_BIG = tr("عدد بزرگ را ضرب کن: اول یک" + Z + "ها، بعد ده" + Z + "ها.", "Multiply the big number: first the ones, then the tens.")

# ---------------------------------------------------------------------------
# Levels 4 and 5: Market Scales (market)
# ---------------------------------------------------------------------------

# picture, Dari noun, English after "kilos of"
KILO_GOODS = [("rice", "برنج", "rice"), ("sugar", "بوره", "sugar"), ("potato", "کچالو", "potatoes"), ("onion", "پیاز", "onions"),
              ("apple", "سیب", "apples"), ("carrot", "زردک", "carrots"), ("salt", "نمک", "salt"), ("walnut", "چهارمغز", "walnuts")]
COUNTABLE = [("bread", "نان"), ("egg", "تخم"), ("pencil", "پنسل"), ("soap", "صابون"), ("notebook", "کتابچه"), ("apple", "سیب"),
             ("pomegranate", "انار"), ("carrot", "زردک")]
PAY_IT = "پولش را بده."


def buy_row(s, rnd, k, price, obj, units):
    """Several of one thing: the wording of level 3."""
    pic, noun = obj
    market_row(s, rnd, tr(f"{fa(k)} {noun} می{Z}خری. هر {noun} {fa(price)} {AFN} است. چند {AFN} می{Z}شود؟ {PAY_IT}",
                          f"You buy {cnt(k, noun)}. Each {one(noun)} is {price} afghani. How many afghani does it make? Pay for it."),
               pic, k * price, units, "pay", tr(f"{fa(k)} ضرب {fa(price)} مساوی {fa(k * price)}.", f"{k} times {price} equals {k * price}."))


def kilo_row(s, rnd, k, price, goods, units):
    pic, noun, en = goods
    market_row(s, rnd, tr(f"{fa(k)} کیلو {noun} می{Z}خری. هر کیلو {fa(price)} {AFN} است. چند {AFN} می{Z}شود؟ {PAY_IT}",
                          f"You buy {k} kilos of {en}. Each kilo is {price} afghani. How many afghani does it make? Pay for it."),
               pic, k * price, units, "pay", tr(f"{fa(k)} ضرب {fa(price)} مساوی {fa(k * price)}.", f"{k} times {price} equals {k * price}."))


# ---------------------------------------------------------------------------
# Levels 4 and 5: Carpet Weaver (builder)
# ---------------------------------------------------------------------------

I_SUM = tr("حساب را به ترتیب درست بچین.", "Put the sum in the right order.")
I_ORDER_FRAC = tr("کسرها را به ترتیب بچین.", "Put the fractions in order.")
I_ORDER_DEC = tr("عددهای اعشاری را به ترتیب بچین.", "Put the decimal numbers in order.")
SIGN = {"*": "×", "/": "÷", "+": "+"}
SIGN_HELP = {
    "*": tr("اول عدد اول، بعد نشان ضرب، بعد عدد دوم، بعد نشان مساوی و در آخر جواب.",
            "First the first number, then the times sign, then the second number, then the equals sign and last the answer."),
    "/": tr("اول عدد اول، بعد نشان تقسیم، بعد عدد دوم، بعد نشان مساوی و در آخر جواب.",
            "First the first number, then the division sign, then the second number, then the equals sign and last the answer."),
    "+": tr("اول کسر اول، بعد نشان جمع، بعد کسر دوم، بعد نشان مساوی و در آخر جواب.",
            "First the first fraction, then the plus sign, then the second fraction, then the equals sign and last the answer."),
}


def sum_item(s, rnd, a, op, b, extra):
    """Build 'a × b = c' or 'a ÷ b = c' from tiles; the wrong answers are extra tiles."""
    c = a * b if op == "*" else a // b
    assert len({a, b, c}) == 3 and not {a, b, c} & set(extra) and len(set(extra)) == len(extra) == 2, (a, op, b, extra)
    say = tr(f"{fa(a)} {OP_WORD[op]} {fa(b)} چند می{Z}شود؟ حساب را به ترتیب بچین.", f"{a} {OP_EN[op]} {b} makes how many? Put the sum in order.")
    row = s.add(round=rnd, intro_fa=I_SUM, say_fa=say, tiles="|".join([W(a), "t:" + SIGN[op], W(b), "t:=", W(c)]),
                extra="|".join(W(x) for x in extra), rtl="",
                done_fa=tr(f"{fa(a)} {OP_WORD[op]} {fa(b)} مساوی {fa(c)}.", f"{a} {OP_EN[op]} {b} equals {c}."), help_fa=SIGN_HELP[op])
    SENT_META.append(row)


def frac_sum_item(s, rnd, a, b, n):
    c = a + b
    assert a != b and c < n
    tiles = [fr(a, n), "t:+", fr(b, n), "t:=", fr(c, n)]
    extra = pick_wrong(fr(c, n), [fr(c, 2 * n), fr(c + 1, n), fr(c - 1, n)], 2)
    assert not set(extra) & set(tiles)
    say = tr(f"{fa_frac(a, n)} جمع {fa_frac(b, n)} چند می{Z}شود؟ حساب را به ترتیب بچین.", f"{a}/{n} plus {b}/{n} makes how many? Put the sum in order.")
    row = s.add(round=rnd, intro_fa=I_SUM, say_fa=say, tiles="|".join(tiles), extra="|".join(extra), rtl="",
                done_fa=tr(f"{fa_frac(a, n)} جمع {fa_frac(b, n)} مساوی {fa_frac(c, n)}.", f"{a}/{n} plus {b}/{n} equals {c}/{n}."), help_fa=SIGN_HELP["+"])
    SENT_META.append(row)


def order_things(s, rnd, intro, things, up, spoken, say, help_fa):
    """Tiles that are not whole numbers (fractions, decimals), smallest first or biggest first."""
    things = sorted(things, key=val, reverse=not up)
    assert len({val(t) for t in things}) == len(things) <= 8
    d, e = said_list(things, lambda t: spoken[t])
    say = tr(f"{d}. {say}", f"{e}. {EN[say]}")
    row = s.add(round=rnd, intro_fa=intro, say_fa=say, tiles="|".join(things), extra="", rtl="",
                done_fa=tr("، ".join(spoken[t][0] for t in things) + ".", ", ".join(spoken[t][1] for t in things) + "."), help_fa=help_fa)
    ORDER_META.append((row, up))


# ---------------------------------------------------------------------------
# Levels 4 and 5: Share the Bread (sorter)
# ---------------------------------------------------------------------------

FRACTIONS["third"] = [("bread_third", "یک بر سه نان"), None, None, ("shape_third_circle", "یک بر سه دایره")]
FRAC_BASKET["third"] = ("f:یک بر سه", "یک بر سه")
FRACTION_EN["third"] = "1/3 of {a} {x}"
I_FRACTION4 = tr("پوره، نیم، یک بر سه یا چارک؟ هر کدام را در سبد خودش بینداز.", "Whole, half, 1/3 or quarter? Put each one in its own basket.")
I_PRODUCT = tr("هر ضرب را در سبد جواب خودش بینداز.", "Put each multiplication in the basket of its answer.")
I_QUOTIENT = tr("هر تقسیم را در سبد جواب خودش بینداز.", "Put each division in the basket of its answer.")
I_HALF_SORT = tr("کسر از نیم کمتر است، مساوی نیم است یا بیشتر؟", "Is the fraction less than half, equal to half or more?")
I_SAME_FRAC = tr("هر کسر را در سبد شکلی بینداز که با آن مساوی است.", "Put each fraction in the basket of the picture it is equal to.")
I_AFGHANI = tr("پول از یک افغانی کمتر است یا بیشتر؟", "Is the money less than 1 afghani or more?")
I_5000 = tr("عدد از پنج هزار کمتر است یا بیشتر؟", "Is the number less than 5000 or more?")


# ---------------------------------------------------------------------------
# Levels 4 and 5: Shape Mason (listen_pick)
# ---------------------------------------------------------------------------

I_WEIGHT = tr("کیلو و گرام را حساب کن.", "Work out the kilos and the grams.")
I_WEIGHT2 = tr("قصه را گوش کن و وزن را حساب کن.", "Listen to the story and work out the weight.")
I_LITRE = tr("قصه را گوش کن و لیترها را حساب کن.", "Listen to the story and work out the litres.")
I_PERIMETER = tr("محیط، یعنی دور شکل را حساب کن: همه ضلع" + Z + "ها را جمع کن.", "Work out the perimeter, the way around the shape: add all the sides.")
I_PERIMETER2 = tr("قصه را گوش کن و محیط یا ضلع را حساب کن.", "Listen to the story and work out the perimeter or the side.")
I_AREA_COUNT = tr("مربع" + Z + "ها را بشمار و مساحت را پیدا کن.", "Count the squares and find the area.")
I_AREA = tr("مساحت را حساب کن: طول ضرب عرض.", "Work out the area: length times width.")
I_AREA2 = tr("مساحت یا ضلع را حساب کن.", "Work out the area or the side.")
I_AREA_OR = tr("خوب گوش کن: محیط است یا مساحت؟", "Listen carefully: is it the perimeter or the area?")
SQM = "متر مربع"

# ---------------------------------------------------------------------------
# Levels 4 and 5: Twin Tiles (pairs)
# ---------------------------------------------------------------------------

I_PAIR_MUL = tr("هر ضرب را با جواب آن جوره کن.", "Pair each multiplication with its answer.")
I_PAIR_DIV = tr("هر تقسیم را با جواب آن جوره کن.", "Pair each division with its answer.")
I_PAIR_PIE = tr("نام را گوش کن و با شکل آن جوره کن.", "Listen to the name and pair it with its picture.")
I_PAIR_SAME = tr("کسرهای مساوی را جوره کن.", "Pair the fractions that are equal.")
I_PAIR_FRAC = tr("هر شکل را با کسر آن جوره کن.", "Pair each picture with its fraction.")
I_PAIR_DEC = tr("هر عدد اعشاری را با کسر مساوی آن جوره کن.", "Pair each decimal number with the fraction equal to it.")


# ---------------------------------------------------------------------------
# Level 4: Days and Months (listen_pick; the choices are read aloud)
# ---------------------------------------------------------------------------

DAYS = [("شنبه", "Saturday"), ("یکشنبه", "Sunday"), ("دوشنبه", "Monday"), ("سه" + Z + "شنبه", "Tuesday"),
        ("چهارشنبه", "Wednesday"), ("پنجشنبه", "Thursday"), ("جمعه", "Friday")]
# The months of the solar year as they are named in Afghanistan.
MONTHS = [("حمل", "Hamal"), ("ثور", "Sawr"), ("جوزا", "Jawza"), ("سرطان", "Saratan"), ("اسد", "Asad"), ("سنبله", "Sunbula"),
          ("میزان", "Mizan"), ("عقرب", "Aqrab"), ("قوس", "Qaws"), ("جدی", "Jadi"), ("دلو", "Dalw"), ("حوت", "Hut")]
SEASONS = [("بهار", "spring"), ("تابستان", "summer"), ("خزان", "autumn"), ("زمستان", "winter")]
I_DAYS = tr("روزهای هفته را به یاد بیاور.", "Remember the days of the week.")
I_MONTHS = tr("ماه" + Z + "ها و فصل" + Z + "های سال را به یاد بیاور.", "Remember the months and the seasons of the year.")
I_CALENDAR = tr("روز، هفته، ماه و سال را حساب کن.", "Work out the day, the week, the month and the year.")
CAL_META: list[tuple[dict, str]] = []

# ---------------------------------------------------------------------------
# Level 5: Tables and Charts (listen_pick)
# ---------------------------------------------------------------------------

# Each picture shows three things and how many there are of each (1 to 5; three,
# not four, so that the small pictures stay as large as counted pictures are):
# chart_bars_* as columns of blocks, chart_table_* as rows of dots. The
# pictures are drawn from this very list by content/math/draw_pictures.py.
CHARTS = {
    "chart_bars_1": [("apple", "سیب", 4), ("bread", "نان", 5), ("egg", "تخم", 2)],
    "chart_table_1": [("sheep", "گوسفند", 3), ("hen", "مرغ", 5), ("cow", "گاو", 1)],
    "chart_bars_2": [("pencil", "پنسل", 5), ("ball", "توپ", 1), ("book", "کتاب", 3)],
    "chart_table_2": [("pomegranate", "انار", 2), ("watermelon", "تربوز", 1), ("walnut", "چهارمغز", 4)],
}
CHART_EXTRA = {"chart_bars_1": "carrot", "chart_table_1": "goat", "chart_bars_2": "notebook", "chart_table_2": "orange"}
I_CHART = tr("گراف را ببین و جواب بده.", "Look at the chart and answer.")
I_TABLE = tr("جدول را ببین و جواب بده.", "Look at the table and answer.")

# ---------------------------------------------------------------------------
# Level 5: Fair Shares (listen_pick): fractions and decimals
# ---------------------------------------------------------------------------

I_FRAC_NAME = tr("شکل را ببین و کسر آن را پیدا کن.", "Look at the picture and find its fraction.")
I_FRAC_PIC = tr("کسر را گوش کن و شکل آن را پیدا کن.", "Listen to the fraction and find its picture.")
I_FRAC_CMP = tr("کسرها را مقایسه کن.", "Compare the fractions.")
I_FRAC_ADD = tr("کسرها را جمع کن. مخرج همان می" + Z + "ماند.", "Add the fractions. The denominator stays the same.")
I_MONEY_DEC = tr("افغانی و پول را با عدد اعشاری بنویس.", "Write afghani and pul as a decimal number.")
I_DEC = tr("عددهای اعشاری را مقایسه و جمع کن.", "Compare and add the decimal numbers.")
PIES5 = [(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (1, 5), (2, 5), (3, 5), (4, 5), (1, 6), (5, 6), (1, 8), (3, 8), (5, 8), (7, 8)]

# ---------------------------------------------------------------------------
# Pools
# ---------------------------------------------------------------------------
#
# Every round is written by a function gen(rng) that adds 16 to 24 rows.
# build() runs it with the round's fixed seed and looks at the pool: no
# question twice, no answer right more than CAP times. A pool that fails is
# thrown away and made again with the next fixed seed, so the files stay the
# same from run to run.

N = 18      # items in a pool unless the material says otherwise
CAP = 3     # how often one answer may be right in a pool
DRAW = 8    # questions asked per play


class Retry(Exception):
    """This pool breaks a rule; build() makes another one."""


def pick_even(cands, n: int, rng: random.Random, key=lambda c: c, cap: int = CAP) -> list:
    """n of the candidates, spread evenly over the whole range of key(c)
    (the answer), no key more than cap times."""
    groups: dict = {}
    for c in sorted(set(cands), key=repr):
        groups.setdefault(key(c), []).append(c)
    order = sorted(groups, key=lambda k: (type(k).__name__ == "str", k))   # numbers first, then names
    for k in order:
        rng.shuffle(groups[k])
    used: Counter = Counter()
    out = []
    while len(out) < n:
        avail = [k for k in order if groups[k] and used[k] < cap]
        if not avail:
            raise AssertionError(f"only {len(out)} of {n} items within the cap")
        need = n - len(out)
        if len(avail) <= need:
            chosen = avail
        else:  # one from each of `need` equal stretches of the range
            chosen = [avail[min(len(avail) - 1, int((i + rng.random()) * len(avail) / need))] for i in range(need)]
            chosen = uniq(chosen)   # two stretches may meet in one key; the loop fills up what is missing
        for k in chosen:
            out.append(groups[k].pop())
            used[k] += 1
    rng.shuffle(out)
    return out


def even(lo: int, hi: int, n: int, rng: random.Random, ok=None, cap: int = CAP) -> list[int]:
    """n numbers from lo..hi, spread evenly, none more than cap times."""
    cands = [(v, i) for v in range(lo, hi + 1) if ok is None or ok(v) for i in range(cap)]
    return [v for v, _ in pick_even(cands, n, rng, key=lambda c: c[0], cap=cap)]


def answer_of(row: dict):
    """What is right in a row, for counting how often an answer is right."""
    if "answer" in row:
        v = val(row["answer"])
        return row["answer"] if v is None else v
    if "target" in row:
        return int(row["target"])
    if "basket" in row:
        return row["basket"]
    if "tiles" in row:
        return row["tiles"]
    if "targets" in row:
        return row["targets"]
    return row["a"] if row["b"] == "snd" else row["b"]


def question_of(row: dict) -> tuple:
    return tuple(row.get(c, "") for c in ("say_fa", "show", "thing", "tiles", "goods", "answer", "targets", "a"))


def pool_faults(sheet: Sheet, rnd: str) -> list[str]:
    """What is wrong with the pool of one round (nothing, if it is good)."""
    rows = [r for r in sheet.rows if r["round"] == rnd]
    faults = []
    if len({question_of(r) for r in rows}) != len(rows):
        faults.append("the same question twice")
    counts = Counter(answer_of(r) for r in rows)
    if "basket" in sheet.columns:  # a sorter: every basket must be likely to come up in a draw of eight
        if min(counts.values()) * 2 * len(counts) < len(rows):
            faults.append(f"a basket with too few things: {dict(counts)}")
    else:
        k = sheet.few.get(rnd)
        cap = CAP if not k else max(CAP, math.ceil(len(rows) / k) + 1)
        if k and len(counts) > k:
            faults.append(f"{len(counts)} different answers, {k} declared")
        if max(counts.values()) > cap:
            faults.append(f"an answer is right {max(counts.values())} times: {counts.most_common(2)}")
    return faults


def build(sheet: Sheet, level: int, game: str, rnd: str, gen, few: int = 0, small: str = "") -> None:
    """Make the pool of one round. few: the round has only that many different
    answers at all (four shapes, twelve hours), so they are balanced instead
    of capped at three. small: why the pool has fewer than 16 items."""
    if few:
        sheet.few[rnd] = few
    if small:
        sheet.small[rnd] = small
    assert not any(r["round"] == rnd for r in sheet.rows), (game, rnd)
    for attempt in range(400):
        mark, used = len(sheet.rows), set(USED_EN)
        try:
            gen(rng_for(level, game, rnd, attempt))
            faults = pool_faults(sheet, rnd)
            if faults:
                raise Retry(faults)
            return
        except Retry as e:
            last = e
            del sheet.rows[mark:]
            USED_EN.clear()
            USED_EN.update(used)
    raise AssertionError((level, game, rnd, last))


def said_list(things, spoken) -> tuple[str, str]:
    """The things of a question read aloud in a mixed order (never the order
    of the answer), so that a child who cannot read them still hears them and
    no two questions of a pool sound the same. spoken(thing) -> (Dari, English)."""
    order = list(things)
    rng_for("said", *order).shuffle(order)
    if order == sorted(order, key=lambda x: (val(x) if isinstance(x, str) else x)) and len(order) > 1:
        order.append(order.pop(0))
    return "، ".join(spoken(x)[0] for x in order), ", ".join(spoken(x)[1] for x in order)


def spoken_number(n) -> tuple[str, str]:
    return fa(n), str(n)


def uniq(items, key=lambda x: x) -> list:
    seen, out = set(), []
    for it in items:
        if key(it) not in seen:
            seen.add(key(it))
            out.append(it)
    return out


def text_sum(text: str):
    """The value of a written sum: '2+3', '10+10+5', '3×4', '12÷3', '7-2', '1/5+2/5'."""
    body = text[2:] if text[:2] == "t:" else text
    body = body.replace("−", "-").replace(" ", "")
    for sign in ("+", "-"):
        if sign in body:
            parts = [text_sum(p) for p in body.split(sign)]
            total = parts[0]
            for p in parts[1:]:
                total = total + p if sign == "+" else total - p
            return total
    for sign in ("×", "÷"):
        if sign in body:
            x, y = (text_sum(p) for p in body.split(sign))
            return x * y if sign == "×" else x / y
    v = val("t:" + body)
    assert v is not None, text
    return v


# The way to the answer, said before the sum in the help of a word problem.
WHY = {
    "+": (tr("چیزها زیاد شد، پس جمع می" + Z + "کنیم.", "There are more now, so we add."), "There are more now, so we add."),
    "-": (tr("چیزها کم شد، پس منفی می" + Z + "کنیم.", "There are fewer now, so we take away."), "There are fewer now, so we take away."),
    "*": (tr("چند دسته برابر است، پس ضرب می" + Z + "کنیم.", "There are several equal groups, so we multiply."), "There are several equal groups, so we multiply."),
    "/": (tr("برابر تقسیم می" + Z + "کنیم.", "We share equally."), "We share equally."),
}
WHY_ALL = (tr("همه را یکجا می" + Z + "کنیم، پس جمع می" + Z + "کنیم.", "We put them all together, so we add."), "We put them all together, so we add.")
WHY_DIFF = (tr("فرق را پیدا می" + Z + "کنیم: عدد کوچک را از عدد بزرگ منفی می" + Z + "کنیم.", "We find the difference: we take the small number away from the big one."),
            "We find the difference: we take the small number away from the big one.")
WHY_GROUPS = (tr("می" + Z + "شماریم که چند دسته جور می" + Z + "شود، پس تقسیم می" + Z + "کنیم.", "We count how many groups it makes, so we divide."),
              "We count how many groups it makes, so we divide.")

# More things to count than OBJS: picture name, Dari noun.
WORD_EN.update({"بره": "lamb", "چوچه مرغ": "chick", "بادنجان رومی": ("tomato", "tomato", "tomatoes"), "بادام": "almond",
                "خر": "donkey", "شتر": "camel", "قدم": "step", "شاگرد": "pupil", "دختر": "girl", "بچه": "boy",
                "خربوزه": "melon", "نوت": "note"})
COUNT_OBJS = OBJS + [("lamb", "بره"), ("chick", "چوچه مرغ"), ("tomato", "بادنجان رومی"), ("pomegranate", "انار"),
                     ("walnut", "چهارمغز"), ("carrot", "زردک"), ("potato", "کچالو"), ("onion", "پیاز"), ("pencil", "پنسل"),
                     ("ball", "توپ"), ("book", "کتاب"), ("orange", "مالته")]
YES, NO = ("yes", tr("درست", "true")), ("no", tr("غلط", "false"))


# ---------------------------------------------------------------------------
# Question forms shared by all levels
# ---------------------------------------------------------------------------

I_MISSING = tr("در قطار عددها یک عدد کم است. آن را پیدا کن.", "One number is missing in the row of numbers. Find it.")
I_PATTERN = tr("ببین عددها چطور پیش می" + Z + "روند و عدد بعدی را پیدا کن.", "See how the numbers go on and find the next number.")
I_BETWEEN = tr("عدد پیش، عدد بعد و عدد بین دو عدد را پیدا کن.", "Find the number before, the number after and the number between two numbers.")
I_BIGGER = tr("عددی را پیدا کن که بزرگتر یا کوچکتر است.", "Find the number that is bigger or smaller.")
I_BOND = tr("عددی را پیدا کن که کم است تا حساب درست شود.", "Find the number that is missing to make the sum right.")
I_DOUBLE = tr("دو چند و نیم عددها را پیدا کن.", "Find the double and the half of the numbers.")
I_DOUBLE1 = tr("دو چند هر عدد را پیدا کن.", "Find the double of each number.")
I_COUNT_ON = tr("از عدد شروع کن و پیش یا پس بشمار.", "Start from the number and count on or back.")
I_VILLAGE = tr("قصه را گوش کن. جمع است یا منفی؟ حساب کن.", "Listen to the story. Is it plus or minus? Work it out.")
I_VILLAGE_MUL = tr("قصه را گوش کن و ضرب کن.", "Listen to the story and multiply.")
I_VILLAGE_DIV = tr("قصه را گوش کن و تقسیم کن.", "Listen to the story and divide.")
I_MORE_THAN = tr("قصه را گوش کن و فرق را پیدا کن.", "Listen to the story and find the difference.")
I_SAME_SUM = tr("حسابی را پیدا کن که جواب آن همان است.", "Find the sum that has the same answer.")
I_TRUE = tr("حساب درست است یا غلط؟ در سبد خودش بینداز.", "Is the sum true or false? Put it in its basket.")
I_TRUE_CMP = tr("گوش کن: درست است یا غلط؟", "Listen: is it true or false?")
BLANK = "_"
GAP = "جای خالی"


SHOW_UNITS = 8   # what a card shows at 24 px or more: eight digits or signs (a space counts as half)


def units(thing: str) -> float:
    """The width of a written thing, in digits."""
    body = thing[2:] if thing[:2] in ("t:", "f:") else ""
    return sum(0.5 if c == " " else 1 for c in body)


def spoken_row(seq, gap: int) -> tuple[str, str]:
    return ("، ".join(GAP if i == gap else fa(x) for i, x in enumerate(seq)),
            ", ".join("blank" if i == gap else str(x) for i, x in enumerate(seq)))


def row_item(s, rnd, intro, start, step, count, gap, rng, lo, hi, script="W"):
    """A run of numbers with one missing (3 4 _ 6), or the next one asked (2 4 6 _)."""
    seq = [start + i * step for i in range(count)]
    assert 1 <= gap < count and all(lo <= x <= hi for x in seq), seq

    def written(numbers, at):
        return "t:" + " ".join(BLANK if i == at else str(x) for i, x in enumerate(numbers))

    # The card holds about eight digits at a readable size: a longer row loses
    # its far end (never the number before the gap), and a row that is still
    # too long is only spoken.
    while units(written(seq, gap)) > SHOW_UNITS and len(seq) > 3:
        if gap == len(seq) - 1 or (gap >= 2 and len(seq) - 1 - gap < gap):
            seq, gap = seq[1:], gap - 1
        else:
            seq = seq[:-1]
    count = len(seq)
    ans, prev = seq[gap], seq[gap - 1]
    shown = written(seq, gap) if units(written(seq, gap)) <= SHOW_UNITS else ""
    last = gap == count - 1
    if last:
        say = tr("، ".join(fa(x) for x in seq[:-1]) + f". بعد کدام عدد می{Z}آید؟", ", ".join(str(x) for x in seq[:-1]) + ". Which number comes next?")
    else:
        d, e = spoken_row(seq, gap)
        say = tr(f"{d}. کدام عدد کم است؟", f"{e}. Which number is missing?")
    k = abs(step)
    if step == 1:
        help_fa = tr(f"عددها یکی یکی زیاد می{Z}شوند. بعد از {fa(prev)}، {fa(ans)} می{Z}آید.", f"The numbers go up one at a time. After {prev} comes {ans}.")
    elif step == -1:
        help_fa = tr(f"عددها یکی یکی کم می{Z}شوند. پیش از {fa(prev)}، {fa(ans)} است.", f"The numbers go down one at a time. Before {prev} is {ans}.")
    elif step > 0:
        help_fa = tr(f"هر بار {fa(k)} زیاد می{Z}شود. {fa(prev)} جمع {fa(k)} مساوی {fa(ans)}.", f"It goes up by {k} each time. {prev} plus {k} equals {ans}.")
    else:
        help_fa = tr(f"هر بار {fa(k)} کم می{Z}شود. {fa(prev)} منفی {fa(k)} مساوی {fa(ans)}.", f"It goes down by {k} each time. {prev} minus {k} equals {ans}.")
    half = [ans + k // 2, ans - k // 2] if k >= 4 else []   # a number between two of the row
    prefer = half + [ans + 1, ans - 1, prev + (1 if step > 0 else -1) * (k + 1 if k > 1 else 2), ans + step]
    wrong = near(ans, rng, lo, hi + 2 * k, [p for p in prefer if p not in seq])
    lp(s, rnd, intro, say, num(ans, script), [num(x, script) for x in wrong], show=shown, help_fa=help_fa,
       truth=lambda c, a=ans: val(c) == a)


def between_item(s, rnd, intro, n, rng, lo, hi, script="W"):
    a, b = n - 1, n + 1
    wrong = near(n, rng, lo, hi, [a, b, n + 2, n - 2])
    lp(s, rnd, intro, tr(f"کدام عدد بین {fa(a)} و {fa(b)} است؟", f"Which number is between {a} and {b}?"), num(n, script),
       [num(x, script) for x in wrong],
       help_fa=tr(f"{fa(a)}، {fa(n)}، {fa(b)}. {fa(n)} بین {fa(a)} و {fa(b)} است.", f"{a}, {n}, {b}. {n} is between {a} and {b}."),
       truth=lambda c, a=a, b=b: a < val(c) < b)


def bigger_item(s, rnd, intro, n, ans, others, bigger: bool, script="W"):
    """'Which number is bigger than n?': only one of the four is."""
    assert len(set(others)) == 3 and ans not in others and n not in [ans] + list(others)
    assert (ans > n and all(o < n for o in others)) if bigger else (ans < n and all(o > n for o in others))
    if bigger:
        say = tr(f"کدام عدد از {fa(n)} بزرگتر است؟", f"Which number is bigger than {n}?")
        help_fa = tr(f"{fa(ans)} از {fa(n)} بزرگتر است. عددهای دیگر کوچکتر هستند.", f"{ans} is bigger than {n}. The other numbers are smaller.")
    else:
        say = tr(f"کدام عدد از {fa(n)} کوچکتر است؟", f"Which number is smaller than {n}?")
        help_fa = tr(f"{fa(ans)} از {fa(n)} کوچکتر است. عددهای دیگر بزرگتر هستند.", f"{ans} is smaller than {n}. The other numbers are bigger.")
    lp(s, rnd, intro, say, num(ans, script), [num(x, script) for x in others], help_fa=help_fa,
       truth=(lambda c, n=n: val(c) > n) if bigger else (lambda c, n=n: val(c) < n))


def bigger_round(s, level, rnd, lo, hi, n=N, scripts="W"):
    """A pool of 'bigger than' and 'smaller than' questions over lo..hi."""
    span = hi - lo

    def gen(rng):
        for i, ans in enumerate(even(lo + 4, hi - 4, n, rng)):
            bigger = i % 2 == 0
            gap = rng.randint(1, max(1, min(span // 10, 9)))
            if bigger:
                ref = max(lo + 3, ans - gap)
                pool = [x for x in range(max(lo, ref - max(8, span // 6)), ref)]
            else:
                ref = min(hi - 3, ans + gap)
                pool = [x for x in range(ref + 1, min(hi, ref + max(8, span // 6)) + 1)]
            if ref == ans or len(pool) < 3:
                raise Retry("no room")
            bigger_item(s, rnd, I_BIGGER, ref, ans, rng.sample(pool, 3), bigger, script=scripts[i % len(scripts)])
    build(s, level, "riddles", rnd, gen)


def addend_item(s, rnd, intro, a, total, rng, hi, first=False, op="+"):
    """a + _ = total (or _ + a = total; a × _ = total): the missing number."""
    sign = SIGN[op]
    b = total - a if op == "+" else total // a
    assert b >= 0 and (op == "+" or a * b == total)
    shown = f"t:{BLANK}{sign}{a}={total}" if first else f"t:{a}{sign}{BLANK}={total}"
    if units(shown) > SHOW_UNITS:
        shown = ""   # too long for the card: the sum is only spoken
    word, en = OP_WORD[op], OP_EN[op]
    if first:
        say = tr(f"چند {word} {fa(a)}، {fa(total)} می{Z}شود؟", f"What {en} {a} makes {total}?")
        help_fa = tr(f"{fa(b)} {word} {fa(a)} مساوی {fa(total)}.", f"{b} {en} {a} equals {total}.")
        hop = f"{b}+{a}"
    else:
        say = tr(f"{fa(a)} {word} چند، {fa(total)} می{Z}شود؟", f"{a} {en} what makes {total}?")
        help_fa = tr(f"{fa(a)} {word} {fa(b)} مساوی {fa(total)}.", f"{a} {en} {b} equals {total}.")
        hop = f"{a}+{b}"
    prefer = [total + a if op == "+" else total - a, b + 1, b - 1, total, a]
    wrong = near(b, rng, 0, hi, prefer)
    lp(s, rnd, intro, say, W(b), [W(x) for x in wrong], show=shown, help_fa=help_fa,
       hop=hop if op == "+" and total <= 20 else "",
       truth=(lambda c, a=a, t=total: a + val(c) == t) if op == "+" else (lambda c, a=a, t=total: a * val(c) == t))


def double_item(s, rnd, intro, a, rng, hi, obj=None):
    ans = 2 * a
    say = tr(f"دو چند {fa(a)} چند می{Z}شود؟", f"Double {a} makes how many?")
    help_fa = tr(f"دو چند {fa(a)} یعنی {fa(a)} جمع {fa(a)}. {fa(a)} جمع {fa(a)} مساوی {fa(ans)}.", f"Double {a} means {a} plus {a}. {a} plus {a} equals {ans}.")
    wrong = near(ans, rng, 0, hi, [a + 2, a, ans + 2, ans - 2])
    lp(s, rnd, intro, say, W(ans), [W(x) for x in wrong], show=f"p:{obj[0]}*{a}" if obj else "", help_fa=help_fa,
       hop=f"{a}+{a}" if ans <= 20 else "", truth=lambda c, a=a: val(c) == 2 * a)


def halve_item(s, rnd, intro, n, rng, hi):
    assert n % 2 == 0
    h = n // 2
    say = tr(f"نیم {fa(n)} چند می{Z}شود؟", f"Half of {n} makes how many?")
    help_fa = tr(f"نیم {fa(n)}، {fa(h)} است، چون {fa(h)} جمع {fa(h)} مساوی {fa(n)}.", f"Half of {n} is {h}, because {h} plus {h} equals {n}.")
    wrong = near(h, rng, 0, hi, [n, h + 1, h - 1, n - 2, 2 * n])
    lp(s, rnd, intro, say, W(h), [W(x) for x in wrong], help_fa=help_fa, hop=f"{n}-{h}" if n <= 20 else "",
       truth=lambda c, n=n: 2 * val(c) == n)


def count_on_item(s, rnd, intro, a, k, on: bool, rng, hi, step=1):
    ans = a + k * step if on else a - k * step
    way = [a + i * step * (1 if on else -1) for i in range(1, k + 1)]
    unit = "" if step == 1 else f"{fa(step)} تا {fa(step)} تا، "
    unit_en = "" if step == 1 else f"in {step}s, "
    if step == 1:
        say = tr(f"از {fa(a)} شروع کن و {fa(k)} تا {'پیش' if on else 'پس'} بشمار. به کدام عدد می{Z}رسی؟",
                 f"Start from {a} and count {'on' if on else 'back'} {k}. Which number do you reach?")
    elif on:
        say = tr(f"از {fa(a)} شروع کن و {unit}{fa(k)} بار پیش بشمار. به کدام عدد می{Z}رسی؟", f"Start from {a} and count on {unit_en}{k} {'time' if k == 1 else 'times'}. Which number do you reach?")
    else:
        say = tr(f"از {fa(a)} شروع کن و {unit}{fa(k)} بار پس بشمار. به کدام عدد می{Z}رسی؟", f"Start from {a} and count back {unit_en}{k} {'time' if k == 1 else 'times'}. Which number do you reach?")
    help_fa = tr("، ".join(fa(x) for x in way) + f". به {fa(ans)} می{Z}رسی.", ", ".join(str(x) for x in way) + f". You reach {ans}.")
    wrong = near(ans, rng, 0, hi, [ans + step, ans - step, a, a - k * step if on else a + k * step])
    lp(s, rnd, intro, say, W(ans), [W(x) for x in wrong], help_fa=help_fa,
       hop=(f"{a}+{k}" if on else f"{a}-{k}") if step == 1 and max(a, ans) <= 20 else "", truth=lambda c, r=ans: val(c) == r)


def same_sum_item(s, rnd, intro, shown: str, right: str, wrong: list[str], spoken: tuple[str, str], help_pair: tuple[str, str]):
    """'Which sum is the same as 2+3?' The choices are written sums."""
    target = text_sum(shown)
    assert text_sum(right) == target and right != shown and all(text_sum(w) != target for w in wrong)
    lp(s, rnd, intro, tr(f"کدام حساب با {spoken[0]} مساوی است؟", f"Which sum is equal to {spoken[1]}?"), right, wrong, show=shown,
       help_fa=tr(help_pair[0], help_pair[1]), truth=lambda c, t=target, sh=shown: text_sum(c) == t and c != sh)


def say_sum(a, op, b) -> tuple[str, str]:
    return f"{fa(a)} {OP_WORD[op]} {fa(b)}", f"{a} {OP_EN[op]} {b}"


SIGN["-"] = "−"


def sum_text(a, op, b) -> str:
    return f"t:{a}{SIGN[op]}{b}"


def same_sum_round(s, level, game, rnd, cands, n=16, hi=None):
    """cands: (a, op, b). Pairs of different sums with the same answer."""
    by_value: dict = {}
    for a, op, b in cands:
        by_value.setdefault(calc4(a, op, b), []).append((a, op, b))
    values = sorted(v for v, g in by_value.items() if len({(t[1], *sorted((t[0], t[2]))) for t in g}) >= 2)
    assert len(values) * CAP >= n, (rnd, len(values))

    def gen(rng):
        for v in even(0, len(values) - 1, n, rng):
            v = values[v]
            (a, op, b) = rng.choice(by_value[v])
            twins = [t for t in by_value[v] if (t[1], *sorted((t[0], t[2]))) != (op, *sorted((a, b)))]   # not 3×7 for 7×3
            if not twins:
                raise Retry("only the same sum turned round")
            (c, op2, d) = rng.choice(twins)
            others = [t for u in values if u != v and abs(u - v) <= max(3, v // 4) for t in by_value[u]]
            if len({calc4(*t) for t in others}) < 3:
                others = [t for u in values if u != v for t in by_value[u]]
            wrong = uniq(rng.sample(others, len(others)), key=lambda t: calc4(*t))[:3]
            if len(wrong) < 3:
                raise Retry("too few sums")
            same_sum_item(s, rnd, I_SAME_SUM, sum_text(a, op, b), sum_text(c, op2, d), [sum_text(*t) for t in wrong], say_sum(a, op, b),
                          (f"{say_sum(a, op, b)[0]} مساوی {fa(v)}. {say_sum(c, op2, d)[0]} هم مساوی {fa(v)}.",
                           f"{say_sum(a, op, b)[1]} equals {v}. {say_sum(c, op2, d)[1]} also equals {v}."))
    build(s, level, game, rnd, gen)


def calc4(a, op, b):
    if op == "/":
        assert a % b == 0
        return a // b
    return calc(a, op, b)


# -- true or false (sorter with a yes and a no basket) ------------------------

TF_META: list[tuple[dict, bool]] = []
EST_META: list[tuple[dict, int, int]] = []


def tf_row(s, rnd, intro, thing, say, true: bool):
    basket = YES if true else NO
    row = s.add(round=rnd, intro_fa=intro, thing=thing, say_fa=say, basket=basket[0], basket_say_fa=basket[1])
    TF_META.append((row, true))


def tf_sum_round(s, level, rnd, cands, intro=None, n=N):
    """cands: (a, op, b). Half of the written sums are right, half are off by
    a little or done with the wrong operation."""
    def gen(rng):
        for i, (a, op, b) in enumerate(rng.sample(sorted(set(cands)), n)):
            right = calc4(a, op, b)
            true = i % 2 == 0
            shown = right
            if not true:
                other = {"+": abs(a - b), "-": a + b, "*": a + b, "/": a - b}[op]
                opts = [x for x in (right + 1, right - 1, other, right + 2, right + 10 if right >= 20 else None) if x is not None and x >= 0 and x != right]
                shown = rng.choice(opts)
            d, e = say_sum(a, op, b)
            tf_row(s, rnd, intro or I_TRUE, f"{sum_text(a, op, b)}={shown}", tr(f"{d} مساوی {fa(shown)}", f"{e} equals {shown}"), true)
    build(s, level, "truefalse", rnd, gen)


def tf_compare_round(s, level, rnd, lo, hi, n=N):
    """Spoken statements about two numbers: 'seven is bigger than four'."""
    def gen(rng):
        seen = set()
        for i, a in enumerate(even(lo, hi, n, rng)):
            b = a
            while b == a or (a, b) in seen:
                b = max(lo, min(hi, a + rng.choice([-1, 1]) * rng.randint(1, max(2, (hi - lo) // 8))))
            seen.add((a, b))
            true = i % 2 == 0
            bigger = (a > b) == true   # what the sentence claims
            word, en = ("بزرگتر", "bigger") if bigger else ("کوچکتر", "smaller")
            tf_row(s, rnd, I_TRUE_CMP, f"t:{a}  {b}", tr(f"{fa(a)} از {fa(b)} {word} است", f"{a} is {en} than {b}"), true)
            assert true == ((a > b) if bigger else (a < b))
    build(s, level, "truefalse", rnd, gen)

# -- word problems from village life ------------------------------------------
#
# Each story: a function of the two numbers that gives (Dari, English), the
# picture of the thing (shown as many times as the first number, when that is
# at most 20) and the way to the answer for the help.

def _st(text, pic=None, why=None):
    return (text, pic, why)


STORIES = {
    "+": [
        _st(lambda a, b: (f"{fa(a)} گوسفند در چراگاه بود. {fa(b)} گوسفند دیگر آمد. حالا چند گوسفند است؟",
                          f"{was(a, 'گوسفند')} in the pasture. {b} more sheep came. How many sheep are there now?"), "sheep"),
        _st(lambda a, b: (f"مرغ{Z}ها دیروز {fa(a)} تخم دادند و امروز {fa(b)} تخم. همه چند تخم شد؟",
                          f"The hens laid {cnt(a, 'تخم')} yesterday and {cnt(b, 'تخم')} today. How many eggs is that altogether?"), "egg", WHY_ALL),
        _st(lambda a, b: (f"مادر صبح {fa(a)} نان پخت و چاشت {fa(b)} نان دیگر. همه چند نان پخت؟",
                          f"Mother baked {cnt(a, 'نان')} in the morning and {b} more at noon. How many loaves did she bake altogether?"), "bread", WHY_ALL),
        _st(lambda a, b: (f"در کیسه {fa(a)} افغانی داری. پدر {fa(b)} افغانی دیگر می{Z}دهد. حالا چند افغانی داری؟",
                          f"You have {a} afghani in your purse. Father gives you {b} afghani more. How many afghani do you have now?")),
        _st(lambda a, b: (f"از خانه تا چاه {fa(a)} قدم است و از چاه تا مکتب {fa(b)} قدم. از خانه تا مکتب چند قدم است؟",
                          f"From the house to the well it is {cnt(a, 'قدم')} and from the well to the school {cnt(b, 'قدم')}. How many steps is it from the house to the school?"), None, WHY_ALL),
        _st(lambda a, b: (f"صبح {fa(a)} پیاله آب نوشیدی و بعد از چاشت {fa(b)} پیاله. همه چند پیاله آب نوشیدی؟",
                          f"You drank {cnt(a, 'پیاله')} of water in the morning and {cnt(b, 'پیاله')} after noon. How many cups of water did you drink altogether?"), "cup", WHY_ALL),
        _st(lambda a, b: (f"در صنف {fa(a)} دختر و {fa(b)} بچه است. همه چند شاگرد است؟",
                          f"In the class there are {cnt(a, 'دختر')} and {cnt(b, 'بچه')}. How many pupils are there altogether?"), None, WHY_ALL),
        _st(lambda a, b: (f"از یک درخت {fa(a)} سیب چیدی و از درخت دیگر {fa(b)} سیب. همه چند سیب چیدی؟",
                          f"You picked {cnt(a, 'سیب')} from one tree and {cnt(b, 'سیب')} from another tree. How many apples did you pick altogether?"), "apple", WHY_ALL),
        _st(lambda a, b: (f"در صنف {fa(a)} بچه و {fa(b)} دختر است. همه چند شاگرد است؟",
                          f"In the class there are {cnt(a, 'بچه')} and {cnt(b, 'دختر')}. How many pupils are there altogether?"), None, WHY_ALL),
    ],
    "-": [
        _st(lambda a, b: (f"{fa(a)} گوسفند در چراگاه بود. {fa(b)} گوسفند به خانه رفت. چند گوسفند در چراگاه ماند؟",
                          f"{was(a, 'گوسفند')} in the pasture. {b} sheep went home. How many sheep are left in the pasture?"), "sheep"),
        _st(lambda a, b: (f"در سبد {fa(a)} تخم بود. {fa(b)} تخم شکست. چند تخم سالم ماند؟",
                          f"{was(a, 'تخم')} in the basket. {cnt(b, 'تخم')} broke. How many whole eggs are left?"), "egg"),
        _st(lambda a, b: (f"روی دسترخوان {fa(a)} نان بود. خانواده {fa(b)} نان را خورد. چند نان ماند؟",
                          f"{was(a, 'نان')} on the tablecloth. The family ate {cnt(b, 'نان')}. How many loaves are left?"), "bread"),
        _st(lambda a, b: (f"{fa(a)} افغانی داشتی. با {fa(b)} افغانی پنسل خریدی. چند افغانی ماند؟",
                          f"You had {a} afghani. You bought pencils for {b} afghani. How many afghani are left?")),
        _st(lambda a, b: (f"تا مکتب {fa(a)} قدم راه است. {fa(b)} قدم را رفته{Z}ای. چند قدم دیگر مانده است؟",
                          f"It is {cnt(a, 'قدم')} to the school. You have walked {cnt(b, 'قدم')}. How many more steps are left?")),
        _st(lambda a, b: (f"در کوزه {fa(a)} پیاله آب بود. {fa(b)} پیاله را نوشیدند. چند پیاله آب ماند؟",
                          f"There {'was' if a == 1 else 'were'} {cnt(a, 'پیاله')} of water in the jug. They drank {cnt(b, 'پیاله')}. How many cups of water are left?"), "cup"),
        _st(lambda a, b: (f"در حویلی {fa(a)} مرغ بود. {fa(b)} مرغ به لانه رفت. چند مرغ در حویلی ماند؟",
                          f"{was(a, 'مرغ')} in the yard. {cnt(b, 'مرغ')} went to the coop. How many hens are left in the yard?"), "hen"),
        _st(lambda a, b: (f"در سبد {fa(a)} سیب بود. {fa(b)} سیب را به همسایه دادی. چند سیب ماند؟",
                          f"{was(a, 'سیب')} in the basket. You gave {cnt(b, 'سیب')} to the neighbour. How many apples are left?"), "apple"),
    ],
    "diff": [
        _st(lambda a, b: (f"خواهر {fa(a)} چهارمغز دارد و برادر {fa(b)} چهارمغز. خواهر چند چهارمغز بیشتر دارد؟",
                          f"The sister has {cnt(a, 'چهارمغز')} and the brother has {cnt(b, 'چهارمغز')}. How many more walnuts does the sister have?"), None, WHY_DIFF),
        _st(lambda a, b: (f"برادر {fa(a)} پنسل دارد و خواهر {fa(b)} پنسل. برادر چند پنسل بیشتر دارد؟",
                          f"The brother has {cnt(a, 'پنسل')} and the sister has {cnt(b, 'پنسل')}. How many more pencils does the brother have?"), None, WHY_DIFF),
        _st(lambda a, b: (f"در رمه {fa(a)} گوسفند و {fa(b)} بز است. گوسفندها چند تا بیشتر از بزها هستند؟",
                          f"In the flock there are {cnt(a, 'گوسفند')} and {cnt(b, 'بز')}. How many more sheep than goats are there?"), None, WHY_DIFF),
        _st(lambda a, b: (f"نان {fa(a)} افغانی است و تخم {fa(b)} افغانی. نان چند افغانی قیمت{Z}تر است؟",
                          f"The bread is {a} afghani and the egg is {b} afghani. How many afghani more does the bread cost?"), None, WHY_DIFF),
        _st(lambda a, b: (f"امروز {fa(a)} پیاله آب نوشیدی و دیروز {fa(b)} پیاله. امروز چند پیاله بیشتر نوشیدی؟",
                          f"Today you drank {cnt(a, 'پیاله')} of water and yesterday {cnt(b, 'پیاله')}. How many more cups did you drink today?"), None, WHY_DIFF),
    ],
    # k groups of m: (k, m). The third field: the m this story is tied to, or None.
    "*": [
        _st(lambda k, m: (f"هر مرغ دو پای دارد. {fa(k)} مرغ چند پای دارد؟", f"Each hen has 2 legs. How many legs do {cnt(k, 'مرغ')} have?"), 2),
        _st(lambda k, m: (f"هر دست پنج انگشت دارد. {fa(k)} دست چند انگشت دارد؟", f"Each hand has 5 fingers. How many fingers do {nn(k, 'hand')} have?"), 5),
        _st(lambda k, m: (f"هر نوت ده افغانی است. {fa(k)} نوت چند افغانی می{Z}شود؟", f"Each note is 10 afghani. How many afghani do {cnt(k, 'نوت')} make?"), 10),
        _st(lambda k, m: (f"هر بز چهار پای دارد. {fa(k)} بز چند پای دارد؟", f"Each goat has 4 legs. How many legs do {cnt(k, 'بز')} have?"), 4),
        _st(lambda k, m: (f"در هر سبد {fa(m)} تخم است. {fa(k)} سبد چند تخم دارد؟", f"In each basket there are {cnt(m, 'تخم')}. How many eggs do {nn(k, 'basket')} have?")),
        _st(lambda k, m: (f"هر روز {fa(m)} پیاله آب می{Z}نوشی. در {fa(k)} روز چند پیاله آب می{Z}نوشی؟",
                          f"Each day you drink {cnt(m, 'پیاله')} of water. How many cups of water do you drink in {nn(k, 'day')}?")),
        _st(lambda k, m: (f"هر نان {fa(m)} افغانی است. {fa(k)} نان چند افغانی می{Z}شود؟", f"Each loaf of bread is {m} afghani. How many afghani do {cnt(k, 'نان')} make?")),
        _st(lambda k, m: (f"در هر قطار {fa(m)} درخت است. {fa(k)} قطار چند درخت دارد؟", f"In each row there are {cnt(m, 'درخت')}. How many trees do {nn(k, 'row')} have?")),
        _st(lambda k, m: (f"هر شاگرد {fa(m)} کتابچه می{Z}گیرد. {fa(k)} شاگرد چند کتابچه می{Z}گیرند؟",
                          f"Each pupil gets {cnt(m, 'کتابچه')}. How many notebooks do {cnt(k, 'شاگرد')} get?")),
    ],
    # n shared by k: (n, k)
    "/": [
        _st(lambda n, k: (f"{fa(n)} تخم را در {fa(k)} سبد برابر می{Z}گذاری. در هر سبد چند تخم است؟",
                          f"You put {cnt(n, 'تخم')} equally into {nn(k, 'basket')}. How many eggs are in each basket?")),
        _st(lambda n, k: (f"{fa(n)} افغانی را بین {fa(k)} خواهر و برادر برابر تقسیم کن. به هر کدام چند افغانی می{Z}رسد؟",
                          f"Share {n} afghani equally among {k} sisters and brothers. How many afghani does each one get?")),
        _st(lambda n, k: (f"{fa(n)} پیاله آب را بین {fa(k)} نفر برابر تقسیم کن. به هر نفر چند پیاله می{Z}رسد؟",
                          f"Share {cnt(n, 'پیاله')} of water equally among {k} people. How many cups does each person get?")),
        _st(lambda n, k: (f"هر نان {fa(k)} افغانی است. با {fa(n)} افغانی چند نان خریده می{Z}توانی؟",
                          f"Each loaf of bread is {k} afghani. How many loaves can you buy with {n} afghani?"), None, WHY_GROUPS),
        _st(lambda n, k: (f"{fa(n)} گوسفند را در {fa(k)} رمه برابر جدا می{Z}کنند. در هر رمه چند گوسفند است؟",
                          f"{cnt(n, 'گوسفند')} are split into {nn(k, 'flock')} of the same size. How many sheep are in each flock?")),
        _st(lambda n, k: (f"{fa(n)} چوکی را در قطارهای {fa(k)} تایی می{Z}چینی. چند قطار می{Z}شود؟",
                          f"You set {n} chairs in rows of {k}. How many rows does it make?"), None, WHY_GROUPS),
    ],
}


# The largest two numbers each story still makes sense with (nobody drinks
# nineteen cups of water in a morning), in the order of STORIES.
ANY = (10 ** 9, 10 ** 9)
STORY_MOST = {
    "+": [(99, 99), (40, 40), (20, 20), ANY, ANY, (6, 6), (40, 40), (60, 60), (40, 40)],
    "-": [(99, 99), (40, 40), (20, 20), ANY, ANY, (20, 20), (40, 40), (60, 60)],
    "diff": [(60, 60), (30, 30), (99, 99), (30, 30), (9, 9)],
    "*": [(20, 2), (10, 5), (20, 10), (20, 4), (12, 30), (30, 8), (20, 50), (30, 50), (40, 6)],
    "/": [(120, 12), ANY, (30, 10), (10 ** 9, 50), (200, 12), (200, 20)],
}
assert all(len(STORY_MOST[k]) == len(STORIES[k]) for k in STORIES)


def story_fits(kind, i, a, b) -> bool:
    return a <= STORY_MOST[kind][i][0] and b <= STORY_MOST[kind][i][1]


def village_item(s, rnd, intro, kind, t, a, b, rng, hi, script="W"):
    if kind == "*":
        text, pic, why = STORIES[kind][t]
    else:   # the stories take turns; one that does not fit these numbers is passed over
        fits = [i for i in range(len(STORIES[kind])) if story_fits(kind, i, a, b)]
        if not fits:
            raise Retry("no story for these numbers")
        text, pic, why = STORIES[kind][fits[t % len(fits)]]
    op = "-" if kind == "diff" else kind
    say = tr(*text(a, b))
    if op == "/":
        div_item(s, rnd, intro, a, b, rng, hi, say=say, why=why or WHY["/"], script=script)
        return
    show = f"p:{pic}*{a}" if isinstance(pic, str) and a <= 20 else ""
    extra = [a * b + rng.choice([-1, 1])] if op == "*" else []
    hop_item(s, rnd, intro, a, op, b, rng, hi, say=say, show=show, why=(why if isinstance(why, tuple) else None) or WHY[op],
             extra_prefer=extra, script=script)


def village_round(s, level, rnd, intro, kinds: dict, hi, n=N):
    """kinds: kind -> candidate (a, b). The stories of a kind take turns."""
    def gen(rng):
        share = n // len(kinds)
        t = rng.randrange(20)
        for j, (kind, cands) in enumerate(kinds.items()):
            want = share + (n - share * len(kinds) if j == 0 else 0)
            key = (lambda c: c[0] // c[1]) if kind == "/" else (lambda c: c[0] * c[1]) if kind == "*" else \
                  (lambda c: c[0] + c[1]) if kind == "+" else (lambda c: c[0] - c[1])
            usable = [c for c in cands if min(c) >= 2] or cands
            for a, b in pick_even(usable, want, rng, key=key, cap=2):
                if kind == "*":   # a story tied to one table (two legs, five fingers) only with that table
                    fits = [i for i, st in enumerate(STORIES["*"]) if st[1] in (None, b) and story_fits("*", i, a, b)]
                    tied = [i for i in fits if STORIES["*"][i][1] == b]
                    free = [i for i in fits if STORIES["*"][i][1] is None]
                    if not fits:
                        raise Retry("no story for these numbers")
                    pick = rng.choice(tied) if tied and (not free or rng.random() < 0.5) else rng.choice(free)
                    village_item(s, rnd, intro, kind, pick, a, b, rng, hi)
                else:
                    village_item(s, rnd, intro, kind, t, a, b, rng, hi)
                t += 1
    build(s, level, "hop", rnd, gen)


# ---------------------------------------------------------------------------
# 1. Count the Flock (listen_pick), levels 1 to 3
# ---------------------------------------------------------------------------

def flock(level: int) -> Sheet:
    if level == 6:
        return flock6(level)
    if level >= 4:
        return flock45(level)
    s = Sheet(LP_COLS)

    def B(rnd, gen, **kw):
        build(s, level, "flock", rnd, gen, **kw)

    def counting(rnd, lo, hi, script, top=20, n=N):
        def gen(rng):
            objs = rng.sample(COUNT_OBJS, len(COUNT_OBJS))
            for i, v in enumerate(even(lo, hi, n, rng)):
                count_item(s, rnd, I_COUNT if script == "W" else I_COUNT_D, v, objs[i], script, rng, top, w=i)
        B(rnd, gen)

    def hearing(rnd, values, scripts, lo, hi, prefer=lambda v: (), n=N, intro=I_HEAR):
        def gen(rng):
            cands = [(v, sc) for v in values for sc in scripts]
            for i, (v, sc) in enumerate(pick_even(cands, n, rng, key=lambda c: c[0])):
                hear_item(s, rnd, intro, v, sc, rng, lo, hi, prefer=prefer(v), w=i)
        B(rnd, gen)

    def matching(rnd, values, lo, hi, prefer=lambda v: (), n=N):
        def gen(rng):
            cands = [(v, sc) for v in values for sc in "WD"]
            for v, sc in pick_even(cands, n, rng, key=lambda c: c[0]):
                match_item(s, rnd, I_MATCH, v, sc, rng, lo, hi, prefer=prefer(v))
        B(rnd, gen)

    def comparing(rnd, values, lo, hi, intro=I_COMPARE, n=N):
        def gen(rng):
            for i, x in enumerate(pick_even(values, n, rng)):
                numeral_compare_item(s, rnd, intro, similar_numbers(x, rng, lo, hi), biggest=i % 2 == 0)
        B(rnd, gen)

    def nexting(rnd, nines, tens, others, lo, hi, n=N):
        """Before and after; some of them across a ten or a hundred."""
        def gen(rng):
            half = n // 2
            for v in rng.sample(nines, 4) + pick_even([x for x in others if x not in nines], half - 4, rng):
                next_item(s, rnd, I_NEXT, v, True, rng, lo, hi)
            for v in rng.sample(tens, 4) + pick_even([x for x in others if x not in tens], n - half - 4, rng):
                next_item(s, rnd, I_NEXT, v, False, rng, lo, hi)
        B(rnd, gen)

    if level == 1:
        counting("01", 1, 6, "W", 10)
        counting("02", 1, 6, "D", 10)
        counting("03", 4, 10, "W", 12)
        counting("04", 1, 10, "D", 12, n=20)
        matching("05", range(0, 11), 0, 10, n=20)
        hearing("06", range(0, 11), "WD", 0, 10, n=20)

        def most(rng):
            objs = rng.sample(COUNT_OBJS, N)
            for i, top in enumerate(even(4, 12, N, rng)):
                counts = [top, top - 1] + rng.sample(range(1, top - 1), 2)
                flock_compare_item(s, "07", I_MORE, objs[i], counts, most=True)
        B("07", most)
        counting("08", 11, 20, "W", n=20)
        counting("09", 11, 20, "D", n=20)
        hearing("10", range(11, 21), "WD", 0, 20, prefer=lambda v: [v - 10], n=20)
        matching("11", range(11, 21), 0, 20, prefer=lambda v: [v - 10], n=20)

        def compare(rng):
            objs = rng.sample(COUNT_OBJS, 6)
            for i, low in enumerate(even(2, 8, 6, rng)):
                counts = [low, low + 1] + rng.sample(range(low + 2, 14), 2)
                flock_compare_item(s, "12", I_COMPARE, objs[i], counts, most=False)
            for i, ans in enumerate(even(6, 20, 6, rng)):
                numeral_compare_item(s, "12", I_COMPARE, [ans] + rng.sample(range(0, ans), 3), True, script="WD"[i % 2])
            for i, ans in enumerate(even(0, 14, 6, rng)):
                numeral_compare_item(s, "12", I_COMPARE, [ans] + rng.sample(range(ans + 1, 21), 3), False, script="WD"[i % 2])
        B("12", compare)

    elif level == 2:
        hearing("01", range(10, 101, 10), "WD", 0, 100, prefer=lambda v: [v // 10 + 10 if 30 <= v <= 90 else None, v // 10], n=20)
        hearing("02", [x for x in range(21, 60) if x % 10], "W", 0, 100, prefer=digit_perms)
        hearing("03", [x for x in range(60, 100) if x % 10], "W", 0, 100, prefer=digit_perms)
        hearing("04", [x for x in range(21, 100) if x % 10], "D", 0, 100, prefer=digit_perms, n=20)
        matching("05", range(21, 100), 0, 100, prefer=digit_perms, n=20)

        def place(rng):
            for v in even(21, 99, 15, rng, ok=lambda x: x % 10 and x // 10 != x % 10) + [10 * t for t in rng.sample(range(2, 10), 3)]:
                place2_item(s, "06", I_PLACE, v // 10, v % 10, rng)
        B("06", place)

        def digits(rng):
            cands = [(v, ask) for v in range(21, 100) if v // 10 != v % 10 for ask in (True, False)]
            for v, ask in pick_even(cands, N, rng, key=lambda c: c[0] // 10 if c[1] else c[0] % 10, cap=2):
                digit_item(s, "07", I_DIGIT, v, ask, rng)
        B("07", digits)
        comparing("08", [x for x in range(21, 99) if x % 11 and x % 10], 10, 100)
        nexting("09", [19, 29, 39, 49, 59, 69, 79, 89, 99], [20, 30, 40, 50, 60, 70, 80, 90, 100], range(21, 99), 0, 101)

        def mix(rng):
            vals = iter(even(21, 98, N, rng, ok=lambda x: x % 11 and x % 10, cap=1))
            for i in range(3):
                v = next(vals)
                hear_item(s, "10", I_MIX, v, "D", rng, 0, 100, prefer=digit_perms(v), w=i)
                v = next(vals)
                match_item(s, "10", I_MIX, v, "WD"[i % 2], rng, 0, 100, prefer=digit_perms(v))
                v = next(vals)
                place2_item(s, "10", I_MIX, v // 10, v % 10, rng)
                v = next(vals)
                digit_item(s, "10", I_MIX, v, i % 2 == 0, rng)
                numeral_compare_item(s, "10", I_MIX, similar_numbers(next(vals), rng, 10, 100), biggest=i % 2 == 0)
                v = next(vals)
                if i % 2 == 0:
                    next_item(s, "10", I_MIX, v // 10 * 10 + 9, True, rng, 0, 101)
                else:
                    next_item(s, "10", I_MIX, v // 10 * 10, False, rng, 0, 101)
        B("10", mix)

    else:
        three = [x for x in range(111, 1000) if "0" not in str(x) and len(set(str(x))) == 3]
        zeros = [x for x in range(101, 1000) if "0" in str(x) and x % 100]
        hearing("01", range(100, 1001, 100), "WD", 0, 1000, prefer=lambda v: [v // 10, v - 100, v + 100], n=20)

        def twins(rng):
            for i, h in enumerate(even(1, 9, N, rng)):
                d = rng.randint(1, 9)
                v, twin = (100 * h + 10 * d, 100 * h + d) if i % 2 == 0 else (100 * h + d, 100 * h + 10 * d)
                hear_item(s, "02", I_HEAR, v, "W", rng, 0, 1000, prefer=[twin, 10 * h + d], w=i)
        B("02", twins)
        hearing("03", three, "W", 0, 1000, prefer=lambda v: digit_perms(v)[1:3])
        hearing("04", three + zeros, "D", 0, 1000, prefer=lambda v: digit_perms(v)[:2])
        matching("05", list(range(101, 1000)) + [1000], 0, 1000, prefer=lambda v: digit_perms(v)[:2])

        def place(rng):
            for v in pick_even(three, 13, rng) + pick_even([x for x in zeros + list(range(110, 1000, 10)) if x % 100], 5, rng):
                place3_item(s, "06", I_PLACE3, v // 100, v // 10 % 10, v % 10, rng)
        B("06", place)
        comparing("07", three, 100, 1000)
        nexting("08", [199, 299, 409, 599, 699, 809, 999, 119, 349], [200, 300, 400, 510, 600, 710, 800, 900, 1000], three, 0, 1001)
    return s


# ---------------------------------------------------------------------------
# 2. Number Hop (journey), levels 1 to 3
# ---------------------------------------------------------------------------

def hop(level: int) -> Sheet:
    if level == 6:
        return hop6(level)
    if level >= 4:
        return hop45(level)
    s = Sheet(LP_COLS)
    answer = lambda t: calc(*t)  # noqa: E731

    def B(rnd, gen, **kw):
        build(s, level, "hop", rnd, gen, **kw)

    def plain(rnd, intro, groups, hi, n=N, cap=CAP, prefer=None):
        """groups: lists of (a, op, b); the pool takes the same number from each."""
        groups = [sorted(set(g)) for g in (groups if isinstance(groups[0], list) else [groups])]

        def gen(rng):
            share = n // len(groups)
            for j, g in enumerate(groups):
                want = share + (n - share * len(groups) if j == 0 else 0)
                for i, (a, op, b) in enumerate(pick_even(g, want, rng, key=answer, cap=cap if len(groups) == 1 else 2)):
                    hop_item(s, rnd, intro, a, op, b, rng, hi, w=1 if i % 3 == 2 else 0, extra_prefer=prefer(a, op, b) if prefer else ())
        B(rnd, gen)

    def stories(rnd, adds, subs, hi, with_picture, n=N):
        def gen(rng):
            k = rng.randrange(6)
            for a, op, b in pick_even(adds, n // 2, rng, key=answer, cap=2) + pick_even(subs, n - n // 2, rng, key=answer, cap=2):
                story_item(s, rnd, I_STORY, a, op, b, rng, hi, k, with_picture)
                k += 1
        B(rnd, gen)

    def bonds(rnd, pairs, hi, n=N):
        """pairs: (a, total): a + _ = total."""
        def gen(rng):
            for i, (a, total) in enumerate(pick_even(pairs, n, rng, key=lambda c: c[1] - c[0])):
                addend_item(s, rnd, I_BOND, a, total, rng, hi, first=i % 3 == 2)
        B(rnd, gen)

    def counting(rnd, cands, hi, n=N):
        """cands: (start, how many, on?, step)."""
        def gen(rng):
            for a, k, on, step in pick_even(cands, n, rng, key=lambda c: c[0] + c[1] * c[3] * (1 if c[2] else -1)):
                count_on_item(s, rnd, I_COUNT_ON, a, k, on, rng, hi, step=step)
        B(rnd, gen)

    def pairs_of(kind, cands):
        return {kind: [(a, b) for a, b in cands]}

    if level == 1:
        add8 = [(a, "+", b) for a in range(1, 8) for b in range(1, 8) if a + b <= 8]
        add10 = [(a, "+", b) for a in range(1, 10) for b in range(1, 10) if 5 <= a + b <= 10]
        sub7 = [(a, "-", b) for a in range(2, 8) for b in range(1, a + 1)]
        sub10 = [(a, "-", b) for a in range(6, 11) for b in range(1, a + 1)]
        ten_n = [(10, "+", n) for n in range(1, 11)] + [(n, "+", 10) for n in range(1, 10)]
        add20 = [(a, "+", b) for a in range(11, 19) for b in range(1, 9) if a % 10 + b <= 9]
        add20 += [(b, "+", a) for a, _, b in add20 if b >= 3]
        sub20 = [(a, "-", b) for a in range(12, 20) for b in range(1, 10) if b <= a % 10]
        sub_teen = [(a, "-", b) for a in range(11, 21) for b in range(10, a + 1)]
        plain("01", I_ADD, add8, 10, n=16)
        plain("02", I_ADD, add10, 12)
        plain("03", I_SUB, sub7, 10)
        plain("04", I_SUB, sub10, 12)
        stories("05", add10 + add8, [t for t in sub10 + sub7 if t[0] > t[2]], 12, True)
        zeros = [(a, "+", 0) for a in range(1, 11)] + [(0, "+", a) for a in range(1, 11)] + [(a, "-", 0) for a in range(1, 11)]
        plain("06", I_BOTH, [zeros, [(a, "-", a) for a in range(1, 11)] + add10 + sub10], 12)
        plain("07", I_ADD, ten_n, 20)
        plain("08", I_ADD, add20, 20)
        plain("09", I_SUB, sub20, 20)
        plain("10", I_SUB, sub_teen, 20)
        stories("11", [t for t in add20 if t[0] > 10], sub20, 20, True)
        plain("12", I_BOTH, [add20, sub20, ten_n + sub_teen], 20)
        bonds("13", [(a, t) for t in range(5, 11) for a in range(1, t)], 12)

        def doubles(rng):
            objs = rng.sample(COUNT_OBJS, 6)   # level 1 does not cross ten: the doubles to ten, and ten and ten
            for i, a in enumerate((1, 2, 3, 4, 5, 10)):
                double_item(s, "14", I_DOUBLE1, a, rng, 22)
                hop_item(s, "14", I_DOUBLE1, a, "+", a, rng, 22, show=f"p:{objs[i][0]}*{a}")
                hop_item(s, "14", I_DOUBLE1, a, "+", a, rng, 22, w=1)
        B("14", doubles)
        counting("15", [(a, k, on, 1) for a in range(1, 20) for k in (1, 2, 3) for on in (True, False) if 0 <= (a + k if on else a - k) <= 20], 22)
        small_add = [(a, b) for a in range(1, 10) for b in range(1, 10) if 4 <= a + b <= 10]
        small_sub = [(a, b) for a in range(4, 11) for b in range(1, a)]
        village_round(s, 1, "16", I_VILLAGE, {"+": small_add, "-": small_sub}, 12)
        teen_add = [(a, b) for a, _, b in add20 if a > 10]
        teen_sub = [(a, b) for a, _, b in sub20]
        village_round(s, 1, "17", I_VILLAGE, {"+": teen_add, "-": teen_sub, "diff": small_sub + teen_sub}, 20)
        for row, a, op, b in HOP_META:  # level 1 never crosses ten
            if a > 10 or b > 10 or calc(a, op, b) > 10:
                assert op == "+" and (a % 10 + b % 10 <= 9 or 10 in (a, b)) or op == "-" and (b % 10 <= a % 10 or b >= 10), (a, op, b)
            assert calc(a, op, b) <= 20 and row["hop"], (a, op, b)

    elif level == 2:
        add20 = [(a, "+", b) for a in range(11, 19) for b in range(1, 9) if a % 10 + b <= 9]
        sub20 = [(a, "-", b) for a in range(12, 20) for b in range(1, 10) if b <= a % 10]
        from10 = [(10, "-", b) for b in range(1, 10)]
        cross9 = [(a, "+", b) for a in (8, 9) for b in range(3, 10) if a + b >= 11]
        cross9 += [(b, "+", a) for a, _, b in cross9 if b < 8]
        cross = [(a, "+", b) for a in range(2, 10) for b in range(2, 10) if a + b >= 11]
        subx = [(a, "-", b) for a in range(11, 19) for b in range(2, 10) if b > a % 10]
        from20 = [(20, "-", b) for b in range(1, 10)]
        doubles = [(a, "+", a) for a in range(5, 11)] + [(a, "+", a + 1) for a in range(5, 10)] + [(a + 1, "+", a) for a in range(5, 10)]
        tens_add = [(a, "+", b) for a in range(10, 100, 10) for b in range(10, 100, 10) if a + b <= 100]
        tens_sub = [(a, "-", b) for a in range(20, 101, 10) for b in range(10, a, 10)]
        plain("01", I_BOTH, [add20, sub20], 20)

        def to_ten(rng):   # what makes ten, and what is left of ten
            for i, a in enumerate(range(1, 10)):
                addend_item(s, "02", I_BOND, a, 10, rng, 20, first=i % 3 == 2)
            for i, (a, op, b) in enumerate(from10):
                hop_item(s, "02", I_BOND, a, op, b, rng, 20, w=i % 2)
        B("02", to_ten)
        plain("03", I_ADD, cross9, 20)
        plain("04", I_ADD, cross, 20)
        plain("05", I_SUB, [t for t in subx if t[0] <= 14], 20)
        plain("06", I_SUB, [t for t in subx if t[0] >= 15] + from20, 20)
        plain("07", I_BOTH, [cross, subx], 20)
        plain("08", I_ADD, doubles, 22, n=16)
        plain("09", I_TENS, tens_add, 110)
        plain("10", I_TENS, tens_sub, 110)

        def told(rng):
            k = rng.randrange(6)
            picks = pick_even(cross, 9, rng, key=answer, cap=2) + pick_even(subx, 9, rng, key=answer, cap=2)
            for i, (a, op, b) in enumerate(picks):
                if i % 3 == 2:
                    money_story(s, "11", I_STORY, a, op, b, rng, 20)
                else:
                    story_item(s, "11", I_STORY, a, op, b, rng, 20, k + i, False)
        B("11", told)
        plain("12", I_BOTH, [cross, subx, tens_add, tens_sub], 110, n=20)
        bonds("13", [(a, t) for t in range(11, 21) for a in range(3, 13) if 2 <= t - a <= 12], 20)

        def halves(rng):
            for a in range(1, 11):
                double_item(s, "14", I_DOUBLE, a + 10 if a <= 2 else a, rng, 40)
                halve_item(s, "14", I_DOUBLE, 2 * a, rng, 22)
        B("14", halves)
        on_back = [(a, k, on, 1) for a in range(6, 15) for k in (2, 3, 4) for on in (True, False) if (a + k > 10 > a if on else a - k < 10 < a)]
        by_ten = [(a, k, on, 10) for a in range(3, 98) for k in (1, 2, 3) for on in (True, False) if a % 10 and 0 < (a + 10 * k if on else a - 10 * k) < 100]
        def count(rng):
            picks = pick_even(on_back, 9, rng, key=lambda c: c[0] + c[1] * (1 if c[2] else -1), cap=2) + \
                pick_even(by_ten, 9, rng, key=lambda c: c[0] + 10 * c[1] * (1 if c[2] else -1), cap=1)
            for a, k, on, step in picks:
                count_on_item(s, "15", I_COUNT_ON, a, k, on, rng, 110, step=step)
        B("15", count)
        village_round(s, 2, "16", I_VILLAGE, {"+": [(a, b) for a, _, b in cross], "-": [(a, b) for a, _, b in subx]}, 20)
        village_round(s, 2, "17", I_MORE_THAN, {"diff": [(a, b) for a, _, b in subx + sub20 + from20 if a - b >= 2]}, 20)

    else:
        a1 = [(a, "+", b) for a in range(15, 90) for b in range(2, 10) if a % 10 and a % 10 + b >= 10]
        s1 = [(a, "-", b) for a in range(21, 96) for b in range(2, 10) if a % 10 < b]
        a2 = [(a, "+", b) for a in range(11, 80) for b in range(11, 80)
              if a % 10 and b % 10 and a % 10 + b % 10 <= 9 and a + b < 100]
        a2c = [(a, "+", b) for a in range(13, 80) for b in range(13, 80) if a % 10 + b % 10 >= 10 and a + b <= 100 and a % 10 and b % 10]
        s2b = [(a, "-", b) for a in range(31, 100) for b in range(12, 90) if a % 10 < b % 10 and a - b >= 3]
        plain("01", I_ADD, a1, 120)
        plain("02", I_SUB, s1, 120)
        plain("03", I_ADD, a2, 120)
        plain("04", I_ADD, a2c, 120)
        plain("05", I_SUB, s2b, 120)
        plain("06", I_BOTH, [a2c, s2b], 120)

        def table(t):
            return [(n, "*", t) for n in range(1, 11)] + [(t, "*", n) for n in range(1, 11) if n != t]

        plain("07", I_MUL, table(2), 120)
        plain("08", I_MUL, table(10), 120)
        plain("09", I_MUL, table(5), 120)
        plain("10", I_MUL, [table(2), table(5), table(10)], 120)
        h_add = [(a, "+", b) for a in range(100, 1000, 100) for b in range(100, 1000, 100) if a + b <= 1000]
        h_sub = [(a, "-", b) for a in range(200, 1001, 100) for b in range(100, a, 100)]
        plain("11", I_BOTH, [h_add, h_sub], 1100, prefer=lambda a, op, b: [calc(a, op, b) + 100, calc(a, op, b) - 100, calc(a, op, b) // 10])
        a3 = [(a, "+", b) for a in range(115, 880, 7) for b in range(13, 90, 3) if a % 10 + b % 10 >= 10 and a % 10 and b % 10 and a % 100 + b < 100]
        s3 = [(a, "-", b) for a in range(131, 990, 7) for b in range(13, 90, 3) if a % 10 < b % 10 and a % 100 > b]
        plain("12", I_BOTH, [a3, s3], 1100)
        to_100 = [(a, 100) for a in range(10, 100, 10)] + [(a, 100) for a in range(5, 100, 10)]
        to_ten = [(a, (a // 10 + 1) * 10) for a in range(21, 99) if a % 10]
        def missing(rng):
            for i, (a, total) in enumerate(pick_even(to_100, 9, rng, key=lambda c: c[1] - c[0], cap=1) +
                                           pick_even(to_ten, 9, rng, key=lambda c: c[1] - c[0], cap=1)):
                addend_item(s, "13", I_BOND, a, total, rng, 120, first=i % 3 == 2)
        B("13", missing)

        def halves(rng):
            for a in pick_even([x for x in range(12, 51) if x % 10 not in (0, 5) or x in (15, 25, 35, 45)], 9, rng):
                double_item(s, "14", I_DOUBLE, a, rng, 120)
            for n in pick_even([x for x in range(22, 101, 2)], 9, rng):
                halve_item(s, "14", I_DOUBLE, n, rng, 120)
        B("14", halves)
        times = [(k, m) for m in (2, 5, 10) for k in range(2, 11)]
        village_round(s, 3, "15", I_VILLAGE_MUL, {"*": times}, 120)
        village_round(s, 3, "16", I_VILLAGE, {"+": [(a, b) for a, _, b in a2c if b <= 49], "-": [(a, b) for a, _, b in s2b if b <= 49]}, 120)
        village_round(s, 3, "17", I_MORE_THAN, {"diff": [(a, b) for a, _, b in s2b if a - b <= 40]}, 120)
    return s


# ---------------------------------------------------------------------------
# 3. Market Scales (market), levels 1 to 3
# ---------------------------------------------------------------------------

_M_COUNT = tr("گوش کن و همان قدر روی ترازو بگذار.", "Listen and put that many on the scales.")
_M_PRICE = tr("قیمت را گوش کن و با سکه" + Z + "ها و نوت" + Z + "ها پول بده.", "Listen to the price and pay with the coins and notes.")
_M_BILL = tr("قیمت دو چیز را جمع کن و پول بده.", "Add the prices of the two things and pay.")
_M_TIMES = tr("چند تا می" + Z + "خری؟ ضرب کن و پول بده.", "How many do you buy? Multiply and pay.")
_M_CHANGE = tr("باقی پول مشتری را حساب کن و پس بده.", "Work out the customer's change and give it back.")
_M_KILO = tr("قیمت چند کیلو را حساب کن و پول بده.", "Work out the price of several kilos and pay.")
M_INTRO = {
    1: {**{f"{i:02d}": _M_COUNT for i in range(1, 7)}, "07": tr("هر دو را جمع کن و همه را روی ترازو بگذار.", "Add the two and put them all on the scales.")},
    2: {**{f"{i:02d}": _M_PRICE for i in range(1, 7)}, "07": _M_BILL},
    3: {"01": _M_BILL, "02": _M_BILL, "03": _M_TIMES, "04": _M_PRICE, "05": _M_BILL, "06": _M_CHANGE,
        "07": tr("قیمت سه چیز را جمع کن و پول بده.", "Add the prices of the three things and pay.")},
    4: {"01": tr("برابر تقسیم کن و حصه یک نفر را روی ترازو بگذار.", "Share equally and put one person's share on the scales."), "02": _M_TIMES, "03": _M_TIMES,
        "04": _M_KILO, "05": tr("قیمت نیم کیلو را حساب کن و پول بده.", "Work out the price of half a kilo and pay."), "06": _M_CHANGE,
        "07": tr("قیمت هر چیز را حساب کن، هر دو را جمع کن و پول بده.", "Work out the price of each thing, add the two and pay.")},
    5: {"01": _M_PRICE, "02": _M_TIMES, "03": _M_CHANGE, "04": _M_KILO,
        "05": tr("نیم قیمت یا حصه یک نفر را حساب کن و پول بده.", "Work out the half price or one person's share and pay."), "06": _M_CHANGE},
}
COUNT_GOODS = GOODS + [("tomato", "بادنجان رومی"), ("orange", "مالته"), ("pencil", "پنسل"), ("flower", "گل")]


def market(level: int) -> Sheet:
    if level == 6:
        return market6(level)
    if level >= 4:
        return market45(level)
    s = Sheet(MARKET_COLS)

    def B(rnd, gen, intro=None, **kw):
        s.intro[rnd] = intro or M_INTRO[level][rnd]
        build(s, level, "market", rnd, gen, **kw)

    def price_round(rnd, prices, units, goods, n=N):
        def gen(rng):
            shop = rng.sample(goods, len(goods))
            for j, p in enumerate(pick_even(prices, n, rng, cap=1) if len(prices) >= n else even(min(prices), max(prices), n, rng, ok=lambda x: x in prices)):
                pic, noun = shop[j % len(shop)]
                say = [tr(f"{noun} {fa(p)} {AFN} است. پولش را بده.", cap(f"{costs(noun, p)}. Pay for it.")),
                       tr(f"قیمت {noun} {fa(p)} {AFN} است. همان قدر پول بده.", f"The price of the {bare(noun)} is {p} afghani. Pay that much.")][j % 2]
                market_row(s, rnd, say, pic, p, units, "pay", pay_help(p, units))
        B(rnd, gen)

    def bill_round(rnd, pairs, units, first, second, n=N):
        both = f"هر دو چند {AFN} می{Z}شود؟ پولش را بده."
        both_en = "How many afghani do both make? Pay for it."

        def gen(rng):
            for j, (a, b) in enumerate(pick_even(pairs, n, rng, key=lambda c: c[0] + c[1])):
                (p1, n1) = first[j % len(first)]
                (p2, n2) = second[(j // len(first) + j) % len(second)]
                if n1 == n2:
                    (p2, n2) = second[(j + 1) % len(second)]
                market_row(s, rnd, tr(f"{n1} {fa(a)} {AFN} و {n2} {fa(b)} {AFN} است. {both}", cap(f"{costs(n1, a)} and {costs(n2, b)}. {both_en}")), p1, a + b,
                           units, "pay", tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}."))
        B(rnd, gen)

    if level == 1:
        for i, (lo, hi) in enumerate([(1, 6), (2, 8), (4, 10), (6, 12), (8, 15), (11, 20)]):
            rnd = f"{i + 1:02d}"

            def gen(rng, lo=lo, hi=hi, rnd=rnd):
                goods = rng.sample(COUNT_GOODS, len(COUNT_GOODS))
                for j, n in enumerate(even(lo, hi, N, rng)):
                    pic, noun = goods[j % len(goods)]
                    say = [tr(f"{fa(n)} {noun} بده.", f"Give {cnt(n, noun)}."),
                           tr(f"{fa(n)} {noun} می{Z}خواهم.", f"I want {cnt(n, noun)}.")][j % 2]
                    market_row(s, rnd, say, pic, n, [1], "count", tr(f"{fa(n)} دانه {noun} روی ترازو بگذار.", f"Put {cnt(n, noun)} on the scales."))
            B(rnd, gen)

        def and_more(rng):
            goods = rng.sample(COUNT_GOODS, len(COUNT_GOODS))
            pairs = [(a, b) for a in range(1, 9) for b in range(1, 6) if 3 <= a + b <= 10]
            for j, (a, b) in enumerate(pick_even(pairs, N, rng, key=lambda c: c[0] + c[1])):
                pic, noun = goods[j % len(goods)]
                market_row(s, "07", tr(f"{fa(a)} {noun} و {fa(b)} {noun} دیگر بده. همه را روی ترازو بگذار.", f"Give {cnt(a, noun)} and {b} more. Put them all on the scales."),
                           pic, a + b, [1], "count", tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}."))
        B("07", and_more)
    elif level == 2:
        plan = [((3, 12), 1, [1, 2, 5]), ((6, 16), 1, [1, 2, 5]), ((11, 29), 1, [1, 2, 5, 10]),
                ((20, 100), 10, [10, 20, 50]), ((21, 69), 1, [1, 2, 5, 10, 20, 50]),
                ((55, 100), 5, [1, 2, 5, 10, 20, 50, 100])]
        for i, ((lo, hi), step, units) in enumerate(plan):
            prices = [p for p in range(lo, hi + 1) if p % step == 0]
            price_round(f"{i + 1:02d}", prices, units, SHOP, n=N if len(prices) * 2 >= N else 16)
        bill_round("07", [(a, b) for a in range(2, 13) for b in range(2, 10) if a != b and 8 <= a + b <= 20], [1, 2, 5, 10], SHOP[:5], SHOP[5:] + SHOP[:2])
    else:
        bill_round("01", [(a, b) for a in range(10, 90, 10) for b in range(10, 90, 10) if a != b and a + b <= 100], [10, 20, 50], SHOP[:5], SHOP[3:])
        bill_round("02", [(a, b) for a in range(12, 59) for b in range(12, 59) if a % 10 + b % 10 >= 10 and a % 10 and b % 10 and a + b <= 100],
                   [1, 2, 5, 10, 20, 50], SHOP[2:7], SHOP[6:] + SHOP[:3])

        def several(rng):
            countable = [SHOP[0], SHOP[1], SHOP[2], SHOP[3], SHOP[4], GOODS[0], GOODS[5], GOODS[7]]
            deals = [(k, price) for price in (2, 5, 10) for k in range(2, 11)]
            for j, (k, price) in enumerate(pick_even(deals, N, rng, key=lambda c: c[0] * c[1], cap=2)):
                buy_row(s, "03", k, price, countable[j % len(countable)], [1, 2, 5, 10, 20, 50, 100])
        B("03", several)
        price_round("04", list(range(110, 501, 10)), [10, 20, 50, 100], BIG)
        bill_round("05", [(a, b) for a in range(100, 301, 10) for b in range(20, 201, 10) if a + b <= 500], [10, 20, 50, 100], BIG, SHOP[3:])

        def change(rng):
            deals = [(g, p) for g in (20, 50, 100) for p in range(g // 2, g) if p % 10]
            for j, (given, price) in enumerate(pick_even(deals, N, rng, key=lambda c: c[0] - c[1])):
                pic, noun = SHOP[j % len(SHOP)]
                left = given - price
                market_row(s, "06", tr(f"{noun} {fa(price)} {AFN} است. مشتری {fa(given)} {AFN} داد. چند {AFN} باقی می{Z}ماند؟ باقی را پس بده.", cap(f"{costs(noun, price)}. The customer gave {given} afghani. How many afghani are left over? Give the change back.")),
                           pic, left, [1, 2, 5, 10, 20, 50], "pay", tr(f"{fa(given)} منفی {fa(price)} مساوی {fa(left)}.", f"{given} minus {price} equals {left}."))
        B("06", change)

        def three(rng):
            triples = [(a, b, c) for a in range(10, 60, 10) for b in range(10, 60, 10) for c in range(10, 60, 10) if a < b and a + b + c <= 120]
            for j, (a, b, c) in enumerate(pick_even(triples, N, rng, key=sum)):
                (p1, n1), (p2, n2), (p3, n3) = SHOP[j % 10], SHOP[(j + 3) % 10], SHOP[(j + 6) % 10]
                total = a + b + c
                market_row(s, "07", tr(f"{n1} {fa(a)} {AFN}، {n2} {fa(b)} {AFN} و {n3} {fa(c)} {AFN} است. هر سه چند {AFN} می{Z}شود؟ پولش را بده.",
                                       cap(f"{costs(n1, a)}, {costs(n2, b)} and {costs(n3, c)}. How many afghani do all three make? Pay for it.")),
                           p1, total, [10, 20, 50, 100], "pay",
                           tr(f"{fa(a)} جمع {fa(b)} جمع {fa(c)} مساوی {fa(total)}.", f"{a} plus {b} plus {c} equals {total}."))
        B("07", three)
    return s


# ---------------------------------------------------------------------------
# 4. Carpet Weaver (builder), levels 1 to 3
# ---------------------------------------------------------------------------

def extras_for(seq, rng, k, hi=10_000_000):
    """k tiles that do not belong to the run: numbers in between, or near it,
    never one that would continue it at either end."""
    step = seq[1] - seq[0]
    banned = set(seq) | {seq[0] - step, seq[-1] + step}
    cands = []
    if abs(step) >= 2:
        cands += [x + (1 if step > 0 else -1) * rng.randint(1, abs(step) - 1) for x in seq[:-1]]
    cands += [seq[0] - 2 * step, seq[-1] + 2 * step, seq[0] - 3 * step, seq[-1] + 3 * step] + digit_perms(seq[len(seq) // 2])[:1]
    cands = uniq(x for x in cands if 0 <= x <= hi and x not in banned)
    if len(cands) < k:
        raise Retry("no room for extra tiles")
    head, tail = cands[:len(seq) - 1] if abs(step) >= 2 else [], cands[len(seq) - 1 if abs(step) >= 2 else 0:]
    picks = rng.sample(head, min(k, len(head))) if head else []
    return (picks + tail)[:k]


def seq_round(s, level, rnd, cands, n=16, dari_every=5, table=None, hi=10_000_000):
    """cands: (start, step, count). Runs of at most six tiles get extra tiles."""
    def gen(rng):
        for i, (start, step, count) in enumerate(rng.sample(sorted(set(cands)), n)):
            seq = [start + j * step for j in range(count)]
            room = 8 - count
            k = 0 if room == 0 else min(room, 2 if abs(step) >= 2 else 1) if (count >= 5 or i % 2) else 0
            extra = extras_for(seq, rng, k, hi) if k else []
            t = abs(step) if table is True else table
            seq_item(s, rnd, start, step, count, extra=extra, script="D" if dari_every and i % dari_every == dari_every - 1 else "W",
                     table=t if t and step > 0 and start % t == 0 else None)
    build(s, level, "weaver", rnd, gen)


def order_round(s, level, rnd, lo, hi, sizes=(4, 5), n=16, close=False):
    """Numbers to arrange, small to big and big to small."""
    def gen(rng):
        for i in range(n):
            k = sizes[i % len(sizes)]
            if close and i % 2:   # numbers that look alike: 34, 43, 30, 40, 44
                x = rng.randint(max(lo, 12), hi - 1)
                near_x = uniq([x] + [c for c in digit_perms(x) + [x - 1, x + 1, x - 10, x + 10, x + 9, x - 9, x - 100, x + 100, x // 10, x * 10 % 1000] if lo <= c <= hi])
                if len(near_x) < k:
                    raise Retry("too few look-alikes")
                numbers = [x] + rng.sample(near_x[1:], k - 1)
            else:
                numbers = even(lo, hi, k, rng, cap=1)
            order_item(s, rnd, numbers, up=i % 3 != 2)
    build(s, level, "weaver", rnd, gen)


def weaver(level: int) -> Sheet:
    if level == 6:
        return weaver6(level)
    if level >= 4:
        return weaver45(level)
    s = Sheet(BUILDER_COLS)

    def runs(starts, steps, counts, lo, hi):
        return [(a, st, c) for a in starts for st in steps for c in counts if lo <= a + st * (c - 1) <= hi and lo <= a <= hi]

    if level == 1:
        seq_round(s, 1, "01", runs(range(0, 8), [1], [3, 4, 5], 0, 10), dari_every=0)
        def dari(rng):
            for start, step, count in rng.sample(runs(range(0, 8), [1], [3, 4, 5, 6], 0, 10), 16):
                seq_item(s, "02", start, step, count, script="D")
        build(s, 1, "weaver", "02", dari)
        seq_round(s, 1, "03", runs(range(0, 6), [1], [6, 7, 8], 0, 12), dari_every=4)
        seq_round(s, 1, "04", runs(range(5, 13), [-1], [5, 6, 7], 0, 12), dari_every=4)
        seq_round(s, 1, "05", runs(range(8, 16), [1], [5, 6, 7], 8, 20) + runs(range(15, 21), [-1], [5, 6], 9, 20), dari_every=4)
        seq_round(s, 1, "06", runs(range(0, 12), [2], [4, 5, 6], 0, 20) + runs([5, 0], [5], [4], 0, 20) + runs(range(12, 21), [-2], [4, 5], 0, 20), dari_every=0)
        order_round(s, 1, "07", 0, 10, sizes=(4, 5))
        order_round(s, 1, "08", 0, 20, sizes=(5, 6, 4))
    elif level == 2:
        seq_round(s, 2, "01", runs(range(1, 60), [2], [6], 0, 70), dari_every=0)
        seq_round(s, 2, "02", runs(range(10, 51, 10), [10], [5, 6, 7, 8], 0, 100) + runs(range(60, 101, 10), [-10], [5, 6], 0, 100), dari_every=4)
        seq_round(s, 2, "03", runs(range(5, 71, 5), [5], [6, 7, 8], 0, 100), dari_every=0)
        order_round(s, 2, "04", 9, 99, sizes=(5, 5, 6), close=True)
        seq_round(s, 2, "05", [(a, 1, 6) for a in range(16, 97) if a % 10 >= 6], dari_every=4)
        seq_round(s, 2, "06", runs(range(20, 61, 2), [-2], [6], 0, 100) + runs(range(60, 101, 10), [-10], [6], 0, 100) +
                  runs(range(40, 101, 5), [-5], [6], 0, 100) + [(a, -1, 6) for a in range(24, 99) if a % 10 <= 4], dari_every=0)
        order_round(s, 2, "07", 0, 100, sizes=(6, 5, 6))
        seq_round(s, 2, "08", [(a, 10, c) for a in range(1, 40) if a % 10 for c in (5, 6) if a + 10 * (c - 1) < 100] +
                  [(a, -10, 5) for a in range(51, 100) if a % 10], dari_every=4)
    else:
        seq_round(s, 3, "01", runs(range(2, 21, 2), [2], [6, 8], 0, 40) + runs(range(20, 41, 2), [-2], [6], 0, 40), table=2, dari_every=0)
        seq_round(s, 3, "02", runs(range(5, 61, 5), [5], [6, 8], 0, 100) + runs(range(50, 101, 5), [-5], [6], 0, 100), table=5, dari_every=0)
        seq_round(s, 3, "03", runs(range(10, 61, 10), [10], [5, 6, 8], 0, 130) + runs(range(80, 131, 10), [-10], [6], 0, 130), table=10, dari_every=4)
        seq_round(s, 3, "04", runs(range(100, 501, 100), [100], [5, 6, 8], 0, 1000) + runs(range(50, 601, 50), [50], [6], 0, 1000) +
                  runs(range(600, 1001, 100), [-100], [6], 0, 1000) + runs(range(120, 500, 110), [100], [6], 0, 1000), dari_every=0)
        order_round(s, 3, "05", 99, 1000, sizes=(5, 6, 5), close=True)
        seq_round(s, 3, "06", [(a, 2, 6) for a in range(92, 400, 100)] + [(a, 5, 6) for a in range(85, 900, 100)] + [(a, 10, 6) for a in range(170, 1000, 100) if a + 50 <= 1000] +
                  [(a, 1, 6) for a in range(195, 1000, 100) if a + 5 <= 1000] + [(a, 1, 6) for a in range(397, 1000, 100) if a + 5 <= 1000] + [(a, 50, 6) for a in range(250, 751, 100)], dari_every=0)

        def sums(rng):
            facts = [(a, b) for b in (2, 5, 10) for a in range(2, 11) if len({a, b, a * b}) == 3] + [(b, a) for b in (2, 5, 10) for a in range(3, 11) if len({a, b, a * b}) == 3]
            for a, b in pick_even(facts, 16, rng, key=lambda c: c[0] * c[1], cap=2):
                wrong = uniq(x for x in (a * b + b, a + b, a * b - a, a * b + 1) if x not in (a, b, a * b) and x > 0)[:2]
                sum_item(s, "07", a, "*", b, wrong)
        build(s, 3, "weaver", "07", sums)
        order_round(s, 3, "08", 0, 1000, sizes=(6, 6, 5))
    return s


# ---------------------------------------------------------------------------
# 5. Share the Bread (sorter), levels 1 to 3
# ---------------------------------------------------------------------------

SHAPED["rectangle"].append(("note", "نوت"))
FRACTIONS["whole"] += [("orange", "مالته پوره"), None]   # the library's pomegranate shows a cut piece beside the fruit: not a clear whole
FRACTIONS["half"] += [("orange_half", "نیم مالته"), ("pomegranate_half", "نیم انار")]
FRACTIONS["quarter"] += [("orange_quarter", "چارک مالته"), ("pomegranate_quarter", "چارک انار")]
FRACTION_NOUNS += ["مالته", "انار"]
I_ESTIMATE = tr("زود ببین، نشمار: از ده کمتر است یا بیشتر؟", "Look quickly, do not count: is it fewer than 10 or more?")
I_COUNT_TRUE = tr("بشمار و بگو: درست است یا غلط؟", "Count and say: is it true or false?")


def sorter(level: int) -> Sheet:
    if level == 6:
        return sorter6(level)
    if level >= 4:
        return sorter45(level)
    s = Sheet(SORTER_COLS)

    def B(rnd, gen, **kw):
        build(s, level, "sorter", rnd, gen, **kw)

    def shapes_round(rnd, plan):
        rows = [(SHAPED[shape][i], shape) for shape, idx in plan for i in idx]

        def gen(rng):
            for (pic, name), shape in rng.sample(rows, len(rows)):
                row = s.add(round=rnd, intro_fa=I_SHAPES, thing=pic, say_fa=tr(name, bare(name)), basket=SHAPES[shape][0],
                            basket_say_fa=tr(SHAPES[shape][1], bare(SHAPES[shape][1])))
                SORT_META.append((row, "shape", shape))
        B(rnd, gen, small="" if len(rows) >= 16 else "the library has only this many things of these shapes")

    def parity_round(rnd, pool, n=N):
        def gen(rng):
            evens = pick_even([x for x in pool if x % 2 == 0], n // 2, rng)
            odds = pick_even([x for x in pool if x % 2 == 1], n - n // 2, rng)
            for x in spread(evens + odds, rng):
                basket = EVEN if x % 2 == 0 else ODD
                row = s.add(round=rnd, intro_fa=I_PARITY, thing=W(x), say_fa=tr(fa(x), str(x)), basket=basket[0], basket_say_fa=tr(basket[1], bare(basket[1])))
                SORT_META.append((row, "parity", x))
        B(rnd, gen)

    def fraction_round(rnd, kinds, named=True):
        """named=False: the speech names only the thing, not its fraction, so
        the child has to judge from the picture."""
        rows = [(FRACTIONS[kind][i], kind, i) for kind in kinds for i in range(len(FRACTIONS[kind])) if FRACTIONS[kind][i]]

        def gen(rng):
            for (pic, name), kind, i in rng.sample(rows, len(rows)):
                basket = FRAC_BASKET[kind]
                noun = FRACTION_NOUNS[i]
                en = FRACTION_EN[kind].format(a=art(bare(noun)), x=bare(noun)) if named else bare(noun)
                if not named:
                    name = noun
                    assert basket[1] not in name
                row = s.add(round=rnd, intro_fa=I_FRACTION, thing=pic, say_fa=tr(name, en), basket=basket[0], basket_say_fa=tr(basket[1], bare(basket[1])))
                SORT_META.append((row, "fraction", kind))
        B(rnd, gen, small="" if len(rows) >= 16 else "six things are drawn whole, in halves and in quarters")

    if level == 1:
        shapes_round("01", [("circle", [0, 1, 2, 3, 4, 5, 6, 7]), ("square", [0, 1, 2, 3])])
        shapes_round("02", [("circle", [0, 1, 2, 3, 4, 5, 6, 7]), ("triangle", [0, 1, 2, 3])])
        shapes_round("03", [("circle", [1, 2, 3, 4, 5, 6, 7]), ("square", [0, 1, 2, 3]), ("triangle", [0, 1, 2, 3])])
        shapes_round("04", [("circle", [0, 1, 2, 3, 4, 5, 6, 7]), ("square", [0, 1, 2, 3]), ("triangle", [0, 1, 2, 3]), ("rectangle", [0, 1, 2, 3, 4])])
    elif level == 2:
        parity_round("01", range(0, 17), n=16)
        parity_round("02", range(11, 41))
        fraction_round("03", ["whole", "half"])
        fraction_round("04", ["whole", "half", "quarter"])
    else:
        parity_round("01", range(21, 100))

        def five_hundred(rng):
            below = [499, 490, 450] + pick_even(range(100, 440), 6, rng)
            above = [501, 510, 550] + pick_even(range(560, 1000), 6, rng)
            for x in spread(below + above, rng):
                less = x < 500
                en = "less than 500" if less else "more than 500"
                row = s.add(round="02", intro_fa=I_500, thing=W(x), say_fa=tr(fa(x), str(x)),
                            basket="f:" + tr(("f:کمتر از ۵۰۰" if less else "f:بیشتر از ۵۰۰")[2:], en),
                            basket_say_fa=tr("کمتر از پنج" + Z + "صد" if less else "بیشتر از پنج" + Z + "صد", en))
                SORT_META.append((row, "500", x))
        B("02", five_hundred)
        fraction_round("03", ["whole", "half", "quarter"], named=False)
        parity_round("04", range(101, 1000))
    return s


# ---------------------------------------------------------------------------
# 6. Shape Mason (listen_pick), levels 1 to 3
# ---------------------------------------------------------------------------

I_RIDDLE_SHAPE = tr("گوش کن و بگو کدام شکل است.", "Listen and say which shape it is.")
I_CLOCK_STORY = tr("قصه را گوش کن و ساعت درست را پیدا کن.", "Listen to the story and find the right clock.")
I_LENGTH_STORY = tr("قصه را گوش کن و درازی را حساب کن.", "Listen to the story and work out the length.")


def mason(level: int) -> Sheet:
    if level == 6:
        return mason6(level)
    if level >= 4:
        return mason45(level)
    s = Sheet(LP_COLS)
    order = ["circle", "square", "triangle", "rectangle"]

    def B(rnd, gen, **kw):
        build(s, level, "mason", rnd, gen, **kw)

    if level == 1:
        def find(rng):
            for shape in order:
                pic, name = SHAPES[shape]
                says = [tr(f"{name} کدام است؟", f"Which one is the {bare(name)}?"), tr(f"شکل {name} را پیدا کن.", f"Find the {bare(name)} shape."),
                        tr(f"کدام شکل {name} است؟", f"Which shape is a {bare(name)}?"), tr(f"{name} را نشان بده.", f"Show the {bare(name)}.")]
                for say in says:
                    lp(s, "01", I_SHAPE, say, pic, [SHAPES[o][0] for o in order if o != shape], help_fa=tr(f"این شکل {name} است.", f"This shape is a {bare(name)}."))
        B("01", find, few=4)

        def things(rng):
            cands = [(shape, k) for shape in order for k in range(1, len(SHAPED[shape]))]
            for shape, k in rng.sample(cands, 16):
                pic, noun = SHAPED[shape][k]
                wrong = [rng.choice(SHAPED[o][1:])[0] for o in order if o != shape and not (shape == "rectangle" and o == "square")]
                if shape == "rectangle":  # a square is a rectangle too: never offer one as a wrong choice
                    wrong.append(rng.choice([p for p, _ in SHAPED["circle"][1:] if p not in wrong]))
                    assert not set(wrong) & {p for p, _ in SHAPED["square"]}
                assert len(set(wrong)) == 3
                lp(s, "02", I_SHAPE_OBJ, tr(f"کدام چیز شکل {SHAPES[shape][1]} دارد؟", f"Which thing has the shape of a {bare(SHAPES[shape][1])}?"), pic, wrong,
                   help_fa=tr(f"{noun} شکل {SHAPES[shape][1]} دارد.", f"The {bare(noun)} has the shape of a {bare(SHAPES[shape][1])}."))
        B("02", things)

        def lengths(rng):
            for i, (noun, long_pic, short_pic, long_word, short_word) in enumerate(LENGTHS):
                for j, d in enumerate((1, 2)):
                    other = LENGTHS[(i + d) % len(LENGTHS)]
                    says = [tr(f"کدام {noun} {long_word} است؟", f"Which {bare(noun)} is {bare(long_word)}?"),
                            tr(f"{noun} {long_word} را پیدا کن.", f"Find the {bare(long_word)} {bare(noun)}.")]
                    lp(s, "03", I_LONG, says[j], long_pic, [short_pic, other[1], other[2]],
                       help_fa=tr(f"این {noun} {long_word} است.", f"This {bare(noun)} is {bare(long_word)}."))
                    says = [tr(f"کدام {noun} {short_word} است؟", f"Which {bare(noun)} is {bare(short_word)}?"),
                            tr(f"{noun} {short_word} را پیدا کن.", f"Find the {bare(short_word)} {bare(noun)}.")]
                    lp(s, "03", I_LONG, says[j], short_pic, [long_pic, other[1], other[2]],
                       help_fa=tr(f"این {noun} {short_word} است.", f"This {bare(noun)} is {bare(short_word)}."))
        B("03", lengths)
        corners = {"circle": 0, "square": 4, "triangle": 3, "rectangle": 4}

        def count_corners(rng):
            for shape, what in [("triangle", "گوشه"), ("square", "ضلع"), ("circle", "گوشه"), ("rectangle", "گوشه"),
                                ("triangle", "ضلع"), ("square", "گوشه"), ("rectangle", "ضلع")]:
                pic, name = SHAPES[shape]
                n = corners[shape]
                says = [tr(f"{name} چند {what} دارد؟", f"How many {many(what)} does a {bare(name)} have?"),
                        tr(f"{what}{Z}های {name} را بشمار. چند تا است؟", f"Count the {many(what)} of the {bare(name)}. How many are there?")]
                for say in (says if n != 4 else says[:1] if what == "گوشه" else says[1:]):   # four is the answer of two shapes: ask each once
                    row = lp(s, "04", I_CORNER, say, W(n), [W(x) for x in near(n, rng, 0, 8)], show=pic,
                             help_fa=(tr(f"{name} {fa(n)} {what} دارد.", f"A {bare(name)} has {cnt(n, what)}.") if n else tr(f"{name} هیچ {what} ندارد.", f"A {bare(name)} has no {many(what)}.")))
                    MASON_META.append((row, n))
            others = ["shape_circle", "shape_triangle", "shape_square", "shape_rectangle"]
            for say, right, help_fa in [
                    (tr("کدام شکل سه گوشه دارد؟", "Which shape has 3 corners?"), "shape_triangle", tr("مثلث سه گوشه دارد.", "A triangle has 3 corners.")),
                    (tr("کدام شکل هیچ گوشه ندارد؟", "Which shape has no corners?"), "shape_circle", tr("دایره هیچ گوشه ندارد.", "A circle has no corners.")),
                    (tr("کدام شکل سه ضلع دارد؟", "Which shape has 3 sides?"), "shape_triangle", tr("مثلث سه ضلع دارد.", "A triangle has 3 sides.")),
                    (tr("شکلی را پیدا کن که سه گوشه دارد.", "Find the shape that has 3 corners."), "shape_triangle", tr("مثلث سه گوشه دارد.", "A triangle has 3 corners.")),
                    (tr("شکلی را پیدا کن که هیچ گوشه ندارد.", "Find the shape that has no corners."), "shape_circle", tr("دایره هیچ گوشه ندارد.", "A circle has no corners.")),
                    (tr("شکلی را پیدا کن که سه ضلع دارد.", "Find the shape that has 3 sides."), "shape_triangle", tr("مثلث سه ضلع دارد.", "A triangle has 3 sides."))]:
                lp(s, "04", I_CORNER, say, right, [o for o in others if o != right], help_fa=help_fa)
        B("04", count_corners, few=5)

        def riddles(rng):
            clues = {
                "circle": [tr("گرد هستم و هیچ گوشه ندارم. من کدام شکل هستم؟", "I am round and have no corners. Which shape am I?")],
                "square": [tr("چهار ضلع برابر و چهار گوشه دارم. من کدام شکل هستم؟", "I have 4 equal sides and 4 corners. Which shape am I?")],
                "triangle": [tr("سه ضلع و سه گوشه دارم. من کدام شکل هستم؟", "I have 3 sides and 3 corners. Which shape am I?")],
                "rectangle": [tr("چهار گوشه دارم. دو ضلع من دراز و دو ضلع من کوتاه است. من کدام شکل هستم؟", "I have 4 corners. Two of my sides are long and two are short. Which shape am I?")],
            }
            for shape in order:
                pic, name = SHAPES[shape]
                for say in clues[shape]:
                    lp(s, "05", I_RIDDLE_SHAPE, say, pic, [SHAPES[o][0] for o in order if o != shape], help_fa=tr(f"این شکل {name} است.", f"This shape is a {bare(name)}."))
                for thing, noun in rng.sample(SHAPED[shape][1:], 3):
                    wrong = [SHAPES[o][0] for o in order if o != shape]
                    lp(s, "05", I_RIDDLE_SHAPE, tr(f"{noun} چه شکلی دارد؟", f"What shape does the {bare(noun)} have?"), pic, wrong, show=thing,
                       help_fa=tr(f"{noun} شکل {name} دارد.", f"The {bare(noun)} has the shape of a {bare(name)}."))
        B("05", riddles, few=4)

    elif level == 2:
        def clock(h):
            return f"clock_{(h - 1) % 12 + 1}"

        def wrap(h):
            return (h - 1) % 12 + 1

        hand = lambda h: tr(f"عقربه کوتاه طرف {fa(h)} است و عقربه دراز طرف دوازده.", f"The short hand points to {h} and the long hand to 12.")  # noqa: E731

        def hear_clock(rnd, hours):
            def gen(rng):
                for h in hours:
                    says = [tr(f"ساعت {fa(h)} است. ساعت درست را پیدا کن.", f"It is {h} o'clock. Find the right clock."),
                            tr(f"کدام ساعت، {fa(h)} را نشان می{Z}دهد؟", f"Which clock shows {h} o'clock?"),
                            tr(f"ساعت {fa(h)} کدام است؟", f"Which one is {h} o'clock?")]
                    for j, say in enumerate(says):
                        wrong = [clock(h - 1), clock(h + 1), clock(h + 6)] if j != 1 else [clock(h + 2), clock(h - 2), clock(h + 6)]
                        row = lp(s, rnd, I_CLOCK, say, clock(h), wrong, help_fa=hand(h))
                        MASON_META.append((row, h))
            B(rnd, gen)

        hear_clock("01", [1, 2, 3, 4, 5, 6])
        hear_clock("02", [7, 8, 9, 10, 11, 12])

        def read(rng):
            asks = [tr("ساعت چند است؟", "What time is it?"), tr("این ساعت چند را نشان می" + Z + "دهد؟", "What time does this clock show?"),
                    tr("عقربه کوتاه را ببین. ساعت چند است؟", "Look at the short hand. What time is it?")]
            for i, (h, sc) in enumerate(pick_even([(h, sc) for h in range(1, 13) for sc in "WD"], N, rng, key=lambda c: c[0])):
                wrong = near(h, rng, 1, 12, [12 if h != 12 else 6, wrap(h + 1), wrap(h - 1)])
                row = lp(s, "03", I_CLOCK_READ, asks[i % 3], num(h, sc), [num(x, sc) for x in wrong], show=clock(h),
                         help_fa=tr(f"عقربه کوتاه طرف {fa(h)} است. ساعت {fa(h)} است.", f"The short hand points to {h}. It is {h} o'clock."))
                MASON_META.append((row, h))
        B("03", read)

        def shifted(rnd, shifts, intro, n=N):
            def gen(rng):
                cands = [(h, d) for h in range(1, 13) for d in shifts]
                for h, d in pick_even(cands, n, rng, key=lambda c: wrap(c[0] + c[1]), cap=2):
                    then = wrap(h + d)
                    k = abs(d)
                    if d > 0:
                        say = tr(f"حالا ساعت {fa(h)} است. {fa(k)} ساعت بعد، ساعت چند می{Z}شود؟", f"Now it is {h} o'clock. {nn(k, 'hour')} later, what time will it be?")
                        help_fa = tr(f"{fa(k)} ساعت بعد از {fa(h)}، ساعت {fa(then)} می{Z}شود.", f"{nn(k, 'hour')} after {h}, it is {then} o'clock.")
                    else:
                        say = tr(f"حالا ساعت {fa(h)} است. {fa(k)} ساعت پیش، ساعت چند بود؟", f"Now it is {h} o'clock. {nn(k, 'hour')} ago, what time was it?")
                        help_fa = tr(f"{fa(k)} ساعت پیش از {fa(h)}، ساعت {fa(then)} بود.", f"{nn(k, 'hour')} before {h}, it was {then} o'clock.")
                    wrong = near(then, rng, 1, 12, [h, wrap(h - d), wrap(then + 1), wrap(then - 1)])
                    row = lp(s, rnd, intro, say, W(then), [W(x) for x in wrong], show=clock(h), help_fa=help_fa)
                    MASON_META.append((row, then))
            B(rnd, gen)

        shifted("04", [1, -1], I_CLOCK_LATER)
        shifted("05", [2, 3, -2], I_CLOCK_LATER)

        def day(rng):
            stories = [
                lambda h, k: (f"مکتب ساعت {fa(h)} شروع می{Z}شود و {fa(k)} ساعت بعد تمام می{Z}شود. مکتب ساعت چند تمام می{Z}شود؟",
                              f"School starts at {h} o'clock and ends {nn(k, 'hour')} later. At what time does school end?"),
                lambda h, k: (f"مادر ساعت {fa(h)} خمیر کرد. نان {fa(k)} ساعت بعد پخته شد. نان ساعت چند پخته شد؟",
                              f"Mother made the dough at {h} o'clock. The bread was baked {nn(k, 'hour')} later. At what time was the bread baked?"),
                lambda h, k: (f"چوپان ساعت {fa(h)} رمه را به کوه برد و {fa(k)} ساعت بعد برگشت. او ساعت چند برگشت؟",
                              f"The shepherd took the flock to the mountain at {h} o'clock and came back {nn(k, 'hour')} later. At what time did the shepherd come back?"),
                lambda h, k: (f"ساعت {fa(h)} به راه افتادی و {fa(k)} ساعت راه رفتی. ساعت چند رسیدی؟",
                              f"You set off at {h} o'clock and walked for {nn(k, 'hour')}. At what time did you arrive?"),
            ]
            cands = [(h, k) for h in range(5, 12) for k in (1, 2, 3, 4)]
            for i, (h, k) in enumerate(pick_even(cands, N, rng, key=lambda c: wrap(c[0] + c[1]), cap=2)):
                then = wrap(h + k)
                wrong = uniq([clock(h), clock(then + 1), clock(then - 1), clock(then + 6)])[:3]
                row = lp(s, "06", I_CLOCK_STORY, tr(*stories[i % len(stories)](h, k)), clock(then), wrong,
                         help_fa=tr(f"{fa(k)} ساعت بعد از {fa(h)}، ساعت {fa(then)} می{Z}شود.", f"{nn(k, 'hour')} after {h}, it is {then} o'clock."))
                MASON_META.append((row, then))
        B("06", day)

    else:
        def q(rnd, intro, say, ans, prefer, help_fa, rng, hi=2000):
            row = lp(s, rnd, intro, say, W(ans), [W(x) for x in near(ans, rng, 0, hi, prefer)], help_fa=help_fa)
            MASON_META.append((row, ans))

        def convert(rng):
            for m in range(1, 11):
                q("01", I_LENGTH, tr(f"{fa(m)} {M} چند {CM} است؟", f"How many centimetres is {nn(m, 'metre')}?"), m * 100, [m * 10, m * 100 + 100, m],
                  tr(f"هر متر صد {CM} است. {fa(m)} {M}، {fa(m * 100)} {CM} می{Z}شود.", f"Each metre is 100 centimetres. {nn(m, 'metre')} makes {m * 100} centimetres."), rng)
            q("01", I_LENGTH, tr(f"نیم {M} چند {CM} است؟", "How many centimetres is half a metre?"), 100 // 2, [5, 500, 20],
              tr(f"یک متر صد {CM} است. نیم آن پنجاه {CM} است.", "One metre is 100 centimetres. Half of it is 50 centimetres."), rng)
            for c in rng.sample(range(200, 1001, 100), 7):
                q("01", I_LENGTH, tr(f"{fa(c)} {CM} چند {M} است؟", f"How many metres is {c} centimetres?"), c // 100, [c // 10, c // 100 + 1, c // 100 - 1],
                  tr(f"هر صد {CM} یک {M} است. {fa(c)} {CM}، {fa(c // 100)} {M} می{Z}شود.", f"Every 100 centimetres is 1 metre. {c} centimetres makes {nn(c // 100, 'metre')}."), rng)
        B("01", convert)
        nouns_cm, nouns_m = ["چوب", "ریسمان", "تکه", "سیم"], ["دیوار", "ریسمان", "جوی", "سرک"]

        def adds(rng):
            pairs = [(a, b) for a in range(12, 80) for b in range(8, 60) if a > b and a + b <= 100 and ((a + b) % 5 == 0 or a % 10 + b % 10 >= 10)]
            for i, (a, b) in enumerate(pick_even(pairs, N, rng, key=lambda c: c[0] + c[1], cap=1)):
                unit = CM if i % 2 == 0 else M
                noun = (nouns_cm if unit == CM else nouns_m)[i // 2 % 4]
                q("02", I_LENGTH, tr(f"یک {noun} {fa(a)} {unit} است و {noun} دیگر {fa(b)} {unit}. هر دو با هم چند {unit} می{Z}شود؟", f"One {bare(noun)} is {a} {many(unit)} and another {bare(noun)} is {b} {many(unit)}. How many {many(unit)} do both make together?"),
                  a + b, [a + b - 10, a - b, a + b + 10], tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}."), rng)
        B("02", adds)

        def subs(rng):
            pairs = [(a, b) for a in range(30, 101) for b in range(12, 70) if a - b >= 8 and (a % 10 < b % 10 or a % 10 == 0)]
            cut = ["ریسمان", "تکه", "چوب", "سیم"]
            for i, (a, b) in enumerate(pick_even(pairs, N, rng, key=lambda c: c[0] - c[1], cap=1)):
                unit = CM if i % 2 == 0 else M
                noun = cut[i // 2 % 4]
                q("03", I_LENGTH, tr(f"یک {noun} {fa(a)} {unit} بود. {fa(b)} {unit} آن بریده شد. چند {unit} ماند؟", f"A {bare(noun)} was {a} {many(unit)}. {b} {many(unit)} of it was cut off. How many {many(unit)} are left?"),
                  a - b, [a - b + 10, a + b, a - b - 10], tr(f"{fa(a)} منفی {fa(b)} مساوی {fa(a - b)}.", f"{a} minus {b} equals {a - b}."), rng)
        B("03", subs)

        def mixed(rng):
            pairs = [(m, c) for m in range(1, 10) for c in list(range(5, 100, 5)) + [8, 2, 12]]
            for m, c in pick_even(pairs, 12, rng, key=lambda p: p[0] * 100 + p[1], cap=1):
                q("04", I_LENGTH, tr(f"{fa(m)} {M} و {fa(c)} {CM}، چند {CM} می{Z}شود؟", f"{nn(m, 'metre')} and {c} centimetres make how many centimetres?"), m * 100 + c, [m * 10 + c, m + c, m * 100 + c * 10],
                  tr(f"{fa(m)} {M}، {fa(m * 100)} {CM} است. {fa(m * 100)} جمع {fa(c)} مساوی {fa(m * 100 + c)}.", f"{nn(m, 'metre')} is {m * 100} centimetres. {m * 100} plus {c} equals {m * 100 + c}."), rng)
            for n in pick_even(range(105, 200, 5), 6, rng):
                q("04", I_LENGTH, tr(f"{fa(n)} {CM}، یک {M} و چند {CM} است؟", f"{n} centimetres is 1 metre and how many centimetres?"), n - 100, [n, (n - 100) // 10, n - 100 + 10],
                  tr(f"یک {M} صد {CM} است. {fa(n)} منفی صد مساوی {fa(n - 100)}.", f"One metre is 100 centimetres. {n} minus 100 equals {n - 100}."), rng)
        B("04", mixed)

        def times(rng):
            things = [("تخته", "plank", "planks", 2), ("ریسمان", "rope", "ropes", 5), ("توپ تکه", "roll of cloth", "rolls of cloth", 10),
                      ("چوب", "stick", "sticks", 2), ("سیم", "wire", "wires", 5), ("دیوار", "wall", "walls", 10)]
            cands = [(k, i) for i in range(len(things)) for k in range(2, 11)]
            for k, i in pick_even(cands, 12, rng, key=lambda c: c[0] * things[c[1]][3], cap=2):
                noun, en, en_many, m = things[i]
                q("05", I_LENGTH_STORY, tr(f"هر {noun} {fa(m)} {M} است. {fa(k)} {noun} چند {M} می{Z}شود؟", f"Each {en} is {nn(m, 'metre')}. How many metres do {k} {en_many} make?"),
                  k * m, [k + m, (k + 1) * m, k * m - 1], tr(f"{fa(k)} ضرب {fa(m)} مساوی {fa(k * m)}.", f"{k} times {m} equals {k * m}."), rng)
            for n in pick_even(range(20, 101, 10), 6, rng):
                q("05", I_LENGTH_STORY, tr(f"یک ریسمان {fa(n)} {M} است. آن را از میان دو نیم می{Z}کنی. هر نیم چند {M} است؟", f"A rope is {n} metres. You cut it in the middle into two halves. How many metres is each half?"),
                  n // 2, [n, n // 2 + 5, n // 2 - 5, n - 2], tr(f"نیم {fa(n)}، {fa(n // 2)} است، چون {fa(n // 2)} جمع {fa(n // 2)} مساوی {fa(n)}.", f"Half of {n} is {n // 2}, because {n // 2} plus {n // 2} equals {n}."), rng)
        B("05", times)

        def longer(rng):
            pairs = [(a, b) for a in range(25, 100) for b in range(12, 80) if 5 <= a - b <= 45]
            pairs_of = [("دیوار", "wall", "حویلی", "yard"), ("ریسمان", "rope", "سیم", "wire"), ("جوی", "stream", "سرک", "road")]
            for i, (a, b) in enumerate(pick_even(pairs, N, rng, key=lambda c: c[0] - c[1], cap=1)):
                n1, e1, n2, e2 = pairs_of[i % 3]
                unit = M if i % 2 else CM
                q("06", I_LENGTH_STORY, tr(f"{n1} {fa(a)} {unit} است و {n2} {fa(b)} {unit}. {n1} چند {unit} درازتر است؟", f"The {e1} is {a} {many(unit)} and the {e2} is {b} {many(unit)}. How many {many(unit)} longer is the {e1}?"),
                  a - b, [a + b, a - b + 10, a - b - 1], tr(f"{WHY_DIFF[0]} {fa(a)} منفی {fa(b)} مساوی {fa(a - b)}.", f"{WHY_DIFF[1]} {a} minus {b} equals {a - b}."), rng)
        B("06", longer)
    return s

# ---------------------------------------------------------------------------
# Levels 4 and 5: Count the Flock (listen_pick)
# ---------------------------------------------------------------------------

def flock45(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    def B(rnd, gen, **kw):
        build(s, level, "flock", rnd, gen, **kw)

    if level == 4:
        shares = [(n, k) for n in range(6, 21) for k in range(2, 7) if n % k == 0 and n // k >= 2]
        groups = [(k, m) for k in range(3, 10) for m in range(3, 7)]

        def share(rng):
            for i, (n, k) in enumerate(pick_even(shares, N, rng, key=lambda c: c[0] // c[1])):
                share_item(s, "01", I_SHARE, n, k, SHARE_OBJS[i % 8], rng)
        B("01", share)

        def group(rng):
            for i, (k, m) in enumerate(pick_even(groups, N, rng, key=lambda c: c[0] * c[1], cap=1)):
                group_item(s, "02", I_GROUPS, k, m, SHARE_OBJS[(i + 3) % 8], rng)
        B("02", group)

        def half(rng):
            for i, n in enumerate(range(6, 21, 2)):
                half_item(s, "03", I_HALF, n, rng, obj=SHARE_OBJS[(i + 5) % 8])
            for i, n in enumerate(pick_even(range(22, 121, 2), 10, rng)):
                half_item(s, "03", I_HALF, n, rng, script="D" if i % 2 else "W")
        B("03", half)

        def parts(rng):
            for q in pick_even(range(8, 81, 4), 9, rng):
                quarter_item(s, "04", I_PARTS, q, rng)
            for t in pick_even(range(6, 61, 3), 9, rng):
                third_item(s, "04", I_PARTS, t, rng)
        B("04", parts)

        def pies(rng):
            for which, ((k, n), name, en) in enumerate(PIES4):
                others = [pie(*kn) for kn, _, _ in PIES4 if kn != (k, n)]
                for j, say in enumerate([tr(f"کدام شکل {name} را نشان می{Z}دهد؟", f"Which picture shows {en}?"),
                                         tr(f"{name} کدام است؟", f"Which one is {en}?")]):
                    wrong = (others[(which + j) % 4:] + others[:(which + j) % 4])[:3]
                    row = lp(s, "05", I_PIE, say, pie(k, n), wrong,
                             help_fa=tr(f"{name} یعنی {fa(k)} حصه از {fa(n)} حصه برابر.", f"{cap(en)} means {k} of {n} equal parts."))
                    CHECK_META.append((row, Fraction(k, n)))
            cands = [(k, n, whole) for k, n in PIES5 for whole in (True, False)]
            for k, n, whole in pick_even(cands, 8, rng, key=lambda c: c[1] if c[2] else c[0], cap=2):
                if whole:
                    parts_item(s, "05", I_PIE, k, n, rng)
                else:
                    numq(s, "05", I_PIE, tr("چند حصه این دایره رنگ شده است؟", "How many parts of this circle are coloured?"), k, [n, k + 1, k - 1, n - k],
                         tr(f"{fa(k)} حصه از {fa(n)} حصه رنگ شده است.", f"{k} of the {n} parts {'is' if k == 1 else 'are'} coloured."), rng, 9, lo=1, show=pie(k, n))
        B("05", pies)

        def mix(rng):
            picks = pick_even(shares, 3, rng, key=lambda c: c[0] // c[1])
            for i in range(3):
                share_item(s, "06", I_MIX, picks[i][0], picks[i][1], SHARE_OBJS[(i * 2) % 8], rng)
                group_item(s, "06", I_MIX, rng.randint(3, 9), rng.randint(3, 6), SHARE_OBJS[(i * 2 + 1) % 8], rng)
                half_item(s, "06", I_MIX, rng.choice(range(24, 121, 2)), rng, script="D" if i == 2 else "W")
                quarter_item(s, "06", I_MIX, rng.choice(range(44, 101, 4)), rng)
                third_item(s, "06", I_MIX, rng.choice(range(33, 91, 3)), rng)
                half_item(s, "06", I_MIX, rng.choice(range(8, 21, 2)), rng, obj=SHARE_OBJS[(i + 4) % 8])
        B("06", mix)
    else:
        top = 10_000_000
        four = [x for x in range(1234, 9877) if "0" not in str(x) and len(set(str(x))) == 4]

        def hear(rnd, intro, values, scripts="W", prefer=lambda v: (), n=N):
            def gen(rng):
                cands = [(v, sc) for v in values for sc in scripts]
                for i, (v, sc) in enumerate(pick_even(cands, n, rng, key=lambda c: c[0])):
                    hear_item(s, rnd, intro, v, sc, rng, 0, top, prefer=prefer(v), w=i)
            B(rnd, gen)

        hear("01", I_THOUSANDS, list(range(2000, 10001, 1000)) + [20000, 30000, 50000], "WD", prefer=lambda v: [v // 10, v + 1000, v * 10])

        def forms(rng):
            for i, a in enumerate(even(1, 9, 9, rng, cap=1)):
                b = rng.randint(1, 9)
                fs = [1000 * a + 100 * b, 1000 * a + 10 * b, 1000 * a + b]
                v = fs[i % 3]
                hear_item(s, "02", I_BIG, v, "W", rng, 0, top, prefer=[f for f in fs if f != v] + [100 * a + b], w=i)
            for i, v in enumerate(pick_even(four, 9, rng)):
                hear_item(s, "02", I_BIG, v, "W", rng, 0, top, prefer=rng.sample(digit_perms(v), 2), w=i)
        B("02", forms)
        hear("03", I_BIG, [12000, 25000, 40000, 75000, 100000, 250000, 500000, 1000000, 15000, 30000, 60000, 90000, 120000, 300000,
                           750000, 2000000, 45000, 18000, 150000, 600000], prefer=lambda v: [v // 10, v * 10 if v < 1000000 else v // 100, v + 1000])

        def dari(rng):
            picks = pick_even(four, 12, rng) + pick_even(range(10500, 99000, 500), 6, rng)
            for i, v in enumerate(picks):
                if i % 2 == 0:
                    hear_item(s, "04", I_BIG, v, "D", rng, 0, top, prefer=rng.sample(digit_perms(v), 2), w=i // 2)
                else:
                    match_item(s, "04", I_MATCH, v, "D" if i % 4 == 1 else "W", rng, 0, top, prefer=rng.sample(digit_perms(v), 2))
        B("04", dari)

        def place(rng):
            zeros = [1000 * a + 10 * b + c for a in range(1, 10) for b in range(1, 10) for c in range(1, 10) if a == b + 1] + \
                    [1000 * a + 100 * b + c for a in range(1, 10) for b in range(1, 10) for c in range(1, 10) if a == c + 2] + \
                    [1000 * a + c for a in range(1, 10) for c in range(1, 10)]
            for v in pick_even(four, 11, rng) + pick_even(zeros, 7, rng):
                place4_item(s, "05", I_PLACE4, v, rng)
        B("05", place)

        def compare(rng):
            for i, x in enumerate(pick_even(four, 6, rng) + pick_even(range(12345, 98765, 1111), 3, rng)):
                numeral_compare_item(s, "06", I_COMPARE, similar_numbers(x, rng, 1000, 99999), biggest=i % 2 == 0)
            for v in (999, 9999, 1999, 4099, 99999):
                next_item(s, "06", I_NEXT, v, True, rng, 0, top)
            for v in (2000, 10000, 5000, 100000):
                next_item(s, "06", I_NEXT, v, False, rng, 0, top)
        B("06", compare)
    return s


# ---------------------------------------------------------------------------
# Levels 4 and 5: Number Hop (journey)
# ---------------------------------------------------------------------------

I_FACTOR = tr("عددی را پیدا کن که کم است تا ضرب درست شود.", "Find the number that is missing to make the multiplication right.")
I_TIMES_WORDS = tr("دو چند، سه چند، نیم و چارک عددها را پیدا کن.", "Find the double, the triple, the half and the quarter of the numbers.")
I_BIG_STORY = tr("قصه را گوش کن و با عددهای بزرگ حساب کن.", "Listen to the story and work it out with the big numbers.")
I_MISSING_BIG = tr("عددی را پیدا کن که کم است تا حساب درست شود.", "Find the number that is missing to make the sum right.")


def stories4(rng) -> list:
    """Word problems of level 4: (question, a, op, b)."""
    out = []
    k, m = rng.randint(3, 9), rng.randint(5, 9)
    out.append((tr(f"{fa(k)} قطار چوکی است. در هر قطار {fa(m)} چوکی است. همه چند چوکی می{Z}شود؟",
                   f"There are {k} rows of chairs. In each row there are {m} chairs. How many chairs is that altogether?"), k, "*", m))
    k = rng.choice([3, 5, 6, 7, 8, 9])
    out.append((tr(f"هر گوسفند چهار پای دارد. {fa(k)} گوسفند چند پای دارد؟", f"Each sheep has 4 legs. How many legs do {k} sheep have?"), k, "*", 4))
    k = rng.choice([2, 3, 4, 5, 6, 8])
    out.append((tr(f"یک هفته هفت روز است. {fa(k)} هفته چند روز می{Z}شود؟", f"One week is 7 days. How many days do {k} weeks make?"), k, "*", 7))
    k, m = rng.randint(4, 9), rng.choice([6, 8, 9])
    out.append((tr(f"هر صندوق {fa(m)} انار دارد. {fa(k)} صندوق چند انار دارد؟", f"Each box has {m} pomegranates. How many pomegranates do {k} boxes have?"), k, "*", m))
    k, c = rng.randint(3, 9), rng.randint(3, 9)
    out.append((tr(f"{fa(k * c)} پنسل را بین {fa(k)} شاگرد برابر تقسیم کن. به هر شاگرد چند پنسل می{Z}رسد؟",
                   f"Share {k * c} pencils equally among {k} pupils. How many pencils does each pupil get?"), k * c, "/", k))
    c = rng.choice([2, 3, 4, 5, 6, 8])
    out.append((tr(f"هر هفته هفت روز است. {fa(7 * c)} روز چند هفته می{Z}شود؟", f"Each week is 7 days. How many weeks do {7 * c} days make?"), 7 * c, "/", 7))
    m, c = rng.choice([6, 8, 9]), rng.randint(3, 9)
    out.append((tr(f"{fa(m * c)} سیب را در سبدها می{Z}گذاری، در هر سبد {fa(m)} سیب. چند سبد لازم است؟",
                   f"You put {m * c} apples into baskets, {m} apples in each basket. How many baskets are needed?"), m * c, "/", m))
    k, c = rng.choice([4, 6, 7, 8]), rng.randint(3, 9)
    out.append((tr(f"{fa(k * c)} نان را بین {fa(k)} خانواده برابر تقسیم کن. به هر خانواده چند نان می{Z}رسد؟",
                   f"Share {k * c} loaves of bread equally among {k} families. How many loaves does each family get?"), k * c, "/", k))
    return out


def stories5(rng) -> list:
    out = []
    k, m = rng.randint(6, 12), rng.choice([24, 25, 32, 35, 40])
    out.append((tr(f"در یک مکتب {fa(k)} صنف است. در هر صنف {fa(m)} شاگرد است. همه چند شاگرد می{Z}شود؟",
                   f"In a school there are {k} classes. In each class there are {m} pupils. How many pupils is that altogether?"), k, "*", m))
    k = rng.choice([3, 4, 5, 6, 7, 8])
    out.append((tr(f"یک سال دوازده ماه دارد. {fa(k)} سال چند ماه می{Z}شود؟", f"One year has 12 months. How many months do {k} years make?"), k, "*", 12))
    k = rng.choice([2, 3, 4, 5])
    out.append((tr(f"یک روز بیست و چهار ساعت دارد. {fa(k)} روز چند ساعت می{Z}شود؟", f"One day has 24 hours. How many hours do {k} days make?"), k, "*", 24))
    k, m = rng.randint(12, 25), rng.choice([50, 7, 25])
    out.append((tr(f"هر بوری {fa(m)} کیلو است. {fa(k)} بوری چند کیلو می{Z}شود؟", f"Each sack is {m} kilos. How many kilos do {k} sacks make?"), k, "*", m))
    k, m = rng.choice([15, 18, 24]), rng.choice([12, 15, 20])
    out.append((tr(f"در یک باغ {fa(k)} قطار درخت است. در هر قطار {fa(m)} درخت است. همه چند درخت می{Z}شود؟",
                   f"In a garden there are {k} rows of trees. In each row there are {m} trees. How many trees is that altogether?"), k, "*", m))
    k, c = rng.choice([4, 5, 6, 8]), rng.choice([15, 20, 25, 30, 45])
    out.append((tr(f"{fa(k * c)} کتاب را بین {fa(k)} صنف برابر تقسیم می{Z}کنیم. به هر صنف چند کتاب می{Z}رسد؟",
                   f"We share {k * c} books equally among {k} classes. How many books does each class get?"), k * c, "/", k))
    k, c = rng.choice([3, 4, 5]), rng.choice([120, 150, 250, 300])
    out.append((tr(f"{fa(k * c)} {AFN} را {fa(k)} نفر برابر تقسیم می{Z}کنند. به هر نفر چند {AFN} می{Z}رسد؟",
                   f"{k} people share {k * c} afghani equally. How many afghani does each person get?"), k * c, "/", k))
    c = rng.choice([3, 4, 6, 7, 9])
    out.append((tr(f"یک سال دوازده ماه دارد. {fa(12 * c)} ماه چند سال می{Z}شود؟", f"One year has 12 months. How many years do {12 * c} months make?"), 12 * c, "/", 12))
    return out


BIG_STORIES = {
    "+": [
        lambda a, b: (f"در صندوق مکتب {fa(a)} {AFN} بود. {fa(b)} {AFN} دیگر جمع شد. حالا چند {AFN} است؟",
                      f"There were {a} afghani in the school's box. {b} afghani more were collected. How many afghani are there now?"),
        lambda a, b: (f"یک دهقان {fa(a)} کیلو گندم درو کرد و همسایه او {fa(b)} کیلو. هر دو با هم چند کیلو گندم درو کردند؟",
                      f"A farmer harvested {a} kilos of wheat and the neighbour {b} kilos. How many kilos of wheat did both harvest together?"),
        lambda a, b: (f"یک قریه {fa(a)} نفر دارد و قریه دیگر {fa(b)} نفر. هر دو قریه چند نفر دارند؟",
                      f"One village has {a} people and another village has {b} people. How many people do both villages have?"),
    ],
    "-": [
        lambda a, b: (f"در گدام {fa(a)} کیلو آرد بود. {fa(b)} کیلو فروخته شد. چند کیلو آرد ماند؟",
                      f"There were {a} kilos of flour in the store. {b} kilos were sold. How many kilos of flour are left?"),
        lambda a, b: (f"از قریه تا شهر {fa(a)} متر راه است. {fa(b)} متر را رفته{Z}ای. چند متر دیگر مانده است؟",
                      f"From the village to the town it is {a} metres. You have walked {b} metres. How many more metres are left?"),
        lambda a, b: (f"یک خانواده {fa(a)} {AFN} داشت و {fa(b)} {AFN} را خرج کرد. چند {AFN} ماند؟",
                      f"A family had {a} afghani and spent {b} afghani. How many afghani are left?"),
    ],
    "diff": [
        lambda a, b: (f"یک قریه {fa(a)} نفر دارد و قریه دیگر {fa(b)} نفر. قریه اول چند نفر بیشتر دارد؟",
                      f"One village has {a} people and another village has {b} people. How many more people does the first village have?"),
        lambda a, b: (f"یک گاو {fa(a)} {AFN} و یک گوسفند {fa(b)} {AFN} است. گاو چند {AFN} قیمت{Z}تر است؟",
                      f"A cow is {a} afghani and a sheep is {b} afghani. How many afghani more does the cow cost?"),
    ],
}


def hop45(level: int) -> Sheet:
    s = Sheet(LP_COLS)
    product = lambda t: t[0] * t[2]  # noqa: E731

    def B(rnd, gen, **kw):
        build(s, level, "hop", rnd, gen, **kw)

    def times(rnd, intro, cands, hi, prefer=lambda a, b: [], script="W", n=N, cap=2):
        def gen(rng):
            for i, (a, op, b) in enumerate(pick_even(cands, n, rng, key=product, cap=cap)):
                hop_item(s, rnd, intro, a, op, b, rng, hi, extra_prefer=prefer(a, b) + [a * b + rng.choice([-1, 1])], script=script, w=1 if i % 3 == 2 else 0)
        B(rnd, gen)

    def divide(rnd, cands, hi, prefer=lambda a, b: [], n=N, cap=2):
        def gen(rng):
            for i, (a, b) in enumerate(pick_even(cands, n, rng, key=lambda c: c[0] // c[1], cap=cap)):
                div_item(s, rnd, I_DIV, a, b, rng, hi, extra_prefer=prefer(a, b), w=1 if i % 3 == 2 else 0)
        B(rnd, gen)

    def told(rnd, make, hi):
        def gen(rng):
            items = uniq(make(rng) + make(rng) + make(rng), key=lambda it: it[0])[:N]
            if len(items) < 16:
                raise Retry("the same story twice")
            for say, a, op, b in items:
                if op == "/":
                    div_item(s, rnd, I_STORY, a, b, rng, hi, say=say, why=WHY_GROUPS if "چند سبد" in say or "چند هفته" in say or "چند سال" in say else WHY["/"])
                else:
                    hop_item(s, rnd, I_STORY, a, op, b, rng, hi, say=say, extra_prefer=[a * b + rng.choice([-1, 1])], why=WHY["*"])
        B(rnd, gen)

    if level == 4:
        for i, t in enumerate((3, 4, 6, 7, 8, 9)):
            cands = [(n, "*", t) for n in range(2, 11)] + [(t, "*", n) for n in range(2, 11) if n != t]
            times(f"{i + 1:02d}", I_MUL, cands, 120, n=16)
        every = uniq([(a, "*", b) for a in (3, 4, 6, 7, 8, 9) for b in range(2, 11)], key=lambda t: tuple(sorted((t[0], t[2]))))
        times("07", I_MUL_D, [(a, op, b) if (a + b) % 2 else (b, op, a) for a, op, b in every], 120, script="D")
        divide("08", [(b * c, b) for b in (2, 3, 4, 5) for c in range(2, 11)], 120)
        divide("09", [(b * c, b) for b in (6, 7, 8, 9) for c in range(2, 11)], 120)
        told("10", stories4, 120)
        village_round(s, 4, "11", I_VILLAGE_MUL, {"*": [(k, m) for m in range(3, 10) for k in range(2, 11)]}, 120)
        village_round(s, 4, "12", I_VILLAGE_DIV, {"/": [(k * c, k) for k in range(2, 10) for c in range(2, 11)]}, 120)

        def factor(rng):
            cands = [(a, a * b) for a in range(3, 10) for b in range(2, 11)]
            for i, (a, total) in enumerate(pick_even(cands, N, rng, key=lambda c: c[1] // c[0], cap=2)):
                addend_item(s, "13", I_FACTOR, a, total, rng, 120, first=i % 3 == 2, op="*")
        B("13", factor)

        def words(rng):
            for a in pick_even(range(11, 51), 5, rng):
                double_item(s, "14", I_TIMES_WORDS, a, rng, 200)
            for a in pick_even(range(6, 34), 4, rng):
                lp(s, "14", I_TIMES_WORDS, tr(f"سه چند {fa(a)} چند می{Z}شود؟", f"Triple {a} makes how many?"), W(3 * a),
                   [W(x) for x in near(3 * a, rng, 0, 200, [2 * a, a + 3, 3 * a + 3])],
                   help_fa=tr(f"سه چند {fa(a)} یعنی سه ضرب {fa(a)}. سه ضرب {fa(a)} مساوی {fa(3 * a)}.", f"Triple {a} means 3 times {a}. 3 times {a} equals {3 * a}."),
                   truth=lambda c, a=a: val(c) == 3 * a)
            for n in pick_even(range(30, 121, 2), 5, rng):
                half_item(s, "14", I_TIMES_WORDS, n, rng)
            for n in pick_even(range(12, 101, 4), 4, rng):
                quarter_item(s, "14", I_TIMES_WORDS, n, rng)
        B("14", words)
    else:
        top = 100000
        adds = [(a, "+", b) for a in range(500, 9001, 500) for b in range(500, 9001, 500) if a + b <= 10000 and (a % 1000 or b % 1000)]
        subs = [(a, "-", b) for a in range(2000, 10001, 500) for b in range(500, a, 500) if a % 1000 == 0 and b % 1000]

        def thousands(rng):
            for i, (a, op, b) in enumerate(pick_even(adds, 9, rng, key=lambda t: calc(*t), cap=1) + pick_even(subs, 9, rng, key=lambda t: calc(*t), cap=1)):
                r = calc(a, op, b)
                hop_item(s, "01", I_THOUSAND_SUM, a, op, b, rng, top, extra_prefer=[r + 1000, r - 1000, r + 100], w=1 if i % 3 == 2 else 0)
        B("01", thousands)
        tens = [(a, "*", 10) for a in range(12, 100) if a % 10] + [(a, "*", 100) for a in range(3, 60)]
        tens += [(10 * a, "*", b) for a in range(2, 10) for b in range(3, 10)] + [(b, "*", 10 * a) for a in range(2, 10) for b in range(3, 10)]
        tens += [(100 * a, "*", b) for a in range(2, 10) for b in range(2, 10)]
        times("02", I_TEN_TIMES, tens, top, prefer=lambda a, b: [a * b * 10, a * b // 10, a * b + 10], cap=1)
        times("03", I_MUL_BIG, [(a, "*", b) for a in range(11, 45) for b in (2, 3, 4) if a % 10 and (a % 10) * b < 10 and (a // 10) * b < 10], top,
              prefer=lambda a, b: [a * b + 10, a * b - 1], cap=1)
        times("04", I_MUL_BIG, [(a, "*", b) for a in range(13, 100) for b in range(3, 10) if (a % 10) * b >= 10], top,
              prefer=lambda a, b: [(a // 10 * b) * 10 + (a % 10 * b) % 10, a * b + 10, a * b - 10], cap=1)   # the carried tens forgotten
        times("05", I_MUL_BIG, [(a, "*", b) for a in range(102, 460) for b in (2, 3, 4, 5) if a % 10 and a * b < 1000], top,
              prefer=lambda a, b: [a * b + 100, a * b - 10, a * b + 10], cap=1)
        times("06", I_MUL_BIG, [(a, "*", b) for a in range(11, 26) for b in range(11, 16) if a != b], top,
              prefer=lambda a, b: [a * (b % 10) + a * (b // 10), a * b + 10, a * b - 100], cap=1)   # the ten of the second number counted as one
        long_div = [(b * c, b) for b in range(2, 10) for c in range(11, 41) if b * c <= 200 and c % 10]
        by_ten = [(10 * c, 10) for c in range(12, 90) if c % 10] + [(100 * c, 100) for c in range(2, 40)]

        def long(rng):
            for i, (a, b) in enumerate(pick_even(long_div, 11, rng, key=lambda c: c[0] // c[1], cap=1) + pick_even(by_ten, 7, rng, key=lambda c: c[0] // c[1], cap=1)):
                div_item(s, "07", I_DIV, a, b, rng, top, extra_prefer=[a // b + 10, a // b * 10 if b >= 10 else None], w=1 if i % 3 == 2 else 0)
        B("07", long)
        told("08", stories5, top)

        def big(rng):
            plus = [(a, b) for a in range(500, 8001, 250) for b in range(250, 4001, 250) if a > b and (a + b) % 500 == 0]
            minus = [(a, b) for a in range(1000, 10001, 500) for b in range(250, 5001, 250) if a - b >= 250]
            picks = [("+", c) for c in pick_even(plus, 7, rng, key=sum, cap=1)] + [("-", c) for c in pick_even(minus, 6, rng, key=lambda c: c[0] - c[1], cap=1)] + \
                    [("diff", c) for c in pick_even(minus, 5, rng, key=lambda c: c[0] - c[1], cap=1)]
            for i, (kind, (a, b)) in enumerate(picks):
                text = BIG_STORIES[kind][i % len(BIG_STORIES[kind])]
                op = "+" if kind == "+" else "-"
                r = calc(a, op, b)
                why = WHY_DIFF if kind == "diff" else WHY_ALL if kind == "+" and i % 3 else WHY[op]
                hop_item(s, "09", I_BIG_STORY, a, op, b, rng, top, say=tr(*text(a, b)), why=why, extra_prefer=[r + 1000, r - 100, r + 500])
        B("09", big)
        village_round(s, 5, "10", I_VILLAGE_MUL, {"*": [(k, m) for m in (12, 15, 20, 24, 25, 30, 50) for k in range(3, 13)]}, top)
        village_round(s, 5, "11", I_VILLAGE_DIV, {"/": [(k * c, k) for k in range(3, 10) for c in (11, 12, 13, 14, 15, 16, 18, 20, 21, 22, 24, 25, 30, 35, 40, 45, 50)]}, top)

        def missing(rng):
            mult = [(a, a * b) for a in (10, 100) for b in range(12, 100) if b % 10]
            add = [(a, 1000) for a in range(50, 1000, 50)] + [(a, 10000) for a in range(500, 10000, 500)]
            for i, (a, total) in enumerate(pick_even(mult, 9, rng, key=lambda c: c[1] // c[0], cap=1)):
                addend_item(s, "12", I_MISSING_BIG, a, total, rng, top, first=i % 2 == 1, op="*")
            for i, (a, total) in enumerate(pick_even(add, 9, rng, key=lambda c: c[1] - c[0], cap=1)):
                addend_item(s, "12", I_MISSING_BIG, a, total, rng, top, first=i % 3 == 2)
        B("12", missing)
    return s


# ---------------------------------------------------------------------------
# Levels 4 and 5: Market Scales (market)
# ---------------------------------------------------------------------------

def market45(level: int) -> Sheet:
    s = Sheet(MARKET_COLS)
    small = [1, 2, 5, 10, 20, 50]

    def B(rnd, gen, **kw):
        s.intro[rnd] = M_INTRO[level][rnd]
        build(s, level, "market", rnd, gen, **kw)

    def change_row(rnd, j, k, p, given, obj, units):
        pic, noun = obj
        left = given - k * p
        market_row(s, rnd, tr(f"مشتری {fa(k)} {noun} می{Z}خرد. هر {noun} {fa(p)} {AFN} است. مشتری {fa(given)} {AFN} داد. چند {AFN} باقی می{Z}ماند؟ باقی را پس بده.",
                              f"The customer buys {cnt(k, noun)}. Each {one(noun)} is {p} afghani. The customer gave {given} afghani. How many afghani are left over? Give the change back."),
                   pic, left, units, "pay",
                   tr(f"{fa(k)} ضرب {fa(p)} مساوی {fa(k * p)}. {fa(given)} منفی {fa(k * p)} مساوی {fa(left)}.",
                      f"{k} times {p} equals {k * p}. {given} minus {k * p} equals {left}."))

    if level == 4:
        def share(rng):
            shares = [(n, k) for n in range(8, 41) for k in range(2, 7) if n % k == 0 and 2 <= n // k <= 10]
            for j, (n, k) in enumerate(pick_even(shares, N, rng, key=lambda c: c[0] // c[1], cap=2)):
                pic, noun = COUNTABLE[(j + 5) % len(COUNTABLE)]
                market_row(s, "01", tr(f"{fa(n)} {noun} را بین {fa(k)} نفر برابر تقسیم کن. حصه یک نفر را روی ترازو بگذار.",
                                       f"Share {cnt(n, noun)} equally among {k} people. Put one person's share on the scales."),
                           pic, n // k, [1], "count", tr(f"{fa(n)} تقسیم {fa(k)} مساوی {fa(n // k)}.", f"{n} divided by {k} equals {n // k}."))
        B("01", share)
        for rnd, prices in (("02", (3, 4, 6)), ("03", (7, 8, 9))):
            def deals(rng, rnd=rnd, prices=prices):
                for j, (k, p) in enumerate(pick_even([(k, p) for p in prices for k in range(3, 11)], N, rng, key=lambda c: c[0] * c[1], cap=2)):
                    buy_row(s, rnd, k, p, COUNTABLE[(j + int(rnd)) % len(COUNTABLE)], small)
            B(rnd, deals)

        def kilos(rng):
            for j, (k, p) in enumerate(pick_even([(k, p) for k in range(2, 10) for p in range(20, 91, 10)], N, rng, key=lambda c: c[0] * c[1], cap=1)):
                kilo_row(s, "04", k, p, KILO_GOODS[j % len(KILO_GOODS)], [10, 20, 50, 100, 500])
        B("04", kilos)

        def halves(rng):
            for j, p in enumerate(even(20, 80, N, rng, ok=lambda x: x % 4 == 0)):
                pic, noun, en = KILO_GOODS[(j + 2) % len(KILO_GOODS)]
                first, first_en = f"یک کیلو {noun} {fa(p)} {AFN} است.", f"One kilo of {en} is {p} afghani."
                if j % 3 == 0:
                    total = p // 2
                    say = tr(f"{first} نیم کیلو چند {AFN} می{Z}شود؟ {PAY_IT}", f"{first_en} How many afghani does half a kilo make? Pay for it.")
                    help_fa = tr(f"نیم {fa(p)}، {fa(p // 2)} است.", f"Half of {p} is {p // 2}.")
                elif j % 3 == 1:
                    total = p + p // 2
                    say = tr(f"{first} یک و نیم کیلو چند {AFN} می{Z}شود؟ {PAY_IT}", f"{first_en} How many afghani do one and a half kilos make? Pay for it.")
                    help_fa = tr(f"نیم {fa(p)}، {fa(p // 2)} است. {fa(p)} جمع {fa(p // 2)} مساوی {fa(total)}.",
                                 f"Half of {p} is {p // 2}. {p} plus {p // 2} equals {total}.")
                else:
                    total = 2 * p + p // 2
                    say = tr(f"{first} دو و نیم کیلو چند {AFN} می{Z}شود؟ {PAY_IT}", f"{first_en} How many afghani do two and a half kilos make? Pay for it.")
                    help_fa = tr(f"دو کیلو {fa(2 * p)} و نیم کیلو {fa(p // 2)} است. {fa(2 * p)} جمع {fa(p // 2)} مساوی {fa(total)}.",
                                 f"Two kilos are {2 * p} and half a kilo is {p // 2}. {2 * p} plus {p // 2} equals {total}.")
                market_row(s, "05", say, pic, total, [1, 2, 5, 10, 20, 50, 100], "pay", help_fa)
        B("05", halves)

        def change(rng):
            deals = [(k, p, given) for k in range(3, 10) for p in range(3, 10) for given in (50, 100) if 20 <= k * p < given]
            for j, (k, p, given) in enumerate(pick_even(deals, N, rng, key=lambda c: c[2] - c[0] * c[1], cap=1)):
                change_row("06", j, k, p, given, COUNTABLE[(j + 3) % len(COUNTABLE)], small)
        B("06", change)

        def two_kinds(rng):
            deals = [(k1, a, k2, b) for k1 in (2, 3, 4) for a in range(3, 10) for k2 in (2, 3, 5) for b in range(3, 10) if a != b and k1 * a + k2 * b <= 80]
            for j, (k1, a, k2, b) in enumerate(pick_even(deals, N, rng, key=lambda c: c[0] * c[1] + c[2] * c[3], cap=1)):
                (p1, n1), (p2, n2) = COUNTABLE[j % 4], COUNTABLE[4 + j % 4]
                x, y = k1 * a, k2 * b
                market_row(s, "07", tr(f"{fa(k1)} {n1} و {fa(k2)} {n2} می{Z}خری. هر {n1} {fa(a)} {AFN} و هر {n2} {fa(b)} {AFN} است. همه چند {AFN} می{Z}شود؟ {PAY_IT}",
                                       f"You buy {cnt(k1, n1)} and {cnt(k2, n2)}. Each {one(n1)} is {a} afghani and each {one(n2)} is {b} afghani. How many afghani is it altogether? Pay for it."),
                           p1, x + y, [1, 2, 5, 10, 20, 50], "pay",
                           tr(f"{fa(k1)} ضرب {fa(a)} مساوی {fa(x)}. {fa(k2)} ضرب {fa(b)} مساوی {fa(y)}. {fa(x)} جمع {fa(y)} مساوی {fa(x + y)}.",
                              f"{k1} times {a} equals {x}. {k2} times {b} equals {y}. {x} plus {y} equals {x + y}."))
        B("07", two_kinds)
    else:
        notes = [50, 100, 500, 1000]   # few kinds, so that the 1000 note is drawn large enough to read
        several = [("blanket", "کمپل"), ("hen", "مرغ"), ("flour_sack", "بوری آرد"), ("rice_sack", "بوری برنج"), ("goat", "بز"), ("carpet", "قالین")]

        def prices(rng):
            for j, p in enumerate(pick_even(range(650, 5001, 50), N, rng)):
                pic, noun = BIG[j % len(BIG)]
                market_row(s, "01", tr(f"{noun} {fa(p)} {AFN} است. {PAY_IT}", cap(f"{costs(noun, p)}. Pay for it.")), pic, p, notes, "pay", pay_help(p, notes))
        B("01", prices)

        def many_of(rng):
            for j, (k, p) in enumerate(pick_even([(k, p) for k in (2, 3, 4, 5) for p in range(250, 951, 50)], N, rng, key=lambda c: c[0] * c[1], cap=1)):
                buy_row(s, "02", k, p, several[j % len(several)], notes)
        B("02", many_of)

        def change(rng):
            deals = [(given, p) for given in (500, 1000) for p in range(given // 4, given - 20, 5) if p % 50]
            for j, (given, price) in enumerate(pick_even(deals, N, rng, key=lambda c: c[0] - c[1], cap=1)):
                pic, noun = BIG[(j + 4) % len(BIG)]
                left = given - price
                market_row(s, "03", tr(f"{noun} {fa(price)} {AFN} است. مشتری {fa(given)} {AFN} داد. چند {AFN} باقی می{Z}ماند؟ باقی را پس بده.",
                                       cap(f"{costs(noun, price)}. The customer gave {given} afghani. How many afghani are left over? Give the change back.")),
                           pic, left, [5, 10, 20, 50, 100, 500], "pay",
                           tr(f"{fa(given)} منفی {fa(price)} مساوی {fa(left)}.", f"{given} minus {price} equals {left}."))
        B("03", change)

        def kilos(rng):
            for j, (k, p) in enumerate(pick_even([(k, p) for k in range(4, 13) for p in range(35, 96, 5)], N, rng, key=lambda c: c[0] * c[1], cap=1)):
                kilo_row(s, "04", k, p, KILO_GOODS[(j + 3) % len(KILO_GOODS)], [5, 10, 20, 50, 100, 500])
        B("04", kilos)

        def shared(rng):
            halves = pick_even(range(300, 1801, 100), 9, rng)
            parts = pick_even([(k, sh) for k in (3, 4, 5) for sh in range(100, 400, 50)], 9, rng, key=lambda c: c[1], cap=2)
            for j in range(9):
                pic, noun = BIG[(j + 1) % len(BIG)]
                p = halves[j]
                market_row(s, "05", tr(f"{noun} {fa(p)} {AFN} است. امروز به نیم قیمت است. {PAY_IT}",
                                       cap(f"{costs(noun, p)}. Today it is at half price. Pay for it.")),
                           pic, p // 2, notes, "pay", tr(f"نیم {fa(p)}، {fa(p // 2)} است.", f"Half of {p} is {p // 2}."))
                pic, noun = BIG[(j + 3) % len(BIG)]
                k, sh = parts[j]
                p = sh * k
                market_row(s, "05", tr(f"{noun} {fa(p)} {AFN} است. {fa(k)} نفر پول آن را برابر تقسیم می{Z}کنند. حصه یک نفر را بده.",
                                       cap(f"{costs(noun, p)}. {k} people share the cost equally. Pay one person's share.")),
                           pic, sh, notes, "pay", tr(f"{fa(p)} تقسیم {fa(k)} مساوی {fa(sh)}.", f"{p} divided by {k} equals {sh}."))
        B("05", shared)

        def big_change(rng):
            deals = [(k, p, 1000) for k in (2, 3, 4, 5, 6) for p in range(60, 301, 10) if 300 <= k * p < 1000]
            for j, (k, p, given) in enumerate(pick_even(deals, N, rng, key=lambda c: c[2] - c[0] * c[1], cap=1)):
                change_row("06", j, k, p, given, several[j % 4], [10, 20, 50, 100, 500])   # blankets, hens, sacks: things of this price
        B("06", big_change)
    return s


# ---------------------------------------------------------------------------
# Levels 4 and 5: Carpet Weaver (builder)
# ---------------------------------------------------------------------------

def sum_round(s, level, rnd, facts, n=16):
    """facts: (a, op, b) built from tiles; two wrong results lie among the tiles."""
    def gen(rng):
        for a, op, b in pick_even(facts, n, rng, key=lambda t: calc4(*t), cap=2):
            c = calc4(a, op, b)
            if op == "*":
                wrong = [c + a, a + b, c - b, c + 1, c + 10]
            else:
                wrong = [c + 1, c - 1, c + 2, a - b]
            wrong = uniq(x for x in wrong if x > 0 and x not in (a, b, c))[:2]
            sum_item(s, rnd, a, op, b, wrong)
    build(s, level, "weaver", rnd, gen)


def weaver45(level: int) -> Sheet:
    s = Sheet(BUILDER_COLS)

    def table_runs(tables, top=10):
        out = []
        for t in tables:
            out += [(t * i, t, c) for i in range(1, 6) for c in (6, 8) if i + c - 1 <= top + 2]
            out += [(t * i, -t, 6) for i in range(8, 11)]
        return out

    if level == 4:
        seq_round(s, 4, "01", table_runs((3, 4)), table=True, dari_every=4)
        seq_round(s, 4, "02", table_runs((6, 7)), table=True, dari_every=4)
        seq_round(s, 4, "03", table_runs((8, 9)), table=True, dari_every=4)
        sum_round(s, 4, "04", [(a, "*", b) for a in range(3, 10) for b in range(3, 10) if len({a, b, a * b}) == 3])
        sum_round(s, 4, "05", [(a * b, "/", b) for a in range(2, 11) for b in range(3, 10) if len({a, b, a * b}) == 3])
        sum_round(s, 4, "06", [(a, "*", b) for a in (2, 5, 10) for b in range(3, 10) if len({a, b, a * b}) == 3] +
                  [(a * b, "/", b) for a in range(3, 11) for b in (2, 5, 10) if len({a, b, a * b}) == 3])
        order_round(s, 4, "07", 10, 1000, sizes=(6, 6, 5), close=True)
    else:
        runs = [(a, 1000, c) for a in range(1000, 4001, 1000) for c in (6, 8) if a + 1000 * (c - 1) <= 10000]
        runs += [(a, 500, 6) for a in range(500, 5001, 500)] + [(a, 2000, 6) for a in (2000, 4000, 1000, 3000)]
        runs += [(a, -1000, 6) for a in range(7000, 10001, 1000)] + [(a, 1, 6) for a in (9997, 4998, 996, 19996)] + [(a, 250, 6) for a in (250, 1000, 2500)]
        runs += [(a, 10000, 6) for a in (10000, 20000, 5000)] + [(a, 100, 6) for a in (800, 1700, 4600, 9500)]
        seq_round(s, 5, "01", runs, dari_every=4)
        order_round(s, 5, "02", 100, 100000, sizes=(5, 6, 5), close=True)

        def fracs(pairs):
            return {fr(k, n): (fa_frac(k, n), f"{k}/{n}") for k, n in pairs}

        same = tr("وقتی مخرج" + Z + "ها یکی است، کسری بزرگتر است که صورت آن بزرگتر است.",
                  "When the denominators are the same, the fraction with the bigger numerator is bigger.")
        unit = tr("وقتی صورت" + Z + "ها یکی است، کسری بزرگتر است که مخرج آن کوچکتر است.",
                  "When the numerators are the same, the fraction with the smaller denominator is bigger.")

        def frac_order(rng):
            up_say = tr("این کسرها را از کوچک به بزرگ بچین.", "Arrange these fractions from small to big.")
            down_say = tr("این کسرها را از بزرگ به کوچک بچین.", "Arrange these fractions from big to small.")
            for i in range(16):
                size = 4 + i % 2
                if i % 2 == 0:
                    n = rng.choice([6, 7, 8, 9, 10, 12])
                    pairs, help_fa = [(k, n) for k in sorted(rng.sample(range(1, n), size))], same
                else:
                    k = 1 if i % 4 == 1 else 2 if i % 8 == 3 else 3
                    pairs, help_fa = [(k, n) for n in sorted(rng.sample([d for d in range(2, 13) if d > k and math.gcd(d, k) == 1], size if k == 1 else 4))], unit
                sp = fracs(pairs)
                up = i % 3 != 2
                order_things(s, "03", I_ORDER_FRAC, list(sp), up, sp, up_say if up else down_say, help_fa)
        build(s, 5, "weaver", "03", frac_order)

        def dec_order(rng):
            dec_help = tr("اول عدد پیش از نقطه را ببین، بعد رقم" + Z + "های بعد از نقطه را.", "First look at the number before the point, then at the digits after the point.")
            up_say = tr("این عددهای اعشاری را از کوچک به بزرگ بچین.", "Arrange these decimal numbers from small to big.")
            down_say = tr("این عددهای اعشاری را از بزرگ به کوچک بچین.", "Arrange these decimal numbers from big to small.")
            for i in range(16):
                if i % 2 == 0:
                    decs = [f"{x // 10}.{x % 10}" for x in rng.sample(range(1, 60), 5)]
                else:   # hundredths that are easy to mix up: 2.05, 2.50, 5.20
                    a, b = rng.sample(range(0, 6), 2)
                    c = rng.randint(1, 9)
                    pool = uniq([f"{a}.{b}{c}", f"{a}.{c}{b}", f"{b}.{a}{c}", f"{b}.{c}{a}", f"{a}.0{c}", f"{b}.0{c}", f"{c}.{a}{b}", f"{a}.{c}0"], key=Fraction)
                    pool = [d for d in pool if Fraction(d) > 0]
                    if len(pool) < 5:
                        raise Retry("too few decimals")
                    decs = rng.sample(pool, 5)
                sp = {"t:" + d: (fa_dec(d), d) for d in decs}
                up = i % 3 != 2
                order_things(s, "04", I_ORDER_DEC, list(sp), up, sp, up_say if up else down_say, dec_help)
        build(s, 5, "weaver", "04", dec_order)

        def frac_sums(rng):
            for a, b, n in pick_even([(a, b, n) for n in range(5, 13) for a in range(1, n) for b in range(1, n) if a != b and a + b < n], 16, rng,
                                     key=lambda c: Fraction(c[0] + c[1], c[2]), cap=1):
                frac_sum_item(s, "05", a, b, n)
        build(s, 5, "weaver", "05", frac_sums)
        sum_round(s, 5, "06", [(a, "*", b) for a in range(11, 31) for b in range(2, 10) if a % 10] + [(a * b, "/", b) for a in range(11, 31) for b in range(2, 10) if a % 10 and a * b <= 200])
    return s


# ---------------------------------------------------------------------------
# Levels 4 and 5: Share the Bread (sorter)
# ---------------------------------------------------------------------------

FRACTIONS["third"] += [("orange_third", "یک بر سه مالته"), ("pomegranate_third", "یک بر سه انار")]


def sorter45(level: int) -> Sheet:
    s = Sheet(SORTER_COLS)

    def B(rnd, gen, **kw):
        build(s, level, "sorter", rnd, gen, **kw)

    def sums_round(rnd, op, groups, intro):
        rows = [(a, b, res) for res, pairs in groups.items() for a, b in pairs]

        def gen(rng):
            for a, b, res in rng.sample(rows, len(rows)):
                assert calc4(a, op, b) == res
                row = s.add(round=rnd, intro_fa=intro, thing=f"t:{a}{SIGN[op]}{b}", say_fa=tr(f"{fa(a)} {OP_WORD[op]} {fa(b)}", f"{a} {OP_EN[op]} {b}"),
                            basket=W(res), basket_say_fa=tr(fa(res), str(res)))
                SORT2_META.append((row, "sum"))
        B(rnd, gen, small="" if len(rows) >= 16 else "these answers have only this many sums in the tables")

    def plain_round(rnd, intro, rows, kind):
        """rows: (thing, spoken Dari, English, basket thing, basket Dari, basket English)"""
        def gen(rng):
            for thing, say, en, basket, b_say, b_en in rng.sample(rows, len(rows)):
                row = s.add(round=rnd, intro_fa=intro, thing=thing, say_fa=tr(say, en), basket=basket, basket_say_fa=tr(b_say, b_en))
                SORT2_META.append((row, kind))
        B(rnd, gen)

    def both_ways(pairs):
        return uniq([p for a, b in pairs for p in ((a, b), (b, a))])

    if level == 4:
        # 01: the baskets are pictures (a written «یک بر سه» would be too small to read)
        pictures = {"whole": "shape_circle", "half": pie(1, 2), "third": pie(1, 3), "quarter": pie(1, 4)}
        rows = [(FRACTIONS[kind][i], kind, i) for kind in ("whole", "half", "third", "quarter") for i in range(len(FRACTIONS[kind])) if FRACTIONS[kind][i]]

        def pieces(rng):
            for (pic, name), kind, i in rng.sample(rows, len(rows)):
                basket = FRAC_BASKET[kind]
                noun = FRACTION_NOUNS[i]
                en = FRACTION_EN[kind].format(a=art(bare(noun)), x=bare(noun))
                row = s.add(round="01", intro_fa=I_FRACTION4, thing=pic, say_fa=tr(name, en), basket=pictures[kind], basket_say_fa=tr(basket[1], bare(basket[1])))
                SORT_META.append((row, "fraction", kind))
        B("01", pieces)
        sums_round("02", "*", {12: both_ways([(3, 4), (2, 6)]), 18: both_ways([(3, 6), (2, 9)]), 24: both_ways([(4, 6), (3, 8)]), 20: both_ways([(4, 5), (2, 10)])}, I_PRODUCT)
        sums_round("03", "*", {36: both_ways([(6, 6), (4, 9)]), 40: both_ways([(5, 8), (4, 10)]), 30: both_ways([(5, 6), (3, 10)]), 16: both_ways([(4, 4), (2, 8)])}, I_PRODUCT)
        sums_round("04", "/", {3: [(12, 4), (18, 6), (27, 9), (21, 7), (24, 8)], 4: [(12, 3), (20, 5), (32, 8), (28, 7), (36, 9)],
                               6: [(18, 3), (42, 7), (24, 4), (54, 9)], 5: [(15, 3), (30, 6), (40, 8), (35, 7)]}, I_QUOTIENT)
    else:
        # The baskets carry one large word (کمتر، نیم، بیشتر); what they are compared with is spoken.
        tr("کمتر", "less"), tr("بیشتر", "more")
        less, same, more = ("f:کمتر", "کمتر از نیم", "less than half"), ("f:نیم", "مساوی نیم", "equal to half"), ("f:بیشتر", "بیشتر از نیم", "more than half")
        rows = []
        for k, n in [(1, 3), (1, 4), (2, 5), (1, 5), (3, 8), (3, 7), (2, 4), (3, 6), (4, 8), (5, 10), (2, 3), (3, 4), (4, 5), (5, 8), (4, 7), (5, 6)]:
            b = less if Fraction(k, n) < Fraction(1, 2) else same if Fraction(k, n) == Fraction(1, 2) else more
            rows.append((fr(k, n), fa_frac(k, n), f"{k}/{n}") + b)
        plain_round("01", I_HALF_SORT, rows, "half")
        rows = []
        baskets = {Fraction(1, 2): (pie(1, 2), "نیم", "half"), Fraction(1, 3): (pie(1, 3), "یک بر سه", "1/3"), Fraction(1, 4): (pie(1, 4), "چارک", "quarter"),
                   Fraction(2, 3): (pie(2, 3), "دو بر سه", "2/3")}
        for k, n in [(2, 4), (3, 6), (4, 8), (5, 10), (6, 12), (2, 6), (3, 9), (4, 12), (5, 15), (2, 8), (3, 12), (4, 16), (5, 20), (4, 6), (6, 9), (8, 12)]:
            rows.append((fr(k, n), fa_frac(k, n), f"{k}/{n}") + baskets[Fraction(k, n)])
        plain_round("02", I_SAME_FRAC, rows, "same")
        rows = []
        for pul in (5, 10, 25, 50, 75, 90, 95, 99, 105, 110, 125, 150, 175, 250, 505, 1050):
            b = ("f:کمتر", "کمتر از یک " + AFN, "less than 1 afghani") if pul < 100 else ("f:بیشتر", "بیشتر از یک " + AFN, "more than 1 afghani")
            rows.append((money(pul), money_fa(pul), money_en(pul)) + b)
        plain_round("03", I_AFGHANI, rows, "afghani")
        rows = []
        for n in (4999, 5001, 4500, 5050, 999, 10000, 4950, 50000, 500, 5500, 4099, 9000, 4909, 5005, 3500, 15000):
            b = ("f:کمتر", "کمتر از پنج هزار", "less than 5000") if n < 5000 else ("f:بیشتر", "بیشتر از پنج هزار", "more than 5000")
            rows.append((W(n), fa(n), str(n)) + b)
        plain_round("04", I_5000, rows, "5000")
    return s


# ---------------------------------------------------------------------------
# Levels 4 and 5: Shape Mason (listen_pick)
# ---------------------------------------------------------------------------

I_WEIGHT3 = tr("کیلو، گرام و لیتر را حساب کن.", "Work out the kilos, the grams and the litres.")
I_AREA_LIFE = tr("قصه را گوش کن: دور آن لازم است یا مساحت آن؟", "Listen to the story: is the way around it needed, or its area?")


def mason45(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    def B(rnd, gen, **kw):
        build(s, level, "mason", rnd, gen, **kw)

    def round_of(rnd, intro, make):
        """make(rng) gives (question, answer, typical mistakes, help[, show[, script]])."""
        def gen(rng):
            for item in make(rng):
                say, ans, prefer, help_fa = item[:4]
                numq(s, rnd, intro, say, ans, prefer, help_fa, rng, 100000, show=item[4] if len(item) > 4 else "", script=item[5] if len(item) > 5 else "W")
        B(rnd, gen)

    def side_help(a, b):
        return tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}. دو طول و دو عرض است: دو ضرب {fa(a + b)} مساوی {fa(2 * (a + b))}.",
                  f"{a} plus {b} equals {a + b}. There are two lengths and two widths: 2 times {a + b} equals {2 * (a + b)}.")

    rects = [(a, b) for a in range(3, 13) for b in range(2, 10) if a > b]

    if level == 4:
        def weights(rng):
            out = []
            for k in range(1, 11):
                out.append((tr(f"{fa(k)} کیلو چند گرام است؟", f"How many grams is {nn(k, 'kilo')}?"), k * 1000, [k * 100, k * 10, k * 1000 + 1000],
                            tr(f"هر کیلو هزار گرام است. {fa(k)} کیلو، {fa(k * 1000)} گرام می{Z}شود.", f"Each kilo is 1000 grams. {nn(k, 'kilo')} makes {k * 1000} grams.")))
            for g in rng.sample(range(2000, 10001, 1000), 5):
                out.append((tr(f"{fa(g)} گرام چند کیلو است؟", f"How many kilos is {g} grams?"), g // 1000, [g // 100, g // 1000 + 1, g // 1000 - 1],
                            tr(f"هر هزار گرام یک کیلو است. {fa(g)} گرام، {fa(g // 1000)} کیلو می{Z}شود.", f"Every 1000 grams is 1 kilo. {g} grams makes {nn(g // 1000, 'kilo')}.")))
            out.append((tr("نیم کیلو چند گرام است؟", "How many grams is half a kilo?"), 1000 // 2, [50, 250, 200],
                        tr("یک کیلو هزار گرام است. نیم آن پنج" + Z + "صد گرام است.", "One kilo is 1000 grams. Half of it is 500 grams.")))
            out.append((tr("یک و نیم کیلو چند گرام است؟", "How many grams is one and a half kilos?"), 1000 + 500, [150, 1050, 2500],
                        tr("یک کیلو هزار گرام و نیم کیلو پنج" + Z + "صد گرام است. هزار جمع پنج" + Z + "صد مساوی یک هزار و پنج" + Z + "صد.",
                           "One kilo is 1000 grams and half a kilo is 500 grams. 1000 plus 500 equals 1500.")))
            out.append((tr("دو و نیم کیلو چند گرام است؟", "How many grams is two and a half kilos?"), 2000 + 500, [250, 2050, 3500],
                        tr("دو کیلو دو هزار گرام و نیم کیلو پنج" + Z + "صد گرام است. دو هزار جمع پنج" + Z + "صد مساوی دو هزار و پنج" + Z + "صد.",
                           "Two kilos are 2000 grams and half a kilo is 500 grams. 2000 plus 500 equals 2500.")))
            return out
        round_of("01", I_WEIGHT, weights)

        def weight_stories(rng):
            out = []
            for a, b in pick_even([(a, b) for a in range(20, 61) for b in range(12, 40) if a > b], 5, rng, key=sum, cap=1):
                out.append((tr(f"یک بوری آرد {fa(a)} کیلو است و یک بوری برنج {fa(b)} کیلو. هر دو با هم چند کیلو می{Z}شود؟",
                               f"A sack of flour is {a} kilos and a sack of rice is {b} kilos. How many kilos do both make together?"),
                            a + b, [a - b, a + b + 10, a + b - 10], tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}.")))
            for k, m in pick_even([(k, m) for k in range(3, 10) for m in range(3, 10)], 5, rng, key=lambda c: c[0] * c[1], cap=1):
                out.append((tr(f"هر تربوز {fa(m)} کیلو است. {fa(k)} تربوز چند کیلو می{Z}شود؟", f"Each watermelon is {m} kilos. How many kilos do {k} watermelons make?"),
                            k * m, [k + m, (k + 1) * m, k * m - 1], tr(f"{fa(k)} ضرب {fa(m)} مساوی {fa(k * m)}.", f"{k} times {m} equals {k * m}.")))
            for n, k in pick_even([(k * c, k) for k in range(3, 10) for c in range(3, 11)], 4, rng, key=lambda c: c[0] // c[1], cap=1):
                out.append((tr(f"{fa(n)} کیلو برنج را بین {fa(k)} خانواده برابر تقسیم می{Z}کنیم. به هر خانواده چند کیلو می{Z}رسد؟",
                               f"We share {n} kilos of rice equally among {k} families. How many kilos does each family get?"),
                            n // k, [n // k + 1, n - k, k], tr(f"{fa(n)} تقسیم {fa(k)} مساوی {fa(n // k)}.", f"{n} divided by {k} equals {n // k}.")))
            for a, b in pick_even([(a, b) for a in range(30, 61) for b in range(12, 40) if a - b >= 8], 4, rng, key=lambda c: c[0] - c[1], cap=1):
                out.append((tr(f"در بوری {fa(a)} کیلو آرد بود. {fa(b)} کیلو مصرف شد. چند کیلو ماند؟", f"There were {a} kilos of flour in the sack. {b} kilos were used. How many kilos are left?"),
                            a - b, [a - b + 10, a + b, a - b - 1], tr(f"{fa(a)} منفی {fa(b)} مساوی {fa(a - b)}.", f"{a} minus {b} equals {a - b}.")))
            return out
        round_of("02", I_WEIGHT2, weight_stories)

        def litres(rng):
            out = []
            for a, b in pick_even([(a, b) for a in range(10, 41) for b in range(5, 30) if a > b], 5, rng, key=sum, cap=1):
                out.append((tr(f"در یک تانکی {fa(a)} لیتر آب است. {fa(b)} لیتر دیگر در آن می{Z}ریزیم. چند لیتر می{Z}شود؟",
                               f"There are {a} litres of water in a tank. We pour {b} litres more into it. How many litres does it make?"),
                            a + b, [a - b, a + b + 10, a + b - 1], tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}.")))
            for k, m in pick_even([(k, m) for k in range(3, 10) for m in (5, 6, 8, 10, 12)], 4, rng, key=lambda c: c[0] * c[1], cap=1):
                out.append((tr(f"هر سطل {fa(m)} لیتر آب می{Z}گیرد. {fa(k)} سطل چند لیتر می{Z}شود؟", f"Each bucket holds {m} litres of water. How many litres do {k} buckets make?"),
                            k * m, [k + m, (k + 1) * m, k * m - 1], tr(f"{fa(k)} ضرب {fa(m)} مساوی {fa(k * m)}.", f"{k} times {m} equals {k * m}.")))
            for n, m in pick_even([(m * c, m) for m in (2, 3, 4, 5) for c in range(3, 11)], 4, rng, key=lambda c: c[0] // c[1], cap=1):
                out.append((tr(f"{fa(n)} لیتر شیر را در ظرف{Z}های {fa(m)} لیتره می{Z}ریزیم. چند ظرف پُر می{Z}شود؟",
                               f"We pour {n} litres of milk into {m}-litre pots. How many pots are filled?"),
                            n // m, [n // m + 1, n - m, n // m - 1], tr(f"{fa(n)} تقسیم {fa(m)} مساوی {fa(n // m)}.", f"{n} divided by {m} equals {n // m}.")))
            for a, b in pick_even([(a, b) for a in range(30, 81, 5) for b in range(12, 50) if a - b >= 10], 3, rng, key=lambda c: c[0] - c[1], cap=1):
                out.append((tr(f"در تانکی {fa(a)} لیتر آب بود. {fa(b)} لیتر مصرف شد. چند لیتر ماند؟", f"There were {a} litres of water in the tank. {b} litres were used. How many litres are left?"),
                            a - b, [a - b + 10, a + b, a - b - 1], tr(f"{fa(a)} منفی {fa(b)} مساوی {fa(a - b)}.", f"{a} minus {b} equals {a - b}.")))
            for k in rng.sample(range(3, 13), 2):
                out.append((tr(f"هر ظرف نیم لیتر شیر می{Z}گیرد. {fa(k)} لیتر شیر چند ظرف را پُر می{Z}کند؟", f"Each pot holds half a litre of milk. How many pots do {nn(k, 'litre')} of milk fill?"),
                            2 * k, [k, k // 2 if k > 3 else k + 3, 2 * k + 2], tr(f"هر لیتر دو ظرف را پُر می{Z}کند. {fa(k)} ضرب دو مساوی {fa(2 * k)}.", f"Each litre fills 2 pots. {k} times 2 equals {2 * k}.")))
            return out
        round_of("03", I_LITRE, litres)

        def perimeters(rng):
            out = []
            for a in pick_even(range(2, 16), 7, rng):
                out.append((tr(f"هر ضلع یک مربع {fa(a)} {M} است. محیط آن چند {M} است؟", f"Each side of a square is {nn(a, 'metre')}. How many metres is its perimeter?"),
                            4 * a, [2 * a, a * a if a != 4 else 12, 3 * a], tr(f"مربع چهار ضلع برابر دارد. چهار ضرب {fa(a)} مساوی {fa(4 * a)}.", f"A square has 4 equal sides. 4 times {a} equals {4 * a}."), "shape_square"))
            for a, b in pick_even(rects, 7, rng, key=sum, cap=1):
                out.append((tr(f"طول یک مستطیل {fa(a)} {M} و عرض آن {fa(b)} {M} است. محیط آن چند {M} است؟",
                               f"The length of a rectangle is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many metres is its perimeter?"),
                            2 * (a + b), [a + b, a * b, 2 * a + b], side_help(a, b), "shape_rectangle"))
            for a in pick_even(range(4, 31), 4, rng):
                out.append((tr(f"هر سه ضلع یک مثلث {fa(a)} {CM} است. محیط آن چند {CM} است؟", f"All three sides of a triangle are {a} centimetres. How many centimetres is its perimeter?"),
                            3 * a, [2 * a, 4 * a, a + 3], tr(f"سه ضرب {fa(a)} مساوی {fa(3 * a)}.", f"3 times {a} equals {3 * a}."), "shape_triangle"))
            return out
        round_of("04", I_PERIMETER, perimeters)

        def perimeter_stories(rng):
            out = []
            for p in pick_even(range(12, 61, 4), 5, rng):
                out.append((tr(f"دور یک حویلی مربع {fa(p)} {M} است. هر ضلع آن چند {M} است؟", f"The way around a square yard is {p} metres. How many metres is each side?"),
                            p // 4, [p // 2, p - 4, p // 4 + 1], tr(f"مربع چهار ضلع برابر دارد. {fa(p)} تقسیم چهار مساوی {fa(p // 4)}.", f"A square has 4 equal sides. {p} divided by 4 equals {p // 4}."), "shape_square"))
            places = [("باغچه", "garden"), ("قالین", "carpet"), ("صنف", "classroom")]
            for i, (a, b) in enumerate(pick_even(rects, 6, rng, key=sum, cap=1)):
                noun, en = places[i % 3]
                out.append((tr(f"طول یک {noun} {fa(a)} {M} و عرض آن {fa(b)} {M} است. دور آن چند {M} است؟",
                               f"The length of a {en} is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many metres is the way around it?"),
                            2 * (a + b), [a + b, a * b, 2 * a + b], side_help(a, b), "shape_rectangle"))
            for a in pick_even(range(5, 16), 3, rng):
                p = 3 * a
                out.append((tr(f"محیط یک مثلث {fa(p)} {CM} است و هر سه ضلع آن برابر است. هر ضلع چند {CM} است؟",
                               f"The perimeter of a triangle is {p} centimetres and all three sides are equal. How many centimetres is each side?"),
                            a, [p - 3, a - 1, a + 1], tr(f"{fa(p)} تقسیم سه مساوی {fa(a)}.", f"{p} divided by 3 equals {a}."), "shape_triangle"))
            for a, b, c in rng.sample([(3, 4, 5), (6, 8, 10), (5, 12, 13), (7, 8, 9), (4, 6, 7), (9, 12, 15), (5, 5, 8)], 4):
                out.append((tr(f"ضلع{Z}های یک مثلث {fa(a)}، {fa(b)} و {fa(c)} {CM} است. محیط آن چند {CM} است؟",
                               f"The sides of a triangle are {a}, {b} and {c} centimetres. How many centimetres is its perimeter?"),
                            a + b + c, [a + b, a + b + c + 1, a + b + c - 2], tr(f"{fa(a)} جمع {fa(b)} جمع {fa(c)} مساوی {fa(a + b + c)}.", f"{a} plus {b} plus {c} equals {a + b + c}."),
                            "shape_triangle"))
            return out
        round_of("05", I_PERIMETER2, perimeter_stories)

        def mixed(rng):
            out = []
            for k, g in pick_even([(k, g) for k in range(1, 10) for g in (100, 200, 250, 300, 400, 500, 600, 750, 800)], 8, rng, key=lambda c: c[0] * 1000 + c[1], cap=1):
                out.append((tr(f"{fa(k)} کیلو و {fa(g)} گرام، چند گرام می{Z}شود؟", f"{nn(k, 'kilo')} and {g} grams make how many grams?"), k * 1000 + g, [k * 100 + g, k + g, k * 1000 + g * 10],
                            tr(f"{fa(k)} کیلو، {fa(k * 1000)} گرام است. {fa(k * 1000)} جمع {fa(g)} مساوی {fa(k * 1000 + g)}.", f"{nn(k, 'kilo')} is {k * 1000} grams. {k * 1000} plus {g} equals {k * 1000 + g}.")))
            for g in pick_even(range(1100, 2000, 50), 5, rng):
                out.append((tr(f"{fa(g)} گرام، یک کیلو و چند گرام است؟", f"{g} grams is 1 kilo and how many grams?"), g - 1000, [g, (g - 1000) // 10, g - 1000 + 100],
                            tr(f"یک کیلو هزار گرام است. {fa(g)} منفی هزار مساوی {fa(g - 1000)}.", f"One kilo is 1000 grams. {g} minus 1000 equals {g - 1000}.")))
            for k in pick_even(range(4, 21, 2), 5, rng):
                out.append((tr(f"هر بوتل نیم لیتر آب دارد. {fa(k)} بوتل چند لیتر آب دارد؟", f"Each bottle holds half a litre of water. How many litres of water do {k} bottles hold?"),
                            k // 2, [k, 2 * k, k // 2 + 1], tr(f"دو بوتل یک لیتر می{Z}شود. نیم {fa(k)}، {fa(k // 2)} است.", f"Two bottles make 1 litre. Half of {k} is {k // 2}.")))
            return out
        round_of("06", I_WEIGHT3, mixed)
    else:
        def squares(rng):
            # the picture lays the squares out in full rows only for these numbers
            out = []
            for cols, rows in [(2, 1), (3, 1), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4), (5, 4)]:
                n = cols * rows
                for script in "WD":
                    out.append(([tr(f"هر مربع یک {SQM} است. مساحت این فرش چند {SQM} است؟", "Each square is 1 square metre. How many square metres is the area of this floor?"),
                                 tr(f"مربع{Z}ها را بشمار. هر مربع یک {SQM} است. مساحت چند {SQM} می{Z}شود؟", "Count the squares. Each square is 1 square metre. How many square metres is the area?")][script == "D"],
                                n, [2 * (cols + rows), n + 1, n - 1, cols + rows],
                                tr(f"{fa(rows)} قطار است و در هر قطار {fa(cols)} مربع. {fa(rows)} ضرب {fa(cols)} مساوی {fa(n)}.",
                                   f"There {'is' if rows == 1 else 'are'} {nn(rows, 'row')} with {nn(cols, 'square')} in each. {rows} times {cols} equals {n}."),
                                f"p:shape_square*{n}", script))
            return out
        round_of("01", I_AREA_COUNT, squares)
        places = [("اتاق", "room"), ("قالین", "carpet"), ("حویلی", "yard"), ("صنف", "classroom"), ("باغچه", "garden"), ("زمین", "field"), ("میدان", "playground")]
        big_rects = rects + [(a, b) for a in (15, 20, 25, 30, 40) for b in (10, 12, 20) if a > b]

        def areas(rng):
            out = []
            for i, (a, b) in enumerate(pick_even(big_rects, N, rng, key=lambda c: c[0] * c[1], cap=1)):
                noun, en = places[i % len(places)] if a <= 12 else places[2 + i % 5]
                out.append((tr(f"طول یک {noun} {fa(a)} {M} و عرض آن {fa(b)} {M} است. مساحت آن چند {SQM} است؟",
                               f"The length of a {en} is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many square metres is its area?"),
                            a * b, [2 * (a + b), a + b, a * (b + 1)], tr(f"مساحت، طول ضرب عرض است. {fa(a)} ضرب {fa(b)} مساوی {fa(a * b)}.", f"The area is length times width. {a} times {b} equals {a * b}."),
                            "shape_rectangle"))
            return out
        round_of("02", I_AREA, areas)

        def sides(rng):
            out = []
            for a in pick_even(list(range(3, 13)) + [20, 30], 9, rng):
                out.append((tr(f"هر ضلع یک مربع {fa(a)} {M} است. مساحت آن چند {SQM} است؟", f"Each side of a square is {nn(a, 'metre')}. How many square metres is its area?"),
                            a * a, [4 * a if a != 4 else 8, 2 * a, a * a + a], tr(f"{fa(a)} ضرب {fa(a)} مساوی {fa(a * a)}.", f"{a} times {a} equals {a * a}."), "shape_square"))
            for a, b in pick_even([(a, b) for a, b in rects if a * b >= 20], 9, rng, key=lambda c: c[1], cap=2):
                area = a * b
                out.append((tr(f"مساحت یک مستطیل {fa(area)} {SQM} و طول آن {fa(a)} {M} است. عرض آن چند {M} است؟",
                               f"The area of a rectangle is {area} square metres and its length is {nn(a, 'metre')}. How many metres is its width?"),
                            b, [area - a, b + 1, b - 1], tr(f"{fa(area)} تقسیم {fa(a)} مساوی {fa(b)}.", f"{area} divided by {a} equals {b}."), "shape_rectangle"))
            return out
        round_of("03", I_AREA2, sides)

        def either(rng):
            out = []
            for a, b in pick_even([(a, b) for a, b in rects if a * b != 2 * (a + b)], 9, rng, key=lambda c: c[0] * c[1], cap=1):
                out.append((tr(f"طول یک مستطیل {fa(a)} {M} و عرض آن {fa(b)} {M} است. محیط آن چند {M} است؟",
                               f"The length of a rectangle is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many metres is its perimeter?"),
                            2 * (a + b), [a * b, a + b, 2 * a + b], side_help(a, b), "shape_rectangle"))
                out.append((tr(f"طول یک مستطیل {fa(a)} {M} و عرض آن {fa(b)} {M} است. مساحت آن چند {SQM} است؟",
                               f"The length of a rectangle is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many square metres is its area?"),
                            a * b, [2 * (a + b), a + b, a * (b + 1)], tr(f"مساحت، طول ضرب عرض است. {fa(a)} ضرب {fa(b)} مساوی {fa(a * b)}.", f"The area is length times width. {a} times {b} equals {a * b}."),
                            "shape_rectangle"))
            return out
        round_of("04", I_AREA_OR, either)

        def life(rng):
            out = []
            picks = pick_even([(a, b) for a, b in big_rects if a * b != 2 * (a + b)], N, rng, key=lambda c: c[0] * c[1], cap=1)
            for i, (a, b) in enumerate(picks):
                if i % 2 == 0:
                    out.append((tr(f"یک باغچه {fa(a)} {M} طول و {fa(b)} {M} عرض دارد. دور آن را سیم می{Z}کشیم. چند {M} سیم لازم است؟",
                                   f"A garden is {nn(a, 'metre')} long and {nn(b, 'metre')} wide. We put a wire around it. How many metres of wire are needed?"),
                                2 * (a + b), [a * b, a + b, 2 * a + b],
                                tr(f"سیم دور باغچه می{Z}رود، پس محیط لازم است. دو ضرب {fa(a + b)} مساوی {fa(2 * (a + b))}.",
                                   f"The wire goes around the garden, so the perimeter is needed. 2 times {a + b} equals {2 * (a + b)}."), "shape_rectangle"))
                else:
                    out.append((tr(f"یک اتاق {fa(a)} {M} طول و {fa(b)} {M} عرض دارد. برای هر {SQM} یک خشت فرش لازم است. چند خشت لازم است؟",
                                   f"A room is {nn(a, 'metre')} long and {nn(b, 'metre')} wide. One floor tile is needed for each square metre. How many tiles are needed?"),
                                a * b, [2 * (a + b), a + b, a * b + a],
                                tr(f"خشت{Z}ها روی فرش اتاق می{Z}روند، پس مساحت لازم است. {fa(a)} ضرب {fa(b)} مساوی {fa(a * b)}.",
                                   f"The tiles go on the floor of the room, so the area is needed. {a} times {b} equals {a * b}."), "shape_rectangle"))
            return out
        round_of("05", I_AREA_LIFE, life)
    return s

# ---------------------------------------------------------------------------
# Twin Tiles (pairs), all levels
# ---------------------------------------------------------------------------

I_PAIR_COUNT = tr("بشمار و با عدد آن جوره کن.", "Count and pair it with its number.")
I_PAIR_DIGITS = tr("هر عدد را با همان عدد به شکل دیگر جوره کن.", "Pair each number with the same number in its other form.")
I_PAIR_SAME_SUM = tr("دو حساب را که جواب آنها یکی است جوره کن.", "Pair the two sums that have the same answer.")
I_PAIR_HEAR = tr("عدد را گوش کن و با نوشته آن جوره کن.", "Listen to the number and pair it with its written form.")
I_PAIR_SUM = tr("هر حساب را با جواب آن جوره کن.", "Pair each sum with its answer.")
I_PAIR_COINS = tr("سکه" + Z + "ها را جمع کن و با جواب جوره کن.", "Add the coins and pair them with the answer.")
I_PAIR_PIECE = tr("نام را گوش کن و با تصویر آن جوره کن.", "Listen to the name and pair it with its picture.")
I_PAIR_MONEY = tr("پول را گوش کن و با عدد اعشاری آن جوره کن.", "Listen to the money and pair it with its decimal number.")


def card_value(card: str, say: str):
    """What a pair card stands for: the spoken text of a speaker card, the
    count of a counted picture, else the value of the number or sum."""
    if card == "snd":
        return say
    m = re.fullmatch(r"p:\w+\*(\d+)", card)
    if m:
        return Fraction(int(m.group(1)))
    if card[:2] in ("t:", "f:"):
        return text_sum("t:" + "".join(str(DARI_DIGITS.index(c)) if c in DARI_DIGITS else c for c in card[2:]))
    return val(card) if val(card) is not None else card


def pairs45(level: int) -> Sheet:
    if level == 6:
        return pairs6(level)
    s = Sheet(PAIRS_COLS)

    def B(rnd, gen, **kw):
        build(s, level, "pairs", rnd, gen, **kw)

    def pair(rnd, intro, a, b, say, kind):
        row = s.add(round=rnd, intro_fa=intro, a=a, b=b, say_fa=say)
        PAIR_META.append((row, kind))

    def digits(rnd, values, n=N):
        def gen(rng):
            for v in pick_even(values, n, rng, cap=1):
                pair(rnd, I_PAIR_DIGITS, W(v), D(v), tr(fa(v), str(v)), "same")
        B(rnd, gen)

    def heard(rnd, values, n=N):
        def gen(rng):
            for i, v in enumerate(pick_even(values, n, rng, cap=1)):
                pair(rnd, I_PAIR_HEAR, num(v, "WD"[i % 2]), "snd", tr(fa(v), str(v)), "numname")
        B(rnd, gen)

    def same_sums(rnd, cands, n=16):
        by_value: dict = {}
        for a, op, b in cands:
            by_value.setdefault(calc(a, op, b), []).append((a, op, b))
        values = [v for v in sorted(by_value) if len({tuple(sorted((a, b))) for a, _, b in by_value[v]}) >= 2]

        def gen(rng):
            for v in pick_even(values, n, rng, cap=1):
                group = rng.sample(by_value[v], len(by_value[v]))
                first = group[0]
                rest = [t for t in group[1:] if tuple(sorted((t[0], t[2]))) != tuple(sorted((first[0], first[2])))]
                second = rest[0]
                (d1, e1), (d2, e2) = say_sum(*first), say_sum(*second)
                pair(rnd, I_PAIR_SAME_SUM, sum_text(*first), sum_text(*second),
                     tr(f"{d1} مساوی {fa(v)}. {d2} هم مساوی {fa(v)}.", f"{e1} equals {v}. {e2} also equals {v}."), "samesum")
        B(rnd, gen)

    def sums(rnd, intro, cands, n=16):
        """Different sums with different answers."""
        def gen(rng):
            for a, op, b in pick_even(cands, n, rng, key=lambda t: calc4(*t), cap=1):
                d, e = say_sum(a, op, b)
                c = calc4(a, op, b)
                pair(rnd, intro, sum_text(a, op, b), W(c), tr(f"{d} مساوی {fa(c)}.", f"{e} equals {c}."), "sum")
        B(rnd, gen, small="" if n >= 16 else "the tables give only ten different answers")

    if level == 1:
        def counted(rng):
            objs = rng.sample(COUNT_OBJS, 12)
            for v in range(1, 13):
                pic, noun = objs[v - 1]
                pair("01", I_PAIR_COUNT, f"p:{pic}*{v}", num(v, "WD"[v % 2]), tr(f"{fa(v)} {noun}", cnt(v, noun)), "count")
        B("01", counted, small="a pair card can show at most twelve things to count")
        digits("02", range(0, 21))
        easy = [(a, "+", b) for a in range(0, 11) for b in range(0, 11) if 2 <= a + b <= 10 and (a, b) != (0, 0)]
        teen = [(a, "+", b) for a in range(10, 19) for b in range(1, 10) if a % 10 + b <= 9] + [(b, "+", a) for a in range(11, 19) for b in range(1, 9) if a % 10 + b <= 9]
        same_sums("03", easy + teen)
        heard("04", range(0, 21))
    elif level == 2:
        digits("01", range(21, 100))
        same_sums("02", [(a, "+", b) for a in range(1, 13) for b in range(1, 11) if 5 <= a + b <= 20])
        cross = [(a, "+", b) for a in range(2, 10) for b in range(2, 10) if a + b >= 11]
        subx = [(a, "-", b) for a in range(11, 19) for b in range(2, 10) if b > a % 10]
        sums("03", I_PAIR_SUM, cross + subx)

        def coins(rng):
            sets = [c for k in (2, 3) for c in itertools.combinations_with_replacement([1, 2, 5, 10, 20, 50], k)]
            sets = [tuple(sorted(c, reverse=True)) for c in sets if sum(c) not in (1, 2, 5, 10, 20, 50, 100)]
            for c in pick_even(sets, 16, rng, key=sum, cap=1):
                total = sum(c)
                pair("04", I_PAIR_COINS, "t:" + "+".join(map(str, c)), W(total),
                     tr(" جمع ".join(fa(x) for x in c) + f" مساوی {fa(total)}.", " plus ".join(map(str, c)) + f" equals {total}."), "sum")
        B("04", coins)
    elif level == 3:
        sums("01", I_PAIR_MUL, [(a, "*", b) for b in (2, 5, 10) for a in range(2, 11)] + [(b, "*", a) for b in (2, 5, 10) for a in range(2, 11)], n=N)
        same_sums("02", [(a, "+", b) for a in range(10, 100, 5) for b in range(10, 100, 10) if 30 <= a + b <= 120 and a != b])
        digits("03", range(101, 1000))
        a1 = [(a, "+", b) for a in range(15, 90) for b in range(2, 10) if a % 10 and a % 10 + b >= 10]
        s1 = [(a, "-", b) for a in range(21, 96) for b in range(2, 10) if a % 10 < b]
        sums("04", I_PAIR_SUM, a1 + s1, n=N)
    elif level == 4:
        sums("01", I_PAIR_MUL, [(a, "*", t) for t in (3, 4, 6) for a in range(2, 11)] + [(t, "*", a) for t in (3, 4, 6) for a in range(2, 11)])
        sums("02", I_PAIR_MUL, [(a, "*", t) for t in (7, 8, 9) for a in range(2, 11)] + [(t, "*", a) for t in (7, 8, 9) for a in range(2, 11)])
        sums("03", I_PAIR_DIV, [(t * c, "/", t) for t in (3, 4, 6, 7, 8, 9) for c in range(1, 11)], n=10)

        def pieces(rng):
            for (k, n), name, en in PIES4:
                pair("04", I_PAIR_PIE, pie(k, n), "snd", tr(name, en), "name")
            pair("04", I_PAIR_PIE, "shape_circle", "snd", tr("دایره پوره", "whole circle"), "name")
            for kind in ("half", "third", "quarter"):
                for i, entry in enumerate(FRACTIONS[kind]):
                    if entry and FRACTION_NOUNS[i] != "دایره":
                        noun = FRACTION_NOUNS[i]
                        pair("04", I_PAIR_PIECE, entry[0], "snd", tr(entry[1], FRACTION_EN[kind].format(a=art(bare(noun)), x=bare(noun))), "name")
        B("04", pieces)
    else:
        def equal(rng):
            base = [(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (1, 5), (2, 5), (3, 5), (4, 5), (1, 6), (5, 6), (1, 8), (3, 8), (5, 8), (7, 8), (1, 10), (3, 10), (7, 10)]
            for i, (k, n) in enumerate(base):
                m = 2 if i % 3 else 3
                pair("01", I_PAIR_SAME, fr(k, n), fr(k * m, n * m), tr(f"{fa_frac(k, n)} مساوی {fa_frac(k * m, n * m)}.", f"{k}/{n} equals {k * m}/{n * m}."), "same")
        B("01", equal)

        def circles(rng):
            for k, n in PIES5:
                pair("02", I_PAIR_FRAC, pie(k, n), fr(k, n), tr(fa_frac(k, n), f"{k}/{n}"), "same")
        B("02", circles, small="fifteen fraction circles are drawn")

        def decimals(rng):
            for d, (k, n) in [("0.5", (1, 2)), ("0.25", (1, 4)), ("0.75", (3, 4)), ("0.1", (1, 10)), ("0.2", (1, 5)), ("0.3", (3, 10)), ("0.4", (2, 5)), ("0.6", (3, 5)),
                              ("0.7", (7, 10)), ("0.8", (4, 5)), ("0.9", (9, 10)), ("0.05", (1, 20)), ("0.01", (1, 100)), ("0.15", (3, 20)), ("0.35", (7, 20)), ("0.45", (9, 20))]:
                pair("03", I_PAIR_DEC, "t:" + d, fr(k, n), tr(f"{fa_dec(d)} مساوی {fa_frac(k, n)}.", f"{d} equals {k}/{n}."), "same")
        B("03", decimals)

        def coins(rng):
            amounts = [a * 100 + p for a in range(0, 13) for p in (0, 5, 10, 25, 50, 75, 90) if a * 100 + p > 0 and p]
            for pul in pick_even(amounts, N, rng, cap=1):
                pair("04", I_PAIR_MONEY, money(pul), "snd", tr(money_fa(pul), money_en(pul)), "money")
        B("04", coins)
    return s


# ---------------------------------------------------------------------------
# Number Rain (catch), all levels
# ---------------------------------------------------------------------------

I_RAIN = tr("گوش کن و فقط عددهای درست را بگیر.", "Listen and catch only the right numbers.")
NEED = 4


def catch45(level: int) -> Sheet:
    if level == 6:
        return catch6(level)
    s = Sheet(CATCH_COLS)

    def rule(rnd, say, targets, others, help_fa, test):
        assert len(targets) >= 5 and len(others) >= 5 and not set(targets) & set(others), (say, targets, others)
        assert all(len(x) - 2 <= 4 for x in targets + others), "too wide for the round card"
        assert len(set(targets)) == len(targets) and len(set(others)) == len(others)
        row = s.add(round=rnd, intro_fa=I_RAIN, say_fa=say, targets="|".join(targets), others="|".join(others), need=NEED, help_fa=help_fa)
        CATCH_META.append((row, test))

    def numbers(rnd, rng, say, help_fa, test, lo, hi, script, edge=()):
        """Six numbers that fit the rule and six that do not, spread over
        lo..hi; `edge` are numbers that must be there (the ones next to the limit)."""
        yes = [x for x in range(lo, hi + 1) if test(x)]
        no = [x for x in range(lo, hi + 1) if not test(x)]
        if len(yes) < 6 or len(no) < 6:
            raise AssertionError((say, len(yes), len(no)))
        forced_yes, forced_no = [x for x in edge if x in yes], [x for x in edge if x in no]
        targets = uniq(forced_yes + pick_even(yes, 6, rng, cap=1))[:6]
        others = uniq(forced_no + pick_even(no, 6, rng, cap=1))[:6]
        rule(rnd, say, [num(x, script) for x in targets], [num(x, script) for x in others], help_fa, lambda v, test=test: test(int(v)))

    def bigger(k):
        return (tr(f"عددهای بزرگتر از {fa(k)} را بگیر.", f"Catch the numbers bigger than {k}."),
                tr(f"{fa(k + 1)} و عددهای بعد از آن از {fa(k)} بزرگتر هستند.", f"{k + 1} and the numbers after it are bigger than {k}."), lambda x, k=k: x > k, (k, k + 1))

    def smaller(k):
        return (tr(f"عددهای کوچکتر از {fa(k)} را بگیر.", f"Catch the numbers smaller than {k}."),
                tr(f"{fa(k - 1)} و عددهای پیش از آن از {fa(k)} کوچکتر هستند.", f"{k - 1} and the numbers before it are smaller than {k}."), lambda x, k=k: x < k, (k, k - 1))

    def between(a, b):
        return (tr(f"عددهای بین {fa(a)} و {fa(b)} را بگیر.", f"Catch the numbers between {a} and {b}."),
                tr(f"این عددها از {fa(a)} بزرگتر و از {fa(b)} کوچکتر هستند.", f"These numbers are bigger than {a} and smaller than {b}."), lambda x, a=a, b=b: a < x < b, (a, b))

    even_rule = (tr("عددهای جفت را بگیر.", "Catch the even numbers."),
                 tr("رقم آخر عدد جفت، صفر، دو، چهار، شش یا هشت است.", "The last digit of an even number is 0, 2, 4, 6 or 8."), lambda x: x % 2 == 0, ())
    odd_rule = (tr("عددهای طاق را بگیر.", "Catch the odd numbers."),
                tr("رقم آخر عدد طاق، یک، سه، پنج، هفت یا نه است.", "The last digit of an odd number is 1, 3, 5, 7 or 9."), lambda x: x % 2 == 1, ())

    def by(step):
        return (tr(f"عددهایی را بگیر که در {fa(step)} تا {fa(step)} تا شمردن می{Z}آیند.", f"Catch the numbers that come when you count in {step}s."),
                tr("، ".join(fa(step * i) for i in range(1, 5)) + " و همین طور پیش برو.", ", ".join(str(step * i) for i in range(1, 5)) + " and so on."),
                lambda x, step=step: x % step == 0 and x > 0, ())

    def tens_digit(t):
        return (tr(f"عددهایی را بگیر که {ONES[t]} ده دارند.", f"Catch the numbers that have {nn(t, 'ten')}."),
                tr(f"عددهای {fa(10 * t)} تا {fa(10 * t + 9)}، {ONES[t]} ده دارند.", f"The numbers {10 * t} to {10 * t + 9} have {nn(t, 'ten')}."), lambda x, t=t: x // 10 % 10 == t, (10 * t - 1, 10 * t + 10))

    def ones_digit(o):
        return (tr(f"عددهایی را بگیر که {ONES[o]} یک دارند.", f"Catch the numbers that have {nn(o, 'one')}."),
                tr(f"رقم آخر این عددها {ONES[o]} است.", f"The last digit of these numbers is {o}."), lambda x, o=o: x % 10 == o, ())

    def hundreds_digit(h):
        return (tr(f"عددهایی را بگیر که {ONES[h]} صد دارند.", f"Catch the numbers that have {nn(h, 'hundred')}."),
                tr(f"عددهای {fa(100 * h)} تا {fa(100 * h + 99)}، {ONES[h]} صد دارند.", f"The numbers {100 * h} to {100 * h + 99} have {nn(h, 'hundred')}."),
                lambda x, h=h: x // 100 == h, (100 * h - 1, 100 * h + 100))

    def table(t):
        return (tr(f"عددهای جدول ضرب {fa(t)} را بگیر.", f"Catch the numbers of the {t} times table."),
                tr(f"جدول ضرب {fa(t)}: " + "، ".join(fa(t * i) for i in range(1, 6)) + " و همین طور پیش برو.",
                   f"The {t} times table: " + ", ".join(str(t * i) for i in range(1, 6)) + " and so on."), lambda x, t=t: x % t == 0, ())

    def both(a, b):
        m = a * b // math.gcd(a, b)
        return (tr(f"عددهایی را بگیر که هم در جدول ضرب {fa(a)} و هم در جدول ضرب {fa(b)} هستند.", f"Catch the numbers that are in both the {a} times table and the {b} times table."),
                tr("، ".join(fa(m * i) for i in range(1, 4)) + " و همین طور پیش برو.", ", ".join(str(m * i) for i in range(1, 4)) + " and so on."),
                lambda x, a=a, b=b: x % a == 0 and x % b == 0, (a * b // math.gcd(a, b) + a, a * b // math.gcd(a, b) + b))

    def number_round(rnd, plans, n=16):
        """plans: (rule, lo, hi). Each rule once in Western and once in Dari digits."""
        def gen(rng):
            cands = [(i, sc) for i in range(len(plans)) for sc in "WD"]
            for i, sc in rng.sample(cands, n):
                (say, help_fa, test, edge), lo, hi = plans[i]
                numbers(rnd, rng, say, help_fa, test, lo, hi, sc, edge)
        build(s, level, "catch", rnd, gen)

    if level == 1:
        number_round("01", [(bigger(k), 0, 15) for k in (5, 6, 7, 8, 9)] + [(smaller(k), 0, 15) for k in (6, 8, 10)])
        number_round("02", [(bigger(k), 0, 20) for k in (8, 11, 14)] + [(smaller(k), 0, 20) for k in (9, 13, 15)] + [(between(a, b), 0, 20) for a, b in ((4, 12), (9, 17))])
    elif level == 2:
        number_round("01", [(even_rule, 1, 60), (odd_rule, 1, 60)] + [(bigger(k), 10, 99) for k in (25, 50, 60)] + [(smaller(k), 10, 99) for k in (30, 45, 75)])
        number_round("02", [(by(10), 1, 100), (by(5), 1, 100)] + [(tens_digit(t), 10, 99) for t in (3, 5, 7)] + [(ones_digit(o), 10, 99) for o in (4, 8, 2)])
        number_round("03", [(between(a, b), 1, 99) for a, b in ((20, 40), (45, 60), (10, 30), (70, 90))] + [(bigger(k), 1, 99) for k in (39, 80)] + [(smaller(k), 1, 99) for k in (20, 61)])
    elif level == 3:
        number_round("01", [(table(2), 2, 30), (table(5), 5, 100), (table(10), 10, 200), (even_rule, 101, 999), (odd_rule, 101, 999), (by(100), 50, 999),
                            (bigger(500), 100, 999), (smaller(500), 100, 999)])
        number_round("02", [(hundreds_digit(h), 100, 999) for h in (3, 6, 8)] + [(bigger(k), 100, 999) for k in (250, 750)] + [(smaller(k), 100, 999) for k in (300, 900)] +
                     [(between(400, 600), 100, 999)])
        number_round("03", [(tens_digit(t), 100, 999) for t in (5, 2, 9)] + [(ones_digit(o), 100, 999) for o in (7, 3, 0)] + [(between(a, b), 100, 999) for a, b in ((150, 350), (690, 810))])
    elif level == 4:
        number_round("01", [(table(t), t + 1, 10 * t) for t in (3, 4, 6, 2, 5, 10)] + [(even_rule, 11, 99), (odd_rule, 11, 99)])
        number_round("02", [(table(t), t + 1, 10 * t) for t in (7, 8, 9)] + [(bigger(k), 10, 100) for k in (48, 72)] + [(smaller(k), 10, 100) for k in (36, 63)] + [(between(24, 56), 10, 100)])
        square = (tr("عددهایی را بگیر که از ضرب یک عدد در خودش ساخته می" + Z + "شوند.", "Catch the numbers that are made by multiplying a number by itself."),
                  tr("دو ضرب دو مساوی چهار، سه ضرب سه مساوی نه، چهار ضرب چهار مساوی شانزده و همین طور پیش برو.", "2 times 2 equals 4, 3 times 3 equals 9, 4 times 4 equals 16 and so on."),
                  lambda x: int(x ** 0.5 + 0.5) ** 2 == x, ())
        number_round("03", [(both(a, b), 4, 120) for a, b in ((2, 3), (2, 5), (3, 4), (3, 5), (2, 7), (4, 6), (4, 5))] + [(square, 2, 100)])
    else:
        hundred = (tr("عددهایی را بگیر که بر صد تقسیم می" + Z + "شوند.", "Catch the numbers that can be divided by 100."),
                   tr("عددی بر صد تقسیم می" + Z + "شود که دو رقم آخر آن صفر است.", "A number can be divided by 100 when its last two digits are 0."), lambda x: x % 100 == 0, (150, 250, 350, 510, 990))
        ten = (tr("عددهایی را بگیر که بر ده تقسیم می" + Z + "شوند.", "Catch the numbers that can be divided by 10."),
               tr("عددی بر ده تقسیم می" + Z + "شود که رقم آخر آن صفر است.", "A number can be divided by 10 when its last digit is 0."), lambda x: x % 10 == 0, (125, 705))
        five = (tr("عددهایی را بگیر که بر پنج تقسیم می" + Z + "شوند.", "Catch the numbers that can be divided by 5."),
                tr("عددی بر پنج تقسیم می" + Z + "شود که رقم آخر آن صفر یا پنج است.", "A number can be divided by 5 when its last digit is 0 or 5."), lambda x: x % 5 == 0, ())
        number_round("01", [(ten, 50, 999), (hundred, 100, 999), (five, 50, 999), (table(12), 13, 120), (table(25), 26, 400), (table(15), 16, 150),
                            (bigger(500), 50, 999), (smaller(250), 50, 999)])

        def fracs(pairs):
            return [fr(k, n) for k, n in pairs]

        half, quarter, third = Fraction(1, 2), Fraction(1, 4), Fraction(1, 3)
        proper = [(k, n) for n in range(2, 13) for k in range(1, n)]

        def frac_rule(rng, say, help_fa, test, also=()):
            yes = [p for p in proper if test(Fraction(*p))] + [p for p in also if test(Fraction(*p))]
            no = [p for p in proper if not test(Fraction(*p)) and p[1] <= 8]
            yes = [p for p in yes if len(f"{p[0]}/{p[1]}") <= 4]
            rule("02", say, fracs(rng.sample(yes, min(6, len(yes)))), fracs(rng.sample(no, 6)), help_fa, test)

        def dec_rule(rng, say, help_fa, test):
            pool = ["0.5", "0.25", "0.75", "0.9", "0.05", "0.1", "0.4", "0.45", "0.6", "0.99", "1.5", "1.25", "2.5", "1.05", "3.75", "1.1", "1.01", "9.9", "1.9", "2.05", "2.25", "0.3", "1.75", "2.75", "3.5", "0.2", "0.8"]
            yes, no = [d for d in pool if test(Fraction(d))], [d for d in pool if not test(Fraction(d))]
            rule("02", say, ["t:" + d for d in rng.sample(yes, 6)], ["t:" + d for d in rng.sample(no, 6)], help_fa, test)

        def fractions(rng):
            frac_rule(rng, tr("کسرهای مساوی نیم را بگیر.", "Catch the fractions equal to half."),
                      tr("کسری مساوی نیم است که صورت آن نیم مخرج باشد.", "A fraction is equal to half when its numerator is half of its denominator."), lambda v: v == half)
            frac_rule(rng, tr("کسرهای بزرگتر از نیم را بگیر.", "Catch the fractions bigger than half."),
                      tr("کسری از نیم بزرگتر است که صورت آن از نیم مخرج بیشتر باشد.", "A fraction is bigger than half when its numerator is more than half of its denominator."), lambda v: v > half)
            frac_rule(rng, tr("کسرهای کوچکتر از نیم را بگیر.", "Catch the fractions smaller than half."),
                      tr("کسری از نیم کوچکتر است که صورت آن از نیم مخرج کمتر باشد.", "A fraction is smaller than half when its numerator is less than half of its denominator."), lambda v: v < half)
            frac_rule(rng, tr("کسرهای مساوی یک پوره را بگیر.", "Catch the fractions equal to one whole."),
                      tr("وقتی صورت و مخرج یکی است، کسر یک پوره است.", "When the numerator and the denominator are the same, the fraction is one whole."), lambda v: v == 1,
                      also=[(n, n) for n in (2, 3, 4, 5, 6, 8, 10)])
            frac_rule(rng, tr("کسرهای مساوی چارک را بگیر.", "Catch the fractions equal to a quarter."),
                      tr("چارک یعنی یک بر چهار. دو بر هشت و سه بر دوازده هم مساوی چارک است.", "A quarter means 1/4. 2/8 and 3/12 are also equal to a quarter."), lambda v: v == quarter,
                      also=[(4, 16), (5, 20), (6, 24)])
            frac_rule(rng, tr("کسرهای مساوی یک بر سه را بگیر.", "Catch the fractions equal to 1/3."),
                      tr("دو بر شش، سه بر نه و چهار بر دوازده مساوی یک بر سه است.", "2/6, 3/9 and 4/12 are equal to 1/3."), lambda v: v == third, also=[(5, 15), (6, 18)])
            frac_rule(rng, tr("کسرهایی را بگیر که صورت آنها یک است.", "Catch the fractions whose numerator is 1."),
                      tr("صورت، عدد بالای کسر است.", "The numerator is the top number of the fraction."), lambda v: v.numerator == 1 and v != 1)
            frac_rule(rng, tr("کسرهای کوچکتر از چارک را بگیر.", "Catch the fractions smaller than a quarter."),
                      tr("یک بر پنج، یک بر شش و یک بر هشت از چارک کوچکتر هستند.", "1/5, 1/6 and 1/8 are smaller than a quarter."), lambda v: v < quarter)
            before = tr("عدد پیش از نقطه را ببین.", "Look at the number before the point.")
            after = tr("رقم اول بعد از نقطه را ببین.", "Look at the first digit after the point.")
            dec_rule(rng, tr("عددهای اعشاری بزرگتر از یک را بگیر.", "Catch the decimal numbers bigger than 1."), before, lambda v: v > 1)
            dec_rule(rng, tr("عددهای اعشاری کوچکتر از یک را بگیر.", "Catch the decimal numbers smaller than 1."), before, lambda v: v < 1)
            dec_rule(rng, tr("عددهای اعشاری بزرگتر از دو را بگیر.", "Catch the decimal numbers bigger than 2."), before, lambda v: v > 2)
            dec_rule(rng, tr("عددهای اعشاری کوچکتر از دو را بگیر.", "Catch the decimal numbers smaller than 2."), before, lambda v: v < 2)
            dec_rule(rng, tr("عددهای اعشاری بین یک و دو را بگیر.", "Catch the decimal numbers between 1 and 2."), before, lambda v: 1 < v < 2)
            dec_rule(rng, tr("عددهای اعشاری کوچکتر از صفر اعشاریه پنج را بگیر.", "Catch the decimal numbers smaller than 0.5."), after, lambda v: v < half)
            dec_rule(rng, tr("عددهای اعشاری بزرگتر از صفر اعشاریه پنج را بگیر.", "Catch the decimal numbers bigger than 0.5."), after, lambda v: v > half)
            dec_rule(rng, tr("عددهای اعشاری بزرگتر از یک اعشاریه پنج را بگیر.", "Catch the decimal numbers bigger than 1.5."), after, lambda v: v > Fraction(3, 2))
        build(s, 5, "catch", "02", fractions)
    return s


# ---------------------------------------------------------------------------
# Level 4: Days and Months (listen_pick; the choices are read aloud)
# ---------------------------------------------------------------------------

I_DAY_COUNT = tr("روزها را پیش و پس بشمار.", "Count the days forwards and backwards.")


def calendar4(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    def word(pair):
        return "f:" + tr(pair[0], pair[1])

    def ask(rnd, intro, say, right, wrong, help_fa):
        row = lp(s, rnd, intro, say, word(right), [word(w) for w in wrong], help_fa=help_fa)
        CAL_META.append((row, right[0]))

    def day(i):
        return DAYS[i % 7]

    def month(i):
        return MONTHS[i % 12]

    week = tr("هفته با شنبه شروع می" + Z + "شود و با جمعه تمام می" + Z + "شود.", "The week starts with Saturday and ends with Friday.")
    year = tr("سال با ماه حمل شروع می" + Z + "شود و با ماه حوت تمام می" + Z + "شود.", "The year starts with the month of Hamal and ends with the month of Hut.")

    def days(rng):
        cands = [(kind, i) for kind in ("after", "before", "tomorrow", "yesterday") for i in range(7)] + [("first", 0), ("last", 6)]
        ans = {"after": 1, "tomorrow": 1, "before": -1, "yesterday": -1, "first": 0, "last": 0}
        for kind, i in pick_even(cands, N, rng, key=lambda c: (c[1] + ans[c[0]]) % 7):
            (d, en), (n, n_en) = day(i), day(i + ans[kind])
            if kind == "after":
                ask("01", I_DAYS, tr(f"بعد از {d} کدام روز می{Z}آید؟", f"Which day comes after {en}?"), day(i + 1), [day(i), day(i - 1), day(i + 2)],
                    tr(f"بعد از {d}، {n} می{Z}آید.", f"After {en} comes {n_en}."))
            elif kind == "before":
                ask("01", I_DAYS, tr(f"پیش از {d} کدام روز است؟", f"Which day is before {en}?"), day(i - 1), [day(i), day(i + 1), day(i - 2)],
                    tr(f"پیش از {d}، {n} است.", f"Before {en} is {n_en}."))
            elif kind == "tomorrow":
                ask("01", I_DAYS, tr(f"امروز {d} است. فردا کدام روز است؟", f"Today is {en}. Which day is tomorrow?"), day(i + 1), [day(i), day(i - 1), day(i + 2)],
                    tr(f"فردا {n} است.", f"Tomorrow is {n_en}."))
            elif kind == "yesterday":
                ask("01", I_DAYS, tr(f"امروز {d} است. دیروز کدام روز بود؟", f"Today is {en}. Which day was yesterday?"), day(i - 1), [day(i), day(i + 1), day(i - 2)],
                    tr(f"دیروز {n} بود.", f"Yesterday was {n_en}."))
            elif kind == "first":
                ask("01", I_DAYS, tr("هفته با کدام روز شروع می" + Z + "شود؟", "With which day does the week start?"), day(0), [day(1), day(2), day(6)], week)
            else:
                ask("01", I_DAYS, tr("روز آخر هفته کدام است؟", "Which is the last day of the week?"), day(6), [day(0), day(5), day(4)], week)
    build(s, 4, "calendar", "01", days, few=7)

    def months(rng):
        cands = [("after", i) for i in range(12)] + [("before", i) for i in range(12)] + [("first", 0), ("last", 11)]
        ans = {"after": 1, "before": -1, "first": 0, "last": 0}
        for kind, i in pick_even(cands, 12, rng, key=lambda c: (c[1] + ans[c[0]]) % 12, cap=1):
            (m, en), (n, n_en) = month(i), month(i + ans[kind])
            if kind == "after":
                ask("02", I_MONTHS, tr(f"بعد از ماه {m} کدام ماه می{Z}آید؟", f"Which month comes after {en}?"), month(i + 1), [month(i), month(i - 1), month(i + 2)],
                    tr(f"بعد از {m}، ماه {n} می{Z}آید.", f"After {en} comes {n_en}."))
            elif kind == "before":
                ask("02", I_MONTHS, tr(f"پیش از ماه {m} کدام ماه است؟", f"Which month is before {en}?"), month(i - 1), [month(i), month(i + 1), month(i - 2)],
                    tr(f"پیش از {m}، ماه {n} است.", f"Before {en} is {n_en}."))
            elif kind == "first":
                ask("02", I_MONTHS, tr("ماه اول سال کدام است؟", "Which is the first month of the year?"), month(0), [month(1), month(11), month(6)], year)
            else:
                ask("02", I_MONTHS, tr("ماه آخر سال کدام است؟", "Which is the last month of the year?"), month(11), [month(0), month(10), month(5)], year)
        for i in pick_even(range(12), 8, rng, key=lambda i: i // 3, cap=2):
            (m, en), season = month(i), SEASONS[i // 3]
            ask("02", I_MONTHS, tr(f"ماه {m} در کدام فصل است؟", f"In which season is the month of {en}?"), season, [x for x in SEASONS if x != season],
                tr(f"ماه {m} در فصل {season[0]} است.", f"The month of {en} is in {season[1]}."))
    build(s, 4, "calendar", "02", months)

    def counts(rng):
        def count(say, ans, wrong, help_fa):
            row = lp(s, "03", I_CALENDAR, say, W(ans), [W(x) for x in near(ans, rng, 0, 400, wrong)], help_fa=help_fa)
            CHECK_META.append((row, Fraction(ans)))

        count(tr("یک هفته چند روز دارد؟", "How many days does a week have?"), 7, [6, 5, 10], tr("یک هفته هفت روز دارد.", "A week has 7 days."))
        count(tr("یک سال چند ماه دارد؟", "How many months does a year have?"), 12, [10, 7, 24], tr("یک سال دوازده ماه دارد.", "A year has 12 months."))
        count(tr("یک سال چند فصل دارد؟", "How many seasons does a year have?"), 4, [3, 12, 7], tr("یک سال چهار فصل دارد.", "A year has 4 seasons."))
        count(tr("هر فصل چند ماه دارد؟", "How many months does each season have?"), 3, [4, 12, 2], tr("هر فصل سه ماه دارد.", "Each season has 3 months."))
        count(tr("یک شبانه" + Z + "روز چند ساعت دارد؟", "How many hours do a day and a night have?"), 24, [12, 60, 20], tr("یک شبانه" + Z + "روز بیست و چهار ساعت دارد.", "A day and a night have 24 hours."))
        for k in rng.sample(range(2, 10), 4):
            count(tr(f"{fa(k)} هفته چند روز می{Z}شود؟", f"How many days do {k} weeks make?"), 7 * k, [7 * k + 7, 7 + k, 5 * k],
                  tr(f"هر هفته هفت روز دارد. {fa(k)} ضرب هفت مساوی {fa(7 * k)}.", f"Each week has 7 days. {k} times 7 equals {7 * k}."))
        for k in rng.sample(range(2, 8), 3):
            count(tr(f"{fa(k)} سال چند ماه می{Z}شود؟", f"How many months do {k} years make?"), 12 * k, [10 * k, 12 + k, 12 * k + 12],
                  tr(f"هر سال دوازده ماه دارد. {fa(k)} ضرب دوازده مساوی {fa(12 * k)}.", f"Each year has 12 months. {k} times 12 equals {12 * k}."))
        for k in rng.sample(range(3, 11), 2):
            count(tr(f"{fa(7 * k)} روز چند هفته می{Z}شود؟", f"How many weeks do {7 * k} days make?"), k, [k + 1, k - 1, 7],
                  tr(f"هر هفته هفت روز دارد. {fa(7 * k)} تقسیم هفت مساوی {fa(k)}.", f"Each week has 7 days. {7 * k} divided by 7 equals {k}."))
        for i in range(4):
            a, b = SEASONS[i], SEASONS[(i + 1) % 4]
            if i % 2 == 0:
                ask("03", I_CALENDAR, tr(f"بعد از {a[0]} کدام فصل می{Z}آید؟", f"Which season comes after {a[1]}?"), b, [x for x in SEASONS if x != b],
                    tr(f"بعد از {a[0]}، {b[0]} می{Z}آید.", f"After {a[1]} comes {b[1]}."))
            else:
                ask("03", I_CALENDAR, tr(f"پیش از {b[0]} کدام فصل است؟", f"Which season is before {b[1]}?"), a, [x for x in SEASONS if x != a],
                    tr(f"پیش از {b[0]}، {a[0]} است.", f"Before {b[1]} is {a[1]}."))
    build(s, 4, "calendar", "03", counts)

    def later(rng):
        cands = [(i, k) for i in range(7) for k in (2, 3, 4, -2, -3)]
        for i, k in pick_even(cands, N, rng, key=lambda c: (c[0] + c[1]) % 7):
            (d, en), (n, n_en) = day(i), day(i + k)
            way = [day(i + j * (1 if k > 0 else -1)) for j in range(1, abs(k) + 1)]
            wrong = uniq([day(i + k + 1), day(i + k - 1), day(i), day(i - k)], key=lambda p: p[0])
            wrong = [w for w in wrong if w != day(i + k)][:3]
            if k > 0:
                say = tr(f"امروز {d} است. {fa(k)} روز بعد کدام روز است؟", f"Today is {en}. Which day is it {k} days later?")
            else:
                say = tr(f"امروز {d} است. {fa(-k)} روز پیش کدام روز بود؟", f"Today is {en}. Which day was it {-k} days ago?")
            ask("04", I_DAY_COUNT, say, day(i + k), wrong,
                tr("، ".join(w[0] for w in way) + f". جواب {n} است.", ", ".join(w[1] for w in way) + f". The answer is {n_en}."))
    build(s, 4, "calendar", "04", later, few=7)
    return s


# ---------------------------------------------------------------------------
# Level 5: Tables and Charts (listen_pick)
# ---------------------------------------------------------------------------

CHARTS.update({
    "chart_bars_3": [("goat", "بز", 2), ("sheep", "گوسفند", 5), ("hen", "مرغ", 3)],
    "chart_table_3": [("apple", "سیب", 5), ("carrot", "زردک", 3), ("onion", "پیاز", 4)],
    "chart_bars_4": [("cup", "پیاله", 3), ("plate", "بشقاب", 4), ("egg", "تخم", 1)],
    "chart_table_4": [("flower", "گل", 4), ("star", "ستاره", 2), ("fish", "ماهی", 5)],
    "chart_bars_5": [("potato", "کچالو", 1), ("onion", "پیاز", 3), ("carrot", "زردک", 5)],
    "chart_table_5": [("book", "کتاب", 2), ("notebook", "کتابچه", 4), ("pencil", "پنسل", 3)],
    "chart_bars_6": [("pomegranate", "انار", 4), ("orange", "مالته", 2), ("apple", "سیب", 1)],
    "chart_table_6": [("bread", "نان", 1), ("egg", "تخم", 4), ("cup", "پیاله", 2)],
})
CHART_EXTRA.update({"chart_bars_3": "cow", "chart_table_3": "potato", "chart_bars_4": "bread", "chart_table_4": "apple",
                    "chart_bars_5": "walnut", "chart_table_5": "ball", "chart_bars_6": "watermelon", "chart_table_6": "plate"})
CHART_ROUNDS = [["chart_bars_1", "chart_bars_3", "chart_bars_5"], ["chart_table_1", "chart_table_3", "chart_table_5"],
                ["chart_bars_2", "chart_bars_4", "chart_bars_6"], ["chart_table_2", "chart_table_4", "chart_table_6"]]


def charts5(level: int) -> Sheet:
    if level == 6:
        return charts6(level)
    s = Sheet(LP_COLS)
    for r, names in enumerate(CHART_ROUNDS):
        rnd = f"{r + 1:02d}"

        def gen(rng, rnd=rnd, names=names):
            cands = []   # (answer for the spread, chart, kind, arguments)
            for name in names:
                rows = CHARTS[name]
                values = [v for _, _, v in rows]
                assert len(rows) == 3 and len(set(values)) == 3 and all(1 <= v <= 5 for v in values)
                cands.append((name + "most", name, "most", ()))
                for i in range(3):
                    cands.append((values[i], name, "count", (i,)))
                    cands.append((name + rows[i][0], name, "which", (i,)))
                for i, j in ((0, 1), (1, 2), (0, 2)):
                    cands.append((values[i] + values[j], name, "sum", (i, j)))
                    hi_, lo_ = (i, j) if values[i] > values[j] else (j, i)
                    cands.append((values[hi_] - values[lo_], name, "more", (hi_, lo_)))
                cands.append((sum(values), name, "total", ()))
            for _, name, kind, args in pick_even(cands, 20, rng, key=lambda c: c[0], cap=2):
                rows = CHARTS[name]
                values = [v for _, _, v in rows]
                bars = "bars" in name
                intro, kw, ke = (I_CHART, "گراف", "chart") if bars else (I_TABLE, "جدول", "table")

                def which(say, row_, help_fa):
                    # The fourth choice is a thing that is not in the chart: the builder
                    # always deals four choices, and it must not pick one by chance.
                    pic = row_[0]
                    row = lp(s, rnd, intro, say, pic, [p for p, _, _ in rows if p != pic] + [CHART_EXTRA[name]], show=name, help_fa=help_fa)
                    CAL_META.append((row, pic))

                def number(say, ans, prefer, help_fa):
                    numq(s, rnd, intro, say, ans, prefer, help_fa, rng, 20, show=name)

                if kind == "most":
                    pic, noun, v = max(rows, key=lambda x: x[2])
                    which(tr(f"در این {kw} کدام از همه بیشتر است؟", f"In this {ke}, which one is the most?"), (pic, noun, v),
                          tr(f"{noun} از همه بیشتر است: {fa(v)} تا.", f"The {bare(noun)} is the most: {v}."))
                elif kind == "count":
                    pic, noun, v = rows[args[0]]
                    number(tr(f"در این {kw} چند {noun} است؟", f"In this {ke}, how many {many(noun)} are there?"), v, [x for x in values if x != v],
                           tr(f"خانه{Z}های {noun} را بشمار: {fa(v)}.", f"Count the boxes of the {bare(noun)}: {v}."))
                elif kind == "which":
                    # "Which one is the fewest?" is not asked: the thing that is not in the chart could be meant.
                    pic, noun, v = rows[args[0]]
                    which(tr(f"در این {kw} از کدام چیز {fa(v)} تا است؟", f"In this {ke}, of which thing {'is' if v == 1 else 'are'} there {v}?"), (pic, noun, v),
                          tr(f"{fa(v)} {noun} است.", f"{there(v, noun)}."))
                elif kind == "sum":
                    (_, n1, v1), (_, n2, v2) = rows[args[0]], rows[args[1]]
                    number(tr(f"در این {kw}، {n1} و {n2} با هم چند تا است؟", f"In this {ke}, how many are the {many(n1)} and the {many(n2)} together?"), v1 + v2,
                           [max(v1, v2), abs(v1 - v2), v1 + v2 + 1], tr(f"{fa(v1)} جمع {fa(v2)} مساوی {fa(v1 + v2)}.", f"{v1} plus {v2} equals {v1 + v2}."))
                elif kind == "more":
                    (_, n1, v1), (_, n2, v2) = rows[args[0]], rows[args[1]]
                    number(tr(f"در این {kw}، {n1} چند تا بیشتر از {n2} است؟", f"In this {ke}, how many more {many(n1)} than {many(n2)} are there?"), v1 - v2,
                           [v1, v1 + v2, v1 - v2 + 1], tr(f"{fa(v1)} منفی {fa(v2)} مساوی {fa(v1 - v2)}.", f"{v1} minus {v2} equals {v1 - v2}."))
                else:
                    total = sum(values)
                    number(tr(f"در این {kw} همه با هم چند تا است؟", f"In this {ke}, how many are there altogether?"), total, [total - 1, total + 1, max(values)],
                           tr(" جمع ".join(fa(v) for v in values) + f" مساوی {fa(total)}.", " plus ".join(str(v) for v in values) + f" equals {total}."))
        build(s, 5, "charts", rnd, gen)
    for row, what in CAL_META:
        if row["show"] in CHARTS:  # most and "of which thing are there n" once more, from the chart's own numbers
            counts = {p: v for p, _, v in CHARTS[row["show"]]}
            assert set(row["distractors"].split("|")) == (set(counts) - {row["answer"]}) | {CHART_EXTRA[row["show"]]}, row
            if "بیشتر" in row["say_fa"]:
                assert row["answer"] == max(counts, key=counts.get), row
            else:
                assert fa(counts[row["answer"]]) + " تا" in row["say_fa"], row
    return s


# ---------------------------------------------------------------------------
# Level 5: Fair Shares (listen_pick): fractions and decimals
# ---------------------------------------------------------------------------

def fractions5(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    def B(rnd, gen, **kw):
        build(s, 5, "fractions", rnd, gen, **kw)

    def add(rnd, intro, say, answer, wrong, help_fa, show=""):
        row = lp(s, rnd, intro, say, answer, wrong, show=show, help_fa=help_fa)
        CHECK_META.append((row, val(answer)))
        return row

    def naming(rng):
        cands = [(k, n, coloured) for k, n in PIES5 for coloured in (True, False) if coloured or 2 * k != n]
        for k, n, coloured in pick_even(cands, N, rng, key=lambda c: Fraction(c[0] if c[2] else c[1] - c[0], c[1]), cap=2):
            a = k if coloured else n - k
            cands_w = [fr(n - a, n), fr(a, n + 1), fr(a + 1, n) if a + 1 < n else fr(a, n + 2), fr(n, a) if a > 1 else fr(a + 1, n + 1),
                       fr(a, n - 1) if n - 1 > a else fr(a + 2, n + 2)]
            wrong = pick_wrong(fr(a, n), cands_w)
            if coloured:
                say = tr("چند حصه رنگ شده است؟ کسر درست را انتخاب کن.", "How many parts are coloured? Choose the right fraction.")
                help_fa = tr(f"{fa(n)} حصه برابر است و {fa(k)} حصه رنگ شده است: {fa_frac(k, n)}.",
                             f"There are {n} equal parts and {k} {'is' if k == 1 else 'are'} coloured: {k}/{n}.")
            else:
                say = tr("چند حصه سفید مانده است؟ کسر درست را انتخاب کن.", "How many parts are left white? Choose the right fraction.")
                help_fa = tr(f"{fa(n)} حصه برابر است و {fa(a)} حصه سفید مانده است: {fa_frac(a, n)}.",
                             f"There are {n} equal parts and {a} {'is' if a == 1 else 'are'} left white: {a}/{n}.")
            add("01", I_FRAC_NAME, say, fr(a, n), wrong, help_fa, show=pie(k, n))
    B("01", naming)

    def picturing(rng):
        equal = [(2, 4, 1, 2), (2, 6, 1, 3), (2, 8, 1, 4), (4, 6, 2, 3), (6, 8, 3, 4), (2, 10, 1, 5), (4, 10, 2, 5), (6, 10, 3, 5), (8, 10, 4, 5)]
        cands = [(k, n, k, n) for k, n in PIES5] + [e for e in equal if (e[2], e[3]) in PIES5]
        for a, b, k, n in pick_even(cands, N, rng, key=lambda c: (c[2], c[3]), cap=2):
            others = [p for p in PIES5 if Fraction(*p) != Fraction(k, n)]
            close = [p for p in others if p[1] == n] + [p for p in others if p[0] == k and p[1] != n]
            rng.shuffle(close)
            rng.shuffle(others)
            wrong = pick_wrong(pie(k, n), [pie(*p) for p in close + others])
            if (a, b) == (k, n):
                help_fa = tr(f"{fa_frac(k, n)} یعنی {fa(k)} حصه از {fa(n)} حصه برابر.", f"{k}/{n} means {k} of {n} equal parts.")
            else:
                help_fa = tr(f"{fa_frac(a, b)} مساوی {fa_frac(k, n)} است: {fa(k)} حصه از {fa(n)} حصه برابر.", f"{a}/{b} is equal to {k}/{n}: {k} of {n} equal parts.")
            add("02", I_FRAC_PIC, tr(f"کدام شکل {fa_frac(a, b)} را نشان می{Z}دهد؟", f"Which picture shows {a}/{b}?"), pie(k, n), wrong, help_fa)
    B("02", picturing)

    same = "مخرج" + Z + "ها یکی است. کسری که صورت بزرگتر دارد، بزرگتر است."
    same_en = "The denominators are the same. The fraction with the bigger numerator is bigger."
    unit = "صورت" + Z + "ها یکی است. هر قدر مخرج کوچکتر باشد، حصه بزرگتر است."
    unit_en = "The numerators are the same. The smaller the denominator, the bigger the part."

    def comparing(rng):
        for i in range(N):
            biggest = i % 2 == 0
            if i % 4 < 2:
                n = rng.choice([5, 6, 7, 8, 9, 10, 12])
                group, why, why_en = [(k, n) for k in rng.sample(range(1, n), 4)], same, same_en
            else:
                k = rng.choice([1, 1, 2, 3])
                group, why, why_en = [(k, n) for n in rng.sample(range(k + 1, 13), 4)], unit, unit_en
            ans = max(group, key=lambda p: Fraction(*p)) if biggest else min(group, key=lambda p: Fraction(*p))
            say = tr("کدام کسر از همه بزرگتر است؟", "Which fraction is the biggest?") if biggest else tr("کدام کسر از همه کوچکتر است؟", "Which fraction is the smallest?")
            tail = tr(f"{fa_frac(*ans)} از همه بزرگتر است.", f"{ans[0]}/{ans[1]} is the biggest.") if biggest else tr(f"{fa_frac(*ans)} از همه کوچکتر است.", f"{ans[0]}/{ans[1]} is the smallest.")
            row = add("03", I_FRAC_CMP, say, fr(*ans), [fr(*p) for p in group if p != ans], tr(why + " " + tail, why_en + " " + EN[tail]))
            got, rest_v = val(row["answer"]), [val(x) for x in row["distractors"].split("|")]
            assert all(got > v for v in rest_v) if biggest else all(got < v for v in rest_v)
    B("03", comparing)

    def adding(rng):
        sums = [(a, b, n) for n in range(5, 13) for a in range(1, n) for b in range(1, n) if a < b and a + b < n]
        for a, b, n in pick_even(sums, N, rng, key=lambda c: Fraction(c[0] + c[1], c[2]), cap=1):
            c = a + b
            wrong = pick_wrong(fr(c, n), [fr(c, 2 * n), fr(c + 1, n), fr(b - a, n), fr(c - 1, n), fr(a * b, n)])
            add("04", I_FRAC_ADD, tr(f"{fa_frac(a, n)} جمع {fa_frac(b, n)} چند می{Z}شود؟", f"{a}/{n} plus {b}/{n} makes how many?"), fr(c, n), wrong,
                tr(f"مخرج همان {fa(n)} می{Z}ماند. {fa(a)} جمع {fa(b)} مساوی {fa(c)}. جواب {fa_frac(c, n)} است.",
                   f"The denominator stays {n}. {a} plus {b} equals {c}. The answer is {c}/{n}."))
    B("04", adding)

    def money_decimals(rng):
        amounts = [a * 100 + p for a in range(1, 13) for p in (5, 10, 20, 25, 50, 75)] + [25, 50, 75, 5, 90]
        for pul in pick_even(amounts, 11, rng, cap=1):
            a, p = divmod(pul, 100)
            swapped = a * 100 + (p // 10 if p % 10 == 0 else p * 10 % 100)
            wrong = pick_wrong(money(pul), [money(swapped), money(pul * 10), money(max(1, pul // 10)), money(pul + 100), money(pul + 5)])
            add("05", I_MONEY_DEC, tr(f"{money_fa(pul)} را با عدد اعشاری چطور می{Z}نویسیم؟", f"How do we write {money_en(pul)} as a decimal number?"), money(pul), wrong,
                tr(f"افغانی پیش از نقطه و پول بعد از نقطه می{Z}آید: {fa_dec(money(pul)[2:])}.", f"The afghani come before the point and the pul after the point: {money(pul)[2:]}."))
        numq(s, "05", I_MONEY_DEC, tr(f"یک {AFN} چند پول است؟", "How many pul is 1 afghani?"), 100, [10, 1000, 50],
             tr(f"یک {AFN} صد پول است.", "1 afghani is 100 pul."), rng, 2000)
        numq(s, "05", I_MONEY_DEC, tr(f"نیم {AFN} چند پول است؟", "How many pul is half an afghani?"), 100 // 2, [5, 500, 25],
             tr(f"یک {AFN} صد پول است. نیم آن پنجاه پول است.", "1 afghani is 100 pul. Half of it is 50 pul."), rng, 2000)
        for pul in rng.sample([25, 75, 10, 5, 90, 150, 225, 105], 5):
            numq(s, "05", I_MONEY_DEC, tr("این چند پول است؟", "How many pul is this?"), pul, [pul * 10, pul // 5, int(str(pul)[::-1]) if pul % 10 else pul + 10],
                 tr(f"{fa_dec(money(pul)[2:])} {AFN}، یعنی {fa(pul)} پول.", f"{money(pul)[2:]} afghani means {pul} pul."), rng, 5000, show=money(pul))
    B("05", money_decimals)

    def decimals(rng):
        for i in range(9):
            biggest = i % 2 == 0
            a, b, c = rng.randint(0, 3), rng.randint(1, 9), rng.randint(1, 9)
            pool = uniq([f"{a}.{b}", f"{a}.{b}{c}", f"{a}.0{c}", f"{a}.{c}", f"{a + 1}.0{b}", f"{a}.{c}{b}", f"{a + 1}.{b}"], key=Fraction)
            if len(pool) < 4:
                raise Retry("too few decimals")
            group = rng.sample(pool, 4)
            ans = max(group, key=Fraction) if biggest else min(group, key=Fraction)
            say = tr("کدام عدد از همه بزرگتر است؟", "Which number is the biggest?") if biggest else tr("کدام عدد از همه کوچکتر است؟", "Which number is the smallest?")
            help_fa = tr(f"{fa_dec(ans)} از همه بزرگتر است.", f"{ans} is the biggest.") if biggest else tr(f"{fa_dec(ans)} از همه کوچکتر است.", f"{ans} is the smallest.")
            add("06", I_DEC, say, "t:" + ans, ["t:" + d for d in group if d != ans], help_fa)
        pairs = [(a, b) for a in range(25, 500, 25) for b in range(25, 400, 25) if a != b and (a + b) % 100]
        for a, b in pick_even(pairs, 9, rng, key=sum, cap=1):
            t = a + b
            wrong = pick_wrong(money(t), [money(t + 100), money(t - 100) if t > 100 else money(t + 50), money(t + 10), money(t - 10)])
            add("06", I_DEC, tr(f"{money_fa(a)} جمع {money_fa(b)} چند می{Z}شود؟", f"{money_en(a)} plus {money_en(b)} makes how much?"), money(t), wrong,
                tr(f"جواب {money_fa(t)} است: {fa_dec(money(t)[2:])}.", f"The answer is {money_en(t)}: {money(t)[2:]}."))
    B("06", decimals)
    return s


# ---------------------------------------------------------------------------
# Number Riddles (listen_pick), all levels
# ---------------------------------------------------------------------------

I_EQUAL = tr("دسته" + Z + "ای را پیدا کن که همان قدر است، بیشتر است یا کمتر است.", "Find the group that is just as many, more or fewer.")
I_COINS = tr("سکه" + Z + "ها و نوت" + Z + "ها را جمع کن.", "Add the coins and the notes.")
I_ODD_ONE = tr("عدد جفت یا طاق را پیدا کن.", "Find the even or the odd number.")
I_SIGN = tr("کدام نشان کم است؟ جمع، منفی، ضرب یا تقسیم؟", "Which sign is missing? Plus, minus, times or divided by?")
I_BIGGEST_SUM = tr("حساب کن و ببین جواب کدام از همه بزرگتر است.", "Work them out and see which answer is the biggest.")
I_EQUAL_VALUE = tr("عددی را پیدا کن که با این عدد مساوی است.", "Find the number that is equal to this number.")


def riddles(level: int) -> Sheet:
    if level == 6:
        return riddles6(level)
    s = Sheet(LP_COLS)

    def B(rnd, gen, **kw):
        build(s, level, "riddles", rnd, gen, **kw)

    def rows_round(rnd, cands, lo, hi, intro, n=N, dari_every=0):
        """cands: (start, step, count, gap). The answer is the number at the gap."""
        def gen(rng):
            for i, (start, step, count, gap) in enumerate(pick_even(cands, n, rng, key=lambda c: c[0] + c[1] * c[3])):
                row_item(s, rnd, intro, start, step, count, gap, rng, lo, hi, script="D" if dari_every and i % dari_every == dari_every - 1 else "W")
        B(rnd, gen)

    def gaps(starts, steps, count, lo, hi, last=False):
        return [(a, st, count, g) for a in starts for st in steps for g in ([count - 1] if last else range(1, count - 1))
                if lo <= a <= hi and lo <= a + st * (count - 1) <= hi]

    def between_round(rnd, values, lo, hi, n=N):
        def gen(rng):
            cands = [(v, form) for v in values for form in (0, 1, 2)]   # between, after, before
            for v, form in pick_even(cands, n, rng, key=lambda c: c[0] + (0, 1, -1)[c[1]], cap=2):
                if form == 0:
                    between_item(s, rnd, I_BETWEEN, v, rng, lo, hi)
                else:
                    next_item(s, rnd, I_BETWEEN, v, form == 1, rng, lo, hi + 1)
        B(rnd, gen)

    def parity_round(rnd, lo, hi, n=N):
        def gen(rng):
            for i, ans in enumerate(even(lo, hi, n, rng, cap=1)):
                want_even = ans % 2 == 0
                others = [x for x in range(max(lo, ans - 12), min(hi, ans + 12) + 1) if (x % 2 == 0) != want_even]
                wrong = rng.sample(others, 3)
                d, e = said_list([ans] + wrong, spoken_number)
                if want_even:
                    say, help_fa = tr(f"{d}. کدام عدد جفت است؟", f"{e}. Which number is even?"), tr(f"{fa(ans)} جفت است: آن را دو حصه برابر کرده می{Z}توانی.", f"{ans} is even: you can make it into 2 equal parts.")
                else:
                    say, help_fa = tr(f"{d}. کدام عدد طاق است؟", f"{e}. Which number is odd?"), tr(f"{fa(ans)} طاق است: وقتی دو حصه می{Z}کنی، یکی باقی می{Z}ماند.", f"{ans} is odd: when you make 2 parts, 1 is left over.")
                lp(s, rnd, I_ODD_ONE, say, W(ans), [W(x) for x in wrong], help_fa=help_fa,
                   truth=(lambda c: val(c) % 2 == 0) if want_even else (lambda c: val(c) % 2 == 1))
        B(rnd, gen, few=0)

    def sign_round(rnd, facts, n=16):
        """facts: (a, op, b): only one of the four signs makes the sum right."""
        names = {"+": ("جمع", "plus"), "-": ("منفی", "minus"), "*": ("ضرب", "times"), "/": ("تقسیم", "divided by")}
        shown = {"+": "t:+", "-": "t:−", "*": "t:×", "/": "t:÷"}

        def fits(a, op, b, c):
            return {"+": a + b == c, "-": a - b == c, "*": a * b == c, "/": b and a == b * c}[op]

        def gen(rng):
            good = [(a, op, b) for a, op, b in facts if sum(fits(a, o, b, calc4(a, op, b)) for o in "+-*/") == 1
                    and units(f"t:{a}{BLANK}{b}={calc4(a, op, b)}") <= SHOW_UNITS]
            for op in "+-*/":
                for a, _, b in rng.sample([t for t in good if t[1] == op], n // 4):
                    c = calc4(a, op, b)
                    d, e = names[op]
                    lp(s, rnd, I_SIGN, tr(f"{fa(a)}، جای خالی، {fa(b)}، مساوی {fa(c)}. کدام نشان درست است؟", f"{a}, blank, {b}, equals {c}. Which sign is right?"),
                       shown[op], [shown[o] for o in "+-*/" if o != op], show=f"t:{a}{BLANK}{b}={c}",
                       help_fa=tr(f"{fa(a)} {d} {fa(b)} مساوی {fa(c)}. نشان {d} درست است.", f"{a} {e} {b} equals {c}. The {e} sign is right."),
                       truth=lambda ch, a=a, b=b, c=c: fits(a, {v: k for k, v in shown.items()}[ch], b, c))
        B(rnd, gen, few=4)

    def biggest_round(rnd, facts, n=16):
        """Four sums: which one has the biggest (or the smallest) answer?"""
        def gen(rng):
            for i in range(n):
                group = uniq(rng.sample(facts, 12), key=lambda t: calc4(*t))[:4]
                if len(group) < 4:
                    raise Retry("too few sums")
                big = i % 2 == 0
                best = (max if big else min)(group, key=lambda t: calc4(*t))
                d, e = say_sum(*best)
                v = calc4(*best)
                if big:
                    say = tr("جواب کدام حساب از همه بزرگتر است؟", "Which sum has the biggest answer?")
                    help_fa = tr(f"{d} مساوی {fa(v)}. این از همه بزرگتر است.", f"{e} equals {v}. This is the biggest.")
                else:
                    say = tr("جواب کدام حساب از همه کوچکتر است؟", "Which sum has the smallest answer?")
                    help_fa = tr(f"{d} مساوی {fa(v)}. این از همه کوچکتر است.", f"{e} equals {v}. This is the smallest.")
                values = [calc4(*t) for t in group]
                lp(s, rnd, I_BIGGEST_SUM, say, sum_text(*best), [sum_text(*t) for t in group if t != best], help_fa=help_fa,
                   truth=(lambda c, m=max(values): text_sum(c) == m) if big else (lambda c, m=min(values): text_sum(c) == m))
        B(rnd, gen)

    if level == 1:
        rows_round("01", gaps(range(0, 8), [1], 4, 0, 10) + gaps(range(0, 7), [1], 5, 0, 10), 0, 10, I_MISSING)
        between_round("02", range(1, 10), 0, 10)

        def groups(rng):
            objs = rng.sample(COUNT_OBJS, len(COUNT_OBJS))
            for i, v in enumerate(even(2, 10, N, rng)):
                (p1, n1), (p2, n2) = objs[i], objs[(i + 5) % len(objs)]
                if i % 3 == 0:
                    wrong = rng.sample([x for x in range(1, 13) if x != v], 3)
                    lp(s, "03", I_EQUAL, tr(f"این {n1} را ببین. در کدام تصویر همین قدر {n2} است؟", f"Look at the {many(n1)}. Which picture has just as many {many(n2)}?"),
                       f"p:{p2}*{v}", [f"p:{p2}*{x}" for x in wrong], show=f"p:{p1}*{v}",
                       help_fa=tr(f"{fa(v)} {n1} و {fa(v)} {n2}: هر دو {fa(v)} تا است.", f"{cnt(v, n1)} and {cnt(v, n2)}: both are {v}."),
                       truth=lambda c, v=v: int(c.split("*")[1]) == v)
                elif i % 3 == 1:
                    ref = v - rng.randint(1, min(3, v - 1))
                    wrong = rng.sample(range(1, ref + 1), 3) if ref >= 3 else None
                    if wrong is None:
                        raise Retry("no room")
                    lp(s, "03", I_EQUAL, tr(f"این {n1} را ببین. در کدام تصویر {n2} بیشتر از این است؟", f"Look at the {many(n1)}. In which picture are there more {many(n2)} than this?"),
                       f"p:{p2}*{v}", [f"p:{p2}*{x}" for x in wrong], show=f"p:{p1}*{ref}",
                       help_fa=tr(f"{fa(v)} از {fa(ref)} بیشتر است.", f"{v} is more than {ref}."), truth=lambda c, r=ref: int(c.split("*")[1]) > r)
                else:
                    ref = v + rng.randint(1, 3)
                    wrong = rng.sample(range(ref, ref + 5), 3)
                    lp(s, "03", I_EQUAL, tr(f"این {n1} را ببین. در کدام تصویر {n2} کمتر از این است؟", f"Look at the {many(n1)}. In which picture are there fewer {many(n2)} than this?"),
                       f"p:{p2}*{v}", [f"p:{p2}*{x}" for x in wrong], show=f"p:{p1}*{ref}",
                       help_fa=tr(f"{fa(v)} از {fa(ref)} کمتر است.", f"{v} is fewer than {ref}."), truth=lambda c, r=ref: int(c.split("*")[1]) < r)
        B("03", groups)
        rows_round("04", gaps(range(6, 18), [1], 4, 0, 20) + gaps(range(8, 21), [-1], 4, 0, 20), 0, 20, I_MISSING, dari_every=4)
        between_round("05", range(9, 20), 0, 20)
        rows_round("06", gaps(range(0, 14), [2], 4, 0, 20, last=True) + gaps([0, 5], [5], 4, 0, 20, last=True) + gaps(range(8, 21), [-2], 4, 0, 20, last=True) +
                   gaps(range(0, 14), [2], 4, 0, 20), 0, 20, I_PATTERN)
        bigger_round(s, 1, "07", 0, 20, scripts="WWD")
    elif level == 2:
        rows_round("01", gaps(range(17, 97), [1], 4, 0, 100), 0, 100, I_MISSING, dari_every=4)
        between_round("02", range(21, 100), 0, 100)
        rows_round("03", gaps(range(10, 90), [2], 4, 0, 100, last=True) + gaps(range(5, 80, 5), [5], 4, 0, 100, last=True) + gaps(range(3, 60), [10], 4, 0, 100, last=True) +
                   gaps(range(40, 100), [-10], 4, 0, 100, last=True) + gaps(range(30, 100, 5), [-5], 4, 0, 100, last=True), 0, 100, I_PATTERN)
        bigger_round(s, 2, "04", 10, 100, scripts="WWD")

        def coins(rng):
            units = [1, 2, 5, 10, 20, 50]
            sets = [tuple(sorted(c, reverse=True)) for k in (2, 3) for c in itertools.combinations_with_replacement(units, k)]
            by_total: dict = {}
            for c in sets:
                by_total.setdefault(sum(c), []).append(c)
            totals = [t for t in sorted(by_total) if 4 <= t <= 90]
            for i, t in enumerate(pick_even(totals, N, rng, cap=1)):
                right = rng.choice(by_total[t])
                text = lambda c: "t:" + "+".join(map(str, c))  # noqa: E731
                if i % 2 == 0:   # which coins make t?
                    near_sets = [c for u in totals if u != t and abs(u - t) <= max(5, t // 3) for c in by_total[u]]
                    wrong = uniq(rng.sample(near_sets, len(near_sets)), key=sum)[:3]
                    if len(wrong) < 3:
                        raise Retry("too few coin sets")
                    lp(s, "05", I_COINS, tr(f"کدام سکه{Z}ها با هم {fa(t)} {AFN} می{Z}شود؟", f"Which coins together make {t} afghani?"), text(right), [text(c) for c in wrong],
                       help_fa=tr(" جمع ".join(fa(x) for x in right) + f" مساوی {fa(t)}.", " plus ".join(map(str, right)) + f" equals {t}."),
                       truth=lambda c, t=t: text_sum(c) == t)
                else:            # how much is this money?
                    wrong = near(t, rng, 1, 150, [t + right[-1], t - right[-1], len(right), t + 10])
                    lp(s, "05", I_COINS, tr(" و ".join(fa(x) for x in right) + f". این پول چند {AFN} است؟", " and ".join(map(str, right)) + ". How many afghani is this money?"),
                       W(t), [W(x) for x in wrong], show=text(right),
                       help_fa=tr(" جمع ".join(fa(x) for x in right) + f" مساوی {fa(t)}.", " plus ".join(map(str, right)) + f" equals {t}."),
                       truth=lambda c, t=t: val(c) == t)
        B("05", coins)
        parity_round("06", 2, 60)
        same_sum_round(s, 2, "riddles", "07", [(a, "+", b) for a in range(1, 13) for b in range(1, 11) if 6 <= a + b <= 20])
    elif level == 3:
        rows_round("01", gaps(range(95, 997), [1], 4, 0, 1000), 0, 1000, I_MISSING, dari_every=4)
        between_round("02", range(101, 1000), 0, 1000)
        rows_round("03", gaps(range(100, 700, 50), [100], 4, 0, 1000, last=True) + gaps(range(50, 800, 50), [50], 4, 0, 1000, last=True) +
                   gaps(range(95, 900, 35), [10], 4, 0, 1000, last=True) + gaps(range(90, 990, 55), [5], 4, 0, 1000, last=True) +
                   gaps(range(300, 1001, 50), [-100], 4, 0, 1000, last=True) + gaps(range(96, 500, 62), [2], 4, 0, 1000, last=True), 0, 1000, I_PATTERN)
        bigger_round(s, 3, "04", 100, 1000, scripts="WWD")
        parity_round("05", 100, 999)
        same_sum_round(s, 3, "riddles", "06", [(a, "+", b) for a in range(10, 100, 5) for b in range(10, 100, 10) if 40 <= a + b <= 150 and a != b] +
                       [(a, "*", b) for a in range(2, 11) for b in (2, 5, 10)])
    elif level == 4:
        rows_round("01", [(t * i, t, 4, g) for t in (3, 4, 6, 7, 8, 9) for i in range(1, 8) for g in (1, 2)], 0, 100, I_MISSING)
        rows_round("02", [(t * i, t, 4, 3) for t in (3, 4, 6, 7, 8, 9) for i in range(1, 8)] + [(t * i, -t, 4, 3) for t in (3, 4, 6, 7, 8, 9) for i in range(6, 11)], 0, 120, I_PATTERN)
        same_sum_round(s, 4, "riddles", "03", [(a, "*", b) for a in range(2, 11) for b in range(2, 11)])
        biggest_round("04", [(a, "*", b) for a in range(3, 10) for b in range(3, 10)])
        facts = [(a, "*", b) for a in range(3, 10) for b in range(2, 10)] + [(a * b, "/", b) for a in range(2, 10) for b in range(3, 10)] + \
                [(a, "+", b) for a in range(12, 60) for b in range(5, 30)] + [(a, "-", b) for a in range(20, 80) for b in range(5, 19)]
        sign_round("05", facts)
    else:
        rows_round("01", gaps(range(1000, 9000, 500), [1000], 4, 0, 20000) + gaps(range(500, 9000, 250), [500], 4, 0, 20000) + gaps(range(250, 5000, 250), [250], 4, 0, 20000) +
                   gaps(range(9996, 10000), [1], 4, 0, 20000) + gaps(range(10000, 60001, 10000), [10000], 4, 0, 100000), 0, 100000, I_MISSING)
        bigger_round(s, 5, "02", 1000, 100000, scripts="WWD")

        def equal_value(rng):
            forms = {Fraction(1, 2): ["1/2", "2/4", "0.5", "5/10", "0.50", "3/6"], Fraction(1, 4): ["1/4", "2/8", "0.25", "3/12"], Fraction(3, 4): ["3/4", "6/8", "0.75"],
                     Fraction(1, 5): ["1/5", "2/10", "0.2", "0.20"], Fraction(1, 10): ["1/10", "0.1", "0.10"], Fraction(2, 5): ["2/5", "4/10", "0.4"],
                     Fraction(3, 5): ["3/5", "6/10", "0.6"], Fraction(1, 3): ["1/3", "2/6", "3/9"], Fraction(2, 3): ["2/3", "4/6", "6/9"], Fraction(4, 5): ["4/5", "8/10", "0.8"]}
            spoken = lambda t: (fa_dec(t), t) if "." in t else (fa_frac(*map(int, t.split("/"))), t)  # noqa: E731
            every = [t for fs in forms.values() for t in fs]
            cands = [(v, a, b) for v, fs in forms.items() for a in fs for b in fs if a != b]
            for v, a, b in pick_even(cands, 16, rng, key=lambda c: c[2], cap=1):
                wrong = uniq(rng.sample([t for t in every if Fraction(t) != v], 12), key=Fraction)[:3]
                lp(s, "03", I_EQUAL_VALUE, tr(f"کدام عدد با {spoken(a)[0]} مساوی است؟", f"Which number is equal to {spoken(a)[1]}?"), "t:" + b, ["t:" + w for w in wrong], show="t:" + a,
                   help_fa=tr(f"{spoken(a)[0]} و {spoken(b)[0]} مساوی هستند.", f"{spoken(a)[1]} and {spoken(b)[1]} are equal."),
                   truth=lambda c, v=v: val(c) == v)
        B("03", equal_value)
        biggest_round("04", [(a, "*", b) for a in (10, 20, 30, 40, 50, 12, 15, 25) for b in range(2, 10)] + [(a, "+", b) for a in range(100, 400, 50) for b in range(50, 300, 50)])
        facts = [(a, "*", b) for a in range(11, 30) for b in range(2, 10)] + [(a * b, "/", b) for a in range(11, 30) for b in range(2, 10)] + \
                [(a, "+", b) for a in range(25, 90) for b in range(15, 60) if a + b < 100] + [(a, "-", b) for a in range(50, 100) for b in range(15, 46)]
        sign_round("05", facts)
    return s


# ---------------------------------------------------------------------------
# True or False (sorter with a yes and a no basket), all levels
# ---------------------------------------------------------------------------

def truefalse(level: int) -> Sheet:
    if level == 6:
        return truefalse6(level)
    s = Sheet(SORTER_COLS)

    def B(rnd, gen, **kw):
        build(s, level, "truefalse", rnd, gen, **kw)

    if level == 1:
        def estimate(rng):
            objs = rng.sample(COUNT_OBJS, N)
            fewer = even(3, 8, N // 2, rng)
            more = even(12, 20, N - N // 2, rng)
            for i, v in enumerate(spread([("less", x) for x in fewer] + [("more", x) for x in more], rng)):
                kind, x = v
                pic, noun = objs[i]
                less = kind == "less"
                en = "fewer than 10" if less else "more than 10"
                row = s.add(round="01", intro_fa=I_ESTIMATE, thing=f"p:{pic}*{x}", say_fa=tr(noun, bare(noun)),
                            basket="f:" + tr(("f:کمتر از ۱۰" if less else "f:بیشتر از ۱۰")[2:], en),
                            basket_say_fa=tr("کمتر از ده" if less else "بیشتر از ده", en))
                EST_META.append((row, x, 10))
        B("01", estimate)

        def counted(rng):
            objs = rng.sample(COUNT_OBJS, N)
            for i, v in enumerate(even(2, 12, N, rng)):
                pic, noun = objs[i]
                true = i % 2 == 0
                said = v if true else v + rng.choice([-1, 1, 2] if v > 2 else [1, 2])
                tf_row(s, "02", I_COUNT_TRUE, f"p:{pic}*{v}", tr(f"اینجا {fa(said)} {noun} است", f"Here {'is' if said == 1 else 'are'} {cnt(said, noun)}"), true)
                EST_META.append((s.rows[-1], v, said if true else -1))
        B("02", counted)
        tf_compare_round(s, 1, "03", 0, 20)
        tf_sum_round(s, 1, "04", [(a, "+", b) for a in range(1, 10) for b in range(1, 10) if a + b <= 10] + [(a, "-", b) for a in range(3, 11) for b in range(1, a)])
        tf_sum_round(s, 1, "05", [(a, "+", b) for a in range(11, 19) for b in range(1, 9) if a % 10 + b <= 9] + [(a, "-", b) for a in range(12, 20) for b in range(1, 10) if b <= a % 10] +
                     [(10, "+", b) for b in range(1, 11)])
    elif level == 2:
        tf_sum_round(s, 2, "01", [(a, "+", b) for a in range(2, 10) for b in range(2, 10) if a + b >= 11] + [(a, "-", b) for a in range(11, 19) for b in range(2, 10) if b > a % 10])
        tf_compare_round(s, 2, "02", 10, 100)

        def places(rng):
            for i, v in enumerate(even(21, 99, N, rng, ok=lambda x: x % 10 and x // 10 != x % 10, cap=1)):
                t, o = divmod(v, 10)
                true = i % 2 == 0
                ask_tens = i % 4 < 2
                said = (t if ask_tens else o) if true else (o if ask_tens else t)
                what, en = ("ده", "ten") if ask_tens else ("یک", "one")
                tf_row(s, "03", I_TRUE_CMP, W(v), tr(f"{fa(v)}، {ONES[said]} {what} دارد", f"{v} has {nn(said, en)}"), true)
        B("03", places)
        tf_sum_round(s, 2, "04", [(a, "+", b) for a in range(10, 100, 10) for b in range(10, 100, 10) if a + b <= 100] + [(a, "-", b) for a in range(20, 101, 10) for b in range(10, a, 10)])
    elif level == 3:
        tf_sum_round(s, 3, "01", [(a, "+", b) for a in range(13, 80) for b in range(13, 60) if a % 10 + b % 10 >= 10 and a + b <= 100 and a % 10 and b % 10])
        tf_sum_round(s, 3, "02", [(a, "*", b) for a in range(2, 11) for b in (2, 5, 10)] + [(b, "*", a) for a in range(3, 11) for b in (2, 5, 10)])
        tf_compare_round(s, 3, "03", 100, 1000)
        tf_sum_round(s, 3, "04", [(a, "-", b) for a in range(31, 100) for b in range(12, 90) if a % 10 < b % 10 and a - b >= 3])
    elif level == 4:
        tf_sum_round(s, 4, "01", [(a, "*", b) for a in range(3, 10) for b in range(3, 10)])
        tf_sum_round(s, 4, "02", [(a * b, "/", b) for a in range(2, 11) for b in range(3, 10)])
        tf_sum_round(s, 4, "03", [(a, "*", b) for a in range(6, 10) for b in range(6, 10)] + [(a * b, "/", b) for a in range(6, 10) for b in range(6, 10)] +
                     [(a, "+", b) for a in range(25, 60) for b in range(16, 40) if a % 10 + b % 10 >= 10] + [(a, "-", b) for a in range(41, 90) for b in range(15, 40) if a % 10 < b % 10])
    else:
        tf_sum_round(s, 5, "01", [(a, "*", b) for a in range(12, 60) for b in (10, 100)] + [(a, "*", b) for a in range(11, 40) for b in range(2, 6) if a % 10] +
                     [(a * b, "/", b) for a in range(11, 30) for b in range(2, 8)])

        def frac_sums(rng):
            sums = [(a, b, n) for n in range(5, 10) for a in range(1, n) for b in range(1, n) if a < b and a + b < n]   # one-digit denominators fit the card
            for i, (a, b, n) in enumerate(rng.sample(sums, 16)):
                true = i % 2 == 0
                top, bottom = (a + b, n) if true else rng.choice([(a + b, 2 * n), (a + b + 1, n), (a + b - 1, n)])
                tf_row(s, "02", I_TRUE, f"t:{a}/{n}+{b}/{n}={top}/{bottom}", tr(f"{fa_frac(a, n)} جمع {fa_frac(b, n)} مساوی {fa_frac(top, bottom)}",
                                                                                 f"{a}/{n} plus {b}/{n} equals {top}/{bottom}"), true)
        B("02", frac_sums)

        def equal(rng):
            forms = [("1/2", "2/4"), ("1/2", "0.5"), ("1/4", "0.25"), ("3/4", "0.75"), ("1/5", "0.2"), ("1/10", "0.1"), ("2/3", "4/6"), ("1/3", "2/6"),
                     ("3/5", "6/10"), ("2/5", "0.4"), ("3/4", "6/8"), ("1/2", "5/10"), ("3/10", "0.3"), ("4/5", "0.8"), ("1/4", "2/8"), ("9/10", "0.9")]
            lies = {"1/2": "0.2", "1/4": "0.4", "3/4": "0.34", "1/5": "0.5", "1/10": "0.01", "2/3": "2/6", "1/3": "0.3", "3/5": "0.35", "2/5": "0.25", "3/10": "0.03",
                    "4/5": "0.45", "9/10": "0.09"}
            spoken = lambda t: (fa_dec(t), t) if "." in t else (fa_frac(*map(int, t.split("/"))), t)  # noqa: E731
            for i, (a, b) in enumerate(rng.sample(forms, 16)):
                true = i % 2 == 0
                shown = b if true else lies[a]
                assert (Fraction(a) == Fraction(shown)) == true
                tf_row(s, "03", I_TRUE_CMP, f"t:{a} = {shown}", tr(f"{spoken(a)[0]} مساوی {spoken(shown)[0]} است", f"{spoken(a)[1]} is equal to {spoken(shown)[1]}"), true)
        B("03", equal)
    return s


PICTURES = {
    "sheep": "one white woolly sheep, side view",
    "hen": "one brown hen, side view",
    "apple": "one whole red apple with a small leaf",
    "egg": "one white egg",
    "bread": "one whole round flat naan bread seen from above",
    "goat": "one goat with small horns, side view",
    "flower": "one red flower on a short green stem",
    "fish": "one fish, side view",
    "cup": "one small tea bowl (piala) without handle",
    "star": "one yellow five-pointed star",
    "frog": "a green frog in mid-jump (icon of Number Hop)",
    "scales": "a two-pan market balance scale",
    "carpet": "a rectangular red Afghan carpet with a simple pattern, clearly longer than wide",
    "brick": "one clay brick",
    "potato": "one potato",
    "onion": "one onion",
    "pomegranate": "one red pomegranate",
    "walnut": "one walnut in its shell",
    "carrot": "one orange carrot with green top",
    "pencil": "one yellow pencil",
    "soap": "one bar of soap",
    "notebook": "one closed school notebook",
    "tea": "a glass of green tea",
    "milk": "a glass of milk",
    "salt": "a small bag of salt",
    "sugar": "a small bag of sugar",
    "rice": "a bowl of white rice",
    "flour_sack": "a large tied sack of flour",
    "rice_sack": "a large tied sack of rice with a few grains shown",
    "oil_can": "a yellow can of cooking oil",
    "shoes": "a pair of simple shoes",
    "blanket": "a folded blanket",
    "shape_circle": "a plain filled circle",
    "shape_square": "a plain filled square",
    "shape_triangle": "a plain filled triangle, point up",
    "shape_rectangle": "a plain filled rectangle, twice as wide as high",
    "shape_half_circle": "half of a circle: a filled half disc, the missing half as a dotted outline",
    "shape_quarter_circle": "a quarter of a circle: a filled quarter disc, the rest as a dotted outline",
    "ball": "a round ball, clearly a circle",
    "plate": "a round plate seen from above",
    "wheel": "a round cart wheel with spokes",
    "coin": "a round plain metal coin with no writing",
    "orange": "a round orange fruit",
    "sun": "a round yellow sun with no rays, or only very short ones",
    "button": "a round button with four holes",
    "window": "a square window with a wooden frame and four panes",
    "box": "a square box seen from the front",
    "handkerchief": "a square cloth handkerchief laid flat",
    "samosa": "a triangular fried samosa (sambosa)",
    "tent": "a triangular tent seen from the front",
    "mountain": "a single mountain peak drawn as a clear triangle with a snow cap",
    "door": "a rectangular wooden door, taller than wide",
    "book": "a closed rectangular book seen from the front",
    "watermelon": "a whole round watermelon",
    "watermelon_half": "half a watermelon, red cut side showing",
    "watermelon_quarter": "a quarter of a watermelon",
    "bread_half": "half of a round naan: a half disc, clean straight cut",
    "bread_quarter": "a quarter of a round naan: a quarter disc",
    "apple_half": "half an apple, cut side with seeds showing",
    "apple_quarter": "a quarter of an apple",
    "rope_long": "a long rope lying straight, filling the width of the picture",
    "rope_short": "a short rope lying straight, a third of the width of the picture",
    "pencil_long": "a long new pencil, filling the width of the picture",
    "pencil_short": "a short used pencil stub, a third of the width of the picture",
    "tree_tall": "a tall tree, filling the height of the picture",
    "tree_short": "a short small tree, half the height of the picture, standing on the same ground line",
    "stick_long": "a long straight wooden stick, filling the width of the picture",
    "stick_short": "a short straight wooden stick, a third of the width of the picture",
}
PICTURES.update({
    "basket": "an empty woven basket (icon of Number Rain)",
    "moon": "a crescent moon (icon of Days and Months)",
    "cow": "one cow, side view",
    "bread_third": "a third of a round naan: one of three equal wedges, drawn like bread_half and bread_quarter",
    "shape_third_circle": "a third of a circle: a filled third of a disc, the rest as a dotted outline",
})
for _n in (2, 3, 4, 5, 6, 8):
    for _k in range(1, _n):
        PICTURES[f"frac_{_k}_{_n}"] = (f"a circle cut into {_n} equal parts by lines from the centre, {_k} of them filled blue "
                                       f"(from the top, going left, as shape_quarter_circle does), the others white")
for _h in range(1, 13):
    PICTURES[f"clock_{_h}"] = (f"a round clock face with the numbers 1 to 12 in Western digits, the short hand pointing "
                              f"exactly at {_h} and the long hand at 12")
PICTURES.update({
    "yes": "a green tick (the basket for true)",
    "no": "a red cross (the basket for false)",
    "lamb": "one lamb, side view",
    "chick": "one yellow chick, side view",
    "tomato": "one red tomato",
    "note": "one plain green banknote with no writing, a clear rectangle",
    "orange_half": "half of a round orange: a half disc with the cut side and its segments showing (drawn by content/math/draw_pictures.py)",
    "orange_third": "a third of a round orange: one of three equal wedges (drawn by content/math/draw_pictures.py)",
    "orange_quarter": "a quarter of a round orange: a quarter disc (drawn by content/math/draw_pictures.py)",
    "pomegranate_half": "half of a round pomegranate: a half disc with red seeds showing (drawn by content/math/draw_pictures.py)",
    "pomegranate_third": "a third of a round pomegranate: one of three equal wedges (drawn by content/math/draw_pictures.py)",
    "pomegranate_quarter": "a quarter of a round pomegranate: a quarter disc (drawn by content/math/draw_pictures.py)",
})
for _name, _rows in CHARTS.items():
    _what = ", ".join(f"{_v} {_p}" for _p, _, _v in _rows)
    PICTURES[_name] = ((f"a block chart with three columns, a small picture under each column and one block per unit: {_what}"
                        if "bars" in _name else
                        f"a picture table with three rows read from the right: a small picture, then one dot per unit: {_what}")
                       + " (drawn by content/math/draw_pictures.py)")


# ---------------------------------------------------------------------------
# Level 6: percent, ratio, averages; profit and loss, a household budget,
# measuring liquids, scale on a map
# ---------------------------------------------------------------------------
#
# Percent is «فیصد» and written 25% in Western digits; a ratio is said «دو به
# سه» (a fraction is «دو بر سه») and written 2:3; the mean is «اوسط»; profit
# and loss «فایده» and «ضرر»; income and spending «عاید» and «مصرف»; saving
# «پس‌انداز»; the scale of a map «مقیاس».
#
# Measuring a dose is arithmetic about measuring only. No medicine is named,
# no amount is tied to an age or a weight, the amounts differ from question
# to question, and every such question and its help say that the amount comes
# from the health worker or the label (DOSE_RULE; check_answers6 asserts it).

PCT = "فیصد"
ML = "ملی" + Z + "لیتر"
KM = "کیلومتر"
L6_META: list[tuple[dict, object]] = []   # a row and a test that the finished row must pass
DOSE_ROWS: list[dict] = []                # every row that speaks of medicine
GRID_PCTS = [1, 5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 99, 100]   # the hundred squares that are drawn
CUP_MARKS = 6                             # the measuring cup that is drawn has six marks
DOSE_RULE = (tr("اندازه دوا را همیشه کارمند صحی یا نوشته روی بوتل می" + Z + "گوید، نه حساب ما.",
                "The amount of medicine always comes from the health worker or the writing on the bottle, never from our own sums."),
             "The amount of medicine always comes from the health worker or the writing on the bottle, never from our own sums.")
# A drawn map: three places on two straight roads, each road made of pieces
# that stand for one centimetre. Drawn from this list by draw_pictures.py.
MAPS6 = {
    "map_scale_1": ((("house", "خانه", "house"), ("well", "چاه", "well"), ("school", "مکتب", "school")), (3, 2)),
    "map_scale_2": ((("school", "مکتب", "school"), ("bridge", "پل", "bridge"), ("shop", "دکان", "shop")), (2, 4)),
    "map_scale_3": ((("tree", "درخت", "tree"), ("house", "خانه", "house"), ("clinic", "کلینیک", "clinic")), (4, 1)),
    "map_scale_4": ((("shop", "دکان", "shop"), ("school", "مکتب", "school"), ("well", "چاه", "well")), (1, 3)),
    "map_scale_5": ((("clinic", "کلینیک", "clinic"), ("tree", "درخت", "tree"), ("bridge", "پل", "bridge")), (4, 3)),
    "map_scale_6": ((("well", "چاه", "well"), ("shop", "دکان", "shop"), ("house", "خانه", "house")), (2, 1)),
}
CHARTS.update({
    "chart_bars_7": [("hen", "مرغ", 2), ("goat", "بز", 1), ("lamb", "بره", 3)],
    "chart_table_7": [("tomato", "بادنجان رومی", 1), ("potato", "کچالو", 3), ("onion", "پیاز", 2)],
    "chart_bars_8": [("walnut", "چهارمغز", 4), ("pomegranate", "انار", 3), ("orange", "مالته", 5)],
    "chart_table_8": [("pencil", "پنسل", 3), ("notebook", "کتابچه", 5), ("book", "کتاب", 4)],
})
CHART_EXTRA.update({"chart_bars_7": "cow", "chart_table_7": "carrot", "chart_bars_8": "apple", "chart_table_8": "ball"})
MEAN_CHARTS = [["chart_bars_2", "chart_bars_7", "chart_bars_8"], ["chart_table_1", "chart_table_7", "chart_table_8"],
               ["chart_bars_5", "chart_table_3", "chart_table_5"]]

_val5 = val


def val(thing: str):   # noqa: F811
    """As before, and the forms of level 6: a percent (t:25%), a ratio
    (t:2:3, the value of the first number over the second), a hundred square
    (pct_25)."""
    m = re.fullmatch(r"pct_(\d+)", thing)
    if m:
        return Fraction(int(m.group(1)), 100)
    if thing[:2] in ("t:", "f:"):
        body = "".join(str(DARI_DIGITS.index(c)) if c in DARI_DIGITS else c for c in thing[2:])
        m = re.fullmatch(r"(\d+)[%٪]", body)
        if m:
            return Fraction(int(m.group(1)), 100)
        m = re.fullmatch(r"(\d+):(\d+)", body)
        if m:
            return Fraction(int(m.group(1)), int(m.group(2)))
    return _val5(thing)


def P(n: int) -> str:
    """A percent tile."""
    assert 0 < n <= 100, n
    return f"t:{n}%"


def R(a: int, b: int) -> str:
    """A ratio tile."""
    return f"t:{a}:{b}"


def grid(n: int) -> str:
    """The picture of a hundred square with n squares coloured."""
    assert n in GRID_PCTS, n
    return f"pct_{n}"


def fa_pct(n: int) -> str:
    return f"{fa(n)} {PCT}"


def fa_ratio(a: int, b: int) -> str:
    return f"{fa(a)} به {fa(b)}"


def dec2(p: int) -> str:
    """A percent as a decimal with two places: 25 -> 0.25."""
    assert 0 < p < 100
    return f"0.{p:02d}"


def pct_frac(p: int) -> tuple[int, int]:
    f = Fraction(p, 100)
    return f.numerator, f.denominator


def fa_list(nums) -> tuple[str, str]:
    """'three, five and four' in both languages."""
    nums = list(nums)
    return "، ".join(fa(x) for x in nums[:-1]) + " و " + fa(nums[-1]), ", ".join(str(x) for x in nums[:-1]) + " and " + str(nums[-1])


def ask(say, en, ans, wrong, help_fa, help_en, show="", key=None):
    """One question of a level 6 pool, as a thing pick_even can spread. ans is
    a whole number (the wrong numbers are then typical mistakes that near()
    fills up) or a thing (the wrong things are candidates that pick_wrong sifts)."""
    if key is None:
        key = ans if isinstance(ans, int) else val(ans) if val(ans) is not None else ans
    if not isinstance(key, (int, Fraction, str)):
        key = repr(key)   # pick_even sorts numbers before names
    return (tr(say, en), ans, tuple(wrong), tr(help_fa, help_en), show, key)


def pool6(s, game, rnd, intro, parts, cap=2, dari=0, few=0, small="", lo=1):
    """A listen-and-pick round of level 6. parts: [(candidates, how many)];
    every dari-th numeric question gets Dari digits."""
    def gen(rng):
        picked = []
        for cands, n in parts:
            picked += pick_even(cands, n, rng, key=lambda c: c[5], cap=cap)
        rng.shuffle(picked)
        for i, (say, ans, wrong, help_fa, show, _) in enumerate(picked):
            if isinstance(ans, int):
                sc = "D" if dari and i % dari == dari - 1 else "W"
                prefer = [w for w in wrong if isinstance(w, int) and w >= lo]
                wr = near(ans, rng, lo, 10_000_000, prefer)
                row = lp(s, rnd, intro, say, num(ans, sc), [num(x, sc) for x in wr], show=show, help_fa=help_fa)
                CHECK_META.append((row, Fraction(ans)))
            elif val(ans) is not None:
                lp(s, rnd, intro, say, ans, pick_wrong(ans, wrong), show=show, help_fa=help_fa, truth=lambda c, a=ans: val(c) == val(a))
            else:
                wr = [w for w in uniq(wrong) if w != ans][:3]
                lp(s, rnd, intro, say, ans, wr, show=show, help_fa=help_fa, truth=lambda c, a=ans: c == a)
    build(s, 6, game, rnd, gen, few=few, small=small)


def pct_of(p: int, n: int) -> tuple[str, str, int]:
    """The spoken way to p percent of n, and the result."""
    assert (p * n) % 100 == 0, (p, n)
    r = p * n // 100
    if p == 100:
        return f"صد {PCT} یعنی همه. جواب {fa(n)} است.", f"100 percent means all of it. The answer is {n}.", r
    if p == 50:
        return f"پنجاه {PCT} یعنی نیم. نیم {fa(n)}، {fa(r)} است.", f"50 percent means half. Half of {n} is {r}.", r
    if p == 25:
        return (f"بیست و پنج {PCT} یعنی چارک. {fa(n)} تقسیم چهار مساوی {fa(r)}.",
                f"25 percent means a quarter. {n} divided by 4 equals {r}.", r)
    if p == 75:
        q = n // 4
        return (f"هفتاد و پنج {PCT} یعنی سه چارک. چارک {fa(n)}، {fa(q)} است. سه ضرب {fa(q)} مساوی {fa(r)}.",
                f"75 percent means three quarters. A quarter of {n} is {q}. 3 times {q} equals {r}.", r)
    if p == 10:
        return (f"ده {PCT} یعنی یک حصه از ده حصه. {fa(n)} تقسیم ده مساوی {fa(r)}.",
                f"10 percent means one part out of 10. {n} divided by 10 equals {r}.", r)
    if p == 20:
        return (f"بیست {PCT} یعنی یک حصه از پنج حصه. {fa(n)} تقسیم پنج مساوی {fa(r)}.",
                f"20 percent means one part out of 5. {n} divided by 5 equals {r}.", r)
    if p % 10 == 0 and n % 10 == 0:
        t = n // 10
        return (f"اول ده {PCT}: {fa(n)} تقسیم ده مساوی {fa(t)}. {fa_pct(p)}، {fa(p // 10)} تا ده {PCT} است: {fa(p // 10)} ضرب {fa(t)} مساوی {fa(r)}.",
                f"First 10 percent: {n} divided by 10 equals {t}. {p} percent is {p // 10} times 10 percent: {p // 10} times {t} equals {r}.", r)
    assert p % 20 == 0 and n % 5 == 0, (p, n)
    u = n // 5
    return (f"اول بیست {PCT}: {fa(n)} تقسیم پنج مساوی {fa(u)}. {fa_pct(p)}، {fa(p // 20)} تا بیست {PCT} است: {fa(p // 20)} ضرب {fa(u)} مساوی {fa(r)}.",
            f"First 20 percent: {n} divided by 5 equals {u}. {p} percent is {p // 20} times 20 percent: {p // 20} times {u} equals {r}.", r)


def pct_wrong(p: int, n: int) -> list[int]:
    """What children typically answer instead of p percent of n."""
    r = p * n // 100
    return [n - p if n > p else None, p if p != r else None, n // p if n % p == 0 else None, r * 10, r // 10 if r % 10 == 0 else None, n - r if n != 2 * r else None]


def near_pcts(n: int) -> list[str]:
    """Percent tiles that could be taken for n percent."""
    xs = [100 - n, n + 10, n - 10, n * 10, n // 10 if n % 10 == 0 else 0, n + 5, n - 5, n + 20, n - 20, n + 1, n - 1, 50, 25]
    return [P(x) for x in uniq(xs) if 0 < x <= 100 and x != n]


# -- Count the Flock: what a percent is ---------------------------------------

I_PCT_GRID = tr("صد خانه را ببین. فیصد یعنی «از صد»: خانه" + Z + "های رنگ" + Z + "شده را بشمار.",
                "Look at the hundred squares. Percent means \"out of a hundred\": count the coloured squares.")
I_PCT_HEAR = tr("فیصد یعنی از صد. گوش کن و فیصد را پیدا کن.", "Percent means out of a hundred. Listen and find the percent.")
I_PCT_FRAC = tr("هر فیصد یک کسر است. فیصد و کسر مساوی آن را پیدا کن.", "Every percent is a fraction. Find the percent and the fraction equal to it.")
I_PCT_DEC = tr("هر فیصد یک عدد اعشاری است. فیصد و عدد اعشاری مساوی آن را پیدا کن.", "Every percent is a decimal number. Find the percent and the decimal number equal to it.")
I_PCT_GROUP = tr("بشمار و فیصد دسته را حساب کن.", "Count and work out the percent of the group.")
I_PCT_OUTOF = tr("چند از چند؟ فیصد آن را پیدا کن.", "How many out of how many? Find its percent.")

# "k out of a hundred": the sentence, with its English, for round 2
HUNDRED_STORIES = [
    (lambda k: f"از صد گوسفند رمه، {fa(k)} گوسفند سیاه است. چند {PCT} رمه سیاه است؟", lambda k: f"Out of the 100 sheep of the flock, {k} are black. What percent of the flock is black?"),
    (lambda k: f"در قریه صد خانه است. {fa(k)} خانه چاه دارد. چند {PCT} خانه{Z}ها چاه دارند؟", lambda k: f"There are 100 houses in the village. {k} have a well. What percent of the houses have a well?"),
    (lambda k: f"در مکتب صد شاگرد است. {fa(k)} نفر آنها دختر هستند. چند {PCT} شاگردان دختر هستند؟", lambda k: f"There are 100 pupils in the school. {k} of them are girls. What percent of the pupils are girls?"),
    (lambda k: f"دهقان صد نهال شاند. {fa(k)} نهال سبز شد. چند {PCT} نهال{Z}ها سبز شد؟", lambda k: f"The farmer planted 100 saplings. {k} grew. What percent of the saplings grew?"),
    (lambda k: f"صد افغانی داشتی و {fa(k)} افغانی را خرج کردی. چند {PCT} پولت را خرج کردی؟", lambda k: f"You had 100 afghani and spent {k} afghani. What percent of your money did you spend?"),
    (lambda k: f"در مکتب صد شاگرد است. {fa(k)} نفر آنها بچه هستند. چند {PCT} شاگردان بچه هستند؟", lambda k: f"There are 100 pupils in the school. {k} of them are boys. What percent of the pupils are boys?"),
]
# "k out of m": Dari, English, and whether the story makes sense with these numbers
def _isare(k: int) -> str:
    return "is" if k == 1 else "are"


_few = lambda m, k: 2 * k <= m          # noqa: E731  (a small part: what broke, who stayed at home)
_class = lambda m, k: m >= 20 and 3 * m <= 10 * k <= 7 * m   # noqa: E731  (girls and boys of one class)
OUTOF_STORIES = [
    (lambda m, k: f"از {fa(m)} سیب، {fa(k)} سیب خراب است. چند {PCT} سیب{Z}ها خراب است؟", lambda m, k: f"Out of {m} apples, {k} went bad. What percent of the apples went bad?", _few),
    (lambda m, k: f"در صنف {fa(m)} شاگرد است. {fa(k)} نفر امروز نیامده است. چند {PCT} شاگردان نیامده است؟", lambda m, k: f"There are {m} pupils in the class. {k} did not come today. What percent of the pupils did not come?", lambda m, k: m >= 20 and 4 * k <= m),
    (lambda m, k: f"مرغ{Z}ها {fa(m)} تخم دادند. {fa(k)} تخم شکست. چند {PCT} تخم{Z}ها شکست؟", lambda m, k: f"The hens laid {m} eggs. {k} broke. What percent of the eggs broke?", _few),
    (lambda m, k: f"از {fa(m)} درخت باغ، {fa(k)} درخت چهارمغز است. چند {PCT} درخت{Z}ها چهارمغز است؟", lambda m, k: f"Out of the {m} trees of the garden, {k} {_isare(k)} walnut. What percent of the trees are walnut trees?", lambda m, k: True),
    (lambda m, k: f"{fa(m)} افغانی داشتی. {fa(k)} افغانی را پس{Z}انداز کردی. چند {PCT} پولت را پس{Z}انداز کردی؟", lambda m, k: f"You had {m} afghani. You saved {k} afghani. What percent of your money did you save?", lambda m, k: True),
    (lambda m, k: f"در صنف {fa(m)} شاگرد است و {fa(k)} نفر آنها دختر هستند. چند {PCT} صنف دختر است؟", lambda m, k: f"There are {m} pupils in the class and {k} of them are girls. What percent of the class are girls?", _class),
    (lambda m, k: f"در صنف {fa(m)} شاگرد است و {fa(k)} نفر آنها بچه هستند. چند {PCT} صنف بچه است؟", lambda m, k: f"There are {m} pupils in the class and {k} of them are boys. What percent of the class are boys?", _class),
    (lambda m, k: f"از {fa(m)} گوسفند، {fa(k)} گوسفند سفید است. چند {PCT} گوسفندها سفید است؟", lambda m, k: f"Out of {m} sheep, {k} {_isare(k)} white. What percent of the sheep are white?", lambda m, k: True),
]


def flock6(level: int) -> Sheet:
    s = Sheet(LP_COLS)
    means = (f"{PCT} یعنی از صد.", "Percent means out of a hundred.")

    # 01: the hundred square
    coloured = [("چند {P} این شکل رنگ شده است؟", "What percent of this picture is coloured?"),
                ("از صد خانه چند خانه رنگ شده است؟ {P} آن را پیدا کن.", "How many squares out of a hundred are coloured? Find the percent."),
                ("خانه" + Z + "های رنگ" + Z + "شده را ده ده بشمار. چند {P} است؟", "Count the coloured squares in tens. What percent is it?")]
    white = [("چند {P} این شکل سفید مانده است؟", "What percent of this picture is still white?"),
             ("خانه" + Z + "های سفید چند {P} شکل است؟", "What percent of the picture are the white squares?")]
    c1 = []
    for i, n in enumerate(GRID_PCTS):
        d, e = coloured[i % 3]
        c1.append(ask(d.format(P=PCT), e, P(n), near_pcts(n), f"{means[0]} از صد خانه، {fa(n)} خانه رنگ شده است: {fa_pct(n)}.",
                      f"{means[1]} Out of 100 squares, {n} {'is' if n == 1 else 'are'} coloured: {n} percent.", show=grid(n)))
        if n < 100:
            d, e = white[i % 2]
            c1.append(ask(d.format(P=PCT), e, P(100 - n), near_pcts(100 - n),
                          f"{fa(n)} خانه رنگ شده است. صد منفی {fa(n)} مساوی {fa(100 - n)}. {fa_pct(100 - n)} سفید است.",
                          f"{n} {'square is' if n == 1 else 'squares are'} coloured. 100 minus {n} equals {100 - n}. {100 - n} percent is white.", show=grid(n)))
    pool6(s, "flock", "01", I_PCT_GRID, [(c1, N)])

    # 02: hearing "out of a hundred"
    plain, back, pics, told = [], [], [], []
    for i, k in enumerate([3, 7, 12, 18, 33, 45, 55, 64, 72, 88, 96, 100]):
        d, e = [("{k} از صد، چند {P} است؟", "{k} out of 100 is what percent?"), ("از هر صد تا، {k} تا. این چند {P} است؟", "{k} out of every 100. What percent is this?")][i % 2]
        plain.append(ask(d.format(k=fa(k), P=PCT), e.format(k=k), P(k), near_pcts(k), f"{means[0]} {fa(k)} از صد، {fa_pct(k)} است.", f"{means[1]} {k} out of 100 is {k} percent."))
    for i, k in enumerate([4, 15, 27, 36, 48, 65, 85, 92]):
        d, e = [("{p} یعنی چند از صد؟", "{k} percent means how many out of 100?"), ("اگر {p} صد خانه را رنگ کنیم، چند خانه رنگ می" + Z + "شود؟", "If we colour {k} percent of 100 squares, how many squares are coloured?")][i % 2]
        back.append(ask(d.format(p=fa_pct(k)), e.format(k=k), k, [100 - k, k // 10 if k >= 10 else k * 10, k + 10], f"{means[0]} {fa_pct(k)} یعنی {fa(k)} از صد.", f"{means[1]} {k} percent means {k} out of 100."))
    for i, n in enumerate(GRID_PCTS):
        j = GRID_PCTS.index(n)
        others = [grid(100 - n)] if 100 - n in GRID_PCTS and n != 50 else []
        others += [grid(GRID_PCTS[(j + d) % len(GRID_PCTS)]) for d in (1, -1, 2, -2, 3)]
        d, e = [("کدام شکل {p} را نشان می" + Z + "دهد؟", "Which picture shows {n} percent?"), ("در کدام شکل {p} خانه" + Z + "ها رنگ شده است؟", "In which picture are {n} percent of the squares coloured?")][i % 2]
        pics.append(ask(d.format(p=fa_pct(n)), e.format(n=n), grid(n), others, f"{fa_pct(n)} یعنی از صد خانه، {fa(n)} خانه رنگ شده است.", f"{n} percent means that out of 100 squares, {n} {'is' if n == 1 else 'are'} coloured."))
    for i, k in enumerate([8, 14, 21, 26, 35, 42, 52, 58, 61, 68, 77, 83, 91, 94]):
        d, e = HUNDRED_STORIES[i % len(HUNDRED_STORIES)]
        told.append(ask(d(k), e(k), P(k), near_pcts(k), f"{means[0]} {fa(k)} از صد، {fa_pct(k)} است.", f"{means[1]} {k} out of 100 is {k} percent."))
    pool6(s, "flock", "02", I_PCT_HEAR, [(plain, 4), (back, 3), (pics, 5), (told, 6)])

    # 03: percent and fraction
    c3 = []
    base = [50, 25, 75, 10, 20, 30, 40, 60, 70, 80, 90, 5, 1]
    for i, p in enumerate(base):
        k, n = pct_frac(p)
        others = [fr(*pct_frac(q)) for q in base[i + 1:] + base[:i]]
        wrong = ([fr(1, p)] if 2 <= p <= 100 else []) + [fr(n, k) if k > 1 else fr(k, n * 10)] + others
        if (k, n) == (p, 100):
            help_pair = (f"{fa_pct(p)} یعنی {fa_frac(p, 100)}.", f"{p} percent means {p}/100.")
        else:
            help_pair = (f"{fa_pct(p)} یعنی {fa_frac(p, 100)}. صورت و مخرج را بر {fa(100 // n)} تقسیم کن: {fa_frac(k, n)}.",
                         f"{p} percent means {p}/100. Divide the numerator and the denominator by {100 // n}: {k}/{n}.")
        c3.append(ask(f"{fa_pct(p)} مساوی کدام کسر است؟", f"{p} percent is equal to which fraction?", fr(k, n), wrong, *help_pair))
        f = 100 // n
        back_help = ((f"{fa_frac(k, n)} یعنی {fa(k)} از صد: {fa_pct(p)}.", f"{k}/{n} means {k} out of 100: {p} percent.") if n == 100 else
                     (f"مخرج را به صد برسان: {fa(n)} ضرب {fa(f)} مساوی صد. صورت را هم در {fa(f)} ضرب کن: {fa(k * f)}. {fa(k * f)} از صد، {fa_pct(p)} است.",
                      f"Bring the denominator to 100: {n} times {f} equals 100. Multiply the numerator by {f} too: {k * f}. {k * f} out of 100 is {p} percent."))
        c3.append(ask(f"{fa_frac(k, n)} چند {PCT} است؟", f"{k}/{n} is what percent?", P(p), [P(n)] + ([P(k * 10)] if k * 10 <= 100 else []) + near_pcts(p), *back_help))
    for word, en, p in (("نیم", "A half", 50), ("چارک", "A quarter", 25), ("سه چارک", "Three quarters", 75)):
        k, n = pct_frac(p)
        c3.append(ask(f"{word} یعنی چند {PCT}؟", f"{en} means what percent?", P(p), near_pcts(p),
                      f"{word} یعنی {fa_frac(k, n)}. {fa_frac(k, n)} مساوی {fa_frac(p, 100)} است: {fa_pct(p)}.", f"{en} means {k}/{n}. {k}/{n} is equal to {p}/100: {p} percent.",
                      key=("word", p)))
    c3.append(ask(f"همه، یعنی یک پوره، چند {PCT} است؟", "All of it, one whole, is what percent?", P(100), near_pcts(100),
                  f"یک پوره یعنی صد از صد: صد {PCT}.", "One whole means 100 out of 100: 100 percent."))
    pool6(s, "flock", "03", I_PCT_FRAC, [(c3, N)])

    # 04: percent and decimal
    c4 = []
    for i, p in enumerate([50, 25, 75, 10, 20, 30, 40, 60, 70, 80, 90, 5, 1, 15, 35, 45, 65, 95]):
        d = dec2(p)
        wrong = [f"t:{p // 10}.{p % 10}", f"t:{p}.0", "t:" + dec2(100 - p), "t:0.0" + str(p)[0], "t:" + dec2(p + 10 if p < 90 else p - 10), "t:" + dec2(p + 1)]
        if i % 2 == 0:
            c4.append(ask(f"{fa_pct(p)} با عدد اعشاری کدام است؟", f"Which one is {p} percent as a decimal number?", "t:" + d, wrong,
                          f"{fa_pct(p)} یعنی {fa_frac(p, 100)}. این را {fa_dec(d)} می{Z}نویسیم.", f"{p} percent means {p}/100. We write this as {d}."))
        else:
            c4.append(ask(f"{fa_dec(d)} چند {PCT} است؟", f"{d} is what percent?", P(p), ([P(p * 10)] if p * 10 <= 100 else []) + ([P(p // 10)] if p % 10 == 0 else []) + near_pcts(p),
                          f"{fa_dec(d)} یعنی {fa_frac(p, 100)}: {fa(p)} از صد. جواب {fa_pct(p)} است.", f"{d} means {p}/100: {p} out of 100. The answer is {p} percent."))
    for p in (2, 8, 12, 24, 33, 55, 66, 85, 99):
        c4.append(ask(f"{fa(p)} پول چند {PCT} یک {AFN} است؟", f"{p} pul is what percent of 1 afghani?", P(p), near_pcts(p),
                      f"یک {AFN} صد پول است. {fa(p)} از صد، {fa_pct(p)} است.", f"1 afghani is 100 pul. {p} out of 100 is {p} percent."))
    pool6(s, "flock", "04", I_PCT_DEC, [(c4[:18], 12), (c4[18:], 6)])

    # 05: a percent of things you can count
    combos = [(n, p) for n in (4, 8, 12, 16) for p in (25, 50, 75)] + [(4, 100), (20, 25), (20, 75), (20, 50)] + \
             [(10, p) for p in range(10, 101, 10)] + [(20, p) for p in (10, 20, 30, 40, 60, 70, 80, 90)] + [(5, p) for p in (20, 40, 60, 80, 100)] + [(15, 20), (15, 40), (15, 60)]
    c5 = []
    for i, (n, p) in enumerate(combos):
        pic, noun = COUNT_OBJS[(i * 5) % len(COUNT_OBJS)]
        d, e, r = pct_of(p, n)
        say = [(f"اینجا {fa(n)} {noun} است. {fa_pct(p)} آنها چند {noun} است؟", f"Here are {cnt(n, noun)}. How many {many(noun)} is {p} percent of them?"),
               (f"{fa_pct(p)} این {fa(n)} {noun} چند تا می{Z}شود؟", f"How many is {p} percent of these {cnt(n, noun)}?")][i % 2]
        c5.append(ask(say[0], say[1], r, [n - r if n != 2 * r else None, r + 1, r - 1, n], d, e, show=f"p:{pic}*{n}"))
    pool6(s, "flock", "05", I_PCT_GROUP, [(c5, N)], dari=4)

    # 06: k out of m as a percent
    c6 = []
    i = 0
    for m in (4, 5, 10, 20, 25, 50):
        f = 100 // m
        for k in range(1, m):
            p = k * f
            if m in (20, 25, 50) and p % 10 and p % 25 and (k * 7 + m) % 3:
                continue   # not every one of the many odd percents
            while not OUTOF_STORIES[i % len(OUTOF_STORIES)][2](m, k):   # the next story that fits these numbers
                i += 1
            d, e, _ = OUTOF_STORIES[i % len(OUTOF_STORIES)]
            i += 1
            c6.append(ask(d(m, k), e(m, k), P(p), [P(k)] + ([P(m)] if m != p else []) + near_pcts(p),
                          f"{fa(m)} ضرب {fa(f)} مساوی صد. پس {fa(k)} را هم در {fa(f)} ضرب کن: {fa(p)}. {fa(k)} از {fa(m)}، {fa_pct(p)} است.",
                          f"{m} times {f} equals 100. So multiply {k} by {f} too: {p}. {k} out of {m} is {p} percent."))
    pool6(s, "flock", "06", I_PCT_OUTOF, [(c6, N)])
    return s


# -- Number Hop: percent of an amount, averages, profit and loss, a budget ------

I_TEN_PCT = tr("ده فیصد یعنی یک حصه از ده حصه: بر ده تقسیم کن.", "10 percent means one part out of 10: divide by 10.")
I_HALF_PCT = tr("پنجاه فیصد یعنی نیم و بیست و پنج فیصد یعنی چارک.", "50 percent means half and 25 percent means a quarter.")
I_MORE_PCT = tr("هفتاد و پنج فیصد یعنی سه چارک. فیصدهای بزرگ را حساب کن.", "75 percent means three quarters. Work out the big percents.")
I_PCT_STORY = tr("قصه را گوش کن و فیصد را حساب کن.", "Listen to the story and work out the percent.")
I_DISCOUNT = tr("تخفیف یعنی قیمت کم می" + Z + "شود. تخفیف و قیمت نو را حساب کن.", "A discount means the price goes down. Work out the discount and the new price.")
I_GROW = tr("چیزی چند فیصد زیاد شده است. حساب کن که حالا چند است.", "Something has grown by some percent. Work out how much it is now.")
I_MEAN = tr("اوسط یعنی اگر همه را برابر تقسیم کنیم، به هر کدام چند می" + Z + "رسد. جمع کن و تقسیم کن.",
            "The average means: if we share everything out evenly, how much does each one get? Add and divide.")
I_MEAN_STORY = tr("قصه را گوش کن و اوسط را حساب کن.", "Listen to the story and work out the average.")
I_PROFIT = tr("فایده یا ضرر؟ قیمت خرید و قیمت فروش را مقایسه کن.", "Profit or loss? Compare the buying price and the selling price.")
I_BUDGET = tr("عاید، مصرف و پس" + Z + "انداز یک خانواده را حساب کن.", "Work out the income, the spending and the saving of a family.")

PCT_GROUPS = [   # (Dari, English) of n and p; the answer is p percent of n
    (lambda n, p: f"در مکتب {fa(n)} شاگرد است. {fa_pct(p)} آنها دختر هستند. چند دختر در مکتب است؟", lambda n, p: f"There are {n} pupils in the school. {p} percent of them are girls. How many girls are in the school?"),
    (lambda n, p: f"در رمه {fa(n)} گوسفند است. {fa_pct(p)} آنها بره دارند. چند گوسفند بره دارد؟", lambda n, p: f"There are {n} sheep in the flock. {p} percent of them have a lamb. How many sheep have a lamb?"),
    (lambda n, p: f"دهقان {fa(n)} کیلو گندم درو کرد. {fa_pct(p)} آن را برای تخم نگه می{Z}دارد. چند کیلو را نگه می{Z}دارد؟", lambda n, p: f"The farmer harvested {n} kilos of wheat. {p} percent of it is kept for seed. How many kilos are kept?"),
    (lambda n, p: f"در باغ {fa(n)} درخت است. {fa_pct(p)} آنها درخت سیب است. چند درخت سیب در باغ است؟", lambda n, p: f"There are {n} trees in the garden. {p} percent of them are apple trees. How many apple trees are in the garden?"),
    (lambda n, p: f"در مکتب {fa(n)} شاگرد است. {fa_pct(p)} آنها بچه هستند. چند بچه در مکتب است؟", lambda n, p: f"There are {n} pupils in the school. {p} percent of them are boys. How many boys are in the school?"),
    (lambda n, p: f"در قریه {fa(n)} خانه است. {fa_pct(p)} خانه{Z}ها باغچه دارند. چند خانه باغچه دارد؟", lambda n, p: f"There are {n} houses in the village. {p} percent of the houses have a small garden. How many houses have a garden?"),
    (lambda n, p: f"یک خانواده {fa(n)} {AFN} عاید دارد. {fa_pct(p)} آن را پس{Z}انداز می{Z}کند. چند {AFN} پس{Z}انداز می{Z}کند؟", lambda n, p: f"A family has an income of {n} afghani. It saves {p} percent of it. How many afghani does it save?"),
    (lambda n, p: f"راه قریه تا بازار {fa(n)} دقیقه است. {fa_pct(p)} راه را رفته{Z}ای. چند دقیقه راه رفته{Z}ای؟", lambda n, p: f"The way from the village to the bazaar takes {n} minutes. You have gone {p} percent of the way. How many minutes have you walked?"),
]
SALE_GOODS = [("کمپل", "blanket"), ("جوره بوت", "pair of shoes"), ("قالینچه", "small carpet"), ("بوری آرد", "sack of flour"), ("چادر", "headscarf"), ("بکس مکتب", "school bag"),
              ("دیگ", "pot"), ("چراغ", "lamp")]
GROW_STORIES = [
    (lambda b, p: f"پارسال در مکتب {fa(b)} شاگرد بود. امسال {fa_pct(p)} زیادتر شده است. امسال چند شاگرد است؟", lambda b, p: f"Last year there were {b} pupils in the school. This year there are {p} percent more. How many pupils are there this year?"),
    (lambda b, p: f"پارسال رمه {fa(b)} گوسفند داشت. امسال {fa_pct(p)} زیادتر شده است. حالا رمه چند گوسفند دارد؟", lambda b, p: f"Last year the flock had {b} sheep. This year it has grown by {p} percent. How many sheep does the flock have now?"),
    (lambda b, p: f"یک بوری برنج {fa(b)} {AFN} بود. قیمت آن {fa_pct(p)} بالا رفت. حالا چند {AFN} است؟", lambda b, p: f"A sack of rice was {b} afghani. Its price went up by {p} percent. How many afghani is it now?"),
    (lambda b, p: f"پارسال دهقان {fa(b)} کیلو کچالو گرفت. امسال حاصل {fa_pct(p)} بیشتر شد. امسال چند کیلو گرفت؟", lambda b, p: f"Last year the farmer got {b} kilos of potatoes. This year the harvest was {p} percent bigger. How many kilos did the farmer get this year?"),
    (lambda b, p: f"یک زن قالین{Z}باف هر ماه {fa(b)} {AFN} مزد می{Z}گرفت. مزد او {fa_pct(p)} زیاد شد. حالا چند {AFN} می{Z}گیرد؟", lambda b, p: f"A woman who weaves carpets earned {b} afghani a month. Her pay went up by {p} percent. How many afghani does she earn now?"),
    (lambda b, p: f"در کتابخانه مکتب {fa(b)} کتاب بود. امسال {fa_pct(p)} زیادتر شد. حالا چند کتاب است؟", lambda b, p: f"There were {b} books in the school library. This year there are {p} percent more. How many books are there now?"),
]
# Averages told as stories: Dari and English of (how many numbers, the list said aloud), and the range of the numbers.
MEAN_STORIES = [
    (lambda k, d: f"مرغ{Z}ها در {fa(k)} روز {d} تخم دادند. اوسط هر روز چند تخم دادند؟", lambda k, e: f"In {k} days the hens laid {e} eggs. How many eggs did they lay a day on average?", 2, 9),
    (lambda k, d: f"یک دختر در {fa(k)} امتحان این نمره{Z}ها را گرفت: {d}. اوسط نمره او چند است؟", lambda k, e: f"A girl got these marks in {k} tests: {e}. What is her average mark?", 5, 10),
    (lambda k, d: f"یک بچه در {fa(k)} روز {d} صفحه کتاب خواند. اوسط هر روز چند صفحه خواند؟", lambda k, e: f"In {k} days a boy read {e} pages of a book. How many pages did he read a day on average?", 4, 16),
    (lambda k, d: f"در {fa(k)} روز {d} مشتری به دکان آمد. اوسط هر روز چند مشتری آمد؟", lambda k, e: f"In {k} days {e} customers came to the shop. How many customers came a day on average?", 6, 20),
    (lambda k, d: f"{fa(k)} دختر {d} چهارمغز جمع کردند. اگر همه را یکجا کنند و برابر تقسیم کنند، به هر دختر چند چهارمغز می{Z}رسد؟",
     lambda k, e: f"{k} girls gathered {e} walnuts. If they put them all together and share them out evenly, how many walnuts does each girl get?", 3, 15),
    (lambda k, d: f"گاو در {fa(k)} روز {d} لیتر شیر داد. اوسط هر روز چند لیتر شیر داد؟", lambda k, e: f"In {k} days the cow gave {e} litres of milk. How many litres of milk did it give a day on average?", 4, 12),
    (lambda k, d: f"{fa(k)} بچه {d} سیب چیدند. اگر همه را یکجا کنند و برابر تقسیم کنند، به هر بچه چند سیب می{Z}رسد؟",
     lambda k, e: f"{k} boys picked {e} apples. If they put them all together and share them out evenly, how many apples does each boy get?", 3, 15),
    (lambda k, d: f"یک بچه در {fa(k)} امتحان این نمره{Z}ها را گرفت: {d}. اوسط نمره او چند است؟", lambda k, e: f"A boy got these marks in {k} tests: {e}. What is his average mark?", 5, 10),
    (lambda k, d: f"یک دختر در {fa(k)} روز {d} دقیقه تا مکتب راه رفت. اوسط هر روز چند دقیقه راه رفت؟", lambda k, e: f"On {k} days a girl walked {e} minutes to school. How many minutes did she walk a day on average?", 10, 30),
]
TRADERS = [("دکاندار", "The shopkeeper"), ("یک زن", "A woman"), ("دهقان", "The farmer"), ("یک دختر", "A girl"), ("یک مرد", "A man"), ("یک بچه", "A boy")]
TRADE_GOODS = [   # Dari, English, the buying prices
    ("یک مرغ", "a hen", range(200, 401, 10)), ("یک صندوق انار", "a box of pomegranates", range(300, 901, 50)), ("ده کیلو کچالو", "10 kilos of potatoes", range(150, 401, 10)),
    ("یک کمپل", "a blanket", range(400, 901, 50)), ("یک جوره بوت", "a pair of shoes", range(300, 801, 50)), ("یک بز", "a goat", range(3000, 6001, 500)),
    ("یک سبد تخم", "a basket of eggs", range(100, 301, 10)), ("یک بوری پیاز", "a sack of onions", range(250, 601, 50)),
]


def mean_help(nums) -> tuple[str, str]:
    total, k = sum(nums), len(nums)
    return (" جمع ".join(fa(x) for x in nums) + f" مساوی {fa(total)}. {fa(k)} عدد است، پس {fa(total)} تقسیم {fa(k)} مساوی {fa(total // k)}.",
            " plus ".join(str(x) for x in nums) + f" equals {total}. There are {k} numbers, so {total} divided by {k} equals {total // k}.")


def mean_lists(tag, k: int, lo: int, hi: int, how_many: int) -> list[tuple]:
    """Lists of k numbers from lo..hi whose mean is a whole number, not all the same."""
    rng = rng_for("mean", tag, k, lo, hi)
    out = []
    while len(out) < how_many:
        nums = [rng.randint(lo, hi) for _ in range(k - 1)]
        m = rng.randint(lo + 1, hi - 1)
        last = k * m - sum(nums)
        if lo <= last <= hi and len(set(nums + [last])) > 1 and tuple(nums + [last]) not in out:
            out.append(tuple(nums + [last]))
    return out


def hop6(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    def amount(p, a, i):
        d, e, r = pct_of(p, a)
        say = [(f"{fa_pct(p)} {fa(a)} {AFN} چند {AFN} است؟", f"How many afghani is {p} percent of {a} afghani?"),
               (f"{fa_pct(p)} {fa(a)} چند می{Z}شود؟", f"{p} percent of {a} makes how many?"),
               (f"{fa(a)} کیلو گندم داری. {fa_pct(p)} آن چند کیلو است؟", f"You have {a} kilos of wheat. How many kilos is {p} percent of it?"),
               (f"از {fa(a)} {AFN}، {fa_pct(p)} را جدا کن. چند {AFN} می{Z}شود؟", f"Set aside {p} percent of {a} afghani. How many afghani is that?")][i % 4]
        return ask(say[0], say[1], r, pct_wrong(p, a), d, e)

    ten = [amount(10, a, i) for i, a in enumerate(range(30, 901, 10)) if a != 100]
    tens = [amount(p, a, i) for i, (p, a) in enumerate((p, a) for a in range(50, 501, 50) for p in (20, 30, 40))]
    pool6(s, "hop", "01", I_TEN_PCT, [(ten, 12), (tens, 6)], cap=1)
    half = [amount(50, a, i) for i, a in enumerate(list(range(30, 200, 2)) + list(range(200, 2001, 50)))]
    quarter = [amount(25, a, i + 1) for i, a in enumerate(list(range(20, 200, 4)) + list(range(200, 1001, 40)))]
    pool6(s, "hop", "02", I_HALF_PCT, [(half, 9), (quarter, 9)], cap=1)
    three = [amount(75, a, i) for i, a in enumerate(list(range(20, 201, 4)) + list(range(240, 801, 40)))]
    whole = [amount(100, a, i + 1) for i, a in enumerate((35, 80, 125, 260, 450, 990))]
    big = [amount(p, a, i + 2) for i, (p, a) in enumerate((p, a) for a in range(20, 301, 10) for p in (60, 70, 80, 90))]
    pool6(s, "hop", "03", I_MORE_PCT, [(three, 9), (whole, 2), (big, 7)], cap=1)

    groups = []
    combos = [(n, p) for n in (40, 60, 80, 120, 160, 200, 240, 300, 360, 400, 500, 600) for p in (10, 20, 25, 50, 75)]
    for i, (n, p) in enumerate(combos):
        if i % 8 == 7 and n > 120:
            continue   # a walk of more than two hours is not a walk to the bazaar
        d, e = PCT_GROUPS[i % len(PCT_GROUPS)]
        hd, he, r = pct_of(p, n)
        groups.append(ask(d(n, p), e(n, p), r, pct_wrong(p, n), hd, he))
    pool6(s, "hop", "04", I_PCT_STORY, [(groups, N)], cap=1)

    new_price, off = [], []
    for i, (price, p) in enumerate((price, p) for price in range(200, 2001, 100) for p in (10, 20, 25, 50)):
        noun, en = SALE_GOODS[i % len(SALE_GOODS)]
        hd, he, r = pct_of(p, price)
        first = (f"قیمت یک {noun} {fa(price)} {AFN} است. دکاندار {fa_pct(p)} تخفیف می{Z}دهد.", f"The price of a {en} is {price} afghani. The shopkeeper gives a discount of {p} percent.")
        new_price.append(ask(f"{first[0]} حالا {noun} چند {AFN} است؟", f"{first[1]} How many afghani is the {en} now?", price - r, [r, price + r, price - p, price - r + 10],
                             f"{hd} این تخفیف است. {fa(price)} منفی {fa(r)} مساوی {fa(price - r)}.", f"{he} This is the discount. {price} minus {r} equals {price - r}."))
        off.append(ask(f"{first[0]} تخفیف چند {AFN} است؟", f"{first[1]} How many afghani is the discount?", r, [price - r, p, r * 2, r + 10], hd, he))
    pool6(s, "hop", "05", I_DISCOUNT, [(new_price, 12), (off, 6)], cap=1)

    grow = []
    for i, (b, p) in enumerate((b, p) for b in (40, 60, 80, 100, 120, 160, 200, 240, 300, 400, 500, 600, 800) for p in (10, 25, 50, 20, 100)):
        d, e = GROW_STORIES[i % len(GROW_STORIES)]
        hd, he, r = pct_of(p, b)
        if p == 100:
            hd, he = f"صد {PCT} زیادتر یعنی یک بار دیگر همان قدر.", "100 percent more means the same amount once again."
        grow.append(ask(d(b, p), e(b, p), b + r, [r, b + p, b - r if b != r else None, b + r + 10],
                        f"{hd} {fa(b)} جمع {fa(r)} مساوی {fa(b + r)}.", f"{he} {b} plus {r} equals {b + r}."))
    pool6(s, "hop", "06", I_GROW, [(grow, N)], cap=1)

    plain = []
    wording = [("اوسط {d} چند است؟", "What is the average of {e}?"), ("{d}. اوسط این عددها را پیدا کن.", "{e}. Find the average of these numbers."),
               ("اگر {d} را یکجا کنیم و برابر تقسیم کنیم، هر حصه چند می" + Z + "شود؟", "If we put {e} together and share them out evenly, how much is each share?")]
    for i, nums in enumerate(mean_lists("plain", 3, 1, 20, 60)):
        d, e = fa_list(nums)
        w = wording[i % 3]
        m = sum(nums) // 3
        hd, he = mean_help(nums)
        plain.append(ask(w[0].format(d=d), w[1].format(e=e), m, [sum(nums), sorted(nums)[1] if sorted(nums)[1] != m else None, max(nums) if max(nums) != m else None, m + 1, m - 1], hd, he))
    pool6(s, "hop", "07", I_MEAN, [(plain, N)], dari=5)

    told = []
    for t, (d, e, lo, hi) in enumerate(MEAN_STORIES):
        for j, nums in enumerate(mean_lists(t, 4 + (t + 1) % 2, lo, hi, 5) + mean_lists(t, 4 + t % 2, lo, hi, 3)):
            ld, le = fa_list(nums)
            k, m = len(nums), sum(nums) // len(nums)
            hd, he = mean_help(nums)
            told.append(ask(d(k, ld), e(k, le), m, [sum(nums), max(nums) if max(nums) != m else None, m + 1, m - 1, sum(nums) // (k - 1) if sum(nums) % (k - 1) == 0 else None], hd, he))
    pool6(s, "hop", "08", I_MEAN_STORY, [(told, N)])

    trade = {"profit": [], "loss": [], "sell": [], "cost": []}
    i = 0
    for g, (noun, en, prices) in enumerate(TRADE_GOODS):
        step = 10 if prices.step == 10 else 50 if prices.step == 50 else 250
        for c in list(prices)[g % 3::3]:
            for f in (step * 2, step * 3, step * 5):
                who, who_en = TRADERS[i % len(TRADERS)]
                i += 1
                sold, low = c + f, c - f
                trade["profit"].append(ask(f"{who} {noun} را به {fa(c)} {AFN} خرید و به {fa(sold)} {AFN} فروخت. چند {AFN} فایده کرد؟",
                                           f"{who_en} bought {en} for {c} afghani and sold it for {sold} afghani. How many afghani was the profit?", f, [c + sold, sold, f + step, f - step if f > step else None],
                                           f"قیمت فروش از قیمت خرید بیشتر است، پس فایده کرد. {fa(sold)} منفی {fa(c)} مساوی {fa(f)}.",
                                           f"The selling price is more than the buying price, so there was a profit. {sold} minus {c} equals {f}."))
                if low > 0:
                    trade["loss"].append(ask(f"{who} {noun} را به {fa(c)} {AFN} خرید، اما به {fa(low)} {AFN} فروخت. چند {AFN} ضرر کرد؟",
                                             f"{who_en} bought {en} for {c} afghani, but sold it for {low} afghani. How many afghani was the loss?", f, [c + low, low, f + step, f - step if f > step else None],
                                             f"قیمت فروش از قیمت خرید کمتر است، پس ضرر کرد. {fa(c)} منفی {fa(low)} مساوی {fa(f)}.",
                                             f"The selling price is less than the buying price, so there was a loss. {c} minus {low} equals {f}."))
                trade["sell"].append(ask(f"{who} {noun} را به {fa(c)} {AFN} خرید و می{Z}خواهد {fa(f)} {AFN} فایده کند. آن را به چند {AFN} بفروشد؟",
                                         f"{who_en} bought {en} for {c} afghani and wants a profit of {f} afghani. For how many afghani should it be sold?", sold, [c - f if c > f else None, c, sold + step, sold - step],
                                         f"قیمت خرید جمع فایده مساوی قیمت فروش. {fa(c)} جمع {fa(f)} مساوی {fa(sold)}.", f"The buying price plus the profit equals the selling price. {c} plus {f} equals {sold}."))
                trade["cost"].append(ask(f"{who} {noun} را به {fa(sold)} {AFN} فروخت و {fa(f)} {AFN} فایده کرد. آن را به چند {AFN} خریده بود؟",
                                         f"{who_en} sold {en} for {sold} afghani and made a profit of {f} afghani. For how many afghani had it been bought?", c, [sold + f, sold, c + step, c - step if c > step else None],
                                         f"قیمت فروش منفی فایده مساوی قیمت خرید. {fa(sold)} منفی {fa(f)} مساوی {fa(c)}.", f"The selling price minus the profit equals the buying price. {sold} minus {f} equals {c}."))
    pool6(s, "hop", "09", I_PROFIT, [(trade["profit"], 6), (trade["loss"], 4), (trade["sell"], 4), (trade["cost"], 4)], cap=1)

    left, needs, save, goal, week = [], [], [], [], []
    for i, (inc, sp) in enumerate((inc, sp) for inc in range(1500, 9001, 500) for sp in range(1000, inc, 750)):
        span, span_en = [("یک هفته", "a week"), ("یک ماه", "a month")][inc >= 4000]
        left.append(ask(f"یک خانواده در {span} {fa(inc)} {AFN} عاید دارد و {fa(sp)} {AFN} مصرف می{Z}کند. چند {AFN} می{Z}ماند؟",
                        f"In {span_en} a family has an income of {inc} afghani and spends {sp} afghani. How many afghani are left?", inc - sp, [inc + sp, sp, inc - sp + 500, inc - sp - 250 if inc - sp > 250 else None],
                        f"عاید منفی مصرف مساوی آنچه می{Z}ماند. {fa(inc)} منفی {fa(sp)} مساوی {fa(inc - sp)}.", f"Income minus spending equals what is left. {inc} minus {sp} equals {inc - sp}."))
    things = [("خوراک", "food", "لباس", "clothes"), ("خوراک", "food", "چیزهای مکتب", "school things"), ("آرد و روغن", "flour and oil", "چوب سوخت", "firewood"),
              ("خوراک", "food", "صابون و چای", "soap and tea")]
    for i, (inc, a, b) in enumerate((inc, a, b) for inc in range(3000, 9001, 1000) for a in range(1500, inc - 500, 1000) for b in (500, 750, 1000) if a + b < inc):
        t = things[i % len(things)]
        rest = inc - a - b
        needs.append(ask(f"عاید یک خانواده در یک ماه {fa(inc)} {AFN} است. {fa(a)} {AFN} برای {t[0]} و {fa(b)} {AFN} برای {t[2]} مصرف می{Z}شود. چند {AFN} می{Z}ماند؟",
                         f"A family's income in a month is {inc} afghani. {a} afghani are spent on {t[1]} and {b} afghani on {t[3]}. How many afghani are left?", rest, [inc - a, inc - b, a + b, rest + 500],
                         f"اول مصرف{Z}ها را جمع کن: {fa(a)} جمع {fa(b)} مساوی {fa(a + b)}. بعد از عاید کم کن: {fa(inc)} منفی {fa(a + b)} مساوی {fa(rest)}.",
                         f"First add what is spent: {a} plus {b} equals {a + b}. Then take it from the income: {inc} minus {a + b} equals {rest}."))
    for i, (w, k) in enumerate((w, k) for w in (20, 25, 30, 40, 50, 75, 100, 150) for k in (4, 6, 8, 10, 12)):
        who, who_en = [("یک دختر", "A girl"), ("یک خانواده", "A family"), ("یک بچه", "A boy")][i % 3]
        save.append(ask(f"{who} هر هفته {fa(w)} {AFN} پس{Z}انداز می{Z}کند. بعد از {fa(k)} هفته چند {AFN} پس{Z}انداز شده است؟",
                        f"{who_en} saves {w} afghani every week. How many afghani are saved after {k} weeks?", w * k, [w + k, w * (k - 1), w * k + w, w * 10 if k != 10 else None],
                        f"هر هفته همان قدر است، پس ضرب می{Z}کنیم. {fa(k)} ضرب {fa(w)} مساوی {fa(w * k)}.", f"It is the same amount every week, so we multiply. {k} times {w} equals {w * k}."))
    wants = [("یک بز", "a goat"), ("یک ماشین خیاطی", "a sewing machine"), ("یک بایسکل", "a bicycle"), ("کتاب" + Z + "های مکتب", "the school books")]
    for i, (w, k) in enumerate((w, k) for w in (200, 250, 300, 400, 500) for k in (3, 4, 5, 6, 8, 9, 12)):
        noun, en = wants[i % len(wants)]
        g = w * k
        goal.append(ask(f"برای خریدن {noun} {fa(g)} {AFN} لازم است. خانواده هر ماه {fa(w)} {AFN} پس{Z}انداز می{Z}کند. بعد از چند ماه پول آن جمع می{Z}شود؟",
                        f"To buy {en}, {g} afghani are needed. The family saves {w} afghani every month. After how many months is the money together?", k, [k + 1, k - 1, k * 2, 10 if k != 10 else None],
                        f"می{Z}شماریم که چند بار {fa(w)} در {fa(g)} جای می{Z}شود. {fa(g)} تقسیم {fa(w)} مساوی {fa(k)}.", f"We count how many times {w} goes into {g}. {g} divided by {w} equals {k}."))
    for i, d in enumerate((40, 50, 60, 80, 90, 100, 120, 150, 200, 250)):
        who, who_en, what, what_en = [("یک زن", "A woman", "فروش تخم", "selling eggs"), ("یک مرد", "A man", "فروش شیر", "selling milk"), ("یک زن", "A woman", "خیاطی", "sewing"), ("یک مرد", "A man", "کار در باغ", "work in the garden")][i % 4]
        week.append(ask(f"{who} هر روز از {what} {fa(d)} {AFN} عاید دارد. در یک هفته چند {AFN} عاید دارد؟",
                        f"{who_en} has an income of {d} afghani every day from {what_en}. How many afghani is the income in a week?", 7 * d, [6 * d, d + 7, 7 * d + d, 5 * d],
                        f"یک هفته هفت روز است. هفت ضرب {fa(d)} مساوی {fa(7 * d)}.", f"A week is 7 days. 7 times {d} equals {7 * d}."))
    pool6(s, "hop", "10", I_BUDGET, [(left, 5), (needs, 4), (save, 4), (goal, 3), (week, 2)], cap=1)
    return s


# -- Market Scales: discount, selling price, profit, what is left, saving, a share ------

M_INTRO[6] = {
    "01": tr("تخفیف را حساب کن و قیمت نو را بده.", "Work out the discount and pay the new price."),
    "02": tr("قیمت خرید و فایده را جمع کن. مشتری چند بدهد؟", "Add the buying price and the profit. How much should the customer pay?"),
    "03": tr("فایده دکاندار را حساب کن و جدا بگذار.", "Work out the shopkeeper's profit and put it aside."),
    "04": tr("از عاید، مصرف را کم کن. آنچه می" + Z + "ماند را پس" + Z + "انداز کن.", "Take the spending from the income. Save what is left."),
    "05": tr("پس" + Z + "انداز چند هفته را حساب کن.", "Work out the saving of several weeks."),
    "06": tr("پول را به نسبت تقسیم کن و حصه یک نفر را بده.", "Share the money in the ratio and pay one person's share."),
}


def market6(level: int) -> Sheet:
    s = Sheet(MARKET_COLS)
    notes = [10, 20, 50, 100, 500]

    def B(rnd, gen):
        s.intro[rnd] = M_INTRO[6][rnd]
        build(s, 6, "market", rnd, gen)

    def discount(rng):
        deals = [(pr, p) for pr in range(200, 1001, 100) for p in (10, 20)] + [(pr, p) for pr in range(120, 1001, 40) for p in (25, 50)]
        for j, (pr, p) in enumerate(pick_even(deals, N, rng, key=lambda c: c[0] - c[0] * c[1] // 100, cap=1)):
            pic, noun = BIG[j % len(BIG)]
            d, e, r = pct_of(p, pr)
            market_row(s, "01", tr(f"{noun} {fa(pr)} {AFN} است. امروز {fa_pct(p)} تخفیف دارد. قیمت نو را بده.",
                                   cap(f"{costs(noun, pr)}. Today there is a discount of {p} percent. Pay the new price.")),
                       pic, pr - r, notes, "pay", tr(f"{d} {fa(pr)} منفی {fa(r)} مساوی {fa(pr - r)}.", f"{e} {pr} minus {r} equals {pr - r}."))
    B("01", discount)

    def selling(rng):
        deals = [(c, f) for c in range(150, 801, 50) for f in (20, 30, 40, 50, 60, 80, 100, 150)]
        for j, (c, f) in enumerate(pick_even(deals, N, rng, key=sum, cap=1)):
            pic, noun = BIG[(j + 2) % len(BIG)]
            market_row(s, "02", tr(f"دکاندار {noun} را به {fa(c)} {AFN} خریده است و می{Z}خواهد {fa(f)} {AFN} فایده کند. مشتری چند {AFN} بدهد؟ {PAY_IT}",
                                   f"The shopkeeper bought the {bare(noun)} for {c} afghani and wants a profit of {f} afghani. How many afghani should the customer pay? Pay for it."),
                       pic, c + f, notes, "pay", tr(f"قیمت خرید جمع فایده مساوی قیمت فروش. {fa(c)} جمع {fa(f)} مساوی {fa(c + f)}.",
                                                   f"The buying price plus the profit equals the selling price. {c} plus {f} equals {c + f}."))
    B("02", selling)

    def profit(rng):
        deals = [(c, f) for c in range(200, 901, 50) for f in range(20, 301, 10)]
        for j, (c, f) in enumerate(pick_even(deals, N, rng, key=lambda d: d[1], cap=1)):
            pic, noun = BIG[(j + 4) % len(BIG)]
            market_row(s, "03", tr(f"دکاندار {noun} را به {fa(c)} {AFN} خرید و به {fa(c + f)} {AFN} فروخت. فایده او چند {AFN} است؟ فایده را جدا بگذار.",
                                   f"The shopkeeper bought the {bare(noun)} for {c} afghani and sold it for {c + f} afghani. How many afghani is the profit? Put the profit aside."),
                       pic, f, [10, 20, 50, 100], "pay", tr(f"قیمت فروش منفی قیمت خرید مساوی فایده. {fa(c + f)} منفی {fa(c)} مساوی {fa(f)}.",
                                                              f"The selling price minus the buying price equals the profit. {c + f} minus {c} equals {f}."))
    B("03", profit)

    def left(rng):
        things = [("چیزهای مکتب", "school things"), ("صابون و چای", "soap and tea"), ("لباس", "clothes"), ("چوب سوخت", "firewood")]
        deals = [(inc, a, b) for inc in range(800, 2001, 100) for a in range(400, inc, 70) for b in (100, 150, 200, 250, 300) if 50 <= inc - a - b <= 600]
        for j, (inc, a, b) in enumerate(pick_even(deals, N, rng, key=lambda d: d[0] - d[1] - d[2], cap=1)):
            what, what_en = things[j % len(things)]
            rest = inc - a - b
            market_row(s, "04", tr(f"این هفته {fa(inc)} {AFN} عاید داری. {fa(a)} {AFN} برای خوراک و {fa(b)} {AFN} برای {what} مصرف می{Z}شود. آنچه می{Z}ماند را در کیسه پس{Z}انداز بگذار.",
                                   f"This week you have an income of {inc} afghani. {a} afghani are spent on food and {b} afghani on {what_en}. Put what is left into the savings purse."),
                       "purse", rest, notes, "pay", tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}. {fa(inc)} منفی {fa(a + b)} مساوی {fa(rest)}.",
                                                       f"{a} plus {b} equals {a + b}. {inc} minus {a + b} equals {rest}."))
    B("04", left)

    def saving(rng):
        deals = [(w, k) for w in (20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150) for k in range(3, 11)]
        for j, (w, k) in enumerate(pick_even(deals, N, rng, key=lambda d: d[0] * d[1], cap=1)):
            market_row(s, "05", tr(f"هر هفته {fa(w)} {AFN} پس{Z}انداز می{Z}کنی. پس{Z}انداز {fa(k)} هفته را در کیسه بگذار.",
                                   f"Every week you save {w} afghani. Put the saving of {k} weeks into the purse."),
                       "money", w * k, notes, "pay", tr(f"{fa(k)} ضرب {fa(w)} مساوی {fa(w * k)}.", f"{k} times {w} equals {w * k}."))
    B("05", saving)

    def shares(rng):
        deals = [(a, b, u) for a, b in ((1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2), (1, 4), (3, 4), (4, 1), (2, 5)) for u in (20, 30, 40, 50, 60, 80, 100, 150)]
        for j, (a, b, u) in enumerate(pick_even(deals, N, rng, key=lambda d: d[2] * (d[0] if (d[0] + d[1] + d[2]) % 20 else d[1]), cap=1)):
            first = bool((a + b + u) % 20)
            total, part = u * (a + b), u * (a if first else b)
            who = ("اول", "first") if first else ("دوم", "second")
            market_row(s, "06", tr(f"دو نفر {fa(total)} {AFN} را به نسبت {fa_ratio(a, b)} تقسیم می{Z}کنند. حصه نفر {who[0]} را بده.",
                                   f"Two people share {total} afghani in the ratio {a} to {b}. Pay the share of the {who[1]} person."),
                       "money", part, notes, "pay",
                       tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)} حصه. {fa(total)} تقسیم {fa(a + b)} مساوی {fa(u)}: هر حصه {fa(u)} {AFN} است. نفر {who[0]} {fa(a if first else b)} حصه می{Z}گیرد: {fa(a if first else b)} ضرب {fa(u)} مساوی {fa(part)}.",
                          f"{a} plus {b} equals {a + b} parts. {total} divided by {a + b} equals {u}: each part is {u} afghani. The {who[1]} person gets {nn(a if first else b, 'part')}: {a if first else b} times {u} equals {part}."))
    B("06", shares)
    return s


# -- Carpet Weaver: order percents, build an equality ---------------------------

I_ORDER_PCT = tr("فیصدها را به ترتیب بچین.", "Put the percents in order.")
I_ORDER_MIX = tr("فیصد، کسر و عدد اعشاری را به ترتیب بچین. اول همه را به فیصد برگردان.", "Put the percent, the fraction and the decimal number in order. First turn them all into percents.")
I_BUILD_PCT = tr("جمله را بچین: فیصد مساوی کدام کسر یا عدد اعشاری است؟", "Build the sentence: the percent is equal to which fraction or decimal number?")
I_BUILD_RATIO = tr("جمله را بچین: کدام نسبت با این نسبت مساوی است؟", "Build the sentence: which ratio is equal to this ratio?")
I_BUILD_SHOP = tr("حساب دکان و خانه را به ترتیب بچین.", "Put the sum of the shop and of the home in order.")


def forms6(p: int) -> list[tuple[str, tuple[str, str]]]:
    """The three ways of writing p percent, each with how it is said."""
    k, n = pct_frac(p)
    return [(P(p), (fa_pct(p), f"{p} percent")), (fr(k, n), (fa_frac(k, n), f"{k}/{n}")), ("t:" + dec2(p), (fa_dec(dec2(p)), dec2(p)))]


def weaver6(level: int) -> Sheet:
    s = Sheet(BUILDER_COLS)
    up_say = tr("از کوچک به بزرگ بچین.", "Arrange them from small to big.")
    down_say = tr("از بزرگ به کوچک بچین.", "Arrange them from big to small.")
    pct_help = tr("فیصد بزرگتر یعنی حصه بیشتر از صد. از یک سر شروع کن و یکی یکی پیش برو.", "A bigger percent means a bigger part of the hundred. Start at one end and go on one by one.")
    mix_help = tr("همه را به فیصد برگردان: نیم پنجاه فیصد است، چارک بیست و پنج فیصد، صفر اعشاریه هفتاد و پنج، هفتاد و پنج فیصد. بعد مقایسه کن.",
                  "Turn them all into percents: a half is 50 percent, a quarter 25 percent, 0.75 is 75 percent. Then compare.")

    def percents(rng):
        seen = set()
        while len(seen) < 16:
            size = 4 + len(seen) % 2
            picks = tuple(sorted(rng.sample([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99, 100], size)))
            if picks in seen:
                continue
            seen.add(picks)
            up = len(seen) % 3 != 0
            order_things(s, "01", I_ORDER_PCT, [P(p) for p in picks], up, {P(p): (fa_pct(p), f"{p} percent") for p in picks}, up_say if up else down_say, pct_help)
    build(s, 6, "weaver", "01", percents)

    def mixed(rng):
        seen = set()
        while len(seen) < 16:
            picks = tuple(sorted(rng.sample([10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90], 4)))
            if picks in seen:
                continue
            seen.add(picks)
            shift = rng.randrange(3)
            chosen = [forms6(p)[(i + shift) % 3] for i, p in enumerate(picks)]
            up = len(seen) % 3 != 0
            order_things(s, "02", I_ORDER_MIX, [t for t, _ in chosen], up, dict(chosen), up_say if up else down_say, mix_help)
    build(s, 6, "weaver", "02", mixed)

    def equal(tiles, extra, say, done, help_fa, rnd, intro):
        assert len(set(tiles + extra)) == len(tiles + extra) <= 8, (tiles, extra)
        row = s.add(round=rnd, intro_fa=intro, say_fa=say, tiles="|".join(tiles), extra="|".join(extra), rtl="", done_fa=done, help_fa=help_fa)
        L6_META.append((row, lambda r: (lambda t, x: len(t) == 3 and t[1] == "t:=" and val(t[0]) == val(t[2]) and all(val(e) != val(t[0]) for e in x))(r["tiles"].split("|"), r["extra"].split("|"))))

    def pct_sentences(rng):
        base = [50, 25, 75, 10, 20, 30, 40, 60, 70, 80, 90, 5]
        cands = [(p, kind) for p in base for kind in (1, 2)]
        for i, (p, kind) in enumerate(pick_even(cands, 16, rng, key=lambda c: c[0], cap=2)):
            (right, (d, e)) = forms6(p)[kind]
            others = [forms6(q)[kind][0] for q in rng.sample([q for q in base if q != p], 4)]
            if kind == 1:
                others = [fr(1, p)] + others if Fraction(1, p) != Fraction(p, 100) else others
            else:
                others = [f"t:{p // 10}.{p % 10}"] + others
            extra = pick_wrong(right, others)
            what, what_en = ("کدام کسر", "which fraction") if kind == 1 else ("کدام عدد اعشاری", "which decimal number")
            flip = i % 4 == 3
            tiles = [right, "t:=", P(p)] if flip else [P(p), "t:=", right]
            if flip:
                extra = pick_wrong(P(p), near_pcts(p))
                say = tr(f"{d} مساوی چند {PCT} است؟ جمله را بچین.", f"{e} is equal to what percent? Build the sentence.")
                done = tr(f"{d} مساوی {fa_pct(p)}.", f"{e} equals {p} percent.")
            else:
                say = tr(f"{fa_pct(p)} مساوی {what} است؟ جمله را بچین.", f"{p} percent is equal to {what_en}? Build the sentence.")
                done = tr(f"{fa_pct(p)} مساوی {d}.", f"{p} percent equals {e}.")
            equal(tiles, extra, say, done, tr(f"{fa_pct(p)} یعنی {fa_frac(p, 100)}. اول یک طرف، بعد نشان مساوی، بعد طرف دیگر.", f"{p} percent means {p}/100. First one side, then the equals sign, then the other side."), "03", I_BUILD_PCT)
    build(s, 6, "weaver", "03", pct_sentences)

    def ratio_sentences(rng):
        cands = [(a, b, m) for a, b in RATIOS6 for m in (2, 3, 4, 5) if a * m <= 20 and b * m <= 20]
        for i, (a, b, m) in enumerate(pick_even(cands, 16, rng, key=lambda c: (c[0] * 100 + c[1]), cap=1)):
            right = R(a * m, b * m)
            extra = pick_wrong(right, [R(a + m, b + m), R(b * m, a * m), R(a * m, b * m + b), R(a * m + a, b * m), R(a * m, b)])
            down = i % 4 == 3   # from the big ratio to its simplest form
            tiles = [right, "t:=", R(a, b)] if down else [R(a, b), "t:=", right]
            if down:
                extra = pick_wrong(R(a, b), [R(b, a), R(a + 1, b), R(a, b + 1), R(a * m, b), R(a, b * m)])
                say = tr(f"{fa_ratio(a * m, b * m)} را ساده کن. جمله را بچین.", f"Simplify {a * m} to {b * m}. Build the sentence.")
                done = tr(f"{fa_ratio(a * m, b * m)} مساوی {fa_ratio(a, b)}.", f"{a * m} to {b * m} equals {a} to {b}.")
                help_fa = tr(f"هر دو عدد را بر {fa(m)} تقسیم کن.", f"Divide both numbers by {m}.")
            else:
                say = tr(f"{fa_ratio(a, b)} مساوی کدام نسبت است؟ جمله را بچین.", f"{a} to {b} is equal to which ratio? Build the sentence.")
                done = tr(f"{fa_ratio(a, b)} مساوی {fa_ratio(a * m, b * m)}.", f"{a} to {b} equals {a * m} to {b * m}.")
                help_fa = tr(f"هر دو عدد را در یک عدد ضرب کن. {fa(a)} ضرب {fa(m)} مساوی {fa(a * m)} و {fa(b)} ضرب {fa(m)} مساوی {fa(b * m)}.",
                             f"Multiply both numbers by the same number. {a} times {m} equals {a * m} and {b} times {m} equals {b * m}.")
            equal(tiles, extra, say, done, help_fa, "04", I_BUILD_RATIO)
    build(s, 6, "weaver", "04", ratio_sentences)

    minus_help = tr("اول عدد بزرگ، بعد نشان منفی، بعد عدد کوچک، بعد نشان مساوی و در آخر جواب.",
                    "First the big number, then the minus sign, then the small number, then the equals sign and last the answer.")

    def shop(rng):
        deals = [(c, f) for c in range(40, 400, 10) for f in range(10, 151, 10) if f != c and c + f != 2 * f and c != 2 * f]
        for i, (c, f) in enumerate(pick_even(deals, 16, rng, key=lambda d: d[1], cap=2)):
            big = c + f
            extra = [x for x in uniq([big + c, f + 10, f - 10, big + f]) if x > 0 and x not in (big, c, f)][:2]
            if i % 2 == 0:
                say = tr(f"دکاندار به {fa(c)} {AFN} خرید و به {fa(big)} {AFN} فروخت. فایده چند است؟ حساب را به ترتیب بچین.",
                         f"The shopkeeper bought for {c} afghani and sold for {big} afghani. How much is the profit? Put the sum in order.")
            else:
                say = tr(f"عاید {fa(big)} {AFN} و مصرف {fa(c)} {AFN} است. چند {AFN} می{Z}ماند؟ حساب را به ترتیب بچین.",
                         f"The income is {big} afghani and the spending is {c} afghani. How many afghani are left? Put the sum in order.")
            row = s.add(round="05", intro_fa=I_BUILD_SHOP, say_fa=say, tiles="|".join([W(big), "t:−", W(c), "t:=", W(f)]), extra="|".join(W(x) for x in extra), rtl="",
                        done_fa=tr(f"{fa(big)} منفی {fa(c)} مساوی {fa(f)}.", f"{big} minus {c} equals {f}."), help_fa=minus_help)
            SENT_META.append(row)
    build(s, 6, "weaver", "05", shop)
    return s


RATIOS6 = [(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5), (2, 1), (3, 1), (4, 1), (3, 2), (5, 2), (4, 3), (5, 3)]


# -- Share the Bread: sorting ------------------------------------------------------

I_PCT_HALF = tr("از نیم کمتر است، مساوی نیم است یا بیشتر؟ پنجاه فیصد یعنی نیم.", "Is it less than half, equal to half or more? 50 percent means half.")
I_PROFIT_SORT = tr("خرید و فروش را ببین: فایده است یا ضرر؟", "Look at the buying and the selling: is it a profit or a loss?")
I_SAME_PCT = tr("هر کدام را در سبد شکلی بینداز که با آن مساوی است.", "Put each one in the basket of the picture it is equal to.")
I_INCOME = tr("پول به خانه می" + Z + "آید یا از خانه می" + Z + "رود؟ عاید یا مصرف؟", "Does the money come into the home or go out of it? Income or spending?")


def sorter6(level: int) -> Sheet:
    s = Sheet(SORTER_COLS)

    def plain(rnd, intro, rows, kind=None, test=None):
        def gen(rng):
            for thing, say, en, basket, b_say, b_en in rng.sample(rows, len(rows)):
                row = s.add(round=rnd, intro_fa=intro, thing=thing, say_fa=tr(say, en), basket=basket, basket_say_fa=tr(b_say, b_en))
                if kind:
                    SORT2_META.append((row, kind))
                if test:
                    L6_META.append((row, test))
        build(s, 6, "sorter", rnd, gen)

    tr("کمتر", "less"), tr("بیشتر", "more"), tr("نیم", "half")
    less, same, more = ("f:کمتر", "کمتر از نیم", "less than half"), ("f:نیم", "مساوی نیم", "equal to half"), ("f:بیشتر", "بیشتر از نیم", "more than half")
    rows = []
    for thing, d, e in [(P(p), fa_pct(p), f"{p} percent") for p in (10, 25, 40, 45, 49, 50, 51, 60, 75, 90, 100)] + \
                       [(fr(k, n), fa_frac(k, n), f"{k}/{n}") for k, n in ((1, 2), (2, 4), (5, 10), (3, 6))] + \
                       [("t:" + x, fa_dec(x), x) for x in ("0.50", "0.25", "0.75")]:
        v = val(thing)
        rows.append((thing, d, e) + (less if v < Fraction(1, 2) else same if v == Fraction(1, 2) else more))
    plain("01", I_PCT_HALF, rows, kind="half")

    profit, loss = ("f:" + tr("فایده", "profit"), "فایده", "profit"), ("f:" + tr("ضرر", "loss"), "ضرر", "loss")
    rows = []
    for c, sold in [(50, 70), (80, 60), (120, 150), (200, 180), (90, 100), (100, 90), (35, 45), (60, 40), (250, 300), (300, 250), (15, 20), (75, 70), (400, 450), (500, 480),
                    (65, 85), (150, 140), (20, 35), (110, 95)]:
        rows.append((f"t:{c} → {sold}", f"به {fa(c)} خرید و به {fa(sold)} فروخت.", f"Bought for {c} and sold for {sold}.") + (profit if sold > c else loss))
    plain("02", I_PROFIT_SORT, rows, test=lambda r: (lambda m: (int(m.group(2)) > int(m.group(1))) == (r["basket"] == "f:فایده") and r["basket"] in ("f:فایده", "f:ضرر"))(
        re.fullmatch(r"t:(\d+) → (\d+)", r["thing"])))

    baskets = {25: (grid(25), "بیست و پنج " + PCT, "25 percent"), 50: (grid(50), "پنجاه " + PCT, "50 percent"), 75: (grid(75), "هفتاد و پنج " + PCT, "75 percent"),
               10: (grid(10), "ده " + PCT, "10 percent")}
    rows = []
    for p, extra in ((25, [(2, 8)]), (50, [(2, 4), (5, 10)]), (75, [(6, 8)]), (10, [(10, 100)])):
        for thing, (d, e) in forms6(p) + [(fr(k, n), (fa_frac(k, n), f"{k}/{n}")) for k, n in extra]:
            rows.append((thing, d, e) + baskets[p])
    plain("03", I_SAME_PCT, rows, kind="same")

    income, spend = ("f:" + tr("عاید", "income"), "عاید", "income"), ("f:" + tr("مصرف", "spending"), "مصرف", "spending")
    rows = [(pic, d, e) + income for pic, d, e in [
        ("egg", "تخم می" + Z + "فروشیم.", "We sell eggs."), ("milk", "شیر می" + Z + "فروشیم.", "We sell milk."), ("carpet", "قالین بافته را می" + Z + "فروشیم.", "We sell the carpet we wove."),
        ("wheat", "گندم می" + Z + "فروشیم.", "We sell wheat."), ("apple", "سیب باغ را می" + Z + "فروشیم.", "We sell the apples of the garden."),
        ("goat", "یک بز می" + Z + "فروشیم.", "We sell a goat."), ("walnut", "چهارمغز می" + Z + "فروشیم.", "We sell walnuts."), ("farmer", "مزد یک روز کار را می" + Z + "گیریم.", "We get the pay for a day's work."),
        ("yoghurt", "ماست می" + Z + "فروشیم.", "We sell yoghurt.")]]
    rows += [(pic, d, e) + spend for pic, d, e in [
        ("flour_sack", "یک بوری آرد می" + Z + "خریم.", "We buy a sack of flour."), ("oil_can", "روغن می" + Z + "خریم.", "We buy oil."), ("notebook", "کتابچه می" + Z + "خریم.", "We buy a notebook."),
        ("shoes", "بوت می" + Z + "خریم.", "We buy shoes."), ("soap", "صابون می" + Z + "خریم.", "We buy soap."), ("tea", "چای می" + Z + "خریم.", "We buy tea."),
        ("sugar", "بوره می" + Z + "خریم.", "We buy sugar."), ("blanket", "یک کمپل می" + Z + "خریم.", "We buy a blanket."), ("pencil", "پنسل می" + Z + "خریم.", "We buy a pencil.")]]
    plain("04", I_INCOME, rows, test=lambda r: ("می" + Z + "خریم" in r["say_fa"]) == (r["basket"] == "f:مصرف"))
    return s


# -- Shape Mason: the scale of a map, measuring liquids ---------------------------

I_SCALE = tr("مقیاس نقشه می" + Z + "گوید که یک سانتی" + Z + "متر روی نقشه چند کیلومتر راه است. حساب کن.",
             "The scale of a map tells how many kilometres one centimetre on the map stands for. Work it out.")
I_SCALE_BACK = tr("از راه راستی به نقشه برگرد، یا مقیاس را پیدا کن.", "Go back from the real way to the map, or find the scale.")
I_MAP = tr("نقشه را ببین. هر تکه راه یک سانتی" + Z + "متر است. تکه" + Z + "ها را بشمار و با مقیاس حساب کن.",
           "Look at the map. Each piece of road is one centimetre. Count the pieces and work it out with the scale.")
I_SPOON = tr("با قاشق اندازه" + Z + "گیری حساب کن: یک قاشق پنج ملی" + Z + "لیتر می" + Z + "گیرد.", "Work it out with the measuring spoon: one spoon holds 5 millilitres.")
I_CUP = tr("پیاله اندازه" + Z + "گیری را ببین و خط" + Z + "ها را بشمار.", "Look at the measuring cup and count the marks.")
I_BOTTLE = tr("حساب کن که بوتل برای چند روز بس است و چه قدر می" + Z + "ماند.", "Work out for how many days the bottle lasts and how much is left.")
I_LITRE_ML = tr("یک لیتر هزار ملی" + Z + "لیتر است. لیتر و ملی" + Z + "لیتر را حساب کن.", "One litre is 1000 millilitres. Work out the litres and the millilitres.")
SCALE_WAYS = [
    (lambda n: f"دو قریه روی نقشه {fa(n)} سانتی{Z}متر از هم دور است. راه راستی چند {KM} است؟", lambda n: f"Two villages are {n} centimetres apart on the map. How many kilometres is the real way?"),
    (lambda n: f"از قریه تا شهر روی نقشه {fa(n)} سانتی{Z}متر است. راه راستی چند {KM} است؟", lambda n: f"From the village to the town it is {n} centimetres on the map. How many kilometres is the real way?"),
    (lambda n: f"دریا روی نقشه {fa(n)} سانتی{Z}متر دراز است. دریا راستی چند {KM} دراز است؟", lambda n: f"The river is {n} centimetres long on the map. How many kilometres long is the real river?"),
    (lambda n: f"از مکتب تا بازار روی نقشه {fa(n)} سانتی{Z}متر است. راه راستی چند {KM} است؟", lambda n: f"From the school to the bazaar it is {n} centimetres on the map. How many kilometres is the real way?"),
]


def scale_say(k: int) -> tuple[str, str]:
    return f"روی نقشه یک سانتی{Z}متر یعنی {fa(k)} {KM}.", f"On the map 1 centimetre stands for {nn(k, 'kilometre')}."


def mason6(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    forward = []
    for i, (k, n) in enumerate((k, n) for k in (1, 2, 5, 10) for n in range(2, 13)):
        d, e = SCALE_WAYS[i % len(SCALE_WAYS)]
        sd, se = scale_say(k)
        if k == 1:
            hd, he = f"یک سانتی{Z}متر یعنی یک {KM}، پس {fa(n)} سانتی{Z}متر یعنی {fa(n)} {KM}.", f"1 centimetre stands for 1 kilometre, so {n} centimetres stand for {n} kilometres."
        else:
            hd, he = f"هر سانتی{Z}متر {fa(k)} {KM} است. {fa(n)} ضرب {fa(k)} مساوی {fa(n * k)}.", f"Each centimetre is {k} kilometres. {n} times {k} equals {n * k}."
        forward.append(ask(f"{sd} {d(n)}", f"{se} {e(n)}", n * k, [n + k, n if k > 1 else n + 1, n * k + k, n * 10 if k != 10 else n], hd, he))
    pool6(s, "mason", "01", I_SCALE, [(forward, N)], dari=6)

    back, scale = [], []
    for i, (k, n) in enumerate((k, n) for k in (2, 5, 10, 4) for n in range(2, 11)):
        sd, se = scale_say(k)
        d, e = [("از قریه تا شهر {x} {KM} راه است. روی نقشه چند سانتی" + Z + "متر می" + Z + "شود؟", "From the village to the town it is {x} kilometres. How many centimetres is that on the map?"),
                ("یک سرک {x} {KM} دراز است. روی نقشه آن را چند سانتی" + Z + "متر بکشیم؟", "A road is {x} kilometres long. How many centimetres do we draw it on the map?")][i % 2]
        back.append(ask(f"{sd} {d.format(x=fa(n * k), KM=KM)}", f"{se} {e.format(x=n * k)}", n, [n * k, n * k * k, n + k, n * k - k],
                        f"هر {fa(k)} {KM} یک سانتی{Z}متر می{Z}شود. {fa(n * k)} تقسیم {fa(k)} مساوی {fa(n)}.", f"Every {k} kilometres make 1 centimetre. {n * k} divided by {k} equals {n}."))
    for i, (k, n) in enumerate((k, n) for k in (2, 3, 4, 5, 6, 8, 10, 20) for n in (2, 3, 4, 5, 6) if n != k):
        scale.append(ask(f"دو قریه روی نقشه {fa(n)} سانتی{Z}متر از هم دور است. راه راستی {fa(n * k)} {KM} است. یک سانتی{Z}متر نقشه چند {KM} است؟",
                         f"Two villages are {n} centimetres apart on the map. The real way is {n * k} kilometres. How many kilometres does 1 centimetre of the map stand for?", k, [n, n * k, n * k - n, k + 1],
                         f"{fa(n * k)} {KM} را بین {fa(n)} سانتی{Z}متر تقسیم کن. {fa(n * k)} تقسیم {fa(n)} مساوی {fa(k)}.", f"Share {n * k} kilometres among {n} centimetres. {n * k} divided by {n} equals {k}."))
    pool6(s, "mason", "02", I_SCALE_BACK, [(back, 11), (scale, 7)])

    piece = (f"هر تکه راه روی نقشه یک سانتی{Z}متر است", "each piece of road on the map is 1 centimetre")
    for rnd, names in (("03", ["map_scale_1", "map_scale_2", "map_scale_3"]), ("04", ["map_scale_4", "map_scale_5", "map_scale_6"])):
        cands = []
        for name in names:
            (a, b, c), (n1, n2) = MAPS6[name]
            for i, k in enumerate((1, 2, 5)):
                sd, se = f"{piece[0]} و یک سانتی{Z}متر یعنی {fa(k)} {KM}.", f"{cap(piece[1])} and 1 centimetre stands for {nn(k, 'kilometre')}."
                for (x, y, n) in ((a, b, n1), (b, c, n2)):
                    hd = f"تکه{Z}های راه را بشمار: {fa(n)}." + (f" {fa(n)} ضرب {fa(k)} مساوی {fa(n * k)}." if k > 1 else f" {fa(n)} سانتی{Z}متر یعنی {fa(n)} {KM}.")
                    he = f"Count the pieces of road: {n}." + (f" {n} times {k} equals {n * k}." if k > 1 else f" {n} {'centimetre stands' if n == 1 else 'centimetres stand'} for {nn(n, 'kilometre')}.")
                    cands.append(ask(f"{sd} از {x[1]} تا {y[1]} چند {KM} راه است؟", f"{se} How many kilometres is it from the {x[2]} to the {y[2]}?", n * k, [n1 * k if n != n1 else n2 * k, (n1 + n2) * k, n + k, n * k + 1], hd, he, show=name))
                t = n1 + n2
                cands.append(ask(f"{sd} از {a[1]} از راه {b[1]} تا {c[1]} چند {KM} راه است؟", f"{se} How many kilometres is it from the {a[2]} past the {b[2]} to the {c[2]}?", t * k, [n1 * k, n2 * k, t + k, t * k + k],
                                 f"هر دو راه را بشمار: {fa(n1)} جمع {fa(n2)} مساوی {fa(t)} سانتی{Z}متر." + (f" {fa(t)} ضرب {fa(k)} مساوی {fa(t * k)}." if k > 1 else f" یعنی {fa(t)} {KM}."),
                                 f"Count both roads: {n1} plus {n2} equals {t} centimetres." + (f" {t} times {k} equals {t * k}." if k > 1 else f" That is {t} kilometres."), show=name))
                if i:
                    big, small_ = ((a, b, n1), (b, c, n2)) if n1 > n2 else ((b, c, n2), (a, b, n1))
                    df = big[2] - small_[2]
                    cands.append(ask(f"{sd} راه {big[0][1]} تا {big[1][1]} چند {KM} از راه {small_[0][1]} تا {small_[1][1]} درازتر است؟",
                                     f"{se} How many kilometres longer is the way from the {big[0][2]} to the {big[1][2]} than the way from the {small_[0][2]} to the {small_[1][2]}?", df * k, [big[2] * k, small_[2] * k, t * k, df],
                                     f"{fa(big[2])} منفی {fa(small_[2])} مساوی {fa(df)} سانتی{Z}متر." + (f" {fa(df)} ضرب {fa(k)} مساوی {fa(df * k)}." if k > 1 else ""),
                                     f"{big[2]} minus {small_[2]} equals {nn(df, 'centimetre')}." + (f" {df} times {k} equals {df * k}." if k > 1 else ""), show=name))
            for (x, y, n) in ((a, b, n1), (b, c, n2)):
                cands.append(ask(f"{cap_fa(piece[0])}. از {x[1]} تا {y[1]} روی نقشه چند سانتی{Z}متر است؟", f"{cap(piece[1])}. How many centimetres is it on the map from the {x[2]} to the {y[2]}?", n, [n1 if n != n1 else n2, n1 + n2, n + 1, n - 1],
                                 f"تکه{Z}های راه را بشمار: {fa(n)}.", f"Count the pieces of road: {n}.", show=name))
        pool6(s, "mason", rnd, I_MAP, [(cands, N)], cap=3)

    spoon = (f"یک قاشق اندازه{Z}گیری پنج {ML} می{Z}گیرد.", "A measuring spoon holds 5 millilitres.")
    med, day, cook, back5 = [], [], [], []
    for a in (5, 10, 15, 20):
        k = a // 5
        med.append(ask(f"کارمند صحی گفته است: هر بار {fa(a)} {ML} دوا. {spoon[0]} هر بار چند قاشق اندازه{Z}گیری می{Z}شود؟",
                       f"The health worker said: {a} millilitres of medicine each time. {spoon[1]} How many measuring spoons is that each time?", k, [a, a + 5, k + 1, k + 2],
                       f"{fa(a)} تقسیم پنج مساوی {fa(k)}. {DOSE_RULE[0]}", f"{a} divided by 5 equals {k}. {DOSE_RULE[1]}"))
        med.append(ask(f"روی بوتل دوا نوشته است: هر بار {fa(a)} {ML}. {spoon[0]} چند قاشق اندازه{Z}گیری پر می{Z}شود؟",
                       f"The writing on the bottle of medicine says: {a} millilitres each time. {spoon[1]} How many full measuring spoons is that?", k, [a, a + 5, k + 1, k + 2],
                       f"می{Z}شماریم که چند بار پنج در {fa(a)} جای می{Z}شود: {fa(k)}. {DOSE_RULE[0]}", f"We count how many times 5 goes into {a}: {k}. {DOSE_RULE[1]}"))
    for a in (5, 10, 15):
        day.append(ask(f"کارمند صحی گفته است: صبح {fa(a)} {ML} و شام {fa(a)} {ML} دوا. در یک روز چند {ML} می{Z}شود؟",
                       f"The health worker said: {a} millilitres of medicine in the morning and {a} millilitres in the evening. How many millilitres is that in a day?", 2 * a, [a, 3 * a, 2 * a + 5, a + 2],
                       f"{fa(a)} جمع {fa(a)} مساوی {fa(2 * a)}. {DOSE_RULE[0]}", f"{a} plus {a} equals {2 * a}. {DOSE_RULE[1]}"))
        day.append(ask(f"روی بوتل دوا نوشته است: روز سه بار، هر بار {fa(a)} {ML}. در یک روز چند {ML} می{Z}شود؟",
                       f"The writing on the bottle of medicine says: three times a day, {a} millilitres each time. How many millilitres is that in a day?", 3 * a, [a, 2 * a, 3 * a + 5, a + 3],
                       f"سه ضرب {fa(a)} مساوی {fa(3 * a)}. {DOSE_RULE[0]}", f"3 times {a} equals {3 * a}. {DOSE_RULE[1]}"))
    dishes = [("برای خمیر", "For the dough", "روغن", "oil"), ("برای فرنی", "For the pudding", "شیر", "milk"), ("برای سالاد", "For the salad", "آب لیمو", "lemon juice"), ("برای آش", "For the soup", "روغن", "oil")]
    for i, a in enumerate(range(10, 65, 5)):
        dish, dish_en, liq, liq_en = dishes[i % len(dishes)]
        cook.append(ask(f"{dish} {fa(a)} {ML} {liq} لازم است. {spoon[0]} چند قاشق {liq} لازم است؟", f"{dish_en}, {a} millilitres of {liq_en} are needed. {spoon[1]} How many spoons of {liq_en} are needed?", a // 5,
                        [a, a // 5 + 1, a // 5 - 1, a - 5], f"می{Z}شماریم که چند بار پنج در {fa(a)} جای می{Z}شود. {fa(a)} تقسیم پنج مساوی {fa(a // 5)}.", f"We count how many times 5 goes into {a}. {a} divided by 5 equals {a // 5}."))
    for i, k in enumerate(range(2, 13)):
        liq, liq_en = [("روغن", "oil"), ("شیر", "milk"), ("آب", "water")][i % 3]
        back5.append(ask(f"{fa(k)} قاشق اندازه{Z}گیری پر از {liq}، چند {ML} می{Z}شود؟ هر قاشق پنج {ML} می{Z}گیرد.", f"{k} full measuring spoons of {liq_en} make how many millilitres? Each spoon holds 5 millilitres.", 5 * k,
                         [k, k + 5, 5 * k + 5, 10 * k], f"{fa(k)} ضرب پنج مساوی {fa(5 * k)}.", f"{k} times 5 equals {5 * k}."))
    pool6(s, "mason", "05", I_SPOON, [(med, 5), (day, 3), (cook, 5), (back5, 5)], cap=3)

    level_, fill = [], []
    liquids = [("آب", "water"), ("شیر", "milk"), ("روغن", "oil"), ("چای", "tea")]
    for i, (k, u) in enumerate((k, u) for u in (5, 10, 20, 25, 50) for k in range(1, CUP_MARKS + 1)):
        liq, liq_en = liquids[i % 4]
        level_.append(ask(f"در این پیاله اندازه{Z}گیری {liq} است. هر خط {fa(u)} {ML} است. چند {ML} {liq} در پیاله است؟",
                          f"There is {liq_en} in this measuring cup. Each mark is {u} millilitres. How many millilitres of {liq_en} are in the cup?", k * u, [k, u, k * u + u, (CUP_MARKS - k) * u if 2 * k != CUP_MARKS else None],
                          f"خط{Z}ها را از پایین تا سر {liq} بشمار: {fa(k)}. {fa(k)} ضرب {fa(u)} مساوی {fa(k * u)}.", f"Count the marks from the bottom to the top of the {liq_en}: {k}. {k} times {u} equals {k * u}.", show=f"cup_marks_{k}"))
        if k < CUP_MARKS:
            rest = CUP_MARKS - k
            fill.append(ask(f"این پیاله اندازه{Z}گیری شش خط دارد و هر خط {fa(u)} {ML} است. برای پر شدن تا خط آخر چند {ML} {liq} دیگر لازم است؟",
                            f"This measuring cup has 6 marks and each mark is {u} millilitres. How many more millilitres of {liq_en} are needed to fill it to the last mark?", rest * u, [k * u if k != rest else None, rest, CUP_MARKS * u, rest * u + u],
                            f"خط{Z}های خالی را بشمار: {fa(rest)}. {fa(rest)} ضرب {fa(u)} مساوی {fa(rest * u)}.", f"Count the empty marks: {rest}. {rest} times {u} equals {rest * u}.", show=f"cup_marks_{k}"))
    pool6(s, "mason", "06", I_CUP, [(level_, 11), (fill, 7)])

    lasts, oil, left = [], [], []
    for i, (b, d) in enumerate((b, d) for b in (60, 100, 120, 150, 200) for d in (5, 10, 15, 20) if b % d == 0):
        first = [(f"یک بوتل دوا {fa(b)} {ML} دارد. کارمند صحی گفته است: هر روز {fa(d)} {ML}.", f"A bottle of medicine holds {b} millilitres. The health worker said: {d} millilitres every day."),
                 (f"یک بوتل دوا {fa(b)} {ML} دارد. روی بوتل نوشته است: هر روز {fa(d)} {ML}.", f"A bottle of medicine holds {b} millilitres. The writing on the bottle says: {d} millilitres every day.")][i % 2]
        lasts.append(ask(f"{first[0]} بوتل برای چند روز بس است؟", f"{first[1]} For how many days does the bottle last?", b // d, [b - d, d, b // d + 1, b // d * 2],
                         f"می{Z}شماریم که چند بار {fa(d)} در {fa(b)} جای می{Z}شود. {fa(b)} تقسیم {fa(d)} مساوی {fa(b // d)}. {DOSE_RULE[0]}",
                         f"We count how many times {d} goes into {b}. {b} divided by {d} equals {b // d}. {DOSE_RULE[1]}"))
    for i, (b, d) in enumerate((b, d) for b in (500, 750, 1000) for d in (25, 50, 100, 125, 250) if b % d == 0):
        oil.append(ask(f"یک بوتل روغن {fa(b)} {ML} دارد. هر روز {fa(d)} {ML} در پخت{Z}وپز مصرف می{Z}شود. بوتل برای چند روز بس است؟",
                       f"A bottle of oil holds {b} millilitres. Every day {d} millilitres are used for cooking. For how many days does the bottle last?", b // d, [b - d, d, b // d + 1, b // d - 1],
                       f"می{Z}شماریم که چند بار {fa(d)} در {fa(b)} جای می{Z}شود. {fa(b)} تقسیم {fa(d)} مساوی {fa(b // d)}.", f"We count how many times {d} goes into {b}. {b} divided by {d} equals {b // d}."))
    for i, (b, d, k) in enumerate((b, d, k) for b in (250, 500, 750, 1000) for d in (20, 25, 50) for k in (3, 4, 5, 6, 8) if b - d * k >= 50):
        liq, liq_en = [("روغن", "oil"), ("شیر", "milk"), ("آب لیمو", "lemon juice")][i % 3]
        left.append(ask(f"در بوتل {fa(b)} {ML} {liq} بود. {fa(k)} روز، هر روز {fa(d)} {ML} از آن گرفته شد. چند {ML} مانده است؟",
                        f"There were {b} millilitres of {liq_en} in the bottle. For {k} days, {d} millilitres were taken from it every day. How many millilitres are left?", b - d * k, [b - d, d * k, b - d * k + d, b - k],
                        f"{fa(k)} ضرب {fa(d)} مساوی {fa(d * k)}. {fa(b)} منفی {fa(d * k)} مساوی {fa(b - d * k)}.", f"{k} times {d} equals {d * k}. {b} minus {d * k} equals {b - d * k}."))
    pool6(s, "mason", "07", I_BOTTLE, [(lasts, 6), (oil, 6), (left, 6)], cap=3)

    conv, cups, total = [], [], []
    litre = (f"یک لیتر هزار {ML} است.", "One litre is 1000 millilitres.")
    for word, en, ml, why, why_en in [("نیم لیتر", "half a litre", 500, "نیم هزار، پنج" + Z + "صد است.", "Half of 1000 is 500."), ("چارک لیتر", "a quarter of a litre", 250, "هزار تقسیم چهار مساوی دوصد و پنجاه.", "1000 divided by 4 equals 250."),
                                      ("سه چارک لیتر", "three quarters of a litre", 750, "چارک آن دوصد و پنجاه است. سه ضرب دوصد و پنجاه مساوی هفت" + Z + "صد و پنجاه.", "A quarter of it is 250. 3 times 250 equals 750."),
                                      ("یک و نیم لیتر", "one and a half litres", 1500, "هزار جمع پنج" + Z + "صد مساوی یک هزار و پنج" + Z + "صد.", "1000 plus 500 equals 1500."),
                                      ("دو لیتر", "2 litres", 2000, "دو ضرب هزار مساوی دو هزار.", "2 times 1000 equals 2000."), ("دو و نیم لیتر", "two and a half litres", 2500, "دو هزار جمع پنج" + Z + "صد مساوی دو هزار و پنج" + Z + "صد.", "2000 plus 500 equals 2500."),
                                      ("سه لیتر", "3 litres", 3000, "سه ضرب هزار مساوی سه هزار.", "3 times 1000 equals 3000."), ("پنج لیتر", "5 litres", 5000, "پنج ضرب هزار مساوی پنج هزار.", "5 times 1000 equals 5000."),
                                      ("ده لیتر", "10 litres", 10000, "ده ضرب هزار مساوی ده هزار.", "10 times 1000 equals 10000.")]:
        conv.append(ask(f"{word} چند {ML} است؟", f"How many millilitres is {en}?", ml, [ml // 10, ml * 10 if ml < 5000 else ml // 100, ml + 500, ml // 2], f"{litre[0]} {why}", f"{litre[1]} {why_en}"))
    for i, (c, lt) in enumerate((c, lt) for c in (100, 125, 200, 250, 500) for lt in (1, 2, 3)):
        liq, liq_en = [("شیر", "milk"), ("آب", "water"), ("دوغ", "doogh")][i % 3]
        k = 1000 * lt // c
        cups.append(ask(f"یک پیاله {fa(c)} {ML} می{Z}گیرد. برای {fa(lt)} لیتر {liq} چند پیاله لازم است؟", f"A cup holds {c} millilitres. How many cups are needed for {nn(lt, 'litre')} of {liq_en}?", k, [c // 10, k + 1, k - 1, k * 2],
                        f"{fa(lt)} لیتر {fa(1000 * lt)} {ML} است. {fa(1000 * lt)} تقسیم {fa(c)} مساوی {fa(k)}.", f"{nn(lt, 'litre')} {'is' if lt == 1 else 'are'} {1000 * lt} millilitres. {1000 * lt} divided by {c} equals {k}."))
    for i, (n, c) in enumerate((n, c) for c in (150, 200, 250) for n in range(3, 9)):
        liq, liq_en = [("چای", "tea"), ("شیر", "milk"), ("آب", "water")][i % 3]
        total.append(ask(f"{fa(n)} پیاله {liq} می{Z}ریزی، در هر پیاله {fa(c)} {ML}. همه چند {ML} می{Z}شود؟", f"You pour {n} cups of {liq_en}, {c} millilitres in each cup. How many millilitres is that altogether?", n * c, [n + c, n * c + c, n * c - c, n * 100],
                         f"{fa(n)} ضرب {fa(c)} مساوی {fa(n * c)}.", f"{n} times {c} equals {n * c}."))
    pool6(s, "mason", "08", I_LITRE_ML, [(conv, 6), (cups, 6), (total, 6)], cap=3)
    return s


def cap_fa(text: str) -> str:
    return text


# -- Twin Tiles ------------------------------------------------------------------

I_PAIR_PCT_FRAC = tr("هر فیصد را با کسر مساوی آن جوره کن.", "Pair each percent with the fraction equal to it.")
I_PAIR_PCT_DEC = tr("هر فیصد را با عدد اعشاری مساوی آن جوره کن.", "Pair each percent with the decimal number equal to it.")
I_PAIR_PCT_PIC = tr("هر شکل را با فیصد آن جوره کن.", "Pair each picture with its percent.")
I_PAIR_RATIO = tr("نسبت" + Z + "های مساوی را جوره کن.", "Pair the ratios that are equal.")


def pairs6(level: int) -> Sheet:
    s = Sheet(PAIRS_COLS)

    def pair(rnd, intro, a, b, say):
        row = s.add(round=rnd, intro_fa=intro, a=a, b=b, say_fa=say)
        PAIR_META.append((row, "same"))

    def fractions(rng):
        for p in (50, 25, 75, 10, 20, 30, 40, 60, 70, 80, 90, 5, 1, 15, 35, 45):
            k, n = pct_frac(p)
            pair("01", I_PAIR_PCT_FRAC, P(p), fr(k, n), tr(f"{fa_pct(p)} مساوی {fa_frac(k, n)}.", f"{p} percent equals {k}/{n}."))
    build(s, 6, "pairs", "01", fractions)

    def decimals(rng):
        for p in (50, 25, 75, 10, 20, 30, 40, 60, 70, 80, 90, 5, 1, 15, 65, 99):
            pair("02", I_PAIR_PCT_DEC, P(p), "t:" + dec2(p), tr(f"{fa_pct(p)} مساوی {fa_dec(dec2(p))}.", f"{p} percent equals {dec2(p)}."))
    build(s, 6, "pairs", "02", decimals)

    def pictures(rng):
        for n in GRID_PCTS:
            pair("03", I_PAIR_PCT_PIC, grid(n), P(n), tr(f"از صد خانه، {fa(n)} خانه: {fa_pct(n)}.", f"Out of 100 squares, {nn(n, 'square')}: {n} percent."))
    build(s, 6, "pairs", "03", pictures)

    def ratios(rng):
        for i, (a, b) in enumerate(RATIOS6):
            m = 2 + i % 3
            pair("04", I_PAIR_RATIO, R(a, b), R(a * m, b * m), tr(f"{fa_ratio(a, b)} مساوی {fa_ratio(a * m, b * m)}.", f"{a} to {b} equals {a * m} to {b * m}."))
    build(s, 6, "pairs", "04", ratios)
    return s


# -- Number Rain -------------------------------------------------------------------

def catch6(level: int) -> Sheet:
    s = Sheet(CATCH_COLS)

    def rule(rnd, say, targets, others, help_fa, test):
        assert len(targets) >= 5 and len(others) >= 5 and not set(targets) & set(others), (say, targets, others)
        assert all(len(x) - 2 <= 4 for x in targets + others), ("too wide for the round card", targets, others)
        assert len(set(targets)) == len(targets) and len(set(others)) == len(others)
        row = s.add(round=rnd, intro_fa=I_RAIN, say_fa=say, targets="|".join(targets), others="|".join(others), need=NEED, help_fa=help_fa)
        CATCH_META.append((row, test))

    half = Fraction(1, 2)
    percents = [1, 2, 4, 5, 8, 9, 10, 11, 15, 20, 24, 25, 26, 30, 35, 40, 45, 49, 50, 51, 55, 60, 65, 70, 74, 75, 76, 80, 85, 89, 90, 91, 92, 95, 96, 98, 99, 100]

    def compare(rng, say, help_fa, test, edge):
        yes, no = [p for p in percents if test(Fraction(p, 100))], [p for p in percents if not test(Fraction(p, 100))]
        ty = uniq([p for p in edge if p in yes] + rng.sample(yes, min(6, len(yes))))[:6]
        tn = uniq([p for p in edge if p in no] + rng.sample(no, min(6, len(no))))[:6]
        rule("01", say, [P(p) for p in ty], [P(p) for p in tn], help_fa, test)

    same_as = {   # a value -> its other spellings, at most four characters wide
        half: ["50%", "1/2", "0.5", "2/4", "3/6", "4/8", "5/10"], Fraction(1, 4): ["25%", "1/4", "0.25", "2/8", "3/12", "4/16"],
        Fraction(3, 4): ["75%", "3/4", "0.75", "6/8", "9/12"], Fraction(1, 10): ["10%", "1/10", "0.1", "2/20", "0.10"],
        Fraction(1, 5): ["20%", "1/5", "0.2", "2/10", "0.20", "3/15"], Fraction(1): ["100%", "2/2", "1.0", "4/4", "5/5", "3/3"],
        Fraction(2, 5): ["40%", "2/5", "0.4", "4/10", "0.40", "6/15"], Fraction(3, 5): ["60%", "3/5", "0.6", "6/10", "0.60", "9/15"],
    }

    def equal(rng, v, name, name_en, help_fa):
        others = [x for w, xs in same_as.items() if w != v for x in xs]
        rule("01", tr(f"هر چه را که مساوی {name} است بگیر.", f"Catch everything that is equal to {name_en}."), ["t:" + x for x in same_as[v]],
             ["t:" + x for x in rng.sample(others, 7)], help_fa, lambda x, v=v: x == v)

    def percent_rules(rng):
        look = tr("فیصد بزرگتر یعنی حصه بیشتر از صد. عددها را مقایسه کن.", "A bigger percent means a bigger part of the hundred. Compare the numbers.")
        for k, edge in ((50, (49, 51)), (25, (24, 26)), (75, (74, 76)), (90, (89, 91))):
            compare(rng, tr(f"فیصدهای بزرگتر از {fa_pct(k)} را بگیر.", f"Catch the percents bigger than {k} percent."), look, lambda x, k=k: x > Fraction(k, 100), edge + (k,))
        for k, edge in ((50, (49, 51)), (25, (24, 26)), (75, (74, 76)), (10, (9, 11))):
            compare(rng, tr(f"فیصدهای کوچکتر از {fa_pct(k)} را بگیر.", f"Catch the percents smaller than {k} percent."), look, lambda x, k=k: x < Fraction(k, 100), edge + (k,))
        compare(rng, tr(f"فیصدهای بین بیست و پنج و هفتاد و پنج {PCT} را بگیر.", "Catch the percents between 25 and 75 percent."),
                tr(f"این فیصدها از بیست و پنج {PCT} بزرگتر و از هفتاد و پنج {PCT} کوچکتر هستند.", "These percents are bigger than 25 percent and smaller than 75 percent."),
                lambda x: Fraction(1, 4) < x < Fraction(3, 4), (25, 26, 74, 75))
        equal(rng, half, "نیم", "a half", tr(f"نیم یعنی پنجاه {PCT}، یک بر دو، صفر اعشاریه پنج.", "A half means 50 percent, 1/2, 0.5."))
        equal(rng, Fraction(1, 4), "چارک", "a quarter", tr(f"چارک یعنی بیست و پنج {PCT}، یک بر چهار، صفر اعشاریه بیست و پنج.", "A quarter means 25 percent, 1/4, 0.25."))
        equal(rng, Fraction(3, 4), "سه چارک", "three quarters", tr(f"سه چارک یعنی هفتاد و پنج {PCT}، سه بر چهار، صفر اعشاریه هفتاد و پنج.", "Three quarters means 75 percent, 3/4, 0.75."))
        equal(rng, Fraction(1, 10), f"ده {PCT}", "10 percent", tr(f"ده {PCT} یعنی یک بر ده، صفر اعشاریه یک.", "10 percent means 1/10, 0.1."))
        equal(rng, Fraction(1, 5), f"بیست {PCT}", "20 percent", tr(f"بیست {PCT} یعنی یک بر پنج، صفر اعشاریه دو.", "20 percent means 1/5, 0.2."))
        equal(rng, Fraction(1), "یک پوره", "one whole", tr(f"یک پوره یعنی صد {PCT}. وقتی صورت و مخرج یکی است، کسر یک پوره است.", "One whole means 100 percent. When the numerator and the denominator are the same, the fraction is one whole."))
        equal(rng, Fraction(2, 5), f"چهل {PCT}", "40 percent", tr(f"چهل {PCT} یعنی چهار بر ده، که همان دو بر پنج است.", "40 percent means 4/10, which is the same as 2/5."))
        equal(rng, Fraction(3, 5), f"شصت {PCT}", "60 percent", tr(f"شصت {PCT} یعنی شش بر ده، که همان سه بر پنج است.", "60 percent means 6/10, which is the same as 3/5."))
    build(s, 6, "catch", "01", percent_rules)

    def ratio_rules(rng):
        bases = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 10), (2, 1), (3, 1), (4, 1), (5, 1), (10, 1)]
        for a, b in bases:
            yes = [R(a * m, b * m) for m in range(2, 10) if len(f"{a * m}:{b * m}") <= 4]
            no = [R(x * m, y * m) for x, y in bases if (x, y) != (a, b) for m in (1, 2, 3) if len(f"{x * m}:{y * m}") <= 4]
            no = uniq([R(b * 2, a * 2), R(b * 3, a * 3)] + rng.sample(no, 6)) if a != b else rng.sample(no, 7)
            no = [x for x in no if len(x) - 2 <= 4 and val(x) != Fraction(a, b)][:7]
            if a == b:
                help_fa = tr("در نسبت یک به یک هر دو عدد یکی است.", "In the ratio 1 to 1 both numbers are the same.")
            elif a == 1:
                help_fa = tr(f"در نسبت {fa_ratio(a, b)} عدد دوم {fa(b)} چند عدد اول است.", f"In the ratio {a} to {b} the second number is {b} times the first.")
            else:
                help_fa = tr(f"در نسبت {fa_ratio(a, b)} عدد اول {fa(a)} چند عدد دوم است.", f"In the ratio {a} to {b} the first number is {a} times the second.")
            rule("02", tr(f"نسبت{Z}های مساوی {fa_ratio(a, b)} را بگیر.", f"Catch the ratios equal to {a} to {b}."), rng.sample(yes, min(6, len(yes))), no, help_fa,
                 lambda x, v=Fraction(a, b): x == v)
    build(s, 6, "catch", "02", ratio_rules, small="eleven ratios have five or more equal ratios that fit a round card")
    return s


# -- Tables and Charts: the average as sharing out evenly ------------------------

I_CHART_MEAN = tr("گراف را ببین. اوسط یعنی اگر همه ستون" + Z + "ها را برابر کنیم، هر ستون چند خانه می" + Z + "شود.",
                  "Look at the chart. The average means: if we make all the columns equal, how many boxes does each column get?")
I_TABLE_MEAN = tr("جدول را ببین. اوسط یعنی اگر همه قطارها را برابر کنیم، هر قطار چند تا می" + Z + "شود.",
                  "Look at the table. The average means: if we make all the rows equal, how many does each row get?")


def charts6(level: int) -> Sheet:
    s = Sheet(LP_COLS)
    for r, names in enumerate(MEAN_CHARTS):
        rnd = f"{r + 1:02d}"
        cands = []
        for name in names:
            rows = CHARTS[name]
            values = [v for _, _, v in rows]
            total, m = sum(values), sum(values) // 3
            assert total % 3 == 0 and len(set(values)) == 3 and m in values, name
            bars = "bars" in name
            kw, ke, col, col_en = ("گراف", "chart", "ستون", "column") if bars else ("جدول", "table", "قطار", "row")
            sums = " جمع ".join(fa(v) for v in values) + f" مساوی {fa(total)}.", " plus ".join(str(v) for v in values) + f" equals {total}."
            mean_help = (f"{sums[0]} سه {col} است، پس {fa(total)} تقسیم سه مساوی {fa(m)}.", f"{sums[1]} There are 3 {col_en}s, so {total} divided by 3 equals {m}.")
            pics = [p for p, _, _ in rows] + [CHART_EXTRA[name]]
            nd, ne = "، ".join(n for _, n, _ in rows[:2]) + " و " + rows[2][1], ", ".join(many(n) for _, n, _ in rows[:2]) + " and " + many(rows[2][1])
            top = max(rows, key=lambda x: x[2])
            low = min(rows, key=lambda x: x[2])
            cands.append(ask(f"در این {kw} {nd} با هم چند تا است؟", f"In this {ke}, how many are the {ne} together?", total, [total - 1, total + 1, max(values), m], *sums, show=name))
            cands.append(ask(f"اگر {nd} این {kw} را یکجا کنیم و بین سه {col} برابر تقسیم کنیم، در هر {col} چند تا می{Z}شود؟",
                             f"If we put the {ne} of this {ke} together and share them out evenly among the 3 {col_en}s, how many are in each {col_en}?", m, [total, max(values), min(values) if min(values) != m else None, m + 2],
                             *mean_help, show=name, key=("mean", name)))
            cands.append(ask(f"در این {kw} اوسط {nd} چند است؟", f"In this {ke}, what is the average of the {ne}?", m, [total, max(values), min(values), m + 2], *mean_help, show=name, key=("mean2", name)))
            eq = next(x for x in rows if x[2] == m)
            cands.append(ask(f"اوسط این {kw} {fa(m)} است. کدام چیز درست به اندازه اوسط است؟", f"The average of this {ke} is {m}. Which thing is exactly as many as the average?", eq[0], [p for p in pics if p != eq[0]],
                             f"{eq[1]} {fa(m)} تا است، درست به اندازه اوسط.", f"There {'is' if m == 1 else 'are'} {m} of the {bare(eq[1])}, exactly the average.", show=name, key=name + "eq"))
            cands.append(ask(f"اوسط این {kw} {fa(m)} است. کدام چیز از اوسط بیشتر است؟", f"The average of this {ke} is {m}. Which thing is more than the average?", top[0], [p for p in pics if p != top[0]],
                             f"{top[1]} {fa(top[2])} تا است و {fa(top[2])} از {fa(m)} بیشتر است.", f"There are {top[2]} of the {bare(top[1])}, and {top[2]} is more than {m}.", show=name, key=name + "top"))
            d = top[2] - m
            cands.append(ask(f"در این {kw} از {col} {top[1]} چند تا را به {col} {low[1]} بدهیم تا هر سه {col} برابر شوند؟",
                             f"In this {ke}, how many must we move from the {col_en} of the {bare(top[1])} to the {col_en} of the {bare(low[1])} so that all three {col_en}s are equal?", d, [top[2], m, d + 1, d + 2],
                             f"اوسط {fa(m)} است. {col} {top[1]} {fa(top[2])} تا دارد. {fa(top[2])} منفی {fa(m)} مساوی {fa(d)}.", f"The average is {m}. The {col_en} of the {bare(top[1])} has {top[2]}. {top[2]} minus {m} equals {d}.", show=name, key=("move", name)))
            for pic, noun, v in rows:
                cands.append(ask(f"در این {kw} چند {noun} است؟", f"In this {ke}, how many {many(noun)} are there?", v, [x for x in values if x != v] + [v + 1],
                                 f"خانه{Z}های {noun} را بشمار: {fa(v)}.", f"Count the boxes of the {bare(noun)}: {v}.", show=name, key=("count", name, pic)))
        pool6(s, "charts", rnd, I_CHART_MEAN if "bars" in names[0] else I_TABLE_MEAN, [(cands, 20)], cap=3)
    return s


# -- Number Riddles ----------------------------------------------------------------

I_SAME_VALUE6 = tr("فیصد، کسر و عدد اعشاری: آن را پیدا کن که مساوی است.", "Percent, fraction and decimal number: find the one that is equal.")
I_BIGGEST6 = tr("همه را به فیصد برگردان و ببین کدام از همه بزرگتر یا کوچکتر است.", "Turn them all into percents and see which one is the biggest or the smallest.")
I_RATIO_GAP = tr("در نسبت یک عدد کم است. آن را پیدا کن.", "One number is missing in the ratio. Find it.")
I_MEAN_GAP = tr("اوسط را می" + Z + "دانی. عددی را که کم است پیدا کن.", "You know the average. Find the number that is missing.")
I_REST_PCT = tr("همه صد فیصد است. حساب کن که باقی چند فیصد است.", "All of it is 100 percent. Work out what percent the rest is.")
REST_STORIES = [
    (lambda p: f"{fa_pct(p)} شاگردان صنف دختر هستند. چند {PCT} بچه هستند؟", lambda p: f"{p} percent of the pupils of the class are girls. What percent are boys?"),
    (lambda p: f"دهقان {fa_pct(p)} زمین را گندم کاشت و باقی را جواری. چند {PCT} زمین جواری است؟", lambda p: f"The farmer sowed wheat on {p} percent of the land and maize on the rest. What percent of the land is maize?"),
    (lambda p: f"{fa_pct(p)} راه را رفته{Z}ای. چند {PCT} راه مانده است؟", lambda p: f"You have gone {p} percent of the way. What percent of the way is left?"),
    (lambda p: f"یک خانواده {fa_pct(p)} عاید خود را مصرف می{Z}کند و باقی را پس{Z}انداز. چند {PCT} عاید پس{Z}انداز می{Z}شود؟", lambda p: f"A family spends {p} percent of its income and saves the rest. What percent of the income is saved?"),
    (lambda p: f"{fa_pct(p)} شاگردان صنف بچه هستند. چند {PCT} دختر هستند؟", lambda p: f"{p} percent of the pupils of the class are boys. What percent are girls?"),
    (lambda p: f"از تخم{Z}های زیر مرغ {fa_pct(p)} چوچه شد. چند {PCT} چوچه نشد؟", lambda p: f"Of the eggs under the hen, {p} percent hatched. What percent did not hatch?"),
    (lambda p: f"سطل {fa_pct(p)} پر است. چند {PCT} آن خالی است؟", lambda p: f"The bucket is {p} percent full. What percent of it is empty?"),
]
REST3_STORIES = [
    (lambda a, b: f"یک خانواده {fa_pct(a)} عاید را برای خوراک و {fa_pct(b)} را برای چیزهای دیگر مصرف می{Z}کند. باقی پس{Z}انداز می{Z}شود. چند {PCT} پس{Z}انداز می{Z}شود؟",
     lambda a, b: f"A family spends {a} percent of its income on food and {b} percent on other things. The rest is saved. What percent is saved?"),
    (lambda a, b: f"در باغ {fa_pct(a)} درخت{Z}ها سیب و {fa_pct(b)} انار است. باقی چهارمغز است. چند {PCT} درخت{Z}ها چهارمغز است؟",
     lambda a, b: f"In the garden {a} percent of the trees are apple and {b} percent pomegranate. The rest are walnut. What percent of the trees are walnut?"),
    (lambda a, b: f"دهقان {fa_pct(a)} زمین را گندم، {fa_pct(b)} را کچالو و باقی را پیاز کاشت. چند {PCT} زمین پیاز است؟",
     lambda a, b: f"The farmer sowed {a} percent of the land with wheat, {b} percent with potatoes and the rest with onions. What percent of the land is onions?"),
]


def riddles6(level: int) -> Sheet:
    s = Sheet(LP_COLS)
    base = [50, 25, 75, 10, 20, 30, 40, 60, 70, 80, 90, 5, 1]

    c1 = []
    for i, p in enumerate(base):
        forms = forms6(p)
        others = [forms6(q) for q in base[i + 1:] + base[:i]]
        for a, b in ((0, 1), (0, 2), (1, 0), (2, 1), (1, 2), (2, 0)):
            (shown, (sd, se)), (right, (rd, re_)) = forms[a], forms[b]
            wrong = [o[b][0] for o in others[:3]] + [o[(b + 1) % 3][0] for o in others[3:6] if (b + 1) % 3 != a] + [o[b][0] for o in others[6:]]
            if b == 0:
                wrong = near_pcts(p)
            c1.append(ask(f"کدام با {sd} مساوی است؟", f"Which one is equal to {se}?", right, wrong,
                          f"{sd} یعنی {fa_frac(p, 100)}، یعنی {fa_pct(p)}. جواب {rd} است.", f"{se} means {p}/100, that is {p} percent. The answer is {re_}.", show=shown, key=(p, a, b)))
    pool6(s, "riddles", "01", I_SAME_VALUE6, [(c1, N)])

    c2 = []
    rng = rng_for("riddles6", "biggest")
    seen = set()
    while len(c2) < 40:
        picks = tuple(sorted(rng.sample([10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90], 4)))
        shift = rng.randrange(3)
        if (picks, shift) in seen:
            continue
        seen.add((picks, shift))
        chosen = [forms6(p)[(i + shift) % 3] for i, p in enumerate(picks)]
        spoken = dict(chosen)
        biggest = len(c2) % 2 == 0
        (right, (rd, re_)), want = (chosen[-1], picks[-1]) if biggest else (chosen[0], picks[0])
        ld, le = said_list([t for t, _ in chosen], lambda t: spoken[t])
        turned = "، ".join(f"{spoken[t][0]} یعنی {fa_pct(p)}" for (t, _), p in zip(chosen, picks) if t != P(p))
        turned_en = ", ".join(f"{spoken[t][1]} means {p} percent" for (t, _), p in zip(chosen, picks) if t != P(p))
        word, word_en = ("بزرگتر", "biggest") if biggest else ("کوچکتر", "smallest")
        c2.append(ask(f"{ld}. کدام از همه {word} است؟", f"{le}. Which one is the {word_en}?", right, [t for t, _ in chosen if t != right],
                      f"همه را به {PCT} برگردان: {turned}. {fa_pct(want)} از همه {word} است.", f"Turn them all into percents: {turned_en}. {want} percent is the {word_en}.", key=(want, biggest)))
    pool6(s, "riddles", "02", I_BIGGEST6, [(c2, N)], cap=3)

    c3 = []
    for i, (a, b, m) in enumerate((a, b, m) for a, b in RATIOS6 for m in (2, 3, 4, 5, 6)):
        if i % 2 == 0:
            c3.append(ask(f"{fa_ratio(a, b)} مساوی {fa(a * m)} به چند است؟", f"{a} to {b} is equal to {a * m} to how many?", b * m, [b + a * m - a, a * m, b * m + b, b * m - 1],
                          f"{fa(a)} ضرب {fa(m)} مساوی {fa(a * m)}. پس {fa(b)} را هم در {fa(m)} ضرب کن: {fa(b * m)}.", f"{a} times {m} equals {a * m}. So multiply {b} by {m} too: {b * m}."))
        else:
            c3.append(ask(f"چند به {fa(b * m)} مساوی {fa_ratio(a, b)} است؟", f"How many to {b * m} is equal to {a} to {b}?", a * m, [a + b * m - b, b * m, a * m + a, a * m + 1],
                          f"{fa(b)} ضرب {fa(m)} مساوی {fa(b * m)}. پس {fa(a)} را هم در {fa(m)} ضرب کن: {fa(a * m)}.", f"{b} times {m} equals {b * m}. So multiply {a} by {m} too: {a * m}."))
    pool6(s, "riddles", "03", I_RATIO_GAP, [(c3, N)])

    c4 = []
    for nums in mean_lists("gap3", 3, 2, 18, 40) + mean_lists("gap4", 4, 2, 15, 20):
        k, m, known, gap = len(nums), sum(nums) // len(nums), nums[:-1], nums[-1]
        ld, le = fa_list(known)
        count, count_en = ("سه", "three") if k == 3 else ("چهار", "four")
        rest, rest_en = (("دو عدد آن", "Two of them are"), ("سه عدد آن", "Three of them are"))[k - 3]
        last, last_en = ("سوم", "third") if k == 3 else ("چهارم", "fourth")
        c4.append(ask(f"اوسط {count} عدد {fa(m)} است. {rest} {ld} است. عدد {last} چند است؟", f"The average of {count_en} numbers is {m}. {rest_en} {le}. What is the {last_en} number?", gap,
                      [m if m != gap else None, k * m, sum(known), gap + 1, gap - 1],
                      f"اوسط {fa(m)} است و {count} عدد است، پس جمع همه {fa(k)} ضرب {fa(m)} مساوی {fa(k * m)} است. " + " جمع ".join(fa(x) for x in known) + f" مساوی {fa(sum(known))}. {fa(k * m)} منفی {fa(sum(known))} مساوی {fa(gap)}.",
                      f"The average is {m} and there are {count_en} numbers, so the sum of all is {k} times {m} equals {k * m}. " + " plus ".join(str(x) for x in known) + f" equals {sum(known)}. {k * m} minus {sum(known)} equals {gap}."))
    pool6(s, "riddles", "04", I_MEAN_GAP, [(c4, N)])

    two, three = [], []
    whole = (f"همه صد {PCT} است.", "All of it is 100 percent.")
    for i, p in enumerate([10, 15, 20, 25, 30, 35, 40, 45, 55, 60, 65, 70, 75, 80, 85, 90, 95, 5]):
        d, e = REST_STORIES[i % len(REST_STORIES)]
        two.append(ask(d(p), e(p), P(100 - p), [P(p)] + near_pcts(100 - p), f"{whole[0]} صد منفی {fa(p)} مساوی {fa(100 - p)}.", f"{whole[1]} 100 minus {p} equals {100 - p}."))
    for i, (a, b) in enumerate((a, b) for a in (30, 40, 50, 60, 45, 55) for b in (10, 20, 25, 30, 35) if a + b < 100):
        d, e = REST3_STORIES[i % len(REST3_STORIES)]
        r = 100 - a - b
        three.append(ask(d(a, b), e(a, b), P(r), [P(a + b), P(100 - a), P(100 - b)] + near_pcts(r),
                         f"{whole[0]} {fa(a)} جمع {fa(b)} مساوی {fa(a + b)}. صد منفی {fa(a + b)} مساوی {fa(r)}.", f"{whole[1]} {a} plus {b} equals {a + b}. 100 minus {a + b} equals {r}."))
    pool6(s, "riddles", "05", I_REST_PCT, [(two, 10), (three, 8)])
    return s


# -- True or False -------------------------------------------------------------------

I_TRUE_PCT = tr("فیصد و کسر یا عدد اعشاری: مساوی هستند؟ درست یا غلط؟", "A percent and a fraction or decimal number: are they equal? True or false?")
I_TRUE_RATIO = tr("دو نسبت مساوی هستند؟ درست یا غلط؟", "Are the two ratios equal? True or false?")
I_TRUE_MEAN = tr("اوسط این عددها همین است؟ درست یا غلط؟", "Is this the average of these numbers? True or false?")


def truefalse6(level: int) -> Sheet:
    s = Sheet(SORTER_COLS)

    def percent(rng):
        base = [50, 25, 75, 10, 20, 30, 40, 60, 70, 80, 90, 5]
        picks = rng.sample([(p, kind) for p in base for kind in (1, 2)], N)
        for i, (p, kind) in enumerate(picks):
            true = i % 2 == 0
            q = p if true else rng.choice([x for x in base if x != p and abs(x - p) <= 30] + ([p // 10] if p % 10 == 0 and kind == 2 and p >= 20 else []))
            if kind == 1 and not true and i % 4 == 1 and Fraction(1, p) != Fraction(p, 100):
                thing, (d, e) = fr(1, p), (fa_frac(1, p), f"1/{p}")   # the classic mistake: 20 percent = 1/20
            elif kind == 2 and not true and q < 10 and q != 5:
                thing, (d, e) = "t:" + dec2(q), (fa_dec(dec2(q)), dec2(q))
            else:
                thing, (d, e) = forms6(q)[kind]
            tf_row(s, "01", I_TRUE_PCT, f"t:{p}% = {thing[2:]}", tr(f"{fa_pct(p)} مساوی {d} است.", f"{p} percent is equal to {e}."), true)
            assert (val(thing) == Fraction(p, 100)) == true, (p, thing)
    build(s, 6, "truefalse", "01", percent)

    def ratio(rng):
        picks = rng.sample([(a, b, m) for a, b in RATIOS6 for m in (2, 3, 4) if a * m <= 20 and b * m <= 20], N)
        for i, (a, b, m) in enumerate(picks):
            true = i % 2 == 0
            x, y = (a * m, b * m) if true else [(a + m, b + m), (b * m, a * m), (a * m, b * m + b)][i % 3]
            assert (Fraction(x, y) == Fraction(a, b)) == true
            tf_row(s, "02", I_TRUE_RATIO, f"t:{a}:{b} = {x}:{y}", tr(f"{fa_ratio(a, b)} مساوی {fa_ratio(x, y)} است.", f"{a} to {b} is equal to {x} to {y}."), true)
    build(s, 6, "truefalse", "02", ratio)

    def mean(rng):
        lists = mean_lists("tf3", 3, 1, 12, 12) + mean_lists("tf4", 4, 1, 9, 6)
        for i, nums in enumerate(rng.sample(lists, N)):
            true = i % 2 == 0
            m = sum(nums) // len(nums)
            wrong = [x for x in (sorted(nums)[1], max(nums), m + 1, m - 1, sum(nums)) if x != m and x > 0]
            claim = m if true else wrong[i % 3 % len(wrong)]
            ld, le = fa_list(nums)
            row_n = len(s.rows)
            tf_row(s, "03", I_TRUE_MEAN, "t:" + ", ".join(str(x) for x in nums), tr(f"اوسط {ld}، {fa(claim)} است.", f"The average of {le} is {claim}."), true)
            L6_META.append((s.rows[row_n], lambda r, claim=claim: (lambda xs: (sum(xs) == claim * len(xs)) == (r["basket"] == "yes"))([int(x) for x in r["thing"][2:].split(", ")])))
    build(s, 6, "truefalse", "03", mean)
    return s


# -- The Cooking Pot: ratio through recipes and mixing, sharing in a ratio ---------

I_RATIO = tr("نسبت می" + Z + "گوید از هر چیز چند حصه می" + Z + "گیریم. نسبت را پیدا کن.", "A ratio tells how many parts of each thing we take. Find the ratio.")
I_RATIO_UP = tr("دیگ کلان" + Z + "تر می" + Z + "پزیم: هر دو چیز را به یک اندازه زیاد کن.", "We cook a bigger pot: make both things bigger by the same amount.")
I_RATIO_SAME = tr("نسبت مساوی را پیدا کن: هر دو عدد را در یک عدد ضرب یا بر یک عدد تقسیم کن.", "Find the equal ratio: multiply both numbers by the same number, or divide both by the same number.")
I_RATIO_SHARE = tr("به نسبت تقسیم کن: اول حصه" + Z + "ها را جمع کن.", "Share in the ratio: first add the parts.")
I_RATIO_PARTS = tr("از نسبت و یک عدد، عدد دیگر را پیدا کن.", "From the ratio and one number, find the other number.")
# what we mix: the two things, the measure, the pot, a picture, and the ratios used
RECIPES = [
    ("برنج", "rice", "آب", "water", "پیاله", "cup", "برای پلو", "For the rice", "rice", [(2, 3), (1, 2), (3, 4)]),
    ("شیر", "milk", "آب", "water", "پیاله", "cup", "برای شیرچای", "For milk tea", "milk", [(1, 2), (1, 3), (2, 3)]),
    ("آرد", "flour", "آب", "water", "پیاله", "cup", "برای خمیر", "For the dough", "flour_sack", [(3, 1), (5, 2), (2, 1)]),
    ("ماست", "yoghurt", "آب", "water", "پیاله", "cup", "برای دوغ", "For doogh", "yoghurt", [(1, 2), (1, 3), (2, 5)]),
    ("ریگ", "sand", "سمنت", "cement", "بیل", "shovel", "برای مصاله دیوار", "For the mortar of a wall", "brick", [(3, 1), (4, 1), (5, 2)]),
    ("خاک", "earth", "کاه", "straw", "سطل", "bucket", "برای کاه" + Z + "گل", "For mud plaster", "bucket", [(4, 1), (5, 1), (3, 2)]),
    ("جو", "barley", "کاه", "straw", "کیلو", "kilo", "برای خوراک گاو", "For the cow's feed", "cow", [(1, 3), (1, 4), (2, 5)]),
]
TIMES_FA = {2: "دو چند", 3: "سه چند", 4: "چهار چند", 5: "پنج چند", 6: "شش چند"}
SHARE_STORIES = [
    (lambda a, b, t: f"دو همسایه یک کشتزار را با هم کار کردند: یکی {fa(a)} روز و دیگری {fa(b)} روز. آنها {fa(t)} کیلو گندم را به نسبت {fa_ratio(a, b)} تقسیم می{Z}کنند.",
     lambda a, b, t: f"Two neighbours worked a field together: one for {nn(a, 'day')} and the other for {nn(b, 'day')}. They share {t} kilos of wheat in the ratio {a} to {b}.", "کیلو", "kilos"),
    (lambda a, b, t: f"دو خواهر با هم قالین بافتند. آنها {fa(t)} {AFN} را به نسبت {fa_ratio(a, b)} تقسیم می{Z}کنند.",
     lambda a, b, t: f"Two sisters wove a carpet together. They share {t} afghani in the ratio {a} to {b}.", AFN, "afghani"),
    (lambda a, b, t: f"دو برادر {fa(t)} چهارمغز جمع کردند و آن را به نسبت {fa_ratio(a, b)} تقسیم می{Z}کنند.",
     lambda a, b, t: f"Two brothers gathered {t} walnuts and share them in the ratio {a} to {b}.", "چهارمغز", "walnuts"),
    (lambda a, b, t: f"نانوا {fa(t)} نان را بین دو خانواده به نسبت {fa_ratio(a, b)} تقسیم می{Z}کند.",
     lambda a, b, t: f"The baker shares {t} loaves of bread between two families in the ratio {a} to {b}.", "نان", "loaves"),
]
GROUP_RATIOS = [("بز", "goats", "گوسفند", "sheep", "در رمه", "In the flock"), ("دختر", "girls", "بچه", "boys", "در صنف", "In the class"),
                ("درخت سیب", "apple trees", "درخت انار", "pomegranate trees", "در باغ", "In the garden"), ("مرغ سفید", "white hens", "مرغ سیاه", "black hens", "در حویلی", "In the yard"),
                ("بچه", "boys", "دختر", "girls", "در صنف", "In the class")]


def ratio6(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    c1, c2 = [], []
    for A, A_en, B_, B_en, unit, unit_en, pot, pot_en, pic, pairs in RECIPES:
        for a, b in pairs:
            first = (f"{pot} {fa(a)} {unit} {A} و {fa(b)} {unit} {B_} می{Z}گیریم.", f"{pot_en} we take {nn(a, unit_en)} of {A_en} and {nn(b, unit_en)} of {B_en}.")
            c1.append(ask(f"{first[0]} نسبت {A} به {B_} چند است؟", f"{first[1]} What is the ratio of {A_en} to {B_en}?", R(a, b), [R(b, a), R(a, a + b), R(b, a + b), R(a + 1, b), R(a, b + 1)],
                          f"اول {A}: {fa(a)}. بعد {B_}: {fa(b)}. نسبت {A} به {B_}، {fa_ratio(a, b)} است.", f"First the {A_en}: {a}. Then the {B_en}: {b}. The ratio of {A_en} to {B_en} is {a} to {b}.", show=pic))
            c1.append(ask(f"{first[0]} نسبت {B_} به {A} چند است؟", f"{first[1]} What is the ratio of {B_en} to {A_en}?", R(b, a), [R(a, b), R(b, a + b), R(a, a + b), R(b + 1, a), R(b, a + 1)],
                          f"اول {B_}: {fa(b)}. بعد {A}: {fa(a)}. نسبت {B_} به {A}، {fa_ratio(b, a)} است.", f"First the {B_en}: {b}. Then the {A_en}: {a}. The ratio of {B_en} to {A_en} is {b} to {a}.", show=pic))
            for m in (2, 3, 4, 5):
                c2.append(ask(f"{pot} برای {fa(a)} {unit} {A}، {fa(b)} {unit} {B_} لازم است. برای {fa(a * m)} {unit} {A} چند {unit} {B_} لازم است؟",
                              f"{pot_en}, {nn(a, unit_en)} of {A_en} {'needs' if a == 1 else 'need'} {nn(b, unit_en)} of {B_en}. How many {unit_en}s of {B_en} are needed for {nn(a * m, unit_en)} of {A_en}?", b * m,
                              [b + a * m - a, a * m, b * m + b, b * m - b if m > 2 else b * m + 1],
                              f"{A} {TIMES_FA[m]} شده است: {fa(a)} ضرب {fa(m)} مساوی {fa(a * m)}. پس {B_} هم {TIMES_FA[m]} می{Z}شود: {fa(b)} ضرب {fa(m)} مساوی {fa(b * m)}.",
                              f"The {A_en} is {m} times as much: {a} times {m} equals {a * m}. So the {B_en} is {m} times as much too: {b} times {m} equals {b * m}.", show=pic))
    pool6(s, "ratio", "01", I_RATIO, [(c1, N)], cap=3)
    pool6(s, "ratio", "02", I_RATIO_UP, [(c2, N)])

    c3 = []
    for i, (a, b, m) in enumerate((a, b, m) for a, b in RATIOS6 for m in (2, 3, 4, 5) if a * m <= 20 and b * m <= 20):
        if i % 3 < 2:
            c3.append(ask(f"کدام نسبت با {fa_ratio(a, b)} مساوی است؟", f"Which ratio is equal to {a} to {b}?", R(a * m, b * m), [R(a + m, b + m), R(b * m, a * m), R(a * m, b * m + b), R(a * m + a, b * m), R(a * m, b)],
                          f"هر دو عدد را در {fa(m)} ضرب کن: {fa(a)} ضرب {fa(m)} مساوی {fa(a * m)} و {fa(b)} ضرب {fa(m)} مساوی {fa(b * m)}.",
                          f"Multiply both numbers by {m}: {a} times {m} equals {a * m} and {b} times {m} equals {b * m}.", show=R(a, b), key=(a, b, m)))
        else:
            c3.append(ask(f"{fa_ratio(a * m, b * m)} را ساده کن. کدام نسبت است؟", f"Simplify {a * m} to {b * m}. Which ratio is it?", R(a, b), [R(b, a), R(a + 1, b), R(a, b + 1), R(a * m, b), R(a, b * m)],
                          f"هر دو عدد را بر {fa(m)} تقسیم کن: {fa(a * m)} تقسیم {fa(m)} مساوی {fa(a)} و {fa(b * m)} تقسیم {fa(m)} مساوی {fa(b)}.",
                          f"Divide both numbers by {m}: {a * m} divided by {m} equals {a} and {b * m} divided by {m} equals {b}.", show=R(a * m, b * m), key=(a, b, m)))
    pool6(s, "ratio", "03", I_RATIO_SAME, [(c3, N)])

    c4 = []
    for i, (a, b, u) in enumerate((a, b, u) for a, b in ((1, 2), (2, 3), (1, 3), (3, 2), (1, 4), (3, 4), (2, 1), (3, 5), (3, 1), (2, 5)) for u in (2, 3, 4, 5, 6, 8, 10, 20)):
        d, e, unit, unit_en = SHARE_STORIES[i % len(SHARE_STORIES)]
        if unit == AFN:
            u *= 50
        t = u * (a + b)
        first = i % 3 != 2
        part, k = (a * u, a) if first else (b * u, b)
        who, who_en = ("اول", "first") if first else ("دوم", "second")
        c4.append(ask(f"{d(a, b, t)} حصه {who} چند {unit} است؟", f"{e(a, b, t)} How many {unit_en} is the {who_en} share?", part, [t // 2 if t // 2 != part else None, (b if first else a) * u, u, t - k, part + u],
                      f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)} حصه. {fa(t)} تقسیم {fa(a + b)} مساوی {fa(u)}: هر حصه {fa(u)} است. حصه {who} {fa(k)} حصه دارد: {fa(k)} ضرب {fa(u)} مساوی {fa(part)}.",
                      f"{a} plus {b} equals {a + b} parts. {t} divided by {a + b} equals {u}: each part is {u}. The {who_en} share has {nn(k, 'part')}: {k} times {u} equals {part}."))
    pool6(s, "ratio", "04", I_RATIO_SHARE, [(c4, N)])

    other, total = [], []
    for i, (a, b, m) in enumerate((a, b, m) for a, b in ((1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (2, 5), (1, 1), (3, 2)) for m in (2, 3, 4, 5, 6, 8)):
        X, X_en, Y, Y_en, where, where_en = GROUP_RATIOS[i % len(GROUP_RATIOS)]
        head = (f"{where} نسبت {X} به {Y}، {fa_ratio(a, b)} است.", f"{where_en} the ratio of {X_en} to {Y_en} is {a} to {b}.")
        other.append(ask(f"{head[0]} {fa(a * m)} {X} است. چند {Y} است؟", f"{head[1]} There are {a * m} {X_en}. How many {Y_en} are there?", b * m, [b + a * m - a, a * m if a != b else None, (a + b) * m, b * m + b],
                         f"{fa(a)} حصه {fa(a * m)} تا است، پس هر حصه {fa(m)} تا است. {Y} {fa(b)} حصه است: {fa(b)} ضرب {fa(m)} مساوی {fa(b * m)}.",
                         f"{nn(a, 'part')} {'is' if a == 1 else 'are'} {a * m}, so each part is {m}. The {Y_en} are {nn(b, 'part')}: {b} times {m} equals {b * m}."))
        t = (a + b) * m
        total.append(ask(f"{head[0]} همه با هم {fa(t)} تا هستند. چند {X} است؟", f"{head[1]} Altogether there are {t}. How many {X_en} are there?", a * m, [b * m if a != b else None, t // 2 if t // 2 != a * m else None, m, t - a],
                         f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)} حصه. {fa(t)} تقسیم {fa(a + b)} مساوی {fa(m)}. {X} {fa(a)} حصه است: {fa(a)} ضرب {fa(m)} مساوی {fa(a * m)}.",
                         f"{a} plus {b} equals {a + b} parts. {t} divided by {a + b} equals {m}. The {X_en} are {nn(a, 'part')}: {a} times {m} equals {a * m}."))
    pool6(s, "ratio", "05", I_RATIO_PARTS, [(other, 9), (total, 9)])
    return s


for _name, _text in {   # library pictures that level 6 is the first math level to use
    "pot": "a cooking pot with a lid (icon of The Cooking Pot)",
    "purse": "a small cloth purse for coins",
    "money": "a few banknotes and coins, no writing",
    "milk": "a glass of milk",
    "yoghurt": "a bowl of white yoghurt",
    "bucket": "a metal bucket",
    "wheat": "three ears of wheat",
    "farmer": "a farmer standing with a tool, whole clothed figure",
}.items():
    PICTURES.setdefault(_name, _text)
for _n in GRID_PCTS:
    PICTURES[f"pct_{_n}"] = (f"a hundred square, ten rows of ten small squares; the first {_n} squares, row by row from the top, are filled yellow, "
                             "the others white (drawn by content/math/draw_pictures.py)")
for _k in range(1, CUP_MARKS + 1):
    PICTURES[f"cup_marks_{_k}"] = (f"a clear measuring cup with {CUP_MARKS} marks on its side and no digits, filled with blue liquid exactly up to mark {_k} "
                                   "counted from the bottom (drawn by content/math/draw_pictures.py)")
for _name, (_places, (_n1, _n2)) in MAPS6.items():
    PICTURES[_name] = (f"a simple drawn map of an invented village area: {_places[0][0]} top left, {_places[1][0]} top right, {_places[2][0]} bottom right; "
                       f"a straight road of {_n1} pieces from the first to the second and a straight road of {_n2} pieces down to the third, "
                       "the pieces coloured in turn like a scale bar (drawn by content/math/draw_pictures.py)")
for _name in ("chart_bars_7", "chart_table_7", "chart_bars_8", "chart_table_8"):
    _what = ", ".join(f"{_v} {_p}" for _p, _, _v in CHARTS[_name])
    PICTURES[_name] = ((f"a block chart with three columns, a small picture under each column and one block per unit: {_what}" if "bars" in _name else
                        f"a picture table with three rows read from the right: a small picture, then one dot per unit: {_what}")
                       + " (drawn by content/math/draw_pictures.py)")


def check_answers6(games: list) -> None:
    """Level 6 once more, from the finished rows."""
    for row, test in L6_META:
        assert test(row), row
    doses = 0
    for game, sheet in games:
        for row in sheet.rows:
            text = row.get("say_fa", "")
            if re.search("(?<![؀-ۿ])دوا(?![؀-ۿ])", text):   # the word itself, not the start of «دوازده»
                doses += 1
                assert "کارمند صحی گفته است" in text or "نوشته است" in text, ("a dose without its source", row)
                assert DOSE_RULE[0] in row["help_fa"], ("a dose without the rule", row)
    assert doses >= 10, doses
    for name, (places, (n1, n2)) in MAPS6.items():
        assert len({p[0] for p in places}) == 3 and 1 <= n1 <= 4 and 1 <= n2 <= 4 and n1 != n2, name


# ---------------------------------------------------------------------------
# Packs
# ---------------------------------------------------------------------------

GAMES = [
    dict(id="count_the_flock", engine="listen_pick", letter="a", title_en="Count the Flock", title_fa="رمه را بشمار",
         intro_fa=tr("بشمار و عدد درست را انتخاب کن.", "Count and choose the right number."), icon="sheep", v1=True, sheet="count_the_flock.csv", make=flock),
    dict(id="number_hop", engine="journey", letter="b", title_en="Number Hop", title_fa="خیز عددها",
         intro_fa=tr("حساب کن و جواب درست را انتخاب کن.", "Work it out and choose the right answer."), icon="frog", v1=True, sheet="number_hop.csv", make=hop),
    dict(id="market_scales", engine="market", letter="c", title_en="Market Scales", title_fa="ترازوی بازار",
         intro_fa={1: tr("گوش کن و همان قدر روی ترازو بگذار.", "Listen and put that many on the scales."), 2: tr("قیمت را گوش کن و با سکه" + Z + "ها و نوت" + Z + "ها پول بده.", "Listen to the price and pay with the coins and notes."),
                   3: tr("حساب کن و با سکه" + Z + "ها و نوت" + Z + "ها پول بده.", "Work it out and pay with the coins and notes."),
                   4: tr("حساب کن و با سکه" + Z + "ها و نوت" + Z + "ها پول بده.", "Work it out and pay with the coins and notes."),
                   5: tr("حساب کن و با سکه" + Z + "ها و نوت" + Z + "ها پول بده.", "Work it out and pay with the coins and notes."),
                   6: tr("حساب کن و با سکه" + Z + "ها و نوت" + Z + "ها پول بده.", "Work it out and pay with the coins and notes.")},
         icon="scales", sheet="market_scales.csv", make=market),
    dict(id="carpet_weaver", engine="builder", letter="d", title_en="Carpet Weaver", title_fa="قالین" + Z + "باف",
         intro_fa=tr("عددها را به ترتیب درست بگذار.", "Put the numbers in the right order."), icon="carpet", sheet="carpet_weaver.csv", make=weaver),
    dict(id="share_the_bread", engine="sorter", letter="e", title_en="Share the Bread", title_fa="نان را تقسیم کن",
         intro_fa=tr("هر چیز را در سبد درست بینداز.", "Put each thing in the right basket."), icon="bread", sheet="share_the_bread.csv", make=sorter),
    dict(id="shape_mason", engine="listen_pick", letter="f", title_en="Shape Mason", title_fa="گلکار شکل" + Z + "ها",
         intro_fa=tr("گوش کن و جواب درست را انتخاب کن.", "Listen and choose the right answer."), icon="brick", sheet="shape_mason.csv", make=mason),
    dict(id="twin_tiles", engine="pairs", letter="g", title_en="Twin Tiles", title_fa="جوره" + Z + "ها",
         intro_fa=tr("دو کارت را که با هم جور است پیدا کن.", "Find the two cards that go together."), icon="box", sheet="twin_tiles.csv", make=pairs45),
    dict(id="number_rain", engine="catch", letter="h", title_en="Number Rain", title_fa="باران عددها",
         intro_fa=I_RAIN, icon="basket", sheet="number_rain.csv", make=catch45),
    # only level 4
    dict(id="days_and_months", engine="listen_pick", letter="i", title_en="Days and Months", title_fa="روزها و ماه" + Z + "ها",
         intro_fa=tr("گوش کن و جواب درست را انتخاب کن.", "Listen and choose the right answer."), icon="moon", sheet="days_and_months.csv",
         read_choices=True, make=calendar4),
    # only level 5
    dict(id="tables_and_charts", engine="listen_pick", letter="j", title_en="Tables and Charts", title_fa="جدول و گراف",
         intro_fa=tr("جدول یا گراف را ببین و جواب بده.", "Look at the table or the chart and answer."), icon="chart_bars_1",
         sheet="tables_and_charts.csv", make=charts5),
    dict(id="fair_shares", engine="listen_pick", letter="k", title_en="Fair Shares", title_fa="حصه" + Z + "های برابر",
         intro_fa=tr("کسر درست را پیدا کن.", "Find the right fraction."), icon="frac_3_4", sheet="fair_shares.csv", make=fractions5),
    # every level
    dict(id="number_riddles", engine="listen_pick", letter="l", title_en="Number Riddles", title_fa="چیستان عددها",
         intro_fa=tr("خوب فکر کن و جواب درست را انتخاب کن.", "Think carefully and choose the right answer."), icon="star", sheet="number_riddles.csv", make=riddles),
    dict(id="true_or_false", engine="sorter", letter="m", title_en="True or False", title_fa="درست یا غلط",
         intro_fa=tr("درست است یا غلط؟ در سبد خودش بینداز.", "Is it true or false? Put it in its basket."), icon="yes", sheet="true_or_false.csv", make=truefalse),
    # only level 6
    dict(id="cooking_pot", engine="listen_pick", letter="n", title_en="The Cooking Pot", title_fa="دیگ آشپزی",
         intro_fa=tr("نسبت را پیدا کن و حساب کن.", "Find the ratio and work it out."), icon="pot", sheet="cooking_pot.csv", make=ratio6),
]
# The spoken instruction of a game where level 6 uses it for something else than the levels before.
INTRO6 = {
    "count_the_flock": tr("فیصد یعنی از صد. بشمار و فیصد درست را انتخاب کن.", "Percent means out of a hundred. Count and choose the right percent."),
    "carpet_weaver": tr("به ترتیب درست بچین.", "Put them in the right order."),
    "shape_mason": tr("نقشه و پیاله اندازه" + Z + "گیری را ببین و حساب کن.", "Look at the map and the measuring cup and work it out."),
    "tables_and_charts": tr("گراف را ببین و اوسط را پیدا کن.", "Look at the chart and find the average."),
    "number_rain": tr("گوش کن و فقط آنهایی را بگیر که درست هستند.", "Listen and catch only the ones that are right."),
}
TITLES = {1: ("Math 1: Counting to 20", "ریاضی ۱: شمارش تا بیست"),
          2: ("Math 2: Numbers to 100", "ریاضی ۲: عددها تا صد"),
          3: ("Math 3: Numbers to 1,000", "ریاضی ۳: عددها تا هزار"),
          4: ("Math 4: Times Tables and Sharing", "ریاضی ۴: جدول ضرب و تقسیم"),
          5: ("Math 5: Large Numbers and Fractions", "ریاضی ۵: عددهای بزرگ و کسرها"),
          6: ("Math 6: Percent, Ratio and Averages", "ریاضی ۶: فیصد، نسبت و اوسط")}
VERSION = 2   # raise it whenever the content of the packs changes
VERSIONS = {6: 1}   # a level that was written later counts for itself
ROUNDS = {  # game -> rounds per level
    "count_the_flock": {1: 12, 2: 10, 3: 8, 4: 6, 5: 6, 6: 6}, "number_hop": {1: 17, 2: 17, 3: 17, 4: 14, 5: 12, 6: 10},
    "market_scales": {1: 7, 2: 7, 3: 7, 4: 7, 5: 6, 6: 6}, "carpet_weaver": {1: 8, 2: 8, 3: 8, 4: 7, 5: 6, 6: 5},
    "share_the_bread": {1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4}, "shape_mason": {1: 5, 2: 6, 3: 6, 4: 6, 5: 5, 6: 8},
    "twin_tiles": {1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4}, "number_rain": {1: 2, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2}, "days_and_months": {4: 4},
    "tables_and_charts": {5: 4, 6: 3}, "fair_shares": {5: 6},
    "number_riddles": {1: 7, 2: 7, 3: 6, 4: 5, 5: 5, 6: 5}, "true_or_false": {1: 5, 2: 4, 3: 4, 4: 3, 5: 3, 6: 3},
    "cooking_pot": {6: 5},
}
OLD_ROUNDS = {  # what version 1 had: no game may lose a round
    "count_the_flock": {1: 12, 2: 10, 3: 8, 4: 6, 5: 6}, "number_hop": {1: 12, 2: 12, 3: 12, 4: 10, 5: 8},
    "market_scales": {1: 6, 2: 6, 3: 6, 4: 6, 5: 5}, "carpet_weaver": {1: 6, 2: 6, 3: 6, 4: 5, 5: 5},
    "share_the_bread": {1: 4, 2: 4, 3: 4, 4: 4, 5: 4}, "shape_mason": {1: 4, 2: 4, 3: 4, 4: 5, 5: 4},
    "twin_tiles": {4: 4, 5: 3}, "number_rain": {4: 2, 5: 2}, "days_and_months": {4: 3},
    "tables_and_charts": {5: 4}, "fair_shares": {5: 6},
}
POOL = (16, 24)     # items in a pool
SMALL_POOL = 10     # the least a pool may have when the material is limited (declared with build(small=...))
PAIRS_DRAW = 6      # a pairs round lays out at most six pairs


def pictures_in(cell: str) -> list[str]:
    out = []
    for spec in filter(None, (c.strip() for c in cell.split("|"))):
        if spec.startswith(("t:", "f:")) or spec == "snd":
            continue
        m = re.match(r"^p:([a-z0-9_]+)\*(\d+)$", spec)
        if m:
            assert 1 <= int(m.group(2)) <= 20, spec
            out.append(m.group(1))
        else:
            assert re.match(r"^[a-z][a-z0-9_]*$", spec), spec
            out.append(spec)
    return out


def check_sheet(level: int, game: dict, sheet: Sheet) -> set[str]:
    """Format checks that hold for every sheet. Returns the pictures used."""
    name = f"math-{level} {game['id']}"
    rounds: dict[str, list[dict]] = {}
    for row in sheet.rows:
        rounds.setdefault(row["round"], []).append(row)
    assert list(rounds) == [f"{i:02d}" for i in range(1, ROUNDS[game["id"]][level] + 1)], (name, list(rounds))
    assert len(rounds) >= OLD_ROUNDS.get(game["id"], {}).get(level, 0), (name, "a round was lost")
    used: set[str] = set()
    for rnd, rows in rounds.items():
        assert not pool_faults(sheet, rnd), (name, rnd, pool_faults(sheet, rnd))
        assert rows[0]["intro_fa"], (name, rnd, "no intro")
        for r in rows:
            assert r["say_fa"].strip() and re.search("[\u0600-\u06ff]", r["say_fa"]), (name, r)
            assert not re.search(r"\d", r["say_fa"] + r.get("help_fa", "")), (name, "digits in speech", r)
            for col in ("show", "answer", "distractors", "thing", "basket", "tiles", "extra", "goods", "a", "b", "targets", "others"):
                used.update(pictures_in(r.get(col, "")))
            if game["engine"] in ("listen_pick", "journey"):
                choices = [r["answer"]] + r["distractors"].split("|")
                assert len(choices) == 4 and len(set(choices)) == 4, (name, r)  # four, or the builder adds its own
                kinds = {"t" if c.startswith("t:") else "f" if c.startswith("f:") else "p" for c in choices}
                assert len(kinds) == 1, (name, "mixed kinds of choices", r)
                values = [val(c) for c in choices]
                if None not in values:  # never two choices of the same value (4 and ۴, 1/2 and 2/4, 2.5 and 2.50)
                    assert len(set(values)) == len(values), (name, r)
    return used


def check_answers() -> None:
    """Every answer once more, independently of how the row was made."""
    for row, a, op, b in HOP_META:
        ans = value(row["answer"])
        if op == "/":
            assert b > 0 and ans * b == a, row
        else:
            assert ans == {"+": a + b, "-": a - b, "*": a * b}[op] and ans >= 0, row
        wrong = [value(x) for x in row["distractors"].split("|")]
        assert ans not in wrong and len(set(wrong)) == 3 and min(wrong) >= 0, row
        assert fa(a) in row["say_fa"] and fa(b) in row["say_fa"], row
        assert f"مساوی {fa(ans)}." in row["help_fa"], row
        if row["hop"]:
            m = re.match(r"^(\d+)([+-])(\d+)$", row["hop"])
            assert m, row
            x, y = int(m.group(1)), int(m.group(3))
            assert (x + y if m.group(2) == "+" else x - y) == ans, row
            assert (x, m.group(2), y) == (a, op, b) and max(x, y, ans) <= 20, row
        else:
            assert op in "*/" or max(a, b, ans) > 20, row
        if op == "*":
            assert "ضرب" in row["say_fa"] + row["help_fa"]
    for row, target in MARKET_META:
        units = [int(u) for u in row["units"].split("|")]
        assert int(row["target"]) == target and reachable(target, units), row
        assert set(units) <= {1, 2, 5, 10, 20, 50, 100, 500, 1000} and len(units) <= 6, row
        if row["mode"] == "count":
            assert units == [1] and 1 <= target <= 20, row
            assert row["say_fa"].startswith(fa(target) + " ") or f"مساوی {fa(target)}." in row["help_fa"], row
        else:
            assert f"{fa(target)}" in row["say_fa"] + row["help_fa"], row
    for row, seq, extra, kind in WEAVE_META:
        tiles = [value(t) for t in row["tiles"].split("|")]
        extras = [value(t) for t in row["extra"].split("|")] if row["extra"] else []
        assert tiles == seq and extras == extra and len(tiles) + len(extras) <= 8, row
        if kind == "seq":
            steps = {y - x for x, y in zip(tiles, tiles[1:])}
            assert len(steps) == 1 and 0 not in steps, row
        else:
            assert tiles == sorted(tiles, reverse=(kind == "down")), row
    for row, kind, what in SORT_META:
        if kind == "parity":
            assert value(row["thing"]) == what and row["basket"] == ("f:جفت" if what % 2 == 0 else "f:طاق"), row
        elif kind == "500":
            assert what != 500 and row["basket"] == ("f:کمتر از ۵۰۰" if what < 500 else "f:بیشتر از ۵۰۰"), row
        elif kind == "shape":
            assert row["basket"] == f"shape_{what}" and row["thing"] in [p for p, _ in SHAPED[what]], row
        else:
            suffix = {"whole": "", "half": "half", "quarter": "quarter", "third": "third"}[what]
            assert (suffix in row["thing"]) if suffix else not re.search("half|quarter|third", row["thing"]), row
    for row, n in MASON_META:
        got = row["answer"]
        assert (int(got.split("_")[1]) if got.startswith("clock_") else value(got)) == n, row
    for row, true in TF_META:
        assert row["basket"] == ("yes" if true else "no"), row
        m = re.fullmatch(r"t:([^=]+)=(.+)", row["thing"].replace(" ", ""))
        if m:   # a written sum or equality: work it out again from the tile
            assert (text_sum(m.group(1)) == text_sum(m.group(2))) == true, row
    for row, n, limit in EST_META:
        shown = int(row["thing"].split("*")[1])
        assert shown == n, row
        if row["basket"] in ("yes", "no"):   # "here are five sheep"
            assert (row["basket"] == "yes") == (fa(shown) + " " in row["say_fa"]) or limit == -1, row
            assert (limit == shown) == (row["basket"] == "yes"), row
        else:
            assert shown != limit and row["basket"] == ("f:کمتر از ۱۰" if shown < limit else "f:بیشتر از ۱۰"), row
    check_answers45()


def check_answers45() -> None:
    """Every answer once more, from what is written in the row."""
    for row, want in CHECK_META:
        assert val(row["answer"]) == want, row
        wrong = [val(x) for x in row["distractors"].split("|")]
        assert want not in wrong and len(set(wrong)) == 3, row
    for row, what in CAL_META:
        assert row["answer"] in (what, "f:" + what) and row["answer"] not in row["distractors"].split("|"), row
    for row in SENT_META:
        tiles = [x[2:] for x in row["tiles"].split("|")]
        assert len(tiles) == 5 and tiles[3] == "=", row
        result = text_sum("".join(tiles[:3]))
        assert result == val("t:" + tiles[4]), row
        extras = [val(x) for x in row["extra"].split("|")]
        assert result not in extras and len(tiles) + len(extras) <= 8, row
        assert not set(row["extra"].split("|")) & set(row["tiles"].split("|")), row
    for row, up in ORDER_META:
        values = [val(x) for x in row["tiles"].split("|")]
        assert values == sorted(values, reverse=not up) and len(set(values)) == len(values) <= 8, row
    for row, kind in PAIR_META:
        if kind == "sum":
            assert text_sum(row["a"]) == val(row["b"]), row
        elif kind == "samesum":
            assert text_sum(row["a"]) == text_sum(row["b"]) and row["a"] != row["b"], row
        elif kind == "same":
            assert val(row["a"]) == val(row["b"]) and row["a"] != row["b"], row
        elif kind == "count":
            assert int(row["a"].split("*")[1]) == value(row["b"]) and fa(value(row["b"])) in row["say_fa"], row
        elif kind == "numname":
            assert row["b"] == "snd" and row["say_fa"] == fa(value(row["a"])), row
        elif kind == "money":
            assert row["b"] == "snd" and row["say_fa"] == money_fa(int(val(row["a"]) * 100)), row
        else:
            assert re.fullmatch(r"[a-z0-9_]+", row["a"]) and row["b"] == "snd" and row["say_fa"], row
    for row, test in CATCH_META:
        assert all(test(val(x)) for x in row["targets"].split("|")), row
        assert not any(test(val(x)) for x in row["others"].split("|")), row
    half = Fraction(1, 2)
    for row, kind in SORT2_META:
        if kind == "sum":
            assert text_sum(row["thing"]) == val(row["basket"]), row
        elif kind == "half":
            v = val(row["thing"])
            assert row["basket"] == ("f:کمتر" if v < half else "f:نیم" if v == half else "f:بیشتر"), row
            assert row["basket_say_fa"].endswith("نیم"), row
        elif kind == "same":
            assert val(row["thing"]) == val(row["basket"]), row
        elif kind == "afghani":
            v = val(row["thing"])
            assert v != 1 and row["basket"] == ("f:کمتر" if v < 1 else "f:بیشتر") and row["basket_say_fa"].endswith("یک افغانی"), row
        else:
            v = val(row["thing"])
            assert v != 5000 and row["basket"] == ("f:کمتر" if v < 5000 else "f:بیشتر") and row["basket_say_fa"].endswith("پنج هزار"), row


# ---------------------------------------------------------------------------
# The mechanical self-check (python3 content/math/generate.py --check)
# ---------------------------------------------------------------------------
#
# It reads only the finished rows, as the builder will, and knows nothing of
# how they were made.

# Latin text that is still drawn at 24 px or more on its card, in digits
# (measured on screenshots: a choice or question card holds eight, the wide
# sorter card twelve; the round card of Number Rain three digits or "1.25").
MAX_CHARS = {"choice": SHOW_UNITS, "show": SHOW_UNITS, "tile": 8, "thing": 12, "card": 8, "catch": 4}


def chars(thing: str) -> float:
    return units(thing) if thing[:2] == "t:" else len(thing) - 2 if thing[:2] == "f:" and not DARI_LETTER.search(thing) else 0


def self_check(packs: dict) -> tuple[list[str], list[tuple]]:
    """packs: level -> [(game, sheet)]. Returns the faults and one table row
    per level: (level, games, rounds, items, pools smaller than 16, the most
    often one answer is right in a pool, the round where that happens)."""
    faults: list[str] = []
    table = []
    truths = {id(row): test for row, test in TRUTH}
    for level, games in packs.items():
        n_rounds = n_items = n_small = 0
        worst = (0, "")
        for game, sheet in games:
            engine = game["engine"]
            where = f"math-{level} {game['id']}"
            want_draw = PAIRS_DRAW if engine == "pairs" else DRAW
            if game.get("draw") != want_draw:
                faults.append(f"{where}: draw is {game.get('draw')}, not {want_draw}")
            rounds: dict[str, list[dict]] = {}
            for row in sheet.rows:
                rounds.setdefault(row["round"], []).append(row)
            for rnd, rows in rounds.items():
                at = f"{where} round {rnd}"
                n_rounds += 1
                n_items += len(rows)
                if rnd in sheet.small:
                    n_small += 1
                    if not SMALL_POOL <= len(rows) <= POOL[1]:
                        faults.append(f"{at}: {len(rows)} items")
                elif not POOL[0] <= len(rows) <= POOL[1]:
                    faults.append(f"{at}: {len(rows)} items, not {POOL[0]} to {POOL[1]}")
                faults += [f"{at}: {f}" for f in pool_faults(sheet, rnd)]
                counts = Counter(answer_of(r) for r in rows)
                if engine != "sorter" and rnd not in sheet.few and max(counts.values()) > worst[0]:
                    worst = (max(counts.values()), f"{game['id']} {rnd}")
                if engine == "pairs":   # every card must have one partner only
                    for side in ("a", "b"):
                        vals = [card_value(r[side], r["say_fa"]) for r in rows]
                        if len(set(vals)) != len(vals):
                            faults.append(f"{at}: two pair cards with the same value on side {side}")
                    cards = [r[c] for r in rows for c in ("a", "b") if r[c] != "snd"]
                    if len(set(cards)) != len(cards):
                        faults.append(f"{at}: the same card twice")
                if engine == "sorter" and not 2 <= len({r["basket"] for r in rows}) <= 4:
                    faults.append(f"{at}: {len({r['basket'] for r in rows})} baskets")
                for r in rows:
                    for col in ("show", "answer", "distractors", "thing", "tiles", "extra", "goods", "a", "b", "targets", "others"):
                        for m in re.finditer(r"p:\w+\*(\d+)", r.get(col, "")):
                            if not 1 <= int(m.group(1)) <= 20:
                                faults.append(f"{at}: {m.group(0)} cannot be drawn")
                    if engine in ("listen_pick", "journey"):
                        choices = [r["answer"]] + r["distractors"].split("|")
                        if len(choices) != 4 or len(set(choices)) != 4:
                            faults.append(f"{at}: not four different choices: {choices}")
                        values = [val(c) for c in choices]
                        if None not in values and len(set(values)) != 4:
                            faults.append(f"{at}: two choices of the same value: {choices}")
                        test = truths.get(id(r))
                        if test and [bool(test(c)) for c in choices] != [True, False, False, False]:
                            faults.append(f"{at}: not exactly one right answer: {r['say_fa']} {choices}")
                        if not r["help_fa"]:
                            faults.append(f"{at}: no help: {r['say_fa']}")
                        if any(chars(c) > MAX_CHARS["choice"] for c in choices if c.startswith("t:")) or chars(r["show"]) > MAX_CHARS["show"] and r["show"].startswith("t:"):
                            faults.append(f"{at}: text too long for its card: {r['show']} {choices}")
                        if r["hop"]:
                            m = re.fullmatch(r"(\d+)([+-])(\d+)", r["hop"])
                            x, y = (int(m.group(1)), int(m.group(3))) if m else (99, 99)
                            res = x + y if m and m.group(2) == "+" else x - y
                            if not m or not 0 <= res <= 20 or max(x, y) > 20 or val(r["answer"]) not in (res, y, x):
                                faults.append(f"{at}: bad number line {r['hop']}")
                        elif engine == "journey" and level == 1:
                            faults.append(f"{at}: a level 1 sum without its number line")
                    elif engine == "market":
                        units, target = [int(u) for u in r["units"].split("|")], int(r["target"])
                        if len(units) > 6 or not reachable(target, units) or (r["mode"] == "count" and not 1 <= target <= 20):
                            faults.append(f"{at}: the market cannot show {target} with {units}")
                        if not r["help_fa"]:
                            faults.append(f"{at}: no help")
                    elif engine == "builder":
                        tiles, extra = r["tiles"].split("|"), [x for x in r["extra"].split("|") if x]
                        if len(tiles) + len(extra) > 8 or len(set(tiles + extra)) != len(tiles + extra):
                            faults.append(f"{at}: tiles {tiles} {extra}")
                        if any(chars(t) > MAX_CHARS["tile"] for t in tiles + extra):
                            faults.append(f"{at}: a tile is too wide: {tiles}")
                        if not r["help_fa"]:
                            faults.append(f"{at}: no help")
                    elif engine == "catch":
                        targets, others = r["targets"].split("|"), r["others"].split("|")
                        if set(targets) & set(others) or len(targets) < int(r["need"]) or not 1 <= int(r["need"]) <= 10:
                            faults.append(f"{at}: targets and others")
                        if any(chars(t) > MAX_CHARS["catch"] or (re.fullmatch(r"[tf]:[0-9۰-۹]+", t) and chars(t) > 3) for t in targets + others):
                            faults.append(f"{at}: too wide for the round card: {targets} {others}")
                    elif engine == "sorter":
                        if chars(r["thing"]) > MAX_CHARS["thing"]:
                            faults.append(f"{at}: thing too wide: {r['thing']}")
                    elif engine == "pairs":
                        if any(chars(r[c]) > MAX_CHARS["card"] for c in ("a", "b")):
                            faults.append(f"{at}: card too wide: {r['a']} {r['b']}")
        table.append((level, len(games), n_rounds, n_items, n_small, worst[0], worst[1]))
    return faults, table


def main() -> None:
    check_only = "--check" in sys.argv[1:]
    _test_numbers()
    used: set[str] = set()
    files: dict[Path, str] = {}
    packs: dict[int, list] = {}
    for level in (1, 2, 3, 4, 5, 6):
        games = []
        packs[level] = []
        for game in GAMES:
            if level not in ROUNDS[game["id"]]:
                continue
            sheet = game["make"](level)
            used |= check_sheet(level, game, sheet)
            files[HERE / str(level) / game["sheet"]] = sheet.text()
            entry = {k: v for k, v in game.items() if k != "make"}
            if isinstance(entry["intro_fa"], dict):
                entry["intro_fa"] = entry["intro_fa"][level]
            if level == 6:
                entry["intro_fa"] = INTRO6.get(game["id"], entry["intro_fa"])
            entry["draw"] = PAIRS_DRAW if game["engine"] == "pairs" else DRAW
            used_en({"intro_fa": entry["intro_fa"]})
            used.add(entry["icon"])
            games.append(entry)
            packs[level].append((entry, sheet))
        assert len({g["letter"] for g in games}) == len(games)
        pack = {"pack": f"math-{level}", "subject": "math", "level": level, "version": VERSIONS.get(level, VERSION),
                "title_en": TITLES[level][0], "title_fa": TITLES[level][1], "games": games}
        files[HERE / str(level) / "pack.json"] = json.dumps(pack, ensure_ascii=False, indent=1) + "\n"
    check_answers()
    check_answers6(packs[6])
    faults, table = self_check(packs)
    missing = used - set(PICTURES)
    assert not missing, f"pictures without a description: {sorted(missing)}"
    files[HERE / "pictures.txt"] = "".join(f"{name}: {PICTURES[name]}\n" for name in sorted(used))
    files[I18N] = english_table()
    if check_only or faults:
        print("level  games  rounds  items  small pools  most often one answer is right in a pool")
        for level, n_games, n_rounds, n_items, n_small, most, where in table:
            print(f"{level:>5}  {n_games:>5}  {n_rounds:>6}  {n_items:>5}  {n_small:>11}  {most} ({where})")
        stale = [str(p.relative_to(HERE.parent)) for p, text in files.items() if not p.exists() or p.read_text("utf-8") != text]
        print(f"files on disk: {'up to date' if not stale else 'NOT up to date: ' + ', '.join(stale[:6])}")
        for f in faults:
            print("FAULT", f)
        print(f"self-check: {len(faults)} faults in {sum(r[3] for r in table)} items")
        sys.exit(1 if faults else 0)
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(files)} files, {len(used)} pictures, {len(USED_EN)} English texts; self-check ok")


if __name__ == "__main__":
    main()

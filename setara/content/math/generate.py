#!/usr/bin/env python3
"""Generates the math packs (levels 1 to 5): every CSV sheet, pack.json and
pictures.txt in this folder, and the English of every Dari text in them
(content/i18n/math.csv, for the English mode of the app).

    python3 content/math/generate.py

Standard library only. Deterministic: every round has its own fixed random
seed, so running it twice writes identical files. Do not edit the CSV files by
hand; change this script and run it again.

Every answer is computed, never typed, and checked again by assertions before
anything is written.
"""

from __future__ import annotations

import csv
import io
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


def lp(sheet: Sheet, rnd: str, intro: str, say: str, answer: str, wrong: list[str],
       show: str = "", help_fa: str = "", hop: str = "") -> dict:
    """One listen-and-pick / journey question. Always three wrong choices, so
    the builder never fills in choices of its own."""
    assert len(wrong) == 3, (say, wrong)
    assert answer not in wrong and len(set(wrong)) == 3, (say, answer, wrong)
    return sheet.add(round=rnd, intro_fa=intro, say_fa=say, show=show, answer=answer,
                     distractors="|".join(wrong), help_fa=help_fa, hop=hop)


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


def count_item(s, rnd, intro, n, obj, script, rng, hi=20):
    pic, noun = obj
    assert 1 <= n <= 20
    if n <= 10:
        help_fa = tr("، ".join(fa(i) for i in range(1, n + 1)) + f". {fa(n)} {noun} است.", ", ".join(str(i) for i in range(1, n + 1)) + f". {there(n, noun)}.")
    else:
        help_fa = tr(f"{fa(n)} {noun} است.", f"{there(n, noun)}.")
    wrong = near(n, rng, 0, hi)
    row = lp(s, rnd, intro, tr(f"چند {noun} است؟", f"How many {many(noun)} are there?"), num(n, script), [num(x, script) for x in wrong],
             show=f"p:{pic}*{n}", help_fa=help_fa)
    m = re.match(r"p:\w+\*(\d+)$", row["show"])
    assert int(m.group(1)) == value(row["answer"]) == n


def hear_item(s, rnd, intro, n, script, rng, lo, hi, prefer=()):
    wrong = near(n, rng, lo, hi, prefer)
    row = lp(s, rnd, intro, tr(f"عدد {fa(n)} کدام است؟", f"Which one is the number {n}?"), num(n, script), [num(x, script) for x in wrong])
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
    row = lp(s, rnd, intro, tr(f"کدام از همه {word} است؟", f"Which one is the {'most' if most else 'fewest'}?"), f"p:{pic}*{ans}", [f"p:{pic}*{c}" for c in wrong],
             help_fa=tr(f"{fa(ans)} {noun} از همه {word} است.", f"{cnt(ans, noun)} is the {'most' if most else 'fewest'}."))
    got = int(row["answer"].split("*")[1])
    others = [int(x.split("*")[1]) for x in row["distractors"].split("|")]
    assert all(got > o for o in others) if most else all(got < o for o in others)


def numeral_compare_item(s, rnd, intro, numbers, biggest: bool, script="W"):
    assert len(set(numbers)) == 4
    ans = max(numbers) if biggest else min(numbers)
    wrong = [n for n in numbers if n != ans]
    word = "بزرگتر" if biggest else "کوچکتر"
    row = lp(s, rnd, intro, tr(f"کدام عدد از همه {word} است؟", f"Which number is the {'biggest' if biggest else 'smallest'}?"), num(ans, script), [num(n, script) for n in wrong],
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


def flock(level: int) -> Sheet:
    if level >= 4:
        return flock45(level)
    s = Sheet(LP_COLS)
    if level == 1:
        def counting(rnd, values, script, hi=20):
            rng = rng_for(1, "flock", rnd)
            values = spread(values, rng)
            objs = OBJS[int(rnd):] + OBJS[:int(rnd)]
            for i, n in enumerate(values):
                count_item(s, rnd, I_COUNT if script == "W" else I_COUNT_D, n, objs[i], script, rng, hi)

        r = rng_for(1, "flock", "values")
        counting("01", [1, 2, 3, 4, 5] + r.sample(range(1, 6), 3), "W", 10)
        counting("02", [1, 2, 3, 4, 5] + r.sample(range(1, 6), 3), "D", 10)
        counting("03", [6, 7, 8, 9, 10] + r.sample(range(1, 6), 3), "W", 10)
        counting("04", r.sample(range(1, 11), 8), "D", 10)

        rng = rng_for(1, "flock", "05")
        for i, n in enumerate(spread([0, 10] + rng.sample(range(1, 10), 6), rng)):
            match_item(s, "05", I_MATCH, n, "D" if i % 2 == 0 else "W", rng, 0, 10)
        rng = rng_for(1, "flock", "06")
        for i, n in enumerate(spread([0] + rng.sample(range(1, 11), 7), rng)):
            hear_item(s, "06", I_HEAR, n, "W" if i % 2 == 0 else "D", rng, 0, 10)
        rng = rng_for(1, "flock", "07")
        for i in range(8):
            top = rng.randint(5, 10)
            counts = [top, top - 1] + rng.sample(range(1, top - 1), 2)
            flock_compare_item(s, "07", I_MORE, OBJS[i], counts, most=True)

        counting("08", r.sample(range(11, 21), 8), "W")
        counting("09", r.sample(range(11, 21), 8), "D")
        rng = rng_for(1, "flock", "10")
        for i, n in enumerate(rng.sample(range(11, 21), 8)):
            hear_item(s, "10", I_HEAR, n, "W" if i % 2 == 0 else "D", rng, 0, 20, prefer=[n - 10])
        rng = rng_for(1, "flock", "11")
        for i, n in enumerate(spread([20] + rng.sample(range(11, 20), 7), rng)):
            match_item(s, "11", I_MATCH, n, "D" if i % 2 == 0 else "W", rng, 0, 20, prefer=[n - 10])
        rng = rng_for(1, "flock", "12")
        for i in range(4):
            low = rng.randint(2, 8)
            counts = [low, low + 1] + rng.sample(range(low + 2, 13), 2)
            flock_compare_item(s, "12", I_COMPARE, OBJS[i + 4], counts, most=False)
        for i in range(4):
            numbers = rng.sample(range(0, 21), 4)
            numeral_compare_item(s, "12", I_COMPARE, numbers, biggest=i % 2 == 0, script="W" if i < 2 else "D")

    elif level == 2:
        rng = rng_for(2, "flock", "01")
        for n in rng.sample(range(10, 101, 10), 8):
            hear_item(s, "01", I_HEAR, n, "W", rng, 0, 100, prefer=[n // 10 + 10 if 30 <= n <= 90 else None, n // 10])
        rng = rng_for(2, "flock", "02")
        for n in rng.sample([x for x in range(21, 60) if x % 10], 8):
            hear_item(s, "02", I_HEAR, n, "W", rng, 0, 100, prefer=digit_perms(n))
        rng = rng_for(2, "flock", "03")
        for n in rng.sample([x for x in range(60, 100) if x % 10], 8):
            hear_item(s, "03", I_HEAR, n, "W", rng, 0, 100, prefer=digit_perms(n))
        rng = rng_for(2, "flock", "04")
        for n in rng.sample([x for x in range(21, 100) if x % 10], 8):
            hear_item(s, "04", I_HEAR, n, "D", rng, 0, 100, prefer=digit_perms(n))
        rng = rng_for(2, "flock", "05")
        for i, n in enumerate(rng.sample(range(21, 100), 8)):
            match_item(s, "05", I_MATCH, n, "D" if i % 2 == 0 else "W", rng, 0, 100, prefer=digit_perms(n))
        rng = rng_for(2, "flock", "06")
        pairs = rng.sample([(t, o) for t in range(2, 10) for o in range(1, 10) if t != o], 6)
        pairs += [(t, 0) for t in rng.sample(range(2, 10), 2)]
        for t, o in pairs:
            place2_item(s, "06", I_PLACE, t, o, rng)
        rng = rng_for(2, "flock", "07")
        for i, n in enumerate(rng.sample([x for x in range(21, 100) if x // 10 != x % 10], 8)):
            digit_item(s, "07", I_DIGIT, n, i % 2 == 0, rng)
        rng = rng_for(2, "flock", "08")
        for i, x in enumerate(rng.sample([x for x in range(21, 99) if x % 11 and x % 10], 8)):
            numeral_compare_item(s, "08", I_COMPARE, similar_numbers(x, rng, 10, 100), biggest=i % 2 == 0)
        rng = rng_for(2, "flock", "09")
        for n in [29, 59, 99] + rng.sample([x for x in range(21, 99) if x % 10 != 9], 1):
            next_item(s, "09", I_NEXT, n, True, rng, 0, 101)
        for n in [40, 70, 100] + rng.sample([x for x in range(22, 99) if x % 10], 1):
            next_item(s, "09", I_NEXT, n, False, rng, 0, 101)
        rng = rng_for(2, "flock", "10")
        a, b, c, d, e, f, g, h = rng.sample([x for x in range(21, 99) if x % 11 and x % 10], 8)
        hear_item(s, "10", I_MIX, a, "D", rng, 0, 100, prefer=digit_perms(a))
        match_item(s, "10", I_MIX, b, "W", rng, 0, 100, prefer=digit_perms(b))
        place2_item(s, "10", I_MIX, c // 10, c % 10, rng)
        digit_item(s, "10", I_MIX, d, True, rng)
        numeral_compare_item(s, "10", I_MIX, similar_numbers(e, rng, 10, 100), biggest=True)
        numeral_compare_item(s, "10", I_MIX, similar_numbers(f, rng, 10, 100), biggest=False)
        next_item(s, "10", I_MIX, g // 10 * 10 + 9, True, rng, 0, 101)
        next_item(s, "10", I_MIX, h // 10 * 10, False, rng, 0, 101)

    else:
        rng = rng_for(3, "flock", "01")
        for n in rng.sample(range(100, 1001, 100), 8):
            hear_item(s, "01", I_HEAR, n, "W", rng, 0, 1000, prefer=[n // 10, n - 100, n + 100])
        rng = rng_for(3, "flock", "02")
        for i, (h, d) in enumerate(zip(rng.sample(range(1, 10), 8), rng.sample(range(1, 10), 8))):
            n, twin = (100 * h + 10 * d, 100 * h + d) if i % 2 == 0 else (100 * h + d, 100 * h + 10 * d)
            hear_item(s, "02", I_HEAR, n, "W", rng, 0, 1000, prefer=[twin, 10 * h + d])
        three = [x for x in range(111, 1000) if "0" not in str(x) and len(set(str(x))) == 3]
        rng = rng_for(3, "flock", "03")
        for n in rng.sample(three, 8):
            hear_item(s, "03", I_HEAR, n, "W", rng, 0, 1000, prefer=rng.sample(digit_perms(n), 2))
        rng = rng_for(3, "flock", "04")
        for n in rng.sample(three, 6) + rng.sample([x for x in range(101, 1000) if "0" in str(x) and x % 100], 2):
            hear_item(s, "04", I_HEAR, n, "D", rng, 0, 1000,
                      prefer=rng.sample(digit_perms(n), min(2, len(digit_perms(n)))))
        rng = rng_for(3, "flock", "05")
        for i, n in enumerate(rng.sample(range(101, 1000), 7) + [1000]):
            match_item(s, "05", I_MATCH, n, "D" if i % 2 == 0 else "W", rng, 0, 1000,
                       prefer=rng.sample(digit_perms(n), min(2, len(digit_perms(n)))))
        rng = rng_for(3, "flock", "06")
        triples = [tuple(int(c) for c in str(x)) for x in rng.sample(three, 5)]
        triples += [(rng.randint(1, 9), 0, rng.randint(1, 9)), (rng.randint(1, 9), rng.randint(1, 9), 0),
                    (rng.randint(1, 9), 0, rng.randint(1, 9))]
        for h, t, o in triples:
            place3_item(s, "06", I_PLACE3, h, t, o, rng)
        rng = rng_for(3, "flock", "07")
        for i, x in enumerate(rng.sample(three, 8)):
            numeral_compare_item(s, "07", I_COMPARE, similar_numbers(x, rng, 100, 1000), biggest=i % 2 == 0)
        rng = rng_for(3, "flock", "08")
        for n in [199, 409, 999] + rng.sample(three, 1):
            next_item(s, "08", I_NEXT, n, True, rng, 0, 1001)
        for n in [300, 710, 1000] + rng.sample(three, 1):
            next_item(s, "08", I_NEXT, n, False, rng, 0, 1001)
    return s


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


def hop_item(s, rnd, intro, a, op, b, rng, hi, say=None, show="", extra_prefer=(), script="W"):
    ans = calc(a, op, b)
    assert ans >= 0 and a >= 0 and b >= 0
    if say is None:
        say = tr(f"{fa(a)} {OP_WORD[op]} {fa(b)} چند می{Z}شود؟", f"{a} {OP_EN[op]} {b} makes how many?")
    help_fa = tr(f"{fa(a)} {OP_WORD[op]} {fa(b)} مساوی {fa(ans)}.", f"{a} {OP_EN[op]} {b} equals {ans}.")
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


def story_item(s, rnd, intro, a, op, b, rng, hi, k, with_picture):
    assert a >= 1 and b >= 1
    pic, noun, came, went = STORY_OBJS[k % len(STORY_OBJS)]
    if op == "+":
        say = tr(f"{fa(a)} {noun} بود، {came[0].format(b=fa(b))}. چند تا شد؟", f"{was(a, noun)}, {came[1].format(b=b)}. How many are there now?")
    else:
        say = tr(f"{fa(a)} {noun} بود، {went[0].format(b=fa(b))}. چند تا ماند؟", f"{was(a, noun)}, {went[1].format(b=b)}. How many are left?")
    show = f"p:{pic}*{a}" if with_picture and a <= 20 else ""
    hop_item(s, rnd, intro, a, op, b, rng, hi, say=say, show=show)


def money_story(s, rnd, intro, a, op, b, rng, hi):
    if op == "+":
        say = tr(f"{fa(a)} افغانی داشتی، {fa(b)} افغانی دیگر گرفتی. چند افغانی شد؟", f"You had {a} afghani, you got {b} afghani more. How many afghani is it now?")
    else:
        say = tr(f"{fa(a)} افغانی داشتی، {fa(b)} افغانی خرج کردی. چند افغانی ماند؟", f"You had {a} afghani, you spent {b} afghani. How many afghani are left?")
    hop_item(s, rnd, intro, a, op, b, rng, hi, say=say)


def hop(level: int) -> Sheet:
    if level >= 4:
        return hop45(level)
    s = Sheet(LP_COLS)

    def plain(rnd, intro, triples, hi):
        rng = rng_for(level, "hop", rnd, "d")
        for a, op, b in triples:
            hop_item(s, rnd, intro, a, op, b, rng, hi)

    def pick(rnd, pool, k, tag=""):
        pool = sorted(set(pool))
        assert len(pool) >= k, (rnd, len(pool))
        return rng_for(level, "hop", rnd, "pick", tag).sample(pool, k)

    if level == 1:
        add5 = [(a, "+", b) for a in range(1, 5) for b in range(1, 5) if a + b <= 5]
        add10 = [(a, "+", b) for a in range(1, 10) for b in range(1, 10) if 6 <= a + b <= 10]
        sub5 = [(a, "-", b) for a in range(2, 6) for b in range(1, a + 1)]
        sub10 = [(a, "-", b) for a in range(6, 11) for b in range(1, a + 1)]
        ten_n = [(10, "+", n) for n in range(1, 11)] + [(n, "+", 10) for n in range(1, 10)]
        add20 = [(a, "+", b) for a in range(11, 19) for b in range(1, 9) if a % 10 + b <= 9]
        add20 += [(b, "+", a) for a, _, b in add20 if b >= 3]
        sub20 = [(a, "-", b) for a in range(12, 20) for b in range(1, 10) if b <= a % 10]
        sub_teen = [(a, "-", b) for a in range(11, 21) for b in range(10, a + 1)]
        plain("01", I_ADD, pick("01", add5, 8), 10)
        plain("02", I_ADD, pick("02", add10, 8), 12)
        plain("03", I_SUB, pick("03", sub5, 8), 10)
        plain("04", I_SUB, pick("04", sub10, 8), 12)
        rng = rng_for(1, "hop", "05")
        for k, (a, op, b) in enumerate(pick("05", add10 + add5, 4, "a") + pick("05", sub10 + sub5[3:], 4, "s")):
            story_item(s, "05", I_STORY, a, op, b, rng, 12, k, True)
        zeros = [(4, "+", 0), (0, "+", 7), (6, "-", 0), (8, "-", 8)]
        mixed = pick("06", add10, 2, "a") + pick("06", sub10, 2, "s")
        plain("06", I_BOTH, spread(zeros + mixed, rng_for(1, "hop", "06", "o")), 12)
        plain("07", I_ADD, pick("07", ten_n, 8), 20)
        plain("08", I_ADD, pick("08", add20, 8), 20)
        plain("09", I_SUB, pick("09", sub20, 8), 20)
        plain("10", I_SUB, pick("10", sub_teen, 8), 20)
        rng = rng_for(1, "hop", "11")
        for k, (a, op, b) in enumerate(pick("11", [t for t in add20 if t[0] > 10], 4, "a") + pick("11", sub20, 4, "s")):
            story_item(s, "11", I_STORY, a, op, b, rng, 20, k + 3, True)
        mixed = pick("12", add20, 3, "a") + pick("12", sub20, 3, "s") + pick("12", ten_n, 1, "t") + pick("12", sub_teen, 1, "u")
        plain("12", I_BOTH, spread(mixed, rng_for(1, "hop", "12", "o")), 20)
        for row, a, op, b in HOP_META:  # level 1 never crosses ten
            if a > 10 or b > 10 or calc(a, op, b) > 10:
                assert op == "+" and (a % 10 + b % 10 <= 9 or 10 in (a, b)) or op == "-" and (b % 10 <= a % 10 or b >= 10), (a, op, b)
            assert calc(a, op, b) <= 20 and row["hop"], (a, op, b)

    elif level == 2:
        add20 = [(a, "+", b) for a in range(11, 19) for b in range(1, 9) if a % 10 + b <= 9]
        sub20 = [(a, "-", b) for a in range(12, 20) for b in range(1, 10) if b <= a % 10]
        bonds = [(a, "+", 10 - a) for a in range(1, 10)]
        from10 = [(10, "-", b) for b in range(1, 10)]
        cross9 = [(a, "+", b) for a in (8, 9) for b in range(3, 10) if a + b >= 11]
        cross9 += [(b, "+", a) for a, _, b in cross9 if b < 8]
        cross = [(a, "+", b) for a in range(2, 10) for b in range(2, 10) if a + b >= 11]
        subx = [(a, "-", b) for a in range(11, 19) for b in range(2, 10) if b > a % 10]
        from20 = [(20, "-", b) for b in range(1, 10)]
        doubles = [(a, "+", a) for a in range(5, 11)] + [(a, "+", a + 1) for a in range(5, 10)] + [(a + 1, "+", a) for a in range(5, 10)]
        tens_add = [(a, "+", b) for a in range(10, 100, 10) for b in range(10, 100, 10) if a + b <= 100]
        tens_sub = [(a, "-", b) for a in range(20, 101, 10) for b in range(10, a + 1, 10)]
        plain("01", I_BOTH, spread(pick("01", add20, 4, "a") + pick("01", sub20, 4, "s"), rng_for(2, "hop", "01", "o")), 20)
        plain("02", I_BOTH, spread(pick("02", bonds, 4, "a") + pick("02", from10, 4, "s"), rng_for(2, "hop", "02", "o")), 20)
        plain("03", I_ADD, pick("03", cross9, 8), 20)
        plain("04", I_ADD, pick("04", [t for t in cross if t[0] < 8 and t[2] < 8] + cross, 8), 20)
        plain("05", I_SUB, pick("05", [t for t in subx if t[0] <= 14], 8), 20)
        plain("06", I_SUB, pick("06", [t for t in subx if t[0] >= 15], 5, "x") + pick("06", from20, 3, "t"), 20)
        plain("07", I_BOTH, spread(pick("07", cross, 4, "a") + pick("07", subx, 4, "s"), rng_for(2, "hop", "07", "o")), 20)
        plain("08", I_ADD, pick("08", doubles, 8), 22)
        plain("09", I_TENS, pick("09", tens_add, 8), 110)
        plain("10", I_TENS, pick("10", [t for t in tens_sub if t[0] != t[2]], 8), 110)
        rng = rng_for(2, "hop", "11")
        st = pick("11", cross, 3, "a") + pick("11", subx, 3, "s")
        for k, (a, op, b) in enumerate(st):
            story_item(s, "11", I_STORY, a, op, b, rng, 20, k, False)
        (a, op, b), (c, op2, d) = pick("11", cross, 1, "ma")[0], pick("11", subx, 1, "ms")[0]
        money_story(s, "11", I_STORY, a, op, b, rng, 20)
        money_story(s, "11", I_STORY, c, op2, d, rng, 20)
        mixed = pick("12", cross, 2, "a") + pick("12", subx, 2, "s") + pick("12", tens_add, 2, "ta") + pick("12", tens_sub, 2, "ts")
        plain("12", I_BOTH, spread(mixed, rng_for(2, "hop", "12", "o")), 110)

    else:
        a1 = [(a, "+", b) for a in range(15, 90) for b in range(2, 10) if a % 10 and a % 10 + b >= 10]
        s1 = [(a, "-", b) for a in range(21, 96) for b in range(2, 10) if a % 10 < b]
        a2 = [(a, "+", b) for a in range(11, 80) for b in range(11, 80)
              if a % 10 and b % 10 and a % 10 + b % 10 <= 9 and a + b < 100]
        a2c = [(a, "+", b) for a in range(13, 80) for b in range(13, 80) if a % 10 + b % 10 >= 10 and a + b <= 100 and a % 10 and b % 10]
        s2b = [(a, "-", b) for a in range(31, 100) for b in range(12, 90) if a % 10 < b % 10 and a - b >= 3]
        plain("01", I_ADD, pick("01", a1, 8), 120)
        plain("02", I_SUB, pick("02", s1, 8), 120)
        plain("03", I_ADD, pick("03", a2, 8), 120)
        plain("04", I_ADD, pick("04", a2c, 8), 120)
        plain("05", I_SUB, pick("05", s2b, 8), 120)
        plain("06", I_BOTH, spread(pick("06", a2c, 4, "a") + pick("06", s2b, 4, "s"), rng_for(3, "hop", "06", "o")), 120)

        def table(t, rnd, k, tag=""):
            ns = rng_for(3, "hop", rnd, "table", t, tag).sample(range(1, 11), k)
            return [(n, "*", t) if i % 2 == 0 else (t, "*", n) for i, n in enumerate(ns)]

        plain("07", I_MUL, table(2, "07", 8), 120)
        plain("08", I_MUL, table(10, "08", 8), 120)
        plain("09", I_MUL, table(5, "09", 8), 120)
        mixed = table(2, "10", 3) + table(5, "10", 3) + table(10, "10", 2)
        assert len({tuple(sorted((a, b))) for a, _, b in mixed}) == 8
        plain("10", I_MUL, spread(mixed, rng_for(3, "hop", "10", "o")), 120)
        h_add = [(a, "+", b) for a in range(100, 1000, 100) for b in range(100, 1000, 100) if a + b <= 1000]
        h_sub = [(a, "-", b) for a in range(200, 1001, 100) for b in range(100, a, 100)]
        rng = rng_for(3, "hop", "11", "d")
        for a, op, b in spread(pick("11", h_add, 4, "a") + pick("11", h_sub, 4, "s"), rng_for(3, "hop", "11", "o")):
            hop_item(s, "11", I_BOTH, a, op, b, rng, 1100, extra_prefer=[calc(a, op, b) + 100, calc(a, op, b) - 100, calc(a, op, b) // 10])
        a3 = [(a, "+", b) for a in range(115, 880, 7) for b in range(13, 90, 3) if a % 10 + b % 10 >= 10 and a % 10 and b % 10 and a % 100 + b < 100]
        s3 = [(a, "-", b) for a in range(131, 990, 7) for b in range(13, 90, 3) if a % 10 < b % 10 and a % 100 > b]
        plain("12", I_BOTH, spread(pick("12", a3, 4, "a") + pick("12", s3, 4, "s"), rng_for(3, "hop", "12", "o")), 1100)
    return s


# ---------------------------------------------------------------------------
# 3. Market Scales (market)
# ---------------------------------------------------------------------------

MARKET_COLS = ["round", "say_en", "say_fa", "goods", "target", "units", "mode", "help_fa"]
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
    row = s.add(round=rnd, say_fa=say, goods=goods, target=target, units="|".join(map(str, units)),
                mode=mode, help_fa=help_fa)
    MARKET_META.append((row, target))


def pay_help(target, units) -> str:
    parts = greedy(target, units)
    if len(parts) == 1:
        return tr(f"{fa(target)} {AFN} بده.", f"Give {target} afghani.")
    return tr(" جمع ".join(fa(p) for p in parts) + f" مساوی {fa(target)}.", " plus ".join(str(p) for p in parts) + f" equals {target}.")


def market(level: int) -> Sheet:
    if level >= 4:
        return market45(level)
    s = Sheet(MARKET_COLS)
    if level == 1:
        ranges = [(1, 3), (2, 5), (4, 7), (5, 10), (8, 12), (10, 15)]
        for i, (lo, hi) in enumerate(ranges):
            rnd = f"{i + 1:02d}"
            rng = rng_for(1, "market", rnd)
            values = list(range(lo, hi + 1))
            values = spread((values * 6)[:6] if len(values) < 6 else rng.sample(values, 6), rng)
            goods = GOODS[i:] + GOODS[:i]
            for j, n in enumerate(values):
                pic, noun = goods[j]
                market_row(s, rnd, tr(f"{fa(n)} {noun} بده.", f"Give {cnt(n, noun)}."), pic, n, [1], "count",
                           tr(f"{fa(n)} دانه {noun} روی ترازو بگذار.", f"Put {cnt(n, noun)} on the scales."))
    elif level == 2:
        plan = [((3, 10), 1, [1, 2, 5]), ((6, 15), 1, [1, 2, 5]), ((11, 25), 1, [1, 2, 5, 10]),
                ((30, 90), 10, [10, 20, 50]), ((21, 60), 1, [1, 2, 5, 10, 20, 50]),
                ((55, 100), 5, [1, 2, 5, 10, 20, 50, 100])]
        for i, ((lo, hi), step, units) in enumerate(plan):
            rnd = f"{i + 1:02d}"
            rng = rng_for(2, "market", rnd)
            prices = rng.sample([p for p in range(lo, hi + 1) if p % step == 0], 6)
            if i == 5 and 100 not in prices:
                prices[-1] = 100
            goods = SHOP[i:] + SHOP[:i]
            for j, p in enumerate(prices):
                pic, noun = goods[j]
                market_row(s, rnd, tr(f"{noun} {fa(p)} {AFN} است. پولش را بده.", cap(f"{costs(noun, p)}. Pay for it.")), pic, p, units, "pay", pay_help(p, units))
    else:
        both = f"هر دو چند {AFN} می{Z}شود؟ پولش را بده."
        both_en = "How many afghani do both make? Pay for it."
        # 01: a bill of two things, whole tens
        rng = rng_for(3, "market", "01")
        pairs = rng.sample([(a, b) for a in range(10, 90, 10) for b in range(10, 90, 10) if a != b and a + b <= 100], 6)
        for j, (a, b) in enumerate(pairs):
            (p1, n1), (p2, n2) = SHOP[j], SHOP[j + 3]
            market_row(s, "01", tr(f"{n1} {fa(a)} {AFN} و {n2} {fa(b)} {AFN} است. {both}", cap(f"{costs(n1, a)} and {costs(n2, b)}. {both_en}")), p1, a + b,
                       [10, 20, 50], "pay", tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}."))
        # 02: a bill of two things, with carrying
        rng = rng_for(3, "market", "02")
        pairs = rng.sample([(a, b) for a in range(12, 59) for b in range(12, 59)
                            if a % 10 + b % 10 >= 10 and a % 10 and b % 10 and a + b <= 100], 6)
        for j, (a, b) in enumerate(pairs):
            (p1, n1), (p2, n2) = SHOP[j + 2], SHOP[(j + 6) % len(SHOP)]
            market_row(s, "02", tr(f"{n1} {fa(a)} {AFN} و {n2} {fa(b)} {AFN} است. {both}", cap(f"{costs(n1, a)} and {costs(n2, b)}. {both_en}")), p1, a + b,
                       [1, 2, 5, 10, 20, 50], "pay", tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}."))
        # 03: several of one thing: tables of 2, 5 and 10
        rng = rng_for(3, "market", "03")
        deals = []
        for price in (2, 5, 10):
            deals += [(k, price) for k in rng.sample(range(2, 11), 2)]
        countable = [SHOP[0], SHOP[1], SHOP[2], SHOP[3], SHOP[4], GOODS[0]]
        for j, (k, price) in enumerate(spread(deals, rng)):
            pic, noun = countable[j]
            market_row(s, "03", tr(f"{fa(k)} {noun} می{Z}خری. هر {noun} {fa(price)} {AFN} است. چند {AFN} می{Z}شود؟ پولش را بده.", f"You buy {cnt(k, noun)}. Each {one(noun)} is {price} afghani. How many afghani does it make? Pay for it."),
                       pic, k * price, [1, 2, 5, 10, 20, 50, 100], "pay", tr(f"{fa(k)} ضرب {fa(price)} مساوی {fa(k * price)}.", f"{k} times {price} equals {k * price}."))
        # 04: prices in the hundreds
        rng = rng_for(3, "market", "04")
        units = [10, 20, 50, 100]
        for j, p in enumerate(rng.sample(range(110, 501, 10), 6)):
            pic, noun = BIG[j]
            market_row(s, "04", tr(f"{noun} {fa(p)} {AFN} است. پولش را بده.", cap(f"{costs(noun, p)}. Pay for it.")), pic, p, units, "pay", pay_help(p, units))
        # 05: a bill of two things, hundreds
        rng = rng_for(3, "market", "05")
        pairs = rng.sample([(a, b) for a in range(100, 301, 10) for b in range(20, 201, 10) if a + b <= 500], 6)
        for j, (a, b) in enumerate(pairs):
            (p1, n1), (p2, n2) = BIG[j], SHOP[j + 3]
            market_row(s, "05", tr(f"{n1} {fa(a)} {AFN} و {n2} {fa(b)} {AFN} است. {both}", cap(f"{costs(n1, a)} and {costs(n2, b)}. {both_en}")), p1, a + b,
                       units, "pay", tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}."))
        # 06: change
        rng = rng_for(3, "market", "06")
        deals = [(g, rng.choice([p for p in range(g // 2, g) if p % 10])) for g in (20, 50, 100, 50, 100, 100)]
        assert len(set(deals)) == 6
        for j, (given, price) in enumerate(deals):
            pic, noun = SHOP[(j + 1) % len(SHOP)]
            change = given - price
            market_row(s, "06", tr(f"{noun} {fa(price)} {AFN} است. مشتری {fa(given)} {AFN} داد. چند {AFN} باقی می{Z}ماند؟ باقی را پس بده.", cap(f"{costs(noun, price)}. The customer gave {given} afghani. How many afghani are left over? Give the change back.")),
                       pic, change, [1, 2, 5, 10, 20, 50], "pay", tr(f"{fa(given)} منفی {fa(price)} مساوی {fa(change)}.", f"{given} minus {price} equals {change}."))
    return s


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
    if up:
        say, help_fa = tr("این عددها را از کوچک به بزرگ بچین.", "Arrange these numbers from small to big."), tr("اول کوچکترین عدد را پیدا کن.", "First find the smallest number.")
    else:
        say, help_fa = tr("این عددها را از بزرگ به کوچک بچین.", "Arrange these numbers from big to small."), tr("اول بزرگترین عدد را پیدا کن.", "First find the biggest number.")
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


def weaver(level: int) -> Sheet:
    if level >= 4:
        return weaver45(level)
    s = Sheet(BUILDER_COLS)
    if level == 1:
        for a, n in [(1, 3), (1, 4), (1, 5), (2, 4), (0, 5)]:
            seq_item(s, "01", a, 1, n)
        for a, n in [(1, 3), (1, 5), (2, 4), (0, 4), (1, 6)]:
            seq_item(s, "02", a, 1, n, script="D")
        seq_item(s, "03", 3, 1, 6, extra=[1])
        seq_item(s, "03", 5, 1, 6, extra=[3])
        seq_item(s, "03", 1, 1, 7)
        seq_item(s, "03", 4, 1, 6, extra=[2], script="D")
        seq_item(s, "03", 1, 1, 8)
        seq_item(s, "04", 5, -1, 5)
        seq_item(s, "04", 10, -1, 5)
        seq_item(s, "04", 8, -1, 6)
        seq_item(s, "04", 6, -1, 7, script="D")
        seq_item(s, "04", 10, -1, 7)
        seq_item(s, "05", 9, 1, 5)
        seq_item(s, "05", 11, 1, 6, extra=[9])
        seq_item(s, "05", 15, 1, 6, extra=[12], script="D")
        seq_item(s, "05", 13, 1, 7)
        seq_item(s, "05", 20, -1, 6, extra=[13])
        seq_item(s, "06", 2, 2, 4, extra=[5, 7])
        seq_item(s, "06", 2, 2, 5, extra=[3, 9])
        seq_item(s, "06", 10, 2, 6, extra=[13, 15])
        seq_item(s, "06", 1, 2, 5, extra=[4, 6])
        seq_item(s, "06", 5, 5, 4, extra=[8, 12])
    elif level == 2:
        seq_item(s, "01", 2, 2, 6, extra=[5, 9])
        seq_item(s, "01", 12, 2, 6, extra=[15, 19])
        seq_item(s, "01", 20, 2, 6, extra=[25, 27])
        seq_item(s, "01", 1, 2, 6, extra=[4, 8])
        seq_item(s, "01", 44, 2, 6, extra=[47, 51])
        seq_item(s, "02", 10, 10, 6, extra=[15, 25])
        seq_item(s, "02", 40, 10, 7)
        seq_item(s, "02", 30, 10, 6, extra=[35, 45])
        seq_item(s, "02", 10, 10, 8)
        seq_item(s, "02", 50, 10, 6, extra=[5, 55], script="D")
        seq_item(s, "03", 5, 5, 6, extra=[12, 18])
        seq_item(s, "03", 25, 5, 6, extra=[32, 44])
        seq_item(s, "03", 50, 5, 6, extra=[57, 61])
        seq_item(s, "03", 70, 5, 6, extra=[73, 82])
        seq_item(s, "03", 5, 5, 8)
        order_item(s, "04", [12, 25, 31, 47, 60])
        order_item(s, "04", [34, 43, 30, 40, 44])
        order_item(s, "04", [19, 91, 90, 9, 29])
        order_item(s, "04", [56, 65, 55, 66, 60], up=False)
        order_item(s, "04", [78, 87, 70, 80, 88, 77], up=False)
        seq_item(s, "05", 28, 1, 6, extra=[38])
        seq_item(s, "05", 47, 1, 6, extra=[57])
        seq_item(s, "05", 68, 1, 6, extra=[86])
        seq_item(s, "05", 86, 1, 6, extra=[68])
        seq_item(s, "05", 95, 1, 6, extra=[90], script="D")
        seq_item(s, "06", 20, -2, 6, extra=[15, 13])
        seq_item(s, "06", 90, -10, 6, extra=[85, 45])
        seq_item(s, "06", 50, -5, 6, extra=[42, 33])
        seq_item(s, "06", 43, -1, 6, extra=[34])
        seq_item(s, "06", 4, 10, 6, extra=[40, 45])
    else:
        seq_item(s, "01", 2, 2, 8, table=2)
        seq_item(s, "01", 2, 2, 6, extra=[5, 9], table=2)
        seq_item(s, "01", 10, 2, 6, extra=[11, 15], table=2)
        seq_item(s, "01", 6, 2, 8, table=2)
        seq_item(s, "01", 20, -2, 6, extra=[15, 17], table=2)
        seq_item(s, "02", 5, 5, 8, table=5)
        seq_item(s, "02", 5, 5, 6, extra=[12, 22], table=5)
        seq_item(s, "02", 25, 5, 6, extra=[28, 42], table=5)
        seq_item(s, "02", 15, 5, 8, table=5)
        seq_item(s, "02", 50, -5, 6, extra=[32, 48], table=5)
        seq_item(s, "03", 10, 10, 8, table=10)
        seq_item(s, "03", 30, 10, 8, table=10)
        seq_item(s, "03", 50, 10, 6, extra=[55, 65], table=10)
        seq_item(s, "03", 10, 10, 6, extra=[1, 6], table=10, script="D")
        seq_item(s, "03", 100, -10, 6, extra=[75, 95], table=10)
        seq_item(s, "04", 100, 100, 8)
        seq_item(s, "04", 300, 100, 8)
        seq_item(s, "04", 50, 50, 6, extra=[125, 225])
        seq_item(s, "04", 1000, -100, 6, extra=[650, 950])
        seq_item(s, "04", 120, 100, 6, extra=[210, 400])
        order_item(s, "05", [120, 210, 102, 201, 200])
        order_item(s, "05", [345, 354, 435, 453, 534, 543])
        order_item(s, "05", [99, 909, 990, 900, 109])
        order_item(s, "05", [678, 687, 768, 786, 800], up=False)
        order_item(s, "05", [1000, 100, 10, 110, 101, 11], up=False)
        seq_item(s, "06", 96, 2, 6, extra=[99, 103])
        seq_item(s, "06", 85, 5, 6, extra=[102, 108])
        seq_item(s, "06", 170, 10, 6, extra=[195, 215])
        seq_item(s, "06", 395, 1, 6, extra=[390, 404])
        seq_item(s, "06", 250, 50, 6, extra=[275, 425])
    return s


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


def sorter(level: int) -> Sheet:
    if level >= 4:
        return sorter45(level)
    s = Sheet(SORTER_COLS)

    def shapes_round(rnd, plan):
        rng = rng_for(level, "sorter", rnd)
        rows = []
        for shape, idx in plan:
            for i in idx:
                rows.append((SHAPED[shape][i], shape))
        rng.shuffle(rows)
        assert len(rows) == 8
        for (pic, name), shape in rows:
            row = s.add(round=rnd, intro_fa=I_SHAPES, thing=pic, say_fa=tr(name, bare(name)), basket=SHAPES[shape][0],
                        basket_say_fa=tr(SHAPES[shape][1], bare(SHAPES[shape][1])))
            SORT_META.append((row, "shape", shape))

    def parity_round(rnd, pool):
        rng = rng_for(level, "sorter", rnd)
        evens = rng.sample([n for n in pool if n % 2 == 0], 4)
        odds = rng.sample([n for n in pool if n % 2 == 1], 4)
        for n in spread(evens + odds, rng):
            basket = EVEN if n % 2 == 0 else ODD
            row = s.add(round=rnd, intro_fa=I_PARITY, thing=W(n), say_fa=tr(fa(n), str(n)), basket=basket[0], basket_say_fa=tr(basket[1], bare(basket[1])))
            SORT_META.append((row, "parity", n))

    def fraction_round(rnd, plan, named=True):
        """named=False: the speech names only the thing, not its fraction, so
        the child has to judge from the picture."""
        rng = rng_for(level, "sorter", rnd)
        rows = [(FRACTIONS[kind][i], kind) for kind, idx in plan for i in idx]
        rng.shuffle(rows)
        assert len(rows) == 8
        for (pic, name), kind in rows:
            basket = FRAC_BASKET[kind]
            noun = FRACTION_NOUNS[FRACTIONS[kind].index((pic, name))]
            en = FRACTION_EN[kind].format(a=art(bare(noun)), x=bare(noun)) if named else bare(noun)
            if not named:
                name = FRACTION_NOUNS[FRACTIONS[kind].index((pic, name))]
                assert basket[1] not in name
            row = s.add(round=rnd, intro_fa=I_FRACTION, thing=pic, say_fa=tr(name, en), basket=basket[0], basket_say_fa=tr(basket[1], bare(basket[1])))
            SORT_META.append((row, "fraction", kind))

    if level == 1:
        shapes_round("01", [("circle", [0, 1, 2, 3]), ("square", [0, 1, 2, 3])])
        shapes_round("02", [("circle", [4, 5, 6, 7]), ("triangle", [0, 1, 2, 3])])
        shapes_round("03", [("circle", [1, 4, 6]), ("square", [1, 2, 3]), ("triangle", [1, 2])])
        shapes_round("04", [("circle", [2, 3]), ("square", [1, 2]), ("triangle", [1, 2]), ("rectangle", [1, 2])])
    elif level == 2:
        parity_round("01", range(1, 11))
        parity_round("02", range(11, 21))
        fraction_round("03", [("whole", [0, 1, 2, 3]), ("half", [0, 1, 2, 3])])
        fraction_round("04", [("whole", [0, 1]), ("half", [0, 1, 2]), ("quarter", [0, 1, 2])])
    else:
        parity_round("01", range(21, 100))
        rng = rng_for(3, "sorter", "02")
        below = [499, 490] + rng.sample(range(100, 480), 2)
        above = [501, 510] + rng.sample(range(520, 1000), 2)
        for n in spread(below + above, rng):
            less = n < 500
            en = "less than 500" if less else "more than 500"
            row = s.add(round="02", intro_fa=I_500, thing=W(n), say_fa=tr(fa(n), str(n)),
                        basket="f:" + tr(("f:کمتر از ۵۰۰" if less else "f:بیشتر از ۵۰۰")[2:], en),
                        basket_say_fa=tr("کمتر از پنج" + Z + "صد" if less else "بیشتر از پنج" + Z + "صد", en))
            SORT_META.append((row, "500", n))
        fraction_round("03", [("whole", [2, 3]), ("half", [1, 2, 3]), ("quarter", [1, 2, 3])], named=False)
        parity_round("04", range(101, 1000))
    return s


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


def mason(level: int) -> Sheet:
    if level >= 4:
        return mason45(level)
    s = Sheet(LP_COLS)
    order = ["circle", "square", "triangle", "rectangle"]
    if level == 1:
        rng = rng_for(1, "mason", "01")
        for shape in order + spread(order, rng):
            pic, name = SHAPES[shape]
            first = len([r for r in s.rows if r["answer"] == pic]) == 0
            say = tr(f"{name} کدام است؟", f"Which one is the {bare(name)}?") if first else tr(f"شکل {name} را پیدا کن.", f"Find the {bare(name)} shape.")
            lp(s, "01", I_SHAPE, say, pic, [SHAPES[o][0] for o in order if o != shape], help_fa=tr(f"این شکل {name} است.", f"This shape is a {bare(name)}."))
        rng = rng_for(1, "mason", "02")
        for k in (1, 2):
            for shape in spread(order, rng):
                pic, noun = SHAPED[shape][k]
                wrong = [SHAPED[o][1 + (k + j) % 3][0] for j, o in enumerate(x for x in order if x != shape)]
                if shape == "rectangle":  # a square is a rectangle too: never offer one as a wrong choice
                    wrong[order.index("square")] = SHAPED["circle"][4 + k][0]
                    assert not set(wrong) & {p for p, _ in SHAPED["square"]} and len(set(wrong)) == 3
                lp(s, "02", I_SHAPE_OBJ, tr(f"کدام چیز شکل {SHAPES[shape][1]} دارد؟", f"Which thing has the shape of a {bare(SHAPES[shape][1])}?"), pic, wrong,
                   help_fa=tr(f"{noun} شکل {SHAPES[shape][1]} دارد.", f"The {bare(noun)} has the shape of a {bare(SHAPES[shape][1])}."))
        for i, (noun, long_pic, short_pic, long_word, short_word) in enumerate(LENGTHS):
            other = LENGTHS[(i + 1) % len(LENGTHS)]
            lp(s, "03", I_LONG, tr(f"کدام {noun} {long_word} است؟", f"Which {bare(noun)} is {bare(long_word)}?"), long_pic, [short_pic, other[1], other[2]],
               help_fa=tr(f"این {noun} {long_word} است.", f"This {bare(noun)} is {bare(long_word)}."))
        for i, (noun, long_pic, short_pic, long_word, short_word) in enumerate(LENGTHS):
            other = LENGTHS[(i + 2) % len(LENGTHS)]
            lp(s, "03", I_LONG, tr(f"کدام {noun} {short_word} است؟", f"Which {bare(noun)} is {bare(short_word)}?"), short_pic, [long_pic, other[1], other[2]],
               help_fa=tr(f"این {noun} {short_word} است.", f"This {bare(noun)} is {bare(short_word)}."))
        corners = {"circle": 0, "square": 4, "triangle": 3, "rectangle": 4}
        rng = rng_for(1, "mason", "04")
        for shape, what in [("triangle", "گوشه"), ("square", "ضلع"), ("circle", "گوشه"), ("rectangle", "گوشه"),
                            ("triangle", "ضلع"), ("square", "گوشه")]:
            pic, name = SHAPES[shape]
            n = corners[shape]
            row = lp(s, "04", I_CORNER, tr(f"{name} چند {what} دارد؟", f"How many {many(what)} does a {bare(name)} have?"), W(n), [W(x) for x in near(n, rng, 0, 8)], show=pic,
                     help_fa=(tr(f"{name} {fa(n)} {what} دارد.", f"A {bare(name)} has {cnt(n, what)}.") if n else tr(f"{name} هیچ {what} ندارد.", f"A {bare(name)} has no {many(what)}.")))
            MASON_META.append((row, n))
        lp(s, "04", I_CORNER, tr("کدام شکل سه گوشه دارد؟", "Which shape has 3 corners?"), "shape_triangle", ["shape_circle", "shape_square", "shape_rectangle"],
           help_fa=tr("مثلث سه گوشه دارد.", "A triangle has 3 corners."))
        lp(s, "04", I_CORNER, tr("کدام شکل هیچ گوشه ندارد؟", "Which shape has no corners?"), "shape_circle", ["shape_triangle", "shape_square", "shape_rectangle"],
           help_fa=tr("دایره هیچ گوشه ندارد.", "A circle has no corners."))
    elif level == 2:
        def clock(h):
            return f"clock_{(h - 1) % 12 + 1}"

        def wrap(h):
            return (h - 1) % 12 + 1

        def hear_clock(rnd, hours):
            rng = rng_for(2, "mason", rnd)
            for h in spread(hours, rng):
                wrong = [clock(h - 1), clock(h + 1), clock(h + 6)]
                row = lp(s, rnd, I_CLOCK, tr(f"ساعت {fa(h)} است. ساعت درست را پیدا کن.", f"It is {h} o'clock. Find the right clock."), clock(h), wrong,
                         help_fa=tr(f"عقربه کوتاه طرف {fa(h)} است و عقربه دراز طرف دوازده.", f"The short hand points to {h} and the long hand to 12."))
                MASON_META.append((row, h))

        hear_clock("01", [1, 2, 3, 4, 5, 6])
        hear_clock("02", [7, 8, 9, 10, 11, 12])
        rng = rng_for(2, "mason", "03")
        for h in rng.sample(range(1, 13), 8):
            wrong = near(h, rng, 1, 12, [12 if h != 12 else 6, wrap(h + 1), wrap(h - 1)])
            row = lp(s, "03", I_CLOCK_READ, tr("ساعت چند است؟", "What time is it?"), W(h), [W(x) for x in wrong], show=clock(h),
                     help_fa=tr(f"عقربه کوتاه طرف {fa(h)} است. ساعت {fa(h)} است.", f"The short hand points to {h}. It is {h} o'clock."))
            MASON_META.append((row, h))
        rng = rng_for(2, "mason", "04")
        hours = rng.sample(range(1, 12), 7)
        for h in hours[:4]:
            wrong = near(h, rng, 1, 12, [12, wrap(h + 1), wrap(h - 1)])
            row = lp(s, "04", I_CLOCK_LATER, tr("ساعت چند است؟", "What time is it?"), D(h), [D(x) for x in wrong], show=clock(h),
                     help_fa=tr(f"عقربه کوتاه طرف {fa(h)} است. ساعت {fa(h)} است.", f"The short hand points to {h}. It is {h} o'clock."))
            MASON_META.append((row, h))
        for h in hours[4:] + [12]:
            later = wrap(h + 1)
            wrong = near(later, rng, 1, 12, [h, wrap(h - 1), wrap(h + 2)])
            row = lp(s, "04", I_CLOCK_LATER, tr(f"حالا ساعت {fa(h)} است. یک ساعت بعد، ساعت چند می{Z}شود؟", f"Now it is {h} o'clock. One hour later, what time will it be?"), W(later),
                     [W(x) for x in wrong], show=clock(h), help_fa=tr(f"یک ساعت بعد از {fa(h)}، ساعت {fa(later)} می{Z}شود.", f"One hour after {h}, it is {later} o'clock."))
            MASON_META.append((row, h % 12 + 1))
    else:
        def q(rnd, say, ans, prefer, help_fa, hi=2000):
            rng = rng_for(3, "mason", rnd, say)
            row = lp(s, rnd, I_LENGTH, say, W(ans), [W(x) for x in near(ans, rng, 0, hi, prefer)], help_fa=help_fa)
            MASON_META.append((row, ans))

        for m in (1, 2, 5, 10):
            q("01", tr(f"{fa(m)} {M} چند {CM} است؟", f"How many centimetres is {nn(m, 'metre')}?"), m * 100, [m * 10, m * 100 + 100, m],
              tr(f"هر متر صد {CM} است. {fa(m)} {M}، {fa(m * 100)} {CM} می{Z}شود.", f"Each metre is 100 centimetres. {nn(m, 'metre')} makes {m * 100} centimetres."))
        q("01", tr(f"نیم {M} چند {CM} است؟", "How many centimetres is half a metre?"), 100 // 2, [5, 500, 20], tr(f"یک متر صد {CM} است. نیم آن پنجاه {CM} است.", "One metre is 100 centimetres. Half of it is 50 centimetres."))
        for c in (300, 700, 400):
            q("01", tr(f"{fa(c)} {CM} چند {M} است؟", f"How many metres is {c} centimetres?"), c // 100, [c // 10, c // 100 + 1, c // 100 - 1],
              tr(f"هر صد {CM} یک {M} است. {fa(c)} {CM}، {fa(c // 100)} {M} می{Z}شود.", f"Every 100 centimetres is 1 metre. {c} centimetres makes {nn(c // 100, 'metre')}."))
        adds = [("چوب", 40, 35, CM), ("ریسمان", 28, 17, CM), ("تکه", 56, 29, CM), ("چوب", 65, 25, CM),
                ("دیوار", 12, 8, M), ("ریسمان", 37, 26, M), ("جوی", 45, 15, M), ("سرک", 120, 60, M)]
        for noun, a, b, unit in adds:
            q("02", tr(f"یک {noun} {fa(a)} {unit} است و {noun} دیگر {fa(b)} {unit}. هر دو با هم چند {unit} می{Z}شود؟", f"One {bare(noun)} is {a} {many(unit)} and another {bare(noun)} is {b} {many(unit)}. How many {many(unit)} do both make together?"),
              a + b, [a + b - 10, a - b, a + b + 10], tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}."))
        subs = [("ریسمان", 90, 35, CM), ("تکه", 72, 48, CM), ("چوب", 50, 15, CM), ("سیم", 100, 40, CM),
                ("ریسمان", 30, 12, M), ("تکه", 64, 27, M), ("سیم", 81, 36, M), ("ریسمان", 200, 50, M)]
        for noun, a, b, unit in subs:
            q("03", tr(f"یک {noun} {fa(a)} {unit} بود. {fa(b)} {unit} آن بریده شد. چند {unit} ماند؟", f"A {bare(noun)} was {a} {many(unit)}. {b} {many(unit)} of it was cut off. How many {many(unit)} are left?"),
              a - b, [a - b + 10, a + b, a - b - 10], tr(f"{fa(a)} منفی {fa(b)} مساوی {fa(a - b)}.", f"{a} minus {b} equals {a - b}."))
        for m, c in [(1, 20), (2, 50), (3, 5), (1, 75), (4, 10), (2, 8)]:
            q("04", tr(f"{fa(m)} {M} و {fa(c)} {CM}، چند {CM} می{Z}شود؟", f"{nn(m, 'metre')} and {c} centimetres make how many centimetres?"), m * 100 + c, [m * 10 + c, m + c, m * 100 + c * 10],
              tr(f"{fa(m)} {M}، {fa(m * 100)} {CM} است. {fa(m * 100)} جمع {fa(c)} مساوی {fa(m * 100 + c)}.", f"{nn(m, 'metre')} is {m * 100} centimetres. {m * 100} plus {c} equals {m * 100 + c}."))
        for n in (150, 130):
            q("04", tr(f"{fa(n)} {CM}، یک {M} و چند {CM} است؟", f"{n} centimetres is 1 metre and how many centimetres?"), n - 100, [n, (n - 100) // 10, n - 100 + 10],
              tr(f"یک {M} صد {CM} است. {fa(n)} منفی صد مساوی {fa(n - 100)}.", f"One metre is 100 centimetres. {n} minus 100 equals {n - 100}."))
    return s


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


def div_item(s, rnd, intro, a, b, rng, hi, say=None, show="", extra_prefer=(), script="W"):
    assert b > 0 and a % b == 0, (a, b)
    ans = a // b
    if say is None:
        say = tr(f"{fa(a)} تقسیم {fa(b)} چند می{Z}شود؟", f"{a} divided by {b} makes how many?")
    help_fa = tr(f"{fa(a)} تقسیم {fa(b)} مساوی {fa(ans)}.", f"{a} divided by {b} equals {ans}.")
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


def pie_item(s, rnd, intro, which):
    (k, n), name, en = PIES4[which]
    wrong = [pie(*kn) for kn, _, _ in PIES4 if kn != (k, n)]
    wrong = wrong[which % 4:] + wrong[:which % 4]
    row = lp(s, rnd, intro, tr(f"کدام شکل {name} را نشان می{Z}دهد؟", f"Which picture shows {en}?"), pie(k, n), wrong[:3],
             help_fa=tr(f"{name} یعنی {fa(k)} حصه از {fa(n)} حصه برابر.", f"{cap(en)} means {k} of {n} equal parts."))
    CHECK_META.append((row, Fraction(k, n)))


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


def flock45(level: int) -> Sheet:
    s = Sheet(LP_COLS)
    if level == 4:
        shares = [(n, k) for n in range(6, 21) for k in range(2, 7) if n % k == 0 and n // k >= 2]
        rng = rng_for(4, "flock", "01")
        for i, (n, k) in enumerate(rng.sample(shares, 8)):
            share_item(s, "01", I_SHARE, n, k, SHARE_OBJS[i], rng)
        rng = rng_for(4, "flock", "02")
        groups = rng.sample([(k, m) for k in range(3, 10) for m in range(3, 7)], 8)
        for i, (k, m) in enumerate(groups):
            group_item(s, "02", I_GROUPS, k, m, SHARE_OBJS[(i + 3) % 8], rng)
        rng = rng_for(4, "flock", "03")
        small = rng.sample(range(6, 21, 2), 4)
        large = rng.sample(range(30, 101, 10), 2) + rng.sample([24, 36, 48, 64, 72, 86], 2)
        for i, n in enumerate(small):
            half_item(s, "03", I_HALF, n, rng, obj=SHARE_OBJS[(i + 5) % 8])
        for i, n in enumerate(large):
            half_item(s, "03", I_HALF, n, rng, script="D" if i % 2 else "W")
        rng = rng_for(4, "flock", "04")
        quarters = rng.sample(range(8, 41, 4), 4)
        thirds = rng.sample(range(6, 31, 3), 4)
        for q, t in zip(quarters, thirds):
            quarter_item(s, "04", I_PARTS, q, rng)
            third_item(s, "04", I_PARTS, t, rng)
        rng = rng_for(4, "flock", "05")
        for which in (0, 3, 1, 4, 2):
            pie_item(s, "05", I_PIE, which)
        for k, n in [(1, 2), (1, 3), (3, 4)]:
            parts_item(s, "05", I_PIE, k, n, rng)
        rng = rng_for(4, "flock", "06")
        (n1, k1), (n2, k2) = rng.sample(shares, 2)
        share_item(s, "06", I_MIX, n1, k1, SHARE_OBJS[6], rng)
        group_item(s, "06", I_MIX, rng.randint(6, 9), rng.randint(3, 6), SHARE_OBJS[0], rng)
        half_item(s, "06", I_MIX, rng.choice([28, 46, 52, 68]), rng)
        quarter_item(s, "06", I_MIX, rng.choice([44, 48, 60, 80]), rng)
        share_item(s, "06", I_MIX, n2, k2, SHARE_OBJS[2], rng)
        third_item(s, "06", I_MIX, rng.choice([33, 36, 45, 60]), rng)
        group_item(s, "06", I_MIX, rng.randint(3, 5), rng.randint(3, 6), SHARE_OBJS[4], rng)
        half_item(s, "06", I_MIX, rng.choice([90, 110, 120, 150]), rng, script="D")
    else:
        top = 10_000_000
        rng = rng_for(5, "flock", "01")
        for n in rng.sample(range(2000, 9001, 1000), 6) + [10000, 20000]:
            hear_item(s, "01", I_THOUSANDS, n, "W", rng, 0, top, prefer=[n // 10, n + 1000, n * 10])
        rng = rng_for(5, "flock", "02")
        for i, (a, b) in enumerate(zip(rng.sample(range(1, 10), 4), rng.sample(range(1, 10), 4))):
            forms = [1000 * a + 100 * b, 1000 * a + 10 * b, 1000 * a + b]
            n = forms[i % 3]
            hear_item(s, "02", I_BIG, n, "W", rng, 0, top, prefer=[f for f in forms if f != n] + [100 * a + b])
        four = [x for x in range(1234, 9877) if "0" not in str(x) and len(set(str(x))) == 4]
        for n in rng.sample(four, 4):
            hear_item(s, "02", I_BIG, n, "W", rng, 0, top, prefer=rng.sample(digit_perms(n), 2))
        rng = rng_for(5, "flock", "03")
        for n in spread([12000, 25000, 40000, 75000, 100000, 250000, 500000, 1000000], rng):
            hear_item(s, "03", I_BIG, n, "W", rng, 0, top, prefer=[n // 10, n * 10 if n < 1000000 else n // 100, n + 1000])
        rng = rng_for(5, "flock", "04")
        picks = rng.sample(four, 6) + rng.sample(range(10500, 99000, 500), 2)
        for n in picks[:4]:
            hear_item(s, "04", I_BIG, n, "D", rng, 0, top, prefer=rng.sample(digit_perms(n), 2))
        for i, n in enumerate(picks[4:]):
            match_item(s, "04", I_MATCH, n, "D" if i % 2 == 0 else "W", rng, 0, top, prefer=rng.sample(digit_perms(n), 2))
        rng = rng_for(5, "flock", "05")
        zeros = [1000 * rng.randint(1, 9) + 10 * rng.randint(1, 9) + rng.randint(1, 9),
                 1000 * rng.randint(1, 9) + 100 * rng.randint(1, 9) + rng.randint(1, 9),
                 1000 * rng.randint(1, 9) + rng.randint(1, 9)]
        for n in spread(rng.sample(four, 5) + zeros, rng):
            place4_item(s, "05", I_PLACE4, n, rng)
        rng = rng_for(5, "flock", "06")
        for i, x in enumerate(rng.sample(four, 3) + [rng.choice(range(12345, 98765, 1111))]):
            numeral_compare_item(s, "06", I_COMPARE, similar_numbers(x, rng, 1000, 99999), biggest=i % 2 == 0)
        for n in (999, 9999):
            next_item(s, "06", I_NEXT, n, True, rng, 0, top)
        for n in (2000, 10000):
            next_item(s, "06", I_NEXT, n, False, rng, 0, top)
    return s


# ---------------------------------------------------------------------------
# Levels 4 and 5: Number Hop (journey)
# ---------------------------------------------------------------------------

I_DIV = tr("تقسیم کن و جواب را انتخاب کن.", "Divide and choose the answer.")
I_MUL_D = tr("ضرب کن و جواب را با عدد دری انتخاب کن.", "Multiply and choose the answer in Dari numbers.")
I_THOUSAND_SUM = tr("هزارها و صدها را جمع و منفی کن.", "Add and subtract the thousands and the hundreds.")
I_TEN_TIMES = tr("ضرب در ده و صد را تمرین کن.", "Practise multiplying by 10 and by 100.")
I_MUL_BIG = tr("عدد بزرگ را ضرب کن: اول یک" + Z + "ها، بعد ده" + Z + "ها.", "Multiply the big number: first the ones, then the tens.")


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


def hop45(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    def table(t, rnd, k=8, tag=""):
        ns = rng_for(level, "hop", rnd, "table", t, tag).sample(range(2, 11), k)
        return [(n, "*", t) if i % 2 == 0 else (t, "*", n) for i, n in enumerate(ns)]

    def told(rnd, intro, items, hi):
        rng = rng_for(level, "hop", rnd, "d")
        for say, a, op, b in items:
            if op == "/":
                div_item(s, rnd, intro, a, b, rng, hi, say=say)
            else:
                hop_item(s, rnd, intro, a, op, b, rng, hi, say=say, extra_prefer=[a * b + rng.choice([-1, 1])])

    if level == 4:
        for i, t in enumerate((3, 4, 6, 7, 8, 9)):
            rnd = f"{i + 1:02d}"
            rng = rng_for(4, "hop", rnd, "d")
            for a, op, b in table(t, rnd):
                hop_item(s, rnd, I_MUL, a, op, b, rng, 120, extra_prefer=[a * b + rng.choice([-1, 1])])
        rng = rng_for(4, "hop", "07", "d")
        mixed = [x for t in (3, 4, 6, 7, 8, 9) for x in table(t, "07", 2)[:2]]
        mixed = [m for i, m in enumerate(mixed) if tuple(sorted((m[0], m[2]))) not in [tuple(sorted((x[0], x[2]))) for x in mixed[:i]]]
        assert len(mixed) >= 8, mixed
        for a, op, b in spread(mixed[:8], rng_for(4, "hop", "07", "o")):
            hop_item(s, "07", I_MUL_D, a, op, b, rng, 120, extra_prefer=[a * b + rng.choice([-1, 1])], script="D")
        rng = rng_for(4, "hop", "08", "d")
        easy = [(b * c, b) for b in (2, 3, 4, 5) for c in range(2, 11)]
        for a, b in rng.sample(easy, 8):
            div_item(s, "08", I_DIV, a, b, rng, 120)
        rng = rng_for(4, "hop", "09", "d")
        hard = [(b * c, b) for b in (6, 7, 8, 9) for c in range(2, 11)]
        for a, b in rng.sample(hard, 8):
            div_item(s, "09", I_DIV, a, b, rng, 120)
        told("10", I_STORY, stories4(rng_for(4, "hop", "10", "s")), 120)
    else:
        top = 100000
        rng = rng_for(5, "hop", "01", "d")
        adds = [(a, "+", b) for a in range(500, 9001, 500) for b in range(500, 9001, 500) if a + b <= 10000 and (a % 1000 or b % 1000)]
        subs = [(a, "-", b) for a in range(2000, 10001, 500) for b in range(500, a, 500) if a % 1000 == 0 and b % 1000]
        for a, op, b in spread(rng.sample(adds, 4) + rng.sample(subs, 4), rng):
            r = calc(a, op, b)
            hop_item(s, "01", I_THOUSAND_SUM, a, op, b, rng, top, extra_prefer=[r + 1000, r - 1000, r + 100])
        rng = rng_for(5, "hop", "02", "d")
        tens = [(a, "*", 10) for a in rng.sample([x for x in range(12, 100) if x % 10], 3)]
        tens += [(a, "*", 100) for a in rng.sample(range(3, 60), 2)]
        tens += [(10 * rng.randint(2, 9), "*", rng.randint(3, 9)), (rng.randint(3, 9), "*", 10 * rng.randint(2, 9)),
                 (100 * rng.randint(2, 9), "*", rng.randint(2, 9))]
        for a, op, b in spread(tens, rng):
            hop_item(s, "02", I_TEN_TIMES, a, op, b, rng, top, extra_prefer=[a * b * 10, a * b // 10, a * b + 10])
        rng = rng_for(5, "hop", "03", "d")
        plain = [(a, b) for a in range(11, 45) for b in (2, 3, 4) if a % 10 and (a % 10) * b < 10 and (a // 10) * b < 10]
        for a, b in rng.sample(plain, 8):
            hop_item(s, "03", I_MUL_BIG, a, "*", b, rng, top, extra_prefer=[a * b + 10, a * b - 1])
        rng = rng_for(5, "hop", "04", "d")
        carry = [(a, b) for a in range(13, 100) for b in range(3, 10) if (a % 10) * b >= 10]
        for a, b in rng.sample(carry, 8):
            lost = (a // 10 * b) * 10 + (a % 10 * b) % 10   # the carried tens forgotten
            hop_item(s, "04", I_MUL_BIG, a, "*", b, rng, top, extra_prefer=[lost, a * b + 10, a * b - 10])
        rng = rng_for(5, "hop", "05", "d")
        three = [(a, b) for a in range(102, 460) for b in (2, 3, 4, 5) if a % 10 and a * b < 1000]
        for a, b in rng.sample(three, 8):
            hop_item(s, "05", I_MUL_BIG, a, "*", b, rng, top, extra_prefer=[a * b + 100, a * b - 10, a * b + 10])
        rng = rng_for(5, "hop", "06", "d")
        two = [(a, b) for a in range(11, 26) for b in range(11, 16) if a != b]
        for a, b in rng.sample(two, 8):
            lost = a * (b % 10) + a * (b // 10)   # the ten of the second number counted as one
            hop_item(s, "06", I_MUL_BIG, a, "*", b, rng, top, extra_prefer=[lost, a * b + 10, a * b - 100])
        rng = rng_for(5, "hop", "07", "d")
        long_div = [(b * c, b) for b in range(2, 10) for c in range(11, 41) if b * c <= 200 and c % 10]
        by_ten = [(10 * c, 10) for c in range(12, 90) if c % 10] + [(100 * c, 100) for c in range(2, 40)]
        for a, b in spread(rng.sample(long_div, 5) + rng.sample(by_ten, 3), rng):
            div_item(s, "07", I_DIV, a, b, rng, top, extra_prefer=[a // b + 10, a // b * 10 if b >= 10 else None])
        told("08", I_STORY, stories5(rng_for(5, "hop", "08", "s")), top)
    return s


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


def market45(level: int) -> Sheet:
    s = Sheet(MARKET_COLS)
    small = [1, 2, 5, 10, 20, 50]
    if level == 4:
        # 01: sharing on the scales
        rng = rng_for(4, "market", "01")
        shares = rng.sample([(n, k) for n in range(8, 41) for k in range(2, 7) if n % k == 0 and 2 <= n // k <= 10], 6)
        for j, (n, k) in enumerate(shares):
            pic, noun = COUNTABLE[(j + 5) % len(COUNTABLE)]
            market_row(s, "01", tr(f"{fa(n)} {noun} را بین {fa(k)} نفر برابر تقسیم کن. حصه یک نفر را روی ترازو بگذار.",
                                   f"Share {cnt(n, noun)} equally among {k} people. Put one person's share on the scales."),
                       pic, n // k, [1], "count", tr(f"{fa(n)} تقسیم {fa(k)} مساوی {fa(n // k)}.", f"{n} divided by {k} equals {n // k}."))
        # 02, 03: several of one thing, all the tables
        for rnd, prices in (("02", (3, 4, 6)), ("03", (7, 8, 9))):
            rng = rng_for(4, "market", rnd)
            deals = [(k, p) for p in prices for k in rng.sample(range(3, 11), 2)]
            for j, (k, p) in enumerate(spread(deals, rng)):
                buy_row(s, rnd, k, p, COUNTABLE[(j + int(rnd)) % len(COUNTABLE)], small)
        # 04: by the kilo
        rng = rng_for(4, "market", "04")
        for j, (k, p) in enumerate(zip(rng.sample(range(2, 10), 6), rng.sample(range(20, 91, 10), 6))):
            kilo_row(s, "04", k, p, KILO_GOODS[j], [10, 20, 50, 100, 500])
        # 05: half a kilo, one and a half, two and a half
        rng = rng_for(4, "market", "05")
        prices = rng.sample(range(20, 81, 4), 6)
        for j, p in enumerate(prices):
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
        # 06: several of one thing, then the change
        rng = rng_for(4, "market", "06")
        deals = []
        while len(deals) < 6:
            k, p, given = rng.randint(3, 9), rng.randint(3, 9), rng.choice([50, 100])
            if 20 <= k * p < given and (k, p) not in [(d[0], d[1]) for d in deals] and given - k * p not in [d[2] - d[0] * d[1] for d in deals]:
                deals.append((k, p, given))
        for j, (k, p, given) in enumerate(deals):
            pic, noun = COUNTABLE[(j + 3) % len(COUNTABLE)]
            change = given - k * p
            market_row(s, "06", tr(f"مشتری {fa(k)} {noun} می{Z}خرد. هر {noun} {fa(p)} {AFN} است. مشتری {fa(given)} {AFN} داد. چند {AFN} باقی می{Z}ماند؟ باقی را پس بده.",
                                   f"The customer buys {cnt(k, noun)}. Each {one(noun)} is {p} afghani. The customer gave {given} afghani. How many afghani are left over? Give the change back."),
                       pic, change, small, "pay",
                       tr(f"{fa(k)} ضرب {fa(p)} مساوی {fa(k * p)}. {fa(given)} منفی {fa(k * p)} مساوی {fa(change)}.",
                          f"{k} times {p} equals {k * p}. {given} minus {k * p} equals {change}."))
    else:
        notes = [50, 100, 500, 1000]   # few kinds, so that the 1000 note is drawn large enough to read
        # 01: prices in the thousands
        rng = rng_for(5, "market", "01")
        for j, p in enumerate(rng.sample(range(650, 5001, 50), 6)):
            pic, noun = BIG[j]
            market_row(s, "01", tr(f"{noun} {fa(p)} {AFN} است. {PAY_IT}", cap(f"{costs(noun, p)}. Pay for it.")), pic, p, notes, "pay", pay_help(p, notes))
        # 02: several of one big thing
        rng = rng_for(5, "market", "02")
        several = [("blanket", "کمپل"), ("hen", "مرغ"), ("flour_sack", "بوری آرد"), ("rice_sack", "بوری برنج"), ("goat", "بز"), ("carpet", "قالین")]
        for j, (k, p) in enumerate(zip([2, 3, 4, 5, 3, 2], rng.sample(range(250, 951, 50), 6))):
            buy_row(s, "02", k, p, several[j], notes)
        # 03: change from a large note
        rng = rng_for(5, "market", "03")
        for j, given in enumerate([500, 1000, 500, 1000, 1000, 500]):
            price = rng.choice([p for p in range(given // 4, given - 20, 5) if p % 50])
            pic, noun = BIG[(j + 4) % len(BIG)]
            change = given - price
            market_row(s, "03", tr(f"{noun} {fa(price)} {AFN} است. مشتری {fa(given)} {AFN} داد. چند {AFN} باقی می{Z}ماند؟ باقی را پس بده.",
                                   cap(f"{costs(noun, price)}. The customer gave {given} afghani. How many afghani are left over? Give the change back.")),
                       pic, change, [5, 10, 20, 50, 100, 500], "pay",
                       tr(f"{fa(given)} منفی {fa(price)} مساوی {fa(change)}.", f"{given} minus {price} equals {change}."))
        # 04: many kilos
        rng = rng_for(5, "market", "04")
        for j, (k, p) in enumerate(zip(rng.sample(range(4, 13), 6), rng.sample(range(35, 96, 5), 6))):
            kilo_row(s, "04", k, p, KILO_GOODS[(j + 3) % len(KILO_GOODS)], [5, 10, 20, 50, 100, 500])
        # 05: a price shared, a half price
        rng = rng_for(5, "market", "05")
        for j in range(6):
            pic, noun = BIG[(j + 1) % len(BIG)]
            if j % 2 == 0:
                p = rng.choice(range(300, 1801, 100))
                market_row(s, "05", tr(f"{noun} {fa(p)} {AFN} است. امروز به نیم قیمت است. {PAY_IT}",
                                       cap(f"{costs(noun, p)}. Today it is at half price. Pay for it.")),
                           pic, p // 2, notes, "pay", tr(f"نیم {fa(p)}، {fa(p // 2)} است.", f"Half of {p} is {p // 2}."))
            else:
                k = rng.choice([3, 4, 5])
                share = rng.choice(range(100, 400, 50))
                p = share * k
                market_row(s, "05", tr(f"{noun} {fa(p)} {AFN} است. {fa(k)} نفر پول آن را برابر تقسیم می{Z}کنند. حصه یک نفر را بده.",
                                       cap(f"{costs(noun, p)}. {k} people share the cost equally. Pay one person's share.")),
                           pic, share, notes, "pay", tr(f"{fa(p)} تقسیم {fa(k)} مساوی {fa(share)}.", f"{p} divided by {k} equals {share}."))
    return s


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
    row = s.add(round=rnd, intro_fa=intro, say_fa=say, tiles="|".join(things), extra="", rtl="",
                done_fa=tr("، ".join(spoken[t][0] for t in things) + ".", ", ".join(spoken[t][1] for t in things) + "."), help_fa=help_fa)
    ORDER_META.append((row, up))


def weaver45(level: int) -> Sheet:
    s = Sheet(BUILDER_COLS)
    if level == 4:
        seq_item(s, "01", 3, 3, 8, table=3)
        seq_item(s, "01", 3, 3, 6, extra=[10, 14], table=3)
        seq_item(s, "01", 4, 4, 8, table=4)
        seq_item(s, "01", 16, 4, 6, extra=[18, 30], table=4, script="D")
        seq_item(s, "01", 30, -3, 6, extra=[20, 25], table=3)
        seq_item(s, "02", 6, 6, 8, table=6)
        seq_item(s, "02", 6, 6, 6, extra=[16, 32], table=6)
        seq_item(s, "02", 7, 7, 8, table=7)
        seq_item(s, "02", 28, 7, 6, extra=[36, 54], table=7, script="D")
        seq_item(s, "02", 60, -6, 6, extra=[50, 40], table=6)
        seq_item(s, "03", 8, 8, 8, table=8)
        seq_item(s, "03", 8, 8, 6, extra=[18, 36], table=8)
        seq_item(s, "03", 9, 9, 8, table=9)
        seq_item(s, "03", 36, 9, 6, extra=[46, 64], table=9, script="D")
        seq_item(s, "03", 80, -8, 6, extra=[60, 42], table=8)
        for a, b in [(3, 7), (4, 6), (6, 8), (7, 9), (8, 4)]:
            sum_item(s, "04", a, "*", b, [a * b + a, a + b if a + b not in (a, b) else a * b - 1])
        for a, b in [(24, 4), (35, 7), (48, 6), (63, 9), (72, 8)]:
            c = a // b
            sum_item(s, "05", a, "/", b, [c + 1, c - 1 if c - 1 != b else c + 2])
    else:
        seq_item(s, "01", 1000, 1000, 8)
        seq_item(s, "01", 500, 500, 6, extra=[1250, 2750])
        seq_item(s, "01", 2000, 2000, 6, extra=[5000, 9000], script="D")
        seq_item(s, "01", 10000, -1000, 6, extra=[8500, 5500])
        seq_item(s, "01", 9997, 1, 6, extra=[9990, 10010])
        order_item(s, "02", [1200, 2100, 1020, 2010, 2001])
        order_item(s, "02", [9999, 10000, 9909, 10100, 9099])
        order_item(s, "02", [45000, 54000, 4500, 5400, 450])
        order_item(s, "02", [7080, 7800, 8070, 8700, 7008, 8007], up=False)
        order_item(s, "02", [1000000, 100000, 10000, 1000, 100, 10], up=False)

        def fracs(pairs):
            return {fr(k, n): (fa_frac(k, n), f"{k}/{n}") for k, n in pairs}

        same = tr("وقتی مخرج" + Z + "ها یکی است، کسری بزرگتر است که صورت آن بزرگتر است.",
                  "When the denominators are the same, the fraction with the bigger numerator is bigger.")
        unit = tr("وقتی صورت" + Z + "ها یکی است، کسری بزرگتر است که مخرج آن کوچکتر است.",
                  "When the numerators are the same, the fraction with the smaller denominator is bigger.")
        up_say = tr("این کسرها را از کوچک به بزرگ بچین.", "Arrange these fractions from small to big.")
        down_say = tr("این کسرها را از بزرگ به کوچک بچین.", "Arrange these fractions from big to small.")
        for pairs, up, help_fa in [([(1, 6), (2, 6), (4, 6), (5, 6)], True, same), ([(1, 8), (3, 8), (5, 8), (7, 8)], True, same),
                                   ([(1, 2), (1, 3), (1, 4), (1, 6), (1, 8)], True, unit), ([(1, 5), (2, 5), (3, 5), (4, 5)], False, same),
                                   ([(1, 2), (1, 3), (1, 5), (1, 10)], False, unit)]:
            sp = fracs(pairs)
            order_things(s, "03", I_ORDER_FRAC, list(sp), up, sp, up_say if up else down_say, help_fa)
        dec_help = tr("اول عدد پیش از نقطه را ببین، بعد رقم" + Z + "های بعد از نقطه را.", "First look at the number before the point, then at the digits after the point.")
        up_say = tr("این عددهای اعشاری را از کوچک به بزرگ بچین.", "Arrange these decimal numbers from small to big.")
        down_say = tr("این عددهای اعشاری را از بزرگ به کوچک بچین.", "Arrange these decimal numbers from big to small.")
        for decs, up in [(["0.1", "0.5", "0.9", "1.2", "1.5"], True), (["0.25", "0.50", "0.75", "1.25", "1.50"], True),
                         (["2.05", "2.50", "2.55", "5.20", "5.25"], True), (["0.2", "0.4", "0.6", "0.8", "1.2"], False),
                         (["3.10", "3.01", "1.30", "1.03", "0.31"], False)]:
            sp = {"t:" + d: (fa_dec(d), d) for d in decs}
            order_things(s, "04", I_ORDER_DEC, list(sp), up, sp, up_say if up else down_say, dec_help)
        for a, b, n in [(1, 2, 5), (2, 3, 7), (1, 4, 8), (3, 4, 9), (2, 5, 10)]:
            frac_sum_item(s, "05", a, b, n)
    return s


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


def sorter45(level: int) -> Sheet:
    s = Sheet(SORTER_COLS)

    def sums_round(rnd, op, groups, intro):
        rng = rng_for(level, "sorter", rnd)
        rows = [(a, b, res) for res, pairs in groups.items() for a, b in pairs]
        assert len(rows) == 8
        for a, b, res in spread_by(rows, rng):
            row = s.add(round=rnd, intro_fa=intro, thing=f"t:{a}{SIGN[op]}{b}", say_fa=tr(f"{fa(a)} {OP_WORD[op]} {fa(b)}", f"{a} {OP_EN[op]} {b}"),
                        basket=W(res), basket_say_fa=tr(fa(res), str(res)))
            SORT2_META.append((row, "sum"))

    def spread_by(rows, rng):
        rows = list(rows)
        rng.shuffle(rows)
        return rows

    def plain_round(rnd, intro, rows, kind):
        """rows: (thing, spoken Dari, English, basket thing, basket Dari, basket English)"""
        rng = rng_for(level, "sorter", rnd)
        assert len(rows) == 8
        for thing, say, en, basket, b_say, b_en in spread_by(rows, rng):
            row = s.add(round=rnd, intro_fa=intro, thing=thing, say_fa=tr(say, en), basket=basket, basket_say_fa=tr(b_say, b_en))
            SORT2_META.append((row, kind))

    if level == 4:
        # 01: the baskets are pictures (a written «یک بر سه» would be too small to read)
        rng = rng_for(4, "sorter", "01")
        pictures = {"whole": "shape_circle", "half": pie(1, 2), "third": pie(1, 3), "quarter": pie(1, 4)}
        rows = [(FRACTIONS[kind][i], kind) for kind in ("whole", "half", "third", "quarter") for i in ((0, 2) if kind == "whole" else (0, 3))]
        rng.shuffle(rows)
        for (pic, name), kind in rows:
            basket = FRAC_BASKET[kind]
            noun = FRACTION_NOUNS[FRACTIONS[kind].index((pic, name))]
            en = FRACTION_EN[kind].format(a=art(bare(noun)), x=bare(noun))
            row = s.add(round="01", intro_fa=I_FRACTION4, thing=pic, say_fa=tr(name, en), basket=pictures[kind], basket_say_fa=tr(basket[1], bare(basket[1])))
            SORT_META.append((row, "fraction", kind))
        sums_round("02", "*", {12: [(3, 4), (2, 6), (4, 3)], 18: [(3, 6), (2, 9), (6, 3)], 24: [(4, 6), (3, 8)]}, I_PRODUCT)
        sums_round("03", "*", {36: [(6, 6), (4, 9), (9, 4)], 40: [(5, 8), (4, 10), (8, 5)], 48: [(6, 8), (8, 6)]}, I_PRODUCT)
        sums_round("04", "/", {3: [(12, 4), (18, 6), (27, 9)], 4: [(12, 3), (20, 5), (32, 8)], 6: [(18, 3), (42, 7)]}, I_QUOTIENT)
    else:
        # The baskets carry one large word (کمتر، نیم، بیشتر); what they are compared with is spoken.
        tr("کمتر", "less"), tr("بیشتر", "more")
        less, same, more = ("f:کمتر", "کمتر از نیم", "less than half"), ("f:نیم", "مساوی نیم", "equal to half"), ("f:بیشتر", "بیشتر از نیم", "more than half")
        rows = []
        for k, n in [(1, 3), (1, 4), (2, 5), (2, 4), (3, 6), (2, 3), (3, 4), (4, 5)]:
            b = less if Fraction(k, n) < Fraction(1, 2) else same if Fraction(k, n) == Fraction(1, 2) else more
            rows.append((fr(k, n), fa_frac(k, n), f"{k}/{n}") + b)
        plain_round("01", I_HALF_SORT, rows, "half")
        rows = []
        for k, n in [(2, 4), (3, 6), (4, 8), (2, 6), (3, 9), (4, 12), (2, 8), (3, 12)]:
            v = Fraction(k, n)
            b = {Fraction(1, 2): (pie(1, 2), "نیم", "half"), Fraction(1, 3): (pie(1, 3), "یک بر سه", "1/3"), Fraction(1, 4): (pie(1, 4), "چارک", "quarter")}[v]
            rows.append((fr(k, n), fa_frac(k, n), f"{k}/{n}") + b)
        plain_round("02", I_SAME_FRAC, rows, "same")
        rows = []
        for pul in (50, 25, 75, 90, 150, 125, 250, 105):
            b = ("f:کمتر", "کمتر از یک " + AFN, "less than 1 afghani") if pul < 100 else ("f:بیشتر", "بیشتر از یک " + AFN, "more than 1 afghani")
            rows.append((money(pul), money_fa(pul), money_en(pul)) + b)
        plain_round("03", I_AFGHANI, rows, "afghani")
        rows = []
        for n in (4999, 5001, 4500, 5050, 999, 10000, 4950, 50000):
            b = ("f:کمتر", "کمتر از پنج هزار", "less than 5000") if n < 5000 else ("f:بیشتر", "بیشتر از پنج هزار", "more than 5000")
            rows.append((W(n), fa(n), str(n)) + b)
        plain_round("04", I_5000, rows, "5000")
    return s


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


def mason45(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    def q(rnd, intro, say, ans, prefer, help_fa, hi=100000, show="", script="W"):
        rng = rng_for(level, "mason", rnd, say, show)
        numq(s, rnd, intro, say, ans, prefer, help_fa, rng, hi, show=show, script=script)

    if level == 4:
        for k in (1, 2, 3, 5):
            q("01", I_WEIGHT, tr(f"{fa(k)} کیلو چند گرام است؟", f"How many grams is {nn(k, 'kilo')}?"), k * 1000, [k * 100, k * 10, k * 1000 + 1000],
              tr(f"هر کیلو هزار گرام است. {fa(k)} کیلو، {fa(k * 1000)} گرام می{Z}شود.", f"Each kilo is 1000 grams. {nn(k, 'kilo')} makes {k * 1000} grams."))
        q("01", I_WEIGHT, tr("نیم کیلو چند گرام است؟", "How many grams is half a kilo?"), 1000 // 2, [50, 250, 200],
          tr("یک کیلو هزار گرام است. نیم آن پنج" + Z + "صد گرام است.", "One kilo is 1000 grams. Half of it is 500 grams."))
        for g in (2000, 4000):
            q("01", I_WEIGHT, tr(f"{fa(g)} گرام چند کیلو است؟", f"How many kilos is {g} grams?"), g // 1000, [g // 100, g // 1000 + 1, g // 1000 - 1],
              tr(f"هر هزار گرام یک کیلو است. {fa(g)} گرام، {fa(g // 1000)} کیلو می{Z}شود.", f"Every 1000 grams is 1 kilo. {g} grams makes {nn(g // 1000, 'kilo')}."))
        q("01", I_WEIGHT, tr("یک و نیم کیلو چند گرام است؟", "How many grams is one and a half kilos?"), 1000 + 500, [150, 1050, 2500],
          tr("یک کیلو هزار گرام و نیم کیلو پنج" + Z + "صد گرام است. هزار جمع پنج" + Z + "صد مساوی یک هزار و پنج" + Z + "صد.",
             "One kilo is 1000 grams and half a kilo is 500 grams. 1000 plus 500 equals 1500."))

        for a, b in [(50, 25), (38, 14)]:
            q("02", I_WEIGHT2, tr(f"یک بوری آرد {fa(a)} کیلو است و یک بوری برنج {fa(b)} کیلو. هر دو با هم چند کیلو می{Z}شود؟",
                                  f"A sack of flour is {a} kilos and a sack of rice is {b} kilos. How many kilos do both make together?"),
              a + b, [a - b, a + b + 10, a + b - 10], tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}."))
        for k, m in [(6, 4), (8, 7)]:
            q("02", I_WEIGHT2, tr(f"هر تربوز {fa(m)} کیلو است. {fa(k)} تربوز چند کیلو می{Z}شود؟", f"Each watermelon is {m} kilos. How many kilos do {k} watermelons make?"),
              k * m, [k + m, (k + 1) * m, k * m - 1], tr(f"{fa(k)} ضرب {fa(m)} مساوی {fa(k * m)}.", f"{k} times {m} equals {k * m}."))
        for n, k in [(36, 4), (56, 8)]:
            q("02", I_WEIGHT2, tr(f"{fa(n)} کیلو برنج را بین {fa(k)} خانواده برابر تقسیم می{Z}کنیم. به هر خانواده چند کیلو می{Z}رسد؟",
                                  f"We share {n} kilos of rice equally among {k} families. How many kilos does each family get?"),
              n // k, [n // k + 1, n - k, k], tr(f"{fa(n)} تقسیم {fa(k)} مساوی {fa(n // k)}.", f"{n} divided by {k} equals {n // k}."))
        for a, b in [(50, 18), (42, 27)]:
            q("02", I_WEIGHT2, tr(f"در بوری {fa(a)} کیلو آرد بود. {fa(b)} کیلو مصرف شد. چند کیلو ماند؟", f"There were {a} kilos of flour in the sack. {b} kilos were used. How many kilos are left?"),
              a - b, [a - b + 10, a + b, a - b - 1], tr(f"{fa(a)} منفی {fa(b)} مساوی {fa(a - b)}.", f"{a} minus {b} equals {a - b}."))

        for a, b in [(12, 8), (25, 15)]:
            q("03", I_LITRE, tr(f"در یک تانکی {fa(a)} لیتر آب است. {fa(b)} لیتر دیگر در آن می{Z}ریزیم. چند لیتر می{Z}شود؟",
                                f"There are {a} litres of water in a tank. We pour {b} litres more into it. How many litres does it make?"),
              a + b, [a - b, a + b + 10, a + b - 1], tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.", f"{a} plus {b} equals {a + b}."))
        for k, m in [(7, 10), (6, 8)]:
            q("03", I_LITRE, tr(f"هر سطل {fa(m)} لیتر آب می{Z}گیرد. {fa(k)} سطل چند لیتر می{Z}شود؟", f"Each bucket holds {m} litres of water. How many litres do {k} buckets make?"),
              k * m, [k + m, (k + 1) * m, k * m - 1], tr(f"{fa(k)} ضرب {fa(m)} مساوی {fa(k * m)}.", f"{k} times {m} equals {k * m}."))
        for n, m in [(18, 2), (40, 5)]:
            q("03", I_LITRE, tr(f"{fa(n)} لیتر شیر را در ظرف{Z}های {fa(m)} لیتره می{Z}ریزیم. چند ظرف پُر می{Z}شود؟",
                                f"We pour {n} litres of milk into {m}-litre pots. How many pots are filled?"),
              n // m, [n // m + 1, n - m, n // m - 1], tr(f"{fa(n)} تقسیم {fa(m)} مساوی {fa(n // m)}.", f"{n} divided by {m} equals {n // m}."))
        q("03", I_LITRE, tr("در تانکی شصت لیتر آب بود. بیست و پنج لیتر مصرف شد. چند لیتر ماند؟", "There were 60 litres of water in the tank. 25 litres were used. How many litres are left?"),
          60 - 25, [45, 85, 25], tr(f"شصت منفی بیست و پنج مساوی {fa(35)}.", "60 minus 25 equals 35."))
        q("03", I_LITRE, tr("هر ظرف نیم لیتر شیر می" + Z + "گیرد. شش لیتر شیر چند ظرف را پُر می" + Z + "کند؟",
                            "Each pot holds half a litre of milk. How many pots do 6 litres of milk fill?"),
          6 * 2, [3, 6, 8], tr("هر لیتر دو ظرف را پُر می" + Z + "کند. شش ضرب دو مساوی دوازده.", "Each litre fills 2 pots. 6 times 2 equals 12."))

        for a in (5, 7, 9):
            q("04", I_PERIMETER, tr(f"هر ضلع یک مربع {fa(a)} {M} است. محیط آن چند {M} است؟", f"Each side of a square is {nn(a, 'metre')}. How many metres is its perimeter?"),
              4 * a, [2 * a, a * a, 3 * a], tr(f"مربع چهار ضلع برابر دارد. چهار ضرب {fa(a)} مساوی {fa(4 * a)}.", f"A square has 4 equal sides. 4 times {a} equals {4 * a}."), show="shape_square")
        for a, b in [(8, 3), (10, 6), (12, 5)]:
            q("04", I_PERIMETER, tr(f"طول یک مستطیل {fa(a)} {M} و عرض آن {fa(b)} {M} است. محیط آن چند {M} است؟",
                                    f"The length of a rectangle is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many metres is its perimeter?"),
              2 * (a + b), [a + b, a * b, 2 * a + b],
              tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}. دو طول و دو عرض است: دو ضرب {fa(a + b)} مساوی {fa(2 * (a + b))}.",
                 f"{a} plus {b} equals {a + b}. There are two lengths and two widths: 2 times {a + b} equals {2 * (a + b)}."), show="shape_rectangle")
        for a in (6, 20):
            q("04", I_PERIMETER, tr(f"هر سه ضلع یک مثلث {fa(a)} {CM} است. محیط آن چند {CM} است؟", f"All three sides of a triangle are {a} centimetres. How many centimetres is its perimeter?"),
              3 * a, [2 * a, 4 * a, a + 3], tr(f"سه ضرب {fa(a)} مساوی {fa(3 * a)}.", f"3 times {a} equals {3 * a}."), show="shape_triangle")

        for p in (36, 20):
            q("05", I_PERIMETER2, tr(f"دور یک حویلی مربع {fa(p)} {M} است. هر ضلع آن چند {M} است؟", f"The way around a square yard is {p} metres. How many metres is each side?"),
              p // 4, [p // 2, p - 4, p // 4 + 1], tr(f"مربع چهار ضلع برابر دارد. {fa(p)} تقسیم چهار مساوی {fa(p // 4)}.", f"A square has 4 equal sides. {p} divided by 4 equals {p // 4}."), show="shape_square")
        for (noun, en), a, b in [(("باغچه", "garden"), 9, 4), (("قالین", "carpet"), 3, 2), (("صنف", "classroom"), 8, 6)]:
            q("05", I_PERIMETER2, tr(f"طول یک {noun} {fa(a)} {M} و عرض آن {fa(b)} {M} است. دور آن چند {M} است؟",
                                     f"The length of a {en} is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many metres is the way around it?"),
              2 * (a + b), [a + b, a * b, 2 * a + b],
              tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}. دو طول و دو عرض است: دو ضرب {fa(a + b)} مساوی {fa(2 * (a + b))}.",
                 f"{a} plus {b} equals {a + b}. There are two lengths and two widths: 2 times {a + b} equals {2 * (a + b)}."), show="shape_rectangle")
        q("05", I_PERIMETER2, tr("محیط یک مثلث بیست و هفت " + CM + " است و هر سه ضلع آن برابر است. هر ضلع چند " + CM + " است؟",
                                 "The perimeter of a triangle is 27 centimetres and all three sides are equal. How many centimetres is each side?"),
          27 // 3, [24, 8, 10], tr("بیست و هفت تقسیم سه مساوی نه.", "27 divided by 3 equals 9."), show="shape_triangle")
        for a, b, c in [(3, 4, 5), (6, 8, 10)]:
            q("05", I_PERIMETER2, tr(f"ضلع{Z}های یک مثلث {fa(a)}، {fa(b)} و {fa(c)} {CM} است. محیط آن چند {CM} است؟",
                                     f"The sides of a triangle are {a}, {b} and {c} centimetres. How many centimetres is its perimeter?"),
              a + b + c, [a + b, a + b + c + 1, a + b + c - 2], tr(f"{fa(a)} جمع {fa(b)} جمع {fa(c)} مساوی {fa(a + b + c)}.", f"{a} plus {b} plus {c} equals {a + b + c}."),
              show="shape_triangle")
    else:
        # 01: the picture lays the squares out in full rows (2x2, 3x2, 3x3, 4x3, 4x4, 5x4)
        for i, (cols, rows) in enumerate([(2, 2), (3, 2), (3, 3), (4, 3), (4, 4), (5, 4)]):
            n = cols * rows
            q("01", I_AREA_COUNT, tr(f"هر مربع یک {SQM} است. مساحت این فرش چند {SQM} است؟", "Each square is 1 square metre. How many square metres is the area of this floor?"),
              n, [2 * (cols + rows), n + 1, n - 1, cols + rows],
              tr(f"{fa(rows)} قطار است و در هر قطار {fa(cols)} مربع. {fa(rows)} ضرب {fa(cols)} مساوی {fa(n)}.",
                 f"There are {nn(rows, 'row')} with {nn(cols, 'square')} in each. {rows} times {cols} equals {n}."),
              show=f"p:shape_square*{n}", script="D" if i % 2 else "W")
        for (noun, en), a, b in [(("اتاق", "room"), 5, 4), (("قالین", "carpet"), 3, 2), (("حویلی", "yard"), 12, 8), (("صنف", "classroom"), 8, 6),
                                 (("باغچه", "garden"), 9, 7), (("زمین", "field"), 30, 20), (("میدان", "playground"), 40, 25), (("اتاق", "room"), 7, 4)]:
            q("02", I_AREA, tr(f"طول یک {noun} {fa(a)} {M} و عرض آن {fa(b)} {M} است. مساحت آن چند {SQM} است؟",
                               f"The length of a {en} is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many square metres is its area?"),
              a * b, [2 * (a + b), a + b, a * (b + 1)], tr(f"مساحت، طول ضرب عرض است. {fa(a)} ضرب {fa(b)} مساوی {fa(a * b)}.", f"The area is length times width. {a} times {b} equals {a * b}."),
              show="shape_rectangle")
        for a in (3, 6, 9, 20):
            q("03", I_AREA2, tr(f"هر ضلع یک مربع {fa(a)} {M} است. مساحت آن چند {SQM} است؟", f"Each side of a square is {nn(a, 'metre')}. How many square metres is its area?"),
              a * a, [4 * a, 2 * a, a * a + a], tr(f"{fa(a)} ضرب {fa(a)} مساوی {fa(a * a)}.", f"{a} times {a} equals {a * a}."), show="shape_square")
        for area, a in [(24, 6), (45, 9), (56, 7), (120, 10)]:
            q("03", I_AREA2, tr(f"مساحت یک مستطیل {fa(area)} {SQM} و طول آن {fa(a)} {M} است. عرض آن چند {M} است؟",
                                f"The area of a rectangle is {area} square metres and its length is {nn(a, 'metre')}. How many metres is its width?"),
              area // a, [area - a, area // a + 1, area // a - 1], tr(f"{fa(area)} تقسیم {fa(a)} مساوی {fa(area // a)}.", f"{area} divided by {a} equals {area // a}."),
              show="shape_rectangle")
        for a, b in [(7, 3), (10, 4), (9, 5), (12, 6)]:
            q("04", I_AREA_OR, tr(f"طول یک مستطیل {fa(a)} {M} و عرض آن {fa(b)} {M} است. محیط آن چند {M} است؟",
                                  f"The length of a rectangle is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many metres is its perimeter?"),
              2 * (a + b), [a * b, a + b, 2 * a + b],
              tr(f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}. دو طول و دو عرض است: دو ضرب {fa(a + b)} مساوی {fa(2 * (a + b))}.",
                 f"{a} plus {b} equals {a + b}. There are two lengths and two widths: 2 times {a + b} equals {2 * (a + b)}."), show="shape_rectangle")
            q("04", I_AREA_OR, tr(f"طول یک مستطیل {fa(a)} {M} و عرض آن {fa(b)} {M} است. مساحت آن چند {SQM} است؟",
                                  f"The length of a rectangle is {nn(a, 'metre')} and its width is {nn(b, 'metre')}. How many square metres is its area?"),
              a * b, [2 * (a + b), a + b, a * (b + 1)], tr(f"مساحت، طول ضرب عرض است. {fa(a)} ضرب {fa(b)} مساوی {fa(a * b)}.", f"The area is length times width. {a} times {b} equals {a * b}."),
              show="shape_rectangle")
    return s


# ---------------------------------------------------------------------------
# Levels 4 and 5: Twin Tiles (pairs)
# ---------------------------------------------------------------------------

I_PAIR_MUL = tr("هر ضرب را با جواب آن جوره کن.", "Pair each multiplication with its answer.")
I_PAIR_DIV = tr("هر تقسیم را با جواب آن جوره کن.", "Pair each division with its answer.")
I_PAIR_PIE = tr("نام را گوش کن و با شکل آن جوره کن.", "Listen to the name and pair it with its picture.")
I_PAIR_SAME = tr("کسرهای مساوی را جوره کن.", "Pair the fractions that are equal.")
I_PAIR_FRAC = tr("هر شکل را با کسر آن جوره کن.", "Pair each picture with its fraction.")
I_PAIR_DEC = tr("هر عدد اعشاری را با کسر مساوی آن جوره کن.", "Pair each decimal number with the fraction equal to it.")


def pairs45(level: int) -> Sheet:
    s = Sheet(PAIRS_COLS)

    def pair(rnd, intro, a, b, say, kind):
        row = s.add(round=rnd, intro_fa=intro, a=a, b=b, say_fa=say)
        PAIR_META.append((row, kind))

    def sums(rnd, intro, op, tables):
        """Six different sums with six different answers."""
        rng = rng_for(level, "pairs", rnd)
        for _ in range(1000):
            picks = [(rng.randint(2, 10), t) if op == "*" else (t * rng.randint(2, 10), t) for t in rng.sample(tables * 2, 6)]
            answers = [a * b if op == "*" else a // b for a, b in picks]
            if len(set(answers)) == 6 and len(set(picks)) == 6 and len({tuple(sorted(p)) for p in picks}) == 6:
                break
        else:
            raise AssertionError(rnd)
        for (a, b), c in zip(picks, answers):
            pair(rnd, intro, f"t:{a}{SIGN[op]}{b}", W(c), tr(f"{fa(a)} {OP_WORD[op]} {fa(b)} مساوی {fa(c)}.", f"{a} {OP_EN[op]} {b} equals {c}."), "sum")

    if level == 4:
        sums("01", I_PAIR_MUL, "*", [3, 4, 6])
        sums("02", I_PAIR_MUL, "*", [7, 8, 9])
        sums("03", I_PAIR_DIV, "/", [3, 4, 6, 7, 8, 9])
        for (k, n), name, en in PIES4:
            pair("04", I_PAIR_PIE, pie(k, n), "snd", tr(name, en), "name")
        pair("04", I_PAIR_PIE, "shape_circle", "snd", tr(WHOLE[1], bare(WHOLE[1])), "name")
    else:
        for (k, n), m in [((1, 2), 2), ((1, 3), 2), ((1, 4), 2), ((2, 3), 2), ((3, 4), 2), ((1, 5), 2)]:
            pair("01", I_PAIR_SAME, fr(k, n), fr(k * m, n * m), tr(f"{fa_frac(k, n)} مساوی {fa_frac(k * m, n * m)}.", f"{k}/{n} equals {k * m}/{n * m}."), "same")
        for k, n in [(1, 2), (2, 3), (3, 4), (2, 5), (5, 6), (3, 8)]:
            pair("02", I_PAIR_FRAC, pie(k, n), fr(k, n), tr(fa_frac(k, n), f"{k}/{n}"), "same")
        for d, (k, n) in [("0.5", (1, 2)), ("0.25", (1, 4)), ("0.75", (3, 4)), ("0.1", (1, 10)), ("0.2", (1, 5)), ("0.3", (3, 10))]:
            pair("03", I_PAIR_DEC, "t:" + d, fr(k, n), tr(f"{fa_dec(d)} مساوی {fa_frac(k, n)}.", f"{d} equals {k}/{n}."), "same")
    return s


# ---------------------------------------------------------------------------
# Levels 4 and 5: Number Rain (catch)
# ---------------------------------------------------------------------------

I_RAIN = tr("گوش کن و فقط عددهای درست را بگیر.", "Listen and catch only the right numbers.")


def catch45(level: int) -> Sheet:
    s = Sheet(CATCH_COLS)

    def rule(rnd, say, targets, others, help_fa, test):
        assert len(targets) >= 5 and len(others) >= 5 and not set(targets) & set(others)
        assert all(len(x) - 2 <= 4 for x in targets + others), "too wide for the round card"
        assert len(set(targets)) == len(targets) and len(set(others)) == len(others)
        row = s.add(round=rnd, intro_fa=I_RAIN, say_fa=say, targets="|".join(targets), others="|".join(others), need=5, help_fa=help_fa)
        CATCH_META.append((row, test))

    def table_rule(rnd, t, script):
        rng = rng_for(level, "catch", rnd, t, script)
        inside = rng.sample(range(2, 11), 6)
        outside = rng.sample([x for x in range(t + 1, 10 * t) if x % t], 6)
        rule(rnd, tr(f"عددهای جدول ضرب {fa(t)} را بگیر.", f"Catch the numbers of the {t} times table."),
             [num(t * i, script) for i in inside], [num(x, script) for x in outside],
             tr(f"جدول ضرب {fa(t)}: " + "، ".join(fa(t * i) for i in range(1, 6)) + " و همین طور پیش برو.",
                f"The {t} times table: " + ", ".join(str(t * i) for i in range(1, 6)) + " and so on."),
             lambda v, t=t: v % t == 0)

    if level == 4:
        for t, script in [(3, "W"), (4, "W"), (6, "W"), (2, "D"), (5, "D"), (10, "D")]:
            table_rule("01", t, script)
        for t, script in [(7, "W"), (8, "W"), (9, "W"), (3, "D"), (4, "D"), (6, "D")]:
            table_rule("02", t, script)
    else:
        def nums(values, script="W"):
            return [num(v, script) for v in values]

        # Numbers of at most three digits: a longer one would be too small on the round card.
        rule("01", tr("عددهایی را بگیر که بر ده تقسیم می" + Z + "شوند.", "Catch the numbers that can be divided by 10."),
             nums([120, 450, 90, 700, 230, 860]), nums([125, 451, 99, 705, 236, 864]),
             tr("عددی بر ده تقسیم می" + Z + "شود که رقم آخر آن صفر است.", "A number can be divided by 10 when its last digit is 0."), lambda v: v % 10 == 0)
        rule("01", tr("عددهایی را بگیر که بر صد تقسیم می" + Z + "شوند.", "Catch the numbers that can be divided by 100."),
             nums([300, 900, 500, 200, 700, 400]), nums([350, 910, 505, 290, 710, 440]),
             tr("عددی بر صد تقسیم می" + Z + "شود که دو رقم آخر آن صفر است.", "A number can be divided by 100 when its last two digits are 0."), lambda v: v % 100 == 0)
        rule("01", tr("عددهای جدول ضرب دوازده را بگیر.", "Catch the numbers of the 12 times table."),
             nums([36, 60, 84, 96, 108, 48]), nums([34, 62, 86, 94, 106, 46]),
             tr("جدول ضرب دوازده: دوازده، بیست و چهار، سی و شش، چهل و هشت، شصت و همین طور پیش برو.", "The 12 times table: 12, 24, 36, 48, 60 and so on."),
             lambda v: v % 12 == 0)
        rule("01", tr("عددهای جدول ضرب بیست و پنج را بگیر.", "Catch the numbers of the 25 times table."),
             nums([75, 125, 150, 225, 250, 175]), nums([85, 120, 155, 230, 245, 170]),
             tr("جدول ضرب بیست و پنج: بیست و پنج، پنجاه، هفتاد و پنج، صد، یکصد و بیست و پنج و همین طور پیش برو.", "The 25 times table: 25, 50, 75, 100, 125 and so on."),
             lambda v: v % 25 == 0)
        rule("01", tr("عددهای بزرگتر از پنج" + Z + "صد را بگیر.", "Catch the numbers bigger than 500."),
             nums([501, 550, 900, 750, 999, 625], "D"), nums([499, 50, 450, 99, 105, 275], "D"),
             tr("اول صدها را ببین.", "Look at the hundreds first."), lambda v: v > 500)
        rule("01", tr("عددهایی را بگیر که بر پنج تقسیم می" + Z + "شوند.", "Catch the numbers that can be divided by 5."),
             nums([105, 250, 435, 90, 605, 770], "D"), nums([102, 251, 434, 99, 606, 772], "D"),
             tr("عددی بر پنج تقسیم می" + Z + "شود که رقم آخر آن صفر یا پنج است.", "A number can be divided by 5 when its last digit is 0 or 5."), lambda v: v % 5 == 0)

        def fracs(pairs):
            return [fr(k, n) for k, n in pairs]

        half = Fraction(1, 2)
        rule("02", tr("کسرهای مساوی نیم را بگیر.", "Catch the fractions equal to half."),
             fracs([(2, 4), (3, 6), (4, 8), (5, 10), (6, 12)]), fracs([(1, 3), (2, 5), (3, 4), (2, 3), (1, 4), (4, 6)]),
             tr("کسری مساوی نیم است که صورت آن نیم مخرج باشد.", "A fraction is equal to half when its numerator is half of its denominator."), lambda v: v == half)
        rule("02", tr("کسرهای بزرگتر از نیم را بگیر.", "Catch the fractions bigger than half."),
             fracs([(2, 3), (3, 4), (4, 5), (5, 6), (7, 8), (3, 5)]), fracs([(1, 3), (1, 4), (2, 5), (1, 5), (3, 8), (1, 6)]),
             tr("کسری از نیم بزرگتر است که صورت آن از نیم مخرج بیشتر باشد.", "A fraction is bigger than half when its numerator is more than half of its denominator."), lambda v: v > half)
        rule("02", tr("کسرهای کوچکتر از نیم را بگیر.", "Catch the fractions smaller than half."),
             fracs([(1, 3), (1, 4), (2, 5), (1, 8), (3, 8), (2, 6)]), fracs([(2, 3), (3, 4), (3, 5), (5, 6), (5, 8), (4, 6)]),
             tr("کسری از نیم کوچکتر است که صورت آن از نیم مخرج کمتر باشد.", "A fraction is smaller than half when its numerator is less than half of its denominator."), lambda v: v < half)
        rule("02", tr("کسرهای مساوی یک پوره را بگیر.", "Catch the fractions equal to one whole."),
             fracs([(2, 2), (3, 3), (4, 4), (5, 5), (8, 8)]), fracs([(1, 2), (2, 3), (3, 4), (4, 5), (7, 8), (1, 8)]),
             tr("وقتی صورت و مخرج یکی است، کسر یک پوره است.", "When the numerator and the denominator are the same, the fraction is one whole."), lambda v: v == 1)
        rule("02", tr("عددهای اعشاری بزرگتر از یک را بگیر.", "Catch the decimal numbers bigger than 1."),
             ["t:1.5", "t:1.25", "t:2.5", "t:1.05", "t:3.75", "t:1.1"], ["t:0.5", "t:0.25", "t:0.75", "t:0.9", "t:0.05", "t:0.1"],
             tr("عدد پیش از نقطه را ببین.", "Look at the number before the point."), lambda v: v > 1)
        rule("02", tr("عددهای اعشاری کوچکتر از یک را بگیر.", "Catch the decimal numbers smaller than 1."),
             ["t:0.5", "t:0.25", "t:0.75", "t:0.99", "t:0.05", "t:0.1"], ["t:1.5", "t:1.25", "t:2.5", "t:1.01", "t:9.9", "t:1.1"],
             tr("عدد پیش از نقطه را ببین.", "Look at the number before the point."), lambda v: v < 1)
    return s


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

    rng = rng_for(4, "calendar", "01")
    after = rng.sample(range(7), 3)
    for i in after:
        (d, en), (n, n_en) = day(i), day(i + 1)
        ask("01", I_DAYS, tr(f"بعد از {d} کدام روز می{Z}آید؟", f"Which day comes after {en}?"), day(i + 1), [day(i), day(i - 1), day(i + 2)],
            tr(f"بعد از {d}، {n} می{Z}آید.", f"After {en} comes {n_en}."))
    i = rng.choice([x for x in range(1, 7) if x not in after])
    (d, en), (n, n_en) = day(i), day(i - 1)
    ask("01", I_DAYS, tr(f"پیش از {d} کدام روز است؟", f"Which day is before {en}?"), day(i - 1), [day(i), day(i + 1), day(i - 2)],
        tr(f"پیش از {d}، {n} است.", f"Before {en} is {n_en}."))
    week = tr("هفته با شنبه شروع می" + Z + "شود و با جمعه تمام می" + Z + "شود.", "The week starts with Saturday and ends with Friday.")
    ask("01", I_DAYS, tr("هفته با کدام روز شروع می" + Z + "شود؟", "With which day does the week start?"), day(0), [day(1), day(2), day(6)], week)
    ask("01", I_DAYS, tr("روز آخر هفته کدام است؟", "Which is the last day of the week?"), day(6), [day(0), day(5), day(4)], week)
    i = rng.choice([1, 2, 3, 4])
    (d, en), (n, n_en) = day(i), day(i + 1)
    ask("01", I_DAYS, tr(f"امروز {d} است. فردا کدام روز است؟", f"Today is {en}. Which day is tomorrow?"), day(i + 1), [day(i), day(i - 1), day(i + 2)],
        tr(f"فردا {n} است.", f"Tomorrow is {n_en}."))
    i = rng.choice([2, 3, 4, 5])
    (d, en), (n, n_en) = day(i), day(i - 1)
    ask("01", I_DAYS, tr(f"امروز {d} است. دیروز کدام روز بود؟", f"Today is {en}. Which day was yesterday?"), day(i - 1), [day(i), day(i + 1), day(i - 2)],
        tr(f"دیروز {n} بود.", f"Yesterday was {n_en}."))

    rng = rng_for(4, "calendar", "02")
    after = rng.sample(range(11), 3)
    for i in after:
        (m, en), (n, n_en) = month(i), month(i + 1)
        ask("02", I_MONTHS, tr(f"بعد از ماه {m} کدام ماه می{Z}آید؟", f"Which month comes after {en}?"), month(i + 1), [month(i), month(i - 1), month(i + 2)],
            tr(f"بعد از {m}، ماه {n} می{Z}آید.", f"After {en} comes {n_en}."))
    i = rng.choice([x for x in range(2, 12) if x not in after])
    (m, en), (n, n_en) = month(i), month(i - 1)
    ask("02", I_MONTHS, tr(f"پیش از ماه {m} کدام ماه است؟", f"Which month is before {en}?"), month(i - 1), [month(i), month(i + 1), month(i - 2)],
        tr(f"پیش از {m}، ماه {n} است.", f"Before {en} is {n_en}."))
    year = tr("سال با ماه حمل شروع می" + Z + "شود و با ماه حوت تمام می" + Z + "شود.", "The year starts with the month of Hamal and ends with the month of Hut.")
    ask("02", I_MONTHS, tr("ماه اول سال کدام است؟", "Which is the first month of the year?"), month(0), [month(1), month(11), month(6)], year)
    ask("02", I_MONTHS, tr("ماه آخر سال کدام است؟", "Which is the last month of the year?"), month(11), [month(0), month(10), month(5)], year)
    for i in rng.sample(range(12), 2):
        (m, en), season = month(i), SEASONS[i // 3]
        ask("02", I_MONTHS, tr(f"ماه {m} در کدام فصل است؟", f"In which season is the month of {en}?"), season, [x for x in SEASONS if x != season],
            tr(f"ماه {m} در فصل {season[0]} است.", f"The month of {en} is in {season[1]}."))

    def count(say, ans, wrong, help_fa):
        row = lp(s, "03", I_CALENDAR, say, W(ans), [W(x) for x in wrong], help_fa=help_fa)
        CHECK_META.append((row, Fraction(ans)))

    count(tr("یک هفته چند روز دارد؟", "How many days does a week have?"), 7, [6, 5, 10], tr("یک هفته هفت روز دارد.", "A week has 7 days."))
    count(tr("یک سال چند ماه دارد؟", "How many months does a year have?"), 12, [10, 7, 24], tr("یک سال دوازده ماه دارد.", "A year has 12 months."))
    count(tr("یک سال چند فصل دارد؟", "How many seasons does a year have?"), 4, [3, 12, 7], tr("یک سال چهار فصل دارد.", "A year has 4 seasons."))
    count(tr("هر فصل چند ماه دارد؟", "How many months does each season have?"), 3, [4, 12, 2], tr("هر فصل سه ماه دارد.", "Each season has 3 months."))
    count(tr("دو هفته چند روز می" + Z + "شود؟", "How many days do 2 weeks make?"), 2 * 7, [12, 7, 10], tr("هفت جمع هفت مساوی چهارده.", "7 plus 7 equals 14."))
    count(tr("یک شبانه" + Z + "روز چند ساعت دارد؟", "How many hours do a day and a night have?"), 24, [12, 60, 20], tr("یک شبانه" + Z + "روز بیست و چهار ساعت دارد.", "A day and a night have 24 hours."))
    ask("03", I_CALENDAR, tr("بعد از بهار کدام فصل می" + Z + "آید؟", "Which season comes after spring?"), SEASONS[1], [SEASONS[0], SEASONS[2], SEASONS[3]],
        tr("بعد از بهار، تابستان می" + Z + "آید.", "After spring comes summer."))
    ask("03", I_CALENDAR, tr("پیش از زمستان کدام فصل است؟", "Which season is before winter?"), SEASONS[2], [SEASONS[0], SEASONS[1], SEASONS[3]],
        tr("پیش از زمستان، خزان است.", "Before winter is autumn."))
    return s


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


def charts5(level: int) -> Sheet:
    s = Sheet(LP_COLS)
    for r, (name, rows) in enumerate(CHARTS.items()):
        rnd = f"{r + 1:02d}"
        bars = "bars" in name
        intro, kw, ke = (I_CHART, "گراف", "chart") if bars else (I_TABLE, "جدول", "table")
        rng = rng_for(5, "charts", rnd)
        values = [v for _, _, v in rows]
        assert len(rows) == 3 and len(set(values)) == 3 and all(1 <= v <= 5 for v in values)
        by_count = sorted(rows, key=lambda x: x[2])

        def which(say, row_, help_fa):
            # The fourth choice is a thing that is not in the chart: the builder
            # always deals four choices, and it must not pick one by chance.
            pic = row_[0]
            row = lp(s, rnd, intro, say, pic, [p for p, _, _ in rows if p != pic] + [CHART_EXTRA[name]], show=name, help_fa=help_fa)
            CAL_META.append((row, pic))

        def number(say, ans, prefer, help_fa):
            numq(s, rnd, intro, say, ans, prefer, help_fa, rng, 20, show=name)

        pic, noun, v = by_count[-1]
        which(tr(f"در این {kw} کدام از همه بیشتر است؟", f"In this {ke}, which one is the most?"), by_count[-1],
              tr(f"{noun} از همه بیشتر است: {fa(v)} تا.", f"The {bare(noun)} is the most: {v}."))
        a, b = rows[0], rows[2]
        for pic, noun, v in (a, b):
            number(tr(f"در این {kw} چند {noun} است؟", f"In this {ke}, how many {many(noun)} are there?"), v, [x for x in values if x != v],
                   tr(f"خانه{Z}های {noun} را بشمار: {fa(v)}.", f"Count the boxes of the {bare(noun)}: {v}."))
        # "Which one is the fewest?" is not asked: the thing that is not in the chart could be meant.
        pic, noun, v = by_count[0]
        which(tr(f"در این {kw} از کدام چیز {fa(v)} تا است؟", f"In this {ke}, of which thing {'is' if v == 1 else 'are'} there {v}?"), by_count[0],
              tr(f"{fa(v)} {noun} است.", f"{there(v, noun)}."))
        (_, n1, v1), (_, n2, v2) = rows[1], rows[2]
        number(tr(f"در این {kw}، {n1} و {n2} با هم چند تا است؟", f"In this {ke}, how many are the {many(n1)} and the {many(n2)} together?"), v1 + v2,
               [max(v1, v2), abs(v1 - v2), v1 + v2 + 1], tr(f"{fa(v1)} جمع {fa(v2)} مساوی {fa(v1 + v2)}.", f"{v1} plus {v2} equals {v1 + v2}."))
        (_, n1, v1), (_, n2, v2) = by_count[-1], by_count[rng.choice([0, 1])]
        number(tr(f"در این {kw}، {n1} چند تا بیشتر از {n2} است؟", f"In this {ke}, how many more {many(n1)} than {many(n2)} are there?"), v1 - v2,
               [v1, v1 + v2, v1 - v2 + 1], tr(f"{fa(v1)} منفی {fa(v2)} مساوی {fa(v1 - v2)}.", f"{v1} minus {v2} equals {v1 - v2}."))
        total = sum(values)
        number(tr(f"در این {kw} همه با هم چند تا است؟", f"In this {ke}, how many are there altogether?"), total, [total - 1, total + 1, max(values)],
               tr(" جمع ".join(fa(v) for v in values) + f" مساوی {fa(total)}.", " plus ".join(str(v) for v in values) + f" equals {total}."))
    for row, what in CAL_META:
        if row["show"] in CHARTS:  # most and fewest once more, from the chart's own numbers
            counts = {p: v for p, _, v in CHARTS[row["show"]]}
            pick = max if "بیشتر" in row["say_fa"] else min
            assert row["answer"] == pick(counts, key=counts.get), row
            assert set(row["distractors"].split("|")) == (set(counts) - {row["answer"]}) | {CHART_EXTRA[row["show"]]}, row
            assert "بیشتر" in row["say_fa"] or fa(counts[row["answer"]]) + " تا" in row["say_fa"], row
    return s


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


def fractions5(level: int) -> Sheet:
    s = Sheet(LP_COLS)

    def add(rnd, intro, say, answer, wrong, help_fa, show=""):
        row = lp(s, rnd, intro, say, answer, wrong, show=show, help_fa=help_fa)
        CHECK_META.append((row, val(answer)))
        return row

    rng = rng_for(5, "fractions", "01")
    picks = rng.sample(PIES5, 8)
    for k, n in picks:
        cands = [fr(n - k, n), fr(k, n + 1), fr(k + 1, n) if k + 1 < n else fr(k, n + 2), fr(n, k) if k > 1 else fr(k + 1, n + 1),
                 fr(k, n - 1) if n - 1 > k else fr(k + 2, n + 2)]
        wrong = pick_wrong(fr(k, n), cands)
        add("01", I_FRAC_NAME, tr("چند حصه رنگ شده است؟ کسر درست را انتخاب کن.", "How many parts are coloured? Choose the right fraction."), fr(k, n), wrong,
            tr(f"{fa(n)} حصه برابر است و {fa(k)} حصه رنگ شده است: {fa_frac(k, n)}.",
               f"There are {n} equal parts and {k} {'is' if k == 1 else 'are'} coloured: {k}/{n}."), show=pie(k, n))
    rng = rng_for(5, "fractions", "02")
    rest = [p for p in PIES5 if p not in picks]
    for k, n in rest + rng.sample(picks, 8 - len(rest)):
        others = [p for p in PIES5 if Fraction(*p) != Fraction(k, n)]
        close = [p for p in others if p[1] == n] + [p for p in others if p[0] == k and p[1] != n]
        rng.shuffle(close)
        rng.shuffle(others)
        wrong = pick_wrong(pie(k, n), [pie(*p) for p in close + others])
        add("02", I_FRAC_PIC, tr(f"کدام شکل {fa_frac(k, n)} را نشان می{Z}دهد؟", f"Which picture shows {k}/{n}?"), pie(k, n), wrong,
            tr(f"{fa_frac(k, n)} یعنی {fa(k)} حصه از {fa(n)} حصه برابر.", f"{k}/{n} means {k} of {n} equal parts."))

    same = "مخرج" + Z + "ها یکی است. کسری که صورت بزرگتر دارد، بزرگتر است."
    same_en = "The denominators are the same. The fraction with the bigger numerator is bigger."
    unit = "صورت" + Z + "ها یکی است. هر قدر مخرج کوچکتر باشد، حصه بزرگتر است."
    unit_en = "The numerators are the same. The smaller the denominator, the bigger the part."
    for group, biggest, why, why_en in [
            ([(1, 8), (3, 8), (5, 8), (7, 8)], True, same, same_en), ([(1, 6), (2, 6), (4, 6), (5, 6)], False, same, same_en),
            ([(1, 2), (1, 3), (1, 5), (1, 8)], True, unit, unit_en), ([(1, 3), (1, 4), (1, 6), (1, 10)], False, unit, unit_en),
            ([(3, 10), (7, 10), (9, 10), (1, 10)], True, same, same_en), ([(2, 5), (3, 5), (4, 5), (1, 5)], False, same, same_en),
            ([(1, 4), (1, 5), (1, 6), (1, 9)], True, unit, unit_en), ([(2, 3), (2, 5), (2, 7), (2, 9)], False, unit, unit_en)]:
        ans = max(group, key=lambda p: Fraction(*p)) if biggest else min(group, key=lambda p: Fraction(*p))
        say = tr("کدام کسر از همه بزرگتر است؟", "Which fraction is the biggest?") if biggest else tr("کدام کسر از همه کوچکتر است؟", "Which fraction is the smallest?")
        tail = tr(f"{fa_frac(*ans)} از همه بزرگتر است.", f"{ans[0]}/{ans[1]} is the biggest.") if biggest else tr(f"{fa_frac(*ans)} از همه کوچکتر است.", f"{ans[0]}/{ans[1]} is the smallest.")
        row = add("03", I_FRAC_CMP, say, fr(*ans), [fr(*p) for p in group if p != ans], tr(why + " " + tail, why_en + " " + EN[tail]))
        got, rest_v = val(row["answer"]), [val(x) for x in row["distractors"].split("|")]
        assert all(got > v for v in rest_v) if biggest else all(got < v for v in rest_v)

    rng = rng_for(5, "fractions", "04")
    sums = rng.sample([(a, b, n) for n in range(5, 11) for a in range(1, n) for b in range(1, n) if a < b and a + b < n], 8)
    for a, b, n in sums:
        c = a + b
        wrong = pick_wrong(fr(c, n), [fr(c, 2 * n), fr(c + 1, n), fr(b - a, n), fr(c - 1, n), fr(a * b, n)])
        add("04", I_FRAC_ADD, tr(f"{fa_frac(a, n)} جمع {fa_frac(b, n)} چند می{Z}شود؟", f"{a}/{n} plus {b}/{n} makes how many?"), fr(c, n), wrong,
            tr(f"مخرج همان {fa(n)} می{Z}ماند. {fa(a)} جمع {fa(b)} مساوی {fa(c)}. جواب {fa_frac(c, n)} است.",
               f"The denominator stays {n}. {a} plus {b} equals {c}. The answer is {c}/{n}."))

    for pul, wrong in [(250, [205, 2500, 25]), (305, [350, 3050, 35]), (75, [750, 7, 7500]), (1025, [125, 1052, 10250]), (120, [102, 1200, 12])]:
        add("05", I_MONEY_DEC, tr(f"{money_fa(pul)} را با عدد اعشاری چطور می{Z}نویسیم؟", f"How do we write {money_en(pul)} as a decimal number?"), money(pul),
            [money(w) for w in wrong],
            tr(f"افغانی پیش از نقطه و پول بعد از نقطه می{Z}آید: {fa_dec(money(pul)[2:])}.", f"The afghani come before the point and the pul after the point: {money(pul)[2:]}."))
    rng = rng_for(5, "fractions", "05")
    numq(s, "05", I_MONEY_DEC, tr(f"یک {AFN} چند پول است؟", "How many pul is 1 afghani?"), 100, [10, 1000, 50],
         tr(f"یک {AFN} صد پول است.", "1 afghani is 100 pul."), rng, 2000)
    numq(s, "05", I_MONEY_DEC, tr(f"نیم {AFN} چند پول است؟", "How many pul is half an afghani?"), 100 // 2, [5, 500, 25],
         tr(f"یک {AFN} صد پول است. نیم آن پنجاه پول است.", "1 afghani is 100 pul. Half of it is 50 pul."), rng, 2000)
    numq(s, "05", I_MONEY_DEC, tr("این چند پول است؟", "How many pul is this?"), 25, [250, 5, 52],
         tr(f"{fa_dec('0.25')} {AFN}، یعنی بیست و پنج پول.", "0.25 afghani means 25 pul."), rng, 2000, show=money(25))

    for group, biggest in [(["0.5", "0.25", "0.05", "0.45"], True), (["1.2", "1.15", "1.09", "0.99"], True),
                           (["0.3", "0.25", "0.4", "1.01"], False), (["2.5", "2.05", "2.45", "3.1"], False)]:
        ans = max(group, key=Fraction) if biggest else min(group, key=Fraction)
        say = tr("کدام عدد از همه بزرگتر است؟", "Which number is the biggest?") if biggest else tr("کدام عدد از همه کوچکتر است؟", "Which number is the smallest?")
        help_fa = tr(f"{fa_dec(ans)} از همه بزرگتر است.", f"{ans} is the biggest.") if biggest else tr(f"{fa_dec(ans)} از همه کوچکتر است.", f"{ans} is the smallest.")
        add("06", I_DEC, say, "t:" + ans, ["t:" + d for d in group if d != ans], help_fa)
    for a, b in [(150, 225), (250, 225), (75, 50), (320, 105)]:
        t = a + b
        wrong = pick_wrong(money(t), [money(t + 100), money(t - 100) if t > 100 else money(t + 50), money(t + 10), money(t - 10)])
        add("06", I_DEC, tr(f"{money_fa(a)} جمع {money_fa(b)} چند می{Z}شود؟", f"{money_en(a)} plus {money_en(b)} makes how much?"), money(t), wrong,
            tr(f"جواب {money_fa(t)} است: {fa_dec(money(t)[2:])}.", f"The answer is {money_en(t)}: {money(t)[2:]}."))
    return s


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
                   5: tr("حساب کن و با سکه" + Z + "ها و نوت" + Z + "ها پول بده.", "Work it out and pay with the coins and notes.")},
         icon="scales", sheet="market_scales.csv", make=market),
    dict(id="carpet_weaver", engine="builder", letter="d", title_en="Carpet Weaver", title_fa="قالین" + Z + "باف",
         intro_fa=tr("عددها را به ترتیب درست بگذار.", "Put the numbers in the right order."), icon="carpet", sheet="carpet_weaver.csv", make=weaver),
    dict(id="share_the_bread", engine="sorter", letter="e", title_en="Share the Bread", title_fa="نان را تقسیم کن",
         intro_fa=tr("هر چیز را در سبد درست بینداز.", "Put each thing in the right basket."), icon="bread", sheet="share_the_bread.csv", make=sorter),
    dict(id="shape_mason", engine="listen_pick", letter="f", title_en="Shape Mason", title_fa="گلکار شکل" + Z + "ها",
         intro_fa=tr("گوش کن و جواب درست را انتخاب کن.", "Listen and choose the right answer."), icon="brick", sheet="shape_mason.csv", make=mason),
    # from level 4
    dict(id="twin_tiles", engine="pairs", letter="g", title_en="Twin Tiles", title_fa="جوره" + Z + "ها",
         intro_fa=tr("دو کارت را که با هم جور است پیدا کن.", "Find the two cards that go together."), icon="box", sheet="twin_tiles.csv", make=pairs45),
    dict(id="number_rain", engine="catch", letter="h", title_en="Number Rain", title_fa="باران عددها",
         intro_fa=I_RAIN, icon="basket", sheet="number_rain.csv", make=catch45),
    dict(id="days_and_months", engine="listen_pick", letter="i", title_en="Days and Months", title_fa="روزها و ماه" + Z + "ها",
         intro_fa=tr("گوش کن و جواب درست را انتخاب کن.", "Listen and choose the right answer."), icon="moon", sheet="days_and_months.csv",
         read_choices=True, make=calendar4),
    dict(id="tables_and_charts", engine="listen_pick", letter="j", title_en="Tables and Charts", title_fa="جدول و گراف",
         intro_fa=tr("جدول یا گراف را ببین و جواب بده.", "Look at the table or the chart and answer."), icon="chart_bars_1",
         sheet="tables_and_charts.csv", make=charts5),
    dict(id="fair_shares", engine="listen_pick", letter="k", title_en="Fair Shares", title_fa="حصه" + Z + "های برابر",
         intro_fa=tr("کسر درست را پیدا کن.", "Find the right fraction."), icon="frac_3_4", sheet="fair_shares.csv", make=fractions5),
]
TITLES = {1: ("Math 1: Counting to 20", "ریاضی ۱: شمارش تا بیست"),
          2: ("Math 2: Numbers to 100", "ریاضی ۲: عددها تا صد"),
          3: ("Math 3: Numbers to 1,000", "ریاضی ۳: عددها تا هزار"),
          4: ("Math 4: Times Tables and Sharing", "ریاضی ۴: جدول ضرب و تقسیم"),
          5: ("Math 5: Large Numbers and Fractions", "ریاضی ۵: عددهای بزرگ و کسرها")}
ROUNDS = {  # game -> rounds wanted per level
    "count_the_flock": {1: 12, 2: 10, 3: 8, 4: 6, 5: 6}, "number_hop": {1: 12, 2: 12, 3: 12, 4: 10, 5: 8},
    "market_scales": {1: 6, 2: 6, 3: 6, 4: 6, 5: 5}, "carpet_weaver": {1: 6, 2: 6, 3: 6, 4: 5, 5: 5},
    "share_the_bread": {1: 4, 2: 4, 3: 4, 4: 4, 5: 4}, "shape_mason": {1: 4, 2: 4, 3: 4, 4: 5, 5: 4},
    "twin_tiles": {4: 4, 5: 3}, "number_rain": {4: 2, 5: 2}, "days_and_months": {4: 3},
    "tables_and_charts": {5: 4}, "fair_shares": {5: 6},
}
ITEMS = {"count_the_flock": (8, 8), "number_hop": (8, 8), "market_scales": (6, 6), "carpet_weaver": (5, 5),
         "share_the_bread": (8, 8), "shape_mason": (6, 8), "twin_tiles": (6, 6), "number_rain": (6, 6),
         "days_and_months": (8, 8), "tables_and_charts": (7, 7), "fair_shares": (8, 8)}

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
for _name, _rows in CHARTS.items():
    _what = ", ".join(f"{_v} {_p}" for _p, _, _v in _rows)
    PICTURES[_name] = ((f"a block chart with three columns, a small picture under each column and one block per unit: {_what}"
                        if "bars" in _name else
                        f"a picture table with three rows read from the right: a small picture, then one dot per unit: {_what}")
                       + " (drawn by content/math/draw_pictures.py)")
for _h in range(1, 13):
    PICTURES[f"clock_{_h}"] = (f"a round clock face with the numbers 1 to 12 in Western digits, the short hand pointing "
                              f"exactly at {_h} and the long hand at 12")


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
    lo, hi = ITEMS[game["id"]]
    used: set[str] = set()
    for rnd, rows in rounds.items():
        assert lo <= len(rows) <= hi and 5 <= len(rows) <= 10, (name, rnd, len(rows))
        keys = [(r["say_fa"], r.get("show", ""), r.get("thing", ""), r.get("tiles", ""), r.get("goods", ""),
                 r.get("answer", ""), r.get("targets", ""), r.get("a", "")) for r in rows]
        assert len(set(keys)) == len(keys), (name, rnd, "the same question twice")
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
                if kinds != {"p"} and level <= 3:
                    assert len({value(c) for c in choices}) == 4, (name, r)
                if None not in values:  # never two choices of the same value (4 and ۴, 1/2 and 2/4, 2.5 and 2.50)
                    assert len(set(values)) == len(values), (name, r)
            if game["engine"] == "pairs":
                assert 3 <= len(rows) <= 6, (name, rnd)
                cards = [x[c] for x in rows for c in ("a", "b") if x[c] != "snd"]
                assert len(set(cards)) == len(cards), (name, rnd, "the same card twice")
            if game["engine"] == "catch":
                assert 1 <= int(r["need"]) <= 10, (name, r)
            if game["engine"] == "sorter":
                baskets = {x["basket"] for x in rows}
                assert 2 <= len(baskets) <= 4, (name, rnd)
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
    check_answers45()


def _sum_value(text: str) -> Fraction:
    """'3×4', '12÷3' or '1/5+2/5' worked out from the written tiles."""
    for sign, op in (("×", "*"), ("÷", "/"), ("+", "+")):
        if sign in text:
            x, y = (val("t:" + part) for part in text.split(sign))
            return x * y if op == "*" else x / y if op == "/" else x + y
    raise AssertionError(text)


def check_answers45() -> None:
    """Levels 4 and 5: every answer once more, from what is written in the row."""
    for row, want in CHECK_META:
        assert val(row["answer"]) == want, row
        wrong = [val(x) for x in row["distractors"].split("|")]
        assert want not in wrong and len(set(wrong)) == 3, row
    for row, what in CAL_META:
        assert row["answer"] in (what, "f:" + what) and row["answer"] not in row["distractors"].split("|"), row
    for row in SENT_META:
        tiles = [x[2:] for x in row["tiles"].split("|")]
        assert len(tiles) == 5 and tiles[3] == "=", row
        result = _sum_value("".join(tiles[:3]))
        assert result == val("t:" + tiles[4]), row
        extras = [val(x) for x in row["extra"].split("|")]
        assert result not in extras and len(tiles) + len(extras) <= 8, row
        assert not set(row["extra"].split("|")) & set(row["tiles"].split("|")), row
    for row, up in ORDER_META:
        values = [val(x) for x in row["tiles"].split("|")]
        assert values == sorted(values, reverse=not up) and len(set(values)) == len(values) <= 8, row
    for row, kind in PAIR_META:
        if kind == "sum":
            assert _sum_value(row["a"][2:]) == val(row["b"]), row
        elif kind == "same":
            assert val(row["a"]) == val(row["b"]) and row["a"] != row["b"], row
        else:
            assert row["a"].startswith(("frac_", "shape_circle")) and row["b"] == "snd" and row["say_fa"], row
    for row, test in CATCH_META:
        assert all(test(val(x)) for x in row["targets"].split("|")), row
        assert not any(test(val(x)) for x in row["others"].split("|")), row
    half = Fraction(1, 2)
    for row, kind in SORT2_META:
        if kind == "sum":
            assert _sum_value(row["thing"][2:]) == val(row["basket"]), row
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
    # no pair round may hold two cards of the same value on its answer side
    rounds: dict[tuple, list] = {}
    for row, kind in PAIR_META:
        rounds.setdefault((row["intro_fa"], row["round"]), []).append(val(row["b"]) if kind != "name" else row["say_fa"])
    for answers in rounds.values():
        assert len(set(answers)) == len(answers), answers


def main() -> None:
    _test_numbers()
    used: set[str] = set()
    files: dict[Path, str] = {}
    for level in (1, 2, 3, 4, 5):
        games = []
        for game in GAMES:
            if level not in ROUNDS[game["id"]]:
                continue
            sheet = game["make"](level)
            used |= check_sheet(level, game, sheet)
            files[HERE / str(level) / game["sheet"]] = sheet.text()
            entry = {k: v for k, v in game.items() if k != "make"}
            if isinstance(entry["intro_fa"], dict):
                entry["intro_fa"] = entry["intro_fa"][level]
            used_en({"intro_fa": entry["intro_fa"]})
            used.add(entry["icon"])
            games.append(entry)
        assert len({g["letter"] for g in games}) == len(games)
        pack = {"pack": f"math-{level}", "subject": "math", "level": level, "version": 1,
                "title_en": TITLES[level][0], "title_fa": TITLES[level][1], "games": games}
        files[HERE / str(level) / "pack.json"] = json.dumps(pack, ensure_ascii=False, indent=1) + "\n"
    check_answers()
    missing = used - set(PICTURES)
    assert not missing, f"pictures without a description: {sorted(missing)}"
    files[HERE / "pictures.txt"] = "".join(f"{name}: {PICTURES[name]}\n" for name in sorted(used))
    files[I18N] = english_table()
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(files)} files, {len(used)} pictures, {len(USED_EN)} English texts")


if __name__ == "__main__":
    main()

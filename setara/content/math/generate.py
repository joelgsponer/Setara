#!/usr/bin/env python3
"""Generates the math packs (levels 1 to 3): every CSV sheet, pack.json and
pictures.txt in this folder.

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
    """0..1000 in Afghan Dari words."""
    assert isinstance(n, int) and 0 <= n <= 1000, n
    if n == 1000:
        return "هزار"
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

I_COUNT = "بشمار و عدد درست را انتخاب کن."
I_COUNT_D = "بشمار و عدد دری را انتخاب کن."
I_HEAR = "گوش کن و عدد را پیدا کن."
I_MATCH = "همین عدد را به شکل دیگر پیدا کن."
I_MORE = "ببین کدام از همه بیشتر است."
I_COMPARE = "خوب ببین و مقایسه کن."
I_PLACE = "ده" + Z + "ها و یک" + Z + "ها را یکجا کن."
I_PLACE3 = "صدها، ده" + Z + "ها و یک" + Z + "ها را یکجا کن."
I_DIGIT = "ببین در عدد چند ده و چند یک است."
I_NEXT = "عدد پیش و عدد بعد را پیدا کن."
I_MIX = "حالا همه را با هم تمرین کن."


def count_item(s, rnd, intro, n, obj, script, rng, hi=20):
    pic, noun = obj
    assert 1 <= n <= 20
    if n <= 10:
        help_fa = "، ".join(fa(i) for i in range(1, n + 1)) + f". {fa(n)} {noun} است."
    else:
        help_fa = f"{fa(n)} {noun} است."
    wrong = near(n, rng, 0, hi)
    row = lp(s, rnd, intro, f"چند {noun} است؟", num(n, script), [num(x, script) for x in wrong],
             show=f"p:{pic}*{n}", help_fa=help_fa)
    m = re.match(r"p:\w+\*(\d+)$", row["show"])
    assert int(m.group(1)) == value(row["answer"]) == n


def hear_item(s, rnd, intro, n, script, rng, lo, hi, prefer=()):
    wrong = near(n, rng, lo, hi, prefer)
    row = lp(s, rnd, intro, f"عدد {fa(n)} کدام است؟", num(n, script), [num(x, script) for x in wrong])
    assert value(row["answer"]) == n


def match_item(s, rnd, intro, n, to_script, rng, lo, hi, prefer=()):
    """Show the number in one digit system, pick it in the other."""
    from_script = "D" if to_script == "W" else "W"
    wrong = near(n, rng, lo, hi, prefer)
    row = lp(s, rnd, intro, f"{fa(n)}. همین عدد را پیدا کن.", num(n, to_script),
             [num(x, to_script) for x in wrong], show=num(n, from_script),
             help_fa=f"این عدد {fa(n)} است.")
    assert value(row["show"]) == value(row["answer"]) == n
    assert row["show"][0] != row["answer"][0]


def flock_compare_item(s, rnd, intro, obj, counts, most: bool):
    """Four groups of the same thing: which has the most (or the fewest)?"""
    pic, noun = obj
    assert len(set(counts)) == 4 and all(1 <= c <= 20 for c in counts)
    ans = max(counts) if most else min(counts)
    wrong = [c for c in counts if c != ans]
    word = "بیشتر" if most else "کمتر"
    row = lp(s, rnd, intro, f"کدام از همه {word} است؟", f"p:{pic}*{ans}", [f"p:{pic}*{c}" for c in wrong],
             help_fa=f"{fa(ans)} {noun} از همه {word} است.")
    got = int(row["answer"].split("*")[1])
    others = [int(x.split("*")[1]) for x in row["distractors"].split("|")]
    assert all(got > o for o in others) if most else all(got < o for o in others)


def numeral_compare_item(s, rnd, intro, numbers, biggest: bool, script="W"):
    assert len(set(numbers)) == 4
    ans = max(numbers) if biggest else min(numbers)
    wrong = [n for n in numbers if n != ans]
    word = "بزرگتر" if biggest else "کوچکتر"
    row = lp(s, rnd, intro, f"کدام عدد از همه {word} است؟", num(ans, script), [num(n, script) for n in wrong],
             help_fa=f"{fa(ans)} از همه {word} است.")
    got = value(row["answer"])
    others = [value(x) for x in row["distractors"].split("|")]
    assert all(got > o for o in others) if biggest else all(got < o for o in others)


def next_item(s, rnd, intro, n, after: bool, rng, lo, hi):
    if after:
        ans, say = n + 1, f"بعد از {fa(n)} کدام عدد می{Z}آید؟"
        prefer = [n, n - 1, n + 2, n + 11]
        help_fa = f"بعد از {fa(n)}، {fa(ans)} می{Z}آید."
    else:
        ans, say = n - 1, f"پیش از {fa(n)} کدام عدد است؟"
        prefer = [n, n + 1, n - 2, n - 11]
        help_fa = f"پیش از {fa(n)}، {fa(ans)} است."
    wrong = near(ans, rng, lo, hi, prefer)
    row = lp(s, rnd, intro, say, W(ans), [W(x) for x in wrong], help_fa=help_fa)
    assert value(row["answer"]) == (n + 1 if after else n - 1)


def place2_item(s, rnd, intro, t, o, rng):
    """'Three tens and four ones' -> 34."""
    assert 1 <= t <= 9 and 0 <= o <= 9
    ans = 10 * t + o
    if o:
        say = f"{ONES[t]} ده و {ONES[o]} یک، چند می{Z}شود؟"
        prefer = [10 * o + t, t + o]
    else:
        say = f"{ONES[t]} ده، چند می{Z}شود؟"
        prefer = [t, 10 + t]
    wrong = near(ans, rng, 0, 100, prefer)
    row = lp(s, rnd, intro, say, W(ans), [W(x) for x in wrong], help_fa=f"{ONES[t]} ده یعنی {fa(10 * t)}. جواب {fa(ans)} است.")
    assert value(row["answer"]) == t * 10 + o


def digit_item(s, rnd, intro, n, ask_tens: bool, rng):
    """Show 34: how many tens? how many ones?"""
    t, o = divmod(n, 10)
    assert 1 <= t <= 9 and t != o
    ans = t if ask_tens else o
    what = "ده" if ask_tens else "یک"
    wrong = near(ans, rng, 0, 9, [o if ask_tens else t])
    row = lp(s, rnd, intro, f"در عدد {fa(n)}، چند {what} است؟", W(ans), [W(x) for x in wrong], show=W(n),
             help_fa=f"{fa(n)} یعنی {ONES[t]} ده و {ONES[o]} یک.")
    shown = value(row["show"])
    assert value(row["answer"]) == (shown // 10 if ask_tens else shown % 10)


def place3_item(s, rnd, intro, h, t, o, rng):
    """'Two hundreds, four tens and five ones' -> 245."""
    assert 1 <= h <= 9 and (t or o)
    ans = 100 * h + 10 * t + o
    bits = [f"{ONES[h]} صد"]
    if t:
        bits.append(f"{ONES[t]} ده")
    if o:
        bits.append(f"{ONES[o]} یک")
    say = (bits[0] + " و " + bits[1] if len(bits) == 2 else f"{bits[0]}، {bits[1]} و {bits[2]}") + f"، چند می{Z}شود؟"
    prefer = digit_perms(ans)[:2]
    if not t:
        prefer = [100 * h + 10 * o, 10 * h + o] + prefer
    if not o:
        prefer = [100 * h + t, 10 * h + t] + prefer
    wrong = near(ans, rng, 0, 1000, prefer)
    row = lp(s, rnd, intro, say, W(ans), [W(x) for x in wrong], help_fa=f"جواب {fa(ans)} است.")
    assert value(row["answer"]) == 100 * h + 10 * t + o


def similar_numbers(x: int, rng: random.Random, lo: int, hi: int) -> list[int]:
    """Four different numbers that look alike, x among them."""
    cands = [c for c in digit_perms(x) + [x - 1, x + 1, x - 10, x + 10, x - 100, x + 100, x + 9, x - 9]
             if lo <= c <= hi and c != x]
    cands = list(dict.fromkeys(cands))
    assert len(cands) >= 3, x
    return [x] + rng.sample(cands, 3)


def flock(level: int) -> Sheet:
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
I_ADD = "جمع کن و جواب را انتخاب کن."
I_SUB = "کم کن و جواب را انتخاب کن."
I_BOTH = "خوب گوش کن: جمع است یا منفی؟"
I_STORY = "قصه را گوش کن و حساب کن."
I_TENS = "ده" + Z + "ها را جمع و منفی کن."
I_MUL = "ضرب کن و جواب را انتخاب کن."

# picture, noun, "... more came", "... went"
STORY_OBJS = [
    ("sheep", "گوسفند", "{b} تای دیگر آمد", "{b} تا رفت"),
    ("apple", "سیب", "{b} تای دیگر آوردند", "{b} تا را خوردند"),
    ("hen", "مرغ", "{b} تای دیگر آمد", "{b} تا رفت"),
    ("bread", "نان", "{b} تای دیگر پختند", "{b} تا را خوردند"),
    ("goat", "بز", "{b} تای دیگر آمد", "{b} تا رفت"),
    ("egg", "تخم", "{b} تای دیگر آوردند", "{b} تا شکست"),
]

HOP_META: list[tuple[dict, int, str, int]] = []


def calc(a: int, op: str, b: int) -> int:
    return a + b if op == "+" else a - b if op == "-" else a * b


def hop_item(s, rnd, intro, a, op, b, rng, hi, say=None, show="", extra_prefer=()):
    ans = calc(a, op, b)
    assert ans >= 0 and a >= 0 and b >= 0
    if say is None:
        say = f"{fa(a)} {OP_WORD[op]} {fa(b)} چند می{Z}شود؟"
    help_fa = f"{fa(a)} {OP_WORD[op]} {fa(b)} مساوی {fa(ans)}."
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
    row = lp(s, rnd, intro, say, W(ans), [W(x) for x in wrong], show=show, help_fa=help_fa, hop=hop)
    HOP_META.append((row, a, op, b))


def story_item(s, rnd, intro, a, op, b, rng, hi, k, with_picture):
    assert a >= 1 and b >= 1
    pic, noun, came, went = STORY_OBJS[k % len(STORY_OBJS)]
    if op == "+":
        say = f"{fa(a)} {noun} بود، {came.format(b=fa(b))}. چند تا شد؟"
    else:
        say = f"{fa(a)} {noun} بود، {went.format(b=fa(b))}. چند تا ماند؟"
    show = f"p:{pic}*{a}" if with_picture and a <= 20 else ""
    hop_item(s, rnd, intro, a, op, b, rng, hi, say=say, show=show)


def money_story(s, rnd, intro, a, op, b, rng, hi):
    if op == "+":
        say = f"{fa(a)} افغانی داشتی، {fa(b)} افغانی دیگر گرفتی. چند افغانی شد؟"
    else:
        say = f"{fa(a)} افغانی داشتی، {fa(b)} افغانی خرج کردی. چند افغانی ماند؟"
    hop_item(s, rnd, intro, a, op, b, rng, hi, say=say)


def hop(level: int) -> Sheet:
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
    assert reachable(target, units), (target, units)
    row = s.add(round=rnd, say_fa=say, goods=goods, target=target, units="|".join(map(str, units)),
                mode=mode, help_fa=help_fa)
    MARKET_META.append((row, target))


def pay_help(target, units) -> str:
    parts = greedy(target, units)
    if len(parts) == 1:
        return f"{fa(target)} {AFN} بده."
    return " جمع ".join(fa(p) for p in parts) + f" مساوی {fa(target)}."


def market(level: int) -> Sheet:
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
                market_row(s, rnd, f"{fa(n)} {noun} بده.", pic, n, [1], "count",
                           f"{fa(n)} دانه {noun} روی ترازو بگذار.")
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
                market_row(s, rnd, f"{noun} {fa(p)} {AFN} است. پولش را بده.", pic, p, units, "pay", pay_help(p, units))
    else:
        both = f"هر دو چند {AFN} می{Z}شود؟ پولش را بده."
        # 01: a bill of two things, whole tens
        rng = rng_for(3, "market", "01")
        pairs = rng.sample([(a, b) for a in range(10, 90, 10) for b in range(10, 90, 10) if a != b and a + b <= 100], 6)
        for j, (a, b) in enumerate(pairs):
            (p1, n1), (p2, n2) = SHOP[j], SHOP[j + 3]
            market_row(s, "01", f"{n1} {fa(a)} {AFN} و {n2} {fa(b)} {AFN} است. {both}", p1, a + b,
                       [10, 20, 50], "pay", f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.")
        # 02: a bill of two things, with carrying
        rng = rng_for(3, "market", "02")
        pairs = rng.sample([(a, b) for a in range(12, 59) for b in range(12, 59)
                            if a % 10 + b % 10 >= 10 and a % 10 and b % 10 and a + b <= 100], 6)
        for j, (a, b) in enumerate(pairs):
            (p1, n1), (p2, n2) = SHOP[j + 2], SHOP[(j + 6) % len(SHOP)]
            market_row(s, "02", f"{n1} {fa(a)} {AFN} و {n2} {fa(b)} {AFN} است. {both}", p1, a + b,
                       [1, 2, 5, 10, 20, 50], "pay", f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.")
        # 03: several of one thing: tables of 2, 5 and 10
        rng = rng_for(3, "market", "03")
        deals = []
        for price in (2, 5, 10):
            deals += [(k, price) for k in rng.sample(range(2, 11), 2)]
        countable = [SHOP[0], SHOP[1], SHOP[2], SHOP[3], SHOP[4], GOODS[0]]
        for j, (k, price) in enumerate(spread(deals, rng)):
            pic, noun = countable[j]
            market_row(s, "03", f"{fa(k)} {noun} می{Z}خری. هر {noun} {fa(price)} {AFN} است. چند {AFN} می{Z}شود؟ پولش را بده.",
                       pic, k * price, [1, 2, 5, 10, 20, 50, 100], "pay", f"{fa(k)} ضرب {fa(price)} مساوی {fa(k * price)}.")
        # 04: prices in the hundreds
        rng = rng_for(3, "market", "04")
        units = [10, 20, 50, 100]
        for j, p in enumerate(rng.sample(range(110, 501, 10), 6)):
            pic, noun = BIG[j]
            market_row(s, "04", f"{noun} {fa(p)} {AFN} است. پولش را بده.", pic, p, units, "pay", pay_help(p, units))
        # 05: a bill of two things, hundreds
        rng = rng_for(3, "market", "05")
        pairs = rng.sample([(a, b) for a in range(100, 301, 10) for b in range(20, 201, 10) if a + b <= 500], 6)
        for j, (a, b) in enumerate(pairs):
            (p1, n1), (p2, n2) = BIG[j], SHOP[j + 3]
            market_row(s, "05", f"{n1} {fa(a)} {AFN} و {n2} {fa(b)} {AFN} است. {both}", p1, a + b,
                       units, "pay", f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.")
        # 06: change
        rng = rng_for(3, "market", "06")
        deals = [(g, rng.choice([p for p in range(g // 2, g) if p % 10])) for g in (20, 50, 100, 50, 100, 100)]
        assert len(set(deals)) == 6
        for j, (given, price) in enumerate(deals):
            pic, noun = SHOP[(j + 1) % len(SHOP)]
            change = given - price
            market_row(s, "06", f"{noun} {fa(price)} {AFN} است. مشتری {fa(given)} {AFN} داد. چند {AFN} باقی می{Z}ماند؟ باقی را پس بده.",
                       pic, change, [1, 2, 5, 10, 20, 50], "pay", f"{fa(given)} منفی {fa(price)} مساوی {fa(change)}.")
    return s


# ---------------------------------------------------------------------------
# 4. Carpet Weaver (builder)
# ---------------------------------------------------------------------------

BUILDER_COLS = ["round", "intro_fa", "say_en", "say_fa", "tiles", "extra", "rtl", "done_en", "done_fa", "help_fa"]
I_SEQ = "عددها را به ترتیب درست بگذار."
WEAVE_META: list[tuple[dict, list[int], list[int], str]] = []


def seq_item(s, rnd, start, step, count, extra=(), script="W", intro=I_SEQ, table=None):
    """A run of numbers: start, start+step, ... (step may be negative)."""
    seq = [start + i * step for i in range(count)]
    assert all(0 <= x <= 1000 for x in seq) and step != 0
    a, b, k = fa(seq[0]), fa(seq[-1]), fa(abs(step))
    if step == 1:
        say, help_fa = f"از {a} تا {b} به ترتیب بشمار.", "هر بار یک زیاد کن."
    elif step == -1:
        say, help_fa = f"از {a} تا {b}، یکی یکی کم کن.", "هر بار یک کم کن."
    elif step > 1:
        say, help_fa = f"{k} تا {k} تا بشمار، از {a} تا {b}.", f"هر بار {k} زیاد کن."
        if table:
            say = f"جدول ضرب {fa(table)}: " + say
    else:
        say, help_fa = f"از {a} تا {b}، {k} تا {k} تا کم کن.", f"هر بار {k} کم کن."
    _weave(s, rnd, intro, say, seq, list(extra), script, help_fa, "seq")


def order_item(s, rnd, numbers, up=True, intro=I_SEQ):
    seq = sorted(numbers, reverse=not up)
    assert len(set(seq)) == len(seq)
    if up:
        say, help_fa = "این عددها را از کوچک به بزرگ بچین.", "اول کوچکترین عدد را پیدا کن."
    else:
        say, help_fa = "این عددها را از بزرگ به کوچک بچین.", "اول بزرگترین عدد را پیدا کن."
    _weave(s, rnd, intro, say, seq, [], "W", help_fa, "up" if up else "down")


def _weave(s, rnd, intro, say, seq, extra, script, help_fa, kind):
    assert 2 <= len(seq) and len(seq) + len(extra) <= 8, (seq, extra)
    assert not set(seq) & set(extra) and len(set(extra)) == len(extra)
    if kind == "seq":  # an extra tile must never continue the run at either end
        step = seq[1] - seq[0]
        assert seq[0] - step not in extra and seq[-1] + step not in extra, (seq, extra)
    row = s.add(round=rnd, intro_fa=intro, say_fa=say, tiles="|".join(num(x, script) for x in seq),
                extra="|".join(num(x, script) for x in extra), rtl="yes" if script == "D" else "",
                done_fa="، ".join(fa(x) for x in seq) + ".", help_fa=help_fa)
    WEAVE_META.append((row, seq, extra, kind))


def weaver(level: int) -> Sheet:
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
I_SHAPES = "هر چیز را در سبد شکل خودش بینداز."
I_PARITY = "عددهای جفت و طاق را جدا کن."
I_FRACTION = "پوره، نیم یا چارک؟ هر کدام را در سبد خودش بینداز."
I_500 = "عدد از پنج" + Z + "صد کمتر است یا بیشتر؟"
SORT_META: list[tuple[dict, str, object]] = []


def sorter(level: int) -> Sheet:
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
            row = s.add(round=rnd, intro_fa=I_SHAPES, thing=pic, say_fa=name, basket=SHAPES[shape][0],
                        basket_say_fa=SHAPES[shape][1])
            SORT_META.append((row, "shape", shape))

    def parity_round(rnd, pool):
        rng = rng_for(level, "sorter", rnd)
        evens = rng.sample([n for n in pool if n % 2 == 0], 4)
        odds = rng.sample([n for n in pool if n % 2 == 1], 4)
        for n in spread(evens + odds, rng):
            basket = EVEN if n % 2 == 0 else ODD
            row = s.add(round=rnd, intro_fa=I_PARITY, thing=W(n), say_fa=fa(n), basket=basket[0], basket_say_fa=basket[1])
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
            if not named:
                name = FRACTION_NOUNS[FRACTIONS[kind].index((pic, name))]
                assert basket[1] not in name
            row = s.add(round=rnd, intro_fa=I_FRACTION, thing=pic, say_fa=name, basket=basket[0], basket_say_fa=basket[1])
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
            row = s.add(round="02", intro_fa=I_500, thing=W(n), say_fa=fa(n),
                        basket="f:کمتر از ۵۰۰" if less else "f:بیشتر از ۵۰۰",
                        basket_say_fa="کمتر از پنج" + Z + "صد" if less else "بیشتر از پنج" + Z + "صد")
            SORT_META.append((row, "500", n))
        fraction_round("03", [("whole", [2, 3]), ("half", [1, 2, 3]), ("quarter", [1, 2, 3])], named=False)
        parity_round("04", range(101, 1000))
    return s


# ---------------------------------------------------------------------------
# 6. Shape Mason (listen_pick)
# ---------------------------------------------------------------------------

I_SHAPE = "شکل درست را پیدا کن."
I_SHAPE_OBJ = "ببین هر چیز چه شکلی دارد."
I_LONG = "ببین کدام درازتر و کدام کوتاه" + Z + "تر است."
I_CORNER = "گوشه" + Z + "ها و ضلع" + Z + "ها را بشمار."
I_CLOCK = "گوش کن و ساعت درست را پیدا کن."
I_CLOCK_READ = "ساعت را ببین و بگو ساعت چند است."
I_CLOCK_LATER = "ساعت را ببین و فکر کن."
I_LENGTH = "متر و سانتی" + Z + "متر را حساب کن."
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
    s = Sheet(LP_COLS)
    order = ["circle", "square", "triangle", "rectangle"]
    if level == 1:
        rng = rng_for(1, "mason", "01")
        for shape in order + spread(order, rng):
            pic, name = SHAPES[shape]
            first = len([r for r in s.rows if r["answer"] == pic]) == 0
            say = f"{name} کدام است؟" if first else f"شکل {name} را پیدا کن."
            lp(s, "01", I_SHAPE, say, pic, [SHAPES[o][0] for o in order if o != shape], help_fa=f"این شکل {name} است.")
        rng = rng_for(1, "mason", "02")
        for k in (1, 2):
            for shape in spread(order, rng):
                pic, noun = SHAPED[shape][k]
                wrong = [SHAPED[o][1 + (k + j) % 3][0] for j, o in enumerate(x for x in order if x != shape)]
                if shape == "rectangle":  # a square is a rectangle too: never offer one as a wrong choice
                    wrong[order.index("square")] = SHAPED["circle"][4 + k][0]
                    assert not set(wrong) & {p for p, _ in SHAPED["square"]} and len(set(wrong)) == 3
                lp(s, "02", I_SHAPE_OBJ, f"کدام چیز شکل {SHAPES[shape][1]} دارد؟", pic, wrong,
                   help_fa=f"{noun} شکل {SHAPES[shape][1]} دارد.")
        for i, (noun, long_pic, short_pic, long_word, short_word) in enumerate(LENGTHS):
            other = LENGTHS[(i + 1) % len(LENGTHS)]
            lp(s, "03", I_LONG, f"کدام {noun} {long_word} است؟", long_pic, [short_pic, other[1], other[2]],
               help_fa=f"این {noun} {long_word} است.")
        for i, (noun, long_pic, short_pic, long_word, short_word) in enumerate(LENGTHS):
            other = LENGTHS[(i + 2) % len(LENGTHS)]
            lp(s, "03", I_LONG, f"کدام {noun} {short_word} است؟", short_pic, [long_pic, other[1], other[2]],
               help_fa=f"این {noun} {short_word} است.")
        corners = {"circle": 0, "square": 4, "triangle": 3, "rectangle": 4}
        rng = rng_for(1, "mason", "04")
        for shape, what in [("triangle", "گوشه"), ("square", "ضلع"), ("circle", "گوشه"), ("rectangle", "گوشه"),
                            ("triangle", "ضلع"), ("square", "گوشه")]:
            pic, name = SHAPES[shape]
            n = corners[shape]
            row = lp(s, "04", I_CORNER, f"{name} چند {what} دارد؟", W(n), [W(x) for x in near(n, rng, 0, 8)], show=pic,
                     help_fa=(f"{name} {fa(n)} {what} دارد." if n else f"{name} هیچ {what} ندارد."))
            MASON_META.append((row, n))
        lp(s, "04", I_CORNER, "کدام شکل سه گوشه دارد؟", "shape_triangle", ["shape_circle", "shape_square", "shape_rectangle"],
           help_fa="مثلث سه گوشه دارد.")
        lp(s, "04", I_CORNER, "کدام شکل هیچ گوشه ندارد؟", "shape_circle", ["shape_triangle", "shape_square", "shape_rectangle"],
           help_fa="دایره هیچ گوشه ندارد.")
    elif level == 2:
        def clock(h):
            return f"clock_{(h - 1) % 12 + 1}"

        def wrap(h):
            return (h - 1) % 12 + 1

        def hear_clock(rnd, hours):
            rng = rng_for(2, "mason", rnd)
            for h in spread(hours, rng):
                wrong = [clock(h - 1), clock(h + 1), clock(h + 6)]
                row = lp(s, rnd, I_CLOCK, f"ساعت {fa(h)} است. ساعت درست را پیدا کن.", clock(h), wrong,
                         help_fa=f"عقربه کوتاه طرف {fa(h)} است و عقربه دراز طرف دوازده.")
                MASON_META.append((row, h))

        hear_clock("01", [1, 2, 3, 4, 5, 6])
        hear_clock("02", [7, 8, 9, 10, 11, 12])
        rng = rng_for(2, "mason", "03")
        for h in rng.sample(range(1, 13), 8):
            wrong = near(h, rng, 1, 12, [12 if h != 12 else 6, wrap(h + 1), wrap(h - 1)])
            row = lp(s, "03", I_CLOCK_READ, "ساعت چند است؟", W(h), [W(x) for x in wrong], show=clock(h),
                     help_fa=f"عقربه کوتاه طرف {fa(h)} است. ساعت {fa(h)} است.")
            MASON_META.append((row, h))
        rng = rng_for(2, "mason", "04")
        hours = rng.sample(range(1, 12), 7)
        for h in hours[:4]:
            wrong = near(h, rng, 1, 12, [12, wrap(h + 1), wrap(h - 1)])
            row = lp(s, "04", I_CLOCK_LATER, "ساعت چند است؟", D(h), [D(x) for x in wrong], show=clock(h),
                     help_fa=f"عقربه کوتاه طرف {fa(h)} است. ساعت {fa(h)} است.")
            MASON_META.append((row, h))
        for h in hours[4:] + [12]:
            later = wrap(h + 1)
            wrong = near(later, rng, 1, 12, [h, wrap(h - 1), wrap(h + 2)])
            row = lp(s, "04", I_CLOCK_LATER, f"حالا ساعت {fa(h)} است. یک ساعت بعد، ساعت چند می{Z}شود؟", W(later),
                     [W(x) for x in wrong], show=clock(h), help_fa=f"یک ساعت بعد از {fa(h)}، ساعت {fa(later)} می{Z}شود.")
            MASON_META.append((row, h % 12 + 1))
    else:
        def q(rnd, say, ans, prefer, help_fa, hi=2000):
            rng = rng_for(3, "mason", rnd, say)
            row = lp(s, rnd, I_LENGTH, say, W(ans), [W(x) for x in near(ans, rng, 0, hi, prefer)], help_fa=help_fa)
            MASON_META.append((row, ans))

        for m in (1, 2, 5, 10):
            q("01", f"{fa(m)} {M} چند {CM} است؟", m * 100, [m * 10, m * 100 + 100, m],
              f"هر متر صد {CM} است. {fa(m)} {M}، {fa(m * 100)} {CM} می{Z}شود.")
        q("01", f"نیم {M} چند {CM} است؟", 100 // 2, [5, 500, 20], f"یک متر صد {CM} است. نیم آن پنجاه {CM} است.")
        for c in (300, 700, 400):
            q("01", f"{fa(c)} {CM} چند {M} است؟", c // 100, [c // 10, c // 100 + 1, c // 100 - 1],
              f"هر صد {CM} یک {M} است. {fa(c)} {CM}، {fa(c // 100)} {M} می{Z}شود.")
        adds = [("چوب", 40, 35, CM), ("ریسمان", 28, 17, CM), ("تکه", 56, 29, CM), ("چوب", 65, 25, CM),
                ("دیوار", 12, 8, M), ("ریسمان", 37, 26, M), ("جوی", 45, 15, M), ("سرک", 120, 60, M)]
        for noun, a, b, unit in adds:
            q("02", f"یک {noun} {fa(a)} {unit} است و {noun} دیگر {fa(b)} {unit}. هر دو با هم چند {unit} می{Z}شود؟",
              a + b, [a + b - 10, a - b, a + b + 10], f"{fa(a)} جمع {fa(b)} مساوی {fa(a + b)}.")
        subs = [("ریسمان", 90, 35, CM), ("تکه", 72, 48, CM), ("چوب", 50, 15, CM), ("سیم", 100, 40, CM),
                ("ریسمان", 30, 12, M), ("تکه", 64, 27, M), ("سیم", 81, 36, M), ("ریسمان", 200, 50, M)]
        for noun, a, b, unit in subs:
            q("03", f"یک {noun} {fa(a)} {unit} بود. {fa(b)} {unit} آن بریده شد. چند {unit} ماند؟",
              a - b, [a - b + 10, a + b, a - b - 10], f"{fa(a)} منفی {fa(b)} مساوی {fa(a - b)}.")
        for m, c in [(1, 20), (2, 50), (3, 5), (1, 75), (4, 10), (2, 8)]:
            q("04", f"{fa(m)} {M} و {fa(c)} {CM}، چند {CM} می{Z}شود؟", m * 100 + c, [m * 10 + c, m + c, m * 100 + c * 10],
              f"{fa(m)} {M}، {fa(m * 100)} {CM} است. {fa(m * 100)} جمع {fa(c)} مساوی {fa(m * 100 + c)}.")
        for n in (150, 130):
            q("04", f"{fa(n)} {CM}، یک {M} و چند {CM} است؟", n - 100, [n, (n - 100) // 10, n - 100 + 10],
              f"یک {M} صد {CM} است. {fa(n)} منفی صد مساوی {fa(n - 100)}.")
    return s


# ---------------------------------------------------------------------------
# Packs
# ---------------------------------------------------------------------------

GAMES = [
    dict(id="count_the_flock", engine="listen_pick", letter="a", title_en="Count the Flock", title_fa="رمه را بشمار",
         intro_fa="بشمار و عدد درست را انتخاب کن.", icon="sheep", v1=True, sheet="count_the_flock.csv", make=flock),
    dict(id="number_hop", engine="journey", letter="b", title_en="Number Hop", title_fa="خیز عددها",
         intro_fa="حساب کن و جواب درست را انتخاب کن.", icon="frog", v1=True, sheet="number_hop.csv", make=hop),
    dict(id="market_scales", engine="market", letter="c", title_en="Market Scales", title_fa="ترازوی بازار",
         intro_fa={1: "گوش کن و همان قدر روی ترازو بگذار.", 2: "قیمت را گوش کن و با سکه" + Z + "ها و نوت" + Z + "ها پول بده.",
                   3: "حساب کن و با سکه" + Z + "ها و نوت" + Z + "ها پول بده."},
         icon="scales", sheet="market_scales.csv", make=market),
    dict(id="carpet_weaver", engine="builder", letter="d", title_en="Carpet Weaver", title_fa="قالین" + Z + "باف",
         intro_fa="عددها را به ترتیب درست بگذار.", icon="carpet", sheet="carpet_weaver.csv", make=weaver),
    dict(id="share_the_bread", engine="sorter", letter="e", title_en="Share the Bread", title_fa="نان را تقسیم کن",
         intro_fa="هر چیز را در سبد درست بینداز.", icon="bread", sheet="share_the_bread.csv", make=sorter),
    dict(id="shape_mason", engine="listen_pick", letter="f", title_en="Shape Mason", title_fa="گلکار شکل" + Z + "ها",
         intro_fa="گوش کن و جواب درست را انتخاب کن.", icon="brick", sheet="shape_mason.csv", make=mason),
]
TITLES = {1: ("Math 1: Counting to 20", "ریاضی ۱: شمارش تا بیست"),
          2: ("Math 2: Numbers to 100", "ریاضی ۲: عددها تا صد"),
          3: ("Math 3: Numbers to 1,000", "ریاضی ۳: عددها تا هزار")}
ROUNDS = {  # game -> rounds wanted per level
    "count_the_flock": {1: 12, 2: 10, 3: 8}, "number_hop": {1: 12, 2: 12, 3: 12},
    "market_scales": {1: 6, 2: 6, 3: 6}, "carpet_weaver": {1: 6, 2: 6, 3: 6},
    "share_the_bread": {1: 4, 2: 4, 3: 4}, "shape_mason": {1: 4, 2: 4, 3: 4},
}
ITEMS = {"count_the_flock": (8, 8), "number_hop": (8, 8), "market_scales": (6, 6), "carpet_weaver": (5, 5),
         "share_the_bread": (8, 8), "shape_mason": (6, 8)}

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
for _h in range(1, 13):
    PICTURES[f"clock_{_h}"] = (f"a round clock face with the numbers 1 to 12 in Western digits, the short hand pointing "
                              f"exactly at {_h} and the long hand at 12")


def pictures_in(cell: str) -> list[str]:
    out = []
    for spec in filter(None, (c.strip() for c in cell.split("|"))):
        if spec.startswith(("t:", "f:")):
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
                 r.get("answer", "")) for r in rows]
        assert len(set(keys)) == len(keys), (name, rnd, "the same question twice")
        for r in rows:
            assert r["say_fa"].strip() and re.search("[\u0600-\u06ff]", r["say_fa"]), (name, r)
            assert not re.search(r"\d", r["say_fa"] + r.get("help_fa", "")), (name, "digits in speech", r)
            for col in ("show", "answer", "distractors", "thing", "basket", "tiles", "extra", "goods"):
                used.update(pictures_in(r.get(col, "")))
            if game["engine"] in ("listen_pick", "journey"):
                choices = [r["answer"]] + r["distractors"].split("|")
                assert len(choices) == 4 and len(set(choices)) == 4, (name, r)
                kinds = {"t" if c.startswith("t:") else "f" if c.startswith("f:") else "p" for c in choices}
                assert len(kinds) == 1, (name, "mixed kinds of choices", r)
                if kinds != {"p"}:
                    assert len({value(c) for c in choices}) == 4, (name, r)
            if game["engine"] == "sorter":
                baskets = {x["basket"] for x in rows}
                assert 2 <= len(baskets) <= 4, (name, rnd)
    return used


def check_answers() -> None:
    """Every answer once more, independently of how the row was made."""
    for row, a, op, b in HOP_META:
        ans = value(row["answer"])
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
            assert op == "*" or max(a, b, ans) > 20, row
        if op == "*":
            assert "ضرب" in row["say_fa"]
    for row, target in MARKET_META:
        units = [int(u) for u in row["units"].split("|")]
        assert int(row["target"]) == target and reachable(target, units), row
        assert set(units) <= {1, 2, 5, 10, 20, 50, 100}, row
        if row["mode"] == "count":
            assert units == [1] and 1 <= target <= 20 and row["say_fa"].startswith(fa(target) + " "), row
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
            suffix = {"whole": "", "half": "half", "quarter": "quarter"}[what]
            assert (suffix in row["thing"]) if suffix else ("half" not in row["thing"] and "quarter" not in row["thing"]), row
    for row, n in MASON_META:
        got = row["answer"]
        assert (int(got.split("_")[1]) if got.startswith("clock_") else value(got)) == n, row


def main() -> None:
    _test_numbers()
    used: set[str] = set()
    files: dict[Path, str] = {}
    for level in (1, 2, 3):
        games = []
        for game in GAMES:
            sheet = game["make"](level)
            used |= check_sheet(level, game, sheet)
            files[HERE / str(level) / game["sheet"]] = sheet.text()
            entry = {k: v for k, v in game.items() if k != "make"}
            if isinstance(entry["intro_fa"], dict):
                entry["intro_fa"] = entry["intro_fa"][level]
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
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(files)} files, {len(used)} pictures")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Writes the sheets of en-1-letters (English letters: the whole alphabet).

    python3 content/english/1-letters/generate.py

Like the math packs, this pack is generated: 26 letters times a dozen
question forms is a table, and a table written by hand goes wrong. Change a
key word, a Dari explanation or a letter set HERE and run the script again;
it rewrites every CSV of this folder and content/i18n/english_letters.csv.
Do not hand-edit those CSVs: the next run would undo it.

The script also checks its own output and prints the tables that SOURCES.md
quotes: how often a spoken question occurs, how often an answer is right,
and how the speech phonemizer (espeak-ng, which the piper voices use) reads
every English line that names a letter.
"""
from __future__ import annotations

import csv
import random
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTENT = HERE.parents[1]
I18N = CONTENT / "i18n" / "english_letters.csv"
PICTURES = CONTENT / "pictures"
RNG = random.Random(26)


# --------------------------------------------------------------------------
# Dari with its English twin. Every Dari text of the pack is a B, so that the
# i18n file can never miss a line.

class B:
    def __init__(self, fa: str, en: str):
        self.fa, self.en = " ".join(fa.split()), " ".join(en.split())

    def __add__(self, other: "B") -> "B":
        return B(self.fa + " " + other.fa, self.en + " " + other.en)

    def __str__(self) -> str:
        return self.fa


TWINS: dict[str, str] = {}


def fa(text) -> str:
    """Cell text for a Dari column; remembers the English twin."""
    if text is None or text == "":
        return ""
    assert isinstance(text, B), f"Dari without English: {text!r}"
    assert not re.search(r"[A-Za-z]", text.fa), f"Latin letters in spoken Dari: {text.fa}"
    old = TWINS.setdefault(text.fa, text.en)
    assert old == text.en, f"two English twins for {text.fa!r}: {old!r} / {text.en!r}"
    return text.fa


def q(fa_text: str) -> str:
    return "«" + fa_text + "»"


# --------------------------------------------------------------------------
# The letters

ALPHA = "abcdefghijklmnopqrstuvwxyz"

# Seven sets, taught in turn. Why this order: see SOURCES.md.
SETS = [list("atsp"), list("nceg"), list("dohm"), list("ibrf"), list("ulkw"), list("jyv"), list("xqz")]
ORDINAL = [B("اول", "first"), B("دوم", "second"), B("سوم", "third"), B("چهارم", "fourth"),
           B("پنجم", "fifth"), B("ششم", "sixth"), B("هفتم", "seventh")]
SET_OF = {l: i for i, s in enumerate(SETS) for l in s}

SAME = B("همان شکل، فقط خُردتر", "the same shape, only smaller")

# letter: (capital shape, small shape, sound hint)
SHAPES = {
    "a": (B("دو خط کج که بالا به هم می‌رسند، با یک خط خُرد در میان، مثل خیمه",
            "two slanting lines that meet at the top, with a small line in the middle, like a tent"),
          B("یک دایره خُرد با یک خط کوتاه طرف راست", "a small circle with a short line on the right"),
          B("صدای آن مثل اول «انار» است، با دهن باز",
            "it sounds like the start of the Dari word anar (pomegranate), with the mouth open")),
    "b": (B("یک خط ایستاده با دو شکم طرف راست", "a standing line with two bellies on the right"),
          B("یک خط بلند ایستاده و بعد یک شکم پایین، طرف راست",
            "a tall standing line and then one belly at the bottom, on the right"),
          B("صدای آن مثل اول «بز» است", "it sounds like the start of the Dari word buz (goat)")),
    "c": (B("یک دایره که طرف راستش باز است، مثل مهتاب نو", "a circle that is open on the right, like a new moon"),
          SAME,
          B("صدای آن مثل اول «کتاب» است", "it sounds like the start of the Dari word kitab (book)")),
    "d": (B("یک خط ایستاده با یک شکم کلان طرف راست", "a standing line with one large belly on the right"),
          B("اول یک شکم خُرد و بعد یک خط بلند ایستاده؛ شکم طرف چپ است",
            "first a small belly and then a tall standing line; the belly is on the left"),
          B("صدای آن مثل اول «دروازه» است", "it sounds like the start of the Dari word darwaza (door)")),
    "e": (B("یک خط ایستاده با سه خط خوابیده طرف راست", "a standing line with three lying lines on the right"),
          B("یک خط خوابیده خُرد که یک دایره باز دورش می‌چرخد",
            "a small lying line with an open circle turning around it"),
          B("صدای آن کوتاه است، مثل اول «امروز»", "its sound is short, like the start of the Dari word imroz (today)")),
    "f": (B("یک خط ایستاده با دو خط خوابیده طرف راست، یکی بالا و یکی در میان",
            "a standing line with two lying lines on the right, one at the top and one in the middle"),
          B("یک خط بلند که سرش خم است، با یک خط خُرد در میان",
            "a tall line with a bent head and a small line across the middle"),
          B("صدای آن مثل اول «فیل» است", "it sounds like the start of the Dari word fil (elephant)")),
    "g": (B("یک دایره باز، با یک خط خُرد که به داخل می‌آید", "an open circle with a small line that comes inside"),
          B("یک دایره با یک دُم که پایین خط می‌رود و طرف چپ خم می‌شود",
            "a circle with a tail that goes below the line and bends to the left"),
          B("صدای آن مثل اول «گل» است", "it sounds like the start of the Dari word gul (flower)")),
    "h": (B("دو خط ایستاده با یک خط خوابیده در میان، مثل زینه", "two standing lines with a lying line between them, like a ladder"),
          B("یک خط بلند ایستاده با یک کمان خُرد طرف راست، مثل چوکی",
            "a tall standing line with a small arch on the right, like a chair"),
          B("صدای آن مثل اول «هفت» است", "it sounds like the start of the Dari word haft (seven)")),
    "i": (B("یک خط راست ایستاده، با دو خط خُرد بالا و پایین", "one straight standing line, with two small lines at the top and bottom"),
          B("یک خط کوتاه ایستاده با یک نقطه بالای آن", "a short standing line with a dot above it"),
          B("صدای آن بسیار کوتاه است، مثل اول «اینجا» اما کوتاه‌تر",
            "its sound is very short, like the start of the Dari word inja (here) but shorter")),
    "j": (B("یک خط ایستاده که پایینش طرف چپ خم می‌شود، مثل چنگک", "a standing line that bends to the left at the bottom, like a hook"),
          B("یک چنگک که پایین خط می‌رود، با یک نقطه بالای آن", "a hook that goes below the line, with a dot above it"),
          B("صدای آن مثل اول «جوی» است", "it sounds like the start of the Dari word joy (stream)")),
    "k": (B("یک خط ایستاده و دو خط کج که از میان آن طرف راست می‌روند",
            "a standing line and two slanting lines that go from its middle to the right"),
          B("یک خط بلند ایستاده با دو خط کج خُرد طرف راست", "a tall standing line with two small slanting lines on the right"),
          B("صدای آن مثل اول «کلید» است", "it sounds like the start of the Dari word kilid (key)")),
    "l": (B("یک خط ایستاده و یک خط خوابیده در پایین، طرف راست", "a standing line and a lying line at the bottom, on the right"),
          B("فقط یک خط بلند ایستاده، بدون نقطه", "only one tall standing line, without a dot"),
          B("صدای آن مثل اول «لب» است", "it sounds like the start of the Dari word lab (lip)")),
    "m": (B("دو خط ایستاده و در میان‌شان دو خط کج که پایین می‌آیند، مثل دو کوه", "two standing lines and between them two slanting lines that come down, like two mountains"),
          B("یک خط کوتاه با دو کمان، مثل دو پل", "a short line with two arches, like two bridges"),
          B("صدای آن مثل اول «مادر» است", "it sounds like the start of the Dari word madar (mother)")),
    "n": (B("دو خط ایستاده با یک خط کج در میان", "two standing lines with one slanting line between them"),
          B("یک خط کوتاه با یک کمان، مثل یک پل", "a short line with one arch, like one bridge"),
          B("صدای آن مثل اول «نان» است", "it sounds like the start of the Dari word nan (bread)")),
    "o": (B("یک دایره بسته، مثل تخم مرغ", "a closed circle, like an egg"),
          SAME,
          B("صدای آن مثل اول «آفتاب» است، اما کوتاه", "it sounds like the start of the Dari word aftab (sun), but short")),
    "p": (B("یک خط ایستاده با یک شکم بالا، طرف راست", "a standing line with one belly at the top, on the right"),
          B("یک خط که پایین خط می‌رود، با یک شکم طرف راست", "a line that goes below the line, with a belly on the right"),
          B("صدای آن مثل اول «پدر» است", "it sounds like the start of the Dari word padar (father)")),
    "q": (B("یک دایره با یک دُم خُرد در پایین، طرف راست", "a circle with a small tail at the bottom, on the right"),
          B("یک شکم طرف چپ و یک خط که پایین خط می‌رود", "a belly on the left and a line that goes below the line"),
          B("دو صدا را زود پشت هم می‌گوید: اول مثل اول «کتاب» و بعد مثل اول «ورق»",
            "it says two sounds quickly one after the other: first like the start of kitab (book), then like the start of waraq (sheet of paper)")),
    "r": (B("یک خط ایستاده با یک شکم بالا و یک پای کج", "a standing line with a belly at the top and a slanting leg"),
          B("یک خط کوتاه با یک شاخچه خُرد طرف راست", "a short line with a small twig on the right"),
          B("صدای آن مثل اول «روز» است", "it sounds like the start of the Dari word roz (day)")),
    "s": (B("مثل مار که دو بار پیچ خورده", "like a snake that bends twice"),
          SAME,
          B("صدای آن مثل اول «سیب» است", "it sounds like the start of the Dari word seb (apple)")),
    "t": (B("یک خط ایستاده با یک خط خوابیده بر سر آن", "a standing line with a lying line on top of it"),
          B("یک خط ایستاده با یک خط خُرد که از میان آن می‌گذرد", "a standing line with a small line that crosses it"),
          B("صدای آن مثل اول «توت» است", "it sounds like the start of the Dari word tut (mulberry)")),
    "u": (B("مثل پیاله: پایین گرد و بالا باز", "like a cup: round at the bottom and open at the top"),
          B("یک پیاله خُرد با یک خط کوتاه طرف راست", "a small cup with a short line on the right"),
          B("صدای آن کوتاه است، مثل اول «اگر»، با دهن کم‌باز",
            "its sound is short, like the start of the Dari word agar (if), with the mouth only a little open")),
    "v": (B("دو خط کج که پایین به هم می‌رسند؛ پایین آن تیز است", "two slanting lines that meet at the bottom; its bottom is pointed"),
          SAME,
          B("برای صدای آن دندان‌های بالا را روی لب پایین بمان، مثل اول «فیل» اما با آواز",
            "for its sound put the upper teeth on the lower lip, like the start of fil (elephant) but with the voice")),
    "w": (B("دو شکل تیز پهلوی هم، مثل دو دره", "two pointed shapes side by side, like two valleys"),
          SAME,
          B("صدای آن مثل اول «ورق» است، با لب‌های گرد", "it sounds like the start of the Dari word waraq (sheet of paper), with round lips")),
    "x": (B("دو خط کج که یکدیگر را قطع می‌کنند، مثل نشان ضرب", "two slanting lines that cross each other, like the times sign"),
          SAME,
          B("دو صدا را زود پشت هم می‌گوید، مثل آخر «عکس»", "it says two sounds quickly one after the other, like the end of the Dari word aks (photo)")),
    "y": (B("دو خط کج که در میان به هم می‌رسند، و یک خط که از آنجا پایین می‌رود", "two slanting lines that meet in the middle, and a line that goes down from there"),
          B("دو خط کج؛ یکی دراز است و پایین خط می‌رود", "two slanting lines; one is long and goes below the line"),
          B("صدای آن مثل اول «یک» است", "it sounds like the start of the Dari word yak (one)")),
    "z": (B("یک خط خوابیده، یک خط کج و باز یک خط خوابیده، مثل راه پیچ‌دار", "a lying line, a slanting line and again a lying line, like a winding road"),
          SAME,
          B("صدای آن مثل اول «زمین» است", "it sounds like the start of the Dari word zamin (ground)")),
}
CAP = {l: v[0] for l, v in SHAPES.items()}
SM = {l: v[1] for l, v in SHAPES.items()}
SND = {l: v[2] for l, v in SHAPES.items()}

# Pictured words by first letter: (english, picture, dari). The first one is
# the key word of the letter. Words up to the bar are known from en-1 / en-2;
# the comment NEW marks words this pack introduces.
WORDS = {
    "a": [("apple", "apple", "سیب"), ("ant", "ant", "مورچه"), ("almond", "almond", "بادام"), ("apricot", "apricot", "زردآلو")],  # ant NEW
    "b": [("bag", "bag", "بکس"), ("book", "book", "کتاب"), ("ball", "ball", "توپ"), ("bed", "bed", "تخت خواب"),
          ("bread", "bread", "نان"), ("bucket", "bucket", "سطل"), ("broom", "broom", "جاروب"), ("basket", "basket", "سبد"),
          ("baby", "baby", "طفل خُرد"), ("boy", "boy", "پسر")],
    "c": [("cat", "cat", "پشک"), ("cow", "cow", "گاو"), ("cup", "cup", "پیاله"), ("comb", "comb", "شانه"),
          ("camel", "camel", "شتر"), ("carrot", "carrot", "زردک"), ("corn", "corn", "جواری"), ("calf", "calf", "گوساله")],
    "d": [("dog", "dog", "سگ"), ("door", "door", "دروازه"), ("donkey", "donkey", "خر"), ("drum", "drum", "دهل")],  # drum NEW
    "e": [("egg", "egg", "تخم مرغ"), ("elephant", "elephant", "فیل"), ("eggplant", "eggplant", "بادنجان سیاه")],  # elephant, eggplant NEW
    "f": [("fish", "fish", "ماهی"), ("foot", "foot", "پای"), ("flower", "flower", "گل"), ("father", "father", "پدر"),
          ("finger", "finger", "انگشت"), ("fox", "fox", "روباه"), ("fire", "fire", "آتش"), ("family", "family", "فامیل")],  # fox, fire NEW
    "g": [("goat", "goat", "بز"), ("girl", "girl", "دختر"), ("grapes", "grapes", "انگور"), ("garlic", "garlic", "سیر"),
          ("grandmother", "grandmother", "مادرکلان"), ("grandfather", "grandfather", "پدرکلان")],  # garlic NEW
    "h": [("hen", "hen", "مرغ"), ("hand", "hand", "دست"), ("horse", "horse", "اسپ"), ("house", "house", "خانه"),
          ("honey", "honey", "عسل"), ("hair", "hair", "موی"), ("hat", "hat", "کلاه"), ("hammer", "hammer", "چکش")],  # hat, hammer NEW
    "i": [("ink", "ink", "سیاهی قلم"), ("in", "pos_in", "در داخل")],  # both NEW
    "j": [("jug", "water_jug", "کوزه"), ("jar", "jar", "مرتبان"), ("juice", "juice", "آب میوه")],  # all NEW
    "k": [("key", "key", "کلید"), ("kite", "kite", "کاغذپران"), ("kebab", "kebab", "کباب")],  # kite, kebab NEW
    "l": [("leg", "leg", "لنگ"), ("leaf", "leaf", "برگ"), ("lamb", "lamb", "بره"), ("lemon", "lemon", "لیمو"),
          ("lamp", "lamp", "چراغ"), ("lock", "lock", "قفل"), ("lion", "lion", "شیر درنده")],  # lemon, lamp, lock, lion NEW
    "m": [("moon", "moon", "مهتاب"), ("milk", "milk", "شیر"), ("meat", "meat", "گوشت"), ("mouse", "mouse", "موش"),
          ("mother", "mother", "مادر"), ("mountain", "mountain", "کوه"), ("mouth", "mouth", "دهن"), ("mirror", "mirror", "آیینه")],  # mirror NEW
    "n": [("nose", "nose", "بینی"), ("nest", "nest", "آشیانه"), ("needle", "needle", "سوزن"), ("nail", "nail", "ناخن")],  # nest, needle, nail NEW
    "o": [("orange", "orange", "مالته"), ("onion", "onion", "پیاز"), ("on", "pos_on", "روی"), ("open", "open", "باز کن")],  # on NEW
    "p": [("pen", "pen", "قلم"), ("pencil", "pencil", "پنسل"), ("pot", "pot", "دیگ"), ("plate", "plate", "بشقاب"),
          ("pillow", "pillow", "بالشت"), ("potato", "potato", "کچالو"), ("pear", "pear", "ناک"), ("pumpkin", "pumpkin", "کدو"),
          ("parrot", "parrot", "طوطی")],  # pear, pumpkin, parrot NEW
    "q": [("quilt", "quilt", "لحاف")],  # NEW
    "r": [("rope", "rope", "ریسمان"), ("rice", "rice", "برنج"), ("river", "river", "دریا"), ("rain", "rain", "باران"),
          ("radio", "radio", "رادیو"), ("rooster", "rooster", "خروس")],  # rain, radio, rooster NEW
    "s": [("sun", "sun", "آفتاب"), ("star", "star", "ستاره"), ("stone", "stone", "سنگ"), ("soap", "soap", "صابون"),
          ("spoon", "spoon", "قاشق"), ("snake", "snake", "مار"), ("sugar", "sugar", "بوره")],  # snake NEW
    "t": [("table", "table", "میز"), ("tea", "tea", "چای"), ("tree", "tree", "درخت"), ("tooth", "tooth", "دندان"),
          ("tomato", "tomato", "بادنجان رومی"), ("tent", "tent", "خیمه"), ("train", "train", "ریل"), ("tap", "tap", "نل")],  # tent, train, tap NEW
    "u": [("umbrella", "umbrella", "چتری"), ("up", "arrow_up", "بالا")],  # both NEW
    "v": [("village", "scene_village", "قریه"), ("van", "van", "موتر مسافربری")],  # van NEW
    "w": [("water", "water", "آب"), ("window", "window", "کلکین"), ("well", "well", "چاه"), ("watermelon", "watermelon", "تربوز"),
          ("walnut", "walnut", "چهارمغز"), ("wall", "wall", "دیوار"), ("wolf", "wolf", "گرگ")],  # wall, wolf NEW
    "x": [],  # no word the children know begins with x: it is taught at the end of box, fox, six
    "y": [("yoghurt", "yoghurt", "ماست"), ("yes", "yes", "بلی"), ("yellow", "color_yellow", "زرد"), ("you", "you", "تو")],
    "z": [("zebra", "zebra", "گوره‌خر"), ("zip", "zip", "زنجیرک")],  # both NEW
}
X_WORDS = [("box", "box", "صندوق"), ("fox", "fox", "روباه"), ("six", "t:6", "شش")]
KEY = {l: (w[0] if w else X_WORDS[0]) for l, w in WORDS.items()}

# Heard only (no picture needed): for the sound game. (english, dari)
HEARD = {
    "a": [("animal", "حیوان"), ("and", "و")], "b": [("big", "کلان"), ("blue", "آبی"), ("black", "سیاه")],
    "c": [("count", "حساب کن"), ("clap", "چک چک کن"), ("class", "صنف")], "d": [("draw", "رسم کن"), ("door", "دروازه")],
    "e": [("eleven", "یازده"), ("egg", "تخم مرغ")], "f": [("four", "چهار"), ("five", "پنج"), ("friend", "دوست")],
    "g": [("go", "برو"), ("give", "بده"), ("green", "سبز")], "h": [("hello", "سلام"), ("happy", "خوش")],
    "i": [("is", "است"), ("it", "آن")], "j": [("juice", "آب میوه"), ("jar", "مرتبان")],
    "k": [("kebab", "کباب"), ("kite", "کاغذپران")], "l": [("look", "ببین"), ("listen", "گوش کن")],
    "m": [("my", "از من"), ("morning", "صبح")], "n": [("no", "نه"), ("nine", "نُه"), ("name", "نام")],
    "o": [("on", "روی"), ("onion", "پیاز")], "p": [("please", "لطفاً"), ("point", "نشان بده"), ("parents", "پدر و مادر")],
    "q": [("question", "سوال"), ("quick", "تیز")], "r": [("red", "سرخ"), ("read", "بخوان")],
    "s": [("six", "شش"), ("seven", "هفت"), ("sad", "غمگین")], "t": [("ten", "ده"), ("two", "دو"), ("teacher", "معلم")],
    "u": [("under", "زیر"), ("up", "بالا")], "v": [("vegetables", "ترکاری"), ("van", "موتر مسافربری")],
    "w": [("white", "سفید"), ("write", "بنویس")], "y": [("yes", "بلی"), ("you", "تو")],
    "z": [("zero", "صفر"), ("zip", "زنجیرک")], "x": [],
}

# Letters that are easily taken for one another. Wrong choices come from here
# first, so that a wrong answer is a plausible one.
ALIKE = {
    "a": "oed", "b": "dph", "c": "eos", "d": "bpa", "e": "coa", "f": "tlk", "g": "qjy", "h": "nbk", "i": "ljt",
    "j": "igy", "k": "hxl", "l": "itk", "m": "nwh", "n": "mhu", "o": "cae", "p": "qbd", "q": "pgd", "r": "ntf",
    "s": "zcx", "t": "fli", "u": "vnw", "v": "uwy", "w": "vmu", "x": "kzy", "y": "vgj", "z": "sxn",
}
ALIKE_CAP = {
    "a": "hvn", "b": "prd", "c": "gos", "d": "obp", "e": "fbl", "f": "ept", "g": "cqo", "h": "ank", "i": "ltj",
    "j": "iul", "k": "xhr", "l": "ite", "m": "wnh", "n": "mhz", "o": "qcd", "p": "rbf", "q": "ogc", "r": "pbk",
    "s": "zcg", "t": "ifl", "u": "vjo", "v": "uwy", "w": "mvn", "x": "kyz", "y": "vxt", "z": "nsx",
}
# Same sound, different letter: never offered against each other in a game
# that goes by the sound.
SAME_SOUND = {"c": "kq", "k": "cq", "q": "ck", "s": "", "x": ""}


def form(letter: str, kind: str) -> str:
    """A letter as a thing: cap 't:A', small 't:a', both 't:Aa'."""
    return "t:" + {"cap": letter.upper(), "small": letter, "both": letter.upper() + letter}[kind]


def wrong_letters(letter: str, pool: list[str], kind: str, n: int = 3, by_sound: bool = False) -> list[str]:
    """n wrong letters: look-alikes that are in the pool first, then the rest of the pool."""
    alike = (ALIKE_CAP if kind == "cap" else ALIKE)[letter]
    banned = set(letter) | (set(SAME_SOUND.get(letter, "")) if by_sound else set())
    out = [c for c in alike if c in pool and c not in banned]
    rest = [c for c in pool if c not in banned and c not in out]
    RNG.shuffle(rest)
    out += rest
    for c in alike:  # a small pool: fall back on any look-alike
        if len(out) >= n:
            break
        if c not in banned and c not in out:
            out.append(c)
    return out[:n]


def things(letters: list[str], kind: str) -> str:
    return "|".join(form(c, kind) for c in letters)


def upto(k: int) -> list[str]:
    """All letters of sets 0..k."""
    return [c for s in SETS[: k + 1] for c in s]


def meaning(word_fa: str) -> B:
    return B(f"این کلمه یعنی {q(word_fa)}.", f"This word means {EN_OF[word_fa]}.")


EN_OF: dict[str, str] = {}
for _l, _ws in list(WORDS.items()) + [("x", X_WORDS)]:
    for _en, _pic, _fa in _ws:
        EN_OF[_fa] = _en
for _l, _ws in HEARD.items():
    for _en, _fa in _ws:
        EN_OF.setdefault(_fa, _en)
EN_OF.update({"باز کن": "open", "تو": "you", "شیر درنده": "lion", "از من": "my", "و": "and", "آن": "it", "است": "is"})


# --------------------------------------------------------------------------
# Bookkeeping: what is spoken, what is right, what the voice has to say

SPOKEN: list[tuple[str, str, str]] = []        # (game, round, normalised question)
RIGHT: list[tuple[str, str, str]] = []         # (game, round, answer)
NAMES: list[tuple[str, str]] = []              # (english text, letters it must name, in order)
ROWS: dict[str, list[dict]] = defaultdict(list)
REVIEW_ROUNDS = {("spell_it", "04")}           # deliberate review: may repeat a question


def norm(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9؀-ۿ ]+", " ", text.lower()).split())


def say(en: str, names: str = "") -> str:
    """English speech. `names`: the letters whose NAMES the voice must say, in order."""
    if names:
        NAMES.append((en, names))
    return en


def row(game: str, rnd: str, question: bool = True, right: str = "", **cells) -> None:
    cells = {k: (fa(v) if isinstance(v, B) else v) for k, v in cells.items()}
    cells["round"] = rnd
    if "choices" in cells:  # a story decision: `right` is also a column
        cells["right"] = right
    if question:
        SPOKEN.append((game, rnd, norm(cells.get("say_fa", "") + " | " + cells.get("say_en", ""))))
    if right:
        RIGHT.append((game, rnd, right))
    ROWS[game].append(cells)


def intro(game: str, rnd: str, text: B) -> None:
    """Put the round's spoken introduction on its first row."""
    for r in ROWS[game]:
        if r["round"] == rnd:
            r["intro_fa"] = fa(text)
            return
    raise AssertionError(f"no rows for {game} {rnd}")


def nn(k: int) -> str:
    return f"{k + 1:02d}"


# --------------------------------------------------------------------------
# a  Meet the Letters (story): every set is introduced before it is asked

LEADS = [B("حرف نو را ببین.", "Look at the new letter."), B("این هم یک حرف نو.", "Here is another new letter."),
         B("حالا این حرف.", "Now this letter."), B("حرف بعدی را ببین.", "Look at the next letter.")]
ASK_NAME = [B("نام کدام حرف را می‌شنوی؟ آن را انتخاب کن.", "Which letter's name do you hear? Choose it."),
            B("گوش کن و همان حرف را بگیر.", "Listen and take that letter."),
            B("حرفی را که نامش را می‌شنوی نشان بده.", "Show the letter whose name you hear."),
            B("کدام یک است؟ گوش کن.", "Which one is it? Listen.")]
ASK_FIRST = [B("این کلمه با کدام حرف شروع می‌شود؟", "Which letter does this word begin with?"),
             B("حرف اول این کلمه کدام است؟", "Which is the first letter of this word?"),
             B("تصویر را ببین و کلمه را بشنو. حرف اول آن را انتخاب کن.", "Look at the picture and hear the word. Choose its first letter.")]
RECAP = [B("آفرین! چهار حرف اول را یاد گرفتی. یک بار دیگر نام‌هایشان را بشنو:", "Well done! You have learned the first four letters. Hear their names once more:"),
         B("شاباش! حالا هشت حرف را می‌شناسی. نام چهار حرف امروز:", "Bravo! Now you know eight letters. The names of today's four:"),
         B("بسیار خوب! دوازده حرف شد. چهار حرف امروز را دوباره بشنو:", "Very good! That makes twelve letters. Hear today's four again:"),
         B("آفرین! شانزده حرف را یاد گرفتی، بیشتر از نیم الفبا. حرف‌های امروز:", "Well done! You have learned sixteen letters, more than half the alphabet. Today's letters:"),
         B("شاباش! بیست حرف شد. تنها شش حرف مانده است. حرف‌های امروز:", "Bravo! That makes twenty letters. Only six are left. Today's letters:"),
         B("بسیار خوب! بیست و سه حرف را می‌شناسی. سه حرف امروز:", "Very good! You know twenty-three letters. Today's three:"),
         B("آفرین! حالا تمام بیست و شش حرف انگلیسی را می‌شناسی. سه حرف آخر:", "Well done! Now you know all twenty-six English letters. The last three:")]


def wrong_shape(letter: str) -> B:
    return B("نه. حرف درست این شکل را دارد:", "No. The right letter has this shape:") + CAP[letter] + B(". دوباره انتخاب کن.", ". Choose again.")


def story() -> None:
    g = "meet_letters"
    r = "00"
    P = lambda **c: row(g, r, question=False, **c)
    P(picture="t:A B C", say_fa=B("سلام! امروز با حرف‌های انگلیسی آشنا می‌شویم. دری سی و دو حرف دارد. انگلیسی بیست و شش حرف دارد. سه حرف اول آن:",
                               "Hello! Today we get to know the English letters. Dari has thirty-two letters. English has twenty-six. Its first three:"),
      say_en=say("A, B, C.", "ABC"))
    P(picture="arrow_right", say_fa=B("دری از راست به چپ نوشته می‌شود. انگلیسی برعکس است: از چپ شروع می‌شود و طرف راست می‌رود، مثل این تیر.",
                                   "Dari is written from right to left. English is the other way round: it starts on the left and goes to the right, like this arrow."))
    row(g, r, picture="arrow_right", say_fa=B("نوشتهٔ انگلیسی به کدام طرف می‌رود؟ تیر درست را انتخاب کن.", "Which way does English writing go? Choose the right arrow."),
        choices="arrow_left|arrow_right", right="arrow_right",
        wrong_say_fa=B("نه. این راه دری است. انگلیسی از چپ شروع می‌شود و طرف راست می‌رود.", "No. That is the way of Dari. English starts on the left and goes to the right."))
    P(picture="t:cat", say_fa=B("حرف‌های دری به هم می‌چسپند. حرف‌های انگلیسی به هم نمی‌چسپند: هر کدام جدا، پهلوی دیگر می‌ایستد. این کلمه سه حرف دارد و معنای آن پشک است:",
                             "Dari letters join one another. English letters do not join: each stands alone, next to the other. This word has three letters and means cat:"),
      say_en="cat")
    P(picture="t:A a", say_fa=B("هر حرف انگلیسی دو شکل دارد: یک شکل کلان و یک شکل خُرد. این هر دو یک حرف است و یک نام دارد. در دری حرف کلان و خُرد نداریم.",
                             "Every English letter has two shapes: a big one and a small one. These two are one letter with one name. Dari has no big and small letters."),
      say_en=say("Big A. Small a.", "AA"))
    P(picture="t:Sara", say_fa=B("حرف کلان را در اول نام آدم‌ها و در اول هر جمله می‌نویسیم. باقی حرف‌ها خُرد است. این یک نام است: تنها حرف اول آن کلان است.",
                              "We write the big letter at the start of people's names and at the start of every sentence. The other letters are small. This is a name: only its first letter is big."),
      say_en="Sara")
    row(g, r, picture="t:Sara", say_fa=B("کدام یک حرف کلان است؟", "Which one is a big letter?"), choices="t:b|t:B", right="t:B",
        wrong_say_fa=B("نه، این خُرد است. حرف کلان بلندتر است و دو شکم دارد.", "No, this one is small. The big letter is taller and has two bellies."))
    P(picture="t:Bb", say_fa=B("هر حرف یک نام دارد و یک صدا، و این دو یکی نیست. اول نام این حرف را بشنو:",
                            "Every letter has a name and a sound, and the two are not the same. First hear the name of this letter:"),
      say_en=say("B.", "B"))
    P(picture="bag", say_fa=B("صدای آن کوتاه‌تر است، مثل اول «بز». صدا را در اول این سه کلمه بشنو:",
                           "Its sound is shorter, like the start of the Dari word buz (goat). Hear the sound at the start of these three words:"),
      say_en="bag. ball. book.")
    P(picture="t:a e i o u", say_fa=B("در دری صداهای کوتاه مثل زبر و زیر و پیش را نمی‌نویسیم. در انگلیسی آن‌ها را هم می‌نویسیم. برای این، پنج حرف است که تقریباً در هر کلمه یکی از آن‌ها را می‌بینی:",
                                   "In Dari we do not write the short sounds, like zabar, zer and pesh. In English we write them too. For this there are five letters, and you see one of them in almost every word:"),
      say_en=say("A, E, I, O, U.", "AEIOU"))
    row(g, r, picture="t:Bb", say_fa=B("نام یک حرف و صدای آن یکی است؟", "Are the name of a letter and its sound the same?"), choices="no|yes", right="no",
        wrong_say_fa=B("نه، یکی نیست. نام را وقتی می‌گوییم که الفبا را می‌خوانیم. صدا را وقتی می‌گوییم که یک کلمه را می‌خوانیم.",
                       "No, they are not the same. We say the name when we say the alphabet. We say the sound when we read a word."))
    P(picture="t:Aa Tt Ss Pp", say_fa=B("حالا آماده هستی. هر بار چند حرف نو یاد می‌گیریم: اول نام و شکل، بعد صدا و یک کلمه. در هر بازی می‌توانی سوال را دوباره بشنوی و کمک بخواهی.",
                                     "Now you are ready. Each time we learn a few new letters: first the name and shape, then the sound and a word. In every game you can hear the question again and ask for help."))
    intro(g, r, B("انگلیسی چطور نوشته می‌شود؟ سه فرق با دری: از چپ به راست، دو شکل برای هر حرف، و نام و صدای جدا. گوش کن و ببین.",
                  "How is English written? Three differences from Dari: from left to right, two shapes for every letter, and a name and a sound that differ. Listen and look."))

    lead = 0
    for k, letters in enumerate(SETS):
        r = nn(k)
        asked = 0
        for j, l in enumerate(letters):
            L = l.upper()
            word, pic, wfa = KEY[l]
            first = B("این اولین حرف الفبا است.", "This is the first letter of the alphabet.") if l == "a" else \
                B("این آخرین حرف الفبا است.", "This is the last letter of the alphabet.") if l == "z" else LEADS[lead % len(LEADS)]
            lead += 1
            row(g, r, question=False, picture=form(l, "both"),
                say_fa=first + B("طرف چپ کلان آن است:", "On the left is its big shape:") + CAP[l]
                + B(". طرف راست خُرد آن:", ". On the right its small shape:") + SM[l] + B(". نام آن:", ". Its name:"),
                say_en=say(f"{L}. The letter {L}.", L + L))
            if l == "x":
                row(g, r, question=False, picture=pic,
                    say_fa=SND[l] + B(". این حرف کم در اول کلمه می‌آید. آن را در آخر این کلمه بشنو، که معنایش «صندوق» است:",
                                      ". This letter seldom comes at the start of a word. Hear it at the end of this word, which means box:"),
                    say_en=say(f"box. {L}, box.", L))
            else:
                extra = B(". بعد از این حرف همیشه یک حرف دیگر می‌آید که مثل پیاله است", ". After this letter there always comes another letter, the one like a cup") if l == "q" else B("", "")
                row(g, r, question=False, picture=pic,
                    say_fa=SND[l] + extra + B(f". این کلمه با آن شروع می‌شود و معنایش {q(wfa)} است:", f". This word begins with it and means {word}:"),
                    say_en=say(f"{word}. {L}, {word}.", L))
            # a question after every second letter, and after the last one
            if j % 2 == 1 or j == len(letters) - 1:
                seen = letters[: j + 1]
                if asked % 2 == 0:
                    target = seen[-2] if len(seen) >= 2 else seen[-1]
                    choices = [form(c, "both") for c in seen[-2:]]
                    if (k + asked) % 2 == 0:
                        choices.reverse()
                    row(g, r, picture="listen", say_fa=ASK_NAME[(k + asked) % len(ASK_NAME)],
                        say_en=say(f"{target.upper()}.", target.upper()), choices="|".join(choices), right=form(target, "both"),
                        wrong_say_fa=wrong_shape(target))
                else:
                    target = seen[-1] if seen[-1] != "x" else seen[0]
                    word, pic, wfa = KEY[target]
                    choices = [form(c, "both") for c in seen[-3:]]
                    if form(target, "both") not in choices:
                        choices[0] = form(target, "both")
                    choices = choices[1:] + choices[:1] if k % 2 else choices
                    row(g, r, picture=pic, say_fa=ASK_FIRST[(k + asked) % len(ASK_FIRST)], say_en=word,
                        choices="|".join(choices), right=form(target, "both"), wrong_say_fa=wrong_shape(target))
                asked += 1
        names = ", ".join(c.upper() for c in letters) + "."
        row(g, r, question=False, picture="t:" + " ".join(c.upper() + c for c in letters), say_fa=RECAP[k],
            say_en=say(names, "".join(c.upper() for c in letters)))
        count = B("چهار", "four") if len(letters) == 4 else B("سه", "three")
        intro(g, r, B("دستهٔ", "Set") + ORDINAL[k] + B(":", ":") + count
              + B("حرف نو. از هر حرف اول نام و شکل کلان و خُرد آن را می‌بینی، بعد صدای آن را در یک کلمه می‌شنوی. در میان، سوال هم است.",
                  "new letters. Of each letter you first see the name and its big and small shape, then you hear its sound in a word. There are questions in between."))


# --------------------------------------------------------------------------
# b  Letter Stall (listen_pick): hear the name, pick the letter; rounds 08-10
#    go from the big letter to the small one and back

def letter_names() -> None:
    g = "letter_names"
    for k, letters in enumerate(SETS):
        r = nn(k)
        pool = letters if len(letters) >= 4 else letters + SETS[k - 1]
        for l in letters:
            L = l.upper()
            word, pic, wfa = KEY[l]
            row(g, r, say_en=say(f"the letter {L}", L), answer=form(l, "cap"), right=form(l, "cap"),
                distractors=things(wrong_letters(l, pool, "cap"), "cap"),
                help_fa=B("حرف کلان را بگیر:", "Take the big letter:") + CAP[l] + B(".", "."))
            row(g, r, say_en=say(f"small {l}", L), answer=form(l, "small"), right=form(l, "small"),
                distractors=things(wrong_letters(l, pool, "small"), "small"),
                help_fa=B("حرف خُرد را بگیر:", "Take the small letter:") + SM[l] + B(".", "."))
            tail = "at the end of box" if l == "x" else f"as in {word}"
            row(g, r, say_en=say(f"{L}, {tail}", L), answer=form(l, "both"), right=form(l, "both"),
                distractors=things(wrong_letters(l, pool, "both"), "both"),
                help_fa=SND[l] + B(f". کلمه‌ای که شنیدی یعنی {q(wfa)}.", f". The word you heard means {word}."))
        # mixed with earlier sets: the set before (small), and the one before that (big)
        if k >= 1:
            for l in SETS[k - 1]:
                row(g, r, say_en=say(f"Find the letter {l.upper()}.", l.upper()), answer=form(l, "small"), right=form(l, "small"),
                    distractors=things(wrong_letters(l, upto(k), "small"), "small"),
                    help_fa=B("این حرف را پیش‌تر دیدی. خُرد آن:", "You have seen this letter before. Its small shape:") + SM[l] + B(".", "."))
        if k >= 2:
            for l in SETS[k - 2]:
                row(g, r, say_en=say(f"Now find {l.upper()}.", l.upper()), answer=form(l, "cap"), right=form(l, "cap"),
                    distractors=things(wrong_letters(l, upto(k), "cap"), "cap"),
                    help_fa=B("این حرف را پیش‌تر دیدی. کلان آن:", "You have seen this letter before. Its big shape:") + CAP[l] + B(".", "."))
        more = B("حرف‌های دسته‌های پیش هم در میان است.", "Letters of the earlier sets are among them too.") if k else B("", "")
        intro(g, r, B("دستهٔ", "Set") + ORDINAL[k]
              + B(". نام حرف را بشنو و همان حرف را انتخاب کن. گاهی پیش از نام یک کلمه می‌شنوی که یعنی «خُرد»: آن وقت حرف خُرد را بگیر. گاهی یک کلمه هم با آن می‌شنوی.",
                  ". Hear the name of the letter and choose that letter. Sometimes you hear a word before the name that means small: then take the small letter. Sometimes you hear a word with it too.") + more)
    groups = [(0, 1), (2, 3), (4, 5, 6)]
    for i, grp in enumerate(groups):
        r = nn(7 + i)
        letters = [c for s in grp for c in SETS[s]]
        for l in letters:
            L = l.upper()
            same = SM[l] is SAME
            row(g, r, say_en=say(f"Find small {l}.", L), show=form(l, "cap"), answer=form(l, "small"), right=form(l, "small"),
                distractors=things(wrong_letters(l, list(ALPHA), "small"), "small"),
                help_fa=B("خُرد این حرف:", "The small shape of this letter:") + SM[l]
                + (B(". این حرف در کلان و خُرد یک شکل دارد.", ". This letter has one shape, big and small.") if same else B(". شکل آن با کلان فرق دارد.", ". Its shape differs from the big one.")))
            row(g, r, say_en=say(f"Find big {L}.", L), show=form(l, "small"), answer=form(l, "cap"), right=form(l, "cap"),
                distractors=things(wrong_letters(l, list(ALPHA), "cap"), "cap"),
                help_fa=B("کلان این حرف:", "The big shape of this letter:") + CAP[l] + B(".", "."))
        intro(g, r, [B("کلان و خُرد، هشت حرف اول. یک شکل حرف را می‌بینی. شکل دیگر همان حرف را پیدا کن: برای کلان، خُرد آن و برای خُرد، کلان آن.",
                       "Big and small, the first eight letters. You see one shape of a letter. Find the other shape of the same letter: for a big one its small one, for a small one its big one."),
                     B("کلان و خُرد، هشت حرف بعدی. بعضی حرف‌ها در کلان و خُرد یک شکل دارند، بعضی دو شکل بسیار جدا. شکل دیگر همان حرف را پیدا کن.",
                       "Big and small, the next eight letters. Some letters have one shape big and small, some two very different shapes. Find the other shape of the same letter."),
                     B("کلان و خُرد، ده حرف آخر. حرف را ببین، نام آن را بشنو و شکل دیگر آن را انتخاب کن.",
                       "Big and small, the last ten letters. Look at the letter, hear its name and choose its other shape.")][i])


# --------------------------------------------------------------------------
# c  Alphabet Echo (say_it): the alphabet in groups

def alphabet_echo() -> None:
    g = "alphabet_echo"
    groups = ["ABCD", "EFG", "HIJK", "LMNOP", "QRS", "TUV", "WXYZ"]
    notes = [B("چهار حرف اول الفبا. با انگشت‌هایت حساب کن.", "The first four letters of the alphabet. Count on your fingers."),
             B("سه حرف بعدی: پنجم، ششم و هفتم.", "The next three: the fifth, sixth and seventh."),
             B("چهار حرف. دو حرف میانی نقطه دارند.", "Four letters. The two in the middle have a dot."),
             B("پنج حرف، تیز پشت هم. این میان الفبا است.", "Five letters, quickly one after the other. This is the middle of the alphabet."),
             B("سه حرف. حرف اول این دسته همان است که دُم دارد.", "Three letters. The first of this group is the one with a tail."),
             B("سه حرف. دو حرف آخر به هم بسیار مانند هستند: یکی پایین گرد و یکی پایین تیز.", "Three letters. The last two look much alike: one round at the bottom and one pointed."),
             B("چهار حرف آخر الفبا.", "The last four letters of the alphabet.")]
    for grp, note in zip(groups, notes):
        row(g, "01", say_en=say(", ".join(grp), grp), meaning_fa=note)
    intro(g, "01", B("الفبای انگلیسی به ترتیب، در هفت دستهٔ کوتاه. گوش کن. بعد خودت بلند بگو. باز گوش کن. نام‌ها را می‌گوییم، نه صداها را.",
                     "The English alphabet in order, in seven short groups. Listen. Then say it aloud yourself. Listen again. We say the names, not the sounds."))
    for k, letters in enumerate(SETS):
        parts, means, names = [], [], ""
        for l in letters:
            word, pic, wfa = KEY[l]
            parts.append(f"{l.upper()}, {word}.")
            means.append(wfa)
            names += l.upper()
        row(g, "02", say_en=say(" ".join(parts), names), picture=KEY[letters[0]][1],
            meaning_fa=B("، ".join(means) + ".", ", ".join(EN_OF[m] for m in means) + "."))
    intro(g, "02", B("هر حرف با کلمهٔ خودش. اول نام حرف را می‌گویی، بعد کلمه‌ای را که آن حرف در آن است. گوش کن و بلند بگو.",
                     "Every letter with its own word. First you say the name of the letter, then the word that has the letter in it. Listen and say it aloud."))
    longer = [("A, B, C, D, E, F, G", "ABCDEFG", B("هفت حرف اول، بدون ایستادن.", "The first seven letters, without stopping.")),
              ("H, I, J, K, L, M, N, O, P", "HIJKLMNOP", B("نُه حرف میانی. یک نفس بگیر و بگو.", "The nine in the middle. Take a breath and say them.")),
              ("Q, R, S, T, U, V", "QRSTUV", B("شش حرف.", "Six letters.")),
              ("W, X, Y, Z. That is the alphabet.", "WXYZ", B("چهار حرف آخر. جملهٔ آخر یعنی: این الفبا است.", "The last four letters. The last sentence means: that is the alphabet.")),
              ("The vowels. A, E, I, O, U.", "AEIOU", B("پنج حرف صدادار. تقریباً در هر کلمه یکی از این‌ها است.", "The five vowels. Almost every word has one of them.")),
              ("A, B, C, D, E, F, G // H, I, J, K, L, M, N, O, P // Q, R, S, T, U, V // W, X, Y, Z", ALPHA.upper(),
               B("تمام الفبا، بیست و شش حرف، از اول تا آخر.", "The whole alphabet, twenty-six letters, from beginning to end."))]
    for text, names, note in longer:
        row(g, "03", say_en=say(text, names), meaning_fa=note)
    intro(g, "03", B("حالا دسته‌های دراز، و در آخر تمام الفبا در یک بار. شتاب نکن: هر چند بار که خواستی گوش کن.",
                     "Now the long groups, and at the end the whole alphabet in one go. Do not hurry: listen as many times as you like."))


# --------------------------------------------------------------------------
# d  Big and Small Pairs (pairs)

def big_small() -> None:
    g = "big_small"
    groups = [(0, 1), (2, 3), (4, 5, 6)]
    intros = [B("هشت حرف اول. هر حرف دو کارت دارد: یک کلان و یک خُرد. دو کارت همان حرف را پیدا کن. هر کارت که باز می‌شود، نام حرف را می‌گوید.",
                "The first eight letters. Every letter has two cards: a big one and a small one. Find the two cards of the same letter. Every card says the letter's name when it turns."),
              B("هشت حرف بعدی. کلان و خُرد یک حرف را جوره کن. اگر شکل‌ها به هم نمی‌مانند، به نام گوش کن: نام یکی است.",
                "The next eight letters. Pair the big and the small of one letter. If the shapes do not look alike, listen to the name: the name is the same."),
              B("ده حرف آخر الفبا. کلان و خُرد را جوره کن. هر بار کارت‌های دیگر می‌آید.",
                "The last ten letters of the alphabet. Pair big and small. Different cards come every time.")]
    for i, grp in enumerate(groups):
        r = nn(i)
        for l in [c for s in grp for c in SETS[s]]:
            L = l.upper()
            row(g, r, question=False, a=form(l, "cap"), b=form(l, "small"), say_en=say(f"the letter {L}, big and small", L))
        intro(g, r, intros[i])
    for i, grp in enumerate([(0, 1, 2), (3, 4, 5, 6)]):
        r = nn(3 + i)
        for l in [c for s in grp for c in SETS[s]]:
            L = l.upper()
            word, pic, wfa = KEY[l]
            text = f"box ends with {L}." if l == "x" else f"{word} begins with {L}."
            row(g, r, question=False, a=form(l, "both"), b=pic, say_en=say(text, L))
        intro(g, r, [B("حرف و تصویر، دوازده حرف اول. هر حرف را با تصویری جوره کن که نام انگلیسی آن با همان حرف شروع می‌شود.",
                       "Letter and picture, the first twelve letters. Pair every letter with the picture whose English name begins with that letter."),
                     B("حرف و تصویر، چهارده حرف دیگر. هر حرف را با تصویر خودش جوره کن. یک حرف در آخر کلمهٔ خود است، نه در اول: صندوق.",
                       "Letter and picture, the other fourteen letters. Pair every letter with its picture. One letter is at the end of its word, not at the start: the box.")][i])


# --------------------------------------------------------------------------
# e  Sound Road (journey): two words that begin alike, pick their letter

def first_sounds() -> None:
    g = "first_sounds"
    plan = [(0, 1), (2, 3), (4, 5)]
    flip = 0
    for i, grp in enumerate(plan):
        r = nn(i)
        letters = [c for s in grp for c in SETS[s]]
        for l in letters:
            ws = WORDS[l]
            pairs = []
            if len(ws) >= 2:
                pairs.append(((ws[0][0], ws[0][2]), (ws[1][0], ws[1][2]), ws[0][1]))
            hs = [h for h in HEARD[l] if h[0] not in (ws[0][0], ws[1][0] if len(ws) > 1 else "")]
            if len(ws) >= 4:
                pairs.append(((ws[2][0], ws[2][2]), (ws[3][0], ws[3][2]), ws[2][1]))
            elif len(hs) >= 2:
                pairs.append((hs[0], hs[1], ""))
            elif hs:
                pairs.append((hs[0], (ws[0][0], ws[0][2]), ""))
            for (w1, f1), (w2, f2), show in pairs:
                kind = ("small", "cap")[flip % 2]
                flip += 1
                row(g, r, say_en=f"{w1}. {w2}.", show=show, answer=form(l, kind), right=form(l, kind),
                    distractors=things(wrong_letters(l, letters, kind, by_sound=True), kind),
                    help_fa=B(f"این دو کلمه یعنی {q(f1)} و {q(f2)}. هر دو با یک حرف شروع می‌شوند.", f"These two words mean {EN_OF.get(f1, w1)} and {EN_OF.get(f2, w2)}. Both begin with the same letter.")
                    + SND[l] + B(".", "."))
        intro(g, r, [B("صدای اول، هشت حرف اول. دو کلمه می‌شنوی که با یک صدا شروع می‌شوند. حرفی را انتخاب کن که آن صدا را می‌دهد، و پیش برو.",
                       "First sounds, the first eight letters. You hear two words that begin with the same sound. Choose the letter that makes that sound, and move on."),
                     B("صدای اول، هشت حرف بعدی. به اول هر دو کلمه گوش کن: صدا یکی است. کدام حرف این صدا را می‌دهد؟",
                       "First sounds, the next eight letters. Listen to the start of both words: the sound is the same. Which letter makes this sound?"),
                     B("صدای اول، هفت حرف دیگر. دو کلمه، یک صدای اول. حرف درست را بگیر و پیش برو. اگر معنای کلمه‌ها را خواستی، کمک بخواه.",
                       "First sounds, seven more letters. Two words, one first sound. Take the right letter and move on. If you want the meaning of the words, ask for help.")][i])
    # round 04: the last three letters, the letter at the END, and three words for old letters
    r = "04"
    for (w1, w2, show) in [("box", "fox", "box"), ("six", "fox", "fox")]:
        row(g, r, say_fa=B("این دو کلمه با یک صدا تمام می‌شوند. کدام حرف در آخر آن‌ها است؟", "These two words end with the same sound. Which letter is at their end?"),
            say_en=f"{w1}. {w2}.", show=show, answer="t:x" if w1 == "box" else "t:X", right="t:x" if w1 == "box" else "t:X",
            distractors="t:s|t:k|t:z" if w1 == "box" else "t:S|t:K|t:Z",
            help_fa=B("به آخر کلمه‌ها گوش کن، نه به اول.", "Listen to the end of the words, not the start.") + SND["x"] + B(".", "."))
    for l, (w1, f1), (w2, f2), show, kind in [("q", ("quilt", "لحاف"), ("question", "سوال"), "quilt", "small"), ("q", ("quick", "تیز"), ("quilt", "لحاف"), "", "cap"),
                                             ("z", ("zebra", "گوره‌خر"), ("zip", "زنجیرک"), "zebra", "small"), ("z", ("zero", "صفر"), ("zip", "زنجیرک"), "zip", "cap")]:
        row(g, r, say_en=f"{w1}. {w2}.", show=show, answer=form(l, kind), right=form(l, kind),
            distractors=things(wrong_letters(l, list("xqzsgjp"), kind, by_sound=True), kind),
            help_fa=B(f"این دو کلمه یعنی {q(f1)} و {q(f2)}. هر دو با یک حرف شروع می‌شوند.", f"These two words mean {EN_OF.get(f1, w1)} and {EN_OF.get(f2, w2)}. Both begin with the same letter.") + SND[l] + B(".", "."))
    for l in "sbmthpfl":
        ws = WORDS[l][4:7]
        if len(ws) < 3:
            ws = WORDS[l][-3:]
        text = ". ".join(w[0] for w in ws) + "."
        row(g, r, say_en=text, show=ws[0][1], answer=form(l, "both"), right=form(l, "both"),
            distractors=things(wrong_letters(l, list("sbmthpfldn"), "both", by_sound=True), "both"),
            help_fa=B("سه کلمه:", "Three words:") + B("، ".join(q(w[2]) for w in ws), ", ".join(w[0] for w in ws))
            + B(". هر سه با یک حرف شروع می‌شوند.", ". All three begin with the same letter.") + SND[l] + B(".", "."))
    intro(g, r, B("سه حرف آخر و تکرار. این بار گاهی دو کلمه و گاهی سه کلمه می‌شنوی. یک حرف را در آخر کلمه می‌شنوی، نه در اول: خوب گوش کن که از تو چه پرسیده می‌شود.",
                  "The last three letters, and review. This time you hear sometimes two and sometimes three words. One letter you hear at the end of the word, not the start: listen well to what you are asked."))


# --------------------------------------------------------------------------
# f  First Letter (listen_pick): a picture and its word, pick the first letter

def first_letter() -> None:
    g = "first_letter"
    kinds = ["small", "cap", "both", "both"]
    reviewed: set[str] = set()
    used_bare: Counter = Counter()
    for k, letters in enumerate(SETS[:6]):
        r = nn(k)
        pool = letters if len(letters) >= 4 else letters + SETS[k - 1]
        for l in letters:
            for n, (word, pic, wfa) in enumerate(WORDS[l][:4]):
                kind = kinds[n]
                used_bare[word] += 1
                row(g, r, say_en=word, show=pic, answer=form(l, kind), right=form(l, kind),
                    distractors=things(wrong_letters(l, pool, kind, by_sound=True), kind),
                    help_fa=meaning(wfa) + B("حرف اول آن را بگیر.", "Take its first letter.") + SND[l] + B(".", "."))
        if k >= 1:  # mixed with earlier sets: words not asked in their own round
            extra = [(l, w) for s in SETS[:k] for l in s for w in WORDS[l][4:]]
            RNG.shuffle(extra)
            taken = 0
            for l, (word, pic, wfa) in extra:
                if used_bare[word] or taken >= 5 or l in reviewed:
                    continue
                reviewed.add(l)
                used_bare[word] += 1
                taken += 1
                row(g, r, say_en=word, show=pic, answer=form(l, "small"), right=form(l, "small"),
                    distractors=things(wrong_letters(l, upto(k), "small", by_sound=True), "small"),
                    help_fa=meaning(wfa) + B("این حرف از دسته‌های پیش است.", "This letter is from the earlier sets.") + SND[l] + B(".", "."))
        intro(g, r, B("دستهٔ", "Set") + ORDINAL[k]
              + B(". تصویر را ببین و کلمهٔ انگلیسی آن را بشنو. به صدای اول کلمه گوش کن و حرفی را انتخاب کن که کلمه با آن شروع می‌شود.",
                  ". Look at the picture and hear its English word. Listen to the first sound of the word and choose the letter the word begins with.")
              + (B("گاهی حرف کلان است، گاهی خُرد، گاهی هر دو.", "Sometimes the letter is big, sometimes small, sometimes both.") if k == 0 else
                 B("چند کلمه از حرف‌های پیش هم است.", "There are a few words of the earlier letters too.")))
    # round 07: q, z, and the LAST letter (x, and known three-letter words)
    r = "07"
    for l in "qz":
        for n, (word, pic, wfa) in enumerate(WORDS[l]):
            kind = kinds[n + 1]
            row(g, r, say_en=word, show=pic, answer=form(l, kind), right=form(l, kind),
                distractors=things(wrong_letters(l, list("xqzgsp"), kind, by_sound=True), kind),
                help_fa=meaning(wfa) + B("حرف اول آن را بگیر.", "Take its first letter.") + SND[l] + B(".", "."))
    ends = [B("حرف آخر این کلمه کدام است؟", "Which is the last letter of this word?"),
            B("این کلمه با کدام حرف تمام می‌شود؟", "Which letter does this word end with?"),
            B("به آخر کلمه گوش کن. حرف آخر را بگیر.", "Listen to the end of the word. Take the last letter.")]
    last = [("box", "box", "صندوق"), ("fox", "fox", "روباه"), ("six", "t:6", "شش"), ("cat", "cat", "پشک"), ("dog", "dog", "سگ"),
            ("sun", "sun", "آفتاب"), ("bed", "bed", "تخت خواب"), ("cup", "cup", "پیاله"), ("hen", "hen", "مرغ"), ("bag", "bag", "بکس"),
            ("pot", "pot", "دیگ"), ("leg", "leg", "لنگ")]
    seen: Counter = Counter()
    for n, (word, pic, wfa) in enumerate(last):
        l = word[-1]
        kind = ("cap", "small", "both")[seen[l] % 3]
        seen[l] += 1
        wrong = list(dict.fromkeys([c for c in word[:2] if c != l] + [c for c in "xtgndp" if c != l]))[:3]
        row(g, r, say_fa=ends[n % 3], say_en=word, show=pic, answer=form(l, kind), right=form(l, kind),
            distractors=things(wrong, kind),
            help_fa=meaning(wfa) + B("این بار حرف آخر را می‌خواهیم، نه حرف اول.", "This time we want the last letter, not the first.") + SND[l] + B(".", "."))
    intro(g, r, B("دستهٔ هفتم: اول و آخر. در این دور دو قسم سوال است. اگر تنها کلمه را شنیدی، حرف اول آن را بگیر. اگر پیش از کلمه پرسیده شد که حرف آخر کدام است، حرف آخر را بگیر. یکی از حرف‌های نو تقریباً همیشه در آخر است.",
                  "Set seven: first and last. This round has two kinds of question. If you hear only the word, take its first letter. If you are asked before the word which the last letter is, take the last letter. One of the new letters is almost always at the end."))


# --------------------------------------------------------------------------
# g  Letter Baskets (sorter)

def letter_baskets() -> None:
    g = "letter_baskets"

    def basket_say(l: str) -> str:
        word = KEY[l][0]
        return say(f"{l.upper()}, {l.upper()}, {word}.", l.upper() * 2)

    def round_(r: str, letters: list[str], per: int, text: B, later: bool = False) -> None:
        rows = []
        for l in letters:
            mine = [(w, p) for w, p, _ in WORDS[l][:per]]
            if later:  # other words than in the round of the letter's own set, or the word said another way
                mine = [(w, p) for w, p, _ in WORDS[l][6:6 + per]] or [("a " + w, p) for w, p, _ in WORDS[l][:per]]
            for word, pic in mine:
                rows.append(dict(thing=pic, say_en=word, basket=form(l, "small"), basket_say_en=basket_say(l)))
            if len(mine) < 4:  # a thin basket: the big letter belongs in it too
                rows.append(dict(thing=form(l, "cap"), say_en=say(f"big {l.upper()}", l.upper()), basket=form(l, "small"), basket_say_en=basket_say(l)))
            if len(mine) < 3:
                rows.append(dict(thing=form(l, "both"), say_en=say(f"{l.upper()}. Big and small.", l.upper()), basket=form(l, "small"), basket_say_en=basket_say(l)))
        RNG.shuffle(rows)
        seen = set()
        for c in rows:
            if c["basket"] in seen:
                c["basket_say_en"] = ""
            seen.add(c["basket"])
            RIGHT.append((g, r, c["basket"]))
            row(g, r, **c)
        intro(g, r, text)

    base = B("هر سبد یک حرف است. تصویر را ببین، کلمه را بشنو و آن را در سبد حرف اولش بینداز.",
             "Every basket is a letter. Look at the picture, hear the word and drop it into the basket of its first letter.")
    for k in range(5):
        round_(nn(k), SETS[k], 6, B("دستهٔ", "Set") + ORDINAL[k] + B(".", ".") + base
               + [B("اول هر سبد نام حرف و کلمهٔ خود را می‌گوید.", "First every basket says the name of its letter and its word."),
                  B("به صدای اول کلمه گوش کن.", "Listen to the first sound of the word."),
                  B("اگر یک حرف کلان آمد، آن را در سبد خُرد همان حرف بینداز.", "If a big letter comes, drop it into the basket of the same small letter."),
                  B("کلمه‌های نو هم در میان است: کمک، سبدها را دوباره می‌گوید.", "There are new words among them too: help says the baskets again."),
                  B("چهار سبد، چهار حرف. شتاب نکن.", "Four baskets, four letters. Do not hurry.")][k])
    round_("06", list("jyvz"), 6, B("چهار حرف کمیاب. این حرف‌ها کلمه‌های کمی دارند، پس حرف‌های کلان هم می‌آید: هر حرف کلان را در سبد خُرد خودش بینداز.",
                                   "Four rare letters. These letters have few words, so big letters come too: drop every big letter into the basket of its own small letter."))
    round_("07", list("bdp"), 5, later=True, text=B("سه حرف همشکل. این سه حرف هر کدام یک خط و یک شکم دارند. پیش از انداختن، سبدها را خوب ببین: شکم کدام طرف است و خط بالا می‌رود یا پایین؟",
                                  "Three look-alike letters. Each of these three has a line and a belly. Before you drop, look well at the baskets: on which side is the belly, and does the line go up or down?"))
    # round 08: vowels and consonants
    r = "08"
    vowel, cons = "f:صدادار", "f:بی‌صدا"
    fa(B("صدادار", "vowel (with a voice)"))
    fa(B("بی‌صدا", "consonant (without a voice)"))
    rows = []
    for n, l in enumerate("aeiou"):
        rows.append(dict(thing=form(l, "small"), say_en=say(f"{l.upper()}.", l.upper()), basket=vowel))
        rows.append(dict(thing=form(l, "cap"), say_en=say(f"{l.upper()}, the big one.", l.upper()), basket=vowel))
    for n, l in enumerate("bcdfgklmnprst"):
        rows.append(dict(thing=form(l, ("small", "cap")[n % 2]), say_en=say(f"{l.upper()}.", l.upper()), basket=cons))
    RNG.shuffle(rows)
    seen = set()
    for c in rows:
        if c["basket"] not in seen:
            c["basket_say_fa"] = B("حرف صدادار", "vowel") if c["basket"] == vowel else B("حرف بی‌صدا", "consonant")
        seen.add(c["basket"])
        RIGHT.append((g, r, c["basket"]))
        row(g, r, **c)
    intro(g, r, B("صدادار و بی‌صدا. پنج حرف انگلیسی صدادار است: وقتی آن‌ها را می‌گویی، دهن باز است و هوا آزاد بیرون می‌آید. همان پنج حرفی که در قصهٔ اول دیدی. بیست و یک حرف دیگر بی‌صدا است: لب یا زبان یا دندان راه هوا را می‌بندد. هر حرف را در سبد درست بینداز.",
                  "Vowels and consonants. Five English letters are vowels: when you say them the mouth is open and the air comes out freely. They are the five letters you saw in the first story. The other twenty-one are consonants: the lips, the tongue or the teeth close the way of the air. Drop every letter into the right basket."))


# --------------------------------------------------------------------------
# h  Find the Word (listen_pick): a letter is shown, pick the picture

def starts_with() -> None:
    g = "starts_with"
    used: set[str] = set()

    def wrong_pics(l: str, letters: list[str], answer: str) -> str:
        cands = [w[1] for c in letters if c != l and c not in SAME_SOUND.get(l, "") for w in WORDS[c][:6] if w[1] != answer and not w[1].startswith("t:")]
        RNG.shuffle(cands)
        out, firsts = [], set()
        for p in cands:
            first = next(c for c in letters if any(w[1] == p for w in WORDS[c]))
            if first in firsts:
                continue
            firsts.add(first)
            out.append(p)
            if len(out) == 3:
                break
        return "|".join(out)

    def item(r: str, l: str, n: int, text: str, letters: list[str], kind: str) -> None:
        ws = [w for w in WORDS[l] if w[1] not in used]
        if not ws:
            return
        word, pic, wfa = ws[0]
        used.add(pic)
        row(g, r, say_en=say(text.format(L=l.upper()), l.upper()), show=form(l, kind), answer=pic, right=pic,
            distractors=wrong_pics(l, letters, pic),
            help_fa=B(f"جواب {q(wfa)} است.", f"The answer is {word}.")
            + B("نام انگلیسی آن با این حرف شروع می‌شود.", "Its English name begins with this letter.") + SND[l] + B(".", "."))

    plan = [(0, 1), (2, 3), (4, 5, 6)]
    for i, grp in enumerate(plan):
        r = nn(i)
        letters = [c for s in grp for c in SETS[s] if c != "x"]
        for l in letters:
            item(r, l, 0, "Which one begins with {L}?", letters, "both")
            item(r, l, 1, "What starts with {L}?", letters, "small")
        if i == 2:
            for word, pic, text in [("box", "box", "Which one ends with X?"), ("fox", "fox", "What has X at the end?")]:
                row(g, r, say_en=say(text, "X"), show="t:x", answer=pic, right=pic, distractors={"box": "bag|zebra|key", "fox": "leg|water_jug|wolf"}[word],
                    help_fa=B(f"جواب {q({'box': 'صندوق', 'fox': 'روباه'}[word])} است.", f"The answer is {word}.")
                    + B("این حرف در آخر نام انگلیسی آن است، نه در اول.", "This letter is at the end of its English name, not at the start.") + SND["x"] + B(".", "."))
        intro(g, r, [B("هشت حرف اول. این بار برعکس است: یک حرف را می‌بینی و نام آن را می‌شنوی. از چهار تصویر، آن را انتخاب کن که نام انگلیسی‌اش با همین حرف شروع می‌شود.",
                       "The first eight letters. This time it is the other way round: you see a letter and hear its name. Of the four pictures, choose the one whose English name begins with this letter."),
                     B("هشت حرف بعدی. حرف را ببین. نام هر تصویر را آهسته با خود بگو: کدام یک با این حرف شروع می‌شود؟",
                       "The next eight letters. Look at the letter. Say the name of every picture quietly to yourself: which one begins with this letter?"),
                     B("ده حرف آخر. بیشتر کلمه‌ها نو است، پس اگر ندانستی کمک بخواه. برای یک حرف، کلمه‌ای را بگیر که آن حرف در آخرش است.",
                       "The last ten letters. Most of the words are new, so ask for help if you do not know. For one letter, take the word that has the letter at its end.")][i])
    r = "04"
    letters = [c for c in ALPHA if c != "x"]
    order = letters[:]
    RNG.shuffle(order)
    for l in order:
        item(r, l, 2, "{L}. Find the picture.", letters, "cap")
    intro(g, r, B("تمام الفبا، گد و ود. این بار حرف کلان را می‌بینی. تصویری را پیدا کن که نامش با آن شروع می‌شود. هر بار هشت سوال دیگر می‌آید.",
                  "The whole alphabet, mixed. This time you see the big letter. Find the picture whose name begins with it. Eight different questions come every time."))


# --------------------------------------------------------------------------
# i  Letter Rain (catch)

def letter_rain() -> None:
    g = "letter_rain"
    groups = [(0, 1), (2, 3), (4, 5, 6)]
    for i, grp in enumerate(groups):
        r = nn(i)
        letters = [c for s in grp for c in SETS[s]]
        for l in letters:
            ws = wrong_letters(l, letters, "small", 5)
            others = [form(c, ("small", "cap")[n % 2]) for n, c in enumerate(ws)]
            row(g, r, say_en=say(f"Catch the letter {l.upper()}.", l.upper()), targets=things([l], "cap") + "|" + things([l], "small"),
                others="|".join(others), need="4", right=form(l, "cap"),
                help_fa=B("کلان و خُرد آن، هر دو درست است. کلان:", "Its big and its small shape are both right. Big:") + CAP[l]
                + B(". خُرد:", ". Small:") + SM[l] + B(".", "."))
        intro(g, r, [B("هشت حرف اول. نام یک حرف گفته می‌شود. تنها همان حرف را در سبد بگیر، کلان باشد یا خُرد. حرف‌های دیگر را بمان که بیفتند.",
                       "The first eight letters. The name of a letter is called. Catch only that letter in the basket, big or small. Let the other letters fall."),
                     B("هشت حرف بعدی. حرفی را که نامش گفته می‌شود بگیر. هوش کن: کلان و خُرد بعضی حرف‌ها به هم نمی‌مانند.",
                       "The next eight letters. Catch the letter whose name is called. Take care: the big and small of some letters do not look alike."),
                     B("ده حرف آخر. نام را بشنو و همان حرف را بگیر. اگر یکی از دستت رفت، غم نیست: باز می‌آید.",
                       "The last ten letters. Hear the name and catch that letter. If one gets away, never mind: it comes again.")][i])
    r = "04"
    for l in "smbthpcdfglrwn":
        ws = WORDS[l]
        word, pic, wfa = ws[min(4, len(ws) - 1)]
        others = [form(c, ("small", "cap")[n % 2]) for n, c in enumerate(wrong_letters(l, list("smbthpcdfglrwn"), "small", 5, by_sound=True))]
        row(g, r, say_en=f"Catch the first letter of {word}.", targets=things([l], "small") + "|" + things([l], "cap"),
            others="|".join(others), need="4", right=form(l, "small"),
            help_fa=meaning(wfa) + B("حرف اول آن را بگیر، کلان یا خُرد.", "Catch its first letter, big or small.") + SND[l] + B(".", "."))
    intro(g, r, B("حرف اول کلمه. این بار نام حرف گفته نمی‌شود. یک کلمه می‌شنوی: حرفی را بگیر که کلمه با آن شروع می‌شود.",
                  "The first letter of a word. This time the letter's name is not said. You hear a word: catch the letter the word begins with."))


# --------------------------------------------------------------------------
# j  Alphabet Train (builder): put letters in alphabet order

def abc_order() -> None:
    g = "abc_order"
    UP = ALPHA.upper()

    def window(r: str, start: int, n: int, small: bool = False) -> None:
        seq = (ALPHA if small else UP)[start:start + n]
        text = ", ".join(seq.upper() if not small else seq) + "."
        first = seq[0].lower()
        row(g, r, say_en=say(text, seq.upper()), tiles="|".join("t:" + c for c in seq), done_en=text, right="|".join(seq),
            help_fa=B("از طرف چپ شروع کن. اول این حرف می‌آید:", "Start on the left. This letter comes first:") + (SM if small else CAP)[first]
            + B(". باقی را به همان ترتیبی بمان که شنیدی.", ". Put the rest in the order you heard."))

    for s, n in [(0, 4), (1, 4), (2, 4), (3, 4), (5, 4), (6, 4), (8, 4), (9, 4), (0, 5), (2, 5), (4, 5), (6, 5), (8, 5), (1, 5)]:
        window("01", s, n)
    intro("abc_order", "01", B("از اول الفبا تا میان آن. چند حرف را به ترتیب الفبا می‌شنوی. آن‌ها را به همان ترتیب، از چپ به راست، مثل واگون‌های قطار پشت هم بمان.",
                               "From the start of the alphabet to its middle. You hear a few letters in alphabet order. Put them in the same order, from left to right, one behind the other like the wagons of a train."))
    for s, n in [(13, 4), (14, 4), (15, 4), (17, 4), (18, 4), (20, 4), (21, 4), (13, 5), (15, 5), (17, 5), (19, 5), (21, 5), (16, 4), (12, 4)]:
        window("02", s, n)
    intro("abc_order", "02", B("از میان الفبا تا آخر آن. گوش کن و حرف‌ها را به ترتیب بمان. قطار همیشه از چپ شروع می‌شود.",
                               "From the middle of the alphabet to its end. Listen and put the letters in order. The train always starts on the left."))
    for s, n in [(0, 6), (2, 6), (4, 6), (6, 6), (8, 6), (10, 6), (12, 6), (14, 6), (16, 6), (18, 6), (20, 6), (1, 3), (10, 3), (22, 3)]:
        window("03", s, n, small=True)
    intro("abc_order", "03", B("حرف‌های خُرد. قطار این بار درازتر است، تا شش واگون. ترتیب همان است؛ تنها شکل حرف‌ها خُرد است.",
                               "The small letters. The train is longer this time, up to six wagons. The order is the same; only the shapes of the letters are small."))
    seen = set()
    while len(seen) < 14:
        picks = sorted(RNG.sample(range(26), 4))
        if any(b - a < 2 for a, b in zip(picks, picks[1:])) or tuple(picks) in seen:
            continue
        seen.add(tuple(picks))
        small = len(seen) % 2 == 0
        seq = [(ALPHA if small else UP)[p] for p in picks]
        heard = seq[:]
        while heard == seq:
            RNG.shuffle(heard)
        said = ", ".join(c.upper() for c in heard) + "."
        done = ", ".join(c.upper() for c in seq) + "."
        row(g, "04", say_en=say(said, "".join(heard).upper()), tiles="|".join("t:" + c for c in seq), done_en=say(done, "".join(seq).upper()), right="|".join(seq),
            help_fa=B("این بار ترتیبی که شنیدی درست نیست. حرفی که در الفبا پیش‌تر است، طرف چپ می‌رود. اول این حرف:", "This time the order you heard is not right. The letter that is earlier in the alphabet goes to the left. First this letter:")
            + (SM if small else CAP)[seq[0].lower()] + B(". در آخر این حرف:", ". Last this letter:") + (SM if small else CAP)[seq[-1].lower()] + B(".", "."))
    intro("abc_order", "04", B("گد و ود. این بار گوینده چهار حرف را بی‌ترتیب می‌گوید. تو خودت آن‌ها را به ترتیب الفبا بمان: حرفی که در الفبا پیش‌تر می‌آید، طرف چپ. اگر یادت رفت، الفبا را آهسته با خود بخوان.",
                               "Mixed up. This time the speaker says four letters out of order. Put them in alphabet order yourself: the letter that comes earlier in the alphabet goes on the left. If you forget, say the alphabet quietly to yourself."))


# --------------------------------------------------------------------------
# k  What Comes Next? (journey)

def abc_next() -> None:
    g = "abc_next"
    UP = ALPHA.upper()

    def near(i: int, small: bool = False) -> str:
        cands = [i + 1, i - 1, i + 2, i - 2, i + 3, i - 3]
        out = [(ALPHA if small else UP)[c] for c in cands if 0 <= c < 26][:3]
        return "|".join("t:" + c for c in out)

    def shape_help(i: int, small: bool = False) -> B:
        return B("جواب این شکل را دارد:", "The answer has this shape:") + (SM if small else CAP)[ALPHA[i]] + B(".", ".")

    for r, lo, hi, text in [("01", 2, 12, B("از اول تا میان الفبا. دو حرف را می‌بینی و می‌شنوی. حرف بعدی کدام است؟ جواب بده و پیش برو.",
                                            "From the start to the middle of the alphabet. You see and hear two letters. Which is the next one? Answer and move on.")),
                            ("02", 14, 25, B("از میان تا آخر الفبا. دو حرف پشت هم، و بعد؟ حرف سوم را انتخاب کن.",
                                             "From the middle to the end of the alphabet. Two letters in a row, and then? Choose the third letter."))]:
        for i in range(lo, hi + 1):
            a, b = UP[i - 2], UP[i - 1]
            row(g, r, say_en=say(f"{a}, {b}. What comes next?", a + b), show=f"t:{a} {b} ?", answer="t:" + UP[i], right="t:" + UP[i], distractors=near(i),
                help_fa=B("الفبا را از اول آهسته با خود بخوان تا به این دو حرف برسی.", "Say the alphabet quietly to yourself from the start until you reach these two letters.") + shape_help(i))
        first = lo - 2
        row(g, r, say_en=say(f"What comes after {UP[first]}?", UP[first]), show=f"t:{UP[first]} ?", answer="t:" + UP[first + 1], right="t:" + UP[first + 1], distractors=near(first + 1),
            help_fa=B("تنها یک حرف را می‌بینی. حرف بعد از آن را بگیر.", "You see only one letter. Take the letter after it.") + shape_help(first + 1))
        intro(g, r, text)
    r = "03"
    for i in [3, 6, 9, 12, 15, 18, 21, 24, 1, 10, 19, 25]:
        row(g, r, say_en=say(f"What comes before {UP[i]}?", UP[i]), show=f"t:? {UP[i]}", answer="t:" + UP[i - 1], right="t:" + UP[i - 1], distractors=near(i - 1),
            help_fa=B("این بار حرف پیش از آن را می‌خواهیم: حرفی که طرف چپ آن می‌ایستد.", "This time we want the letter before it: the one that stands on its left.") + shape_help(i - 1))
    for i in [2, 5, 7, 11, 14, 17, 20, 23]:
        a, b = UP[i - 1], UP[i + 1]
        row(g, r, say_en=say(f"Which letter is between {a} and {b}?", a + b), show=f"t:{a} ? {b}", answer="t:" + UP[i], right="t:" + UP[i], distractors=near(i),
            help_fa=B("دو حرف را می‌بینی و میان آن‌ها یک جای خالی است. حرف میانی را بگیر.", "You see two letters with an empty place between them. Take the middle letter.") + shape_help(i))
    intro(g, r, B("پیش از آن و در میان. دو قسم سوال: کدام حرف پیش از این حرف می‌آید، و کدام حرف میان این دو حرف است. نشان سوال جای خالی را نشان می‌دهد.",
                  "Before, and in between. Two kinds of question: which letter comes before this letter, and which letter is between these two. The question mark shows the empty place."))
    r = "04"
    for i in [1, 2, 4, 5, 7, 8, 10, 11, 14, 16, 17, 19, 20, 22, 23, 25]:
        row(g, r, say_en=say(f"What comes after {UP[i - 1]}?", UP[i - 1]), show=f"t:{ALPHA[i - 1]} ?", answer="t:" + ALPHA[i], right="t:" + ALPHA[i], distractors=near(i, True),
            help_fa=B("حرف‌ها این بار خُرد است، اما ترتیب همان است.", "The letters are small this time, but the order is the same.") + shape_help(i, True))
    row(g, r, say_fa=B("اولین حرف الفبا کدام است؟", "Which is the first letter of the alphabet?"), answer="t:a", right="t:a", distractors="t:z|t:b|t:e",
        help_fa=B("الفبا با آن شروع می‌شود.", "The alphabet begins with it.") + shape_help(0, True))
    row(g, r, say_fa=B("آخرین حرف الفبا کدام است؟", "Which is the last letter of the alphabet?"), answer="t:z", right="t:z", distractors="t:a|t:y|t:x",
        help_fa=B("الفبا با آن تمام می‌شود.", "The alphabet ends with it.") + shape_help(25, True))
    intro(g, r, B("حرف‌های خُرد، تمام الفبا. یک حرف خُرد را می‌بینی. حرف بعد از آن کدام است؟ دو سوال هم دربارهٔ اول و آخر الفبا است.",
                  "The small letters, the whole alphabet. You see a small letter. Which letter comes after it? There are also two questions about the start and the end of the alphabet."))


# --------------------------------------------------------------------------
# l  Look-alike Letters (listen_pick): b d p q, m n, u v, i l, and the capitals

TELL = {
    "b": B("اول خط بلند می‌آید و بعد شکم. شکم طرف راست و پایین است.", "The tall line comes first and then the belly. The belly is on the right, at the bottom."),
    "d": B("اول شکم می‌آید و بعد خط بلند. شکم طرف چپ است.", "The belly comes first and then the tall line. The belly is on the left."),
    "p": B("خط آن پایین می‌رود، و شکم طرف راست است.", "Its line goes down, and the belly is on the right."),
    "q": B("خط آن پایین می‌رود، و شکم طرف چپ است.", "Its line goes down, and the belly is on the left."),
    "m": B("دو کمان دارد، مثل دو پل.", "It has two arches, like two bridges."),
    "n": B("تنها یک کمان دارد، مثل یک پل.", "It has only one arch, like one bridge."),
    "u": B("پایین آن گرد است، مثل پیاله.", "Its bottom is round, like a cup."),
    "v": B("پایین آن تیز است.", "Its bottom is pointed."),
    "i": B("کوتاه است و یک نقطه بالای خود دارد.", "It is short and has a dot above it."),
    "l": B("بلند است و نقطه ندارد.", "It is tall and has no dot."),
    "h": B("خط آن بلند است و بالا می‌رود.", "Its line is tall and goes up."),
    "w": B("پایین آن دو جای تیز دارد.", "Its bottom has two pointed places."),
}
TELL_CAP = {
    "e": B("سه خط خوابیده دارد: بالا، میان و پایین.", "It has three lying lines: top, middle and bottom."),
    "f": B("دو خط خوابیده دارد؛ پایین آن خالی است.", "It has two lying lines; its bottom is empty."),
    "m": B("جاهای تیز آن پایین را نشان می‌دهند، و روی دو پای ایستاده است.", "It stands on two legs, and its point in the middle points down."),
    "w": B("جاهای تیز آن در پایین است، مثل دو دره.", "Its points are at the bottom, like two valleys."),
    "o": B("دایره بسته است و دُم ندارد.", "The circle is closed and has no tail."),
    "q": B("دایره یک دُم خُرد دارد.", "The circle has a small tail."),
    "c": B("دایره باز است و در داخل هیچ ندارد.", "The circle is open and has nothing inside."),
    "g": B("دایره باز است و یک خط خُرد به داخل می‌آید.", "The circle is open and a small line comes inside."),
    "p": B("تنها یک شکم دارد و پای کج ندارد.", "It has only a belly and no slanting leg."),
    "r": B("یک شکم دارد و یک پای کج.", "It has a belly and a slanting leg."),
}


def look_alikes() -> None:
    g = "look_alikes"

    def pair_round(r: str, pairs: list[tuple[str, list[str]]], text: B) -> None:
        for l, rivals in pairs:
            L = l.upper()
            ws = WORDS[l]
            tell = TELL[l]
            # 1 the name -> the small letter
            row(g, r, say_en=say(f"Which one is {l}?", L), answer=form(l, "small"), right=form(l, "small"),
                distractors=things(rivals, "small"), help_fa=tell)
            # 2 a word and its picture -> small or both
            w = ws[min(2, len(ws) - 1)]
            rv = rivals[0].upper()
            row(g, r, say_en=say(f"{w[0]}. {L} or {rv}?", L + rv), show=w[1], answer=form(l, "both"), right=form(l, "both"),
                distractors=things(rivals[:2], "both"), help_fa=meaning(w[2]) + SND[l] + B(".", ".") + tell)
            # 3 the big letter is shown -> its small one
            row(g, r, say_en=say(f"This is big {L}. Find small {l}.", L + L), show=form(l, "cap"), answer=form(l, "small"), right=form(l, "small"),
                distractors=things(rivals, "small"),
                help_fa=B("حرف کلان را می‌بینی. خُرد آن را بگیر.", "You see the big letter. Take its small one.") + tell)
            # 4 the small letter is shown -> the picture
            if len(ws) >= 2:
                w = ws[1]
                wrong = [WORDS[c][1 if len(WORDS[c]) > 1 else 0][1] for c in rivals if WORDS[c]][:3]
                row(g, r, say_en=say(f"{l}. Which picture?", L), show=form(l, "small"), answer=w[1], right=w[1], distractors="|".join(wrong),
                    help_fa=B(f"جواب {q(w[2])} است.", f"The answer is {w[0]}.") + SND[l] + B(".", "."))
            # 5 two words -> the big letter
            hs = HEARD[l]
            if len(hs) >= 2:
                row(g, r, say_en=f"{hs[1][0]}. {hs[0][0]}.", answer=form(l, "cap"), right=form(l, "cap"), distractors=things(rivals, "cap"),
                    help_fa=B(f"این دو کلمه یعنی {q(hs[1][1])} و {q(hs[0][1])}.", f"These two words mean {EN_OF.get(hs[1][1], hs[1][0])} and {EN_OF.get(hs[0][1], hs[0][0])}.")
                    + SND[l] + B(". این بار حرف کلان را بگیر:", ". This time take the big letter:") + CAP[l] + B(".", "."))
        intro(g, r, text)

    pair_round("01", [("b", ["d", "p", "q"]), ("d", ["b", "q", "p"])],
               B("دو حرف که به هم بسیار می‌مانند: هر دو یک خط بلند و یک شکم دارند. فرق این است: در یکی اول خط می‌آید و بعد شکم، در دیگری اول شکم و بعد خط. انگلیسی از چپ خوانده می‌شود، پس از چپ ببین. آهسته برو.",
                 "Two letters that look much alike: both have a tall line and a belly. The difference: in one the line comes first and then the belly, in the other the belly first and then the line. English is read from the left, so look from the left. Go slowly."))
    pair_round("02", [("p", ["q", "b", "d"]), ("q", ["p", "d", "g"])],
               B("دو حرف دیگر با خط و شکم. خط این دو پایین می‌رود. در یکی شکم طرف راست است، در دیگری طرف چپ. دو حرف دور پیش هم در میان است، تا خوب فرق کنی.",
                 "Two more letters with a line and a belly. The line of these two goes down. In one the belly is on the right, in the other on the left. The two letters of the last round are among them, so that you tell them apart well."))
    pair_round("03", [("m", ["n", "w", "h"]), ("n", ["m", "h", "u"]), ("u", ["v", "n", "w"]), ("v", ["u", "w", "y"]), ("i", ["l", "j", "t"]), ("l", ["i", "t", "k"])],
               B("سه جوره حرف همشکل: یکی یا دو کمان؛ پایین گرد یا پایین تیز؛ کوتاه با نقطه یا بلند بدون نقطه. پیش از جواب دادن، هر چهار حرف را خوب ببین.",
                 "Three pairs of look-alike letters: one arch or two; a round bottom or a pointed one; short with a dot or tall without. Before you answer, look well at all four letters."))
    r = "04"
    for a, b, third in [("e", "f", "l"), ("m", "w", "n"), ("o", "q", "c"), ("c", "g", "o"), ("p", "r", "b")]:
        for l, other in ((a, b), (b, a)):
            L = l.upper()
            rivals = [other, third] + [c for c in ALIKE_CAP[l] if c not in (other, third)][:1]
            row(g, r, say_en=say(f"Which one is big {L}?", L), answer=form(l, "cap"), right=form(l, "cap"), distractors=things(rivals, "cap"),
                help_fa=TELL_CAP[l] + B("کلمهٔ آن:", "Its word:") + B(q(KEY[l][2]), KEY[l][0]) + B(".", "."))
            row(g, r, say_en=say(f"This is small {l}. Find big {L}.", L + L), show=form(l, "small"), answer=form(l, "cap"), right=form(l, "cap"),
                distractors=things(rivals, "cap"), help_fa=B("حرف خُرد را می‌بینی. کلان آن را بگیر.", "You see the small letter. Take its big one.") + TELL_CAP[l])
    intro(g, r, B("حرف‌های کلان همشکل. پنج جوره: سه خط یا دو خط؛ تیزی بالا یا پایین؛ دایره با دُم یا بدون دُم؛ دایرهٔ باز خالی یا با خط؛ شکم با پای یا بدون پای.",
                  "Look-alike big letters. Five pairs: three lines or two; points up or down; a circle with a tail or without; an open circle, empty or with a line; a belly with a leg or without."))


# --------------------------------------------------------------------------
# m  Spell It (builder): three-letter words from letter tiles

ANCHOR = {"a": "انار", "b": "بز", "c": "کتاب", "d": "دروازه", "e": "امروز", "f": "فیل", "g": "گل", "h": "هفت", "i": "اینجا", "j": "جوی",
          "k": "کلید", "l": "لب", "m": "مادر", "n": "نان", "o": "آفتاب", "p": "پدر", "r": "روز", "s": "سیب", "t": "توت", "u": "اگر",
          "v": "فیل", "y": "یک", "z": "زمین"}
ANCHOR_EN = {"a": "anar", "b": "buz", "c": "kitab", "d": "darwaza", "e": "imroz", "f": "fil", "g": "gul", "h": "haft", "i": "inja", "j": "joy",
             "k": "kilid", "l": "lab", "m": "madar", "n": "nan", "o": "aftab", "p": "padar", "r": "roz", "s": "seb", "t": "tut", "u": "agar",
             "v": "fil", "y": "yak", "z": "zamin"}
SPELL = {
    "01": [("cat", "پشک"), ("bag", "بکس"), ("hat", "کلاه"), ("ant", "مورچه"), ("tap", "نل"), ("sad", "غمگین"), ("van", "موتر مسافربری"), ("can", "قطی"), ("and", "و")],
    "02": [("hen", "مرغ"), ("pen", "قلم"), ("bed", "تخت خواب"), ("leg", "لنگ"), ("red", "سرخ"), ("ten", "ده"), ("yes", "بلی"), ("egg", "تخم مرغ"), ("net", "جال")],
    "03": [("big", "کلان"), ("six", "شش"), ("zip", "زنجیرک"), ("ink", "سیاهی قلم"), ("dog", "سگ"), ("box", "صندوق"), ("fox", "روباه"), ("pot", "دیگ"), ("in", "در داخل"), ("on", "روی")],
    "04": [("sun", "آفتاب"), ("cup", "پیاله"), ("jug", "کوزه"), ("up", "بالا"), ("milk", "شیر"), ("hand", "دست"), ("nest", "آشیانه"), ("lamp", "چراغ"), ("drum", "دهل"),
           ("cat", "پشک"), ("hen", "مرغ"), ("dog", "سگ")],
}
EN_OF.update({"قطی": "can", "جال": "net", "تیز": "quick"})


def sound_of(l: str, pos: B) -> B:
    if l == "x":
        return pos + B("دو صدا، مثل آخر «عکس»", "two sounds, like the end of aks")
    if l == "v":
        return pos + B("مثل اول «فیل» اما با آواز", "like the start of fil but with the voice")
    return pos + B(f"مثل اول {q(ANCHOR[l])}", f"like the start of {ANCHOR_EN[l]}")


def spell_it() -> None:
    g = "spell_it"
    POS3 = [B("صدای اول", "the first sound"), B("، صدای میان", ", the middle sound"), B("، و صدای آخر", ", and the last sound")]
    POS = [B("صدای اول", "the first sound"), B("، بعد", ", then"), B("، بعد", ", then"), B("، و در آخر", ", and at the end")]
    vowels = "aeiou"
    for r, words in SPELL.items():
        for n, (word, wfa) in enumerate(words):
            ln = len(word)
            if ln == 3:
                pos = POS3
            elif ln == 2:
                pos = [POS[0], POS[3]]
            else:
                pos = POS
            hint = B("", "")
            for j, c in enumerate(word):
                if j and word[j - 1] == c:
                    hint = hint + B("، و همان حرف یک بار دیگر", ", and the same letter once more")
                    continue
                hint = hint + sound_of(c, pos[j] if j < len(pos) else POS[2])
            extra = ""
            if r in ("03", "04") or n % 2:
                v = next(c for c in word if c in vowels)
                other = vowels[(vowels.index(v) + 1 + n % 3) % 5]
                if other in word:
                    other = vowels[(vowels.index(other) + 1) % 5]
                extra = "t:" + other
            spelled = ", ".join(c.upper() for c in word)
            row(g, r, say_fa=B(wfa, word), say_en=word, tiles="|".join("t:" + c for c in word), extra=extra,
                done_en=say(f"{spelled}. {word}.", word.upper()), right=word,
                help_fa=B(f"کلمه {len(word)} صدا دارد:", f"The word has {len(word)} sounds:") + hint + B(".", "."))
    intro(g, "01", B("کلمه‌های سه حرفی با صدای میانی باز. اول معنای کلمه را به دری می‌شنوی، بعد کلمهٔ انگلیسی را. آن را آهسته با خود بگو و صداهایش را جدا کن. برای هر صدا یک حرف بگیر و از چپ به راست بمان.",
                         "Three-letter words with the open middle sound. First you hear the meaning of the word in Dari, then the English word. Say it slowly to yourself and take its sounds apart. Take one letter for every sound and put them from left to right."))
    intro(g, "02", B("کلمه‌های سه حرفی با یک صدای میانی دیگر. کلمه را بشنو، صداهایش را جدا کن و حرف‌ها را به ترتیب بمان. در یک کلمه، حرف آخر دو بار می‌آید.",
                         "Three-letter words with another middle sound. Hear the word, take its sounds apart and put the letters in order. In one word the last letter comes twice."))
    intro(g, "03", B("دو صدای میانی دیگر. این بار همیشه یک حرف زیاد هم است که به کلمه تعلق ندارد: به صدای میان کلمه خوب گوش کن.",
                         "Two more middle sounds. This time there is always one letter too many that does not belong to the word: listen well to the middle sound of the word."))
    intro(g, "04", B("صدای میانی پنجم، کلمه‌های چهار حرفی و تکرار. بعضی کلمه‌ها چهار صدا دارند: هر صدا یک حرف. سه کلمه را از دورهای پیش می‌شناسی.",
                         "The fifth middle sound, four-letter words and review. Some words have four sounds: one letter for every sound. Three words you know from the earlier rounds."))


# --------------------------------------------------------------------------
# Writing and checking

HEADERS = {
    "story": ["round", "intro_fa", "picture", "say_en", "say_fa", "show_en", "show_fa", "choices", "right", "wrong_say_fa", "wrong_picture"],
    "listen_pick": ["round", "intro_fa", "say_en", "say_fa", "show", "answer", "distractors", "help_fa"],
    "say_it": ["round", "intro_fa", "say_en", "say_fa", "picture", "meaning_fa"],
    "sorter": ["round", "intro_fa", "thing", "say_en", "say_fa", "basket", "basket_say_fa", "basket_say_en"],
    "builder": ["round", "intro_fa", "say_en", "say_fa", "tiles", "extra", "rtl", "done_en", "done_fa", "help_fa"],
    "catch": ["round", "intro_fa", "say_en", "say_fa", "targets", "others", "need", "help_fa"],
    "pairs": ["round", "intro_fa", "a", "b", "say_en", "say_fa"],
}
HEADERS["journey"] = HEADERS["listen_pick"]

GAMES = [
    # id, engine, letter, draw, title_en, title_fa, intro (game default), icon, maker
    ("meet_letters", "story", "a", None, "Meet the Letters", B("آشنایی با حرف‌ها", "Meet the Letters"),
     B("گوش کن و ببین. هر حرف نام، شکل و صدای خود را دارد. وقتی سوال آمد، جواب درست را انتخاب کن.", "Listen and look. Every letter has its name, its shape and its sound. When a question comes, choose the right answer."), "t:Aa", story),
    ("letter_names", "listen_pick", "b", 8, "Letter Stall", B("دکان حرف‌ها", "Letter Stall"),
     B("نام حرف را بشنو و حرف درست را انتخاب کن.", "Hear the name of the letter and choose the right letter."), "t:Tt", letter_names),
    ("alphabet_echo", "say_it", "c", None, "Alphabet Echo", B("پژواک الفبا", "Alphabet Echo"),
     B("گوش کن. بعد خودت بلند بگو. باز گوش کن و ببین که درست گفتی یا نه.", "Listen. Then say it aloud yourself. Listen again and see whether you said it right."), "t:ABC", alphabet_echo),
    ("big_small", "pairs", "d", 6, "Big and Small Pairs", B("جوره‌های کلان و خُرد", "Big and Small Pairs"),
     B("دو کارت را که با هم جور است پیدا کن.", "Find the two cards that go together."), "t:Gg", big_small),
    ("first_sounds", "journey", "e", 8, "Sound Road", B("راه صداها", "Sound Road"),
     B("به صدای اول کلمه‌ها گوش کن، حرف درست را بگیر و پیش برو.", "Listen to the first sound of the words, take the right letter and move on."), "listen", first_sounds),
    ("first_letter", "listen_pick", "f", 8, "First Letter", B("حرف اول", "First Letter"),
     B("تصویر را ببین، کلمه را بشنو و حرف اول آن را انتخاب کن.", "Look at the picture, hear the word and choose its first letter."), "apple", first_letter),
    ("letter_baskets", "sorter", "g", 8, "Letter Baskets", B("سبدهای حرف", "Letter Baskets"),
     B("هر چیز را در سبد حرف اولش بینداز.", "Drop every thing into the basket of its first letter."), "basket", letter_baskets),
    ("starts_with", "listen_pick", "h", 8, "Find the Word", B("کلمه را پیدا کن", "Find the Word"),
     B("حرف را ببین و تصویری را انتخاب کن که نامش با آن شروع می‌شود.", "Look at the letter and choose the picture whose name begins with it."), "key", starts_with),
    ("letter_rain", "catch", "i", 4, "Letter Rain", B("باران حرف‌ها", "Letter Rain"),
     B("گوش کن. تنها حرفی را که گفته می‌شود در سبد بگیر.", "Listen. Catch only the letter that is called in the basket."), "rain", letter_rain),
    ("abc_order", "builder", "j", 8, "Alphabet Train", B("قطار الفبا", "Alphabet Train"),
     B("حرف‌ها را به ترتیب الفبا، از چپ به راست بمان.", "Put the letters in alphabet order, from left to right."), "train", abc_order),
    ("abc_next", "journey", "k", 8, "What Comes Next?", B("بعد از آن چیست؟", "What Comes Next?"),
     B("حرف بعدی الفبا را انتخاب کن و پیش برو.", "Choose the next letter of the alphabet and move on."), "t:AB?", abc_next),
    ("look_alikes", "listen_pick", "l", 8, "Look-alike Letters", B("حرف‌های همشکل", "Look-alike Letters"),
     B("این حرف‌ها به هم می‌مانند. خوب ببین و حرف درست را انتخاب کن.", "These letters look alike. Look well and choose the right letter."), "t:bd", look_alikes),
    ("spell_it", "builder", "m", 6, "Spell It", B("کلمه بساز", "Spell It"),
     B("کلمه را بشنو و حرف‌های آن را به ترتیب، از چپ به راست بمان.", "Hear the word and put its letters in order, from left to right."), "t:cat", spell_it),
]


def phonemes(text: str) -> str:
    out = subprocess.run(["espeak-ng", "-v", "en-us", "-x", "-q", text], capture_output=True, text=True).stdout
    return " ".join(out.split())


NAME_PH = dict(A="eI", B="bi:", C="si:", D="di:", E="i:", F="Ef", G="dZi:", H="eItS", I="aI", J="dZeI", K="keI", L="El", M="Em", N="En",
               O="oU", P="pi:", Q="kju:", R="A@", S="Es", T="ti:", U="ju:", V="vi:", W="dVb@Lju:", X="Eks", Y="waI", Z="zi:")


def check_names() -> list[str]:
    """Every English line that must NAME a letter: does the phonemizer say the names, in order?"""
    if not shutil.which("espeak-ng"):
        return ["espeak-ng not installed: letter names were not checked"]
    bad = []
    for text, names in sorted(set(NAMES)):
        ph = re.sub(r"[',_]|r-", "", phonemes(text.replace("//", ". ")))
        at = 0
        for n in names:
            found = ph.find(NAME_PH[n], at)
            if found < 0:
                bad.append(f"{text!r}: no name of {n} in {ph!r}")
                break
            at = found + len(NAME_PH[n])
    return bad


def main() -> int:
    import json

    problems: list[str] = []
    games_json = []
    for gid, engine, letter, draw, title_en, title_fa, default_intro, icon, maker in GAMES:
        maker()
        rows = ROWS[gid]
        sheet = f"{gid}.csv"
        with (HERE / sheet).open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=HEADERS[engine], extrasaction="raise")
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in HEADERS[engine]})
        game = {"id": gid, "engine": engine, "letter": letter, "title_en": title_en, "title_fa": fa(title_fa),
                "intro_fa": fa(default_intro), "icon": icon, "sheet": sheet}
        if draw:
            game["draw"] = draw
        games_json.append(game)
        # pictures must exist
        for r in rows:
            for col in ("picture", "show", "answer", "distractors", "thing", "a", "b", "choices", "right", "targets", "others", "tiles", "extra", "wrong_picture"):
                for t in (r.get(col) or "").split("|"):
                    t = t.strip()
                    if t and not t.startswith(("t:", "f:", "p:")) and t != "snd" and not (PICTURES / f"{t}.svg").exists():
                        problems.append(f"{gid}: missing picture {t}")
            if engine in ("listen_pick", "journey"):
                wrong = (r.get("distractors") or "").split("|")
                if r["answer"] in wrong or len(set(wrong)) != len(wrong) or not 1 <= len(wrong) <= 3:
                    problems.append(f"{gid} {r['round']}: bad distractors {r['answer']} / {wrong}")
                if not r.get("help_fa"):
                    problems.append(f"{gid} {r['round']}: no help_fa")
    pack = {"pack": "en-1-letters", "subject": "en", "level": 1, "version": 1, "optional": True,
            "title_en": "English letters: the whole alphabet", "title_fa": fa(B("حرف‌های انگلیسی: تمام الفبا", "English letters: the whole alphabet")),
            "games": games_json}
    (HERE / "pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with I18N.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fa", "en"])
        for k, v in TWINS.items():
            w.writerow([k, v])

    # ---- the tables ----
    print("| Game | Engine | Rounds | Items | Items per round | Asked per play |")
    print("| --- | --- | --- | --- | --- | --- |")
    total_r = total_i = 0
    for gid, engine, letter, draw, *_ in GAMES:
        per = Counter(r["round"] for r in ROWS[gid])
        total_r += len(per)
        total_i += sum(per.values())
        print(f"| `{gid}` | {engine} | {len(per)} | {sum(per.values())} | {min(per.values())} to {max(per.values())} | {draw or 'all'} |")
    print(f"| **total** | | **{total_r}** | **{total_i}** | | |")

    print("\nSpoken questions (Dari + English of a row, punctuation and case ignored):")
    counts = Counter(s for g, r, s in SPOKEN if (g, r) not in REVIEW_ROUNDS)
    hist = Counter(counts.values())
    print("  distinct questions:", len(counts), " asked once:", hist[1], " twice:", hist[2], " more often:", sum(v for k, v in hist.items() if k > 2))
    for s, n in counts.items():
        if n > 2:
            problems.append(f"question asked {n} times: {s}")
    print("\n| Game | Questions | Distinct | Most often the same | Answers | Most often right (answer) |")
    print("| --- | --- | --- | --- | --- | --- |")
    for gid, engine, *_ in GAMES:
        qs = Counter(s for g, r, s in SPOKEN if g == gid)
        ans = Counter(a for g, r, a in RIGHT if g == gid)
        top = ans.most_common(1)[0] if ans else ("", 0)
        print(f"| `{gid}` | {sum(qs.values())} | {len(qs)} | {max(qs.values()) if qs else 0} | {len(ans)} | {top[1]} ({top[0]}) |")
        if engine != "sorter":
            for a, n in ans.items():
                if n > 3:
                    problems.append(f"{gid}: answer {a} is right {n} times")
    bad = check_names()
    print(f"\nLetter names: {len(set(NAMES))} English lines must name a letter; the phonemizer gets {len(set(NAMES)) - len(bad)} right.")
    problems += bad
    print(f"Dari texts with an English twin: {len(TWINS)}")
    if problems:
        print("\nPROBLEMS")
        for p in problems:
            print(" -", p)
        return 1
    print("\nok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

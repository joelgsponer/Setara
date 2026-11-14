#!/usr/bin/env python3
"""Generates content/dari/1 and content/dari/2 (authoring sources) from hand-written data."""
import csv, json, random, sys
from pathlib import Path

OUT = Path("/home/user/Setara/setara/content/dari")

# ---------------------------------------------------------------- letters
NAME = {
    "آ": "آ", "ا": "الف", "ب": "بِ", "پ": "پِ", "ت": "تِ", "ث": "ثِ", "ج": "جیم", "چ": "چِ", "ح": "حِ",
    "خ": "خِ", "د": "دال", "ذ": "ذال", "ر": "رِ", "ز": "زِ", "ژ": "ژِ", "س": "سین", "ش": "شین",
    "ص": "صاد", "ض": "ضاد", "ط": "طا", "ظ": "ظا", "ع": "عین", "غ": "غین", "ف": "فِ", "ق": "قاف",
    "ک": "کاف", "گ": "گاف", "ل": "لام", "م": "میم", "ن": "نون", "و": "واو", "ه": "هِ", "ی": "یا",
}
ALPHABET = list("ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی")
assert len(ALPHABET) == 32
NONJOIN = set("ادذرزژو")
CLASS = {}
for grp in ("سصث", "زذضظ", "تط", "هح", "اآع", "قغ"):
    for ch in grp:
        CLASS[ch] = grp[0]
def cls(ch): return CLASS.get(ch, ch)
SKELETON = ["بپتثنی", "جچحخ", "دذ", "رزژ", "سش", "صض", "طظ", "عغ", "فق", "کگ"]
def mates(ch):
    for g in SKELETON:
        if ch in g:
            return [c for c in g if c != ch]
    return []

L1 = list("ابندمرستکلوی")          # teaching order, level 1
L2 = list("پگشخزچجهقفعصحغطژثذضظ")  # teaching order, level 2
assert sorted(L1 + L2) == sorted(ALPHABET)

# ---------------------------------------------------------------- vocabulary
# picture: (dari, english, tag, also-called first letters to avoid as a distractor, what to draw)
V = {
 "water": ("آب", "water", "nature", "", "a glass of clear water with one drop above it"),
 "fire": ("آتش", "fire", "nature", "", "a small wood fire with orange flames"),
 "pomegranate": ("انار", "pomegranate", "food", "", "a red pomegranate with its crown, one cut piece showing seeds"),
 "horse": ("اسپ", "horse", "animal", "", "a brown horse standing, side view"),
 "grapes": ("انگور", "grapes", "food", "", "a bunch of green grapes with a leaf"),
 "goat": ("بز", "goat", "animal", "", "a goat with horns and a small beard, side view"),
 "almond": ("بادام", "almond", "food", "", "three almonds, one in its shell"),
 "roof": ("بام", "roof", "home", "خ", "a mud village house with a flat roof, the roof coloured strongly and an arrow-free emphasis on the roof (ladder leaning on it)"),
 "rain": ("باران", "rain", "nature", "ا", "a grey cloud with rain drops falling"),
 "shoe": ("بوت", "shoe", "thing", "ک", "one simple closed shoe, side view"),
 "bread": ("نان", "bread", "food", "", "a long flat Afghan naan with the stamped pattern"),
 "salt": ("نمک", "salt", "food", "", "a small bowl of white salt with a pinch falling into it"),
 "pear": ("ناک", "pear", "food", "", "a yellow-green pear with a stalk and leaf"),
 "tap": ("نل", "water tap", "home", "ا", "a water tap (standpipe) with water running from it"),
 "hand": ("دست", "hand", "body", "", "an open hand, palm facing the viewer"),
 "tooth": ("دندان", "tooth", "body", "", "one white tooth"),
 "tree": ("درخت", "tree", "nature", "", "a tree with a brown trunk and a round green crown"),
 "pot": ("دیگ", "cooking pot", "home", "", "a metal cooking pot with two handles and a lid"),
 "door": ("دروازه", "door", "home", "", "a closed wooden door in a mud wall"),
 "snake": ("مار", "snake", "animal", "", "a green snake curled in an S shape"),
 "moon": ("ماه", "moon", "nature", "", "a full yellow moon in a dark blue night sky with two small stars"),
 "hen": ("مرغ", "hen", "animal", "", "a brown hen standing, side view"),
 "fish": ("ماهی", "fish", "animal", "", "one fish, side view"),
 "mouse": ("موش", "mouse", "animal", "", "a grey mouse with a long tail"),
 "fox": ("روباه", "fox", "animal", "", "an orange fox with a bushy tail"),
 "rope": ("ریسمان", "rope", "thing", "", "a coil of thick rope"),
 "radio": ("رادیو", "radio", "thing", "", "a small battery radio with an aerial"),
 "apple": ("سیب", "apple", "food", "", "a red apple with a leaf"),
 "dog": ("سگ", "dog", "animal", "", "a village dog standing, side view"),
 "star": ("ستاره", "star", "nature", "", "one yellow five-pointed star"),
 "stone": ("سنگ", "stone", "nature", "", "a grey stone"),
 "basket": ("سبد", "basket", "thing", "ت", "an empty woven basket with a handle"),
 "mulberry": ("توت", "mulberry", "food", "", "white and dark mulberries on a twig with a leaf"),
 "egg": ("تخم", "egg", "food", "", "one white egg"),
 "watermelon": ("تربوز", "watermelon", "food", "", "a watermelon with one red slice cut out"),
 "ball": ("توپ", "ball", "thing", "", "a plain coloured ball"),
 "book": ("کتاب", "book", "school", "", "a closed book"),
 "key": ("کلید", "key", "thing", "", "one metal key"),
 "pigeon": ("کبوتر", "pigeon", "animal", "", "a white pigeon standing, side view"),
 "mountain": ("کوه", "mountain", "nature", "", "a mountain with snow on the top"),
 "pumpkin": ("کدو", "pumpkin", "food", "", "an orange pumpkin"),
 "lips": ("لب", "lip", "body", "د", "a closed mouth, the lips only"),
 "lemon": ("لیمو", "lemon", "food", "", "a yellow lemon with a leaf"),
 "waistcoat": ("واسکت", "waistcoat", "thing", "", "a sleeveless Afghan waistcoat with buttons, no person"),
 "ice": ("یخ", "ice", "nature", "", "a block of ice with icicles, light blue"),
 # words used in the listening rounds and rhymes
 "leaf": ("برگ", "leaf", "nature", "", "one green leaf"),
 "onion": ("پیاز", "onion", "food", "", "an onion with its dry skin"),
 "flower": ("گل", "flower", "nature", "", "one red flower with a green stem and two leaves"),
 "elephant": ("فیل", "elephant", "animal", "", "a grey elephant, side view"),
 "eye": ("چشم", "eye", "body", "", "one open eye with eyebrow"),
 "cow": ("گاو", "cow", "animal", "", "a cow, side view"),
 "donkey": ("خر", "donkey", "animal", "", "a grey donkey with long ears, side view"),
 "bridge": ("پل", "bridge", "nature", "", "a small arched bridge over a stream"),
 "well": ("چاه", "well", "home", "", "a round stone well with a bucket on a rope"),
 "bell": ("زنگ", "bell", "school", "", "a hand bell"),
 "needle": ("سوزن", "needle", "thing", "ت", "a sewing needle with a piece of thread through it"),
 "comb": ("شانه", "comb", "thing", "", "a hair comb"),
 "bed": ("تخت", "bed", "home", "چ", "a simple wooden bed with a blanket"),
 "wall": ("دیوار", "wall", "home", "", "a piece of mud-brick wall"),
 "wool": ("پشم", "wool", "thing", "", "a ball of raw white wool next to a sheep-shearing tuft"),
 "seed": ("دانه", "seed", "nature", "ت", "a few seeds or grains in a small heap"),
 "hat": ("کلاه", "hat", "thing", "", "a round embroidered Afghan cap, no person"),
 "bee": ("زنبور", "bee", "animal", "", "a yellow and black bee"),
 "pocket": ("جیب", "pocket", "thing", "", "a shirt pocket shown large on a piece of cloth"),
 # level 2
 "father": ("پدر", "father", "person", "مب", "a father: a man with a short beard in shalwar kameez and a cap, friendly, standing"),
 "cat": ("پشک", "cat", "animal", "گ", "a cat sitting"),
 "wheat": ("گندم", "wheat", "food", "", "three golden ears of wheat"),
 "ear": ("گوش", "ear", "body", "", "one ear"),
 "camel": ("شتر", "camel", "animal", "ا", "a one-humped camel, side view"),
 "candle": ("شمع", "candle", "thing", "", "a burning candle"),
 "rooster": ("خروس", "rooster", "animal", "م", "a rooster with a red comb and big tail"),
 "carrot": ("زردک", "carrot", "food", "", "an orange carrot with green top"),
 "tea": ("چای", "tea", "food", "", "a glass of tea with steam next to a teapot"),
 "umbrella": ("چتری", "umbrella", "thing", "", "an open umbrella"),
 "broom": ("جاروب", "broom", "home", "", "a short hand broom made of straw"),
 "corn": ("جواری", "corn", "food", "", "one cob of maize, husk partly open"),
 "stream": ("جوی", "stream", "nature", "داآ", "a narrow water channel running between fields"),
 "firewood": ("هیزم", "firewood", "home", "چ", "a tied bundle of firewood sticks"),
 "pen": ("قلم", "pen", "school", "", "one pen"),
 "spoon": ("قاشق", "spoon", "home", "", "one spoon"),
 "lock": ("قفل", "lock", "thing", "", "a padlock"),
 "glasses": ("عینک", "glasses", "thing", "", "a pair of eyeglasses"),
 "honey": ("عسل", "honey", "food", "", "a jar of golden honey with a spoon dripping honey"),
 "cave": ("غار", "cave", "nature", "ک", "a dark cave opening in a rock wall"),
 "pond": ("حوض", "pond, water basin", "home", "اآ", "a small square built water basin (hawz) in a yard"),
 "courtyard": ("حویلی", "courtyard", "home", "خ", "a walled courtyard seen from above the wall: mud walls, a gate, a tree inside"),
 "soap": ("صابون", "soap", "home", "", "a bar of soap with bubbles"),
 "box": ("صندوق", "chest, box", "home", "ب", "a wooden chest with a lid and a metal clasp"),
 "classroom": ("صنف", "classroom", "school", "م", "an empty classroom: blackboard, mat on the floor, small window; no people"),
 "parrot": ("طوطی", "parrot", "animal", "", "a green parrot on a perch"),
 "peacock": ("طاووس", "peacock", "animal", "", "a peacock with its tail open"),
 "hail": ("ژاله", "hail", "nature", "ب", "a dark cloud with round white hailstones falling and bouncing on the ground"),
 "school": ("مکتب", "school", "school", "ص", "a small village school building with a flag-free plain front, a door and children's shoes at the door; no people"),
 "sapling": ("نهال", "sapling", "nature", "د", "a very young tree: thin stem, a few leaves, in a small earth mound"),
}
V["roof"] = (V["roof"][0], "roof", "home", "خ", "a mud village house with a flat roof; the roof is drawn in a strong colour and a ladder leans against it")
V["school"] = (V["school"][0], "school", "school", "ص", "a small plain village school building with an open door; no people, no flag")
V["wool"] = (V["wool"][0], "wool", "thing", "", "a heap of raw white sheep wool")
SCENES = {}
ICONS = {}

def fa(p): return V[p][0]
def first(p): return fa(p)[0]

# key words without a picture
WORDS_ONLY = {"ث": ["ثمر"], "ذ": ["ذره"], "ض": ["ضعیف"], "ظ": ["ظرف"], "ف": ["فرش"], "غ": ["غذا"], "ه": ["هوا"],
              "ح": ["حلوا"], "و": [], "ی": []}

PICS = {  # per letter, pictures in teaching order
 "آ": ["water", "fire"], "ا": ["pomegranate", "horse", "grapes"],
 "ب": ["goat", "almond", "roof", "rain"], "ن": ["bread", "salt", "pear", "tap"],
 "د": ["hand", "tooth", "tree", "pot", "door"], "م": ["snake", "moon", "hen", "fish", "mouse"],
 "ر": ["fox", "rope", "radio"], "س": ["apple", "dog", "star", "stone"],
 "ت": ["mulberry", "egg", "watermelon", "ball"], "ک": ["book", "key", "pigeon", "mountain", "pumpkin"],
 "ل": ["lips", "lemon"], "و": ["waistcoat"], "ی": ["ice"],
 "پ": ["cat", "father", "onion", "bridge"], "گ": ["cow", "flower", "wheat", "ear"],
 "ش": ["camel", "comb", "candle"], "خ": ["donkey", "rooster", "courtyard"][:2],
 "ز": ["bee", "carrot", "bell"], "چ": ["eye", "tea", "umbrella", "well"],
 "ج": ["broom", "corn", "stream"], "ه": ["firewood"], "ق": ["pen", "spoon", "lock"],
 "ف": ["elephant"], "ع": ["glasses", "honey"], "ص": ["soap", "box", "classroom"],
 "ح": ["pond", "courtyard"], "غ": ["cave"], "ط": ["parrot", "peacock"], "ژ": ["hail"],
 "ث": [], "ذ": [], "ض": [], "ظ": [],
}
for L, ps in PICS.items():
    for p in ps:
        assert first(p) == L, (L, p, fa(p))

def words(L):
    return [fa(p) for p in PICS[L]] + WORDS_ONLY.get(L, [])

# ---------------------------------------------------------------- helpers
class Sheet:
    def __init__(self, header):
        self.header = header.split(",")
        self.rows = []
    def add(self, **kw):
        for k in kw:
            assert k in self.header, k
        self.rows.append([kw.get(h, "") for h in self.header])
    def write(self, path):
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(self.header)
            w.writerows(self.rows)

USED = {1: set(), 2: set()}
def use(level, *things):
    for t in things:
        for s in t.split("|"):
            s = s.strip()
            if not s or s[:2] in ("f:", "t:") or s.startswith("lf:") or s == "snd":
                continue
            if s.startswith("p:"):
                s = s[2:].split("*")[0]
            if not s.startswith("scene_"):
                assert s in V, s
            USED[level].add(s)

LP = "round,intro_fa,say_en,say_fa,show,answer,distractors,help_fa,hop"

class Garden:
    """Builds alefba_garden rows for one level."""
    def __init__(self, level, pic_pool, seed):
        self.level, self.pool, self.rng = level, pic_pool, random.Random(seed)
        self.sheet = Sheet(LP)
        self.taught = []          # letters known so far (for distractors)
        self.fallback = []
        self.intro = {}
    def row(self, rnd, **kw):
        if rnd in self.intro:
            kw["intro_fa"] = self.intro.pop(rnd)
        use(self.level, kw.get("show", ""), kw.get("answer", ""), kw.get("distractors", ""))
        assert len(kw["distractors"].split("|")) in (2, 3), kw
        self.sheet.add(round=rnd, **kw)
    def letter_distractors(self, L, by_sound=True, pool=None, lookalike=False):
        def ok(c):
            if c == L: return False
            if by_sound: return cls(c) != cls(L)
            return NAME[c] != NAME[L] and not (L in "اآ" and c in "اآ")
        pool = [c for c in (pool or self.taught) if ok(c)]
        if len(pool) < 3:
            extra = [c for c in self.fallback if ok(c) and c not in pool]
            self.rng.shuffle(extra)
            pool += extra[:3 - len(pool)]
        out = []
        if lookalike:
            m = [c for c in mates(L) if c in pool]
            self.rng.shuffle(m)
            out += m[:1 if by_sound else 2]
        rest = [c for c in pool if c not in out]
        self.rng.shuffle(rest)
        out += rest[: 3 - len(out)]
        assert len(out) == 3, (L, out)
        self.rng.shuffle(out)
        return "|".join("f:" + c for c in out)
    def pic_distractors(self, L, answer):
        bad = cls(L)
        pool = [p for p in self.pool if p != answer and cls(first(p)) != bad
                and all(cls(c) != bad for c in V[p][3])]
        out = self.rng.sample(pool, 3)
        return "|".join(out)
    # question types
    def a(self, rnd, L, word, **kw):   # hear the letter with a key word, pick the letter
        n = NAME[L]
        self.row(rnd, say_fa=f"{n}، مثل {word}. کدام حرف {n} است؟", answer="f:" + L,
                 distractors=self.letter_distractors(L, True, **kw), help_fa=f"{word} با {n} شروع می‌شود.")
    def b(self, rnd, L, pic):          # see the letter, pick the picture that starts with it
        n = NAME[L]
        self.row(rnd, say_fa=f"این حرف {n} است. کدام تصویر با {n} شروع می‌شود؟", show="f:" + L, answer=pic,
                 distractors=self.pic_distractors(L, pic), help_fa=f"{fa(pic)} با {n} شروع می‌شود.")
    def c(self, rnd, L, pic, **kw):    # see a picture, hear its word, pick the first letter
        n, w = NAME[L], fa(pic)
        self.row(rnd, say_fa=f"{w}. {w} با کدام حرف شروع می‌شود؟", show=pic, answer="f:" + L,
                 distractors=self.letter_distractors(L, True, **kw), help_fa=f"{w} با {n} شروع می‌شود.")
    def n(self, rnd, L, **kw):         # letter name only
        n = NAME[L]
        self.row(rnd, say_fa=f"حرف {n} کدام است؟", answer="f:" + L,
                 distractors=self.letter_distractors(L, False, **kw), help_fa=f"این حرف {n} است.", show="")
    def oral(self, rnd, say, answer, distractors, help_fa):
        self.row(rnd, say_fa=say, answer=answer, distractors=distractors, help_fa=help_fa)


def sorter_sheet(level, rounds):
    """rounds: list of (round, intro, [(letter, form), ...])"""
    BASKET = {"start": ("f:اول", "اول کلمه"), "middle": ("f:وسط", "وسط کلمه"),
              "end": ("f:آخر", "آخر کلمه"), "alone": ("f:تنها", "تنها")}
    sh = Sheet("round,intro_fa,thing,say_en,say_fa,basket,basket_say_fa")
    for rnd, intro, items in rounds:
        assert 6 <= len(items) <= 10, (rnd, len(items))
        seen = set()
        for i, (L, form) in enumerate(items):
            assert (L, form) not in seen
            seen.add((L, form))
            if L in NONJOIN:
                assert form in ("alone", "end"), (L, form)
            b, bs = BASKET[form]
            sh.add(round=rnd, intro_fa=intro if i == 0 else "", thing=f"lf:{L}:{form}",
                   say_fa=f"حرف {NAME[L]}", basket=b, basket_say_fa=bs)
    return sh

def full(*letters, seed=0):
    """All forms of the given letters, interleaved so the same letter does not come twice in a row."""
    forms = {True: ["alone", "end"], False: ["start", "end", "middle", "alone"]}
    cols = []
    for k, L in enumerate(letters):
        f = forms[L in NONJOIN][:]
        f = f[k % len(f):] + f[:k % len(f)]
        cols.append([(L, x) for x in f])
    out = []
    while any(cols):
        for c in cols:
            if c:
                out.append(c.pop(0))
    return out

def weaver_sheet(level, rounds, allowed_by_round):
    sh = Sheet("round,say_en,say_fa,tiles,extra,rtl,done_en,done_fa,help_fa")
    rng = random.Random(level * 7)
    for rnd, items in rounds:
        allowed = allowed_by_round[rnd]
        assert len(items) == 5, rnd
        for word, done in items:
            letters = list(word)
            assert all(c in allowed for c in letters), (word, [c for c in letters if c not in allowed])
            pool = [c for c in allowed if c not in letters and c != "آ" and all(cls(c) != cls(x) for x in letters)]
            extra = rng.sample(sorted(pool), min(len(pool), 2 if len(letters) <= 4 else 1))
            assert len(letters) + len(extra) <= 8
            sh.add(round=rnd, say_fa=f"{word}. کلمه {word} را بساز.", tiles="|".join("f:" + c for c in letters),
                   extra="|".join("f:" + c for c in extra), rtl="yes", done_fa=done)
    return sh

def catch_sheet(rounds):
    sh = Sheet("round,intro_fa,say_en,say_fa,targets,others,need")
    for rnd, intro, items in rounds:
        assert 6 <= len(items) <= 10, rnd
        for i, (say, target, others) in enumerate(items):
            assert target not in others and len(others) == 3
            sh.add(round=rnd, intro_fa=intro if i == 0 else "", say_fa=say, targets="f:" + target,
                   others="|".join("f:" + o for o in others), need="3")
    return sh

def catch_letters(words_letters, pool, seed, where="اول", lookalike=False):
    rng = random.Random(seed)
    out = []
    for word, L in words_letters:
        cand = [c for c in pool if cls(c) != cls(L)]
        pick = []
        if lookalike:
            m = [c for c in mates(L) if c in cand]
            rng.shuffle(m)
            pick += m[:1]
        rest = [c for c in cand if c not in pick]
        rng.shuffle(rest)
        pick += rest[:3 - len(pick)]
        out.append((f"حرف {where} «{word}» را بگیر.", L, pick))
    return out

def story_sheet(level, stories):
    sh = Sheet("round,picture,say_en,say_fa,show_fa,choices,right,wrong_say_fa,wrong_picture")
    for rnd, pages in stories:
        for p in pages:
            if len(p) == 2:
                scene, text = p
                sh.add(round=rnd, picture=scene, say_fa=text, show_fa=text)
            else:
                scene, q, choices, right, wrong = p
                use(level, choices)
                sh.add(round=rnd, picture=scene, say_fa=q, show_fa=q if level == 2 else "", choices=choices, right=right, wrong_say_fa=wrong)
    return sh

def pairs_sheet(level, rounds):
    sh = Sheet("round,intro_fa,a,b,say_en,say_fa")
    for rnd, intro, items in rounds:
        assert 3 <= len(items) <= 6
        for i, (a, b, say) in enumerate(items):
            use(level, a, b)
            sh.add(round=rnd, intro_fa=intro if i == 0 else "", a=a, b=b, say_fa=say)
    return sh

def write_pack(level, meta, sheets, unit_of):
    d = OUT / str(level)
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.csv"):
        old.unlink()
    (d / "pack.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", "utf-8")
    for name, sh in sheets.items():
        sh.write(d / name)
    items = Sheet("unit,key,en,fa,picture,tags")
    for p in sorted(USED[level], key=lambda p: (unit_of(p), ALPHABET.index("ا" if first(p) == "آ" else first(p)), p)):
        if p.startswith("scene_"):
            continue
        items.add(unit=unit_of(p), key=p, en=V[p][1], fa=V[p][0], picture=p, tags=V[p][2])
    items.write(d / "items.csv")

def game(gid, engine, letter, title_en, title_fa, intro, icon, v1=False):
    g = {"id": gid, "engine": engine, "letter": letter, "title_en": title_en, "title_fa": title_fa,
         "intro_fa": intro, "icon": icon}
    if v1:
        g["v1"] = True
    g["sheet"] = gid + ".csv"
    ICONS[icon] = True
    return g

SHAPES_INTRO = "هر حرف چند شکل دارد. هر شکل را در سبد درست بگذار: اول کلمه، وسط کلمه، آخر کلمه، یا تنها."
NONJOIN_INTRO = "این حرف‌ها به حرف بعد از خود نمی‌چسبند. برای همین فقط دو شکل دارند. هر شکل را در سبد درست بگذار."

# ================================================================ LEVEL 1
L1_POOL = [p for L in ["آ"] + L1 for p in PICS.get(L, [])] + [
    "leaf", "onion", "flower", "elephant", "eye", "cow", "donkey", "bridge", "well", "bell"]
g = Garden(1, L1_POOL, 11)
L1SYM = ["آ"] + L1
g.taught = []
g.fallback = L1SYM  # level 1: wrong letters come from letters already met, then from the level's other letters
def teach1(*ls):
    for L in ls:
        if L not in g.taught: g.taught.append(L)

def intro2(rnd, X, Y):
    teach1(X, Y)
    px, py, wx, wy = PICS[X], PICS[Y], words(X), words(Y)
    g.a(rnd, X, wx[0]); g.b(rnd, X, px[0])
    g.a(rnd, Y, wy[0]); g.b(rnd, Y, py[0])
    g.c(rnd, X, px[1] if len(px) > 1 else px[0])
    g.c(rnd, Y, py[1] if len(py) > 1 else py[0])
    if len(px) > 2: g.b(rnd, X, px[2])
    else: g.n(rnd, X)
    if len(wy) > 2: g.a(rnd, Y, wy[2])
    else: g.n(rnd, Y)

def intro1(rnd, X, review, k=0):
    teach1(X)
    px, wx = PICS[X], words(X)
    g.a(rnd, X, wx[0]); g.b(rnd, X, px[0])
    if len(px) > 1:
        g.c(rnd, X, px[1]); g.b(rnd, X, px[-1])
    else:
        g.c(rnd, X, px[0]); g.n(rnd, X)
    for i, R in enumerate(review):
        pr = PICS[R]
        pic = pr[(i + k + 1) % len(pr)]
        if i % 2 == 0: g.b(rnd, R, pic)
        else: g.c(rnd, R, pic)

# 01: alef (آ and ا) and be
g.intro["01"] = "حرف‌ها را یاد می‌گیریم. گوش کن و جواب درست را انتخاب کن."
teach1("آ", "ا", "ب")
g.a("01", "آ", "آب"); g.b("01", "آ", "water")
g.a("01", "ا", "انار"); g.b("01", "ا", "pomegranate")
g.a("01", "ب", "بز"); g.b("01", "ب", "goat")
g.c("01", "ب", "almond"); g.c("01", "ا", "horse")
intro1("02", "ن", ["ب", "ا", "آ", "ب"])
g.intro["03"] = "حالا فقط گوش کن. کدام کلمه مثل کلمه اول شروع می‌شود؟"
for w, ans, d in [
    ("مار", "moon", "goat|apple|hand"), ("بز", "almond", "bread|dog|book"), ("نان", "salt", "water|hen|tooth"),
    ("دست", "tree", "fish|mulberry|key"), ("سیب", "dog", "fox|pomegranate|pear"),
    ("کتاب", "pigeon", "snake|lemon|rain"), ("توت", "egg", "star|mouse|door"), ("روباه", "rope", "lips|pumpkin|horse")]:
    assert first(ans) == w[0] and all(first(x) != w[0] for x in d.split("|"))
    g.oral("03", f"{w}. کدام کلمه مثل {w} شروع می‌شود؟", ans, d, f"{w}، {fa(ans)}. هر دو با یک صدا شروع می‌شوند.")
intro2("04", "د", "م")
intro1("05", "ر", ["د", "م", "ن", "ب"])
g.intro["06"] = "گوش کن. کدام کلمه مثل کلمه اول تمام می‌شود؟"
for w, ans, d in [
    ("سگ", "leaf", "water|bread|snake"), ("آب", "apple", "hand|moon|flower"), ("مار", "donkey", "goat|book|tooth"),
    ("بز", "onion", "dog|mulberry|roof"), ("دست", "tree", "rain|stone|lips"), ("گل", "elephant", "horse|hen|salt"),
    ("توپ", "horse", "star|pear|key"), ("بام", "eye", "fox|pomegranate|cow")]:
    assert fa(ans)[-1] == w[-1] and all(fa(x)[-1] != w[-1] for x in d.split("|")), w
    g.oral("06", f"{w}. کدام کلمه مثل {w} تمام می‌شود؟", ans, d, f"{w}، {fa(ans)}. هر دو با یک صدا تمام می‌شوند.")
intro2("07", "س", "ت")
intro1("08", "ک", ["س", "ت", "ر", "د"])
g.intro["09"] = "بعضی کلمه‌ها آخرشان مثل هم است، مثل مار و انار. گوش کن و کلمه‌ای را پیدا کن که آخرش مثل کلمه اول است."
for w, ans, d in [
    ("مار", "pomegranate", "fish|goat|bread"), ("گل", "bridge", "leaf|cow|apple"), ("نان", "tooth", "salt|water|hand"),
    ("ماه", "well", "snake|fish|star"), ("سر", "donkey", "stone|dog|mulberry"), ("توت", "shoe", "egg|ball|key"),
    ("سنگ", "bell", "apple|star|lips"), ("آب", "book", "horse|pomegranate|roof")]:
    assert fa(ans)[-1] == w[-1], w
    g.oral("09", f"{w}. آخر کدام کلمه مثل {w} است؟", ans, d, f"{w}، {fa(ans)}. آخر هر دو مثل هم است.")
# 10: lam and waw
teach1("ل", "و")
g.a("10", "ل", "لب"); g.b("10", "ل", "lips")
g.a("10", "و", "واسکت"); g.b("10", "و", "waistcoat")
g.c("10", "ل", "lemon"); g.c("10", "و", "waistcoat")
g.b("10", "ل", "lemon"); g.n("10", "و")
intro1("11", "ی", ["ل", "ک", "و", "س"])
g.intro["12"] = "همه حرف‌ها را با هم تمرین می‌کنیم."
for i, L in enumerate(["ب", "م", "س", "ک", "ن", "د", "ت", "ر"]):
    if i % 2 == 0: g.a("12", L, words(L)[2])
    else: g.c("12", L, PICS[L][-1])
for L, p in [("ا", "grapes"), ("آ", "fire"), ("ل", "lemon"), ("ی", "ice"), ("ب", "rain"), ("ن", "pear"), ("م", "hen"), ("ت", "watermelon")]:
    g.b("13", L, p)
g.intro["14"] = "گوش کن و فکر کن: اول کلمه، آخر کلمه."
for say, ans, d, h in [
    ("کلید. کدام کلمه مثل کلید شروع می‌شود؟", "mountain", "lemon|hand|moon", "کلید، کوه. هر دو با یک صدا شروع می‌شوند."),
    ("لب. کدام کلمه مثل لب شروع می‌شود؟", "lemon", "bread|star|goat", "لب، لیمو. هر دو با یک صدا شروع می‌شوند."),
    ("ماهی. کدام کلمه مثل ماهی شروع می‌شود؟", "mouse", "pigeon|tree|apple", "ماهی، موش. هر دو با یک صدا شروع می‌شوند."),
    ("نان. کدام کلمه مثل نان تمام می‌شود؟", "tooth", "book|fox|flower", "نان، دندان. هر دو با یک صدا تمام می‌شوند."),
    ("سیب. کدام کلمه مثل سیب تمام می‌شود؟", "book", "salt|tree|snake", "سیب، کتاب. هر دو با یک صدا تمام می‌شوند."),
    ("انار. آخر کدام کلمه مثل انار است؟", "snake", "pear|water|hen", "انار، مار. آخر هر دو مثل هم است."),
    ("تخت. آخر کدام کلمه مثل تخت است؟", "tree", "egg|rain|key", "تخت، درخت. آخر هر دو مثل هم است."),
    ("باران. آخر کدام کلمه مثل باران است؟", "bread", "goat|roof|leaf", "باران، نان. آخر هر دو مثل هم است.")]:
    g.oral("14", say, ans, d, h)
garden1 = g.sheet

shapes1 = sorter_sheet(1, [
    ("01", "", full("ب", "ن")),
    ("02", NONJOIN_INTRO, full("ا", "د", "ر")),
    ("03", "", full("م", "س")),
    ("04", "", full("ت", "ک")),
    ("05", "", full("ل", "ی")),
    ("06", NONJOIN_INTRO, full("و", "ا", "د", "ر")),
    ("07", "", [("ب", "end"), ("م", "start"), ("س", "middle"), ("ک", "alone"), ("ل", "start"), ("ی", "middle"), ("ن", "end"), ("ت", "alone")]),
    ("08", "", [("ب", "middle"), ("م", "end"), ("س", "alone"), ("ک", "start"), ("ل", "end"), ("ی", "start"), ("ن", "middle"), ("ت", "start")]),
])

A1 = set("آابن"); A2 = A1 | set("دمر"); A3 = A2 | set("ستک"); A4 = A3 | set("لوی")
weaver1 = weaver_sheet(1, [
    ("01", [("آب", "آب. آب پاک است."), ("با", "با. من با مادر می‌روم."), ("آن", "آن. آن نان است."),
            ("نان", "نان. نان گرم است."), ("بابا", "بابا. بابا آمد.")]),
    ("02", [("باد", "باد. باد می‌وزد."), ("بام", "بام. بام خانه."), ("مار", "مار. مار دراز است."),
            ("در", "در. در باز است."), ("ابر", "ابر. ابر باران دارد.")]),
    ("03", [("نام", "نام. هر کس یک نام دارد."), ("آرد", "آرد. نان از آرد است."), ("انار", "انار. انار سرخ است."),
            ("مادر", "مادر. مادر مهربان است."), ("باران", "باران. باران می‌بارد.")]),
    ("04", [("سر", "سر. این سر من است."), ("دست", "دست. دست پاک."), ("کتاب", "کتاب. کتاب من."),
            ("نمک", "نمک. نمک سفید است."), ("ماست", "ماست. ماست سفید است.")]),
    ("05", [("تار", "تار. تار و سوزن."), ("ناک", "ناک. ناک شیرین است."), ("سبد", "سبد. سبد پر از سیب است."),
            ("کارد", "کارد. کارد تیز است."), ("آسمان", "آسمان. آسمان آبی است.")]),
    ("06", [("لب", "لب. لب و دندان."), ("توت", "توت. توت شیرین است."), ("سیب", "سیب. سیب سرخ است."),
            ("کدو", "کدو. کدو بزرگ است."), ("لیمو", "لیمو. لیمو ترش است.")]),
], {"01": A1, "02": A2, "03": A2, "04": A3, "05": A3, "06": A4})

SYL_INTRO = "هر کلمه از چند بخش ساخته شده است. بادام: با، دام. گوش کن و بخش درست را بگیر."
catch1 = catch_sheet([
    ("01", "", catch_letters([("نان", "ن"), ("بز", "ب"), ("دست", "د"), ("مار", "م"), ("روباه", "ر"), ("آب", "آ")], L1SYM, 21)),
    ("02", "", catch_letters([("سیب", "س"), ("توت", "ت"), ("کتاب", "ک"), ("لب", "ل"), ("یخ", "ی"), ("واسکت", "و")], L1SYM, 22)),
    ("03", "حالا به آخر کلمه گوش کن. حرف آخر را بگیر.",
     catch_letters([("آب", "ب"), ("نان", "ن"), ("مار", "ر"), ("بام", "م"), ("دست", "ت"), ("نمک", "ک")], L1, 23, where="آخر")),
    ("04", SYL_INTRO, [
        ("بخش اول «بادام» را بگیر.", "با", ["بو", "بی", "ما"]),
        ("بخش اول «ماهی» را بگیر.", "ما", ["مو", "با", "نا"]),
        ("بخش اول «نامه» را بگیر.", "نا", ["نو", "ما", "نی"]),
        ("بخش اول «دانه» را بگیر.", "دا", ["دو", "را", "دی"]),
        ("بخش اول «لیمو» را بگیر.", "لی", ["لا", "لو", "بی"]),
        ("بخش اول «سوزن» را بگیر.", "سو", ["سا", "سی", "تو"]),
    ]),
])

story1 = story_sheet(1, [
    ("01", [
        ("scene_girl_with_goat", "لیلا یک بز کوچک دارد."),
        ("scene_goat_leaves_yard", "یک روز بز از حویلی بیرون رفت."),
        ("scene_girl_calls_goat", "لیلا بز را صدا کرد، اما بز نیامد."),
        ("scene_girl_looks_by_stream", "لیلا پشت درخت و کنار جوی را دید."),
        ("scene_goat_eats_leaves", "بز در باغ بود و برگ می‌خورد."),
        ("scene_girl_brings_goat_home", "لیلا به بز آب داد و او را به خانه آورد."),
        ("scene_girl_with_goat", "لیلا کدام حیوان را دارد؟", "goat|cow|donkey", "goat", "نه. لیلا یک بز دارد."),
        ("scene_goat_eats_leaves", "بز در باغ چه می‌خورد؟", "leaf|bread|apple", "leaf", "نه. بز برگ می‌خورد."),
    ]),
    ("02", [
        ("scene_mother_bakes_bread", "مادر در تنور نان می‌پزد."),
        ("scene_boy_takes_bread", "فرید سه نان گرم می‌گیرد."),
        ("scene_boy_gives_bread_grandfather", "او یک نان را به پدرکلان می‌دهد."),
        ("scene_boy_gives_bread_sister", "یک نان را به خواهر کوچکش می‌دهد."),
        ("scene_boy_one_bread", "یک نان برای خودش می‌ماند."),
        ("scene_family_eats_bread_tea", "همه با هم نان و چای می‌خورند."),
        ("scene_mother_bakes_bread", "مادر چه می‌پزد؟", "bread|egg|apple", "bread", "نه. مادر نان می‌پزد."),
        ("scene_boy_takes_bread", "فرید چند نان گرفت؟", "p:bread*3|p:bread*2|p:bread*5", "p:bread*3", "نه. فرید سه نان گرفت."),
    ]),
])
SCENES.update({
 "scene_girl_with_goat": "a girl of about 8 (headscarf, long dress over trousers) kneels in a walled mud courtyard and strokes a small goat",
 "scene_goat_leaves_yard": "the small goat walks out through the open courtyard gate; nobody is watching",
 "scene_girl_calls_goat": "the same girl stands at the gate with a hand at her mouth, calling; the lane is empty",
 "scene_girl_looks_by_stream": "the girl looks behind a tree next to a narrow water channel",
 "scene_goat_eats_leaves": "the goat stands in an orchard eating leaves from a low branch",
 "scene_girl_brings_goat_home": "the girl holds a bowl of water for the goat in front of the house; both look content",
 "scene_mother_bakes_bread": "a mother (headscarf, modest dress) sits by a clay tandoor oven in the ground and lifts out a flat bread",
 "scene_boy_takes_bread": "a boy of about 9 (shalwar kameez, cap) holds three flat breads in a cloth",
 "scene_boy_gives_bread_grandfather": "the boy hands one bread to a seated grandfather with a white beard and turban",
 "scene_boy_gives_bread_sister": "the boy hands one bread to his small sister (about 4, small headscarf)",
 "scene_boy_one_bread": "the boy smiles, holding the one bread that is left",
 "scene_family_eats_bread_tea": "the family (mother, grandfather, boy, small sister) sit on a mat around a cloth with bread and tea glasses",
})

verse1 = pairs_sheet(1, [
    ("01", "", [("snake", "pomegranate", "مار، انار"), ("flower", "bridge", "گل، پل"), ("bread", "tooth", "نان، دندان"),
                ("moon", "well", "ماه، چاه"), ("stone", "bell", "سنگ، زنگ")]),
    ("02", "", [("mulberry", "shoe", "توت، بوت"), ("water", "book", "آب، کتاب"), ("comb", "seed", "شانه، دانه"),
                ("bed", "tree", "تخت، درخت"), ("roof", "almond", "بام، بادام")]),
    ("03", "", [("fox", "hat", "روباه، کلاه"), ("bee", "grapes", "زنبور، انگور"), ("apple", "pocket", "سیب، جیب"),
                ("eye", "wool", "چشم، پشم")]),
    ("04", "", [("snake", "wall", "مار، دیوار"), ("bread", "rain", "نان، باران"), ("well", "hat", "چاه، کلاه"),
                ("flower", "bridge", "گل، پل"), ("eye", "wool", "چشم، پشم")]),
])

meta1 = {"pack": "fa-1", "subject": "fa", "level": 1, "version": 1,
         "title_en": "Dari 1: Sounds and first letters", "title_fa": "دری ۱: صداها و حرف‌های اول",
         "games": [
    game("alefba_garden", "listen_pick", "a", "Alefba Garden", "باغ الفبا", "گوش کن و جواب درست را انتخاب کن.", "flower", True),
    game("letter_shapes", "sorter", "b", "Letter Shapes", "شکل حرف‌ها", SHAPES_INTRO, "basket", True),
    game("word_weaver", "builder", "c", "Word Weaver", "کلمه‌باف", "حرف‌ها را از راست به چپ کنار هم بگذار و کلمه بساز.", "rope"),
    game("syllable_catch", "catch", "d", "Syllable Catch", "بگیر بگیر", "گوش کن و فقط حرف درست را بگیر.", "ball"),
    game("read_along", "story", "e", "Read Along", "با هم بخوانیم", "به قصه گوش کن. بعد به سوال‌ها جواب بده.", "book"),
    game("verse_corner", "pairs", "f", "Verse Corner", "گوشه شعر", "دو تصویر را پیدا کن که آخر نام‌شان مثل هم است.", "moon"),
]}
use(1, "flower", "basket", "rope", "ball", "book", "moon")
INTRO_ROUND_1 = {"آ": "01", "ا": "01", "ب": "01", "ن": "02", "د": "04", "م": "04", "ر": "05", "س": "07", "ت": "07",
                 "ک": "08", "ل": "10", "و": "10", "ی": "11"}
write_pack(1, meta1, {"alefba_garden.csv": garden1, "letter_shapes.csv": shapes1, "word_weaver.csv": weaver1,
                      "syllable_catch.csv": catch1, "read_along.csv": story1, "verse_corner.csv": verse1},
           lambda p: INTRO_ROUND_1.get(first(p), "20"))

# ================================================================ LEVEL 2
L2_POOL = [p for p in V if p not in ("school", "sapling", "wool", "seed", "pocket", "hat", "wall", "bed", "needle")]
g = Garden(2, L2_POOL, 12)
g.taught = L1[:]
g.fallback = ALPHABET[:]

def teach(*letters):
    for L in letters:
        if L not in g.taught:
            g.taught.append(L)

def l2_intro2(rnd, X, Y):
    teach(X, Y)
    for L in (X, Y):
        g.a(rnd, L, words(L)[0], lookalike=True)
        g.b(rnd, L, PICS[L][0])
    for L in (X, Y):
        ps, ws = PICS[L], words(L)
        if len(ps) > 1:
            g.c(rnd, L, ps[1], lookalike=True)
            if len(ps) > 2: g.b(rnd, L, ps[2])
            elif L not in "حه": g.n(rnd, L, lookalike=True)
            else: g.b(rnd, L, ps[1])
        else:
            g.a(rnd, L, ws[1] if len(ws) > 1 else ws[0], lookalike=True) if len(ws) > 1 else g.c(rnd, L, ps[0], lookalike=True)
            if L not in "حه": g.n(rnd, L, lookalike=True)
            else: g.c(rnd, L, ps[0], lookalike=True)

g.intro["01"] = "حرف‌های نو را یاد می‌گیریم. گوش کن و جواب درست را انتخاب کن."
l2_intro2("01", "پ", "گ")
l2_intro2("02", "ش", "خ")
l2_intro2("03", "ز", "چ")
l2_intro2("04", "ج", "ه")
l2_intro2("05", "ق", "ف")
g.intro["06"] = "حرف‌هایی را که یاد گرفتی با هم تمرین می‌کنیم."
for L, p, t in [("پ", "onion", "c"), ("گ", "wheat", "b"), ("ش", "candle", "c"), ("خ", "rooster", "b"),
                ("ز", "bell", "c"), ("چ", "umbrella", "b"), ("ج", "stream", "c"), ("ق", "lock", "b")]:
    (g.c if t == "c" else g.b)("06", L, p, **({"lookalike": True} if t == "c" else {}))
l2_intro2("07", "ع", "ص")
l2_intro2("08", "ح", "غ")
l2_intro2("09", "ط", "ژ")
# 10: four rare letters. Each has a common sound; the name tells them apart.
g.intro["10"] = "این چهار حرف کم دیده می‌شوند. نام هر کدام را خوب یاد بگیر."
teach("ث", "ذ", "ض", "ظ")
for L in "ثذضظ":
    g.a("10", L, words(L)[0], lookalike=True)
for L in "ذظثض":
    g.n("10", L, lookalike=True)
g.intro["11"] = "هر حرف یک نام دارد. به نام حرف گوش کن و آن را پیدا کن."
g.taught = ALPHABET[:]
for L in ["ا", "ج", "د", "ش", "م", "ق", "ن", "گ", "س", "ب"]:
    g.n("11", L, lookalike=True)
g.intro["12"] = "هر حرف یک نام دارد. به نام حرف گوش کن و آن را پیدا کن."
for L in ["ک", "ع", "ل", "ص", "و", "غ", "ی", "ض", "ت", "ر"]:
    g.n("12", L, lookalike=True)
g.intro["13"] = "بالا یا پایین حرف گاهی نشانه کوچک است: زبر، زیر و پیش. نشانه صدای حرف را نشان می‌دهد. گوش کن و کلمه درست را انتخاب کن."
for w, d, h in [
    ("گُل", "گِل|گَل", "گُل پیش دارد."), ("گِل", "گُل|گَل", "گِل زیر دارد."), ("سَر", "سِر|سُر", "سَر زبر دارد."),
    ("پُر", "پَر|پِر", "پُر پیش دارد."), ("پَر", "پُر|پِر", "پَر زبر دارد."), ("دِل", "دَل|دُل", "دِل زیر دارد."),
    ("بُز", "بَز|بِز", "بُز پیش دارد."), ("شَب", "شِب|شُب", "شَب زبر دارد.")]:
    g.sheet.add(round="13", intro_fa=g.intro.pop("13", ""), say_fa=f"{w}. کدام کلمه {w} است؟", answer="f:" + w,
                distractors="|".join("f:" + x for x in d.split("|")), help_fa=h)
g.intro["14"] = "همه الفبا را با هم تمرین می‌کنیم."
for L, p, t in [("ع", "honey", "c"), ("ص", "box", "b"), ("ط", "peacock", "c"), ("ح", "pond", "b"),
                ("ه", "firewood", "c"), ("ف", "elephant", "b"), ("غ", "cave", "c"), ("ژ", "hail", "b"),
                ("ک", "pigeon", "c"), ("د", "pot", "b")]:
    (g.c if t == "c" else g.b)("14", L, p, **({"lookalike": True} if t == "c" else {}))
garden2 = g.sheet

shapes2 = sorter_sheet(2, [
    ("01", "", full("پ", "گ")), ("02", "", full("ش", "خ")), ("03", "", full("ج", "چ")), ("04", "", full("ه", "ع")),
    ("05", "", full("ف", "ق")), ("06", "", full("ص", "ط")), ("07", "", full("ح", "غ")), ("08", "", full("ث", "ض")),
    ("09", "حرف‌های ذال، زِ و ژِ به حرف بعد از خود نمی‌چسبند و فقط دو شکل دارند. هر شکل را در سبد درست بگذار.",
     full("ظ", "ذ", "ز", "ژ")),
    ("10", "", [("پ", "middle"), ("ش", "start"), ("ج", "end"), ("ه", "middle"), ("ع", "alone"), ("ف", "start"), ("ق", "end"), ("گ", "middle")]),
    ("11", "", [("خ", "middle"), ("چ", "start"), ("ه", "end"), ("ع", "middle"), ("ص", "alone"), ("ط", "start"), ("ح", "end"), ("غ", "middle")]),
    ("12", "", [("ی", "start"), ("ک", "middle"), ("ن", "end"), ("ه", "start"), ("ع", "end"), ("غ", "start"), ("ث", "middle"), ("ض", "alone")]),
])

ALL = set(ALPHABET) | {"آ"}
weaver2 = weaver_sheet(2, [
    ("01", [("پدر", "پدر. پدر از کار آمد."), ("چای", "چای. چای گرم است."), ("خانه", "خانه. خانه ما."),
            ("گاو", "گاو. گاو شیر می‌دهد."), ("شب", "شب. شب تاریک است.")]),
    ("02", [("قلم", "قلم. قلم و کتاب."), ("فیل", "فیل. فیل بزرگ است."), ("زنگ", "زنگ. زنگ مکتب."),
            ("جوی", "جوی. آب در جوی است."), ("حوض", "حوض. حوض پر از آب است.")]),
    ("03", [("صنف", "صنف. صنف ما پاک است."), ("طوطی", "طوطی. طوطی سبز است."), ("عسل", "عسل. عسل شیرین است."),
            ("غار", "غار. غار تاریک است."), ("ژاله", "ژاله. ژاله می‌بارد.")]),
    ("04", [("مکتب", "مکتب. من به مکتب می‌روم."), ("درخت", "درخت. درخت سبز است."), ("گندم", "گندم. نان از گندم است."),
            ("خروس", "خروس. خروس صبح بانگ می‌دهد."), ("چشم", "چشم. چشم می‌بیند.")]),
    ("05", [("پشک", "پشک. پشک شیر می‌خورد."), ("برف", "برف. برف سفید است."), ("کاغذ", "کاغذ. کاغذ و قلم."),
            ("ظرف", "ظرف. ظرف پاک."), ("ثمر", "ثمر. درخت ثمر می‌دهد.")]),
    ("06", [("روباه", "روباه. روباه زیرک است."), ("ستاره", "ستاره. ستاره در آسمان است."), ("دختر", "دختر. دختر کتاب می‌خواند."),
            ("بچه", "بچه. بچه کتاب می‌خواند."), ("انگور", "انگور. انگور شیرین است.")]),
], {r: ALL for r in ("01", "02", "03", "04", "05", "06")})

catch2 = catch_sheet([
    ("01", "", catch_letters([("پدر", "پ"), ("گاو", "گ"), ("شتر", "ش"), ("خانه", "خ"), ("زنگ", "ز"), ("چشم", "چ"),
                              ("جوی", "ج"), ("هیزم", "ه")], ALPHABET, 31, lookalike=True)),
    ("02", "", catch_letters([("قلم", "ق"), ("فیل", "ف"), ("عسل", "ع"), ("غار", "غ"), ("حوض", "ح"), ("صابون", "ص"),
                              ("طوطی", "ط"), ("ژاله", "ژ")], ALPHABET, 32, lookalike=True)),
    ("03", SYL_INTRO, [
        ("بخش اول «خانه» را بگیر.", "خا", ["خو", "جا", "خی"]),
        ("بخش اول «شانه» را بگیر.", "شا", ["شو", "شی", "سا"]),
        ("بخش اول «قالین» را بگیر.", "قا", ["فا", "قو", "قی"]),
        ("بخش اول «جاروب» را بگیر.", "جا", ["چا", "خا", "جو"]),
        ("بخش اول «طوطی» را بگیر.", "طو", ["طا", "طی", "قو"]),
        ("بخش اول «زانو» را بگیر.", "زا", ["زو", "را", "زی"]),
        ("بخش اول «پیاله» را بگیر.", "پی", ["پا", "پو", "بی"]),
        ("بخش اول «هیزم» را بگیر.", "هی", ["ها", "هو", "می"]),
    ]),
    ("04", "حالا به آخر کلمه گوش کن. ماهی: ما، هی. بخش آخر را بگیر.", [
        ("بخش آخر «ماهی» را بگیر.", "هی", ["ها", "می", "هو"]),
        ("بخش آخر «طوطی» را بگیر.", "طی", ["طو", "طا", "نی"]),
        ("بخش آخر «لیمو» را بگیر.", "مو", ["ما", "می", "لو"]),
        ("بخش آخر «زانو» را بگیر.", "نو", ["نا", "نی", "زو"]),
        ("بخش آخر «کدو» را بگیر.", "دو", ["دا", "دی", "کو"]),
        ("بخش آخر «دریا» را بگیر.", "یا", ["یو", "با", "ری"]),
        ("بخش آخر «شانه» را بگیر.", "نه", ["نا", "نی", "مه"]),
        ("بخش آخر «ستاره» را بگیر.", "ره", ["را", "رو", "ری"]),
    ]),
])

story2 = story_sheet(2, [
    ("01", [
        ("scene_girl_walks_to_school", "نرگس به مکتب می‌رود."),
        ("scene_girl_sees_cat", "در راه یک پشک می‌بیند."),
        ("scene_hungry_cat", "پشک گرسنه است."),
        ("scene_girl_gives_cat_bread", "نرگس به پشک نان می‌دهد."),
        ("scene_cat_eats_bread", "پشک نان را می‌خورد."),
        ("scene_girl_happy_at_school", "نرگس خوش است."),
        ("scene_girl_walks_to_school", "نرگس کجا می‌رود؟", "school|bridge|mountain", "school", "نه. نرگس به مکتب می‌رود."),
        ("scene_girl_sees_cat", "نرگس در راه چه دید؟", "cat|dog|hen", "cat", "نه. نرگس یک پشک دید."),
        ("scene_girl_gives_cat_bread", "نرگس به پشک چه داد؟", "bread|apple|egg", "bread", "نه. نرگس به پشک نان داد."),
    ]),
    ("02", [
        ("scene_boy_with_sapling", "نوید یک نهال دارد."),
        ("scene_boy_plants_sapling", "او نهال را در باغ می‌کارد."),
        ("scene_boy_waters_sapling", "نوید هر روز به نهال آب می‌دهد."),
        ("scene_sapling_grows", "نهال بزرگ می‌شود."),
        ("scene_apple_tree", "حالا درخت سیب دارد."),
        ("scene_boy_shares_apples", "نوید سیب را با دوستانش می‌خورد."),
        ("scene_boy_plants_sapling", "نوید چه کاشت؟", "sapling|wheat|flower", "sapling", "نه. نوید یک نهال کاشت."),
        ("scene_boy_waters_sapling", "نوید به نهال چه داد؟", "water|bread|salt", "water", "نه. نوید به نهال آب داد."),
        ("scene_apple_tree", "درخت چه میوه دارد؟", "apple|pomegranate|grapes", "apple", "نه. درخت سیب دارد."),
    ]),
])
SCENES.update({
 "scene_girl_walks_to_school": "a girl of about 9 (headscarf, long dress over trousers, cloth school bag) walks on a village path toward a small school building",
 "scene_girl_sees_cat": "the same girl stops on the path; a thin cat sits by a mud wall and looks at her",
 "scene_hungry_cat": "the thin cat alone, mouth open, meowing",
 "scene_girl_gives_cat_bread": "the girl crouches and holds out a piece of bread to the cat",
 "scene_cat_eats_bread": "the cat eats the piece of bread on the ground",
 "scene_girl_happy_at_school": "the girl, smiling, at the school door with her bag",
 "scene_boy_with_sapling": "a boy of about 10 (shalwar kameez, cap) holds a small sapling with its roots in a ball of earth",
 "scene_boy_plants_sapling": "the boy plants the sapling in a hole in an orchard; a small spade lies next to him",
 "scene_boy_waters_sapling": "the boy pours water from a watering can onto the sapling",
 "scene_sapling_grows": "the sapling is now a young tree taller than the boy, who stands next to it",
 "scene_apple_tree": "the full-grown tree carries red apples",
 "scene_boy_shares_apples": "the boy and two friends (one girl with headscarf, one boy) sit under the tree eating apples",
})

LP_INTRO = "هر حرف را با تصویری جوره کن که نامش با آن حرف شروع می‌شود."
def lp(L, p):
    assert first(p) == L
    return ("f:" + L, p, f"{NAME[L]}، مثل {fa(p)}")
verse2 = pairs_sheet(2, [
    ("01", "", [lp("پ", "cat"), lp("گ", "cow"), lp("ش", "camel"), lp("خ", "donkey"), lp("ز", "bee"), lp("چ", "eye")]),
    ("02", "", [lp("ج", "broom"), lp("ه", "firewood"), lp("ق", "pen"), lp("ف", "elephant"), lp("ع", "glasses"), lp("غ", "cave")]),
    ("03", "", [lp("ح", "pond"), lp("ص", "soap"), lp("ط", "parrot"), lp("ژ", "hail"), lp("ک", "book"), lp("م", "snake")]),
    ("04", "", [lp("ب", "goat"), lp("د", "hand"), lp("س", "apple"), lp("ن", "bread"), lp("ل", "lemon"), lp("ت", "mulberry")]),
])

meta2 = {"pack": "fa-2", "subject": "fa", "level": 2, "version": 1,
         "title_en": "Dari 2: The whole alphabet", "title_fa": "دری ۲: همه الفبا",
         "games": [
    game("alefba_garden", "listen_pick", "a", "Alefba Garden", "باغ الفبا", "گوش کن و جواب درست را انتخاب کن.", "flower", True),
    game("letter_shapes", "sorter", "b", "Letter Shapes", "شکل حرف‌ها", SHAPES_INTRO, "basket", True),
    game("word_weaver", "builder", "c", "Word Weaver", "کلمه‌باف", "حرف‌ها را از راست به چپ کنار هم بگذار و کلمه بساز.", "rope"),
    game("syllable_catch", "catch", "d", "Syllable Catch", "بگیر بگیر", "گوش کن و فقط حرف درست را بگیر.", "ball"),
    game("read_along", "story", "e", "Read Along", "با هم بخوانیم", "به قصه گوش کن و با آن بخوان. بعد به سوال‌ها جواب بده.", "book"),
    game("verse_corner", "pairs", "f", "Verse Corner", "گوشه شعر", LP_INTRO, "moon"),
]}
use(2, "flower", "basket", "rope", "ball", "book", "moon")
INTRO_ROUND_2 = {}
for rnd, ls in [("01", "پگ"), ("02", "شخ"), ("03", "زچ"), ("04", "جه"), ("05", "قف"), ("07", "عص"), ("08", "حغ"), ("09", "طژ"), ("10", "ثذضظ")]:
    for L in ls:
        INTRO_ROUND_2[L] = rnd
write_pack(2, meta2, {"alefba_garden.csv": garden2, "letter_shapes.csv": shapes2, "word_weaver.csv": weaver2,
                      "syllable_catch.csv": catch2, "read_along.csv": story2, "verse_corner.csv": verse2},
           lambda p: INTRO_ROUND_2.get(first(p), "00"))

# ---------------------------------------------------------------- pictures.txt
lines = []
for p in sorted(USED[1] | USED[2]):
    lines.append(f"{p}: {V[p][4]} ({V[p][0]})")
for s in sorted(SCENES):
    lines.append(f"{s}: {SCENES[s]}")
(OUT / "pictures.txt").write_text("\n".join(lines) + "\n", "utf-8")
unused = [p for p in V if p not in USED[1] | USED[2]]
print("pictures:", len(USED[1]), len(USED[2]), "scenes:", len(SCENES), "unused vocab:", unused)

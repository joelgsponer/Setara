#!/usr/bin/env python3
"""Logic puzzles (math-2-puzzles): draws the pack's pictures and wrote its first sheets.

  python3 make_puzzles.py            redraw the pictures (only files this script made)
  python3 make_puzzles.py --check    draw nothing new, only run the checks
  python3 make_puzzles.py --sheets   ALSO rewrite the CSV sheets, pictures.txt and
                                     content/i18n/puzzles.csv from this file

The CSV sheets are the source of the pack, as everywhere in Setara. This script
wrote their first version, because a puzzle and its picture have to agree (the
row drawn in scene_puz_pat_031 and the answer in what_next.csv). A reviewer who
changes a sentence edits the sheet and i18n/puzzles.csv; `--sheets` would
overwrite that, so use it only together with a change of the puzzles themselves.

Every puzzle is checked here where a machine can check it: the empty place of a
grid has one possible value, an order follows from its clues in one way only,
the triangles and squares of a figure are counted by brute force.
"""
from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import puzzle_draw as D  # noqa: E402
import puzzle_scenes as S  # noqa: E402
from puzzle_scenes import tok_thing  # noqa: E402

I18N: dict[str, str] = {}


def T(fa: str, en: str) -> str:
    """A Dari text with its English twin."""
    fa = " ".join(fa.split())
    assert I18N.setdefault(fa, en) == en, f"two English texts for {fa!r}"
    return fa


def F(fa: str, en: str) -> str:
    return "f:" + T(fa, en)


SHEETS: dict[str, tuple[list, list]] = {}
COLS = {
    "story": ["round", "intro_fa", "picture", "say_en", "say_fa", "show_fa", "choices", "right", "wrong_say_fa", "wrong_picture"],
    "pick": ["round", "intro_fa", "say_en", "say_fa", "show", "answer", "distractors", "help_fa", "hop"],
    "builder": ["round", "intro_fa", "say_en", "say_fa", "tiles", "extra", "rtl", "done_en", "done_fa", "help_fa"],
    "sorter": ["round", "intro_fa", "thing", "say_en", "say_fa", "basket", "basket_say_fa"],
    "pairs": ["round", "intro_fa", "a", "b", "say_en", "say_fa"],
}


def sheet(name: str, kind: str):
    rows: list = []
    SHEETS[name] = (COLS[kind], rows)
    seen = set()

    def add(rnd: str, intro: str = "", **kw):
        row = {"round": rnd, **kw}
        if rnd not in seen:
            seen.add(rnd)
            row["intro_fa"] = intro
        rows.append(row)
    return add


_turn = itertools.count()


def mix(right: str, wrong: list) -> str:
    """The choices of a story question; the right one is not always listed first."""
    assert right not in wrong and len(set(wrong)) == len(wrong), (right, wrong)
    k = next(_turn) % (len(wrong) + 1)
    return "|".join(wrong[:k] + [right] + wrong[k:])


# The names of library pictures, as the other packs say them.
N = {
    "cat": ("پشک", "cat"), "dog": ("سگ", "dog"), "goat": ("بز", "goat"), "sheep": ("گوسفند", "sheep"),
    "cow": ("گاو", "cow"), "horse": ("اسپ", "horse"), "donkey": ("خر", "donkey"), "camel": ("شتر", "camel"),
    "hen": ("مرغ", "hen"), "rooster": ("خروس", "rooster"), "chick": ("چوچه مرغ", "chick"), "fox": ("روباه", "fox"),
    "wolf": ("گرگ", "wolf"), "mouse": ("موش", "mouse"), "frog": ("بقه", "frog"), "fish": ("ماهی", "fish"),
    "snake": ("مار", "snake"), "elephant": ("فیل", "elephant"), "eagle": ("عقاب", "eagle"),
    "pigeon": ("کبوتر", "pigeon"), "sparrow": ("گنجشک", "sparrow"), "bee": ("زنبور عسل", "bee"),
    "ant": ("مورچه", "ant"), "fly": ("مگس", "fly"), "butterfly": ("پروانه", "butterfly"),
    "apple": ("سیب", "apple"), "pear": ("ناک", "pear"), "orange": ("مالته", "orange"), "lemon": ("لیمو", "lemon"),
    "grape": ("انگور", "grapes"), "watermelon": ("تربوز", "watermelon"), "almond": ("بادام", "almond"),
    "tree": ("درخت", "tree"), "seed": ("دانه", "seed"), "sprout": ("سبزه نو", "sprout"), "sapling": ("نهال", "sapling"),
    "egg": ("تخم", "egg"), "wheat": ("گندم", "wheat"), "flour_sack": ("آرد", "flour"), "bread": ("نان", "bread"),
    "wool": ("پشم", "wool"), "carpet": ("قالین", "carpet"), "book": ("کتاب", "book"), "pen": ("قلم", "pen"),
    "pencil": ("پنسل", "pencil"), "notebook": ("کتابچه", "notebook"), "button": ("دکمه", "button"),
    "table": ("میز", "table"), "house": ("خانه", "house"), "spring": ("بهار", "spring"),
    "summer": ("تابستان", "summer"), "autumn": ("خزان", "autumn"), "winter": ("زمستان", "winter"),
    "bread_half": ("نیم نان", "half a bread"), "bread_quarter": ("چارک نان", "a quarter of a bread"),
    "ice": ("یخ", "ice"), "water": ("آب", "water"), "steam": ("بخار", "steam"),
}


def names(pics: list) -> tuple[str, str]:
    return "، ".join(N[p][0] for p in pics), ", ".join(N[p][1] for p in pics)


# =============================================================================
# a  They belong together (pairs)
# =============================================================================

def game_pairs():
    add = sheet("belong_together.csv", "pairs")
    r1 = [("key", "lock", "کلید و قفل", "key and lock"), ("hen", "egg", "مرغ و تخم", "hen and egg"),
          ("cow", "milk", "گاو و شیر", "cow and milk"), ("bee", "honey", "زنبور و عسل", "bee and honey"),
          ("foot", "shoe", "پای و بوت", "foot and shoe"), ("rain", "umbrella", "باران و چتری", "rain and umbrella")]
    r2 = [("sheep", "wool", "گوسفند و پشم", "sheep and wool"), ("wheat", "bread", "گندم و نان", "wheat and bread"),
          ("sparrow", "nest", "گنجشک و آشیانه", "sparrow and nest"), ("eye", "glasses", "چشم و عینک", "eye and glasses"),
          ("tooth", "toothbrush", "دندان و برس دندان", "tooth and toothbrush"),
          ("pen", "notebook", "قلم و کتابچه", "pen and notebook")]
    intro = T("دو کارت را پیدا کن که با هم جور است. فکر کن: کدام چیز به کدام چیز کار دارد؟",
              "Find two cards that belong together. Think: which thing goes with which?")
    for rnd, rows in (("01", r1), ("02", r2)):
        for a, b, fa, en in rows:
            add(rnd, intro, a=a, b=b, say_fa=T(fa, en))
    intro = T("هر چیز یک سایه دارد. هر چیز را با سایه خودش جوره کن.",
              "Every thing has a shadow. Pair every thing with its own shadow.")
    for pic, fa, en in (("rooster", "خروس و سایه‌اش", "the rooster and its shadow"),
                        ("bell", "زنگ و سایه‌اش", "the bell and its shadow"),
                        ("shoe", "بوت و سایه‌اش", "the shoe and its shadow"),
                        ("elephant", "فیل و سایه‌اش", "the elephant and its shadow"),
                        ("pear", "ناک و سایه‌اش", "the pear and its shadow"),
                        ("frog", "بقه و سایه‌اش", "the frog and its shadow")):
        add("03", intro, a=pic, b=shadow(pic), say_fa=T(fa, en))


def shadow(pic: str) -> str:
    name = f"puz_shadow_{pic}"
    if name not in D.briefs:
        D.obj(name, D.shadow_of(pic), f"The shadow of the library picture '{pic}': the same drawing, all in one dark colour.")
    return name


# =============================================================================
# b  Odd one out (story: four cards, always all four on the screen)
# =============================================================================

def game_odd():
    add = sheet("odd_one_out.csv", "story")
    say = T("کدام یک با سه تای دیگر جور نیست؟", "Which one does not belong with the other three?")

    def odd(rnd, intro, three, one, why_fa, why_en, toks=False):
        f = tok_thing if toks else (lambda x: tok_thing(x) if not x.startswith("t:") else x)
        add(rnd, intro, say_fa=say, choices=mix(f(one), [f(x) for x in three]), right=f(one),
            wrong_say_fa=T(why_fa, why_en))

    i1 = T("چهار تصویر را ببین. سه تای آن با هم جور است، یکی جور نیست. همان یکی را انتخاب کن.",
           "Look at the four pictures. Three of them belong together, one does not. Choose that one.")
    odd("01", i1, ["cat", "dog", "goat"], "apple", "سه تا حیوان است. یکی حیوان نیست.", "Three are animals. One is not an animal.")
    odd("01", i1, ["apple", "pear", "orange"], "shoe", "سه تا میوه است. یکی میوه نیست.", "Three are fruit. One is not a fruit.")
    odd("01", i1, ["hen", "pigeon", "sparrow"], "fish", "سه تا پرنده است و بال دارد. یکی پرنده نیست.",
        "Three are birds and have wings. One is not a bird.")
    odd("01", i1, ["pen", "pencil", "notebook"], "bread", "سه تا چیزهای مکتب است. یکی را می‌خوریم.",
        "Three are things for school. One we eat.")
    odd("01", i1, ["table", "chair", "bed"], "tree", "سه تا در خانه است و نجار ساخته است. یکی در زمین می‌روید.",
        "Three are in the house and were made by a carpenter. One grows in the ground.")
    odd("01", i1, ["carrot", "potato", "onion"], "ball", "سه تا ترکاری است. یکی را نمی‌خوریم.",
        "Three are vegetables. One we do not eat.")
    odd("01", i1, ["cup", "plate", "spoon"], "sheep", "سه تا ظرف است. یکی زنده است.", "Three are dishes. One is alive.")

    i2 = T("حالا کمی مشکل‌تر است. خوب فکر کن که سه تا چه چیز مشترک دارند.",
           "Now it is a little harder. Think well what three of them have in common.")
    odd("02", i2, ["apple", "pear", "grapes"], "carrot", "سه تا میوه است. یکی ترکاری است.", "Three are fruit. One is a vegetable.")
    odd("02", i2, ["horse", "donkey", "camel"], "hen", "سه تا چهار پا دارد و بار می‌برد. یکی دو پا دارد.",
        "Three have four legs and carry loads. One has two legs.")
    odd("02", i2, ["eagle", "pigeon", "parrot"], "butterfly", "سه تا پرنده است و پر دارد. یکی پرواز می‌کند، ولی پرنده نیست.",
        "Three are birds and have feathers. One flies, but is not a bird.")
    odd("02", i2, ["coat", "waistcoat", "shoe"], "pot", "سه تا را می‌پوشیم. یکی را نمی‌پوشیم.",
        "Three we wear. One we do not wear.")
    odd("02", i2, ["sun", "moon", "star"], "tree", "سه تا در آسمان است. یکی روی زمین است.",
        "Three are in the sky. One is on the ground.")
    odd("02", i2, ["bee", "ant", "fly"], "mouse", "سه تا حشره است و شش پا دارد. یکی چهار پا دارد.",
        "Three are insects and have six legs. One has four legs.")
    odd("02", i2, ["axe", "shovel", "broom"], "bread", "با سه تا کار می‌کنیم. یکی را می‌خوریم.",
        "With three we work. One we eat.")

    i3 = T("به شکل، رنگ و کلانی نگاه کن. سه تا در یک چیز مثل هم است.",
           "Look at the shape, the colour and the size. Three are alike in one thing.")
    odd("03", i3, ["triangle_red", "triangle_blue", "triangle_yellow"], "square_green", "سه تا مثلث است. یکی مثلث نیست.",
        "Three are triangles. One is not a triangle.", True)
    odd("03", i3, ["circle_red", "square_red", "triangle_red"], "star_blue", "سه تا سرخ است. یکی سرخ نیست.",
        "Three are red. One is not red.", True)
    odd("03", i3, ["square_red", "triangle_blue", "star_yellow"], "small_circle_green", "سه تا کلان است. یکی خُرد است.",
        "Three are big. One is small.", True)
    odd("03", i3, ["triangle_red", "square_blue", "star_yellow"], "circle_green", "سه تا گوشه دارد. یکی گرد است و گوشه ندارد.",
        "Three have corners. One is round and has no corners.", True)
    odd("03", i3, ["circle_yellow", "star_yellow", "square_yellow"], "triangle_blue", "سه تا زرد است. یکی زرد نیست.",
        "Three are yellow. One is not yellow.", True)
    odd("03", i3, ["square_red", "square_blue", "square_green"], "circle_yellow", "سه تا مربع است. یکی مربع نیست.",
        "Three are squares. One is not a square.", True)
    odd("03", i3, ["small_triangle_red", "small_square_blue", "small_circle_green"], "star_yellow", "سه تا خُرد است. یکی کلان است.",
        "Three are small. One is big.", True)

    i4 = T("فکر کن: این چیزها چه کار می‌کنند، و از کجا می‌آیند؟", "Think: what do these things do, and where do they come from?")
    odd("04", i4, ["sun", "candle", "fire"], "stone", "سه تا روشنی می‌دهد. یکی روشنی نمی‌دهد.",
        "Three give light. One gives no light.")
    odd("04", i4, ["train", "aeroplane", "ship"], "house", "با سه تا سفر می‌کنیم. یکی از جایش نمی‌جنبد.",
        "With three we travel. One does not move from its place.")
    odd("04", i4, ["chick", "lamb", "kitten"], "cow", "سه تا چوچه است. یکی کلان شده است.",
        "Three are young animals. One is grown up.")
    odd("04", i4, ["cow", "goat", "sheep"], "cat", "از سه تا شیر می‌دوشیم. از یکی نمی‌دوشیم.",
        "Three we milk. One we do not milk.")
    odd("04", i4, ["apple", "pear", "walnut"], "carrot", "سه تا در درخت می‌روید. یکی زیر خاک می‌روید.",
        "Three grow on a tree. One grows under the soil.")
    odd("04", i4, ["fox", "wolf", "elephant"], "goat", "سه تا حیوان وحشی است. یکی در خانه با ما زندگی می‌کند.",
        "Three are wild animals. One lives with us at home.")
    odd("04", i4, ["bell", "drum", "radio"], "pillow", "سه تا آواز می‌دهد. یکی آرام است.",
        "Three make a sound. One is quiet.")

    i5 = T("حالا عددها. سه عدد با هم جور است، یکی جور نیست.", "Now numbers. Three numbers belong together, one does not.")
    odd("05", i5, ["t:2", "t:4", "t:6"], "t:7", "سه تا جفت است. یکی طاق است.", "Three are even. One is odd.")
    odd("05", i5, ["t:15", "t:25", "t:35"], "t:30", "سه تا با پنج ختم می‌شود. یکی با صفر ختم می‌شود.",
        "Three end in five. One ends in zero.")
    odd("05", i5, ["t:10", "t:20", "t:30"], "t:25", "سه تا ده تا ده تا شمرده می‌شود: ده، بیست، سی. یکی در این شمار نیست.",
        "Three are counted in tens: ten, twenty, thirty. One is not in this count.")
    odd("05", i5, ["t:3", "t:5", "t:7"], "t:8", "سه تا طاق است. یکی جفت است.", "Three are odd. One is even.")
    odd("05", i5, ["t:11", "t:22", "t:33"], "t:34", "در سه تا هر دو رقم یکی است. در یکی دو رقم فرق دارد.",
        "In three both digits are the same. In one the two digits differ.")
    odd("05", i5, ["t:3", "t:6", "t:9"], "t:10", "سه تا سه تا سه تا شمرده می‌شود: سه، شش، نُه. یکی در این شمار نیست.",
        "Three are counted in threes: three, six, nine. One is not in this count.")
    odd("05", i5, ["t:41", "t:43", "t:47"], "t:52", "سه تا بین چهل و پنجاه است. یکی از پنجاه کلان‌تر است.",
        "Three are between forty and fifty. One is more than fifty.")


# =============================================================================
# c  What comes next? (story: the row is the large picture)
# =============================================================================

W = {}


def game_next():
    add = sheet("what_next.csv", "story")
    say_pic = T("قطار را ببین. در جای خالی کدام یک می‌آید؟", "Look at the row. Which one goes in the empty place?")
    say_num = T("عددها را ببین. در جای خالی کدام عدد می‌آید؟", "Look at the numbers. Which number goes in the empty place?")
    W.update(
        ab=T("ببین: یکی این، یکی آن، و باز از سر. نوبت کدام است؟", "Look: one of this, one of that, and again from the start. Whose turn is it?"),
        aab=T("ببین: دو تا مثل هم، بعد یکی دیگر، و باز از سر.", "Look: two alike, then a different one, and again from the start."),
        abb=T("ببین: یکی، بعد دو تا مثل هم، و باز از سر.", "Look: one, then two alike, and again from the start."),
        abc=T("ببین: سه چیز پشت سر هم می‌آید، و باز از سر. بعد از این کدام بود؟",
              "Look: three things come one after the other, and again from the start. Which came after this one?"),
        aabb=T("ببین: دو تا این، دو تا آن، و باز از سر.", "Look: two of this, two of that, and again from the start."),
        four=T("ببین: چهار چیز پشت سر هم می‌آید، و باز از سر تکرار می‌شود.",
               "Look: four things come one after the other, and then it repeats from the start."),
        size=T("ببین: یکی کلان، یکی خُرد، و باز از سر.", "Look: one big, one small, and again from the start."),
        p1=T("هر بار یکی زیاد می‌شود.", "Each time there is one more."),
        m1=T("هر بار یکی کم می‌شود.", "Each time there is one less."),
        p2=T("هر بار دو زیاد می‌شود.", "Each time there are two more."),
        m2=T("هر بار دو کم می‌شود.", "Each time there are two less."),
        p3=T("هر بار سه زیاد می‌شود.", "Each time there are three more."),
        p4=T("هر بار چهار زیاد می‌شود.", "Each time there are four more."),
        p5=T("هر بار پنج زیاد می‌شود.", "Each time there are five more."),
        m5=T("هر بار پنج کم می‌شود.", "Each time there are five less."),
        p10=T("هر بار ده زیاد می‌شود.", "Each time there are ten more."),
        m10=T("هر بار ده کم می‌شود.", "Each time there are ten less."),
        bigger=T("هر بار دایره کلان‌تر می‌شود.", "Each time the circle gets bigger."),
        smaller=T("هر بار دایره خُردتر می‌شود.", "Each time the circle gets smaller."),
        twice=T("هر عدد دو بار می‌آید، بعد یکی زیاد می‌شود.", "Every number comes twice, then there is one more."),
        double=T("هر عدد دو برابر عدد پیش از خود است.", "Every number is twice the number before it."),
        halve=T("هر عدد نیم عدد پیش از خود است.", "Every number is half of the number before it."),
        turn=T("تیر هر بار یک چارک دور می‌خورد.", "The arrow makes a quarter turn each time."),
        turn2=T("هر تیر دو بار می‌آید، بعد یک چارک دور می‌خورد.", "Every arrow comes twice, then it makes a quarter turn."),
        two=T("دو قاعده است: شکل‌ها سه تا سه تا تکرار می‌شوند، و رنگ‌ها یکی سرخ، یکی آبی.",
              "There are two rules: the shapes repeat in threes, and the colours go one red, one blue."),
        updown=T("یک بار دو زیاد می‌شود، بعد یکی کم می‌شود، و باز از سر.", "First two more, then one less, and again from the start."),
        grow=T("هر بار یکی بیشتر از بار پیش زیاد می‌شود: یک، دو، سه، چهار.",
               "Each time the step is one more than before: one, two, three, four."),
        fib=T("هر عدد جمع دو عدد پیش از خود است.", "Every number is the sum of the two numbers before it."),
        sq=T("فاصله‌ها را ببین: سه، پنج، هفت. هر بار دو بیشتر زیاد می‌شود.",
             "Look at the gaps: three, five, seven. Each time the step is two more."),
        two_rows=T("دو قطار در هم است: یک، دو، سه، و ده، بیست، سی.", "Two rows are woven together: one, two, three, and ten, twenty, thirty."),
        m1p2=T("یک بار یکی کم می‌شود، بعد دو زیاد می‌شود، و باز از سر.", "First one less, then two more, and again from the start."),
        fall=T("هر بار پنج بیشتر از بار پیش کم می‌شود: پنج، ده، پانزده.",
               "Each time five more is taken away than before: five, ten, fifteen."),
        dbl1=T("فاصله‌ها را ببین: دو، چهار، هشت. فاصله هر بار دو برابر می‌شود.",
               "Look at the gaps: two, four, eight. The gap doubles each time."),
    )
    count = itertools.count(1)
    state = {"rnd": None}

    def pat(rnd, intro, seq, gap, wrong, why, rtl=True):
        if state["rnd"] != rnd:
            state["rnd"], state["k"] = rnd, 0
        state["k"] += 1
        toks = seq.split()
        if gap < 0:
            gap += len(toks)
        answer = toks[gap]
        num = answer.startswith("n:")
        name = f"scene_puz_pat_{rnd}{state['k']}"
        shown = " ".join("[EMPTY]" if i == gap else t for i, t in enumerate(toks))
        S.pattern(name, toks, gap, rtl and not num,
                  f"A row of cards with one empty yellow place, {'right to left' if rtl and not num else 'left to right'}: {shown}. "
                  f"The arrow underneath shows the direction. (Drawn by make_puzzles.py.)")
        add(rnd, intro, picture=name, say_fa=say_num if num else say_pic,
            choices=mix(tok_thing(answer), [tok_thing(w) for w in wrong.split()]), right=tok_thing(answer),
            wrong_say_fa=W[why])
        next(count)

    def nums(s):
        return " ".join("n:" + x for x in s.split())

    i = T("چیزها با یک ترتیب در قطار ایستاده‌اند. ترتیب را پیدا کن. بعد ببین که در جای خالی کدام یک می‌آید.",
          "The things stand in the row in an order. Find the order. Then see which one goes in the empty place.")
    pat("01", i, "circle_red circle_blue circle_red circle_blue circle_red circle_blue", -1, "circle_red circle_yellow", "ab")
    pat("01", i, "apple pear apple pear apple pear", -1, "apple orange", "ab")
    pat("01", i, "square_yellow triangle_blue square_yellow triangle_blue square_yellow triangle_blue", -1, "square_yellow circle_blue", "ab")
    pat("01", i, "cat dog cat dog cat dog", -1, "cat hen", "ab")
    pat("01", i, "size_5 size_2 size_5 size_2 size_5 size_2", -1, "size_5 small_square_blue", "size")
    pat("01", i, "star flower star flower star flower", -1, "star leaf", "ab")
    pat("01", i, "square_red square_blue square_red square_blue square_red square_blue", 4, "square_blue circle_red", "ab")

    i = T("حالا ترتیب کمی درازتر است. از اول قطار، با تیر، پیش برو.",
          "Now the order is a little longer. Go along the row from the start, with the arrow.")
    pat("02", i, "circle_red circle_red circle_blue circle_red circle_red circle_blue circle_red", -1, "circle_blue circle_yellow", "aab")
    pat("02", i, "hen hen chick hen hen chick hen", -1, "chick rooster", "aab")
    pat("02", i, "triangle_yellow square_blue square_blue triangle_yellow square_blue square_blue triangle_yellow", -1, "square_blue triangle_blue", "abb")
    pat("02", i, "circle_red circle_blue circle_yellow circle_red circle_blue circle_yellow circle_red", -1, "circle_blue circle_yellow", "abc")
    pat("02", i, "apple pear orange apple pear orange apple pear", -1, "orange apple", "abc")
    pat("02", i, "square_green square_green circle_yellow square_green square_green circle_yellow square_green", 4, "circle_yellow square_yellow", "aab")
    pat("02", i, "cat dog goat cat dog goat", -1, "cat dog", "abc")

    i = T("این بار جای خالی گاهی در میان قطار است. پیش و پس آن را ببین.",
          "This time the empty place is sometimes in the middle of the row. Look before it and after it.")
    pat("03", i, "circle_red circle_red circle_blue circle_blue circle_red circle_red circle_blue circle_blue", -1, "circle_red circle_yellow", "aabb")
    pat("03", i, "star star leaf leaf star star leaf leaf", 6, "star flower", "aabb")
    pat("03", i, "triangle_blue circle_yellow triangle_blue square_red triangle_blue circle_yellow triangle_blue square_red", -1, "circle_yellow triangle_blue", "four")
    pat("03", i, "apple pear pear apple pear pear apple pear", -1, "apple orange", "abb")
    pat("03", i, "circle_yellow circle_yellow circle_blue circle_yellow circle_yellow circle_blue circle_yellow circle_yellow", 1, "circle_blue circle_red", "aab")
    pat("03", i, "square_red circle_blue triangle_yellow square_red circle_blue triangle_yellow square_red circle_blue", -1, "triangle_yellow square_red", "abc")
    pat("03", i, "dog dog cat hen dog dog cat hen", -1, "dog cat", "four")

    i = T("این بار چیزها زیاد می‌شوند یا کم می‌شوند. خوب بشمار.", "This time the things get more or get less. Count well.")
    pat("04", i, "tower_1 tower_2 tower_3 tower_4 tower_5", -1, "tower_4 tower_6", "p1")
    pat("04", i, "dots_2 dots_4 dots_6 dots_8", -1, "dots_7 dots_6", "p2")
    pat("04", i, "tower_5 tower_4 tower_3 tower_2 tower_1", -1, "tower_2 tower_3", "m1")
    pat("04", i, "size_1 size_2 size_3 size_4 size_5", -1, "size_4 size_1", "bigger")
    pat("04", i, "dots_1 dots_3 dots_5 dots_7", -1, "dots_6 dots_8", "p2")
    pat("04", i, "tower_1 tower_1 tower_2 tower_2 tower_3 tower_3", -1, "tower_4 tower_2", "twice")
    pat("04", i, "dots_10 dots_8 dots_6 dots_4", -1, "dots_5 dots_2", "m2")
    pat("04", i, "size_5 size_4 size_3 size_2 size_1", 3, "size_3 size_1", "smaller")

    i = T("حالا قطار عددها. پیدا کن که از یک عدد تا عدد دیگر چند زیاد یا کم می‌شود.",
          "Now rows of numbers. Find how much is added or taken away from one number to the next.")
    pat("05", i, nums("5 6 7 8 9 10"), -1, "n:11 n:8", "p1")
    pat("05", i, nums("2 4 6 8 10"), -1, "n:9 n:12", "p2")
    pat("05", i, nums("5 10 15 20 25"), -1, "n:30 n:21", "p5")
    pat("05", i, nums("10 20 30 40 50"), 3, "n:35 n:45", "p10")
    pat("05", i, nums("9 8 7 6 5"), -1, "n:4 n:7", "m1")
    pat("05", i, nums("3 6 9 12 15"), -1, "n:14 n:13", "p3")
    pat("05", i, nums("20 18 16 14 12"), -1, "n:13 n:10", "m2")

    i = T("این قطارها مشکل‌تر است. گاهی عدد دو برابر می‌شود.", "These rows are harder. Sometimes the number doubles.")
    pat("06", i, nums("1 2 4 8 16"), -1, "n:10 n:12", "double")
    pat("06", i, nums("1 3 5 7 9 11"), -1, "n:10 n:12", "p2")
    pat("06", i, nums("30 25 20 15 10"), -1, "n:5 n:12", "m5")
    pat("06", i, nums("4 8 12 16 20"), 2, "n:10 n:14", "p4")
    pat("06", i, nums("100 90 80 70 60"), -1, "n:50 n:65", "m10")
    pat("06", i, nums("3 6 12 24 48"), -1, "n:36 n:30", "double")
    pat("06", i, nums("1 4 7 10 13"), -1, "n:12 n:14", "p3")

    i = T("این قطارها دو قاعده دارند، یا قاعده‌ای که خودش تغییر می‌کند. آهسته فکر کن.",
          "These rows have two rules, or a rule that itself changes. Think slowly.")
    pat("07", i, "arrow_up arrow_right arrow_down arrow_left arrow_up arrow_right arrow_down", -1, "arrow_left arrow_up", "turn")
    pat("07", i, "circle_red square_blue triangle_red circle_blue square_red triangle_blue circle_red", -1,
        "circle_blue square_red triangle_blue", "two")
    pat("07", i, "tower_1 tower_3 tower_2 tower_4 tower_3 tower_5 tower_4", -1, "tower_6 tower_5", "updown")
    pat("07", i, nums("1 2 4 7 11 16"), -1, "n:15 n:14", "grow")
    pat("07", i, "arrow_up arrow_up arrow_right arrow_right arrow_down arrow_down arrow_left", -1, "arrow_down arrow_up", "turn2")
    pat("07", i, nums("1 1 2 3 5 8 13"), -1, "n:11 n:10", "fib")
    pat("07", i, nums("2 3 5 8 12 17"), -1, "n:16 n:15", "grow")

    i = T("این‌ها مشکل‌ترین قطارها است. فاصله بین عددها را ببین.", "These are the hardest rows. Look at the gaps between the numbers.")
    pat("08", i, nums("1 4 9 16 25"), -1, "n:20 n:24", "sq")
    pat("08", i, nums("64 32 16 8 4"), -1, "n:2 n:6", "halve")
    pat("08", i, nums("1 10 2 20 3 30 4"), -1, "n:40 n:31", "two_rows")
    pat("08", i, nums("5 4 6 5 7 6 8"), -1, "n:7 n:5", "m1p2")
    pat("08", i, nums("100 95 85 70 50"), -1, "n:55 n:60", "fall")
    pat("08", i, nums("3 5 9 17 33"), -1, "n:25 n:34", "dbl1")
    pat("08", i, nums("2 4 8 16 32"), 2, "n:6 n:10", "double")


# =============================================================================
# d  Shadows and mirrors (listen_pick: the shown thing in the middle)
# =============================================================================

FIGS = [  # six figures of squares that look different turned and mirrored
    ("orange", [(0, 0), (0, 1), (0, 2), (1, 2)]),
    ("blue", [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)]),
    ("green", [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]),
    ("purple", [(1, 0), (1, 1), (1, 2), (0, 2), (0, 3)]),
    ("red", [(1, 0), (0, 1), (1, 1), (1, 2), (1, 3)]),
    ("yellow", [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)]),
]


def fig(k: int, variant: str) -> str:
    color, cells = FIGS[k]
    c = D.norm(cells)
    r90 = D.rot90(c)
    r180 = D.rot90(r90)
    m = D.mirror(c)
    m90 = D.rot90(m)
    m180 = D.rot90(m90)
    forms = {"base": c, "r90": r90, "r180": r180, "m": m, "m90": m90, "m180": m180}
    turned = {tuple(v) for kk, v in forms.items() if not kk.startswith("m")} | {tuple(D.rot90(r180))}
    mirrored = {tuple(v) for kk, v in forms.items() if kk.startswith("m")} | {tuple(D.rot90(m180))}
    assert len(turned) == 4 and len(mirrored) == 4 and not turned & mirrored, f"figure {k} is not different in a mirror"
    what = {"base": "as given", "r90": "turned a quarter turn to the right", "r180": "turned upside down (half a turn)",
            "m": "as seen in a mirror standing beside it", "m90": "mirrored and then turned a quarter turn",
            "m180": "mirrored and turned upside down"}[variant]
    name = f"puz_fig{k + 1}_{variant}"
    if name not in D.briefs:
        D.obj(name, D.blocks(forms[variant], 64, 64, 108, color),
              f"Figure {k + 1}: {len(cells)} {color} squares joined edge to edge, {what}. Series puz_fig{k + 1}_*: only the position changes.")
    if variant == "base":
        mname = f"puz_fig{k + 1}_mirror"
        if mname not in D.briefs:
            body = (D.blocks(c, 34, 64, 56, color, 4)
                    + f'<rect x="68" y="8" width="10" height="112" rx="4" fill="#bfe3f0" stroke="{D.INK}" stroke-width="4"/>'
                    + f'<path d="M71 20v30M75 60v20" stroke="#fff" stroke-width="2" stroke-linecap="round"/>'
                    + D.gap_box(86, 36, 38, 56))
            D.obj(mname, body, f"Figure {k + 1} standing left of an upright mirror (a tall pale blue bar); right of the mirror an empty yellow place for its mirror picture.")
    return name


def game_shadows():
    add = sheet("shadows_mirrors.csv", "pick")
    i = T("هر چیز یک سایه دارد. چیز را ببین و سایه خودش را پیدا کن.", "Every thing has a shadow. Look at the thing and find its own shadow.")
    say = T("سایه این کدام است؟", "Which is the shadow of this?")
    hlp = T("سایه همان شکل را دارد، ولی رنگ ندارد. به دور شکل نگاه کن.", "The shadow has the same shape, but no colour. Look at the outline.")
    easy = ["cat", "tree", "key", "umbrella", "fish", "chair", "butterfly"]
    for k, p in enumerate(easy):
        others = [easy[(k + j) % len(easy)] for j in (1, 3, 5)]
        add("01", i, say_fa=say, show=p, answer=shadow(p), distractors="|".join(shadow(o) for o in others), help_fa=hlp)

    i = T("این بار سایه را می‌بینی. پیدا کن که سایه از کدام حیوان است. این حیوان‌ها به هم مانند استند، خوب ببین.",
          "This time you see the shadow. Find which animal it belongs to. These animals look alike, so look well.")
    say = T("این سایه از کدام حیوان است؟", "Which animal does this shadow belong to?")
    hlp = T("به گوش‌ها، دم، گردن و پاها نگاه کن.", "Look at the ears, the tail, the neck and the legs.")
    hard = ["goat", "sheep", "cow", "horse", "donkey", "camel", "dog"]
    for k, p in enumerate(hard):
        others = [hard[(k + j) % len(hard)] for j in (1, 2, 4)]
        add("02", i, say_fa=say, show=shadow(p), answer=p, distractors="|".join(others), help_fa=hlp)

    i = T("این شکل را چرخانده‌ایم. فقط یکی از کارت‌ها همان شکل است. دیگرها شکل آیینه‌ای است.",
          "We have turned this figure. Only one of the cards is the same figure. The others are its mirror picture.")
    say = T("این شکل را چرخانده‌ایم. کدام یک همان شکل است؟", "We have turned this figure. Which one is the same figure?")
    hlp = T("شکل را در فکر خود آهسته بچرخان. شکل آیینه‌ای هر قدر بچرخد، با این شکل یکی نمی‌شود.",
            "Turn the figure slowly in your mind. However the mirror picture is turned, it never becomes this figure.")
    for k in range(len(FIGS)):
        right = "r90" if k % 2 == 0 else "r180"
        add("03", i, say_fa=say, show=fig(k, "base"), answer=fig(k, right),
            distractors="|".join(fig(k, v) for v in ("m", "m90", "m180")), help_fa=hlp)

    i = T("این شکل پیش آیینه ایستاده است. پیدا کن که در آیینه چطور دیده می‌شود.",
          "This figure stands in front of a mirror. Find how it looks in the mirror.")
    say = T("این شکل در آیینه چطور دیده می‌شود؟", "How does this figure look in the mirror?")
    hlp = T("در آیینه چپ و راست جای خود را بدل می‌کند. بالا و پایین همان می‌ماند.",
            "In the mirror left and right change places. Up and down stay the same.")
    for k in range(len(FIGS)):
        fig(k, "base")
        add("04", i, say_fa=say, show=f"puz_fig{k + 1}_mirror", answer=fig(k, "m"),
            distractors="|".join(fig(k, v) for v in ("base", "r180", "m180")), help_fa=hlp)


# =============================================================================
# e  In the right order (builder; pictures are placed from the right)
# =============================================================================

def unique_order(tiles: list, clues: list) -> None:
    """The clues must leave exactly the given order."""
    ok = []
    for perm in itertools.permutations(tiles):
        pos = {t: i + 1 for i, t in enumerate(perm)}
        pos["_n"] = len(tiles)
        if all(c(pos) for c in clues):
            ok.append(list(perm))
    assert ok == [tiles], f"clues give {ok}, wanted only {tiles}"


def game_order():
    add = sheet("right_order.csv", "builder")

    def simple(rnd, intro, say, tiles, help_):
        fa, en = names(tiles)
        add(rnd, intro, say_fa=say, tiles="|".join(tiles), rtl="yes",
            done_fa=T("آفرین! " + fa + ".", "Well done! " + en[0].upper() + en[1:] + "."), help_fa=help_)

    i = T("کدام خُردتر است و کدام کلان‌تر؟ تصویرها را به ترتیب بمان.", "Which is smaller and which is bigger? Put the pictures in order.")
    up = T("از خُردترین تا کلان‌ترین بمان.", "Put them from the smallest to the biggest.")
    down = T("از کلان‌ترین تا خُردترین بمان.", "Put them from the biggest to the smallest.")
    h_up = T("اول آن که از همه خُردتر است. آخر آن که از همه کلان‌تر است.", "First the one that is smallest of all. Last the one that is biggest of all.")
    h_down = T("اول آن که از همه کلان‌تر است. آخر آن که از همه خُردتر است.", "First the one that is biggest of all. Last the one that is smallest of all.")
    simple("01", i, up, ["mouse", "cat", "sheep", "elephant"], h_up)
    simple("01", i, up, ["ant", "chick", "hen", "horse"], h_up)
    simple("01", i, down, ["camel", "goat", "hen", "bee"], h_down)
    simple("01", i, up, ["almond", "apple", "watermelon", "tree"], h_up)
    simple("01", i, down, ["house", "table", "book", "button"], h_down)
    simple("01", i, T("از کمترین پا تا بیشترین پا بمان.", "Put them from the fewest legs to the most legs."),
           ["snake", "hen", "cat", "ant"],
           T("مار پا ندارد. مرغ دو پا دارد. پشک چهار پا دارد. مورچه شش پا دارد.",
             "The snake has no legs. The hen has two legs. The cat has four legs. The ant has six legs."))

    i = T("اول چه می‌شود و بعد چه؟ تصویرها را به ترتیب بمان.", "What happens first and what next? Put the pictures in order.")
    first = T("اول چه بود؟ بعد چه شد؟ به ترتیب بمان.", "What was first? What came then? Put them in order.")
    simple("02", i, first, ["seed", "sprout", "sapling", "tree"],
           T("دانه سبز می‌شود، نهال می‌شود، و نهال درخت می‌شود.", "The seed sprouts, becomes a sapling, and the sapling becomes a tree."))
    simple("02", i, first, ["egg", "chick", "hen"],
           T("از تخم چوچه می‌برآید. چوچه کلان می‌شود و مرغ می‌شود.", "A chick hatches from the egg. The chick grows and becomes a hen."))
    simple("02", i, first, ["wheat", "flour_sack", "bread"],
           T("گندم را آرد می‌کنیم. از آرد نان می‌پزیم.", "We grind wheat into flour. From flour we bake bread."))
    simple("02", i, first, ["sheep", "wool", "carpet"],
           T("پشم را از گوسفند می‌گیریم. از پشم قالین می‌بافیم.", "We take wool from the sheep. From wool we weave a carpet."))
    simple("02", i, T("نان را می‌خوریم. اول چقدر بود؟ بعد چقدر ماند؟", "We eat the bread. How much was there first? How much was left then?"),
           ["bread", "bread_half", "bread_quarter"],
           T("اول نان پوره بود. بعد نیم ماند. بعد چارک ماند.", "First the bread was whole. Then half was left. Then a quarter was left."))
    simple("02", i, T("چهار فصل سال را به ترتیب بمان. از بهار شروع کن.", "Put the four seasons of the year in order. Start with spring."),
           ["spring", "summer", "autumn", "winter"],
           T("بعد از بهار تابستان می‌آید، بعد خزان، بعد زمستان.", "After spring comes summer, then autumn, then winter."))
    simple("02", i, T("آب را گرم می‌کنیم. اول چه بود؟ بعد چه شد؟", "We heat water. What was first? What came then?"),
           ["ice", "water", "steam"],
           T("یخ گرم شود، آب می‌شود. آب جوش بیاید، بخار می‌شود.", "When ice is warmed it becomes water. When water boils it becomes steam."))

    def clue(rnd, intro, fa, en, tiles, clues, help_fa, help_en, extra=None):
        unique_order(tiles, clues)
        nfa, nen = names(tiles)
        add(rnd, intro, say_fa=T(fa, en), tiles="|".join(tiles), extra="|".join(extra or []), rtl="yes",
            done_fa=T("آفرین! " + nfa + ".", "Well done! " + nen[0].upper() + nen[1:] + "."), help_fa=T(help_fa, help_en))

    def first_(x): return lambda p: p[x] == 1
    def last(x): return lambda p: p[x] == p["_n"]
    def before(x, y): return lambda p: p[x] < p[y]
    def just_before(x, y): return lambda p: p[x] + 1 == p[y]
    def middle(x): return lambda p: p[x] == 2 and p["_n"] == 3
    def not_first(x): return lambda p: p[x] != 1
    def not_last(x): return lambda p: p[x] != p["_n"]
    def between(x, a, b): return lambda p: p[a] < p[x] < p[b] or p[b] < p[x] < p[a]

    i = T("سه چیز در قطار ایستاده است. خوب گوش کن که کدام اول است و کدام آخر. بعد به ترتیب بمان.",
          "Three things stand in a row. Listen well which is first and which is last. Then put them in order.")
    clue("03", i, "پشک اول است. مرغ آخر است. سگ کجا است؟ به ترتیب بمان.",
         "The cat is first. The hen is last. Where is the dog? Put them in order.",
         ["cat", "dog", "hen"], [first_("cat"), last("hen")],
         "پشک اول، مرغ آخر. برای سگ فقط میان می‌ماند.", "Cat first, hen last. Only the middle is left for the dog.")
    clue("03", i, "بز در میان است. گاو آخر است. به ترتیب بمان.", "The goat is in the middle. The cow is last. Put them in order.",
         ["sheep", "goat", "cow"], [middle("goat"), last("cow")],
         "بز در میان و گاو آخر است. پس گوسفند اول است.", "The goat is in the middle and the cow is last. So the sheep is first.")
    clue("03", i, "شتر اول است. اسپ پیش از خر است. به ترتیب بمان.", "The camel is first. The horse is before the donkey. Put them in order.",
         ["camel", "horse", "donkey"], [first_("camel"), before("horse", "donkey")],
         "شتر اول است. بعد اسپ می‌آید، چون اسپ پیش از خر است.", "The camel is first. Then comes the horse, because the horse is before the donkey.")
    clue("03", i, "سیب نه اول است و نه آخر. ناک آخر است. به ترتیب بمان.",
         "The apple is neither first nor last. The pear is last. Put them in order.",
         ["orange", "apple", "pear"], [not_first("apple"), not_last("apple"), last("pear")],
         "سیب نه اول است نه آخر، پس در میان است. ناک آخر است. مالته اول می‌ماند.",
         "The apple is neither first nor last, so it is in the middle. The pear is last. The orange is left for first.")
    clue("03", i, "مرغ پیش از چوچه است. چوچه پیش از خروس است. به ترتیب بمان.",
         "The hen is before the chick. The chick is before the rooster. Put them in order.",
         ["hen", "chick", "rooster"], [before("hen", "chick"), before("chick", "rooster")],
         "مرغ پیش از چوچه، و چوچه پیش از خروس. پس مرغ اول است.", "The hen before the chick, and the chick before the rooster. So the hen is first.")
    clue("03", i, "سگ بعد از پشک است. سگ آخر نیست. به ترتیب بمان.", "The dog is after the cat. The dog is not last. Put them in order.",
         ["cat", "dog", "mouse"], [before("cat", "dog"), not_last("dog")],
         "سگ بعد از پشک است، پس اول نیست. آخر هم نیست. پس سگ در میان است.",
         "The dog is after the cat, so it is not first. It is not last either. So the dog is in the middle.")

    i = T("حالا چهار چیز در قطار است. گوش کن و فکر کن. اگر یاد نماند، دکمه آهسته را فشار بده و دوباره بشنو.",
          "Now four things are in the row. Listen and think. If you cannot remember, press the slow button and hear it again.")
    clue("04", i, "گاو اول است. مرغ آخر است. بز پیش از گوسفند است. به ترتیب بمان.",
         "The cow is first. The hen is last. The goat is before the sheep. Put them in order.",
         ["cow", "goat", "sheep", "hen"], [first_("cow"), last("hen"), before("goat", "sheep")],
         "گاو اول و مرغ آخر است. در میان، بز پیش از گوسفند می‌آید.", "The cow is first and the hen is last. In between, the goat comes before the sheep.")
    clue("04", i, "موش اول است. پشک آخر است. سگ درست پیش از پشک است. به ترتیب بمان.",
         "The mouse is first. The cat is last. The dog is right before the cat. Put them in order.",
         ["mouse", "frog", "dog", "cat"], [first_("mouse"), last("cat"), just_before("dog", "cat")],
         "موش اول، پشک آخر، و سگ درست پیش از پشک. برای بقه جای دوم می‌ماند.",
         "Mouse first, cat last, and the dog right before the cat. The second place is left for the frog.")
    clue("04", i, "ناک پیش از مالته است. سیب پیش از ناک است. لیمو آخر است. به ترتیب بمان.",
         "The pear is before the orange. The apple is before the pear. The lemon is last. Put them in order.",
         ["apple", "pear", "orange", "lemon"], [before("pear", "orange"), before("apple", "pear"), last("lemon")],
         "سیب پیش از ناک، و ناک پیش از مالته است. لیمو آخر است.", "The apple is before the pear, and the pear before the orange. The lemon is last.")
    clue("04", i, "قلم اول است. پنسل درست بعد از قلم است. کتابچه آخر است. به ترتیب بمان.",
         "The pen is first. The pencil is right after the pen. The notebook is last. Put them in order.",
         ["pen", "pencil", "book", "notebook"], [first_("pen"), just_before("pen", "pencil"), last("notebook")],
         "قلم، بعد پنسل. کتابچه آخر است. برای کتاب جای سوم می‌ماند.", "The pen, then the pencil. The notebook is last. The third place is left for the book.")
    clue("04", i, "شتر اول است. گاو آخر است. اسپ بین شتر و خر است. به ترتیب بمان.",
         "The camel is first. The cow is last. The horse is between the camel and the donkey. Put them in order.",
         ["camel", "horse", "donkey", "cow"], [first_("camel"), last("cow"), between("horse", "camel", "donkey")],
         "شتر اول و گاو آخر است. اسپ بین شتر و خر است، پس اسپ دوم و خر سوم است.",
         "The camel is first and the cow is last. The horse is between the camel and the donkey, so the horse is second and the donkey third.")
    clue("04", i, "چوچه اول است. کبوتر آخر است. مرغ پیش از خروس است. به ترتیب بمان.",
         "The chick is first. The pigeon is last. The hen is before the rooster. Put them in order.",
         ["chick", "hen", "rooster", "pigeon"], [first_("chick"), last("pigeon"), before("hen", "rooster")],
         "چوچه اول و کبوتر آخر است. در میان، مرغ پیش از خروس می‌آید.", "The chick is first and the pigeon is last. In between, the hen comes before the rooster.")

    i = T("این‌ها مشکل‌ترین قطارها است. گاهی می‌شنوی که چیزی کجا نیست. گاهی یک تصویر هیچ در قطار نیست.",
          "These are the hardest rows. Sometimes you hear where a thing is not. Sometimes one picture is not in the row at all.")
    clue("05", i, "گوسفند اول نیست. بز درست بعد از گوسفند است. گاو آخر است. خر هم در قطار است. به ترتیب بمان.",
         "The sheep is not first. The goat is right after the sheep. The cow is last. The donkey is in the row too. Put them in order.",
         ["donkey", "sheep", "goat", "cow"], [not_first("sheep"), just_before("sheep", "goat"), last("cow")],
         "گاو آخر است. گوسفند اول نیست و بز درست بعد از آن است، پس گوسفند دوم و بز سوم است. خر اول می‌ماند.",
         "The cow is last. The sheep is not first and the goat is right after it, so the sheep is second and the goat third. The donkey is left for first.")
    clue("05", i, "پشک پیش از سگ است، ولی بعد از موش. مرغ پیش از موش است. به ترتیب بمان.",
         "The cat is before the dog, but after the mouse. The hen is before the mouse. Put them in order.",
         ["hen", "mouse", "cat", "dog"], [before("cat", "dog"), before("mouse", "cat"), before("hen", "mouse")],
         "مرغ پیش از موش، موش پیش از پشک، و پشک پیش از سگ است.", "The hen is before the mouse, the mouse before the cat, and the cat before the dog.")
    clue("05", i, "لیمو اول است. سیب آخر نیست. ناک درست پیش از سیب است. مالته هم در قطار است. به ترتیب بمان.",
         "The lemon is first. The apple is not last. The pear is right before the apple. The orange is in the row too. Put them in order.",
         ["lemon", "pear", "apple", "orange"], [first_("lemon"), not_last("apple"), just_before("pear", "apple")],
         "لیمو اول است. ناک و سیب پهلوی هم استند و سیب آخر نیست، پس ناک دوم و سیب سوم است. مالته آخر می‌ماند.",
         "The lemon is first. The pear and the apple are side by side and the apple is not last, so the pear is second and the apple third. The orange is left for last.")
    clue("05", i, "در مسابقه سه حیوان بود. اسپ از سگ پیش بود. خر از همه آخر بود. پشک در مسابقه نبود. به ترتیب بمان.",
         "Three animals were in the race. The horse was ahead of the dog. The donkey was last of all. The cat was not in the race. Put them in order.",
         ["horse", "dog", "donkey"], [before("horse", "dog"), last("donkey")],
         "خر آخر است. اسپ از سگ پیش بود، پس اسپ اول و سگ دوم است. پشک در مسابقه نبود.",
         "The donkey is last. The horse was ahead of the dog, so the horse is first and the dog second. The cat was not in the race.",
         extra=["cat"])
    clue("05", i, "مگس آخر است. زنبور اول نیست و دوم هم نیست. مورچه درست پیش از زنبور است. پروانه هم در قطار است. به ترتیب بمان.",
         "The fly is last. The bee is not first and not second either. The ant is right before the bee. The butterfly is in the row too. Put them in order.",
         ["butterfly", "ant", "bee", "fly"],
         [last("fly"), not_first("bee"), lambda p: p["bee"] != 2, just_before("ant", "bee")],
         "مگس آخر است. زنبور نه اول است و نه دوم، پس سوم است. مورچه درست پیش از آن، دوم است. پروانه اول می‌ماند.",
         "The fly is last. The bee is neither first nor second, so it is third. The ant, right before it, is second. The butterfly is left for first.")
    clue("05", i, "روباه آخر است. گرگ پهلوی روباه نیست. عقاب درست بعد از گرگ است. مار اول نیست. به ترتیب بمان.",
         "The fox is last. The wolf is not next to the fox. The eagle is right after the wolf. The snake is not first. Put them in order.",
         ["wolf", "eagle", "snake", "fox"],
         [last("fox"), lambda p: abs(p["wolf"] - p["fox"]) != 1, just_before("wolf", "eagle"), not_first("snake")],
         "روباه آخر است. مار اول نیست، پس گرگ اول است. عقاب درست بعد از گرگ، دوم است. مار سوم می‌ماند.",
         "The fox is last. The snake is not first, so the wolf is first. The eagle, right after the wolf, is second. The snake is left for third.")


N.update({"wolf": ("گرگ", "wolf"), "eagle": ("عقاب", "eagle")})


# =============================================================================
# f  Both or neither (sorter)
# =============================================================================

NUM_FA = {3: ("سه", "three"), 4: ("چهار", "four"), 7: ("هفت", "seven"), 8: ("هشت", "eight"), 12: ("دوازده", "twelve"),
          13: ("سیزده", "thirteen"), 16: ("شانزده", "sixteen"), 17: ("هفده", "seventeen")}
SHAPE_FA = {"circle": ("دایره", "circle"), "square": ("مربع", "square"), "triangle": ("مثلث", "triangle"), "star": ("ستاره", "star")}
COLOR_FA = {"red": ("سرخ", "red"), "blue": ("آبی", "blue"), "yellow": ("زرد", "yellow"), "green": ("سبز", "green")}


def shape_say(tok: str, size: bool = False) -> str:
    kind, color, small = S._parse_shape(tok)
    sfa, sen = SHAPE_FA[kind]
    cfa, cen = COLOR_FA[color]
    if size:
        return T(f"{sfa} {'خُرد' if small else 'کلان'} {cfa}", f"{'small' if small else 'big'} {cen} {sen}")
    return T(f"{sfa} {cfa}", f"{cen} {sen}")


def game_sorter():
    add = sheet("both_or_neither.csv", "sorter")
    i = T("هر حیوان چند پا دارد؟ هر کدام را در سبد درست بینداز.", "How many legs does each animal have? Drop each one into the right basket.")
    b = {2: (F("دو پا", "two legs"), T("دو پا دارد", "it has two legs")),
         4: (F("چهار پا", "four legs"), T("چهار پا دارد", "it has four legs")),
         0: (F("بی پا", "no legs"), T("پا ندارد", "it has no legs"))}
    for pic, legs in (("hen", 2), ("cat", 4), ("fish", 0), ("pigeon", 2), ("cow", 4), ("snake", 0), ("goat", 4), ("sparrow", 2), ("horse", 4)):
        add("01", i, thing=pic, say_fa=T(*N[pic]), basket=b[legs][0], basket_say_fa=b[legs][1])

    both = F("هر دو", "both")
    none = F("هیچ کدام", "neither")
    i = T("دو چیز را ببین: رنگ و شکل. سرخ است؟ گرد است؟ یا هر دو؟", "Look at two things: colour and shape. Is it red? Is it round? Or both?")
    red = (F("سرخ", "red"), T("سرخ است، ولی گرد نیست", "it is red, but not round"))
    rnd_ = (F("گرد", "round"), T("گرد است، ولی سرخ نیست", "it is round, but not red"))
    bth = (both, T("هم سرخ است و هم گرد", "it is both red and round"))
    for tok, bk in (("square_red", red), ("circle_blue", rnd_), ("circle_red", bth), ("triangle_red", red), ("circle_yellow", rnd_),
                    ("small_circle_red", bth), ("star_red", red), ("circle_green", rnd_)):
        add("02", i, thing=tok_thing(tok), say_fa=shape_say(tok), basket=bk[0], basket_say_fa=bk[1])

    i = T("حالا چهار سبد است. آبی است؟ مثلث است؟ هر دو؟ یا هیچ کدام؟", "Now there are four baskets. Is it blue? Is it a triangle? Both? Or neither?")
    blue = (F("آبی", "blue"), T("آبی است، ولی مثلث نیست", "it is blue, but not a triangle"))
    tri = (F("مثلث", "triangle"), T("مثلث است، ولی آبی نیست", "it is a triangle, but not blue"))
    bth = (both, T("هم آبی است و هم مثلث", "it is both blue and a triangle"))
    non = (none, T("نه آبی است و نه مثلث", "it is neither blue nor a triangle"))
    for tok, bk in (("triangle_blue", bth), ("triangle_red", tri), ("circle_blue", blue), ("star_yellow", non), ("small_triangle_blue", bth),
                    ("square_blue", blue), ("triangle_yellow", tri), ("circle_red", non)):
        add("03", i, thing=tok_thing(tok), say_fa=shape_say(tok), basket=bk[0], basket_say_fa=bk[1])

    i = T("حالا عددها. جفت است؟ از ده کلان‌تر است؟ هر دو؟ یا هیچ کدام؟", "Now numbers. Is it even? Is it more than ten? Both? Or neither?")
    even = (F("جفت", "even"), T("جفت است، ولی از ده کلان‌تر نیست", "it is even, but not more than ten"))
    big = (F("بیش از ده", "more than ten"), T("از ده کلان‌تر است، ولی جفت نیست", "it is more than ten, but not even"))
    bth = (both, T("هم جفت است و هم از ده کلان‌تر", "it is both even and more than ten"))
    non = (none, T("نه جفت است و نه از ده کلان‌تر", "it is neither even nor more than ten"))
    for n, bk in ((4, even), (13, big), (16, bth), (7, non), (8, even), (17, big), (12, bth), (3, non)):
        add("04", i, thing=f"t:{n}", say_fa=T(*NUM_FA[n]), basket=bk[0], basket_say_fa=bk[1])

    i = T("این بار کلانی و رنگ. کلان است؟ زرد است؟ هر دو؟ یا هیچ کدام؟", "This time size and colour. Is it big? Is it yellow? Both? Or neither?")
    bg = (F("کلان", "big"), T("کلان است، ولی زرد نیست", "it is big, but not yellow"))
    yl = (F("زرد", "yellow"), T("زرد است، ولی کلان نیست", "it is yellow, but not big"))
    bth = (both, T("هم کلان است و هم زرد", "it is both big and yellow"))
    non = (none, T("نه کلان است و نه زرد", "it is neither big nor yellow"))
    for tok, bk in (("circle_red", bg), ("small_star_yellow", yl), ("star_yellow", bth), ("small_square_blue", non), ("triangle_blue", bg),
                    ("small_circle_yellow", yl), ("square_yellow", bth), ("small_triangle_green", non)):
        add("05", i, thing=tok_thing(tok), say_fa=shape_say(tok, size=True), basket=bk[0], basket_say_fa=bk[1])


# =============================================================================
# g  Riddles (journey; written answers are read aloud)
# =============================================================================

def game_riddles():
    add = sheet("riddles.csv", "pick")

    def q(rnd, intro, fa, en, answer, wrong, hfa, hen):
        add(rnd, intro, say_fa=T(fa, en), answer=answer, distractors=wrong, help_fa=T(hfa, hen))

    i = T("چیستان! خوب گوش کن و فکر کن که این چیست. بعد تصویر درست را انتخاب کن.",
          "A riddle! Listen well and think what it is. Then choose the right picture.")
    q("01", i, "چهار پا دارد، ولی راه رفته نمی‌تواند. بالایش می‌نشینیم. چیست؟",
      "It has four legs, but it cannot walk. We sit on it. What is it?", "chair", "donkey|ball|tree",
      "چوکی چهار پایه دارد، ولی زنده نیست و راه نمی‌رود.", "A chair has four legs, but it is not alive and does not walk.")
    q("01", i, "دندان دارد، ولی چیزی نمی‌خورد. موی را هموار می‌کند. چیست؟",
      "It has teeth, but it eats nothing. It makes hair smooth. What is it?", "comb", "dog|spoon|toothbrush",
      "شانه دندانه دارد. با آن موی خود را شانه می‌کنیم.", "A comb has teeth. We comb our hair with it.")
    q("01", i, "وقتی باران می‌بارد باز می‌شود. وقتی آفتاب است بسته می‌ماند. چیست؟",
      "When it rains it opens. When the sun shines it stays closed. What is it?", "umbrella", "door|book|window",
      "چتری را در باران باز می‌کنیم تا تر نشویم.", "We open an umbrella in the rain so that we do not get wet.")
    q("01", i, "خانه‌ای سفید است. نه دروازه دارد و نه کلکین. در میانش زردی است. چیست؟",
      "It is a white house. It has no door and no window. Inside it is something yellow. What is it?", "egg", "house|lemon|tent",
      "تخم از بیرون سفید است و راه ندارد. در میانش زردی است.", "An egg is white outside and has no opening. Inside is the yolk.")
    q("01", i, "روشنی می‌دهد. هر قدر می‌سوزد، کوتاه‌تر می‌شود. چیست؟",
      "It gives light. The longer it burns, the shorter it gets. What is it?", "candle", "sun|pencil|tree",
      "شمع می‌سوزد و روشنی می‌دهد، و آهسته آهسته کوتاه می‌شود.", "A candle burns and gives light, and slowly gets shorter.")
    q("01", i, "صبح می‌آید و شام می‌رود. همه جا را روشن و گرم می‌کند. چیست؟",
      "It comes in the morning and goes in the evening. It makes everything bright and warm. What is it?", "sun", "moon|candle|star",
      "آفتاب صبح می‌برآید و شام می‌نشیند.", "The sun rises in the morning and sets in the evening.")
    q("01", i, "زبان ندارد، ولی گپ می‌زند و آواز می‌خواند. چیست؟",
      "It has no tongue, but it talks and sings. What is it?", "radio", "book|stone|pillow",
      "رادیو گپ می‌زند و آواز می‌خواند، ولی دهن و زبان ندارد.", "A radio talks and sings, but it has no mouth and no tongue.")

    i = T("این چیستان‌ها کمی مشکل‌تر است. هر کلمه را خوب بشنو.", "These riddles are a little harder. Listen well to every word.")
    q("02", i, "هر قدر خشک می‌کند، خودش ترتر می‌شود. چیست؟",
      "The more it dries, the wetter it gets itself. What is it?", "towel", "sun|fire|stone",
      "با دستمال دست و روی خود را خشک می‌کنیم. آب به دستمال می‌رود و دستمال تر می‌شود.",
      "We dry our hands and face with a towel. The water goes into the towel and the towel gets wet.")
    q("02", i, "اگر چوب بدهی زنده می‌ماند. اگر آب بدهی می‌میرد. چیست؟",
      "If you give it wood it lives. If you give it water it dies. What is it?", "fire", "tree|fish|goat",
      "آتش با چوب می‌سوزد و با آب خاموش می‌شود.", "Fire burns with wood and goes out with water.")
    q("02", i, "وقتی می‌خری سیاه است. وقتی می‌سوزد سرخ است. وقتی دور می‌اندازی خاکستری است. چیست؟",
      "When you buy it, it is black. When it burns, it is red. When you throw it away, it is grey. What is it?", "charcoal", "brick|tomato|bread",
      "زغال سیاه است. در آتش سرخ می‌شود و در آخر خاکستر می‌شود.", "Charcoal is black. In the fire it turns red and at the end it becomes ash.")
    q("02", i, "پا ندارد، ولی از کوه تا دشت می‌دود و هیچ ایستاده نمی‌شود. چیست؟",
      "It has no legs, but it runs from the mountain to the plain and never stands still. What is it?", "river", "horse|stone|tree",
      "آب دریا از کوه پایین می‌آید و همیشه روان است.", "The water of the river comes down from the mountain and always flows.")
    q("02", i, "روز دیده نمی‌شود، شب می‌آید. بسیار زیاد است و شمرده نمی‌شود. چیست؟",
      "By day it is not seen, at night it comes. There are very many and they cannot be counted. What is it?", "star", "sun|candle|sheep",
      "ستاره‌ها شب در آسمان دیده می‌شوند و بسیار زیاد استند.", "The stars are seen in the sky at night and there are very many.")
    q("02", i, "یک پوست دارد و در میانش صدها دانه سرخ و شیرین است. چیست؟",
      "It has one skin and inside it are hundreds of red, sweet seeds. What is it?", "pomegranate", "apple|walnut|onion",
      "انار پر از دانه‌های سرخ و شیرین است.", "A pomegranate is full of red, sweet seeds.")
    q("02", i, "هر قدر او را بزنی، گریه نمی‌کند. آواز خوش می‌دهد. چیست؟",
      "However much you beat it, it does not cry. It gives a happy sound. What is it?", "drum", "cat|pillow|ball",
      "دهل را می‌زنیم تا آواز بدهد.", "We beat a drum so that it sounds.")

    i = T("این سوال‌ها آسان معلوم می‌شود، ولی نیست! پیش از جواب دادن دو بار فکر کن.",
          "These questions seem easy, but they are not! Think twice before you answer.")
    q("03", i, "نجار یک چوب دراز را سه توته می‌کند. چند بار اره می‌کند؟",
      "A carpenter cuts a long piece of wood into three pieces. How many times does he saw?", "t:2", "t:3|t:4|t:1",
      "با یک بار اره کردن دو توته می‌شود. با دو بار اره کردن سه توته می‌شود.", "One cut makes two pieces. Two cuts make three pieces.")
    q("03", i, "پنج درخت در یک قطار ایستاده است. بین هر دو درخت یک چوکی است. چند چوکی است؟",
      "Five trees stand in a row. Between every two trees there is one chair. How many chairs are there?", "t:4", "t:5|t:6|t:3",
      "بین پنج درخت چهار جای خالی است. پس چهار چوکی است.", "Between five trees there are four gaps. So there are four chairs.")
    q("03", i, "اطاق چهار گوشه دارد. در هر گوشه یک پشک نشسته است. هر پشک سه پشک دیگر را می‌بیند. در اطاق چند پشک است؟",
      "A room has four corners. In every corner sits a cat. Every cat sees three other cats. How many cats are in the room?", "t:4", "t:12|t:16|t:3",
      "چهار گوشه، چهار پشک. هر پشک سه تای دیگر را می‌بیند، ولی پشک‌ها همان چهار است.",
      "Four corners, four cats. Every cat sees the other three, but the cats are the same four.")
    q("03", i, "یک پدر سه دختر دارد. هر دختر یک برادر دارد. این پدر چند طفل دارد؟",
      "A father has three daughters. Every daughter has one brother. How many children does this father have?", "t:4", "t:6|t:3|t:5",
      "سه دختر و یک پسر. همان یک پسر برادر هر سه دختر است.", "Three daughters and one son. That one son is the brother of all three daughters.")
    q("03", i, "یک کیلو پشم سنگین‌تر است، یا یک کیلو سنگ؟",
      "Which is heavier, one kilo of wool or one kilo of stone?", F("هر دو برابر", "both the same"), F("پشم", "wool") + "|" + F("سنگ", "stone") + "|" + F("هیچ کدام", "neither"),
      "یک کیلو یک کیلو است. پشم بسیار جای می‌گیرد، ولی وزن هر دو برابر است.",
      "A kilo is a kilo. The wool takes much more room, but both weigh the same.")
    q("03", i, "مورچه از دیواری بالا می‌رود که سه متر بلند است. هر روز دو متر بالا می‌رود و هر شب یک متر پایین می‌لغزد. روز چندم به سر دیوار می‌رسد؟",
      "An ant climbs a wall that is three metres high. Every day it climbs two metres and every night it slips down one metre. On which day does it reach the top?",
      "t:2", "t:3|t:4|t:1",
      "روز اول تا دو متر می‌رود و شب به یک متر می‌لغزد. روز دوم از یک متر دو متر بالا می‌رود و به سه متر می‌رسد.",
      "On the first day it gets to two metres and at night slips to one metre. On the second day it climbs two metres from one metre and reaches three metres.")
    q("03", i, "در یک بکس جراب‌های سرخ و آبی است. اطاق تاریک است و رنگ را نمی‌بینی. کم از کم چند جراب برداری تا حتماً دو جراب یک رنگ داشته باشی؟",
      "In a box there are red and blue socks. The room is dark and you cannot see the colour. How many socks must you take at least to be sure of having two socks of one colour?",
      "t:3", "t:2|t:4|t:10",
      "دو جراب شاید یکی سرخ و یکی آبی باشد. جراب سوم یا سرخ است یا آبی، پس با یکی از آن دو جور می‌شود.",
      "Two socks may be one red and one blue. The third sock is either red or blue, so it matches one of those two.")
    q("03", i, "دو پدر و دو پسر به ماهی‌گیری رفتند. هر کدام یک ماهی گرفت. همه با هم سه ماهی گرفتند. چند نفر بودند؟",
      "Two fathers and two sons went fishing. Each caught one fish. Together they caught three fish. How many people were there?",
      "t:3", "t:4|t:2|t:6",
      "سه نفر بودند: پدرکلان، پدر و پسر. پدر هم پدر است و هم پسرِ پدرکلان.",
      "There were three people: a grandfather, a father and a son. The father is both a father and the grandfather's son.")

    i = T("خوب گوش کن و گپ‌ها را با هم جوره کن. جواب در خود سوال است.",
          "Listen well and put the statements together. The answer is in the question itself.")
    q("04", i, "اسپ از گاو تیزتر می‌دود. گاو از خر تیزتر می‌دود. کدام از همه آهسته‌تر است؟",
      "The horse runs faster than the cow. The cow runs faster than the donkey. Which is the slowest of all?", "donkey", "horse|cow|hen",
      "اسپ از گاو تیزتر، و گاو از خر تیزتر است. پس خر از هر دو آهسته‌تر است.",
      "The horse is faster than the cow, and the cow faster than the donkey. So the donkey is slower than both.")
    q("04", i, "سیب از ناک سنگین‌تر است. تربوز از سیب سنگین‌تر است. کدام از همه سبک‌تر است؟",
      "The apple is heavier than the pear. The watermelon is heavier than the apple. Which is the lightest of all?", "pear", "apple|watermelon|orange",
      "ناک از سیب سبک‌تر است، و سیب از تربوز. پس ناک از همه سبک‌تر است.",
      "The pear is lighter than the apple, and the apple lighter than the watermelon. So the pear is the lightest of all.")
    q("04", i, "موش از پشک می‌ترسد. پشک از سگ می‌ترسد. کدام از هیچ کدام نمی‌ترسد؟",
      "The mouse is afraid of the cat. The cat is afraid of the dog. Which one is afraid of neither?", "dog", "cat|mouse|hen",
      "موش از پشک می‌ترسد و پشک از سگ. سگ از این دو نمی‌ترسد.", "The mouse fears the cat and the cat fears the dog. The dog fears neither of the two.")
    q("04", i, "دیروز جمعه بود. فردا چه روز است؟", "Yesterday was Friday. What day is tomorrow?",
      F("یکشنبه", "Sunday"), F("شنبه", "Saturday") + "|" + F("دوشنبه", "Monday") + "|" + F("جمعه", "Friday"),
      "دیروز جمعه بود، پس امروز شنبه است و فردا یکشنبه.", "Yesterday was Friday, so today is Saturday and tomorrow is Sunday.")
    q("04", i, "مرغ پیش از بز به خانه رسید. گوسفند بعد از بز رسید. کدام آخر رسید؟",
      "The hen came home before the goat. The sheep came after the goat. Which came last?", "sheep", "hen|goat|cow",
      "اول مرغ رسید، بعد بز، و بعد از بز گوسفند. پس گوسفند آخر رسید.", "First the hen came, then the goat, and after the goat the sheep. So the sheep came last.")
    q("04", i, "من هشت ساله استم. برادرم دو سال از من کلان‌تر است. وقتی من ده ساله شوم، برادرم چند ساله می‌شود؟",
      "I am eight years old. My brother is two years older than I am. When I am ten, how old will my brother be?", "t:12", "t:10|t:14|t:20",
      "برادرم همیشه دو سال از من کلان‌تر است. ده جمع دو مساوی دوازده.", "My brother is always two years older than I am. Ten plus two is twelve.")
    q("04", i, "مرغ دو پا دارد و بز چهار پا. در حویلی دو مرغ و یک بز است. همه با هم چند پا دارند؟",
      "A hen has two legs and a goat has four. In the yard there are two hens and one goat. How many legs do they have together?", "t:8", "t:6|t:3|t:10",
      "دو مرغ چهار پا دارند. یک بز چهار پا دارد. چهار جمع چهار مساوی هشت.", "Two hens have four legs. One goat has four legs. Four plus four is eight.")


# =============================================================================
# h  Squares and shapes (story: a grid or a figure as the large picture)
# =============================================================================

def game_grids():
    add = sheet("squares_shapes.csv", "story")
    say = T("در هر قطار و در هر ستون، هر کدام فقط یک بار می‌آید. در خانه زرد کدام یک می‌آید؟",
            "In every row and in every column, each one comes only once. Which one goes in the yellow square?")
    why_row = T("قطار خانه زرد را ببین. در آن قطار کدام یک هنوز نیست؟", "Look at the row of the yellow square. Which one is not yet in that row?")
    why_col = T("ستون خانه زرد را ببین، از بالا تا پایین. در آن ستون کدام یک هنوز نیست؟",
                "Look at the column of the yellow square, from top to bottom. Which one is not yet in that column?")
    why_both = T("هم قطار و هم ستون خانه زرد را ببین. آنچه در قطار یا در ستون است، در خانه زرد آمده نمی‌تواند.",
                 "Look at both the row and the column of the yellow square. What is already in the row or in the column cannot go in the yellow square.")
    why_far = T("اول فکر کن که در خانه‌های دیگر چه می‌آید. هر کدام در هر قطار و هر ستون فقط یک بار است.",
                "First think what goes in the other squares. Each one is only once in every row and every column.")
    k = itertools.count(1)

    def lat(rnd, intro, symbols, rows, gap, why):
        rows = [[symbols[c] if c is not None else None for c in r] for r in rows]
        found = S.latin_answers(rows, gap, symbols)
        assert len(found) == 1, f"grid {rnd}: empty place can be {found}"
        answer = found.pop()
        name = f"scene_puz_grid_{next(k):02d}"
        txt = " / ".join(" ".join("[EMPTY]" if (r, c) == gap else (rows[r][c] or "blank") for c in range(len(rows))) for r in range(len(rows)))
        S.grid(name, rows, gap, f"A {len(rows)} by {len(rows)} grid of cards, rows from the top: {txt}. One yellow empty place. (Drawn by make_puzzles.py.)")
        wrong = [s for s in symbols if s != answer][:3]
        add(rnd, intro, picture=name, say_fa=say, choices=mix(tok_thing(answer), [tok_thing(w) for w in wrong]),
            right=tok_thing(answer), wrong_say_fa=why)

    _ = None
    col3 = ["circle_red", "circle_blue", "circle_yellow"]
    shp3 = ["circle_red", "square_blue", "triangle_yellow"]
    ani3 = ["cat", "dog", "hen"]
    fru3 = ["apple", "pear", "orange"]
    i = T("این خانه‌ها یک قاعده دارد: در هر قطار و در هر ستون، هر رنگ یا هر تصویر فقط یک بار می‌آید. پیدا کن که در خانه زرد چه می‌آید.",
          "These squares have one rule: in every row and in every column, each colour or picture comes only once. Find what goes in the yellow square.")
    lat("01", i, col3, [[0, 1, 2], [1, 2, 0], [2, 0, 1]], (0, 2), why_row)
    lat("01", i, ani3, [[0, 1, 2], [2, 0, 1], [1, 2, 0]], (1, 1), why_row)
    lat("01", i, shp3, [[1, 0, 2], [0, 2, 1], [2, 1, 0]], (2, 0), why_row)
    lat("01", i, fru3, [[2, 1, 0], [0, 2, 1], [1, 0, 2]], (1, 2), why_row)
    lat("01", i, col3, [[0, _, _], [1, _, _], [2, _, _]], (1, 0), why_col)
    lat("01", i, ani3, [[_, _, _], [1, 0, 2], [_, _, _]], (1, 0), why_row)
    lat("01", i, shp3, [[_, 2, _], [_, 0, _], [_, 1, _]], (2, 1), why_col)

    i = T("حالا خانه‌های سفید زیاد است. برای خانه زرد هم قطار را ببین و هم ستون را.",
          "Now there are many white squares. For the yellow square look at both the row and the column.")
    col4 = ["circle_red", "circle_blue", "circle_yellow", "circle_green"]
    ani4 = ["cat", "dog", "hen", "fish"]
    lat("02", i, col3, [[0, _, _], [_, 1, _], [_, _, _]], (0, 1), why_both)
    lat("02", i, fru3, [[_, _, 0], [_, _, _], [1, _, _]], (2, 2), why_both)
    lat("02", i, shp3, [[_, _, 0], [_, _, _], [1, _, _]], (1, 1), why_far)
    lat("02", i, col4, [[0, 1, 2, 3], [1, 0, 3, 2], [2, 3, 0, 1], [3, 2, 1, 0]], (2, 1), why_row)
    lat("02", i, ani4, [[0, 1, _, _], [_, _, _, _], [_, _, 2, _], [_, _, _, _]], (0, 2), why_both)
    lat("02", i, col4, [[_, 0, _, _], [1, _, 2, _], [_, _, _, _], [_, _, _, _]], (1, 1), why_both)
    lat("02", i, ani3, [[0, _, _], [_, _, 1], [_, _, _]], (2, 1), why_far)

    # ---- figures to count
    say_t = T("در این شکل چند مثلث است؟ خُرد و کلان را بشمار.", "How many triangles are in this figure? Count the small ones and the big ones.")
    say_s = T("در این شکل چند مربع است؟ خُرد و کلان را بشمار.", "How many squares are in this figure? Count the small ones and the big ones.")
    why_t = T("اول مثلث‌های خُرد را بشمار. بعد مثلث‌های کلان را که از چند مثلث خُرد ساخته شده است.",
              "First count the small triangles. Then the big triangles that are made of several small ones.")
    why_s = T("اول مربع‌های خُرد را بشمار. بعد مربع‌های کلان را که از چند مربع خُرد ساخته شده است.",
              "First count the small squares. Then the big squares that are made of several small ones.")
    kf = itertools.count(1)
    SQ = (100, 50, 300, 250)

    def box(x1, y1, x2, y2):
        return [(x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)]

    def cells(x1, y1, x2, y2, nx, ny):
        segs = []
        for a in range(nx + 1):
            x = x1 + (x2 - x1) * a / nx
            segs.append((x, y1, x, y2))
        for b in range(ny + 1):
            y = y1 + (y2 - y1) * b / ny
            segs.append((x1, y, x2, y))
        return segs

    A, B, C = (200, 36), (60, 262), (340, 262)

    def fan(n):   # a triangle with n lines from the top to the base
        segs = [(*A, *B), (*B, *C), (*C, *A)]
        for j in range(1, n + 1):
            x = B[0] + (C[0] - B[0]) * j / (n + 1)
            segs.append((*A, x, B[1]))
        return segs

    def count(rnd, intro, what, segs, fill, expect, wrong, en):
        n = S.count_triangles(segs) if what == "t" else S.count_rects(segs, squares_only=True)
        assert n == expect, f"figure {en}: counted {n}, expected {expect}"
        name = f"scene_puz_count_{next(kf):02d}"
        S.figure(name, segs, fill, f"A line figure on a plain ground: {en}. It holds exactly {n} {'triangles' if what == 't' else 'squares'}. (Drawn by make_puzzles.py.)")
        assert str(n) not in wrong.split()
        add(rnd, intro, picture=name, say_fa=say_t if what == "t" else say_s,
            choices=mix(f"t:{n}", ["t:" + w for w in wrong.split()]), right=f"t:{n}",
            wrong_say_fa=why_t if what == "t" else why_s)

    sq_poly = [[(SQ[0], SQ[1]), (SQ[2], SQ[1]), (SQ[2], SQ[3]), (SQ[0], SQ[3])]]
    tri_poly = [[A, B, C]]
    i = T("در یک شکل، شکل‌های دیگر پنهان است. همه را پیدا کن و بشمار.", "Other shapes are hidden in a figure. Find them all and count.")
    count("03", i, "t", box(*SQ) + [(SQ[0], SQ[1], SQ[2], SQ[3])], sq_poly, 2, "1 3 4", "a square with one diagonal")
    count("03", i, "t", fan(1), tri_poly, 3, "2 4", "a triangle with one line from the top corner to the base")
    count("03", i, "s", cells(*SQ, 2, 2), sq_poly, 5, "4 6", "a square cut into 2 by 2 small squares")
    count("03", i, "s", box(80, 40, 230, 190) + box(155, 115, 305, 265),
          [[(80, 40), (230, 40), (230, 190), (80, 190)], [(155, 115), (305, 115), (305, 265), (155, 265)]], 3, "2 4",
          "two equal squares that overlap at a corner, so that the overlap is a small square")
    count("03", i, "t", fan(2), tri_poly, 6, "3 5 4", "a triangle with two lines from the top corner to the base")
    count("03", i, "t", box(*SQ) + [(SQ[0], SQ[1], SQ[2], SQ[3]), (SQ[2], SQ[1], SQ[0], SQ[3])], sq_poly, 8, "4 6",
          "a square with both diagonals")

    i = T("این شکل‌ها مشکل‌تر است. آهسته و با ترتیب بشمار: اول خُردها، بعد کلان‌ها.",
          "These figures are harder. Count slowly and in order: first the small ones, then the big ones.")
    count("04", i, "s", cells(*SQ, 3, 3), sq_poly, 14, "9 10 13", "a square cut into 3 by 3 small squares")
    mid_y = 149
    ex = B[0] + (A[0] - B[0]) * (B[1] - mid_y) / (B[1] - A[1])
    count("04", i, "t", fan(1) + [(ex, mid_y, 400 - ex, mid_y)], tri_poly, 6, "4 5 8",
          "a triangle with one line from the top corner to the base and one line across, parallel to the base")
    count("04", i, "s", cells(80, 70, 320, 230, 3, 2), [[(80, 70), (320, 70), (320, 230), (80, 230)]], 8, "6 7",
          "a rectangle cut into 3 by 2 small squares")
    hs = (120, 120, 280, 280)
    count("04", i, "t", box(*hs) + [(hs[0], hs[1], hs[2], hs[3]), (hs[2], hs[1], hs[0], hs[3]), (hs[0], hs[1], 200, 30), (200, 30, hs[2], hs[1])],
          [[(hs[0], hs[1]), (200, 30), (hs[2], hs[1]), (hs[2], hs[3]), (hs[0], hs[3])]], 9, "5 8 10",
          "a house: a square with both diagonals and a triangle roof on top")
    count("04", i, "t", fan(3), tri_poly, 10, "4 8 9", "a triangle with three lines from the top corner to the base")
    count("04", i, "t", box(*SQ) + [(SQ[0], SQ[1], SQ[2], SQ[3]), (SQ[2], SQ[1], SQ[0], SQ[3]), (200, SQ[1], 200, SQ[3]), (SQ[0], 150, SQ[2], 150)],
          sq_poly, 16, "8 12 14", "a square with both diagonals and both middle lines")


# =============================================================================
# i  Thinking stories (story)
# =============================================================================

def game_stories():
    add = sheet("thinking_stories.csv", "story")

    def page(rnd, intro, pic, fa, en, show=True):
        t = T(fa, en)
        add(rnd, intro, picture=pic, say_fa=t, show_fa=t if show else "")

    def ask(rnd, intro, pic, fa, en, right, wrong, wfa, wen, wrong_pic=""):
        add(rnd, intro, picture=pic, say_fa=T(fa, en), choices=mix(right, wrong), right=right,
            wrong_say_fa=T(wfa, wen), wrong_picture=wrong_pic)

    # ---- 01 the farmer, the fox, the hen and the wheat
    r = "01"
    i = T("این یک معمای بسیار قدیمی است. قصه را گوش کن و به دهقان کمک کن.", "This is a very old puzzle. Listen to the story and help the farmer.")
    who = "the farmer in his small boat, the fox, the hen and the sack of wheat"
    s0 = S.river("scene_puz_river_0", ["fox", "hen", "flour_sack"], [], "near", f"A river from top to bottom, green banks. On the right bank: fox, hen, sack of wheat. {who}: the boat lies at the right bank.")
    s1 = S.river("scene_puz_river_1", ["fox", "flour_sack"], ["hen"], "near", "The same river. Hen alone on the left bank. Fox and sack on the right bank; the farmer's boat is back at the right bank.")
    s2 = S.river("scene_puz_river_2", ["flour_sack"], ["fox", "hen"], "far", "The same river. Fox and hen on the left bank, the boat with the farmer at the left bank. The sack alone on the right bank.")
    s3 = S.river("scene_puz_river_3", ["hen", "flour_sack"], ["fox"], "near", "The same river. Fox alone on the left bank. Hen and sack on the right bank, the boat with the farmer at the right bank.")
    s4 = S.river("scene_puz_river_4", ["hen"], ["fox", "flour_sack"], "far", "The same river. Fox and sack on the left bank with the boat. The hen alone on the right bank.")
    s5 = S.river("scene_puz_river_5", [], ["fox", "hen", "flour_sack"], "far", "The same river. Fox, hen and sack all on the left bank, the boat with the farmer at the left bank. The right bank is empty.")
    danger = D.scene("scene_puz_river_danger",
                     D.card(14, 30, 180, 240, fill=D.CREAM, sw=4) + D.card(206, 30, 180, 240, fill=D.CREAM, sw=4)
                     + D.embed("fox", 24, 40, 100) + D.embed("hen", 96, 160, 90) + D.embed("no", 30, 170, 60)
                     + D.embed("hen", 216, 40, 100) + D.embed("flour_sack", 290, 160, 90) + D.embed("no", 222, 170, 60),
                     "Two panels. Left: the fox above the hen, with a red cross (they must not be left alone). Right: the hen above the sack of wheat, with a red cross.")
    empty = D.obj("puz_boat_empty",
                  f'<rect x="6" y="70" width="116" height="46" rx="10" fill="{D.WATER}" stroke="{D.INK}" stroke-width="5"/>'
                  f'<path d="M20 100q10-8 20 0t20 0M70 106q10-8 20 0t20 0" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/>'
                  f'<path d="M14 50H114L96 88H32z" fill="#9a6b3f" stroke="{D.INK}" stroke-width="5" stroke-linejoin="round"/>'
                  f'<path d="M30 62H98" fill="none" stroke="{D.INK}" stroke-width="4" stroke-linecap="round"/>',
                  "An empty wooden boat on water, nobody and nothing in it (the choice 'take nothing').")
    page(r, i, s0, "دهقان می‌خواهد با یک روباه، یک مرغ و یک بوجی گندم از دریا بگذرد.",
         "A farmer wants to cross the river with a fox, a hen and a sack of wheat.")
    page(r, i, s0, "کشتی او خُرد است. هر بار فقط یکی را با خود برده می‌تواند.", "His boat is small. Each time he can take only one of them with him.")
    page(r, i, danger, "اگر روباه با مرغ تنها بماند، مرغ را می‌خورد. اگر مرغ با گندم تنها بماند، گندم را می‌خورد.",
         "If the fox is left alone with the hen, it eats the hen. If the hen is left alone with the wheat, it eats the wheat.")
    ask(r, i, s0, "دهقان اول کدام را ببرد؟", "Which one should the farmer take first?", "hen", ["fox", "flour_sack"],
        "این نمی‌شود. اگر مرغ این طرف بماند، یا روباه مرغ را می‌خورد، یا مرغ گندم را.",
        "That does not work. If the hen stays on this side, either the fox eats the hen, or the hen eats the wheat.", danger)
    page(r, i, s1, "دهقان مرغ را برد و تنها برگشت. روباه گندم نمی‌خورد.", "The farmer took the hen across and came back alone. A fox does not eat wheat.")
    page(r, i, s2, "بعد روباه را برد. حالا روباه و مرغ در آن طرف استند.", "Then he took the fox across. Now the fox and the hen are on the other side.")
    ask(r, i, s2, "دهقان باید برگردد و گندم را بیاورد. ولی روباه و مرغ تنها می‌مانند! کدام را با خود پس ببرد؟",
        "The farmer has to go back and fetch the wheat. But the fox and the hen would be left alone! Which one should he take back with him?",
        "hen", ["fox", empty],
        "این نمی‌شود. اگر تنها برود، روباه مرغ را می‌خورد. اگر روباه را پس ببرد، همه چیز مثل پیش می‌شود.",
        "That does not work. If he goes alone, the fox eats the hen. If he takes the fox back, everything is as it was before.", danger)
    page(r, i, s3, "دهقان مرغ را پس آورد. حالا روباه در آن طرف تنها است.", "The farmer brought the hen back. Now the fox is alone on the other side.")
    ask(r, i, s3, "حالا کدام را ببرد؟", "Which one should he take now?", "flour_sack", ["hen"],
        "اگر باز مرغ را ببرد، دوباره همان مشکل پیش می‌آید. گندم را ببرد: روباه گندم نمی‌خورد.",
        "If he takes the hen again, the same trouble comes again. Let him take the wheat: a fox does not eat wheat.")
    page(r, i, s4, "دهقان گندم را برد و مرغ را این طرف ماند. روباه گندم نمی‌خورد.", "The farmer took the wheat across and left the hen on this side. A fox does not eat wheat.")
    page(r, i, s5, "در آخر تنها برگشت و مرغ را آورد. همه سالم از دریا گذشتند. آفرین!",
         "At last he came back alone and fetched the hen. They all crossed the river safely. Well done!")

    # ---- 02 the balance
    r = "02"
    i = T("با ترازو فکر می‌کنیم. ترازو را خوب ببین و جواب بده.", "We think with a balance. Look well at the balance and answer.")
    b0 = S.scales("scene_puz_scale_0", [(["watermelon"], ["apple"], -1)], "A balance. Left pan: a watermelon, DOWN. Right pan: an apple, up.")
    page(r, i, b0, "این ترازو است. طرفی که پایین می‌رود، سنگین‌تر است.", "This is a balance. The side that goes down is the heavier one.")
    b1 = S.scales("scene_puz_scale_1", [(["egg"], ["stone"], 1)], "A balance. Left pan: an egg, up. Right pan: a stone, DOWN.")
    ask(r, i, b1, "کدام سنگین‌تر است؟", "Which is heavier?", "stone", ["egg"],
        "طرفی که پایین است، سنگین‌تر است.", "The side that is down is the heavier one.")
    b2 = S.scales("scene_puz_scale_2", [(["circle_red"], ["circle_blue"], 1)], "A balance. Left pan: a red ball, UP. Right pan: a blue ball, down.")
    ask(r, i, b2, "کدام توپ سبک‌تر است؟", "Which ball is lighter?", tok_thing("circle_red"), [tok_thing("circle_blue")],
        "طرفی که بالا است، سبک‌تر است.", "The side that is up is the lighter one.")
    b3 = S.scales("scene_puz_scale_3", [(["circle_red"], ["circle_blue"], -1), (["circle_blue"], ["circle_yellow"], -1)],
                  "Two balances side by side. First: red ball DOWN against blue ball. Second: blue ball DOWN against yellow ball.")
    ask(r, i, b3, "توپ سرخ از آبی سنگین‌تر است. توپ آبی از زرد سنگین‌تر است. کدام توپ از همه سنگین‌تر است؟",
        "The red ball is heavier than the blue one. The blue ball is heavier than the yellow one. Which ball is the heaviest of all?",
        tok_thing("circle_red"), [tok_thing("circle_blue"), tok_thing("circle_yellow")],
        "سرخ از آبی سنگین‌تر است، و آبی از زرد. پس سرخ از هر دو سنگین‌تر است.",
        "Red is heavier than blue, and blue heavier than yellow. So red is heavier than both.")
    b4 = S.scales("scene_puz_scale_4", [(["circle_yellow"], ["circle_blue"], 1), (["circle_green"], ["circle_yellow"], 1)],
                  "Two balances side by side. First: yellow ball up, blue ball DOWN. Second: green ball up, yellow ball DOWN.")
    ask(r, i, b4, "دو ترازو را ببین. کدام توپ از همه سبک‌تر است؟", "Look at the two balances. Which ball is the lightest of all?",
        tok_thing("circle_green"), [tok_thing("circle_blue"), tok_thing("circle_yellow")],
        "زرد از آبی سبک‌تر است. سبز از زرد هم سبک‌تر است. پس سبز از همه سبک‌تر است.",
        "Yellow is lighter than blue. Green is lighter still than yellow. So green is the lightest of all.")
    b5 = S.scales("scene_puz_scale_5", [(["circle_red"], ["circle_blue"], 0)], "A level balance: a red ball on the left pan, a blue ball on the right pan. A yellow ball lies beside the balance.",
                  aside=["circle_yellow"])
    ask(r, i, b5, "یکی از این سه توپ از دو تای دیگر سنگین‌تر است. ترازو برابر ایستاده است. کدام توپ سنگین است؟",
        "One of these three balls is heavier than the other two. The balance stands level. Which ball is the heavy one?",
        tok_thing("circle_yellow"), [tok_thing("circle_red"), tok_thing("circle_blue")],
        "ترازو برابر است، پس سرخ و آبی هم‌وزن استند. توپ سنگین روی ترازو نیست.",
        "The balance is level, so red and blue weigh the same. The heavy ball is not on the balance.")
    b6 = S.scales("scene_puz_scale_6", [(["watermelon"], ["apple", "apple"], 0), (["apple"], ["apricot", "apricot"], 0)],
                  "Two level balances. First: one watermelon against two apples. Second: one apple against two apricots.")
    ask(r, i, b6, "یک تربوز هم‌وزن دو سیب است. یک سیب هم‌وزن دو زردآلو است. یک تربوز هم‌وزن چند زردآلو است؟",
        "One watermelon weighs the same as two apples. One apple weighs the same as two apricots. How many apricots weigh the same as one watermelon?",
        "t:4", ["t:2", "t:3"],
        "هر سیب هم‌وزن دو زردآلو است. تربوز دو سیب است: دو بار دو زردآلو.",
        "Every apple weighs the same as two apricots. The watermelon is two apples: two times two apricots.")
    page(r, i, b0, "آفرین! تو مثل یک دکاندار ماهر با ترازو فکر کردی.", "Well done! You thought with the balance like a skilled shopkeeper.")

    # ---- 03 who has which? (two stories)
    r = "03"
    i = T("کی چه دارد؟ نشانی‌ها را خوب بشنو و فکر کن. جواب را کسی نمی‌گوید، خودت پیدا می‌کنی.",
          "Who has what? Listen well to the clues and think. Nobody tells the answer, you find it yourself.")

    def portraits(*kids):
        out = []
        for kd, fa, en in kids:
            name = f"scene_puz_kid_{kd}"
            if name not in D.briefs:
                S.portrait(name, ["kid:" + kd], S.KID_BRIEF[kd] + " Large, alone, sky and grass behind.")
            page(r, i, name, f"این {fa} است.", f"This is {en}.")

    L, Y, M = "girl_red", "boy_blue", "girl_green"
    portraits((L, "لیلا", "Laila"), (Y, "یوسف", "Yusuf"), (M, "مریم", "Maryam"))
    a_all = S.who_all("scene_puz_who_a0", ["kid:" + L, "kid:" + Y, "kid:" + M], ["hen", "goat", "cat"], "Three children in a row (girl in red, boy in blue, girl in green). Below, in a frame of their own: a hen, a goat, a cat.")
    page(r, i, a_all, "هر کدام یک حیوان دارد: یک پشک، یک مرغ و یک بز. ولی کدام حیوان از کیست؟",
         "Each of them has one animal: a cat, a hen and a goat. But which animal is whose?")
    a1 = S.who_clue("scene_puz_who_a1", "kid:" + Y, "hen", True, "The boy in blue beside a hen, with a green tick: he has the hen.")
    a2 = S.who_clue("scene_puz_who_a2", "kid:" + L, "cat", False, "The girl in red beside a cat, with a red cross: she does not have the cat.")
    page(r, i, a1, "یوسف مرغ دارد.", "Yusuf has the hen.")
    page(r, i, a2, "لیلا پشک ندارد.", "Laila does not have the cat.")
    a_s1 = S.who_final("scene_puz_who_a4", [("kid:" + Y, "hen", True), ("kid:" + L, "cat", False)],
                       "Two frames, the clues so far: the boy in blue with a hen and a green tick; the girl in red with a cat and a red cross.")
    a_s2 = S.who_final("scene_puz_who_a5", [("kid:" + Y, "hen", True), ("kid:" + L, "goat", True)],
                       "Two frames: the boy in blue with a hen and a green tick; the girl in red with a goat and a green tick.")
    ask(r, i, a_s1, "لیلا کدام حیوان را دارد؟", "Which animal does Laila have?", "goat", ["cat", "hen"],
        "لیلا پشک ندارد. مرغ از یوسف است. پس برای لیلا کدام می‌ماند؟", "Laila does not have the cat. The hen is Yusuf's. So which one is left for Laila?")
    ask(r, i, a_s2, "مریم کدام حیوان را دارد؟", "Which animal does Maryam have?", "cat", ["hen", "goat"],
        "مرغ از یوسف است و بز از لیلا. برای مریم کدام می‌ماند؟", "The hen is Yusuf's and the goat is Laila's. Which one is left for Maryam?")
    a_end = S.who_final("scene_puz_who_a3", [("kid:" + L, "goat"), ("kid:" + Y, "hen"), ("kid:" + M, "cat")],
                        "Three frames: the girl in red with a goat, the boy in blue with a hen, the girl in green with a cat.")
    page(r, i, a_end, "آفرین! یوسف مرغ دارد، لیلا بز دارد و مریم پشک دارد.", "Well done! Yusuf has the hen, Laila has the goat and Maryam has the cat.")

    SH, O, K = "girl_blue", "boy_orange", "boy_green"
    portraits((SH, "شیرین", "Shirin"), (O, "عمر", "Omar"), (K, "کریم", "Karim"))
    b_all = S.who_all("scene_puz_who_b0", ["kid:" + O, "kid:" + SH, "kid:" + K], ["pear", "pomegranate", "apple"], "Three children in a row (boy in orange, girl in blue, boy in green). Below, in a frame: a pear, a pomegranate, an apple.")
    page(r, i, b_all, "هر کدام یک میوه دارد: یک سیب، یک ناک و یک انار.", "Each of them has one fruit: an apple, a pear and a pomegranate.")
    c1 = S.who_clue("scene_puz_who_b1", "kid:" + SH, "apple", False, "The girl in blue beside an apple, with a red cross.")
    c2 = S.who_clue("scene_puz_who_b2", "kid:" + SH, "pear", False, "The girl in blue beside a pear, with a red cross.")
    c3 = S.who_clue("scene_puz_who_b3", "kid:" + K, "apple", False, "The boy in green beside an apple, with a red cross.")
    page(r, i, c1, "شیرین سیب ندارد.", "Shirin does not have the apple.")
    page(r, i, c2, "شیرین ناک هم ندارد.", "Shirin does not have the pear either.")
    b_s1 = S.who_final("scene_puz_who_b5", [("kid:" + SH, "apple", False), ("kid:" + SH, "pear", False)],
                       "Two frames, the clues so far: the girl in blue with an apple and a red cross; the girl in blue with a pear and a red cross.")
    b_s2 = S.who_final("scene_puz_who_b6", [("kid:" + SH, "pomegranate", True), ("kid:" + K, "apple", False)],
                       "Two frames: the girl in blue with a pomegranate and a green tick; the boy in green with an apple and a red cross.")
    b_s3 = S.who_final("scene_puz_who_b7", [("kid:" + SH, "pomegranate", True), ("kid:" + K, "pear", True)],
                       "Two frames: the girl in blue with a pomegranate and a green tick; the boy in green with a pear and a green tick.")
    ask(r, i, b_s1, "شیرین کدام میوه را دارد؟", "Which fruit does Shirin have?", "pomegranate", ["apple", "pear"],
        "شیرین نه سیب دارد و نه ناک. فقط یک میوه می‌ماند.", "Shirin has neither the apple nor the pear. Only one fruit is left.")
    page(r, i, c3, "کریم سیب ندارد.", "Karim does not have the apple.")
    ask(r, i, b_s2, "کریم کدام میوه را دارد؟", "Which fruit does Karim have?", "pear", ["apple", "pomegranate"],
        "کریم سیب ندارد، و انار از شیرین است.", "Karim does not have the apple, and the pomegranate is Shirin's.")
    ask(r, i, b_s3, "پس سیب از کیست؟", "So whose is the apple?", tok_thing("kid:" + O), [tok_thing("kid:" + SH), tok_thing("kid:" + K)],
        "شیرین انار دارد و کریم ناک. کی مانده است؟", "Shirin has the pomegranate and Karim the pear. Who is left?")
    b_end = S.who_final("scene_puz_who_b4", [("kid:" + O, "apple"), ("kid:" + SH, "pomegranate"), ("kid:" + K, "pear")],
                        "Three frames: the boy in orange with an apple, the girl in blue with a pomegranate, the boy in green with a pear.")
    page(r, i, b_end, "آفرین! عمر سیب دارد، شیرین انار دارد و کریم ناک دارد.", "Well done! Omar has the apple, Shirin has the pomegranate and Karim has the pear.")

    # ---- 04 the race, and the three houses
    r = "04"
    i = T("دو قصه دیگر برای فکر کردن. هر نشانی را به یاد داشته باش.", "Two more stories to think about. Keep every clue in mind.")
    Z, FA, NA = "girl_red", "boy_green", "girl_green"
    portraits((Z, "زهرا", "Zahra"), (FA, "فرید", "Farid"), (NA, "نرگس", "Narges"))
    race = S.portrait("scene_puz_race_0", ["kid:" + Z, "kid:" + FA, "kid:" + NA], "Three children side by side on grass: girl in red, boy in green, girl in green.")
    page(r, i, race, "زهرا، فرید و نرگس مسابقه دویدن کردند.", "Zahra, Farid and Narges ran a race.")
    page(r, i, race, "فرید آخر نشد.", "Farid was not last.")
    page(r, i, race, "نرگس پیش از فرید رسید.", "Narges arrived before Farid.")
    kids = [tok_thing("kid:" + x) for x in (Z, FA, NA)]
    ask(r, i, race, "کی اول شد؟", "Who came first?", kids[2], [kids[0], kids[1]],
        "نرگس پیش از فرید رسید، پس فرید اول نیست. فرید آخر هم نشد، پس فرید دوم است. کی پیش از فرید است؟",
        "Narges arrived before Farid, so Farid is not first. Farid was not last either, so Farid is second. Who is before Farid?")
    ask(r, i, race, "کی آخر شد؟", "Who came last?", kids[0], [kids[1], kids[2]],
        "نرگس اول شد و فرید دوم. کی می‌ماند؟", "Narges came first and Farid second. Who is left?")
    r_end = S.who_final("scene_puz_race_1", [("kid:" + NA, "n:1"), ("kid:" + FA, "n:2"), ("kid:" + Z, "n:3")],
                        "Three frames: the girl in green with the number 1, the boy in green with the number 2, the girl in red with the number 3.")
    page(r, i, r_end, "آفرین! نرگس اول شد، فرید دوم و زهرا سوم.", "Well done! Narges came first, Farid second and Zahra third.")

    h_all = S.who_all("scene_puz_house_0", ["house_red", "house_blue", "house_yellow"], ["cat", "dog", "hen"], "Three small houses in a row: red, blue, yellow. Below, in a frame: a cat, a dog, a hen.")
    hred, hblue, hyel = (tok_thing("house_" + c) for c in ("red", "blue", "yellow"))
    page(r, i, h_all, "سه خانه است: سرخ، آبی و زرد. در هر خانه یک حیوان زندگی می‌کند: پشک، سگ و مرغ.",
         "There are three houses: red, blue and yellow. In each house lives one animal: the cat, the dog and the hen.")
    h1 = S.who_clue("scene_puz_house_1", "dog", "house_blue", True, "The dog beside the blue house, with a green tick: the dog lives in the blue house.")
    h2 = S.who_clue("scene_puz_house_2", "cat", "house_yellow", False, "The cat beside the yellow house, with a red cross: the cat does not live in the yellow house.")
    page(r, i, h1, "سگ در خانه آبی زندگی می‌کند.", "The dog lives in the blue house.")
    page(r, i, h2, "پشک در خانه زرد زندگی نمی‌کند.", "The cat does not live in the yellow house.")
    h_s1 = S.who_final("scene_puz_house_4", [("dog", "house_blue", True), ("cat", "house_yellow", False)],
                       "Two frames, the clues so far: the dog with the blue house and a green tick; the cat with the yellow house and a red cross.")
    h_s2 = S.who_final("scene_puz_house_5", [("dog", "house_blue", True), ("cat", "house_red", True)],
                       "Two frames: the dog with the blue house and a green tick; the cat with the red house and a green tick.")
    ask(r, i, h_s1, "خانه پشک کدام است؟", "Which is the cat's house?", hred, [hblue, hyel],
        "خانه آبی از سگ است. پشک در خانه زرد هم نیست. کدام خانه می‌ماند؟", "The blue house is the dog's. The cat is not in the yellow house either. Which house is left?")
    ask(r, i, h_s2, "خانه مرغ کدام است؟", "Which is the hen's house?", hyel, [hred, hblue],
        "خانه آبی از سگ است و خانه سرخ از پشک. برای مرغ کدام می‌ماند؟", "The blue house is the dog's and the red house is the cat's. Which one is left for the hen?")
    h_end = S.who_final("scene_puz_house_3", [("cat", "house_red"), ("dog", "house_blue"), ("hen", "house_yellow")],
                        "Three frames: the cat with the red house, the dog with the blue house, the hen with the yellow house.")
    page(r, i, h_end, "آفرین! پشک در خانه سرخ، سگ در خانه آبی و مرغ در خانه زرد زندگی می‌کند.",
         "Well done! The cat lives in the red house, the dog in the blue house and the hen in the yellow house.")

    # ---- 05 the shortest way, and sharing fairly
    r = "05"
    i = T("کوتاه‌ترین راه کدام است؟ و چطور یک نان را عادلانه تقسیم کنیم؟ فکر کن و جواب بده.",
          "Which is the shortest way? And how do we share one bread fairly? Think and answer.")
    w1 = S.ways("scene_puz_way_1", "house", "school", [
        ("red", [(322, 120), (260, 40), (140, 40), (78, 120)], 9),
        ("blue", [(318, 150), (82, 150)], 6),
        ("yellow", [(322, 182), (290, 262), (110, 262), (78, 182)], 10)],
        "A house on the right, a school on the left, three ways of stepping stones between them: a red way over the top with 9 stones, a straight blue way with 6 stones, a yellow way round the bottom with 10 stones.")
    page(r, i, w1, "زهرا از خانه به مکتب می‌رود. سه راه است: سرخ، آبی و زرد.", "Zahra walks from home to school. There are three ways: red, blue and yellow.")
    why = ("سنگ‌های هر راه را بشمار. راهی که کمترین سنگ را دارد، کوتاه‌ترین است.", "Count the stones of every way. The way with the fewest stones is the shortest.")
    ask(r, i, w1, "کدام راه کوتاه‌ترین است؟ سنگ‌ها را بشمار.", "Which way is the shortest? Count the stones.",
        "color_blue", ["color_red", "color_yellow"], *why)
    w2 = S.ways("scene_puz_way_2", "house", "well", [
        ("red", [(326, 116), (296, 40), (236, 92), (176, 34), (116, 92), (76, 116)], 11),
        ("blue", [(318, 150), (268, 172), (200, 142), (132, 172), (82, 150)], 8),
        ("yellow", [(322, 184), (250, 268), (140, 268), (78, 184)], 7)],
        "A house on the right, a well on the left. A red zigzag way over the top with 11 stones, a blue wavy way through the middle with 8 stones, a yellow way round the bottom with 7 stones.")
    page(r, i, w2, "حالا زهرا به چاه می‌رود. راه‌ها پیچ و خم دارد.", "Now Zahra walks to the well. The ways wind and bend.")
    ask(r, i, w2, "کدام راه کوتاه‌ترین است؟ با چشم باور نکن، بشمار.", "Which way is the shortest? Do not trust your eyes, count.",
        "color_yellow", ["color_red", "color_blue"], *why)

    G, Bk = "girl_blue", "boy_orange"
    f0 = S.portrait("scene_puz_share_0", ["kid:" + G, "bread", "kid:" + Bk], "A girl in blue and a boy in orange with one flat bread between them.")
    page(r, i, f0, "لیلا و کریم یک نان دارند. هر دو گرسنه استند.", "Laila and Karim have one bread. Both are hungry.")
    page(r, i, f0, "هر کدام می‌خواهد توته کلان‌تر را بگیرد. چطور نان را عادلانه تقسیم کنند؟",
         "Each of them wants to get the bigger piece. How can they share the bread fairly?")
    page(r, i, f0, "مادر می‌گوید: یکی نان را دو توته کند، و دیگری اول انتخاب کند.",
         "Mother says: one of you cuts the bread in two, and the other one chooses first.")
    ask(r, i, f0, "کریم نان را دو توته می‌کند. کی اول انتخاب کند؟", "Karim cuts the bread in two. Who should choose first?",
        tok_thing("kid:" + G), [tok_thing("kid:" + Bk)],
        "کریم نان را توته کرد. اگر خودش اول انتخاب کند، توته کلان را می‌گیرد. این عادلانه نیست.",
        "Karim cut the bread. If he also chooses first, he takes the big piece. That is not fair.")
    eq = D.obj("puz_bread_equal",
               f'<g {D.G5}><path d="M58 22C24 22 8 44 8 64s16 42 50 42z" fill="#e8b96a"/><path d="M70 22c34 0 50 22 50 42s-16 42-50 42z" fill="#e8b96a"/></g>'
               f'<path d="M28 50l14 28M44 40l4 44M82 40l-4 44M100 50l-14 28" fill="none" stroke="#9a6b3f" stroke-width="4" stroke-linecap="round"/>',
               "A flat oval bread cut into two EQUAL halves, a small gap between them.")
    uneq = D.obj("puz_bread_unequal",
                 f'<g {D.G5}><path d="M82 24C40 14 6 40 6 64s34 50 76 40z" fill="#e8b96a"/><path d="M96 30c16 6 26 20 26 34s-10 28-26 34z" fill="#e8b96a"/></g>'
                 f'<path d="M26 50l14 28M44 38l4 50M64 36l-2 54" fill="none" stroke="#9a6b3f" stroke-width="4" stroke-linecap="round"/>',
                 "The same flat bread cut into one BIG piece and one SMALL piece. Pair with puz_bread_equal.")
    ask(r, i, f0, "کریم می‌داند که لیلا اول انتخاب می‌کند. نان را چطور توته کند تا خودش کم نگیرد؟",
        "Karim knows that Laila chooses first. How should he cut the bread so that he himself does not get less?",
        eq, [uneq],
        "اگر یک توته کلان و یک توته خُرد باشد، لیلا توته کلان را می‌گیرد و برای کریم توته خُرد می‌ماند.",
        "If there is one big piece and one small piece, Laila takes the big piece and the small one is left for Karim.")
    f1 = S.portrait("scene_puz_share_1", ["kid:" + G, "bread_half", "kid:" + Bk], "The girl in blue and the boy in orange, half a bread shown between them (each got an equal half).")
    page(r, i, f1, "کریم نان را دو توته برابر کرد. هر کدام نیم نان گرفت. این تقسیم عادلانه است.",
         "Karim cut the bread into two equal pieces. Each got half the bread. That is a fair share.")


# =============================================================================

PACK_TEXTS = [
    ("دو کارت را پیدا کن که با هم جور است.", "Find two cards that belong together."),
    ("چهار تصویر را ببین. یکی با سه تای دیگر جور نیست. همان را انتخاب کن.", "Look at the four pictures. One does not belong with the other three. Choose that one."),
    ("قطار را خوب ببین و پیدا کن که در جای خالی چه می‌آید.", "Look well at the row and find what goes in the empty place."),
    ("تصویر میان را ببین و جواب درست را انتخاب کن.", "Look at the picture in the middle and choose the right answer."),
    ("گوش کن و تصویرها را به ترتیب درست بمان.", "Listen and put the pictures in the right order."),
    ("به دو چیز فکر کن و هر کدام را در سبد درست بینداز.", "Think of two things and drop each one into the right basket."),
    ("چیستان را گوش کن، فکر کن و جواب درست را انتخاب کن.", "Listen to the riddle, think and choose the right answer."),
    ("شکل را خوب ببین، فکر کن و جواب درست را انتخاب کن.", "Look well at the figure, think and choose the right answer."),
    ("قصه را گوش کن و در هر سوال فکر کن که چه باید کرد.", "Listen to the story and at every question think what should be done."),
]


def main() -> None:
    check = "--check" in sys.argv
    if check:
        D.save = lambda name, viewbox, body, brief: D.briefs.setdefault(name, brief) and name  # noqa: E731
        D.obj = lambda name, body, brief: D.save(name, "", body, brief)
        D.scene = lambda name, body, brief, bg=None: D.save(name, "", body, brief)
    for fa, en in PACK_TEXTS:
        T(fa, en)
    game_pairs()
    game_odd()
    game_next()
    game_shadows()
    game_order()
    game_sorter()
    game_riddles()
    game_grids()
    game_stories()
    items = sum(len(rows) for _, rows in SHEETS.values())
    rounds = sum(len({r["round"] for r in rows}) for _, rows in SHEETS.values())
    print(f"{len(SHEETS)} sheets, {rounds} rounds, {items} rows, {len(D.briefs)} pictures "
          f"({len(D.written)} written now), {len(I18N)} texts")
    if D.skipped:
        print("NOT overwritten (not made by this script):", ", ".join(D.skipped))
    if "--sheets" in sys.argv and not check:
        for name, (cols, rows) in SHEETS.items():
            with (HERE / name).open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
                w.writeheader()
                for row in rows:
                    w.writerow({c: row.get(c, "") for c in cols})
        (HERE / "pictures.txt").write_text(
            "# The pictures drawn for this pack, by make_puzzles.py. name: what it shows\n"
            + "".join(f"{n}: {b}\n" for n, b in sorted(D.briefs.items())), "utf-8")
        with (D.ROOT / "content" / "i18n" / "puzzles.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["fa", "en"])
            for fa, en in I18N.items():
                w.writerow([fa, en])
        print("sheets, pictures.txt and i18n/puzzles.csv written")


if __name__ == "__main__":
    main()

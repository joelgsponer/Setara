# Logic puzzles (`math-2-puzzles`): what it is and what a reviewer must decide

An optional add-on pack for the Workshop, shown beside level 2. It is not
arithmetic practice. It is thinking: finding a rule, leaving out what does
not fit, putting clues together. It needs no new code; every game runs in one
of the existing engines.

**Nobody has reviewed this pack.** It was written and drawn by an AI (Claude).
The Dari has not been read by a Dari speaker, the speech has not been heard,
and no child has tried a single puzzle. The builder and the app were run; the
list of what was checked is at the end.

## What is in it

9 games, 43 rounds, 285 puzzles (plus 42 story pages that only tell). The
games go from easy to hard, and so do the rounds inside each game. Ages are
my guess.

| | Game | Engine | Rounds | What the child does | Age |
| --- | --- | --- | --- | --- | --- |
| a | They Belong Together | pairs | 3 | Memory with a thought: key and lock, hen and egg; round 3 pairs a thing with its shadow | 6+ |
| b | Odd One Out | story | 5 | Four cards, one does not belong: by kind (1, 2), by shape, colour or size (3), by what a thing does (4), numbers (5) | 6 to 12 |
| c | What Comes Next? | story | 8 | A row with one empty place: two things in turn (1), longer repeats (2, 3), growing and shrinking (4), number rows (5, 6), two rules at once and steps that change (7, 8) | 6 to 14 |
| d | Shadows and Mirrors | listen_pick | 4 | Find a thing's shadow (1), find whose shadow it is among animals that look alike (2), find the turned figure among mirrored ones (3), find the mirror picture (4) | 6 to 14 |
| e | In the Right Order | builder | 5 | By size (1), by what happens first (2), from spoken clues with three things (3), four things (4), with "is not" clues and a picture that is not in the row (5) | 6 to 14 |
| f | Both or Neither | sorter | 5 | Legs: two, four, none (1); red / round / both (2); blue / triangle / both / neither (3); even / more than ten / both / neither (4); big / yellow / both / neither (5) | 7 to 12 |
| g | Riddles | journey | 4 | Spoken riddles with a picture answer (1, 2), "think twice" questions with a number answer (3), putting statements together (4) | 7 to 14 |
| h | Squares and Shapes | story | 4 | A grid where each colour or picture stands once in every row and column (1, 2), counting the triangles and squares hidden in a figure (3, 4) | 8 to 14 |
| i | Thinking Stories | story | 5 | The farmer, the fox, the hen and the wheat (1); thinking with a balance (2); who has which animal, who has which fruit (3); who won the race, who lives in which house (4); the shortest way, and sharing one bread fairly (5) | 9 to 14 |

Everything is spoken. Written words appear as answers only in Riddles (the
weekday question, and "wool / stone / both the same"); that game has
`read_choices`, so each written card is read aloud. Number cards are read by
the child: that is the reading of numerals that Math 2 teaches.

## Decisions I took

**The story engine carries the picture puzzles.** Listen and Pick shows the
question's picture in a card of 128 pixels (1.4 cm on the device) and it
chooses by itself how many of the wrong cards to show, two to four. Both are
wrong for these puzzles. A row of seven things cannot be read at 1.4 cm, and
"which of these four does not belong" needs all four on the screen. A story
page draws its picture 357 pixels wide (4 cm) and always shows every choice.
So Odd One Out, What Comes Next?, Squares and Shapes are "stories" in which
every page is a question. Consequences:

- After a wrong choice the guide says `wrong_say_fa`. There is one sentence
  per question, not one per wrong card. It names the rule ("three are
  birds") and lets the child try again; it does not name the answer.
- After a right choice nothing is explained; the next question comes.
- Y does not explain in a story (the engine repeats the page slowly).
- Odd One Out has no picture above the four cards, so the engine draws its
  large speaker there. It works; it is plain.
- Stars in a story count wrong choices against the number of questions.

**A row longer than five runs on in a second line**, like writing: the second
line starts on the same side as the first, and a grey arrow under each line
shows the direction. Picture rows run from right to left, number rows from
left to right. This follows the other packs (Dari tiles are placed from the
right, number tiles from the left). The answer never depends on the
direction: the empty place is one fixed place in the row.

**Listen and Pick and Journey fill up to four choices by themselves** from
the other answers of the round when a row lists fewer than three wrong
choices. In a riddle that could put a second defensible answer on the screen,
so every row in `riddles.csv` and `shadows_mirrors.csv` lists three wrong
choices itself. Keep it so when editing.

**Checked by machine** (`python3 make_puzzles.py --check`): the empty square
of every grid can take one value only (all completions are tried); every
order in rounds 3 to 5 of In the Right Order follows from its clues in
exactly one way (all orders are tried); the triangles and squares of every
figure are counted by brute force from the lines; every turned figure is
truly different from its mirror picture; no question lists its answer among
the wrong choices.

**Checked by me only, by thinking** (a person should check again): that an
odd-one-out has no second reason that singles out another card; that no wrong
card of a riddle also fits; that the number rows have one rule a child would
accept.

**Pictures.** 241 new pictures, all drawn by rule in `make_puzzles.py` and
its two helper files, so that a series is alike and only the meaningful
difference changes: 112 single things (`puz_*`: coloured shapes, towers,
dots, arrows, six figures of squares in six positions each, 20 shadows,
children in other colours, houses, bread) and 129 scenes (`scene_puz_*`: 57
rows, 14 grids, 12 figures, 7 river pictures, 7 balances, 28 pictures for the
who-has-what stories, 2 ways, 2 of the bread). Library pictures
(apple, cat, the girl, the boy, the father as the farmer) are copied into the
new files; nothing refers to another file. Shadows are the library drawing in
one dark colour. The children of the stories are the library's girl and boy
with other colours of headscarf, dress and shirt. `pictures.txt` says what
each picture shows. No picture has letters; numerals are the outlines of the
app's own Latin font (Andika), as on the number cards.

**The sheets are the source.** `make_puzzles.py` wrote the first version of
the nine sheets and of `content/i18n/puzzles.csv`, because a puzzle and its
picture have to agree. From now on edit the sheets, as in every other pack.
Run the script without options after changing a drawing rule (it replaces
only pictures it made itself, marked by a comment inside the file). Run it
with `--sheets` only when the puzzles themselves change: it overwrites the
sheets and the i18n file and would undo a reviewer's wording.

**Girls and boys.** Stories: Laila, Maryam, Shirin, Zahra, Narges (girls);
Yusuf, Omar, Karim, Farid (boys). In the bread story the boy cuts and the
girl chooses; in the race a girl is first and a girl is last. The farmer is
a man (the library's "father"); a father and a carpenter appear in riddles,
a mother gives the fair-sharing rule.

## Puzzle types I dropped, and why

- **Which piece completes the picture** (a carpet with a hole). The Latin
  grid does the same job with one clear rule; a free picture with a hole
  needs four hand-drawn pieces per puzzle that differ only slightly, and at
  1.4 cm they do not.
- **Pouring water with two jugs, the bridge and the lantern, nine balls on
  the balance.** Each needs the child to hold a long plan while only hearing
  it. Without reading and without moving things on the screen it becomes a
  memory test. The balance round stops at "which of three balls is heavy".
- **Riddles that live on a word.** "It has an eye but cannot see" (needle),
  "it has hands but cannot clap" (clock), "it has a head and a tail" (coin),
  "leaves but no tree" (book) work in English or Iranian Persian; I could
  not be sure of the Afghan Dari word in each. Kept: only riddles where the
  Dari word is plain (legs of a chair, teeth of a comb) or no word-play is
  needed.
- **Riddles whose answer has no picture** (shadow, name, echo, tomorrow) and
  the mushroom and snail riddles (no library picture; "one leg and a hat"
  also fits the umbrella).
- **Trick questions with a debated answer** ("ten sparrows sat on a wall, a
  stone hit one, how many are left?").
- **Truth-teller and liar puzzles.** The frame is "one of these children is
  lying"; I did not want that in a classroom pack.
- **Odd one out by the colour of real things** (three red things and a
  lemon): every set I tried had a second reading (the ball is not food, the
  tomato is not a fruit). Colour is asked with plain shapes instead.
- **Pentagram and six-pointed star for counting triangles**: they are
  symbols; the figures are a triangle, a square and a plain house.
- **Catch, Market, Say It**: no puzzle fits them without bending them.

## What a human reviewer must decide

For the Dari-speaking educator:

1. **Every sentence.** The Dari is mine. Words I am least sure of: «نشانی»
   for a clue; «چیستان» for a riddle; «تیر» for an arrow; «خانه» for a square
   of a grid and «ستون» for a column, «قطار» for a row; «توته» for a piece;
   «هم‌وزن»; «بوجی گندم» for a sack of wheat; «کم از کم»; «بی پا»; «حشره»;
   «رقم» for a digit; «می‌برآید». River is «دریا» and boat «کشتی», as in the
   other packs.
2. **Are these riddles known, or at least natural, in Dari?** They are
   common riddles retold plainly, not taken from a Dari collection. A
   teacher will know better ones; replace freely, but keep three wrong
   pictures per row and make sure none of them also fits.
3. **Direction of the rows.** Picture rows run right to left, number rows
   left to right, and long rows continue in a second line. Is that how a
   pattern is shown in the school books?
4. **Odd one out, set by set.** Sets where I see a possible objection:
   table, chair, bed / tree ("made by a carpenter" is the stated reason);
   fox, wolf, elephant / goat (wild and tame; the elephant is also the only
   one not found in Afghanistan); eagle, pigeon, parrot / butterfly;
   bee, ant, fly / mouse ("insect" and "six legs" must be known);
   numbers 15, 25, 35 / 30 and 41, 43, 47 / 52.
5. **"Think twice" (Riddles round 3)** uses a metre, a kilo, and a family
   riddle (two fathers and two sons are three people). The ant on the wall
   reaches the top on day 2, not 3; the sock question needs "at least" to be
   understood. Right level for 10 to 14? Too much to hold by ear?
6. **Clue rounds of In the Right Order (3 to 5).** The whole puzzle is
   spoken: up to four short clues. X repeats slowly, Y gives the solution
   path. A wrong tile only shakes, so a child can also finish by trying.
   Is that acceptable, or should round 5 go?
7. **The fair-sharing story** has the mother give the rule "one cuts, the
   other chooses". Fine as told?
8. **Names** of the nine children: common first names, no real person meant.

For whoever tries it with children:

9. Shadows of goat, sheep, cow, horse, donkey, camel, dog: tell them apart
   at device size? (On the PC screenshots they can be.)
10. Mirror round: the figure beside the mirror is small (about 6 mm).
11. The two-balance pictures and the 4 by 4 grids are the densest scenes.
12. Thinking Stories round 3 has 20 pages and round 4 has 15: perhaps too
    long for one sitting; each could be split into two rounds.
13. Do six-year-olds understand the empty yellow place without being shown?
    There is no worked example page; only the spoken instruction.

For the project:

14. `docs/games.md`, `docs/content-overview.md` and `docs/review-notes.md`
    do not mention this pack yet (I was asked not to touch docs).
15. The warm-up before a round of this pack draws on its own Shadows and
    Riddles questions once those rounds have stars, and otherwise on Math 1.
    "Find my level" uses only the main Math 2 pack, so the puzzles do not
    move a class's math level.

## What was run

- `python3 make_puzzles.py --check`: all machine checks pass.
- `validate --only math-2-puzzles`: ok, 0 warnings; `--untranslated`: no
  line of this pack is missing its English.
- A silent build of `core` and `math-2-puzzles` into a scratch folder: ok.
- `tools/shoot.sh` with a script that opens 34 rounds across all nine games,
  answers right and wrong, and takes 95 screenshots; I looked at all of
  them. `tests/fuzz_rounds.lua` on the scratch build: all 43 rounds open and
  survive random presses, with one and with two players.
- Every new picture was looked at on contact sheets, and the dense scenes
  again at device size.

Not done: nothing was heard (the build was silent), nothing was run on a
handheld, the piper build and `setara/packs/` were not touched.

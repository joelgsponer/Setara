# The games

Setara has ten game engines. An engine is one mechanic, written once in
`app/engines/<id>.lua` and reused in every subject with different content. A
"game" is an engine plus a sheet of content, listed in a pack's `pack.json`.

This page describes each engine as the code has it, then the rules they
share. The item data of each engine is in [level-format.md](level-format.md);
the sheets an author writes are in [authoring.md](authoring.md).

The lists of games were taken from the `pack.json` files on 14 November 2026.
The numbers in brackets are rounds. The first-aid pack (`garden-3`) was still
being changed on that day.

Buttons are named as on the handheld. On a PC: arrows, Z = A, X = B, A = X,
S = Y, Enter = Start.

Buttons that work the same in every game, unless a section says otherwise:

| Button | Does |
| --- | --- |
| X | Say it again, slowly |
| Y | Explain in Dari (where the item has a Dari help text; otherwise the same as X) |
| B | Leave the round, back to the place |
| Start | Pause |

## 1. Listen and Pick (`listen_pick`)

**What the child does.** Hears a word or a question and picks the right card.
Two to four cards sit up, left, right and down of the centre. The centre shows
a speaker, or a picture that belongs to the question (for example five sheep
to count).

**Buttons.** One press of the D-pad in the direction of a card answers. A
says the question again.

**Right and wrong.** Right: the card turns green and grows, the next question
comes. Wrong: the card shakes and is greyed out, the question is said again,
and the child tries the other cards. The question then comes back once later
in the round.

**Read-aloud choices.** Where the cards are written Dari words and the game
has `"read_choices": true`, each card is read aloud after the question and
lit while it is read.

**Pair mode.** With two players chosen, a Listen and Pick round is played as
a Duel (section 9).

**Item data.** `prompt_audio`, `choices`, `answer`, optional `show`,
`help_audio`, `tags`.

**Used by.**

| Pack | Games |
| --- | --- |
| `en-1` | Word Stall (18), Number Stall (5) |
| `en-2` | Word Stall (20), Number Stall (5) |
| `fa-1`, `fa-2` | Alefba Garden (14 each) |
| `math-1` | Count the Flock (12), Shape Mason (4) |
| `math-2` | Count the Flock (10), Shape Mason (4) |
| `math-3` | Count the Flock (8), Shape Mason (4) |
| `garden-1` | My Body (5) |
| `garden-2` | Healthy Home (3) |
| `garden-3` | Danger Signs (4) |
| `garden-4-rights` | Which Right Is It? (3) |
| `garden-4-world` | The Seven Continents (3, choices read aloud) |

The warm-up and "find my level" also run in this engine.

## 2. Pairs (`pairs`)

**What the child does.** A memory game. Three to six pairs lie face down. A
pair can be a speaker card and a picture, a sum and its answer, a word and a
picture. Every card says its pair's audio when it is turned.

**Buttons.** The D-pad moves the gold border. A turns a card. X and Y say the
last heard audio again, slowly.

**Right and wrong.** Two cards of the same pair stay open and sparkle. Two
others turn back after about a second (A turns them back sooner). Nothing is
taken away.

**Stars.** By the number of tries: at most twice the number of pairs gives
three stars, at most three times gives two, more gives one.

**Pair mode.** The children take turns. A match gives another go. Each
child's pairs are shown as stars under their number.

**Item data.** `a`, `b`, `audio`.

**Used by.**

| Pack | Games |
| --- | --- |
| `fa-1`, `fa-2` | Verse Corner (4 each) |
| `garden-4-rights` | Rights Pairs (2) |
| `garden-4-world` | World Pairs (2) |

## 3. Catch (`catch`)

**What the child does.** Hears a rule ("catch the healthy food", "catch the
letter b"). Things drift slowly down three lanes, one at a time. The child
moves a basket under the things that fit the rule.

**Buttons.** Left and right move the basket between the three lanes. A
during the spoken rule starts at once.

**Right and wrong.** A thing that fits fills one of the dots at the bottom. A
thing that does not fit bounces off the basket; that counts as a wrong try.
Letting a thing fall past is never counted. When all dots are full (1 to 10,
set by `need`) the next rule is spoken. Nothing falls while a new rule is
being spoken. About half the things fit the rule, and never more than two in
a row do not.

**Pace.** The fall takes 4 seconds from top to basket, 5.5 seconds after
mistakes and 3.2 seconds after a run of right answers.

**Pair mode.** The turn passes after each rule.

**Item data.** `prompt_audio`, `targets`, `others`, `need`, optional
`help_audio`.

**Used by.**

| Pack | Games |
| --- | --- |
| `en-1`, `en-2` | Sound Catcher (6 each) |
| `fa-1`, `fa-2` | Syllable Catch (4 each) |

## 4. Builder (`builder`)

**What the child does.** Puts tiles in the right order: the letters of a
word, the words of a sentence, the steps of handwashing, numbers in a row.
The top row has one empty place per tile; Dari answers fill from the right.
The tray below holds the tiles, shuffled, sometimes with tiles that do not
belong. At most eight tiles.

**Buttons.** The D-pad moves the gold cursor over the tray. A puts the chosen
tile into the next empty place.

**Right and wrong.** A tile that belongs next flies to its place. A wrong
tile shakes and stays in the tray. When the row is full, the answer is spoken
(`done_audio`) and the next item comes.

**Pair mode.** The turn passes after each item.

**Item data.** `prompt_audio`, `tiles`, `extra`, `rtl`, `done_audio`,
optional `help_audio`.

**Used by.**

| Pack | Games |
| --- | --- |
| `en-1`, `en-2` | Sentence Train (10 each) |
| `fa-1`, `fa-2` | Word Weaver (6 each) |
| `math-1`, `math-2`, `math-3` | Carpet Weaver (6 each) |
| `garden-1` | Clean Hands (4) |
| `garden-2` | Clean Hands (3) |
| `garden-3` | First Steps (6) |
| `garden-4-world` | Large and Small (2) |

## 5. Say It (`say_it`)

**What the child does.** Speaking practice without a microphone (the
handheld has none). Four steps per phrase:

1. Listen: the device says the phrase. A picture and the text are shown.
2. Your turn: the guide invites the child to say it aloud while a bar fills.
3. Compare: the device says it again.
4. Judge: the child decides.

**Buttons.** A during steps 1 to 3 skips ahead. In step 4, A means "I said it
well" and X means "once more" (back to step 1). Y gives the Dari meaning and
then the phrase again.

**Right and wrong.** There is no wrong. "Once more" only means the phrase
does not count as right at the first try.

**Pair mode.** The turn passes after each phrase, so the partner can judge.
The app does not check who presses.

**Item data.** `prompt_audio`, `text` or `fa`, optional `show`, `help_audio`.

**Used by.**

| Pack | Games |
| --- | --- |
| `en-1`, `en-2` | Echo (20 each) |

## 6. Story (`story`)

**What the child does.** Listens to an illustrated story, page by page. A
caption can be shown and is lit while it is spoken (Read Along). Some pages
are decisions with two or more picture cards.

**Buttons.** A turns the page; A during speech stops the speech first. Left
goes back one page. On a decision, left and right move the gold border and A
chooses. X and Y both say the page again, slowly.

**Right and wrong.** The right choice continues the story. A wrong choice
shows what happens (`wrong_img`), explains (`wrong_audio`), and asks again
with that card dimmed.

**Stars.** No wrong choice gives three stars. Wrong choices up to half the
number of decisions (rounded up) give two. More gives one. A story without
decisions gives three.

**Pair mode.** The turn passes after each decision.

**Item data.** One item per page: `audio`, `img`, `text` or `fa`; for a
decision also `choices`, `answer`, `wrong_audio`, `wrong_img`.

**Used by.**

| Pack | Games |
| --- | --- |
| `en-1`, `en-2` | Radio Stories (2 each) |
| `fa-1`, `fa-2` | Read Along (2 each) |
| `garden-1` | Omid's Day (1) |
| `garden-2` | Shirin and the Safe Water (1), Little Nurse (1) |
| `garden-3` | Nazanin and the Hot Tea (1), Jawad and the Rusty Nail (1), When Someone at Home Is Ill (2), When Someone Has Collapsed (2), Poison (2) |
| `garden-4-rights` | Two Stories: The New Girl, and Tired Yusuf (2), Tell an Adult You Trust (1), Class Talk: The Rights of Every Child (1) |
| `garden-4-world` | From the Whole World to Basel (3) |

Teacher mode's Story Time lists every story round of the Dari, English and
Garden places, to play to the whole class.

## 7. Journey (`journey`)

**What the child does.** Answers Listen and Pick questions to cross a stream.
Stepping stones run along the bottom of the screen. The guide bird hops one
stone forward for each question solved and stands on the far bank at the end.

**Buttons.** As in Listen and Pick: the D-pad answers, A says the question
again.

**The number line.** A sum with a `hop` value (`3+2`, `7-3`, all numbers
within 0 to 20) is shown on a number line after the right answer: the bird
starts at the first number and makes the hops one by one, so the child sees
why the answer is right. A skips it.

**Right and wrong, pair mode.** As in Listen and Pick, but the round stays a
Journey in pair mode and the turn passes after each question. Read-aloud
choices work here too.

**Item data.** As Listen and Pick, plus optional `hop`.

**Used by.**

| Pack | Games |
| --- | --- |
| `math-1`, `math-2`, `math-3` | Number Hop (12 each) |
| `garden-1`, `garden-2` | Tree Keeper (4 each) |
| `garden-4-world` | The Long Journey (3, choices read aloud) |

## 8. Market (`market`)

**What the child does.** Serves a customer at a stall. Two modes:

- **count**: the customer asks for some goods ("Three apples, please"). The
  child puts that many on the tray. The goods lie in rows of five.
- **pay**: the child pays an amount with coins and notes. The purse holds one
  of each value (up to six values).

**Buttons.**

| Button | count | pay |
| --- | --- | --- |
| Up | One more on the tray | Put one of the chosen coin or note on the counter |
| Down | Take one away | Take one of it back |
| Left, right | | Choose a coin or note |
| A | Done | Done |

A with nothing placed only says the request again. In pay mode the total is
shown as a number only after A.

**Right and wrong.** The right amount moves on. A wrong amount makes the
person at the stall shake the head; the counter is cleared and the request
is said again. A full tray only shakes a little.

**Pair mode.** The turn passes after each customer.

**Item data.** `prompt_audio`, `mode`, `target`, `units`, `goods`, optional
`help_audio`.

**Used by.**

| Pack | Games |
| --- | --- |
| `en-1`, `en-2` | Shopkeeper (4 each) |
| `math-1`, `math-2`, `math-3` | Market Scales (6 each) |

## 9. Duel (`duel`)

**What the children do.** Two players, one device. The question is a Listen
and Pick question with up to four cards. The fastest right answer wins the
point. Before the first question a picture shows who uses which buttons.

**Buttons.**

| Card | Player 1 | Player 2 |
| --- | --- | --- |
| Upper | D-pad up | X |
| Lower | D-pad down | B |
| Left | D-pad left | Y |
| Right | D-pad right | A |

All face buttons are answer buttons here. So X and Y do not repeat or
explain, and B does not leave the round: use Start, then "home". The question
is repeated by itself after six seconds of silence.

**Right and wrong.** A right answer gives that player a point and the card
flashes in their colour. A wrong answer locks that player out of this
question only. If both are out, the right card is shown and the question
comes back once later.

**Stars.** Shared. They count how many questions were answered right by
either player the first time they came up. The points are shown during the
round; no winner is announced at the end.

**In the current code** written choices are not read aloud in a Duel, even
where the game has `read_choices`.

**Item data.** As Listen and Pick.

**Used by.** No `pack.json` names `duel` as a game's engine. Every
`listen_pick` game becomes a Duel when two players are chosen on the place
screen.

## 10. Sorter (`sorter`)

**What the child does.** Drops each thing into the right basket. Two to four
baskets sit left, right, up and down of the centre. The thing to sort lies on
a card in the middle.

**Buttons.** One press of the D-pad drops the thing into the basket on that
side. A says the thing's audio again. Y says all the baskets again.

**Spoken baskets.** Many children cannot read the labels. So the round starts
by saying every basket in turn while it pulses. A skips that.

**Right and wrong.** Right: the basket bounces and says its name. Wrong: the
thing slides back and that basket is dimmed for this thing.

**Pair mode.** The turn passes after each thing.

**Item data.** Round: `baskets`. Item: `thing`, `basket`, `prompt_audio`.

**Used by.**

| Pack | Games |
| --- | --- |
| `fa-1` | Letter Shapes (8) |
| `fa-2` | Letter Shapes (12) |
| `math-1`, `math-2`, `math-3` | Share the Bread (4 each) |
| `garden-1` | Clean or Dirty (4), Garden Baskets (4) |
| `garden-2` | Safe Water (4), Good Plate (4) |
| `garden-3` | Do It, Don't Do It (7) |
| `garden-4-rights` | What Every Child Needs (4) |
| `garden-4-world` | Two Countries (3) |

## The shared rules

These hold in every game. Most of them live in `app/core/quiz.lua` and
`app/scenes/play.lua`.

### Everything is spoken

Every round starts with a spoken Dari instruction from the guide bird. Every
question, word and basket has audio. No game needs the child to read, except
where reading is the exercise. The builder refuses a question without speech.

### The warm-up five

Before a round, up to five quick review questions from rounds the class has
already played, in this level or the level below. A small sun in the corner
marks it. It does not count for stars or for the counts. It is left out when
there is not enough to review, and in Story Time. Details in
[architecture.md](architecture.md#the-life-of-a-round).

### Wrong answers come back

A wrong answer is never punished. There are no lives, no game over and no
timer that punishes. An item that needed more than one try is put at the end
of the round's queue and comes back once.

### Adaptive pace

Three first-try right answers in a row make the round a little harder. Two
wrong tries make it a little easier. In the choice games this is the number
of cards (two to four; a round starts with three). In Catch it is the fall
speed.

### Stars

Every finished round gives one to three stars. In most games:

| First-try right answers | Stars |
| --- | --- |
| 85 % or more | 3 |
| 50 % or more | 2 |
| Less | 1 |

Pairs and Story count differently (see their sections). The best result of a
round is kept and never lowered. Stars are per device, not per child. They
make the place on the home screen grow: at 20 %, 50 % and 80 % of a
subject's stars its picture gets richer.

The place screen always offers the first round of a game that does not have
three stars yet. Every level is open from the start; nothing is locked.

### X = slowly, Y = Dari help

X says the question again from the slow recording. Y plays the Dari
explanation of the item where the sheet has one (`help_fa`); where it has
none, Y does the same as X. Exceptions: Duel (both are answer buttons), Say
It (X in the last step means "once more"), Sorter (Y says the baskets), Pairs
and Story (both repeat slowly).

### One or two players

The place screen has a switch for one or two players. With two, the top bar
shows whose turn it is and the turn passes as described per game. Listen and
Pick becomes a Duel. Nothing is stored about either child.

### Pass the device on

After ten minutes of play the result screen says, once, that it is time to
pass the device on, and shows two children. The count then starts again.

### Read-aloud choices

In Listen and Pick and Journey games marked `read_choices`, written Dari
choices are read aloud in the order up, left, right, down, each lit while it
is read. Currently two games use it, both in `garden-4-world`.

### Find my level

The magnifying glass on the place screen starts a short placement game: four
questions per level with up to four cards each. Three right at the first try move
on to the next level. The app then suggests a level. Only the suggested level
is remembered, for the device.

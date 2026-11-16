# English 3 "My day": what it teaches, what was decided, what a human must check

Written by an AI (Claude). Nobody who speaks Dari, teaches English or knows
the villages has read or heard any of it yet. The unit-by-unit word list is
in [`syllabus.md`](syllabus.md); the briefs of the new pictures are in
[`pictures.txt`](pictures.txt).

## Version 2: more variety (read this first)

Version 2 answers one complaint: the same questions came back. Everything
below this section describes version 1 unless it says otherwise; this section
says what changed. Still nobody who speaks Dari or teaches English has read
or heard it.

**Size**: 15 games, 104 rounds, 1006 items (version 1: 11 games, 86 rounds,
617 items). How it was counted: a script reads `items.csv` and every sheet and counts each spoken prompt (`say_fa` + `say_en`, for derived games the word itself) over the whole pack; "more than twice" counts the items whose prompt occurs three times or more.

| Game | Rounds v1 → v2 | Items v1 → v2 | Draw | Prompts heard more than twice, v1 → v2 |
| --- | --- | --- | --- | --- |
| word_stall | 20 → 24 | 100 → 118 | - | 49 → 0 |
| echo | 20 → 24 | 200 → 237 | - | 61 → 0 |
| sound_catcher | 6 → 6 | 19 → 27 | - | 0 → 0 |
| sentence_train | 11 → 12 | 67 → 142 | 8 | 23 → 0 |
| shopkeeper | 4 → 4 | 24 → 48 | 8 | 0 → 0 |
| radio_stories | 3 → 4 | 27 → 35 | - | 0 → 0 |
| number_stall | 4 → 4 | 34 → 58 | 8 | 7 → 0 |
| day_journey | 4 → 4 | 40 → 60 | 8 | 5 → 0 |
| memory | 5 → 5 | 30 → 59 | 6 | 15 → 0 |
| baskets | 6 → 6 | 51 → 84 | 8 | 19 → 0 |
| yes_no | 3 → 3 | 25 → 40 | 8 | 0 → 0 |
| riddles | - → 3 | - → 41 | 8 | - → 0 |
| day_in_order | - → 2 | - → 21 | - | - → 0 |
| odd_one_out | - → 2 | - → 24 | 8 | - → 0 |
| opposites | - → 1 | - → 12 | 6 | - → 0 |

Whole pack: 179 of 617 items had a prompt that is heard more than twice;
now 0 of 1006.

What was done:

- **Pools.** Seven sheet games are now pools (`"draw"`): a round holds 12 to
  16 items and each play asks eight (pairs: six of about twelve). Sound
  Catcher, the stories and the two new builder games are not pools.
- **No word a third time.** Word Stall and Echo both say every word of the
  word bank, so a third bare "hat" in a sheet was the main repetition. Review
  rows outside the review units 10 and 20 were replaced by new words; in the
  review units the word comes back inside a new sentence ("I play with my
  kite."). Sheets that only repeated the word now say something else (Memory
  says "a cat", Baskets says "my shirt").
- **35 new words** (the reviewer of version 1 asked for 30 to 50): toothbrush,
  toothpaste, dirty (unit 01b); rain, snow, ice, wind (12b); spring, summer,
  autumn, winter, season (12c); toilet, chimney, fence, pump (16b); wheel,
  knife, noon, watch, clinic, run (in place of review rows); behind, in front
  of (17); map, pan, log, ant, fan (18) and net, web, pin, lid, bug, rug (19)
  as new three-letter words to read. The words known by ear (cat, hat, dog
  ...) are still read in Sound Catcher, Sentence Train, Memory and Baskets.
- **Four new games**: Riddles (two short sentences, pick the picture; 41),
  First, Then (hear two to four things, put their pictures in that order;
  21), Odd One Out (24) and Opposites (picture pairs; 12). A fourth story
  ("Snow!", round 12c) uses the weather and season words.
- **Number Stall 04b** asks tens and teens inside sentences ("My brother is
  thirteen."), and Memory 05 pairs mirror numbers (47 / 74).
- **The day names** are no longer four long tiles in a row. Sentence Train
  has a new round 09b in which each day is built from its parts (Wed + nes +
  day), every tile at 24 px or more; the order of the days is asked in Day
  Journey ("Which day comes after Monday?", Dari choices read aloud) and in
  First, Then. Other long tiles were widened by joining small words ("in the"
  is one tile). One tile is still drawn at 20 px: "homework".
- **Towel** is now «روی‌پاک». «دستمال» is "handkerchief" in the shared English
  table (the math pack uses it so); with its own Dari word the English mode
  shows "towel" again and the other packs are untouched. **A Dari speaker must
  confirm «روی‌پاک».**
- **Pictures**: 11 new ones (bug, fan, lid, log, map, net, pan, pin, web,
  pos_behind, pos_in_front; briefs in `pictures.txt`). `wind` was drawn by
  another writer at the same time and is reused.

Decisions and doubts of version 2:

- **Yes or No still has only two answers** (21 yes, 19 no in the pools). The
  rule "no answer right more than about three times a game" cannot hold for
  it; a play now draws eight of 12 to 15 questions, so the questions change.
- **Odd One Out never counts the cards** ("Which one is not for your feet?"),
  because the app shows two, three or four cards depending on how the child
  is doing.
- New Dari words to confirm: برس دندان، کریم دندان، چتل، باد، یخ، فصل، تشناب،
  دودکش، کتاره (fence)، بمبه (pump)، چرخ (wheel; or ارابه?)، کارد، چاشت
  (noon)، ساعت دستی، کلینیک، پشت، پیش روی (in front of)، نقشه، تابه (pan; or
  کرایی?)، کنده چوب (log)، مورچه، پکه (fan)، جال (net)، تار جولا (web)، سنجاق،
  سرپوش، حشره (bug)، قالینچه (rug).
- "bug" is drawn as a ladybird, "lid" as a dome lid, "pan" with an egg in
  it, "net" as a hand net, "map" without any letters. "rug" reuses the
  picture `carpet` (level 2 calls it carpet).
- `pos_behind` and `pos_in_front` show the ball half hidden behind the box
  and overlapping it in front; try them with children beside `pos_next_to`.
- The riddles use a few words that are only explained by the Dari help:
  "round", "around", "over", "tells stories", "holds". An English teacher
  should read all 41.
- "It rains", "It snows" are taught as fixed sentences (present simple, as
  the level asks), not "It is raining".
- Checked for version 2: `validate --only en-3` ok, 0 warnings, 0 Dari texts
  without English; silent build ok; `tests/fuzz_rounds.lua` on the scratch
  build ends "fuzz ok"; screenshots of the four new games, the new story,
  Sentence Train 09b and one pool round looked at. Not checked: audio, a
  real handheld, children.

## What the pack teaches

The curriculum line (spec section 8): *describe her day, tell the time, days
of the week, home and clothes, count to 100; present simple, do / does;
reading simple three-letter words.*

| Units | Content |
| --- | --- |
| 01-03 | The daily routine in the first person: get up, wash, brush my teeth, eat, drink, go to school, play, sleep; morning, afternoon, evening, night; hungry, thirsty, tired |
| 04-05 | Numbers 21 to 100, afghani; a few countable things |
| 06-07 | What time is it? It is ... o'clock. I get up at six o'clock. early, late |
| 08-09 | The seven days, today, tomorrow, week; On Friday I don't go to school; places and chores |
| 10 | Review, first story |
| 11-12 | Clothes; I wear, put on, take off; new, old, warm, cold |
| 13-14 | He / she with verb-s, we, they; Do you ...? Does she ...? Yes, she does. No, he doesn't; always, never; second story |
| 15-17 | Home: rooms and things; Where is ...? in, on, under, next to |
| 18-19 | Reading three-letter words (short a, o, then e, i, u) |
| 20 | Review, third story |

Size: 20 units, 11 games, 86 rounds, 617 items. Nine of the ten engines are
used (all but duel, which the app offers by itself for two players).

| Game | Engine | Rounds | What is new against level 2 |
| --- | --- | --- | --- |
| Word Stall | listen_pick | 20 | derived from `items.csv` |
| Echo | say_it | 20 | derived from `items.csv` |
| Sound Catcher | catch | 6 | middle letter, last letter, then whole three-letter words and word families |
| Sentence Train | builder | 11 | sentences; the days in order; rounds 18 and 19 build words from letters |
| Shopkeeper | market | 4 | the child is the customer and pays in afghani up to 100 |
| Radio Stories | story | 3 | three decisions each; the right choice is first in none of the nine |
| Number Stall | listen_pick | 4 | 21-100; tens against teens (thirty / thirteen); what comes next |
| Day Journey | journey | 4 | the time, the days (Dari choices, read aloud), whole sentences |
| Memory | pairs | 5 | spoken number or time to numeral or clock; written word to picture |
| Baskets | sorter | 6 | clean / dirty, morning / night, do / does, clothes / home / food, the middle vowel |
| Yes or No | listen_pick | 3 | a picture and a question: Is it seven o'clock? Does she cook? Is the ball on the table? |

## Decisions taken

- **Word count.** The spec asks for about 200 new words. The pack has about
  145 new word forms in real use (roughly 125 headwords), 34 more
  three-letter words that are only decoded in the reading games (bat, log,
  pin ...), and the numbers 21 to 100. I kept ten rows a unit, as levels 1
  and 2 do, so that an Echo round stays under four minutes, and did not pad
  the list with words that have nothing to do with the theme. A reviewer may
  want 30 to 50 more words; the library has unused pictures for them.
- **Only full hours.** The clock pictures exist for the twelve full hours.
  "Half past" is not taught.
- **The week runs Saturday to Friday**, and "I go to school from Saturday to
  Thursday", "On Friday I don't go to school".
- **The days have no pictures.** In Day Journey round 09 the child hears the
  English day and picks the Dari word; the game has `read_choices`, so every
  choice is read aloud. The Y help does not say the answer but where the day
  lies ("the day after Sunday").
- **Yes or No is its own game** because the builder fills every listen_pick
  question up to four choices from the game's other answers; in a game whose
  only answers are yes and no, the two stay alone on the screen.
- **Shopkeeper**: level 2 counted goods; level 3 pays. "How much is ...?"
  belongs to level 4 and is not used; the shopkeeper says "The hat is forty
  afghani." **The prices are practice numbers, not real prices.**
- **Reading** uses words the child already knows by ear (cat, hat, bag, dog,
  pot, box, pen, hen, bed, leg, sun, cup) plus fox and jug. Wrong words in
  Sound Catcher differ in one letter. I left out "god", "sin", "pig" and
  similar as wrong choices.
- **Dari "on"** is «بالای», because «روی» is also "face" in unit 01.
- **«او»** is both he and she. Where one Dari help sentence serves two
  English sentences, `i18n/english3.csv` says "he (or she)".
- **Nine** is written «نُه», as the review notes ask.
- **Names**: Mina (girl, 9) and Hamid (boy, 11) are invented. Two stories
  are told by the girl and one by the boy; the questions in the boy's story
  are asked by the woman's voice and in the third story by the man's voice.
- **Who does what.** A woman cooks and a man digs the field, a girl carries
  water and a boy sweeps the yard. The boy's story has him fetch water and
  help both parents. No sentence says that a boy or man does not cook or
  clean.
- **Pictures**: 28 new ones (22 things, 6 story scenes). `lamp` was drawn
  by another pack at the same time and is reused. Six further story pages
  reuse scenes of the health and Dari packs that show the same girl (blue
  scarf, purple dress) and the same boy (green shirt, white cap).

## What was checked, and how

- `validate --only en-3`: ok, 0 warnings, 0 Dari texts without English.
- Silent build of `core` and `en-3` into a scratch folder: ok.
- `tests/fuzz_rounds.lua` against that build under xvfb: all 86 rounds open
  and survive random button presses (97 runs with the pair variants).
- Screenshots of 18 rounds, one or more per game, looked at.
- Every new picture looked at on a contact sheet at device size, the scenes
  also at full size.

Not checked: no audio was generated or heard (the build was silent), nothing
ran on a handheld, no child has played it.

## For the Dari-speaking educator

Words I chose and am not sure of:

- get up «از خواب خیستن» (می‌خیزم); go to bed «به خواب می‌روم»
- breakfast «نان صبح», lunch «نان چاشت», dinner «نان شب»; afternoon «بعد از
  چاشت», evening «شام»
- tired «مانده» (not «خسته»); hungry «گرسنه» (or «گشنه»?); late «ناوقت»,
  "I am late" «من ناوقت کرده‌ام»; early «زود» (or «وقت»?)
- o'clock: «ساعت هفت است», as the math packs say (or «هفت بجه»?)
- clothes «کالا»; shirt «پیراهن»; **dress «پیراهن زنانه»** (is there a better
  everyday word for a girl's dress?); trousers «تنبان»; scarf «چادر»; shoes
  «بوت»; sandals «چپلک»; socks «جراب»; coat «بالاپوش»; button «دکمه» (or
  «تکمه»?); "take off your shoes" «بوت‌هایت را بکش»
- kite «کاغذپران»; homework «کار خانگی»; notebook «کتابچه»; street «کوچه»;
  tap «نل»; firewood «هیزم»; bottle «بوتل»; umbrella «چتری»; glasses «عینک»
- room «اطاق» (the English packs write اطاق, the health packs اتاق: pick
  one); kitchen «آشپزخانه»; stove «دیگدان»; mirror «آیینه»; jug «کوزه»
- next to «پهلوی»; on «بالای»; "I can read" «من خوانده می‌توانم»
- week from Saturday; Friday called «روز آخر هفته» in a hint
- short answers: "Yes, I do" is rendered by repeating the verb («بلی،
  می‌روم»), because Dari has no "do"
- The hints for English vowel sounds compare a to the start of «انار», o to
  «آب», e to «امروز». For u and i there is no hint. Are these comparisons
  right for a Dari ear?

## For the English teacher

- Is "clean" for sweeping the yard (unit 13) and "clean / dirty" as
  adjectives (Baskets round 01) too much for one word?
- "always" and "never" come in one unit with do / does (14). Too much?
- Third person forms that change the stem are taught as whole words: goes,
  carries, does, doesn't.
- "Put on" and "take off" come as fixed commands, without explanation.
- Plural "The socks are fifteen afghani", "My shoes are new": "are" is used
  but never explained.
- The day rows of Sentence Train put four day names on tiles. "Wednesday"
  and "Saturday" are drawn at about 20 px, under the 24 px the spec wants
  for Latin text (level 2 has the same with "grandmother").
- Units 04, 05, 08, 09 and 14 have only three or four pictured words, so
  their Word Stall rounds are short (level 2 has the same in its number
  units).
- Sorter round 03 puts "I go to school" under morning. Where school is in
  the afternoon, drop the row.
- No teacher lessons exist for level 3 (`content/teacher/` has level 1
  only). The 20 units are numbered as lessons so that they can follow.

## For the local reviewer of pictures

- Every picture of a person: `drink`, `cook`, `work`, `carry`, `sweep`,
  `scarf` and the six scenes.
- `scarf` shows a girl in pale grey with only the headscarf in colour. Is
  that understood as "the scarf", and is a pale face acceptable?
- `dress` is a red dress with yellow bands and long sleeves. Right for the
  region?
- `morning` and `evening` differ by the colour of the sky, a rooster
  (morning) and stars and a lit window (evening). A sunrise and a sunset
  are easy to confuse; try it with children.
- In Word Stall unit 03, `night` (a house under the moon), `sleep` (a child
  asleep under the moon) and `dinner` (a meal by lamplight) all show night.
  I judged that "night" still points to the first; a child may not.
- `eating` (a woman eating) next to `breakfast` and `lunch` (the food alone)
  for the word "eat": same doubt.
- `pos_in` and `pos_next_to` use a box, `pos_on` and `pos_under` a table, so
  "in" can also be told by the box alone.
- In `scene_shoe_room` the shoe under the table is small.
- The mother in `scene_mother_bakes_bread` and the woman in `cook` wear
  the same colours; the father in `scene_boy_father_repair` and the man in
  `work` do not.
- `clock_10` stands for the word "clock" in unit 16.

## Left open

- (Fixed in version 2: towel is «روی‌پاک», see above.)
- The spec's "from English level 3, Garden and Workshop games can be
  replayed in English" is not part of this pack.

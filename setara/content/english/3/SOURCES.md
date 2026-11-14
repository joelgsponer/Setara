# English 3 "My day": what it teaches, what was decided, what a human must check

Written by an AI (Claude). Nobody who speaks Dari, teaches English or knows
the villages has read or heard any of it yet. The unit-by-unit word list is
in [`syllabus.md`](syllabus.md); the briefs of the new pictures are in
[`pictures.txt`](pictures.txt).

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

- English mode: a few Dari words of this pack get their English from other
  packs' tables (`دستمال` shows "handkerchief", here it means towel), since
  the table is shared and keyed by the Dari text.
- The spec's "from English level 3, Garden and Workshop games can be
  replayed in English" is not part of this pack.

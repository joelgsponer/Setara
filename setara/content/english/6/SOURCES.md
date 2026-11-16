# English 6 "The wider world": what it teaches, what was decided, what is open

**Nothing here has been reviewed by a person.** The pack was written by an AI
(Claude) from the curriculum in the product spec (section 8, level 6: "Talk
about jobs and plans, tell a short story, compare things, write a short
message; going to, comparatives, because"). Nobody has heard the audio and
it has not run on a handheld. The builder validated and built it, and every
round was opened once in the app by `tests/fuzz_rounds.lua` on a PC.

## What the pack teaches

20 units, one per classroom lesson. `syllabus.md` lists, unit by unit, the
words, the pattern, the can-do and the games in playing order; the teacher
guide is to be written from it.

| Units | Topic | Language |
| --- | --- | --- |
| 01-03 | Jobs, what people do, where and with what they work | What does he do? He is a farmer. A baker makes bread. Where does she work? She works in a clinic / with a saw |
| 04 | I want to be | What do you want to be? I want to be a teacher. When I grow up ... |
| 05-06 | Plans | I am going to visit my aunt. Are you going to come? Yes, I am. No, I'm not. She is not going to cook |
| 07 | Travel | by bus, by car, on foot; A ticket to Kabul, please |
| 08 | The world | country, city, sea, desert, island, forest, lake; There is / There are |
| 09, 11 | Comparing | bigger than, faster than; more expensive than; better, worse |
| 10 | Review | |
| 12-13 | Why? Because | I am afraid because it is dark. I want to be a doctor because I want to help sick people |
| 14-16 | Telling a story | One day, Then, Suddenly, Finally, In the end; said, asked, answered; clever, greedy, brave |
| 17-18 | A short message | Dear ..., How are you? ... See you soon. From ...; Please come; Thank you for ...; I am sorry, I can't come because ... |
| 19 | My future | I am going to study because I want to be an engineer |
| 20 | Review | |

### Every unit is a teaching sequence

As in level 5, the letters of the round ids are the order of teaching
inside a unit: PRESENT (`a` Word Stall, `b` Echo), UNDERSTAND (`c` Listen
In, the pattern explained in Dari on its first page), PRACTISE (three
different games out of `d` to `l`), USE (`m` Read and Decide), and REVIEW in
units 10 and 20 and by recycling (jobs come back with "want to be", "going
to" and "because"; comparatives in the tales).

Units 04, 05, 06, 10, 13, 15, 18, 19 and 20 have no Word Stall: they teach a
pattern or review. Units 10 and 20 have no Listen In.

Thirteen games, 129 rounds, 1162 rows:

| Game | Engine | Rounds | Pool | What it adds |
| --- | --- | --- | --- | --- |
| a Word Stall | listen_pick (items) | 11 | | hear the word, pick the picture |
| b Echo | say_it (items) | 20 | | say every word, sentence and dialogue |
| c Listen In | story | 18 | | dialogue or spoken tale, explained in Dari first, two questions |
| d Riddles | listen_pick | 7 | 12, asks 8 | jobs, tools, transport, places, feelings with a reason, tale animals, message things |
| e Yes or No? | listen_pick | 6 | 12, asks 8 | a short text and a question about it |
| f Which One? | listen_pick | 7 | 12, asks 8 | odd one out, "what is going to happen", the right reason, the right written word |
| g Question Road | journey | 11 | 12, asks 8 | question to answer; who wrote the message, who said it, which is more expensive |
| h Baskets | sorter | 5 | 12, asks 8 | farmer / builder, yesterday / tomorrow, "-er" / "more", start / middle / end of a story, invite / thank / sorry |
| i Sentence Train | builder | 14 | 9, asks 6 | build the sentence; in units 13, 17 and 18 the tiles are phrases and the child builds a whole message |
| j Catch It | catch | 4 | 6 rules, asks 4 | a spoken rule; in unit 20 the things are written words |
| k Shopkeeper | market | 1 | 11, asks 6 | count tickets, pay the fare |
| l Pairs | pairs | 5 | 9-10, shows 5 | job to picture, big / bigger, a reason and what it calls for |
| m Read and Decide | story | 20 | | reading texts over two to four pages, what and why |

Reading: 60 to 85 words over two or three pages in every unit, 90 words on
four pages in unit 20. Every text has at least one "why" question; from
unit 12 the text itself says "because".

**"Write a short message"**: the device has no keyboard. The child reads
messages (units 17, 18, 20), sorts message sentences (Baskets 18), chooses
what to write (Which One? 18) and builds whole messages from four to six
phrase tiles in Sentence Train 17 and 18 ("Dear Sara," / "How are you?" /
"I am fine." / "From Mina"), with one tile that does not belong.

## Repetition (counted by a script over the sheets)

- 894 different spoken questions and prompts: 778 are said once, 116 twice,
  none more than twice.
- No picture or word is the right answer more than three times in a game,
  except where the form of the game makes it so: Yes or No? (yes 38, no 34)
  and Baskets (the basket is the answer).
- Every question row has a `help_fa`; every sheet round has its own
  `intro_fa`, each with an English twin in `content/i18n/english6.csv`.

## Decisions taken

- **Size.** 129 rounds.
- **New words: fewer than the target.** The spec asks for about 300. The
  sheets hold about 235 word forms that do not occur in levels 1 to 5 (about
  170 dictionary words). **Open**, as in levels 4 and 5.
- **Comparatives only.** Superlatives are not taught. "the fastest" occurs
  twice inside a question (Which One? 10, Yes or No? 15) and should be
  explained by the teacher or reworded.
- **"going to" in Dari.** Dari has no separate near future in everyday
  speech; the meanings are given in the present («فردا به دیدن خاله‌ام
  می‌روم») and "It is going to rain" as «باران خواهد بارید».
- **Jobs and gender.** Pictures: farmer, driver, builder, carpenter,
  mechanic, tailor, nurse are men, the shepherd a boy; baker, weaver,
  engineer, doctor and teacher are women. In the texts girls want to be an
  engineer, a doctor, a nurse, a teacher, a weaver, a baker; boys a driver,
  a mechanic, a farmer, a teacher, a shepherd. A girl studies in the city and
  comes back (story 19). **The local team should read units 04, 13 and 19.**
- **Family words.** "aunt" is given as «خاله» and "uncle" as «کاکا». English
  has one word where Dari has two each (خاله / عمه, کاکا / ماما); the teacher
  has to say so.
- **Places.** Afghanistan, Asia, Kabul, Herat, Mazar-i-Sharif, Kandahar and
  Jalalabad are named in unit 08 as geography only. "There is no sea." Other
  countries are not named.
- **Tales.** The lion and the mouse, the crow and the jug, the fox and the
  grapes, the fox and the crow, the tortoise and the hare (here a rabbit) and
  the two goats on the bridge are old fables in the public domain, retold in
  the pack's own words. Some are also in the optional pack `en-3-stories`;
  here they carry the past tense, "said / asked" and the comparatives. No
  kings, no religious figures, nobody is killed.
- **Money.** A ticket costs 30 to 200 afghani: teaching numbers, not fares.
- **"Dear"** in a message is given as «... عزیز», "From Mina" as «از طرف
  مینا», "See you soon" as «به امید دیدار».
- **Names** are common first names, not people; girls and boys act and speak
  equally often.

## New pictures (26, listed in `pictures.txt`)

Drawn as SVG by the same AI from one small figure kit, and looked at
rendered. `saw`, `letter`, `crow`, `net`, `nest`, `cave`, `pigeon` and the
map and landscape pictures were already in the library. Weakest:

- `shepherd`: the sheep beside the boy is a white shape with a dark head and
  no legs.
- `carpenter`: the saw is small; the plank carries the meaning.
- `engineer`: a yellow helmet and a plan with a bridge. Will children know a
  helmet?
- `strong` / `weak`: the same boy with a rock above his head, and unable to
  lift it.
- `fast` and `slow` are taught with `rabbit` and `tortoise`; "tall" and
  "short" with `tree_tall` and `tree_short`; "long" with `pencil_long`;
  "heavy" with `heavy_load`; "country" with `map_afghanistan`; "world" with
  `globe`. The words have to be taught with the picture.
- `net` in the library is a hand net with a handle. The lion "was in a net":
  the picture fits the word, not the scene.
- `city` is four tall houses; Kabul does not look like that everywhere.
- `calendar` and `ticket` carry no writing or digits, as the rules ask.

## For the Dari-speaking reviewer

- jobs: farmer «دهقان», shepherd «چوپان», baker «نانوا», driver «دریور»,
  builder «گلکار», carpenter «نجار», weaver «قالین‌باف», mechanic «مستری»,
  engineer «انجنیر», workshop «ورکشاپ», "What do you want to be?" «می‌خواهی
  چه کاره شوی؟».
- travel: bus «بس» (or «سرویس»?), car «موتر», bicycle «بایسکل», motorbike
  «موترسایکل», boat «کشتی», plane «طیاره», train «ریل», ticket «تکت», lorry
  «لاری», tractor «تراکتور».
- world: sea «بحر», desert «دشت» (or «ریگستان»?), lake «جهیل», island
  «جزیره», forest «جنگل», country «کشور», "river" is «دریا» as in the other
  packs.
- comparing: bigger «کلانتر», younger «خُردتر», taller «قدبلندتر» / «بلندتر»,
  faster «تیزتر», slower «آهسته‌تر», more beautiful «مقبول‌تر», more
  difficult «مشکل‌تر», better «بهتر», worse «بدتر», new «نو», old (thing)
  «کهنه».
- feelings and character: afraid «ترسیده», angry «قهر», worried «پریشان»,
  calm «آرام», clever «هوشیار», greedy «حریص», brave «دلیر».
- story words: one day «یک روز», suddenly «ناگهان», finally «بالاخره», in
  the end «در آخر», shouted «چیغ زد», tale «قصهٔ قدیمی».
- messages: letter «خط», message «پیام», phone «تلفون», calendar «جنتری»,
  present «تحفه», "Get well soon" «زود جور شوی», university «پوهنتون».
- Help lines contain English words inside Dari sentences (see level 5).

## For the teacher or educator

- Unit 13 and the messages of units 17 and 18 use tiles that carry several
  words. They are shown smaller than single words. Check on a device that
  they can be read.
- "because" sentences with eight words have no extra tile (the screen holds
  eight).
- Story 11 ends with a sum (300 afghani, shoes for 500 or 250). Story 16
  asks the child to decide for the goats before the ending.
- The Yes or No? rounds of units 04, 06, 15 and 19 are listening tasks of
  two sentences; the picture only sets the scene.
- Catch It 20 and Baskets 11 need reading.

## For whoever listens to the audio

- Quoted speech: "Come here," said the fox. Does the voice pause?
- Gaps written "..." and pairs such as "big, bigger" in one clip.
- City names; "Mazar-i-Sharif".
- Whole messages are spoken in one clip ("Dear Sara, How are you? I am
  fine. From Mina.").

## Not done

- No teacher lessons and no teacher guide for level 6: this pack is the
  learner side and its `syllabus.md`.
- Not run on a handheld; nobody has listened to it.
- The sheets were written through a small authoring script; the CSV files in
  this folder are the source from now on, and `syllabus.md` has to be kept in
  step by hand.

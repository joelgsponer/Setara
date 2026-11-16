# English 5 "Health and help": what it teaches, what was decided, what is open

**Nothing here has been reviewed by a person.** The pack was written by an AI
(Claude) from the curriculum in the product spec (section 8, level 5:
"Explain what hurts, understand clinic instructions, give directions, talk
about weather and yesterday; past simple, must / should, reading short
texts"). Nobody has heard the audio and it has not run on a handheld. The
builder validated and built it, and every round was opened once in the app by
`tests/fuzz_rounds.lua` on a PC.

## What the pack teaches

20 units, one per classroom lesson. `syllabus.md` lists, unit by unit, the
words, the pattern, the can-do and the games in playing order; the teacher
guide is to be written from it.

| Units | Topic | Language |
| --- | --- | --- |
| 01-03 | How do you feel? What hurts? Aches and illnesses | I feel ..., I am not well, My ... hurts, I have a headache, He has a fever |
| 04-05 | At the clinic, the doctor's instructions | The doctor helps sick people, Take the child to the clinic; Open your mouth, Lie down, Breathe in, Don't move, Come back tomorrow |
| 06-07 | must, should | You must wash your hands, You must not ...; You should rest, You should not ..., What should I do? |
| 08 | Help! | Help! Can you help me? My brother is hurt. Be careful! Don't touch it. Are you all right? |
| 09, 11 | Where is it? Directions | near, far, behind, in front of, between; Go straight, Turn left / right, Cross the bridge, How do I get to ...? |
| 10 | Review | |
| 12-13 | Weather, the four seasons | It is sunny / raining / windy; In winter it snows |
| 14-17 | Yesterday | was / were; regular past (walked); irregular past (went, ate, drank, saw, slept, gave, came, had, took, fell); Did you ...? Yes, I did. I didn't ... |
| 18-19 | First, then, after that; We help | before / after, I feel better; My neighbour was sick, I visited her, I brought soup |
| 20 | Review | |

### Every unit is a teaching sequence

The round id carries the game's letter (`en-5-03-c`); within a unit the
letters are the order of teaching:

1. **PRESENT**: `a` Word Stall (hear the word, pick the picture, Dari on the
   help button) and `b` Echo (hear, say, compare: every word, sentence and
   dialogue of the unit). Both come from `items.csv`.
2. **UNDERSTAND**: `c` Listen In, a short dialogue with the new language. Its
   first page explains the pattern in Dari (`intro_fa`); two questions.
3. **PRACTISE**: three different games per unit out of `d` Riddles, `e` Yes or
   No?, `f` Which One?, `g` Question Road, `h` Baskets, `i` Sentence Train,
   `j` Catch It, `k` Shopkeeper, `l` Pairs.
4. **USE**: `m` Read and Decide, a reading text with questions that ask what
   and why.
5. **REVIEW**: units 10 and 20 have no new words; later units recycle
   earlier ones (must and should come back in the weather units, the clinic
   in the past-tense units).

Units 10, 14, 17, 18 and 20 have no Word Stall: they teach a pattern (was /
were, did, first / then) or review, and their words cannot honestly be
pictured. Units 10 and 20 have no Listen In.

Thirteen games, 132 rounds, 1171 rows:

| Game | Engine | Rounds | Pool | What it adds |
| --- | --- | --- | --- | --- |
| a Word Stall | listen_pick (items) | 15 | | hear the word, pick the picture |
| b Echo | say_it (items) | 20 | | say every word, sentence and dialogue |
| c Listen In | story | 18 | | dialogue, explained in Dari first, two questions |
| d Riddles | listen_pick | 7 | 12, asks 8 | the word is never said: "I want water" is "thirsty" |
| e Yes or No? | listen_pick | 8 | 12-13, asks 8 | a picture and a question; the same question with different pictures |
| f Which One? | listen_pick | 5 | 12-13, asks 8 | odd one out, what goes together, which written past form |
| g Question Road | journey | 9 | 12-13, asks 8 | question to answer; many answers are written words |
| h Baskets | sorter | 6 | 12-14, asks 8 | sick / well, must / must not, safe / dangerous, winter / summer, today / yesterday |
| i Sentence Train | builder | 13 | 9-10, asks 6 | build the sentence; the extra tile is the typical mistake; unit 18 orders pictures |
| j Catch It | catch | 3 | 5-6 rules, asks 4 | a spoken rule |
| k Shopkeeper | market | 1 | 9, asks 6 | a number inside a past-tense sentence |
| l Pairs | pairs | 7 | 9-12, shows 5 | written word to picture; walk / walked; go / went; opposites |
| m Read and Decide | story | 20 | | reading pages and what / why questions |

Reading grows through the level: 30 words on one page in unit 01, about 45
in the middle, two pages from unit 10, three pages (about 85 words) in unit
20. Written answers start in unit 01 with two or three short words.

## Repetition (counted by a script over the sheets)

- 881 different spoken questions and prompts: 720 are said once, 161 twice,
  none more than twice.
- No picture or word is the right answer more than three times in a game,
  with three exceptions that lie in the form of the game: Yes or No? (yes 53,
  no 44), Baskets (the basket is the answer), and in Question Road "no" (3)
  and "clinic" (3) after trimming.
- Every question row has a `help_fa`; every sheet round has its own
  `intro_fa` (130 of them, each with an English twin in
  `content/i18n/english5.csv`). The rounds of Word Stall and Echo use the
  game's instruction.

## Health content is language practice only

The pack teaches a child to **say** what is wrong and to **understand** what
she is told. It adds no medical fact to the health packs:

- No medicine is named, no dose, no remedy. The word "medicine" is not
  taught. The doctor's sentences are instructions for an examination (Open
  your mouth, Breathe in, Come back tomorrow), not treatment.
- "must" sentences repeat Health 1 and 2: wash your hands with soap, drink
  clean water, do not play with fire or matches.
- "should" sentences are everyday advice: rest, drink water, sleep early,
  wear a coat, brush your teeth, go to the clinic. "She has a fever. Should
  she go to school? No." is the strongest of them.
- Unit 08 follows `content/garden/3/SOURCES.md`: stay with the hurt person,
  shout for help, tell an adult, do not move him. Nothing else is said about
  first aid. The man in the dialogue says "Don't move him".
- In the stories the nurse "washed my knee and gave me a bandage", the doctor
  "saw the tooth and helped", "looked in her ear". No outcome depends on a
  treatment.
- "Should she eat sweets with a toothache? No" and "You should drink tea" (a
  boy with a cold) are the two sentences nearest to advice. **A health
  reviewer should read units 03 to 08 and stories 07, 08, 10, 16, 19 and 20**
  (`content/i18n/english5.csv` has the English of every Dari line).

## Decisions taken

- **Size.** 132 rounds, two more than the 110-130 asked for: 20 units times
  the five steps, less the Word Stall and Listen In rounds that five units do
  not have.
- **New words: fewer than the target.** The spec asks for about 250 new
  words. The sheets hold about 190 word forms that do not occur in levels 1
  to 4 (about 150 dictionary words: "walk, walked, walks" counted once). 89
  of them are in the word bank; the others are met in riddles, stories and
  sentences with Dari help. More words need more units or second rounds per
  unit. **Open**, as in level 4.
- **Past simple before "did".** Units 14 to 16 only state (was, walked,
  went); questions and negatives come in unit 17. Questions about the stories
  of 15 and 16 therefore use "Who ...?" and "Where was ...?". The reading
  questions of 15 and 16 do use "What did Sara wash?", one unit early, with
  Dari on the wrong-answer speech.
- **"because" is level 6.** Why-questions are answered by choosing a short
  written sentence ("He is thirsty"), without the word "because".
- **should** is translated «بهتر است که», **must** «باید», so that the two
  stay apart in Dari.
- **Clinic staff.** The doctor is a woman, the nurse a man (pictures and
  pronouns). Level 6 mixes further.
- **"road"** got the Dari «سرک», which level 4 gave to "street".
- **Written choices** are short because a card is one line. Three long ones
  in stories ("t:behind the school", "t:to find the goat", "t:He fed the
  hens") are drawn narrower.
- **Names** (Omar, Ali, Hamid, Karim, Jawad, Navid, Yusuf, Farid; Laila,
  Sara, Mina, Roya, Nargis, Shirin, Zarmina) are common first names, not
  people. Girls and boys speak and act equally often; the helper and the
  helped are a girl as often as a boy.

## New pictures (32, listed in `pictures.txt`)

Drawn as SVG by the same AI from one small figure kit, and looked at
rendered. All other pictures come from the library. Weakest:

- `neck` and `throat` stand side by side in unit 02 and both show a neck: the
  neck framed in yellow, the throat with an open mouth, a red spot and pain
  marks.
- `toothache` (hand on the cheek, a tooth above) and `earache` (a large ear
  with red waves) need the small extra sign to be told apart.
- `sick`, `hungry`, `thirsty`, `hot`, `cold`: feelings shown by one sign each
  (bed, empty bowl, tongue and empty cup, sun and sweat, snowflakes). They
  have to be taught; the picture alone does not say the word.
- `stop` is a hand in a red ring: a road sign that village children may not
  know. `hand` (level 2) is a plain palm.
- `near` and `far` are a pair (the same girl and house). `wait` is a boy
  behind a bench with a clock.
- Reused with a new word: `fa_fever_days` (fever), `fa_cough` (cough),
  `sneeze` (a cold), `tummy` (stomach), `water_covered` (clean water),
  `toddler_fire` (dangerous), `grandfather` (old), `baby` (young),
  `food_bowl` (soup), `go` (went), `look` (saw), `sweep` (cleaned),
  `arrow_up` (go straight). `pos_on` and `pos_under` show a table, the other
  position pictures a box; the questions say so.
- Stories reuse scenes of other packs (`scene_clinic`,
  `scene_health_worker`, `scene_boy_toothache`, `scene_directions`,
  `scene_village_map`), so the people in a picture are not always those of
  the text (the health worker in `scene_health_worker` is a woman; the
  dialogue of unit 02 calls her the nurse).

## For the Dari-speaking reviewer

Afghan Dari was intended throughout. Word choices to confirm or replace:

- feelings: sick «مریض», well «جور», tired «مانده», hungry «گرسنه», "I feel
  cold" «خنک می‌خورم», "I feel hot" «گرمی می‌کنم», "How do you feel?" «چه حال
  داری؟», "I feel sick" «خود را مریض احساس می‌کنم» (bookish?).
- body and illness: back «کمر», stomach «شکم», throat «گلو», shoulder «شانه»,
  neck «گردن», knee «زانو»; "What hurts?" «کجایت درد می‌کند؟»; a cold «ریزش»;
  cough «سرفه»; fever «تب»; hurt (injured) «افگار».
- clinic: doctor «داکتر», "doctor" as an address «داکتر صاحب», nurse «نرس»,
  bandage «بنداژ», thermometer «ترمامیتر», "Lie down" «دراز بکش», "Don't
  move" «شور نخور», "Breathe out" «نفست را بیرون کن».
- must «باید», must not «نباید», should «بهتر است که», "What should I do?"
  «من چه کنم بهتر است؟»; careful «احتیاط کن»; dangerous «خطرناک»; safe
  «بی‌خطر»; an adult «یک کلان».
- directions: "Turn left" «به دست چپ دور بخور», "Go straight" «مستقیم برو»,
  "Cross the bridge" «از پل تیر شو», "Stop" «ایستاد شو», in front of «پیش
  روی», between «بین», road «سرک».
- weather: sunny «آفتابی», cloudy «ابری», windy «بادی» / «باد می‌وزد», storm
  «طوفان», autumn «خزان», cool «خنک», wet «تر», umbrella «چتری», coat
  «بالاپوش».
- past: the help lines explain "ed" and the irregular forms in Dari with the
  English word inside the sentence («went گذشتهٔ go است»). The Persian voice
  will meet Latin words there; decide how they should be spoken.
- others: neighbour «همسایه», soup «شوربا», blanket «کمپل», old (person)
  «پیر», young «خُردسال» (with a vowel mark for the voice), kind «مهربان»,
  "You're welcome" «قابل تشکر نیست» as in level 4.
- Ezafe is written with «ٔ» (همسایهٔ من), as in level 4.

## For the teacher or educator

- Is "should" with "No" answers right for the age ("His knee hurts. Should
  he run?")? The questions have one sensible answer each, but they are
  judgements, not facts.
- Unit 08 has a child alone with a hurt brother who must decide (story 08:
  run, play, or stay and shout for help). Suitable for the youngest?
- Story 19 and unit 19 show children visiting an old woman neighbour who
  lives next door and bringing food. Acceptable everywhere?
- Grammar is sorted in three Baskets rounds (today / yesterday by sentence,
  then by written verb; must / must not). Too abstract for some?
- Unit 18 of Sentence Train asks the child to put three pictures in the
  order of a spoken mini-story. It is a new use of the builder; see whether
  children understand it without a teacher.
- Reading: the written answers of Read and Decide are not read aloud. A
  child who cannot yet read Latin letters can only guess there. The pack
  assumes the reading of levels 3 and 4.

## For whoever listens to the audio

- Pairs of words said in one clip: "go, went", "walk, walked".
- Gaps are written "..." ("Yesterday I ... to the bazaar."): what does the
  voice do with them?
- "ah", "Mazar" (level 6), the names, "didn't", "wasn't".
- Dari help lines that contain English words (see above).
- Dialogues switch between the two voices up to three times in one clip.

## Not done

- No teacher lessons and no teacher guide for level 5: this pack is the
  learner side and its `syllabus.md`.
- Not run on a handheld; nobody has listened to it.
- The sheets were written through a small authoring script; the CSV files in
  this folder are the source from now on, and `syllabus.md` has to be kept in
  step by hand.

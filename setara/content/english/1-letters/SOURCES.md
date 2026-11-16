# Sources and review status of en-1-letters (English letters: the whole alphabet)

**This pack is optional** (`"optional": true`). It adds 13 games to English
level 1. It is a separate zip: leave it off the card and nothing of it is
there. No other pack refers to it.

**Not read or heard by a Dari speaker, an English teacher or a child.** It was
written by an AI. It was only ever built with silent speech: nobody has heard
one clip. `content/i18n/english_letters.csv` carries the English of every Dari
text, for the reviewer who does not read Dari.

## Why the pack exists

English 1 and 2 teach about 240 words and no alphabet: only "Sound Catcher"
touches twelve first-letter sounds. This pack teaches all 26 letters: the
name, the most common sound, the big and the small shape, the alphabet order,
and the first letter of words the children already know from `en-1` and
`en-2`.

## The pack is generated

`generate.py` in this folder writes every CSV here, `pack.json` and
`content/i18n/english_letters.csv`. 26 letters times a dozen question forms
is a table, and the script also checks the table (see "What the script
checks"). **To change a key word, a Dari explanation or a letter set, edit
`generate.py` and run it; do not hand-edit the CSVs**, the next run would
undo it. `setara/CLAUDE.md` names math as the only generated content; this
pack is a second case and that file was not touched. If the owner prefers
hand-kept sheets, delete `generate.py` and the CSVs stand on their own.

## The seven sets, and why this order

| Set | Letters | Key words |
| --- | --- | --- |
| 1 | a t s p | apple, table, sun, pen |
| 2 | n c e g | nose, cat, egg, goat |
| 3 | d o h m | dog, orange, hen, moon |
| 4 | i b r f | ink, bag, rope, fish |
| 5 | u l k w | umbrella, leg, key, water |
| 6 | j y v | jug, yoghurt, village |
| 7 | x q z | box (at the end), quilt, zebra |

Not alphabetical, but by usefulness, in the manner of "s a t p i n":

- the letters that begin most of the words the children know come first; the
  rare ones (j y v, x q z) last, in small sets of three;
- every set but the last two has a vowel, so words can be built early
  (cat, hen, dog, pen after set 3);
- **look-alikes are never introduced together**: b (4), d (3), p (1), q (7);
  m (3), n (2); i (4), l (5); u (5), v (6); h (3), n (2);
- alphabetical order is its own subject and has its own three games
  (Alphabet Echo, Alphabet Train, What Comes Next?), which a child can play
  from the first day.

Each set is introduced in "Meet the Letters" (name, both shapes described in
words, the sound, a key word with its picture), then practised in Letter
Stall, First Letter and Letter Baskets, whose later rounds mix in the earlier
sets. The other games go in groups of two or three sets.

## The games

| Game | Engine | Rounds | Items | Asked per play | What it is |
| --- | --- | --- | --- | --- | --- |
| `meet_letters` | story | 8 | 85 pages, 17 decisions | all | Round 00: how English writing differs from Dari. Rounds 01-07: one set each |
| `letter_names` | listen_pick | 10 | 173 | 8 of 12 to 20 | 01-07 hear the name, pick the letter (big, small, both, earlier sets). 08-10 a big letter is shown, find its small one, and back |
| `alphabet_echo` | say_it | 3 | 20 | all | The alphabet in seven groups; every letter with its key word; long groups and the whole alphabet |
| `big_small` | pairs | 5 | 52 pairs | 6 of 8 to 14 | 01-03 big with small. 04-05 letter with its key picture |
| `first_sounds` | journey | 4 | 60 | 8 of 14 to 16 | Two (or three) words that begin alike: pick their letter. Round 04: also the letter at the END (box, fox, six) |
| `first_letter` | listen_pick | 7 | 107 | 8 of 11 to 18 | A picture and its word: pick the first letter. Round 07: first and LAST letter |
| `letter_baskets` | sorter | 8 | 155 | 8 of 12 to 23 | 01-05 the four letters of a set as baskets. 06 j y v z. 07 the look-alikes b d p. 08 vowels and consonants |
| `starts_with` | listen_pick | 4 | 70 | 8 of 16 to 19 | The reverse: a letter is shown, pick the picture that begins with it |
| `letter_rain` | catch | 4 | 40 rules | 4 of 8 to 14 | Catch the letter that is called (big or small). Round 04: catch the first letter of a spoken word |
| `abc_order` | builder | 4 | 56 | 8 of 14 | Put 3 to 6 letters in alphabet order. Round 04: the letters are called out of order |
| `abc_next` | journey | 4 | 63 | 8 of 12 to 20 | Which letter comes next, before, in between |
| `look_alikes` | listen_pick | 4 | 69 | 8 of 9 to 30 | b and d; p and q; m n, u v, i l; the look-alike big letters E F, M W, O Q, C G, P R |
| `spell_it` | builder | 4 | 40 | 6 of 9 to 12 | Build three-letter words from letter tiles (cat, hen, dog, sun ...), then four-letter ones |

13 games, 69 rounds, 990 items. That is more than the 10 games and 50 to 60
rounds asked for: 26 letters in seven sets, each met in several forms, did not
fit in less. `big_small` and `starts_with` are the first to merge or drop if
the level screen gets too full.

Engines used: story, listen_pick, journey, pairs, sorter, catch, builder,
say_it. Not used: market and duel (nothing here is counted or paid).

## Decisions

- **Dari explains, English names.** No Dari text contains a Latin letter
  (the script refuses one), because the Persian voice cannot be trusted to
  read it. Dari speaks of "this letter", describes its shape in words
  ("a tall standing line and then one belly at the bottom, on the right")
  and compares its sound with the start of a Dari word («بز», «نان»). The
  name of a letter is always said by the English voice.
- **How English differs from Dari** is told in story round 00 and repeated
  in round introductions and help: left to right; letters do not join; two
  shapes per letter, the big one for names and the start of a sentence; a
  letter's name and its sound differ; English writes the short vowels that
  Dari leaves out.
- **No bare sound is ever spoken.** A synthetic voice reads "a" or "b" as the
  letter's name, and respellings ("buh", "sss") come out wrong (checked: the
  phonemizer reads "sss" as "ess ess ess"). So a sound is always carried by
  words: two words that begin alike ("bag. ball."), and a Dari word that
  begins with the same sound in the help. The task's example "a, a, apple"
  would be spoken "ay, ay, apple": name, name, word. That form is used only
  where the name is meant (the baskets say "A, A, apple.").
- **A letter's name is written so that the voice says the name.** "A" before
  another word is read as the article ("A is for apple" comes out as
  "uh is for apple"). Every name therefore stands at the end of a phrase or
  before a comma or full stop: "the letter A", "A, as in apple", "Find small
  a.", "A, B, C, D.". "big" and "small" are used, not "capital": the children
  know both words from en-1.
- **x** begins no word the children know. It is taught at the end of box,
  fox and six, and that became a question form of its own (the LAST letter).
- **q** has one pictured word (quilt) and **i**, **u**, **v** two each.
  Their baskets and rounds are filled with the big letter as a thing to sort.
- **Words that begin with another sound than their letter's are left out**:
  almond, apricot, onion, open, sugar, eleven, write, eye, ear, and every
  word with ch, sh, th. The script checks this.
- **c, k and q** have the same first sound: where a question goes by the
  sound, they are never offered against each other.
- **Vowels and consonants** (baskets round 08) are «حرف صدادار» and «حرف
  بی‌صدا», explained by the mouth: open, air free, or closed by lips, tongue
  or teeth.
- **Wrong choices** are look-alike letters first (b: d p h), then letters of
  the same set.
- **New words**, each with its Dari meaning in the help: ant, axe, drum,
  elephant, eggplant, fox, fire, garlic, hat, hammer, ink, in, jug, jar,
  juice, kite, kebab, lemon, lamp, lock, lion, mirror, nest, needle, nail,
  on, pear, pumpkin, parrot, quilt, rain, radio, rooster, snake, tent, train,
  tap, umbrella, up, van, wall, wolf, zebra, zip; heard only: end, empty,
  olive, ox, question, quick, zero, we, under, map, net, can. Many of them
  come back in en-3 and en-4.

## What the script checks (the variety table)

Rules of the variety brief: no spoken question more than twice in the pack,
no answer right more than about three times per game. A question is the Dari
plus the English of a row, case and punctuation ignored.

Whole pack: 763 distinct questions; 668 asked once, 95 twice, none more often.

| Game | Questions | Distinct | Most often the same | Different answers | Most often right |
| --- | --- | --- | --- | --- | --- |
| `meet_letters` | 17 | 17 | 1 | 17 | 1 |
| `letter_names` | 173 | 173 | 1 | 78 | 3 |
| `alphabet_echo` | 20 | 20 | 1 | | |
| `big_small` | 52 pairs | 52 | 1 | | |
| `first_sounds` | 60 | 60 | 1 | 60 | 1 |
| `first_letter` | 107 | 107 | 1 | 71 | 3 |
| `letter_baskets` | 155 | 155 | 1 | 26 baskets | 13 (see below) |
| `starts_with` | 70 | 70 | 1 | 70 | 1 |
| `letter_rain` | 40 | 40 | 1 | 40 | 1 |
| `abc_order` | 56 | 56 | 1 | 56 | 1 |
| `abc_next` | 63 | 62 | 2 | 43 | 3 |
| `look_alikes` | 69 | 69 | 1 | 46 | 3 |
| `spell_it` | 40 | 37 | 2 | 37 | 2 |

Exceptions, on purpose: in a sorter the answer is the basket, so a basket is
right for every thing that belongs in it (4 to 6 per letter basket, 13 for
"consonant"). `spell_it` round 04 repeats cat, hen and dog as review.

The script also checks: every picture exists; no wrong choice equals the
answer; every question row has a `help_fa`; every Dari text has an English
twin; every word of the word bank begins with its letter's sound; and the
693 English lines that must name a letter do so in the phonemizer (next
section).

## The voice: what was checked and every doubtful case

**Checked by machine, not by ear.** The piper stand-in voices get their
phonemes from espeak-ng. `generate.py` passes every English line that must
name a letter through espeak-ng and compares: all 693 name the right letters
in the right order. This says the voice is *asked* for the right sounds. It
says nothing about how the clip sounds, and nothing at all about the
production voices (ElevenLabs), which read text their own way. **Listen to
these:**

1. **Single letters.** "A.", "B.", "small a", "Which one is b?", "l. Which
   picture?", "Find small l." A one-syllable clip may be clipped, or a
   production voice may read "a" as "uh", "I" as the pronoun (same sound,
   fine), small "l" as "one" or "ell".
2. **Names that are easily confused by ear:** B / D / E / G / P / T / V / Z
   (all end in "ee"), M / N, F / S, A / K / J. A child cannot ask the device
   to repeat more clearly; X (again) and the slow replay are all there is.
3. **Z is "zee"** (American voices). A teacher trained on British English
   says "zed". Decide; a British voice would change it by itself.
4. **H** ("aitch"), **W** ("double-u"), **R** ("ar"), **Y** ("why"),
   **Q** ("cue"): names that sound nothing like the letter's sound.
5. **Letter strings:** "A, B, C, D.", "w, x, y.", "T, C, M, F." and the
   whole alphabet in one clip (`alphabet_echo` round 03, four lines joined
   with `//`): a voice may run the names together or read "A" as an article
   after a pause.
6. **Spelling aloud:** the builder says "C, A, T. cat." when the word is
   built; "I, N. in.", "O, N. on.", "U, P. up." are the risky ones.
7. **Carrier phrases with a name inside:** "Big A. Small a.", "X, at the end
   of box", "box ends with X.", "Which letter is between N and P?",
   "bag. B or D?", "This is big I. Find small i.", "A, the big one.".
8. **Words said alone or in pairs** to carry a sound: "in.", "on.", "up.",
   "is. it.", "end. empty.", "olive. ox.", "red. read." (read must rhyme
   with "need" here; the phonemizer says so), "tap", "a dog", "yoghurt",
   "quilt. question.", "zero. zip.".
9. **Dari clips of one word** (the meaning before a word to spell): «شیر»
   (milk; the lion is written «شیر درنده»), «ده» (ten, not village), «نُه»,
   «خُرد» (written with the vowel mark everywhere), «در داخل», «روی», «بالا».
10. **Dari words used as sound anchors** must be said the Afghan way:
    «انار», «امروز», «اینجا», «آفتاب», «اگر», «ورق», «عکس», «جوی», «گل»,
    «کلید», «لب», «یک». The stand-in Persian voice is Iranian.

## For the Dari-speaking educator

- **Sound anchors.** a = start of «انار» "with the mouth open"; e = start of
  «امروز», "short"; i = start of «اینجا» "but shorter"; o = start of «آفتاب»
  "but short"; u = start of «اگر» "with the mouth only a little open". To a
  Dari ear English a and u, and e and i, are close. Are these the anchors a
  teacher would use? Is «امروز» said with e or with i where the pack goes?
- **v** is explained by the mouth (upper teeth on the lower lip, like the
  start of «فیل» but with the voice) and **w** by «ورق» "with round lips",
  on the assumption that Afghan Dari says «و» as w. In a region where it is
  said v, swap the two explanations.
- **q** is "two sounds quickly: like the start of «کتاب», then like the
  start of «ورق»"; **x** is "like the end of «عکس»". Good enough?
- **Words for the letters and shapes**: «حرف کلان» / «حرف خُرد» for capital
  and small (schools may say «حرف بزرگ / کوچک»); «شکم» (belly) for the bowl
  of b d p q; «خط ایستاده / خوابیده / کج» for vertical, horizontal, slanting;
  «کمان», «دُم», «چنگک», «پایین خط می‌رود» (goes below the line).
- **«صدادار» / «بی‌صدا»** for vowel and consonant.
- **Meanings of new words**: zebra «گوره‌خر», zip «زنجیرک», quilt «لحاف»,
  ink «سیاهی قلم», van «موتر مسافربری», jug «کوزه», jar «مرتبان», kite
  «کاغذپران», umbrella «چتری», eggplant «بادنجان سیاه», lion «شیر درنده»,
  train «ریل», tap «نل», can «قطی», net «جال», nail «ناخن» (the finger
  nail, as the picture shows), "in" «در داخل», "on" «روی», "up" «بالا».
- Colloquial words: «بمان» (put), «گد و ود» (mixed up), «هوش کن», «شاباش»,
  «غم نیست». Keep or replace.
- Dari is said to have 32 letters, English 26, and "five letters, one of
  which you see in almost every word" (the vowels).
- The 26 shape descriptions are long sentences heard, not read. Too long for
  a six-year-old? They are also the help text (Y) of most questions.

## For the English teacher

- Is the set order right for these children, or should the pack follow the
  alphabet (the order a school book uses)? Changing `SETS` in `generate.py`
  regroups everything.
- Key words: ink (not a word of en-1 or en-2), jug, quilt, zebra, village
  (a scene, not an object), box for x.
- Only the short vowel sounds and the hard c and g are taught. Long vowels,
  soft c and g, ch, sh, th and silent letters are left for later levels;
  words that have them at the start are kept out.
- comb, lamb (silent b), walnut, yoghurt, tree and train (tr sounds like
  "chr" to many ears) are used for their FIRST letter only.
- `spell_it` says the meaning in Dari and then the English word; the letters
  are named only after the word is built. egg has a double letter; box, fox,
  six end in x; in, on, up have two letters.
- English carrier phrases the children have not been taught are used as
  prompts ("Find", "Which one begins with", "What comes after", "Catch the
  first letter of"). Each round's Dari introduction says what to do, and the
  key word of every prompt is a letter name or a known word. Acceptable?

## Limits of the engines (nothing was changed in the app)

- **The builder cannot show a picture.** The task asked for three-letter
  words spelled "with the picture shown". The engine has only tiles, so
  `spell_it` speaks the Dari meaning and the English word instead. A `show`
  column for the builder would be a small engine change.
- **The sorter has no `help_fa` column**: Y repeats the baskets. Its things
  therefore have no "why" text; the round introduction carries it.
- **Pairs has no help either**; every card speaks its sentence when turned.
- Pools are smaller than the 12 the authoring doc asks for where the
  material is small: `look_alikes` round 01 (b, d: 9 items, 8 asked),
  `spell_it` (9 to 12 words, 6 asked), `letter_rain` (8 to 14 rules, 4 asked).
- `look_alikes` round 03 has 30 items, more than the 24 suggested; it covers
  six letters.

## Pictures

Five new ones, drawn for this pack and looked at on a contact sheet: `ink`,
`quilt`, `zebra`, `van`, `zip` (briefs in `pictures.txt`). The zebra's head
is busy at 3 cm; the quilt could be read as a window or a board of colours.
No picture of a person was drawn. Library pictures that show people and are
used here: girl, boy (as "baby"/"boy" words), father, mother, grandmother,
grandfather, family, baby, you, hair: all approved or pending with their
home packs.

Pictures used as words they were not drawn for: `water_jug` (jug),
`scene_village` (village), `pos_in` (in), `pos_on` (on), `arrow_up` (up),
`color_yellow` (yellow), `yes` (a green tick for "yes"), `nail` (finger
nail), `hat` (a round cap).

## What was run

- `generate.py`: ends `ok` (all its own checks).
- `validate --quiet --only en-1-letters`: `ok`, 0 warnings, no untranslated
  line of this pack.
- Silent build of `core` and `en-1-letters` into a scratch folder: `ok`.
- `tests/fuzz_rounds.lua` on a scratch save dir with the two packs: every
  round opened in single and pair mode, no error.
- Screenshots of at least one round of every game were looked at: letters,
  `t:Aa`, `t:A B ?` and the Dari basket labels fit their cards; the big I has
  serifs and the small l has a tail in the app's font (Andika), so I and l
  are told apart; the small a is the one-storey a the descriptions speak of.
- **Not done:** no build with real voices, nothing heard, nothing tried on a
  handheld or with a child.

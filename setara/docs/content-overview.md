# Content overview

**Review status: none of this content is ready for children.** Every text in
every pack (Dari, English, math, health, first aid, children's rights,
geography), every teacher lesson and every picture was produced by an AI
(Claude). **No Dari-speaking educator, no health professional and nobody
from the local team has reviewed any of it.** **Nobody has listened to the
generated speech**; the voices are stand-ins, and the Persian voice is
Iranian, not Afghan. **The content must not reach children before that
review. This holds most of all for the first-aid pack (`garden-3`)**, which
follows standard first-aid guidance as the AI understood it. The English of
English mode was written by the same AI; it shows what the Dari is meant to
say and is not a check of the Dari.

The open points that earlier AI passes could not judge are collected in
[review-notes.md](review-notes.md). What the review has to cover is listed in
[authoring.md](authoring.md#what-has-to-be-true-before-content-ships) and in
[privacy-and-safety.md](privacy-and-safety.md#safeguards-for-content).

## All packs

This table was made on 14 November 2026 by a small script that ran the
builder's own parser over every `pack.json` and its sheets in `content/`
(no audio, nothing written). "Rounds" are playable rounds; a round is 6 to 10
items and takes two to four minutes. The first-aid pack was still being
changed on that day, so its numbers may have moved. The table in the project
`README.md` is older and shows fewer packs and rounds.

### Learner packs

| Id | Title | Subject | Level | Optional | Games | Rounds |
| --- | --- | --- | --- | --- | --- | --- |
| `en-1` | English 1: Hello | `en` | 1 | no | 7 | 65 |
| `en-2` | English 2: My world | `en` | 2 | no | 7 | 67 |
| `en-3-stories` | English story book | `en` | 3 | **yes** | 4 | 16 |
| `en-3` | English 3: My day | `en` | 3 | no | 11 | 86 |
| `en-4` | English 4: At the bazaar | `en` | 4 | no | 11 | 76 |
| `fa-1` | Dari 1: Sounds and first letters | `fa` | 1 | no | 6 | 38 |
| `fa-2` | Dari 2: The whole alphabet | `fa` | 2 | no | 6 | 42 |
| `fa-3-stories` | Dari story book | `fa` | 3 | **yes** | 4 | 16 |
| `fa-3` | Dari 3: Syllables and words | `fa` | 3 | no | 7 | 60 |
| `fa-4` | Dari 4: Sentences | `fa` | 4 | no | 7 | 50 |
| `garden-1` | Garden 1: Me | `garden` | 1 | no | 6 | 22 |
| `garden-2` | Garden 2: My Home | `garden` | 2 | no | 7 | 20 |
| `garden-3` | Health 3: First aid | `garden` | 3 | no | 8 | 25 |
| `garden-4-rights` | My rights, your rights | `garden` | 4 | **yes** | 6 | 13 |
| `garden-4-world` | The world, Switzerland and Basel | `garden` | 4 | **yes** | 9 | 32 |
| `garden-4` | Health and environment 4: My future | `garden` | 4 | no | 15 | 40 |
| `math-1` | Math 1: Counting to 20 | `math` | 1 | no | 6 | 44 |
| `math-2-puzzles` | Logic Puzzles | `math` | 2 | **yes** | 9 | 43 |
| `math-2` | Math 2: Numbers to 100 | `math` | 2 | no | 6 | 42 |
| `math-3` | Math 3: Numbers to 1,000 | `math` | 3 | no | 6 | 40 |
| `math-4` | Math 4: Times Tables and Sharing | `math` | 4 | no | 9 | 45 |
| `math-5` | Math 5: Large Numbers and Fractions | `math` | 5 | no | 10 | 47 |
| **Total** | 22 learner packs | | | 5 optional | **167** | **929** |

The per-pack descriptions further down cover the first 14 packs; for the newer ones read each pack's `SOURCES.md`.

### Other packs

| Id | Kind | What |
| --- | --- | --- |
| `core` | core | The app's own strings: menus, the guide's sentences, the tutorial, numbers for the class games. 116 strings in `content/core/strings.csv`. The app does not start without it |
| `teacher-en-1` | teacher | 20 classroom lessons for English 1 (599 lesson lines, five check questions each), a Phrase Board of 5 pages with 8 phrases each, 10 teaching tips |

All packs are version 1.

### Not written yet

English 3 to 6, Dari 3 to 6, math 4 to 6, a regular Garden level 4, teacher
lessons beyond English 1. The level chips for them are shown greyed out on
the place screens.

### Sizes

The built zips in `packs/` on that day were 1 MB (`core`) to 16 MB
(`math-3`), about 135 MB together, with the stand-in voices. Most of a pack
is speech.

To print a table from your own build:

```sh
cd builder && python3 -m setara_builder.cli build && cd ..
python3 tools/content_table.py
```

Careful: `tools/content_table.py` also rewrites the content table inside
`README.md`.

## What each pack teaches

The descriptions below say what the sheets contain. They do not say the
content is correct.

**`en-1`, English 1: Hello.** Twenty units that match the twenty teacher
lessons: greetings, classroom commands, "What's your name?", boy and girl,
yes and no, numbers 1 to 10, "How old are you?", classroom things, colours,
food, "my friend", "How are you?", big and small, please and thank you, and
two review units. Speaking and listening first. Games: Word Stall (hear a
word, pick its picture), Echo (say it aloud), Sound Catcher, Sentence Train
(build a sentence from word tiles), Shopkeeper (count goods for a customer),
Radio Stories, Number Stall. The word list is
[../content/english/1/syllabus.md](../content/english/1/syllabus.md).

**`en-2`, English 2: My world.** Twenty more units: family, "I have a
ball", face and body, numbers 11 to 20, "How many?", food and drink, fruit
and vegetables, "Do you like honey?", animals, plurals ("Two goats"), at
home, my village, and two review units. The same seven games. Word list:
[../content/english/2/syllabus.md](../content/english/2/syllabus.md). There
are no teacher lessons for this level yet.

**`fa-1`, Dari 1: Sounds and first letters.** First steps in reading Dari:
hearing the first and last sound of a word, rhyme, the first letters, the
shapes a letter takes at the start, in the middle, at the end of a word and
alone, building short words from letters (right to left), syllables, two
read-along stories, and a pairs game on words that end the same way.

**`fa-2`, Dari 2: The whole alphabet.** The remaining letters including the
rare ones, the names of the letters, the short-vowel marks (zabar, zer,
pesh), more letter shapes, longer words, syllables, two read-along stories,
and a pairs game matching letters to pictures.

**`math-1`, Math 1: Counting to 20.** Counting things, numbers in both
forms (the numerals used in Dari and the Western ones), more and fewer,
adding and taking away within 20 with a number line that shows the hops,
short spoken story sums, putting a number of goods on the scales, ordering
numbers, basic shapes, longer and shorter, corners and sides.

**`math-2`, Math 2: Numbers to 100.** Tens and ones, before and after,
comparing, adding and subtracting including whole tens, paying a price with
coins and notes, even and odd, whole, half and quarter, reading a clock.

**`math-3`, Math 3: Numbers to 1,000.** Hundreds, tens and ones, comparing,
adding and subtracting, first multiplication, paying larger amounts, even
and odd, more or less than 500, fractions again, metres and centimetres.

All three math packs are generated by
[../content/math/generate.py](../content/math/generate.py). Every answer is
computed and checked by assertions, so the arithmetic is the one part of the
content that has a mechanical check. The Dari wording of the questions has
none.

**`garden-1`, Garden 1: Me.** Washing hands (the steps, and when),
brushing teeth, bedtime, clean and dirty, a story about a boy's day (Omid's
Day), parts of the body and what they do, animals and plants, the four
seasons, domestic and wild animals.

**`garden-2`, Garden 2: My Home.** Making water safe by boiling (with a
grown-up), keeping water clean at home and at the well, using the latrine,
oral rehydration solution for a child with diarrhoea (a grown-up prepares
it), three food groups and a good plate, where water comes from, rubbish,
why trees matter, stove smoke, and two stories (Shirin and the Safe Water,
Little Nurse).

**`garden-3`, Health 3: First aid.** Burns, cuts and bleeding, animal
bites, nosebleed, choking, a fit, what to do when someone has collapsed
(marked as being for older pupils and teachers; a small child's job is to
run for an adult), danger signs in an ill relative and when to go to the
clinic, and poisoning (swallowed poison, poison in the eye, smoke in a
closed room, keeping dangerous things out of reach). Told through five
stories, ordering games, do-and-don't sorting and listening questions. No
doses, no names of medicines, no home remedies. **Not checked by a health
professional.** Its notes file names the rounds that most need a
professional's eye.

**`garden-4-rights`, My rights, your rights (optional).** Ten ideas from
the UN Convention on the Rights of the Child in a child's words: every child
matters the same; a name and a family; food, water, a home and health care;
learning; play and rest; safety; being listened to; children with a
disability; respect for the rights of others; telling an adult you trust.
Three stories, a class talk for the teacher to run through Story Time, a
sorter, listening questions and pairs. Neither document is named in the
pack.

**`garden-4-world`, The world, Switzerland and Basel (optional).** The
round Earth, seven continents, five oceans, where Afghanistan is, how far
Switzerland is, what the two countries share (no sea coast, high mountains
with snow), Switzerland, and the city of Basel. It ends with one sentence
saying that the lessons and pictures on the device were made in Basel. A
three-part class session, listening questions with choices read aloud, a
sorter (Afghanistan, Switzerland, both), a journey, ordering and pairs.

**`teacher-en-1`, English 1 lessons.** See
[teacher-mode.md](teacher-mode.md).

Which engine each game uses is listed in [games.md](games.md).

## Where the facts come from

Three packs carry a `SOURCES.md` next to their sheets. Each records the fact
sheet the pack was written from, where the pack simplifies or goes beyond
it, what a reviewer should look at, and its review status.

| Pack | File | What it holds |
| --- | --- | --- |
| `garden-3` | [../content/garden/3/SOURCES.md](../content/garden/3/SOURCES.md) | The first-aid fact sheet in full (modelled on IFRC and WHO guidance, as the file says), every simplification, the changes made in a first-aid review, and the same for the poisoning part that was added later. The file says that the reviewer was not a health professional and not a native Dari speaker |
| `garden-4-rights` | [../content/garden/4-rights/SOURCES.md](../content/garden/4-rights/SOURCES.md) | The ten ideas with their CRC articles, which game teaches what, the limits the pack keeps, and a numbered list of sentences a cautious local reviewer might question |
| `garden-4-world` | [../content/garden/4-world/SOURCES.md](../content/garden/4-world/SOURCES.md) | The geography fact sheet in full, the simplifications, and a list of Dari words a reviewer should check |

Some statements in these files about pictures "not drawn yet" are older than
the picture library; see below for the count.

The other packs have no sources file. The health statements of `garden-1`
and `garden-2` (handwashing, boiling water, oral rehydration, food groups)
have no recorded source in the repository.

For a reader who does not read Dari, `content/i18n/*.csv` carries the English
of the Dari texts: `firstaid.csv`, `rights.csv`, `world.csv`, `garden.csv`,
`dari.csv`, `math.csv`, `teacher.csv`. This English was written by the AI
from its own Dari.

## The picture library

| | |
| --- | --- |
| Where | `content/pictures/`, one SVG per picture, shared by all packs |
| How many | 595 SVG files on 14 November 2026; the sheets used 593 picture names and all of them were drawn. The number was still growing that day |
| Kinds | Things (square, `viewBox 0 0 128 128`, transparent background) and story scenes (`scene_*`, 4:3, 128 of them) |
| Style | Thick dark outlines, flat colours, no text, no gradients, readable at 3 cm on a 3.5 inch screen |
| How made | Written as SVG code by the AI from the drawing briefs in the `pictures.txt` files. The commit history shows review rounds and some redrawing. No illustrator and no local reviewer has seen them |
| Maps | The 25 map pictures of the geography pack (`map_*`, `scene_map_*`, `globe`) are generated by [../tools/maps.py](../tools/maps.py) from Natural Earth map data (naturalearthdata.com, public domain). Country borders are not drawn; a map shows land and sea and at most the one or two countries a lesson is about |
| In a pack | The builder renders each used picture to a PNG of 160×160 px (scenes 400×300 px) with 64 colours |

To count and check on your own checkout:

```sh
ls content/pictures/*.svg | wc -l
python3 tools/picture_list.py --missing      # pictures the sheets use that are not drawn
python3 tools/contact_sheet.py /tmp/sheet.png apple bread scene_well
```

`tools/maps.py` needs the `shapely` package and downloads the map data once.

A local reviewer must approve every picture of a person before it ships:
dress, gestures, girls and boys together in one picture. The briefs say what
was intended; see for example
[../content/english/1/pictures.txt](../content/english/1/pictures.txt).

## Speech

Every text in the sheets becomes an audio clip at build time; a full build of
the current content generated about 6,900 clip files, slow variants included. They are generated with stand-in voices
and have not been listened to by anyone. See [speech.md](speech.md).

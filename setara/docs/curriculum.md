# Curriculum and teaching design

This is the plan Setara's content is written against: what is taught, in what
order, how a session teaches, and what the teacher is given. The product spec
sets the frame (four subjects, levels, a child starts where a placement game
puts her). This document fills it in. It was designed by an AI and has not
been checked by an educator; it is where an educator should start.

Status words used below: **written** (in the repo, builds, every round
opens), **written**, **planned**. "Written" never means reviewed.

## 1. Principles

1. **Teach, then ask.** Nothing is tested that was not first shown. Every
   new word, letter, number fact or health rule is presented with picture,
   sound and, where it helps, a short story, before any question about it.
2. **One idea at a time, many forms.** A unit teaches one small thing and
   practises it in at least three different kinds of task, so that the child
   meets the idea and not the question.
3. **Explain why.** A wrong answer is followed by the reason, never by a
   buzzer alone. The Y button explains in Dari on every question.
4. **Come back to it.** What was learned returns the next day, the next week
   and in later units. What a child got wrong returns sooner.
5. **Speech first, reading grows.** Nothing depends on reading until the
   Dari reading level that teaches it; from there reading is practised in
   every subject.
6. **The class and the device teach together.** The teacher teaches the
   idea with things in the room; the device supplies correct speech,
   pictures and practice. Neither replaces the other.
7. **Gentle.** No ranking, no lives, no timer that punishes. Girls and boys
   in equal measure. Local things: sheep, bread, the well, the bazaar.

## 2. How a unit teaches

A unit is one step of a level (English and the teacher lessons count 20
units a level; other subjects 8 to 14). Its rounds follow one sequence:

| Step | What happens | On the device |
| --- | --- | --- |
| 1. Remember | Five questions from earlier units | The warm-up before a round |
| 2. Present | The new items, each with picture, sound, Dari meaning | Word Stall, Echo, a teaching story |
| 3. Understand | The items used in a small situation | A dialogue, a mini-story, a number line that shows why |
| 4. Practise | Three or more different forms | Odd one out, yes or no, riddles, sorting, building, catching, pairs, the market |
| 5. Use | A task that needs the idea to decide something | A story with decisions, a reading page with questions, a word problem |
| 6. Check | Did it stay? | Mixed review rounds; the teacher's Quick Check |

A round takes two to five minutes. A round is a pool: it holds more
questions than it asks, in a new order every time, so that playing it again
is practice and not memory of positions.

## 3. How a class session runs

One device, one loudspeaker, up to 50 children, about 35 minutes:

| Minutes | Step | Teacher | Device |
| --- | --- | --- | --- |
| 3 | Hello | Greets, recalls yesterday | Plays the greeting and yesterday's line |
| 5 | Listen | Shows the new thing with objects or the board | Says it correctly, as often as needed |
| 8 | Say | Leads the class, then halves, then rows | Drill Master |
| 8 | Do | Pairs or groups work without the device | A tune, a timer |
| 8 | Play | A class game by rows | Class Games, or a round on the loudspeaker |
| 3 | Goodbye | Five questions, hands up | Quick Check counts who knows |

Between class sessions, children take turns at the device alone or in pairs
(the Station Timer rotates groups) and play the rounds of the unit that was
taught.

## 4. What the teacher is given

For every subject and level:

- **A guide** (`content/guide/<subject>-<level>/`): a chapter for every unit
  with the goal, what the teacher herself must know, how to explain it with
  things in the room, figures, a worked example, common mistakes and what to
  do, class activities for 50 children, the games that practise it, and how
  to check. Read and heard on the device; printed with
  `tools/guide_book.py`.
- **Lessons** (`content/teacher/…`), the six-step class session above,
  written out line by line, for subjects where the device must speak for the
  teacher. English first; the same form serves Dari, math and health.
- **Phrase Board, Drill Master, Class Games, Story Time, Station Timer,
  Quick Check, Tonight's Preview, teaching tips**: see `teacher-mode.md`.

## 5. English: zero to simple conversation

| Level | Theme | At the end a child can | New words | Status |
| --- | --- | --- | --- | --- |
| 1 | Hello | greet, say name and age, follow 15 commands, count to 10, name colours | 80 | written |
| 1 add-on | Letters | name and sound all 26 letters, both forms, spell short words | | written |
| 2 | My world | talk about family, body, food, animals; have, like; count to 20 | 120 | written |
| 3 | My day | describe her day, tell the time, days, home, clothes; count to 100; do/does | 200 | written |
| 3 add-on | Story book | read 16 short stories | | written |
| 4 | At the bazaar | buy and sell, prices, quantities, polite questions; can, some/any | 250 | written |
| 5 | Health and help | say what hurts, follow clinic instructions, give directions, weather, yesterday; past simple, must/should | 250 | written |
| 6 | The wider world | jobs and plans, tell a story, compare, build a short message; going to, comparatives, because | 300 | written |

## 6. Dari reading: sounds to fluent reading

| Level | Focus | At the end a child can | Status |
| --- | --- | --- | --- |
| 1 | Sounds and first letters | hear first and last sounds, rhyme, know 12 frequent letters | written |
| 1 add-on | The whole alphabet | name, sound and order all 32 letters; tell look-alikes apart | written |
| 2 | Every letter in every position | read letters at the start, middle, end; short vowels | written |
| 3 | Syllables and words | join letters, read 150 common words | written |
| 3 add-on | Story book | read 16 stories with questions | written |
| 4 | Sentences | read and understand simple sentences with punctuation | written |
| 5 | Stories | read a story alone and answer what, why, what would you do | written |
| 6 | Fluent reader | read information texts, proverbs, poems; sound-alike letters | written |

## 7. Math: tied to daily life

| Level | Numbers and operations | Measures and life | Status |
| --- | --- | --- | --- |
| 1 | count, read, compare 0–20 in both digit systems; add and take away with things | shapes, longer/shorter, more/less | written |
| 2 | numbers to 100, tens and ones, add and subtract within 20 fluently | time by the hour, coins and notes | written |
| 2 add-on | Logic puzzles | patterns, order from clues, grids, thinking stories | written |
| 3 | to 1,000, carrying, tables of 2, 5, 10 | metres and centimetres, simple bills | written |
| 4 | all tables, division as sharing, halves, quarters, thirds | weight, volume, perimeter, calendar | written |
| 5 | large numbers, multi-digit multiplication, fractions, decimals through money | area, tables and charts | written |
| 6 | percent, ratio, averages | profit and loss, a household budget, scale on a map | planned |

## 8. Health and environment

| Level | Circle | Health | Environment | Status |
| --- | --- | --- | --- | --- |
| 1 | Me | handwashing, teeth, body, sleep | animals and plants, seasons | written |
| 2 | My home | food groups, safe water, latrine, cooking smoke, diarrhoea | water cycle, waste, trees | written |
| 2 add-on | Nature and how things work | senses | animals, plants, sky, weather, materials, light, sound, simple machines | written |
| 3 | My village | first aid, poisoning, when to seek help | | written |
| 3, rest | My village | germs and vaccines, common illnesses, staying safe outdoors | soil, crops, water sources, weather | planned |
| 4 | My future | growth, feelings, small children | drought and flood, energy, land and water | written |
| 4 add-ons | | children's rights; the world, Switzerland and Basel | | written |

"Growing up" for older girls and boys, and safety around dangerous objects
found outdoors, are left to the local team with specialist material, as the
spec says. Health content adds no medical advice beyond its fact sheets
(`SOURCES.md` in each pack), which a health professional must sign off.

## 9. Teacher material

| Material | Status |
| --- | --- |
| Lessons, English 1 and 2 (20 each) | written |
| Lessons, English 3–6 | planned |
| Lessons for Dari reading, math, health | planned |
| Guide format, reader on the device, print export | written |
| Guides: math 1–5, Dari 1–4, English 1–4, health 1–4 | written |
| Guides: English 5–6, Dari 5–6 | planned |

## 10. What an educator should decide first

- Whether the unit sequence of section 2 and the class session of section 3
  fit how the teachers actually work.
- The order of letters in Dari level 1 and of the English alphabet.
- Which national textbooks the levels should be aligned with, grade by
  grade (open question of the spec).
- Reading-speed targets, which the spec marks as placeholders.
- Everything in `review-notes.md`.

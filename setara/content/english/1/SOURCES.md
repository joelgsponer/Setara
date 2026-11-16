# English 1 "Hello": what version 2 adds, what was decided, what a human must check

Written by an AI (Claude). Nobody who speaks Dari, teaches English or knows
the villages has read or heard any of it yet. The unit-by-unit word list is
in [`syllabus.md`](syllabus.md) and did not change: unit N is still lesson N
of the teacher pack, and no `en` text of `items.csv` was touched.

## Why version 2

The owner played version 1 and asked for "more and more varied content, not
always the same questions". Version 1 had 65 rounds; 30 % of its spoken
questions were heard more than twice, and a replayed round was identical.
Version 2 has 123 rounds. Word Stall and Echo are as they were; eight new
games practise the same twenty units in other forms, and every new game but
the stories is a pool (`"draw"`): a play asks 6 or 8 items out of 12 to 24.

| Game | Engine | Rounds | Items | Draw | Form |
| --- | --- | --- | --- | --- | --- |
| Word Stall | listen_pick | 18 | 82 | - | unchanged, from `items.csv` |
| Echo | say_it | 20 | 170 | - | unchanged, from `items.csv` |
| Sound Catcher | catch | 6 | 12 | - | unchanged |
| Sentence Train | builder | 19 (was 10) | 151 (was 44) | 6 | a round for every unit with a sentence pattern; 05 and 06 share the number-order round 06 |
| Shopkeeper | market | 4 | 20 | - | unchanged |
| Radio Stories | story | 2 | 16 pages | - | unchanged |
| Number Stall | listen_pick | 5 | 40 | - | same answers; the counting rows now say "Count the apples." and round 06b "The number three." instead of the bare number a third and fourth time |
| **Yes or No** | listen_pick | 9 | 166 | 8 | a picture and a question: Is this a book? Three red pens. Yes or no? |
| **Which One Is Missing?** | listen_pick | 8 | 120 | 8 | three words are said, four pictures shown: pick the one NOT said |
| **Listen and Find** | listen_pick | 5 | 75 | 8 | a red book; three red apples; What colour is the pen? How many red pens? |
| **Baskets** | sorter | 4 | 64 | 8 | colour baskets; food / classroom things / people; he / she |
| **Catch It** | catch | 5 | 63 | 6 | catch a number, a classroom thing, a colour, a food |
| **Question and Answer** | listen_pick | 7 | 100 | 8 | a two-voice dialogue: does the reply fit the question? yes / no |
| **Memory** | pairs | 7 | 95 | 6 | spoken card to picture; numeral to counted things; opposites |
| **Mini Stories** | story | 4 | 25 pages | - | each page in Dari first, then in English; 9 decisions |

Every unit is practised by at least four forms besides Word Stall and Echo
(the table is in the hand-over report of this change; the lowest are units
03, 07 and 10 with four).

## Decisions taken

- **Question and Answer for children who cannot read.** The answers cannot
  be shown as pictures ("My name is Sara") and cannot be written. So the
  child hears question and reply in two voices and judges: does it fit? The
  wrong replies answer another question ("How old are you?" / "My name is
  Sara."). They never contain wrong English.
- **Which One Is Missing replaces a visual "what is missing".** The engine
  shows one thing in the middle, not a row of things, so the missing thing is
  the one not *said*. The child has to know all three spoken words.
- **No Odd One Out and no Riddles in level 1.** Level 1 has no category
  words (animal, fruit) and no "has / likes". Both games are in level 2.
- **The "?" card.** Which One Is Missing and Question and Answer show a "?"
  in the middle. Without it the app's new look-and-listen screen would
  present the answer picture together with the question's words before the
  round, which here would teach the wrong thing.
- **Wording varies on purpose**: "Is this a book?", "Is it a book?", "This is
  a book. Yes or no?", "A book? Yes or no?"; in Memory and Baskets a word
  comes as "A book.", "Look! A book.", "Point to the book." A script counted
  every spoken English text of the pack: no text written for version 2 is
  heard more than twice. What is still heard more often is old: words that
  are in Word Stall, in Echo and again as a review row of a later unit.
- **Yes and no are each right half the time**; that is the form, not a bias.
- **Coloured things** (11 new pictures) are recoloured copies of the plain
  picture. The plain book is red, the plain pen blue, the plain pencil
  yellow, the plain bag brown: "a red book" is the plain book.
- **Pictures that show one another are never offered against each other**
  (the class picture has girls in it, the classroom picture a board and a
  window, the teacher picture a board).
- **Mini stories** reuse scenes of the shared library drawn for other packs.
  New invented names: Nadia, Shirin (girls), Yusuf, Jawad (boys). Two
  stories are told by a girl, two by a boy.
- **Words met slightly early, always with Dari first or on Y**: "people" and
  "food" as basket names, "How many ...?" in Listen and Find round 20 (it is
  taught in level 2), "Count the ..." in Number Stall rounds 05 and 06 (unit
  15), plural "-s" before unit 17 (as version 1 already did).
- The sheets were written by a generator script kept outside the repository;
  the CSVs are the source from now on and can be edited by hand.

## For the human reviewer

- **Dari of every new text**: the round introductions, the Y help of each
  row, the story pages. English twins are in `content/i18n/english12.csv`.
- «جور است» for "fits" (جواب به سوال جور است؟): the right everyday word?
- «او، برای پسر یا مرد» / «او، برای دختر یا زن» name the he and she baskets.
- Baskets round 14 sorts by "he" and "she" heard in a sentence; the pictures
  are single children from the command pictures. Check that each is clearly
  a boy or a girl to local eyes.
- Question and Answer: is judging a reply too abstract for six-year-olds?
  Try it with real children first; it is the least proven new form.
- Which One Is Missing asks the child to hold three words in mind. It may
  suit the older children only.
- Story 16 uses a scene drawn as "a boy gives bread to his sister"; here the
  girl is called his friend's name only (Nadia). Acceptable?
- Listen to the two-voice dialogues and the three-word lists ("book. pen.
  bag."): the pauses depend on the voice.

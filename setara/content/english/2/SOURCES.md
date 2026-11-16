# English 2 "My world": what version 2 adds, what was decided, what a human must check

Written by an AI (Claude). Nobody who speaks Dari, teaches English or knows
the villages has read or heard any of it yet. The unit-by-unit word list is
in [`syllabus.md`](syllabus.md) and did not change: unit N is still lesson N
of the teacher pack, and no `en` text of `items.csv` was touched.

## Why version 2

The owner asked for "more and more varied content, not always the same
questions". Version 1 had 67 rounds; 22 % of its spoken questions were heard
more than twice, and a replayed round was identical. Version 2 has 129
rounds. Word Stall and Echo are as they were; nine new games practise the
same twenty units in other forms, and every new game but the stories is a
pool (`"draw"`): a play asks 6 or 8 items out of 12 to 24.

| Game | Engine | Rounds | Items | Draw | Form |
| --- | --- | --- | --- | --- | --- |
| Word Stall | listen_pick | 20 | 111 | - | unchanged, from `items.csv` |
| Echo | say_it | 20 | 200 | - | unchanged, from `items.csv` |
| Sound Catcher | catch | 6 | 15 | - | unchanged |
| Sentence Train | builder | 19 (was 10) | 156 (was 49) | 6 | a round for every unit; 06 and 07 share the number-order round 07 |
| Shopkeeper | market | 4 | 20 | - | unchanged |
| Radio Stories | story | 2 | 16 pages | - | unchanged |
| Number Stall | listen_pick | 5 | 44 | - | same answers; the counting rows now say "Count the eggs." and round 07b "The number thirteen." |
| **Yes or No** | listen_pick | 9 | 198 | 8 | a picture and a question: Is this a goat? I have two keys. Yes or no? |
| **Odd One Out** | listen_pick | 6 | 92 | 8 | "goat. cow. key. hen. Which one is not an animal?" |
| **Riddles** | listen_pick | 6 | 87 | 8 | "I am an animal. I have milk. I am not a cow. I am not a sheep." |
| **Listen and Find** | listen_pick | 5 | 80 | 8 | a blue ball; thirteen flowers (against three); two goats; What colour is the tree? |
| **Baskets** | sorter | 5 | 87 | 8 | family / things; fruit / vegetables; animals / food / family; four baskets; at home / in the village |
| **Catch It** | catch | 5 | 72 | 6 | parts of the body; food; fruit or vegetables; animals (big, small, babies); things at home |
| **Question and Answer** | listen_pick | 5 | 80 | 8 | a two-voice dialogue, three rounds with a picture: is the answer right? |
| **Memory** | pairs | 7 | 111 | 6 | spoken card to picture; numeral 11 to 20 to counted things; partners (sheep and lamb) |
| **Mini Stories** | story | 5 | 30 pages | - | each page in Dari first, then in English; 10 decisions |

Every unit is practised by at least three forms besides Word Stall and Echo
(unit 10, a review unit without new words, has three; unit 20 has five; all
others six or more).

## Decisions taken

- **Riddles use only taught language**: colours and big / small from level
  1, "I have", "I like", "I am", "is not", numbers, the category words food,
  fruit, vegetable, animal, family. Three wrong pictures are written out for
  every riddle so that exactly one fits (no yoghurt, rice or sugar beside
  "It is white. Babies and cats like it."). Untaught but needed, always with
  the Dari on Y: "mother's mother", "from", "many", "very", "or", "no legs",
  "Good night".
- **Odd One Out names the group in English** ("Which one is not a fruit?")
  and says all four words. The app shows two to four choices depending on how
  the child is doing; with the group named the question is fair even with
  two pictures.
- **Question and Answer for children who cannot read**: the reply is spoken
  and judged with yes or no. With a picture (rounds 01, 08, 14) the answer
  must be true of the picture; without (13, 20) it must fit the question.
- **The "?" card** in Odd One Out, Riddles and Question and Answer keeps the
  app's look-and-listen screen from showing a riddle's answer before the
  round.
- **Pictures that show one another are never offered against each other**:
  mother (holds a baby) and baby, parents and mother or father, sister and
  brother, head and the parts of the face, hand / finger / arm, leg and
  foot, bed and pillow or blanket, well and bucket, sun / field / river /
  mountain, moon and star, rice / sugar / yoghurt, orange and apricot, an
  animal and its young (except where "baby animals" is the rule itself).
- **Numbers that sound alike** are the wrong choices in Listen and Find 08
  and Question and Answer 08: thirteen against three, fifteen against five.
- **Wording varies on purpose**; a script counted every spoken English text:
  no text written for version 2 is heard more than twice. What is still
  heard more often is old (a word in Word Stall, Echo and a review row).
- **Yes and no are each right half the time**; that is the form.
- **Five recoloured pictures** (three balls, two flowers) and four basket
  labels made of three library pictures each.
- **Mini stories** reuse library scenes. Invented names: Hamid, Navid
  (boys), Laila, Mariam, Soraya (girls). Three are told by a girl, two by a
  boy.
- Irregular plurals are heard, not taught: feet (taught in unit 05), leaves,
  teeth is avoided ("Catch the tooth."), mice is avoided.
- The sheets were written by a generator script kept outside the repository;
  the CSVs are the source from now on and can be edited by hand.

## For the human reviewer

- **Dari of every new text**; English twins are in
  `content/i18n/english12.csv`.
- **Riddle facts** depend on local life: cats like milk and fish, a dog
  likes meat, a hen likes corn, cows and sheep like the field, "I have water
  from it. I have a bucket and a rope" (the well), the camel as "a big
  animal that is not a horse, cow or donkey". Replace what does not hold.
- Riddle Dari: «من مادرِ مادر تو هستم», «من مثل یک کوه خُرد هستم» (the stone).
- "Which one is not food?" counts milk as food and leaves tea and water out.
- Baskets 19 sorts "at home" and "in the village"; the village basket is the
  scene picture of a village. Is a bucket or a basket "at home" for
  everybody?
- Baskets 02 uses the box picture for the basket "things".
- Body words: «لنگ» (leg), «پای» (foot), «بازو» (arm), as in version 1.
- Story 16 says Navid has three sheep (the scene shows three); story 19 lets
  the goat walk out of an open door; story 10 has a boy carry the bread his
  mother baked to grandfather and sister.
- Is judging a reply (Question and Answer) too abstract for the youngest?
- Listen to the four-word lists and the riddles: pauses and stress depend
  on the voice.

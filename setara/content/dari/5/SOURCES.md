# Dari reading 5: Stories (`fa-5`)

**Nobody who speaks Dari has read or heard this pack.** It was written by an
AI (Claude). Every text needs a Dari-speaking educator before a child sees
it. The English of every text, paragraph for paragraph, is in
`content/i18n/dari5.csv`; `syllabus.md` in this folder gives every story
with its key words, questions and games, for the teacher guide.

## What the pack teaches

Curriculum, level 5: *read a short story alone and answer questions about
it*. Twenty stories of 166 to 246 Dari words (3,900 words in all), each one
a unit. A unit is a fixed sequence, spread over three games that carry the
unit's number as their round number (unit 07 is round 07 of its story game,
of Story Builder and of one more game):

1. **Before reading** (story round): the title picture and a question that
   makes the child curious; then three key words, each with a picture and a
   spoken meaning in one or two sentences.
2. **Read** (story round): four or five reading pages (text only, the whole
   screen, 4 to 7 lines).
3. **Understand** (story round): a question after each passage: who / what /
   where first, then why (21 of 85 questions), at the end of 18 stories "what
   would you do?".
4. **Work with the words**: Story Builder, and one of Story Baskets, Word
   Pairs or The Missing Word.
5. **Review**: Which Story? after units 5, 10, 15 and 20.

| Game | Engine | Rounds | What the child does |
| --- | --- | --- | --- |
| Animal Fables (`a`) | story | 01-07 | seven fables, about 170 to 190 words |
| Village Stories (`b`) | story | 08-14 | seven original stories of village children, about 165 to 195 words |
| Old Tales (`c`) | story | 15-20 | six longer tales, about 215 to 245 words, five reading pages |
| Story Builder (`d`) | builder | 01-20 | puts four or five event words in the order of the story; builds three heard sentences and two answers to questions from word tiles (one tile often does not belong) |
| Story Baskets (`e`) | sorter | 01 04 07 10 13 16 19 | who did it (two characters); in the story / not in the story; which season; dreamed / really happened |
| Word Pairs (`f`) | pairs | 02 05 08 11 14 17 20 | word and picture; opposites (twice); one and many (twice); same meaning; strong, stronger |
| The Missing Word (`g`) | listen_pick | 03 06 09 12 15 18 | hears a sentence whose last word is missing and picks it among words that look alike; riddles ("I am black and say caw"); opposite; same meaning |
| Which Story? (`h`) | listen_pick | 05 10 15 20 | "in which story …", "which story says …", who, which thing: answers are pictures |

Every game except the stories is a pool (`"draw"`): each play asks 8 (builder
and pairs: 5) of the 9 to 14 items of the round, in a new order.

## How `say_fa` is used on reading pages (the pause)

The story engine speaks a page the moment it appears; a sheet cannot ask for
silence first. So on every reading page of this pack the spoken text
(`say_fa`) is **a reading purpose followed by the page**: "بخوان و ببین:
مورچه چرا به کنار جوی رفت؟" and then the paragraph exactly as shown
(`show_fa`). The child sees the whole page from the first moment, hears what
to look for, and has those two or three seconds to start reading alone; then
the voice reads the page and carries a weak reader. A strong reader presses
A, which cuts the voice and turns the page; X reads the page again. The
purpose question is different on all 86 pages and is usually answered by the
question that follows the page. If a real silent pause is wanted (say five
seconds per line), that is a small change to the story engine, not to the
sheets; it was not made because this job may not touch code.

Key-word pages speak the word and then its meaning. Questions are spoken as
written. A wrong answer is never called wrong: the guide gives the passage
that holds the answer. On "what would you do?" questions every hint begins
with «هر کس فکر خود را دارد» ("everyone has their own thoughts") and then
says what the character in the story did. The engine needs one right choice
on such a page too; the "right" one is the choice the story itself shows,
and the wrong ones are ordinary reactions (I would be angry, I would sleep),
not bad deeds.

## Where every story comes from

Nothing was copied or translated from a modern book, website or published
translation. The traditional tales are old and in the public domain; they
are retold from the bare plot in new words. None of them is among the tales
already told in `dari/3-stories` and `english/3-stories` (thirsty crow, fox
and stork, tortoise and hare, doves and net, lion and mouse, fox and grapes,
wind and sun, two goats, turnip, stone soup, elephant in the dark, the
Nasruddin tales).

| Unit | Story | Source |
| --- | --- | --- |
| 01 | مورچه و کبوتر, The ant and the dove | Aesop. The bird-catcher only loses his net. |
| 02 | سگ و استخوان, The dog and the bone | Aesop (The Dog and His Reflection). The butcher who gives the bone is added. |
| 03 | زاغ و روباه, The crow and the fox | Aesop; also in Dari school readers. New wording. |
| 04 | مورچه و ملخ, The ant and the grasshopper | Aesop. **Ending changed:** the ant shares her grain; the grasshopper promises to work next summer and sings for her in winter. |
| 05 | موش شهر و موش قریه, The town mouse and the village mouse | Aesop, with local food (dried mulberries, chickpeas, biscuits, jam). |
| 06 | موش‌ها و زنگوله, The mice and the bell | Belling the Cat, a medieval fable in the Aesop tradition. **Added ending:** the mice dig a hole too narrow for the cat, a plan they can carry out. |
| 07 | زاغ و پَرهای طاووس, The crow and the peacock's feathers | Aesop (The Jackdaw and the Peacocks). **Added ending:** an old crow tells the young one that her wings are strong. |
| 08 | کوزه شکسته, The broken jug | Original. |
| 09 | سنگ‌های جوی, The stones in the stream | Original. |
| 10 | خط برای بی‌بی, A letter for Grandmother | Original. |
| 11 | مترسک, The scarecrow | Original. |
| 12 | کبوتر یاسین, Yasin's dove | Original. |
| 13 | نان سال آینده, Next year's bread | Original, on the farming rule of keeping the seed grain. |
| 14 | صدای ثریا, Soraya's voice | Original. |
| 15 | دسته چوب, The bundle of sticks | Aesop. The father and sons are a grandmother and three grandchildren. |
| 16 | گلالی و دیگ ماست, Gulalai and the pot of yoghurt | The daydreamer with the pot (Kalila wa Dimna / Panchatantra; in Europe the milkmaid and her pail). **Added:** the mother's advice and a second, careful trip that ends with two chicks. |
| 17 | گنج در باغ انگور, The treasure in the vineyard | Aesop (The Farmer and His Sons). **Changed:** the farmer is old, not dying; a daughter and two sons; the daughter understands. |
| 18 | دختر دانا, The wise girl | Folk-tale type of the clever peasant girl and the ruler's riddles (Asia and Europe). The marriage ending is left out. |
| 19 | خر و بار نمک, The donkey and the load of salt | Aesop (The Salt Merchant and His Donkey). Sponges became wool; a boy looks after the donkey kindly. |
| 20 | موش و قوی‌ترین چیز دنیا, The mouse and the strongest thing | The chain tale of the mouse and the strongest (Kalila wa Dimna / Panchatantra, the mouse-maiden). The marriage frame is left out. |

**Girls and boys.** Human heroes: Zarmina, Nadia (with her brother Karim),
Parwin, Soraya (with Laila), Gulalai, Shabnam, Zohra, and the smallest
grandchild Hila who gives the answer / Karim, Omid (with his sister Mina),
Yasin, Farid, Bashir, Nasim, Hamid. Girls build a stepping-stone bridge,
answer a king and teach a grandmother to read; boys nurse a bird and are
kind to a donkey. Among the animals the ant, the dove, the crow, the
village mouse, the old mouse and the mountain mouse are "she" in the
English; Dari has no gender in the pronoun. The names are common first
names, not real people.

## Decisions taken

- **Homographs and the synthetic voice.** Words a voice could misread carry
  a vowel mark, also on the page, as in the earlier packs: خُرد، پُر، پُل،
  دُم، پَر (feather), مَرد، گِل، تَر، کَند / کَندن (dug), می‌بُرد (carried),
  می‌بَرد (carries), بُرد. Avoided altogether: «نه» (no: «نخیر» is used),
  «ده» (ten / village: the stories say «قریه», and "ten days" became seven),
  «در» for door («دروازه»), «کی» for who («چه کسی»), «گرد». «شیر» occurs
  only as milk; «سر», «بار», «خر», «سیر» occur in their usual meaning. A
  script checks every spoken text for the bare forms.
- **Answer cards are measured.** A card holds one line. Every written card
  was measured in the bold face against the width its engine really gives
  it (story 150 px, sorter 170 px, builder tile 116 px, picking games
  120 px, pairs 122 px) so that it is drawn at 30 px. That is why answers
  are one to three short words, and why Story Baskets show short phrases
  ("در آب افتاد") rather than full sentences.
- **Story Baskets speak the card**, The Missing Word and Which Story? speak
  the question, Word Pairs speak the pair when it is found. Answer cards in
  The Missing Word are not read aloud (`read_choices` is off): reading them
  is the exercise. The wrong words there are real words that look alike
  (گرفت among گفت، رفت، گشت).
- **A gap is spoken as a sentence that stops.** "زاغ بالای شاخه بلند یک
  درخت…": Dari puts the verb last, so the missing word is always the last
  one and the voice simply stops before it.
- **Ezafe is not written**, as in levels 2 to 4, except بی‌بی «مادرِ پدر».
- **Words kept from the earlier packs:** قریه، جوی، دریا (river), کلان، خُرد،
  پشک، مکتب، صنف، معلم، حویلی، دروازه، چوچه، گپ، بوت، کلچه، پیسه، بی‌بی.
- The sheets were written out by a script from the story texts, so that
  every Dari text carries its English and every width is checked; the CSV
  files are the source from now on.
- **Pictures:** 25 new ones (`pictures.txt`): 20 title scenes and the
  things crow, grasshopper, king, letter, scarecrow. The scenes are composed
  from library pictures and newly drawn figures. Everything else (about 75
  pictures) is from the library.

## What a Dari-speaking educator must decide

1. **Read every story aloud.** The aim was simple written Afghan Dari.
   Words and turns I am least sure of: «دوش کردند» (ran a race), «ترق» /
   «ترپ» / «جرنگ» (sounds), «چک‌چک کردند» (clapped), «نول» (beak), «جال»
   (net), «صفت می‌کند» (praises), «قات می‌کنیم» (bend), «تیر شد» (passed,
   crossed), «خیز زد» (jumped), «شور نمی‌خورد» (does not move), «ایلا
   می‌کنم» (I give up), «راه می‌پالم» (I look for a way), «بند بمانند» (get
   stuck), «افگار» (hurt), «آبله کرد» (blistered), «پُف», «مانده» (tired),
   «قصداً» (on purpose), «نفس‌زنان», «دامنه کوه», «بازی داده است» (has
   tricked), «نواسه», «کاکا», «بزگر» and «سخن» (as plain synonyms in Word
   Pairs), «یاری», «قوت», «هوشیار», «یکباره», «زخمی», «جرأت», «ختم».
2. **Verb forms:** «کرده نمی‌تواند», «خوانده نمی‌توانست», «رفته
   نمی‌توانم», «می‌داشته باشم», «می‌بودم / می‌بودی» are the colloquial
   Afghan forms; the school books may want others.
3. **"What would you do?"** has one choice that continues the story. Is the
   hint gentle enough, and are the other two choices harmless? Two
   stories have no such question because none fitted (05 and 20; they ask
   what the character understood).
4. **Changed endings** (04, 06, 07, 16, 17): the old fables end with a
   loser; here somebody learns and nobody is left hungry or mocked. Say if
   the traditional endings are wanted.
5. **The king** in The wise girl is a fairy-tale king («بود نبود، یک
   پادشاه بود»); the picture shows a crown. Replace him by a rich
   merchant if a king is not wanted.
6. **A man with a net** comes for the dove (01) and only loses his net; a
   cat frightens the mice (05, 06); a girl breaks a jug and is not punished
   (08); a family is hungry in winter (13); a dove's wing hurts (12).
   Nothing worse happens in the pack.
7. **Uncle Rahim works in a far town** (10) and a grandmother cannot read
   and learns from her granddaughter. Acceptable everywhere?
8. **Level.** A page has 30 to 60 words; the purpose question before each
   page and the voice after it are meant for the reader who is not yet
   fluent. Reading speed (about 60 words a minute in the curriculum) is not
   measured anywhere.
9. **One and many:** «دوستان», «مادران», «فرزندان», «درختان» next to
   «ها» plurals. «چشم‌ها», «دست‌ها». Right for this level?

## What nobody has checked

- **Speech.** No clip has been heard; the pack was built with silent speech
  only. Risks: a sentence that stops before its last word (The Missing
  Word); the sounds «قار قار», «ترق», «جرنگ»; a reading purpose and a
  paragraph in one clip of 30 to 40 seconds.
- **Children.** Whether 4 to 7 lines of 30 px Dari are comfortable on the
  3.5 inch screen has only been judged from screenshots.
- **Pictures of people** (girls, boys, a father, a grandmother, a king)
  need the local reviewer. Weakest pictures: `scene_dog_bridge` (the
  reflection is a pale upside-down dog), `scene_yoghurt_girl` (the pot hides
  the headscarf), `scene_wise_girl` (the king is head and shoulders on a
  seat), `scene_mice_bell` (the cat is small), `king`.
- **Library pictures used for a new meaning:** `feather` for wing, `scarf`
  for a shawl, `happy` for a smile, `tease` for a quarrel, `sleep` for a
  daydream, `coin` for treasure, `grapes` for a vine, `street` for town,
  `seed` for a grain, `water_stream` for a spring, `firewood` for a bundle,
  `puz_small_star_yellow` for a riddle, `give` for generous, `yes` / `no`
  and `sleep` as baskets.

## Counts (from a script over the sheets)

| Game | Engine | Rounds | Items | Items per round | draw | Most frequent right answer | Answers right more than 3 times |
| --- | --- | --- | --- | --- | --- | --- | --- |
| animal_fables | story | 7 | 84 | 12-12 | - | f:در آب ×1 | none |
| village_stories | story | 7 | 85 | 12-13 | - | f:از چشمه ×1 | none |
| old_tales | story | 6 | 83 | 13-14 | - | f:جنجال ×1 | none |
| story_builder | builder | 20 | 120 | 6-6 | 5 | f:تشنگی|f:برگ|f:جال|f:پرواز ×1 | none |
| story_baskets | sorter | 7 | 81 | 11-12 | 8 | yes ×18 | (baskets) |
| word_pairs | pairs | 7 | 64 | 9-10 | 5 | bone ×1 | none |
| missing_word | listen_pick | 6 | 62 | 10-12 | 8 | f:بود ×3 | none |
| story_review | listen_pick | 4 | 56 | 14-14 | 8 | scene_ant_dove ×2 | none |

Total: 8 games, 64 rounds, 635 rows. Distinct spoken texts: 635; spoken more than twice: 0; spoken exactly twice: 0.


In sorter games the "answer" is a basket, so a basket is right many times by
design. In `missing_word` «بود» is the right last word three times.

**Card sizes, measured and then seen.** Of 1,231 written cards, 64 are within
a tenth of the width their card allows at 30 px. The widths were computed
from the font tables; on the screenshots a few of these near-limit cards
(for example two-word answers with a comma) were drawn one step smaller, at
24 px, below the project's 30 px rule for Dari. They are readable but should
be shortened or accepted by the reviewer.


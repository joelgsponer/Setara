# Dari reading 4: Sentences (`fa-4`)

**Nobody who speaks Dari has read or heard this pack.** It was written by an
AI (Claude). Every sentence needs a Dari-speaking educator before a child
sees it. The English of every text is in `content/i18n/dari4.csv`.

## Version 2: more variety (read this first)

Version 2 answers one complaint: the same questions came back. The sections
below describe version 1 unless they say otherwise. **Still nobody who speaks
Dari has read or heard this pack**, and version 2 adds about 150 new items
that need the same review.

**Size**: 10 games, 56 rounds, 531 items (version 1: 7 games, 50 rounds, 383
rows). How it was counted: a script reads `items.csv` and every sheet and counts each spoken prompt (`say_fa` + `say_en`, for derived games the word itself) over the whole pack; "more than twice" counts the items whose prompt occurs three times or more.

| Game | Rounds v1 → v2 | Items v1 → v2 | Draw | Prompts heard more than twice, v1 → v2 |
| --- | --- | --- | --- | --- |
| action_words | 4 → 4 | 32 → 48 | 8 | 27 → 0 |
| read_and_choose | 8 → 8 | 64 → 64 | - | 64 → 0 |
| sentence_weaver | 10 → 10 | 60 → 100 | 8 | 0 → 0 |
| sentence_baskets | 8 → 8 | 65 → 97 | 8 | 49 → 0 |
| who_what_where | 6 → 6 | 48 → 48 | - | 0 → 0 |
| word_catch | 4 → 4 | 24 → 24 | - | 0 → 0 |
| read_along | 10 → 10 | 90 → 90 | - | 0 → 0 |
| fits_or_not | - → 2 | - → 20 | - | - → 0 |
| story_order | - → 2 | - → 16 | - | - → 0 |
| complete_sentence | - → 2 | - → 24 | 8 | - → 0 |

Whole pack: 140 of 383 items had a prompt that is heard more than twice (five
fixed instructions: "Read the sentence. Which picture is right?" 64 times,
"Read. Which basket does it go in?" 33 times, and three more); now 0 of 531.

What was done, and what that number hides:

- **The fixed instruction is worded differently each time.** In this pack
  the sentence must not be read aloud, so in Read and Choose, Sentence
  Baskets 3 to 8 and Action Words the voice can only give an instruction.
  It is now put together from ten openings and several endings ("Read it
  word by word. Which picture goes with it?"). **This is a change of wording
  only**: in those 180 items the task is the same as before. The real
  variety is in the new forms and the pools.
- **Three new games in new forms**:
  - Fits or Not? (`i`, story engine; 20): a picture and one written
    sentence; the child reads and answers yes or no; after a wrong answer
    the guide says why ("The fish is in the water, not in the tree.").
  - First, Then, Last (`j`, story engine; 16): a story of three short
    sentences is read, and one question asks what came first, next or last
    ("What did Laila do first?"); the answer is a picture. The engine cannot
    show sentences as tiles at 30 px, so the story is not put in order by
    hand; the child shows that she has kept the order.
  - Finish the Sentence (`f`, journey; 24): the sentence is spoken without
    its last word; the child reads four look-alike words. Round 01 is one
    or many (می‌رود / می‌روند), round 02 is opposites (گرم، خرد، تاریک ...).
- **Pools.** Action Words, Sentence Weaver, Sentence Baskets and Finish the
  Sentence are pools (`"draw"`): 10 to 13 items a round, eight asked each
  play. The story games cannot be pools.
- **New material**: 40 sentences to build, 32 to sort, 16 verbs asked both
  ways (new: می‌کشد، می‌وزد، می‌جوشد، می‌روید، می‌دوزد), 24 cloze sentences. No new
  pictures.
- **Story-question cards**: all written answers in the story games were
  measured again; none is drawn below 30 px.

For the reviewer (version 2):

1. Finish the Sentence: the voice says the sentence up to the missing word
   («کلمه آخر این جمله کدام است؟ لیلا و زهرا به مکتب»). A voice may let this
   sound odd; nobody has heard it. Plural subjects of animals take a plural
   verb here (مرغ‌ها دانه می‌خورند، گاوها علف می‌خورند); the stories of version 1
   use a singular verb for things (برگ‌ها می‌ریزد). Consistent enough?
2. Opposites in round 02: سخت / نرم، روشن / تاریک، تر / خشک، نو / کهنه، تیز /
   آهسته. The wrong words include دود، آمده، آینده.
3. First, Then, Last: «مادر آرد را خمیر کرد», «پشک توپ را پایین انداخت»,
   «از تخم چوچه برآمد», «چوپان رمه را به خانه آورد» ("flock" is answered
   with the picture of a sheep).
4. Fits or Not?: true sentences and false ones are ten each; the false ones
   are plainly false (a fish in a tree), not near misses.
5. New sorter sentences: «نمک شور است», «شیر سیاه است» (not true; شیر is
   milk here), «آتش تر است», «کالای گرم» (winter; not a sentence), «خروس
   خواند» (day), «چراغ می‌سوزد» (night), «گوساله دارد», «چوچه دارد», «تر است»
   (fish).
6. Fits or Not? has only the answers yes and no, ten each; that is the form.

Checked for version 2: `validate --only fa-4` ok, 0 warnings, 0 untranslated
lines (448 English lines added to `i18n/dari4.csv`); silent build ok;
`tests/fuzz_rounds.lua` on the scratch build ends "fuzz ok"; screenshots of
the three new games, a sorter round and an Action Words round looked at; all
new tiles, sorter cards and choice cards measured at 30 px or more. Not
checked: audio, a real handheld, children.

## What the pack teaches

Curriculum, level 4: *read simple sentences with punctuation and understand
them*. Level 3 (syllables and 150 sight words) was being written at the same
time; this pack does not depend on it and only assumes the child can read
common concrete words.

In this pack reading is the exercise. Where the written sentence is the
task, the voice gives the instruction ("Read the sentence. Which picture is
right?") and does **not** read the sentence. A child who is stuck still gets
help: a wrong choice makes the guide read the sentence aloud, and Y in Action
Words says the word.

| Game | Engine | Rounds | What the child does |
| --- | --- | --- | --- |
| Action Words (`a`) | listen_pick | 4 | Verbs, which level 2 did not have. Rounds 1 and 3: see a picture, pick the written verb among look-alikes (می‌خوابد، می‌خواند، می‌خورد، می‌خندد). Rounds 2 and 4: read a verb, pick the picture |
| Read and Choose (`g`) | story | 8 | Reads one sentence, picks the picture. From "the cow gives milk" over two-word decisions ("the pen is red": red pen, blue pen, red apple) to riddles that do not name the thing ("we write with it") |
| Sentence Weaver (`c`) | builder | 10 | Hears a sentence and builds it from word tiles, right to left. 3 to 5 words, later with tiles that do not belong. Rounds 7 and 10: the last tile exists twice, with a full stop and with a question mark |
| Sentence Baskets (`b`) | sorter | 8 | Sorts short written sentences: question mark or full stop (1, 2), true or not true (3, 4), winter or summer, four seasons (5, 6), day or night (7), cow, hen or fish (8) |
| Who? What? Where? (`h`) | story | 6 | Reads a sentence and a question under it, picks the answer: who, what, where, a past-tense mix, how many (number words), two sentences |
| Word Catch (`d`) | catch | 4 | Hears a question and catches the written answer among words that look alike (نان among نام، بام، جان) |
| Read Along (`e`) | story | 10 | Ten stories of six or seven sentences, one sentence a page, with three questions each, one of them in the middle of the story |

50 rounds, 383 rows. Every round has 6 to 9 items.

## Decisions taken

- **Sentences are only shown where they can be drawn at 30 px.** A
  listen_pick `show` box and choice cards are about 120 px wide and draw one
  line: a sentence would shrink below the size the spec allows. So whole
  sentences appear in the story engine (wrapped text, as `show_fa` on a row
  without a picture, which gives the text the screen) and as word tiles in
  the builder. The sorter's centre card holds two or three short words at
  30 px; every sorter sentence was measured against it (at most 167 px in the
  bold face). Catch cards hold only very short words (at most 53 px), which
  limited the vocabulary there. All widths were measured with the font
  metrics and looked at in screenshots.
- **True / not true** is sorted against what every child knows ("ice is
  warm", "the donkey has wings"), not against a picture: the sorter shows one
  thing and fixed baskets, so a picture to compare with has no place.
- **Full stop or question mark** is taught three ways: sorter rounds 1 and 2
  (the sentence is spoken there, because the mark is the task, not the
  reading), the last tile in Sentence Weaver rounds 7 and 10, and by being
  seen in every sentence. Colon, comma and exclamation mark appear in the
  stories ("مادر می‌گوید: آفرین، دخترم!") but are not asked about.
- **The mark is part of the last word tile** in every Sentence Weaver item.
  A tile with only a full stop is a dot of a few pixels.
- **Story questions have no picture**, so that the picture cannot answer
  them; the question is read by the voice as in levels 1 and 2. In 9 of 30
  story questions the right choice is listed first; the app mixes the cards
  anyway.
- **Names**: لیلا، نرگس، زهرا، سارا، نسرین and فرید، نوید، علی، عمر، کریم, as in the
  earlier packs. Five stories have a girl in the middle, five a boy. Girls
  herd sheep and read to a brother, a father sweeps the house, a boy fetches
  water: tasks are not tied to one gender on purpose.
- **Kite flying was left out** of the stories although it is the obvious
  village game, because it is forbidden in places.
- **Ezafe is not written**, like level 2 (کلمه خروس).
- The sheets were written from one script so that every Dari text carries
  its English and every width is checked; the CSVs are the source from now
  on. Where another i18n file already had an English for the same Dari text,
  `dari4.csv` repeats that English instead of its own, so that it changes no
  other pack's captions.
- **Pictures**: 19 new ones (`pictures.txt` in this folder), drawn by
  composing library pictures with newly drawn figures. Everything else is
  from the library.

## What a Dari-speaking educator must decide

1. **Every sentence**: natural Afghan Dari for a village child? Doubtful
   ones: «باران بس می‌شود. آفتاب می‌برآید.», «برادر کوچکش هنوز خوانده
   نمی‌تواند.», «او رسم می‌کشد.», «این پرنده گپ می‌زند.», «دخترها سنگ‌بازی
   می‌کنند.», «مادر شیر را جوش می‌دهد.», «امروز مکتب رخصت است.», «همه خواب
   اند», «تو کجایی», «چند ساله‌ای», «دست‌هایش یخ می‌کند», «بره جان».
2. **Words**: دریا for river, بالاپوش for coat, کلینیک (as in the health
   packs), چهارمغز, کتابچه, بکس, چوچه مرغ, رمه, دکاندار, بخاری, تفریح (school
   break), «می‌پرد» used for "flies" in «گاو می‌پرد».
3. **Verb forms** are written with the half-space (می‌خواند). Is that what
   the school books show?
4. **Plural subjects with a singular verb** («برگ‌ها می‌ریزد», «توت‌ها
   می‌رسد», «دست‌ها پاک است») next to plural verbs for people and animals
   («درخت‌ها گل می‌کنند», «بچه‌ها ... می‌کنند»). Consistent enough?
5. **Wrong words in Action Words and Word Catch** are real words chosen
   because they look alike (می‌بازد، می‌تازد، می‌کوبد; خم، جر، بیخ، گاز، آه، کل).
   Any that are unknown to children, rude or unlucky should go. «تب»
   (fever), «درد» (pain), «زخم» (wound), «کور» (blind) are among them.
6. **True / not true**: is "آب تر است" a sensible true sentence? Is "گاو
   می‌پرد" clearly false, or does it read as "the cow jumps"?
7. **Seasons**: wheat and mulberries ripen "in summer", saplings are planted
   "in spring", ice and snow mean winter. Right for the regions the devices
   go to? "هوا سرد است" is sorted to winter and "هوا گرم است" to summer.
8. **Day or night**: "we go to school", "we play" are day; "we see stars",
   "everyone is asleep" are night.
9. **Cow, hen or fish**: "it lays eggs" is sorted to the hen although fish
   lay eggs too; "it has no legs" to the fish.
10. **Riddle sentences** in Read and Choose round 3 and 7 ("it has four legs
    and carries loads": donkey, with hen and fish as the wrong pictures).
    Clear for a child?
11. **Stories**: the new girl who knows nobody (story 3) and the lost lamb
    (story 8) are the only ones with a worry in them; both end well. The
    shop story has a girl and her little brother go to the shop alone and
    pay. Acceptable everywhere?
12. **Reading speed** (about 30 words a minute in the curriculum) is not
    measured anywhere in the pack.

## What nobody has checked

- **Speech.** No clip has been heard. The pack was built with silent speech
  only. Risks for the stand-in voice: sentences without their mark are
  spoken with it in sorter rounds 1 and 2 (the voice must make a question
  sound like one); «کی» (who) can be read as "when"; «شیر» (milk / lion),
  «گل» (flower / mud), «کل», «تر», «در», «سه»; the animal sounds «میو میو»,
  «بع، بع», «عوعو»; a sentence followed by "جمله را بساز." in one clip.
- **Children.** Whether 3 to 5 word tiles, falling words and the sorter's
  30 px sentences are readable on the real 3.5 inch screen has only been
  judged from screenshots on a PC.
- **Pictures of people** (girls, boys, a mother, a father on a roof and at a
  tree) need the local reviewer like every other picture of a person. The
  father's beard and cap, the girls' headscarves and the mother's dress
  follow the existing library. Weakest pictures: `scene_mulberry_shake`
  (busy), `scene_roof_snow` (the father's arms), `scene_boy_under_tree_rain`
  (small boy), the lamp in `scene_girl_reads_to_brother`.
- **Existing pictures used for a new meaning**: `happy` for "laughs", `look`
  for "sees", `count` for "counts", `go` for "goes", `say` for "says",
  `scene_laila_sad` for the quiet new girl, `scene_mother_calls` for the
  mother who is glad, `night` and `sun` as the baskets for night and day,
  `yes` and `no` as the baskets for true and not true. The full stop on its
  basket is a small dot.

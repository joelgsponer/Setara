# Dari 3: Syllables and words (`fa-3`)

Written by an AI (Claude). **No Dari speaker, teacher or child has seen or
heard any of it.** This file says what the pack teaches, what was decided
while writing it, and what a human reviewer has to decide.

## What it teaches

Curriculum, level 3: join letters into syllables and words, read 150 common
words on sight. The pack continues `fa-2` (the whole alphabet, short vowels,
first open syllables) and uses the same six Library games plus a journey.

In levels 1 and 2 the child answered by ear and by picture. From here on
**reading is the exercise**: the choices are written Dari words (`f:` things)
and are *not* read aloud (`read_choices` is off on purpose). Every question
and instruction is still spoken, and Y always gives spoken help.

| Game | Engine | Rounds | What the child does |
| --- | --- | --- | --- |
| Alefba Garden `a` | listen_pick | 16 | Odd rounds: hears a word, picks it among four written look-alikes (Y spells it with letter names). Even rounds: sees a written word, picks its picture (Y says the word) |
| Word Baskets `b` (id `letter_shapes`) | sorter | 11 | Sorts written words by first letter (1-4, word spoken), by number of syllables (5-7, word spoken), by word family (8-11, word **not** spoken: she has to read it) |
| Word Weaver `c` | builder | 10 | Builds words from letters (1-4), then from syllables: open syllables (5), closed second syllable (6), short vowels with marks (7), two closed syllables (8-9), three syllables (10) |
| Syllable Catch `d` | catch | 6 | Catches the first syllable (1) or last syllable (2) of a spoken word, a spoken word among look-alikes (3, 6), words that begin with the same syllable (4), words of one family (5) |
| Read Along `e` | story | 6 | Six stories of three to six words a sentence, built almost only from the word list. The questions come inside the story and the answers are written words |
| Verse Corner `f` | pairs | 7 | Written word to picture (1-5), then two written words that rhyme (6-7) |
| Word Journey `g` | journey | 4 | Review: the small words (1), rhymes (2), "which word is an animal?" (3), word to picture (4) |

60 rounds, 458 items. No new pictures: every picture comes from the library.

## The word list (153 words)

Chosen to be common, concrete, Afghan Dari, and safe everywhere: home,
family, food, animals, school, body, nature, a few verbs in the simple past,
and the small words that hold a sentence together.

- **Family and people** (14): مادر (mother)، پدر (father)، خواهر (sister)، برادر (brother)، دختر (girl)، بچه (boy)، کاکا (uncle (father's brother))، ماما (uncle (mother's brother))، خاله (aunt (mother's sister))، طفل (baby)، فامیل (family)، دوست (friend)، پدرکلان (grandfather)، مادرکلان (grandmother)
- **Home** (22): خانه (house)، دروازه (door)، کلکین (window)، بام (roof)، دیوار (wall)، حویلی (courtyard)، چاه (well)، دیگ (cooking pot)، قاشق (spoon)، پیاله (cup)، بشقاب (plate)، شمع (candle)، جاروب (broom)، صابون (soap)، قالین (carpet)، میز (table)، چوکی (chair)، کلید (key)، قفل (lock)، سبد (basket)، آتش (fire)، تخت (bed)
- **Food** (22): نان (bread)، آب (water)، چای (tea)، شیر (milk)، تخم (egg)، برنج (rice)، گوشت (meat)، نمک (salt)، ماست (yoghurt)، عسل (honey)، سیب (apple)، انار (pomegranate)، انگور (grapes)، توت (mulberry)، تربوز (watermelon)، لیمو (lemon)، بادام (almond)، پیاز (onion)، کچالو (potato)، زردک (carrot)، کدو (pumpkin)، گندم (wheat)
- **Animals** (21): گاو (cow)، بز (goat)، گوسفند (sheep)، بره (lamb)، خر (donkey)، اسپ (horse)، شتر (camel)، سگ (dog)، پشک (cat)، موش (mouse)، مرغ (hen)، خروس (rooster)، ماهی (fish)، مار (snake)، کبوتر (pigeon)، زنبور (bee)، روباه (fox)، گرگ (wolf)، فیل (elephant)، طوطی (parrot)، پروانه (butterfly)
- **School** (12): مکتب (school)، صنف (class)، معلم (teacher)، شاگرد (pupil)، کتاب (book)، کتابچه (notebook)، قلم (pen)، پنسل (pencil)، تخته (board)، بکس (bag)، زنگ (bell)، کاغذ (paper)
- **Body** (10): سر (head)، دست (hand)، پای (foot)، چشم (eye)، گوش (ear)، بینی (nose)، دهن (mouth)، دندان (tooth)، انگشت (finger)، زانو (knee)
- **Nature and places** (19): آفتاب (sun)، ماه (moon)، ستاره (star)، آسمان (sky)، ابر (cloud)، باران (rain)، برف (snow)، کوه (mountain)، دریا (river)، جوی (stream)، سنگ (stone)، درخت (tree)، گل (flower)، برگ (leaf)، باغ (garden)، روز (day)، شب (night)، راه (way)، پل (bridge)
- **Things** (3): توپ (ball)، بوت (shoe)، کلاه (cap)
- **Verbs, simple forms** (11): آمد (came)، رفت (went)، دید (saw)، داد (gave)، خورد (ate)، گفت (said)، نشست (sat)، خواند (read)، نوشت (wrote)، دارد (has)، است (is)
- **Small words** (19): من (I)، تو (you)، او (he or she)، ما (we)، این (this)، آن (that)، یک (one)، دو (two)، و (and)، در (in)، به (to)، با (with)، از (from)، را ((object mark))، هم (also)، خوب (good)، کلان (big)، خرد (small)، خوش (happy)

Every word except «پدرکلان، مادرکلان، و، در، به، را، هم، خوب، کلان، خوش» is
practised in at least one game outside the stories. Nine of those ten appear
in the stories and in the sentences spoken when a word is built; «مادرکلان»
is on the list but not yet used anywhere (a story with a grandmother is
missing).

## Decisions taken

- **Game ids are those of `fa-2`** (`alefba_garden`, `letter_shapes`,
  `word_weaver`, `syllable_catch`, `read_along`, `verse_corner`), so the
  Library keeps its six games on every level. The sorter keeps the id
  `letter_shapes` but is titled «سبد کلمه‌ها» (Word Baskets), because it now
  sorts words. `word_journey` is new.
- **Written words carry no vowel marks**, as in the books the children will
  meet. **Syllable tiles do carry زبر، زیر، پیش** on every short vowel
  (مَک، تَب، کِ، دُخ), because a syllable alone cannot be read without them.
  Vowels follow the reading tradition (کِتاب، سِتاره، دُختر).
- **Marks for the voice only.** «سر، گل، پل، خرد، در» are written with a mark
  in the *spoken* text (سَر، گُل، پُل، خُرد، دَر) and without it on screen, as
  the earlier packs do for نُه and خُرد.
- **Words left out because they are spelled like another word or differ by
  region:** شیر is taught as milk only and is never a choice in an "animal"
  question (it is also "lion"); ده (ten / village), سیر, کرم, مرد, شش, شست are
  not used at all. پدر and برادر are not built from syllable tiles, because
  their first vowel is said differently in Kabul and in the reading
  tradition.
- **Wrong choices are look-alikes**: same first letter, same ending or same
  length (چای / چاه, توت / توپ, خانه / خاله). In picture questions, pictures
  that could be taken for each other are never shown together (mother and
  girl, boy and head, salt and rice, house and school, cloud and rain ...).
- **Catch uses short words only.** The falling disc is 84 px wide; only words
  that still fit at 30 px are used there.
- **Pairs speak the word when a card is turned** (that is how the engine
  works), so in Verse Corner the child hears and sees the word together. It
  is supported reading, not a test.
- Story names are invented and common: سارا، نسرین، شبنم (girls), فرید، امید،
  جاوید (boys): three and three. The stories reuse scenes drawn for other
  packs; the characters therefore do not always wear the same colours as in
  the pack the scene was drawn for.
- English twins of every text are in `content/i18n/dari3.csv`. Lines that
  `dari.csv` already translates are not repeated there.

## For the reviewer to decide

Language
1. **The word list itself.** Is every word the one a village child in your
   region uses? Especially: بچه (boy; the English pack says پسر), فامیل
   (family), طفل (baby), کاکا / ماما / خاله, چوکی, کلکین, بکس, پنسل, کتابچه,
   بشقاب, پیاله, تخت (bed), پشک, کچالو, زردک, تربوز, دریا (river), پای, دهن,
   جاروب, کلاه (drawn as a round cap).
2. **Syllable breaks and vowel marks** in Word Weaver rounds 5-10 and Syllable
   Catch rounds 1-2: کِ‌تاب، سِ‌تا‌ره، پِ‌یا‌له، دُخ‌تَر، گَن‌دُم، کِل‌کین، پِن‌سِل،
   شا‌گِرد، گوس‌فَند، آس‌مان، کَ‌چا‌لو، پَر‌وا‌نه. Schools may break or vowel some
   of them differently (آ‌سِ‌مان? گو‌سفند?).
3. **"Syllable" is «بخش»**, as in levels 1 and 2. Schools may say «هجا».
4. The wrong syllable tiles are mostly non-words (مَت، کَب، تاپ). A few are
   real words (دار، کور، قَند، تار، نان). Acceptable?
5. **Counting syllables** (Word Baskets 5-7) assumes: دست، چشم، برف one; مکتب،
   دختر، زنبور two; کبوتر، ستاره، دروازه، پیاله، کچالو، پروانه three.
6. **Word families.** Baskets are «حیوان، خوراکی، بدن، مکتب، فامیل، طبیعت،
   خانه». Is «خوراکی» the right heading for food, «طبیعت» for mountain, rain
   and star? Fish, hen and meat are kept out of animal-or-food rounds.
7. **Rhymes** hold in Dari vowels only: توت/بوت، موش/گوش، ماه/چاه، سنگ/زنگ،
   مار/انار، بام/بادام، گل/پل، روباه/کلاه، زنبور/انگور، نان/باران، خر/سر،
   کتاب/آفتاب.
8. Story Dari is deliberately bare («سارا سیب را به دوست داد», «دوست او هم
   آمد», «در بکس چه است؟», «شبنم آب پاک خورد»). Is it still natural? Should it
   be «دوستش», «چیست», «نوشید»?
9. Letter names in the spoken help follow levels 1 and 2 (بِ، جیم، طا، هِ ...).

Voice
10. **Nobody has listened.** The stand-in voice is Iranian. Words it does not
    know from Iranian Persian are a risk: پشک، چوکی، کلکین، بکس، پنسل، کچالو،
    زردک، بره، بچه، کاکا، تو، دو. Single syllables spoken in the help line
    («مکتب: مَک، تَب.») and the letter-by-letter spelling («نان: نون، الف، نون.»)
    need a real ear.
11. The spoken and the written form differ for «سَر، گُل، پُل، خُرد، دَر». Check
    that the marks make the voice say them right, and decide whether the
    screen should show the mark too.

Teaching
12. **Reading without a spoken safety net.** In the "read it yourself" rounds
    (Alefba Garden even rounds, Word Baskets 8-11, Catch 4-5, Journey 3-4, the
    story questions) a child who cannot read yet can only guess; Y helps in
    most of them, but not in the sorter and not in the stories. This is what
    level 3 is for, but it is a break with "nothing depends on reading".
    Is the step from level 2 too steep? Should the placement game hold
    children back longer?
13. In Alefba Garden a longer word is drawn smaller than a short one on the
    answer cards, which can give the answer away by size alone.
14. Vowel marks on single-letter tiles (کَ، پِ) are drawn a little to the left
    of the letter, because the device does not shape text. Readable?
15. The order of rounds (food, animals, family, home, school, body, nature,
    verbs) is a guess at what is easiest first.
16. Stories: a wrong answer repeats the sentence and asks again. Three of
    the six are about girls, three about boys; adults shown are a mother, a
    grandfather and families at a meal. A local reviewer has to approve the
    scenes with people, as everywhere.

## How it was checked

- `validate --only fa-3`: ok, 0 warnings, 0 untranslated lines.
- Silent build of `core` and `fa-3` into a scratch folder: ok. A scratch card
  made from it ran `tests/fuzz_rounds.lua` (all 60 rounds open and take
  button presses without a crash), and screenshots of every game were looked
  at once.
- Not done: no audio was generated or heard, nothing ran on a handheld, no
  child or teacher tried it.

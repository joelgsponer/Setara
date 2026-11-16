# Dari 1: Sounds and first letters (`fa-1`), version 2

Written by an AI (Claude). **No Dari speaker, teacher or child has seen or
heard any of it.** Version 1 had no SOURCES file; its open points are in
`docs/review-notes.md` ("Dari reading 1 and 2") and still stand.

## What it teaches

Curriculum, level 1: hear first and last sounds in words, rhyme, know twelve
frequent letters (ا ب ن د م ر س ت ک ل و ی, and آ as its own sign). The other
letters are in `fa-2` and, for a class that wants them at once, in the
optional add-on `fa-1-alphabet`.

## What version 2 changed, and why

The owner played version 1 and said: "More and more varied content. Not
always the same questions." Measured on version 1: a third of the spoken
questions occurred more than twice («این حرف نون است. کدام تصویر با نون شروع
می‌شود؟» four times), each letter was the right answer about five times in
Alefba Garden, and a round replayed was the same round.

- Every game except the stories is now a **pool** (`"draw"`): a round holds
  12 to 24 items and a play asks eight (five in the builder, six pairs).
- **Game ids, letters and all 38 old rounds are kept.** Old rows are still
  there, some in a new wording, and some turned round (letter shown, picture
  asked instead of picture shown, letter asked) so that a letter is the right
  answer about three times a game, not five.
- 30 new rounds, three new games, about 110 more words with pictures.

| Game | Engine | Rounds (v1) | New in version 2 |
| --- | --- | --- | --- |
| Alefba Garden `a` | listen_pick | 16 (14) | New forms inside the old rounds: which picture **ends** with the letter, which of four does **not** start with it, odd one out by first sound and by rhyme. Round 15: two words, one letter. Round 16: sixteen riddles ("It is red, sweet, grows on a tree. It starts with sin.") |
| Letter Shapes `b` | sorter | 11 (8) | A third letter in every round; round 6 mixes joining and non-joining letters. Rounds 9-11: find a letter **inside a written word** (start, middle, end) |
| Word Weaver `c` | builder | 8 (6) | Twice as many words; round 7 longer words; round 8 builds open syllables (با، بو، بی). Y spells every word by letter names |
| Syllable Catch `d` | catch | 6 (4) | Round 5 last syllable; round 6 pictures fall: catch what starts like «نان», what ends like «مار» |
| Read Along `e` | story | 4 (2) | Two new stories from library scenes: Zohra and the hens' eggs, Yusuf and the lost lamb |
| Verse Corner `f` | pairs | 6 (4) | 28 rhyme pairs instead of 19 pair slots; rounds 5-6 pair pictures by **first** sound |
| Sound Baskets `g` (new) | sorter | 8 | Pictures into letter baskets by first sound, by last sound; yes/no ("Does سگ start with sin?", "Do مار and انار end alike?"); clap and count the syllables into baskets ۱ ۲ ۳; rhyme baskets |
| Sound Detective `h` (new) | listen_pick | 5 | Odd first sound out; odd rhyme out; which word has two parts; which word is longest or shortest; blend the parts («با، دام» → almond) |
| Sound Journey `i` (new) | journey | 4 | Mixed review in four stops: first letter, last letter, letter to picture, same start, rhyme |

68 rounds, 985 items (version 1: 38 rounds, 263 items). Three new pictures
are not needed here; everything comes from the library.

## Decisions

- **Wording.** Each question form has three to eight wordings; a script picks
  one that the pack has not yet spoken twice. Result: no spoken question
  occurs more than twice (version 1: 83 of 247).
- **Answers.** In Alefba Garden ten answers are still right four times
  (version 1: eight answers right four or five times, among 58; now among
  142). Everywhere else three at most. Sorter baskets and yes/no are by their
  nature right many times.
- **Right and wrong choices are checked by script**: a wrong picture never
  starts (or ends, or rhymes) like the right one, also not under another
  common name (بوت/کفش، لاری/موتر، چراغ/لامپ ...); two letters with one sound
  never stand together.
- **Help.** Every listen-and-pick, builder and catch row has a `help_fa` that
  says why the answer is right; every round has an `intro_fa`.
- **Voice.** Letter names carry their vowel mark as before (بِ، تِ، رِ). New
  Afghan words that an Iranian voice may misread are written with marks in the
  spoken text only (مُرچ، دُهُل، چَوکی، کَمپَل، جُراب، تُنبان ...). Words of
  version 1 are spoken as before. No word with two readings is a key word
  (شیر، سیر، کرم are not used).
- **Syllables** are split the way they are said (نَ، مَک); Y speaks the split.

## For the reviewer

1. Everything in `docs/review-notes.md` under "Dari reading 1 and 2".
2. **Rhymes** added: ناک/خاک، دیگ/ریگ، چای/پای، شفتالو/کچالو، خروس/طاووس،
   گندم/هیزم، فیل/فامیل، زردک/نمک، قالین/کلکین، عسل/نل، خر/تبر، نهال/زغال،
   بازار/قطار، ریسمان/تنبان، دیوار/غار، باران/دکان، خانه/پروانه، جراب/آفتاب،
   پشک/عینک، لیمو/کدو، پدر/مادر، برف/ظرف، سنگ/بادرنگ، بشقاب/کباب،
   شانه/آشیانه، زانو/ترازو، جنگل/بوتل، چپلک/سرک. Do they all hold in Dari
   as spoken locally? (موش/گوش and بیل/فیل were left out on purpose.)
3. **Syllable counts and splits**, above all: درخت (دِ، رَخت), معلم (3),
   آشیانه (4), کاغذپران (4), بره (بَ، ره), برنج (بِ، رِنج).
4. **Words**: بادرنگ، بوتل، کمپل، کلکین، چوکی، جراب، تنبان، چپلک، کچالو،
   مالته، لاری، سرک، قطی، کلچه، بالشت، بنا (mason), داس, آسیاب, کاکا/ماما.
5. **Riddles** (round 16 of Alefba Garden): are the clues what a village
   child would say about the thing?
6. The **yes/no** baskets use a green tick and a red cross. Understood?
7. The position rounds show a written word to a child who cannot read; she is
   meant to look for one letter shape. Too early for level 1?
8. Names in the new stories: زهره، یوسف.

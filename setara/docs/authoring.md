# Authoring content

Everything a child sees or hears is authored here as spreadsheets (CSV files,
UTF-8, comma separated, first row is the header). The builder turns them into
packs. Check your work at any time:

```sh
cd builder && python3 -m setara_builder.cli validate
```

It names the file and row of every problem and writes nothing.

## Where things live

```
content/
  pictures/<name>.svg          one shared picture library for all packs
  core/                        app strings (menus, guide, tutorial)
  english/1/                   one folder per pack: subject and level
    pack.json                  the games in this pack
    items.csv                  the word bank
    <game>.csv                 one sheet per game that is not derived from items
  teacher/english-1/           classroom lessons, phrase board, tips
```

## Rules that apply everywhere

- **Everything is spoken.** A question without `say_en` or `say_fa` is an error.
  Write the text exactly as it should be said. The builder makes the audio.
- **Dari is written normally**, in logical order, as you would type it. Use
  Afghan Dari words and spelling (مکتب، صنف، معلم، شفاخانه), not Iranian
  Persian. The builder joins the letters and reverses the order.
- **No names of real people, no personal data.**
- **Girls and boys in equal measure** in names, stories and pictures.
- **Short.** A round takes two to four minutes: 6 to 10 items.
- **At most four choices** on screen.
- Blank rows and rows starting with `#` are ignored.

### Two voices

Speech uses a woman's voice by default. For a dialogue, mark the speakers with
`f:` and `m:` and separate them with `//`:

```
f: What's your name? // m: My name is Omar.
```

### Things

Wherever a sheet asks for a *thing* (a choice, a tile, a card, a basket), write
one of these:

| You write | The child sees |
| --- | --- |
| `apple` | The picture `content/pictures/apple.svg` |
| `p:sheep*5` | The picture five times, for counting (1 to 20) |
| `t:Seven` | Latin text |
| `f:سیب` | Dari text |
| `lf:ب:start` | One form of a Dari letter: `alone`, `start`, `middle` or `end` |
| `snd` | A speaker card that plays the row's speech (Pairs only) |

Picture names are lowercase letters, digits and `_`. Story scenes start with
`scene_` and are drawn 4:3. A missing picture gets a labelled placeholder and
a warning, so you can author before the art exists. Several things in one cell
are separated with `|`.

## pack.json

```json
{
  "pack": "en-1",
  "subject": "en",
  "level": 1,
  "version": 1,
  "title_en": "English 1: Hello",
  "title_fa": "انگلیسی ۱: سلام",
  "games": [
    {
      "id": "word_stall",
      "engine": "listen_pick",
      "letter": "a",
      "title_en": "Word Stall",
      "title_fa": "دکان کلمه‌ها",
      "intro_fa": "گوش کن و تصویر درست را انتخاب کن.",
      "icon": "apple",
      "v1": true,
      "source": "items"
    },
    {
      "id": "sentence_train",
      "engine": "builder",
      "letter": "d",
      "title_en": "Sentence Train",
      "title_fa": "قطار جمله",
      "intro_fa": "کلمه‌ها را به ترتیب درست بگذار.",
      "icon": "train",
      "sheet": "sentence_train.csv"
    }
  ]
}
```

- `subject`: `en`, `fa` (Dari reading), `math` or `garden`.
- `pack` is `<subject>-<level>`. Raise `version` whenever you change a pack
  that has shipped.
- `letter`: one lowercase letter, unique per game in the pack. Round ids are
  `<pack>-<round>-<letter>`, for example `en-1-03-a`.
- `intro_fa`: the Dari instruction the guide speaks at the start of a round.
- `title_fa` is spoken when the child moves onto the game.
- `source: "items"` derives the rounds from `items.csv`. Otherwise give
  `sheet`.
- `"read_choices": true` on a listen_pick or journey game whose choices
  are written Dari words (`f:کابل`): after the question each choice is read
  aloud and lit in turn, so that answering never depends on reading. Do not
  use it where reading the word is the exercise. With two players such a
  game is played in turns, not as a duel.
- `"draw": 8` turns every round of the game into a pool: write 12 to 24
  items per round and each play asks only eight of them, a different eight
  every time (3 to 10; for pairs 3 to 6 out of up to 24 pairs). Use it
  wherever enough material exists: a round should not be the same twice.
  Questions always come in a new order, with or without `draw`. Not for
  story and say_it games. In a sorter every basket should have enough
  things that a draw without it is unlikely.
- `"say": "fa"` makes an items-derived game speak the Dari column (for the
  Dari subject). The default is `en`.
- `"optional": true` at the top marks a pack shipped only where the local
  team approves it. An optional pack is named `<subject>-<level>-<name>`
  (for example `garden-4-rights`) and adds its games to that level of that
  place. It is a separate zip: leave it off the card and nothing of it is
  there.

## items.csv, the word bank

```
unit,key,en,fa,picture,tags
01,hello,Hello,سلام,,greeting
03,apple,apple,سیب,apple,food
```

- `unit`: groups words into rounds. Keep it the same as the classroom lesson
  number where there is one. Two digits.
- `picture`: optional, and a thing: usually a picture name, but `p:book*2`
  works too. Words without a picture are used for speaking practice only.
- Games with `"source": "items"` use it like this:

| Engine | One round per unit, made of |
| --- | --- |
| `listen_pick`, `duel`, `journey` | Hear the word, pick its picture. Wrong choices come from the same unit, then from the rest of the pack. Dari meaning on Y |
| `say_it` | Hear, say aloud, hear again. Every word and phrase of the unit |
| `pairs` | Speaker card to picture, up to six pairs (units with fewer than three pictures are skipped) |

## Game sheets

Every sheet has a `round` column (for example `03`; use `03b` for a second
round in the same unit) and, optionally, `intro_fa` on the first row of a
round to replace the game's spoken instruction.

### listen_pick, journey, duel

```
round,say_en,say_fa,show,answer,distractors,help_fa,hop
01,apple,,,apple,bread|water,سیب,
02,,چند گوسفند است؟,p:sheep*5,t:5,t:4|t:6|t:7,,
03,three plus two,,,t:5,t:4|t:6,سه جمع دو,3+2
```

- `say_en`, `say_fa`: the spoken question. With both, Dari is spoken first.
- `show`: an optional thing shown with the question.
- `answer`: the right thing. `distractors`: up to three wrong things. Leave
  empty to take them from the other answers in the round.
- `help_fa`: Dari explanation spoken on Y.
- `hop` (journey only): `3+2` or `7-3`. The app shows the hops on a number
  line after the answer, so the child sees why it is right.

### say_it

```
round,say_en,say_fa,picture,meaning_fa
01,"Good morning, teacher",,sun,صبح بخیر، معلم
```

### sorter

```
round,thing,say_en,say_fa,basket,basket_say_fa
01,water_tap,,آب نل,f:پاک,آب پاک
01,water_puddle,,آب ایستاده,f:ناپاک,آب ناپاک
```

Two to four different baskets per round. A basket is a thing too.

### builder

```
round,say_en,say_fa,tiles,extra,rtl,done_en,done_fa,help_fa
01,I am a girl,,t:I|t:am|t:a|t:girl,t:is,,I am a girl,,من یک دختر هستم
02,,کتاب,f:ک|f:ت|f:ا|f:ب,,yes,,کتاب,
```

- `tiles`: the things in the correct order. `extra`: tiles that do not belong.
  At most eight in total.
- `rtl`: `yes` when the answer is built from right to left (Dari).
- `done_en`, `done_fa`: spoken when the answer is complete.

### catch

```
round,say_en,say_fa,targets,others,need,help_fa
01,,خوراکی‌های سالم را بگیر,apple|carrot|egg,candy|soda,5,
```

The row's speech is the rule. `need` is how many right things must be caught
(1 to 10). `help_fa` is the Dari explanation on Y.

### pairs

```
round,a,b,say_en,say_fa
01,snd,apple,apple,
01,t:2+3,t:5,,دو جمع سه مساوی پنج
```

Three to six pairs per round.

### market

```
round,say_en,say_fa,goods,target,units,mode
01,"Three apples, please",,apple,3,1,count
02,,بیست و پنج افغانی,bread,25,1|2|5|10|20,pay
```

- `count`: the child puts `target` goods on the scale (at most 20).
- `pay`: the child pays `target` with coins and notes of the given `units`
  (at most six different units).
- `help_fa` (optional column): Dari explanation on Y.

### story

One row per page, in order.

```
round,picture,say_en,say_fa,show_fa,choices,right,wrong_say_fa,wrong_picture
01,scene_well,,زهرا تشنه است.,زهرا تشنه است.,,,,
01,scene_two_waters,,کدام آب را بنوشد؟,,water_boiled|water_puddle,water_boiled,این آب ناپاک است و او را مریض می‌کند.,scene_sick
```

- A row with `choices` is a decision. The right one continues the story. A
  wrong one plays `wrong_say_fa`, shows `wrong_picture`, and asks again.
- `show_fa` or `show_en`: text shown on the page and lit while it is spoken
  (Read Along). One sentence per row.
- **Reading pages.** A row with `show_fa` or `show_en` and no `picture` is a
  reading page for children who can already read: the text has the whole
  screen. Write a paragraph, not a sentence: at most 8 lines of Dari (about
  60 words) or about 330 letters of English; with `choices` on the same row,
  at most 4 lines. The builder refuses a page that would not fit. The page
  is still spoken (`say_fa` or `say_en`, normally the same text). Put a
  picture row in between now and then. Questions about the text are rows
  with `choices`, which may be written words (`f:مرغ`, `t:a hen`).

## Teacher lessons: content/teacher/<name>/

`pack.json`: `{"pack": "teacher-en-1", "kind": "teacher", "subject": "en", "level": 1, "version": 1, ...}`

### lessons.csv

Every lesson has the same six steps: `hello` (3 min), `listen` (5), `say` (8),
`do` (8), `play` (8), `goodbye` (3).

```
lesson,title_en,title_fa,step,kind,teacher_fa,play_en,meaning_fa,answer_en
3,What's your name?,نام تو چیست؟,hello,line,به صنف صبح بخیر بگویید.,"Good morning, class!",صبح بخیر صنف,
3,,,say,drill,صنف تکرار می‌کند.,What's your name?,نام تو چیست؟,My name is Sara.
3,,,play,command,شاگردان فرمان را اجرا می‌کنند.,Stand up,ایستاده شوید,
3,,,goodbye,check,بپرسید. دست‌ها بالا.,What's your name?,نام تو چیست؟,
```

- `teacher_fa` (required): what the teacher does, in plain Dari, one or two
  short sentences.
- `play_en`: the English the speaker plays when she presses A.
- `meaning_fa`: the Dari meaning, on Y.
- `kind`: `line` (default), `drill` (also used by Drill Master; `answer_en`
  is the reply for the half-and-half drill), `command` (also used by Listen
  and Do), `check` (the five Quick Check questions), `tune` (the device plays
  a tune, for passing games), `note` (teacher instruction only).
- The first row of a lesson carries `title_en` and `title_fa`.

### phrases.csv, the Phrase Board

```
page,page_title_fa,en,fa
1,شروع درس,Stand up,ایستاده شوید
```

Eight phrases a page at most.

### tips.csv, five-minute teaching tips

```
title_fa,say_fa
صنف بزرگ,وقتی صنف بزرگ است…
```

## Teacher's guide: content/guide/<subject>-<level>/

Everything a teacher needs to know to teach a level, chapter by chapter:
what to teach, the background, how to explain it, figures, examples, common
mistakes, activities without the device, which games practise it, and how to
check. It is read on the device (teacher mode, Teacher's Course, the guide
tab; every page is also spoken) and printed with `tools/guide_book.py`.

`pack.json`: `{"pack": "guide-math-1", "kind": "guide", "subject": "math", "level": 1, "version": 1, "title_en": …, "title_fa": …}`

### guide.csv

```
chapter,title_en,title_fa,kind,picture,text_fa
1,Counting to five,شمردن تا پنج,goal,,در آخر این درس هر شاگرد می‌تواند…
1,,,figure,p:sheep*5,هر چیز یک عدد می‌گیرد.
```

- One row is one page. The first row of a chapter carries the titles. A
  chapter follows one unit of the learner pack, or one idea.
- `kind`: `goal` (what pupils can do at the end), `know` (what the teacher
  herself must know: the subject matter, in plain words), `explain` (how to
  explain it to the class, step by step, with things found in a classroom),
  `figure` (a picture with one or two sentences), `example` (a worked
  example), `mistake` (common mistakes and what to do), `activity` (class
  activities for up to 50 children without the device), `games` (which
  games on the device practise it, named by their Dari titles), `check`
  (how to see who has understood).
- `picture`: a thing, as everywhere (`p:sheep*5`, a scene). With a picture
  the text is at most 4 lines of Dari; without, at most 8 (about 60 words).
  Split longer explanations over several pages of the same kind.
- `text_fa` is shown and spoken. Plain Afghan Dari, short sentences, to a
  teacher who may have little training: say what to do and what to say.

A good chapter has 8 to 14 pages, in the order above. `content/guide/math-1`
chapter 1 is the model.

## What has to be true before content ships

The builder checks the form. People have to check the rest (spec section 9):

- A Dari-speaking educator reads and hears every text and signs it off.
- A fluent English speaker spot-checks every pack's audio.
- A local reviewer approves every picture of a person.
- Health content is checked by someone qualified.
- It is tried with real children on two or three devices.

## Pictures

`python3 tools/picture_list.py --missing` lists the pictures the sheets use
that are not drawn yet. `python3 tools/contact_sheet.py out.png name …` shows
pictures at about the size a child sees them.

One SVG per picture in `content/pictures/`. Style: thick dark outlines, flat
colours, no text, no gradients, readable at 3 cm on a 3.5 inch screen.

- Things: `viewBox="0 0 128 128"`, the object fills most of the square,
  transparent background.
- Scenes (`scene_*`): `viewBox="0 0 400 300"`, full background.
- Outline `#3b2f2f`, width 5 for things and 4 for scenes, round joins.
- People, clothing, houses, food and animals are local. A local reviewer
  approves every picture of a person.

# Privacy and safety

What Setara stores, what it does not, and how content is meant to be kept
safe before it reaches a classroom. The first half is read from the code
(`app/core/store.lua` and the places that call it). The second half
describes rules and gates; most of the gates are still ahead.

## Why this matters here

The app is meant for village classrooms in Afghanistan, including girls'
classes. Schooling can be sensitive there, and the local team knows the
situation best. The product spec therefore keeps the device low-risk by
default: nothing on it should say who used it, where, or for whom.

## In short

| | |
| --- | --- |
| Network | None. The app opens no connection. It uses no socket, HTTP or URL function |
| Accounts, logins, passwords | None |
| Profiles of children | None. Stars belong to the device |
| Names, photos, voice recordings, location, school | Never asked for, never stored. The app records no sound and no picture and has no text input at all (the handheld has no microphone) |
| What is stored | Two small JSON files on the SD card: stars and settings, and anonymous counts |
| Finest time unit stored | The ISO week (for example `2026-W46`) |
| What leaves the device | Nothing by itself. A person copies one file at a field visit |

## What the app stores, field by field

Everything is in `setara/data/love/setara/data/` on the card. Each file has a
backup copy next to it (`.bak`) with an older good state.

### progress.json: what the device remembers

One shared record per device. There is no per-child record.

| Field | Content | Written by |
| --- | --- | --- |
| `stars` | Round id → best star count (1 to 3) | `store.set_stars`, after a round |
| `level` | Subject → the level last chosen in that place (or suggested by "find my level") | `scenes/place.lua`, `scenes/placement.lua` |
| `last` | The subject and level of the last finished round | `scenes/play.lua` |
| `settings.volume` | 0.1 to 1 | pause menu |
| `settings.brightness` | 0.4 to 1 | pause menu |
| `settings.locale` | `fa` or `en` (English mode) | pause menu, or the launcher |
| `settings.class_size` | 1 to 80, starts at 30 | pause menu in teacher mode |
| `teacher_lesson` | The number of the teacher's current lesson | teacher mode |
| `tutorial_done` | The button tutorial has been seen | `scenes/tutorial.lua` |
| `calibration_seen` | The button calibration has been offered | `scenes/calibrate.lua` |
| `missed` | Up to 300 question keys (round and answer) that were answered wrong on this device, so that they come back first in the warm-up; removed when answered right at the first try. Nothing about who | `scenes/play.lua` |
| `teacher_pack`, `teacher_lessons` | Which lesson book and lesson the teacher is on | `teacher/common.lua` |
| `starts` | How often the app has been started. Used only to seed the random numbers, because handhelds without a clock battery start at the same "time" every day | `main.lua` |

### stats.json: anonymous counts

| Field | Content | Written by |
| --- | --- | --- |
| `device` | Eight random hexadecimal characters, made once on the first start | `store.ensure_device` |
| `weeks` | ISO week → minutes of use per subject (`en`, `fa`, `math`, `garden`) and for `teacher` mode | `store.add_minutes` |
| `rounds` | Round id → `plays`, `attempts`, `correct` (first-try right), `minutes`, `stars` (added up) | `store.count_round` |
| `checks` | Teacher lesson id → `times`, `right` (hands counted), `size` (class size × questions) | `store.count_check` |
| `teacher` | Counters: tools opened (`open_<tool>`), lessons started and finished (`lesson_<id>`, `done_<id>`), previews (`preview_<id>`), tips played (`tip`), the highest lesson previewed (`course_lesson`) | `store.count_teacher`, `teacher/preview.lua` |
| `log` | The last 30 problems: app version, a short code of at most 120 characters, the week | `store.log` |

The log codes are technical: a rejected update with the reason, a pack that
could not be read, a round that could not be loaded, or the text of a crash
(a Lua error message, which names a source file and a line of the app).

### buttons.json

Only if a game pad had to be calibrated: which raw button of the pad is
which of the eleven button names.

### What is not there

- No name, age, sex or number of any child or teacher.
- No record of which child answered what. A round's counts are sums over
  everyone who ever played it on that device.
- No school, village, class or teacher identifier. `class_size` is a number
  the teacher sets so that Quick Check can show a share.
- No date and no time of day. The counts carry the week only.
- No audio, no picture, no text typed by anyone.
- "Find my level" stores only the suggested level, for the device.

### The random device id

`device` is not derived from the hardware, the card or anything else. It is
drawn from the random generator once and saved. Its only use is to tell two
copied files apart. The team may map an id to a classroom on paper, or not
at all. A new card gets a new id. Deleting `stats.json` (and its `.bak`)
makes a new one.

### The weekly granularity

`store.lua` has one clock function, `week()`, which returns the ISO year
and week. It is the only use of the date in what is stored. Minutes of use
are added up per week; round counts carry no time at all.

Two honest limits:

- The file system of the card keeps a "last modified" time for every file,
  as every file system does. Whoever holds the card can see when
  `stats.json` and `progress.json` were last written, as far as the
  device's clock is right. The app does not control this.
- Seen together, the counts say something about a class as a whole: how
  much the device is used and which rounds are hard. That is their purpose.
  They cannot be split into children.

## What a field visit copies

Version 1 uploads nothing. At a visit, a team member takes the card out (or
connects it) and copies one file:

```text
setara/data/love/setara/data/stats.json
```

and reads it on a PC:

```sh
python3 tools/read_stats.py stats.json
```

It prints: the device id, minutes per week and subject, plays and first-try
success per level, the hardest rounds, the Quick Check shares per lesson,
teacher mode use, and the problem log. `progress.json` need not be copied.

The copy on the PC is then the team's to protect. If the team notes on paper
which device id belongs to which classroom, that list is the one piece of
information that links counts to a place. It should be kept apart from the
files, or not made.

## No network

`grep` finds no network call in `app/`: no socket library, no HTTP, no
`love.system.openURL`. The app uses only LÖVE's own file system inside its
save folder (plus one `os.rename` there for safe writing). Updates arrive as
zip files that a person copies into `setara/update/` on the card; the app
checks every file against a checksum before it installs anything
([pack-format.md](pack-format.md)).

The reference handheld has Wi-Fi and Bluetooth hardware. The app does not
use them. What the device's firmware does with them is outside the app, and
no firmware has been chosen or tested yet.

The builder is different: on the team's PC it may download voices, map data
or call a speech service. That happens before anything reaches a device.

The browser version is for showing the app, not for classrooms. The page
loads its own files from the server that hosts it; stars and settings stay
in the browser's storage. The server's own access log is the host's
business.

## The neutral look

- No organisation name or logo anywhere in the app. The start screen shows
  the guide bird, the word "Setara" and the version number.
- No third-party games and no branding on the card folder.
- A deployment can replace the start picture: a 640×480 `start.png` in
  `setara/data/love/setara/` is shown instead of the bird.
- The sound effects are synthesised by the app. There are no songs or
  recordings from elsewhere.
- Stories, names and pictures are meant to show girls and boys in equal
  measure. Whether the pictures are acceptable locally (dress, girls and
  boys in one picture) is for a local reviewer to decide; none has seen them.

One thing does point to an origin: the optional geography pack ends by
saying that the lessons were made in Basel, in Switzerland. That is one
reason it is optional.

## Optional packs

A pack marked `"optional": true` in its `pack.json` is a separate zip. Leave
the file off the card and nothing of it is on the device: no game tile, no
picture, no sound. No other pack refers to it. An optional pack is named
`<subject>-<level>-<name>` and adds its games to that level of that place.

`image/make_card.py` copies every zip it finds in `packs/`, optional or not,
unless told otherwise. **To leave an optional pack off a card, run
`python3 image/make_card.py --without garden-4-rights` (repeat `--without`
for each pack), or delete its zip from `setara/data/love/setara/packs/` on
the card.** `VERSION.txt` in the card folder says how many packs `make_card.py` put there.

There are two optional packs today.

| Pack | Why it is optional |
| --- | --- |
| `garden-4-rights` (My rights, your rights) | Talk about rights, and about girls' schooling, can put a teacher or a class at risk where the programme works. Only the local team can judge that, class by class. The pack's notes say: it must not be installed anywhere before the local team has read it and agreed, and "if in doubt, leave the pack out". The notes list 18 sentences and choices a cautious reviewer might question |
| `garden-4-world` (The world, Switzerland and Basel) | It tells the children where the device and its lessons come from. The local team may or may not want that said |

Both files are worth reading in full before any decision:
[../content/garden/4-rights/SOURCES.md](../content/garden/4-rights/SOURCES.md),
[../content/garden/4-world/SOURCES.md](../content/garden/4-world/SOURCES.md).

The product spec names further optional packs (for example on growing up
for older girls). They are not written.

## Safeguards for content

### Where things stand

All content was written by an AI (Claude): the Dari, the English, the math,
the health and first-aid lessons, the rights and geography packs, the
teacher lessons, the pictures. **None of it has been reviewed by a
Dari-speaking educator, a health professional or the local team. Nobody has
listened to the generated speech. The app has not been run on a handheld.**
Until the gates below are passed, the content must not reach children.

The first-aid pack needs the most care. Wrong first-aid advice can hurt
someone. Its notes file,
[../content/garden/3/SOURCES.md](../content/garden/3/SOURCES.md), prints the
fact sheet it was written from and marks the rounds that most need a
professional (for example the "help at home or go to the clinic" round).

### What the machine checks

The builder (`python3 -m setara_builder.cli validate`) checks the form, not
the truth:

| Check | Kind |
| --- | --- |
| Every question has speech | error |
| Every game has a spoken Dari instruction and a spoken title | error |
| English speech contains no Dari letters | error |
| Every Dari character has a glyph in the device font | error |
| At most four choices; a distractor is never the answer | error |
| Sorter rounds have two to four baskets; pairs rounds three to six pairs | error |
| A missing picture | warning and a placeholder (error with `--strict`) |
| Dari texts without English for English mode | listed with `--untranslated` |

The math sheets are generated, and every answer is computed and asserted by
`content/math/generate.py`.

The tests check that no round crashes the app. Nothing checks that a Dari
sentence is correct, kind or natural, that a health statement is true, or
that a clip is pronounced well.

### What people have to check (the review gates)

From the product spec, section 9, as quoted in [authoring.md](authoring.md):

1. A Dari-speaking educator reads and hears every text and signs it off.
2. A fluent English speaker spot-checks every pack's audio.
3. A local reviewer approves every picture of a person.
4. Health content is checked by someone qualified.
5. It is tried with real children on two or three devices.

And for the optional packs: the local team reads the pack and agrees before
it is installed anywhere.

None of these gates has been passed. [review-notes.md](review-notes.md)
collects the open points for the people who will do the review. The repository has no sign-off column
or record yet; the spec asked for a shared spreadsheet with one, and the
build uses plain CSV files instead.

### Rules the content follows

Written into the authoring guide and the pack notes:

- No names of real people.
- No doses, no names of medicines, no home remedies in the health packs.
  When in doubt the lesson is: tell an adult, go to the clinic.
- Dangerous steps are for adults: boiling water, preparing oral rehydration
  solution and abdominal thrusts are shown as done by a grown-up.
- Nothing about government, religion, war or politics in the rights and
  geography packs; no adult is a villain; nobody is blamed.
- No copyrighted songs, pictures or recordings.

### Gentle by design

No lives, no game over, no ranking of children, no timer that punishes. A
wrong answer comes back later. In a Duel the two children's points are shown
during the round, but the stars are shared and no winner is announced.

### English mode as a review tool

English mode lets someone who reads no Dari see what every text is meant to
say. It is useful for a first look by a health professional or a partner. It
cannot replace the Dari review: the English and the Dari come from the same
AI, so an error in the Dari can be invisible in the English.

## If you find a problem

A wrong fact, an unkind sentence, a picture that would cause trouble, a
field that stores more than this page says: please report it. See
[../../CONTRIBUTING.md](../../CONTRIBUTING.md).

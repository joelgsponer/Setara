# Contributing to Setara

Thank you for wanting to help. Setara is an offline learning app for cheap
Linux game handhelds, meant for village classrooms in Afghanistan. The
project lives in the [`setara/`](setara/) folder of this repository.

Please read this first, because it decides what help is most needed:

- The app runs on a PC and in a browser. It has **not** been run on a
  handheld yet.
- **Nobody has listened to the generated speech.** The voices are stand-ins;
  the Persian voice is Iranian, not Afghan.
- **All content was written by an AI (Claude)**: the Dari, the English, the
  math, the health and first-aid lessons, the rights and geography packs,
  the teacher lessons and the pictures. **None of it has been reviewed by a
  Dari-speaking educator, a health professional or the local team.** It must
  not reach children before that review. This holds most of all for the
  first-aid pack.

So the most valuable contributions are reviews by people, not code.

## Ways to help

| You are… | You can… | Start here |
| --- | --- | --- |
| A Dari speaker, best of all an Afghan teacher | Read and hear the Dari: is it correct, natural Afghan Dari, kind, and right for children of 6 to 14? | [`setara/docs/review-notes.md`](setara/docs/review-notes.md), the sheets in `setara/content/`, and the app itself |
| A nurse, doctor or first-aid trainer | Check the health content, the first-aid pack first | [`setara/content/garden/3/SOURCES.md`](setara/content/garden/3/SOURCES.md); the English of every text is in `setara/content/i18n/firstaid.csv` and `garden.csv` |
| Someone who knows the local situation | Judge the optional packs and the pictures of people: would any of it cause trouble for a teacher or a class? | [`setara/content/garden/4-rights/SOURCES.md`](setara/content/garden/4-rights/SOURCES.md), [`setara/docs/privacy-and-safety.md`](setara/docs/privacy-and-safety.md) |
| A fluent English speaker | Listen to the English clips and read the English lessons | `setara/content/english/`, `setara/content/teacher/english-1/` |
| An illustrator | Redraw weak pictures, fix pictures a reviewer rejects | [Pictures](setara/docs/authoring.md#pictures) |
| An owner of an RG35XX H, an R36S or a similar handheld | Try to run the app on it and report exactly what happened | [`setara/docs/device.md`](setara/docs/device.md) |
| A translator | Bring the content to another language, for example Pashto | [`setara/docs/faq.md`](setara/docs/faq.md), question 11 |
| A programmer | Fix bugs, improve the builder, the tests and the tools | [`setara/docs/architecture.md`](setara/docs/architecture.md) |
| A teacher trainer | Read the teacher mode guide and tell us what would not work in a real room | [`setara/docs/teacher-mode.md`](setara/docs/teacher-mode.md) |

You do not need to build anything to review content. The app can be tried in
a browser or on a PC in English mode, where every Dari text is shown in
English and everything spoken has a caption
([`setara/docs/english-mode.md`](setara/docs/english-mode.md)). Keep in mind
that this English was written by the same AI as the Dari. It shows what the
Dari is meant to say. It does not prove that the Dari says it.

A review is welcome in any form: an issue, a pull request, or a list of rows
with your remarks. Say who you are in general terms (for example "primary
teacher, native Dari speaker, Herat") only if you are comfortable with that
being public.

## Ground rules

These are product decisions from the spec. They are written out in
[`setara/CLAUDE.md`](setara/CLAUDE.md). Please do not trade them away for
convenience.

- **Audio first.** Everything is spoken. Nothing may depend on the child
  reading. A prompt without audio is a bug.
- **No personal data.** No names, photos, recordings, location, school
  identifiers or profiles, ever. Counts are anonymous, nothing finer than
  the week.
- **No network.** The app never opens a connection. Updates arrive as files.
- **Eight buttons, no typing.** D-pad, A, B, X, Y, L, R, Start.
- **Small screen, weak hardware.** 640×480. Latin text at least 24 px, Dari
  at least 30 px, at most four choices. No video, no shaders, nothing
  allocated per frame.
- **Only LÖVE 11.** The same app on device and PC. No native extensions, no
  FFI, no LÖVE 12.
- **Dari is shaped at build time.** No shaping or bidi in the app.
- **Data-driven.** One engine per mechanic. New content must not need new
  code.
- **Nothing breaks the device.** Damaged packs are ignored, a damaged save
  file resets only itself, a crash restarts the app.
- **Gentle.** No lives, no game over, no ranking of children, no timer that
  punishes.
- **Neutral.** No third-party games, no branding, no organisation logo.
- **Balanced.** Girls and boys in equal measure in stories, names, voices
  and pictures.

And one rule for everyone who writes about the project: **do not overstate
where it stands.** Do not call something tested on a device, listened to or
reviewed unless a person has done exactly that.

## Set up

You need LÖVE 11.5, Python 3.11 or newer, ffmpeg and the Cairo library. The
full guide with the common problems is
[`setara/docs/getting-started.md`](setara/docs/getting-started.md).

```sh
git clone https://github.com/joelgsponer/Setara
cd Setara/setara
(cd builder && pip install -e .)
```

## Validate, build, run, test

All from the `setara/` folder.

```sh
# check every sheet; writes nothing; a few seconds
(cd builder && python3 -m setara_builder.cli validate)

# build the packs without speech (minutes), or leave out --tts for the stand-in voices
(cd builder && python3 -m setara_builder.cli build --tts silent)

# assemble the card folder and run it
python3 image/make_card.py
dist/card/setara/Setara-English.sh        # or Setara.sh for Dari

# tests
(cd builder && python3 -m pytest -q)       # builder
SETARA_LOVE=love tools/test.sh             # the app, headless (Linux, needs xvfb-run)
```

`tools/test.sh` needs the built packs and the card folder. It prints where
the screenshots are. Look at them after changing anything visible: a passing
test says the app did not crash, not that the screen is right. If the
`update` step fails on a busy machine, run `tests/update/run.sh` again by
itself before you look for a bug; it has been seen to fail under heavy load
and pass when repeated.

## Proposing content

Content is CSV sheets in `setara/content/`, one folder per pack. The format
is in [`setara/docs/authoring.md`](setara/docs/authoring.md).

1. **Edit the sheets**, not the built packs. UTF-8, comma separated. Write
   Dari normally, in logical order, in Afghan Dari words and spelling.
2. **Math is the exception.** The math sheets are generated: change
   `content/math/generate.py` and run it. Do not edit the math CSVs by hand.
3. **Give every Dari text its English** in `content/i18n/*.csv`, so that
   people who do not read Dari can follow. This lists what is missing:

   ```sh
   (cd builder && python3 -m setara_builder.cli validate --untranslated /tmp/todo.csv)
   ```

4. **Validate.** The command above must end with `ok`. It names the file and
   row of every problem.
5. **New pictures** go to `content/pictures/<name>.svg` in the library's
   style ([Pictures](setara/docs/authoring.md#pictures)). A missing picture
   only gives a warning and a placeholder, so text can come first.
   `python3 tools/picture_list.py --missing` lists what is not drawn.
6. **Raise `version`** in `pack.json` when you change a pack that has
   already been put on cards.
7. **Say where facts come from.** For health content, name the source of
   every medical statement and what you simplified, in the pack's
   `SOURCES.md`, as the first-aid pack does. No doses, no names of
   medicines, no home remedies.
8. **Say what you are and what you checked** in the pull request: "native
   Dari speaker, read rounds 01 to 06 of `fa-1`", or "written with an AI,
   not reviewed by a Dari speaker". Both are welcome. They are not the same,
   and the difference must stay visible.

### The review gates

The builder checks the form. People have to check the rest before content
ships to a classroom:

- A Dari-speaking educator reads and hears every text and signs it off.
- A fluent English speaker spot-checks every pack's audio.
- A local reviewer approves every picture of a person.
- Health content is checked by someone qualified.
- It is tried with real children on two or three devices.
- An optional pack is installed only where the local team has read it and
  agreed.

Merging a pull request does not pass any of these gates. Content in the
repository is a draft until the people above have signed it off. There is
no sign-off record in the repository yet; a proposal for how to keep one
would be a useful contribution.

### Content rules

- No names of real people, no personal data.
- Short: a round is 6 to 10 items, two to four minutes.
- Nothing about government, religion, war or politics. Nobody is blamed.
- No copyrighted songs, pictures or recordings.

## Coding conventions

As the code shows them. There is no linter configuration in the repository.

### Lua (the app, `setara/app/`)

- Two spaces, no tabs. `snake_case` for functions and variables,
  `UPPER_CASE` for constants at the top of a file.
- One module per file: `local M = {}` … `return M`, or a class table with
  `X.__index = X` and `X.new()`. No globals, except the one `app` table made
  in `main.lua`.
- Every file starts with a comment that says what it is for. Comments say
  why, in plain words.
- Scenes have `enter`, `leave`, `resume`, `update`, `draw`, `input`. Never
  call `app.push` or `app.pop` from `enter`.
- Engines follow the interface at the top of `app/engines/init.lua`;
  `listen_pick.lua` is the reference. Use button names from
  `core/input.lua`, never raw keys.
- To wait for speech, watch `audio.busy()` in `update`. Do not rely on
  `on_done`: speech that is stopped or replaced never calls it.
- Never trust pack data. Check types, skip what cannot be shown, and never
  let a bad round crash the app. Ask `love.filesystem.getInfo` before a
  read (the browser build cannot catch a failed read).
- Draw in 640×480 coordinates with the colours in `ui.c`. Dari text goes
  through `text.fa` or `text.centered`; do not wrap or reorder it.
- Depend only on LÖVE 11 and plain Lua. The browser build runs without
  LuaJIT.

### Python (the builder and tools)

- Python 3.11+, type hints, `pathlib`, `from __future__ import annotations`.
- Lines up to about 120 characters.
- Problems in content are reported with `report.error(where, message)` or
  `report.warn(...)`, naming the file and row. They do not raise. One bad
  pack must not stop the others.
- Output must be reproducible: the same sheets give the same pack.

### Formats and tests

- When a format changes, change the builder, the app and the doc
  (`docs/level-format.md`, `docs/pack-format.md`, `docs/authoring.md`) in
  one pull request.
- A new engine or a changed one gets a test script in `setara/tests/` that
  plays full rounds. Run `tests/fuzz_rounds.lua` after any change to an
  engine or to the builder's output.
- Builder changes get a test in `setara/builder/tests/test_builder.py`.

### Documentation

Plain, short sentences. Tables where they help. No emojis. State only what
is true of the code and content as they are, and say what has not been
verified.

## Licences

By contributing you agree that your contribution is released under the
licence of the part you change.

| Part | Licence | File |
| --- | --- | --- |
| Code (app, builder, tools, tests) | MIT | [`LICENSE`](LICENSE), [`setara/LICENSE`](setara/LICENSE) |
| Content: everything under `setara/content/` (lessons, sheets, pictures, generated audio) | CC BY-SA 4.0 | [`setara/content/LICENSE.md`](setara/content/LICENSE.md) |
| Fonts: Andika, Noto Naskh Arabic | SIL Open Font License | `setara/app/assets/fonts/OFL-*.txt` |
| Map outlines used by `tools/maps.py` | Natural Earth, public domain | naturalearthdata.com |

Do not add anything you do not have the right to share: no copyrighted
songs, pictures, recordings or textbook pages. If you add third-party
material under a free licence, name its source and licence in the pull
request and next to the file.

## Commits and pull requests

- **One topic per pull request.** A content change and a code change go in
  separate pull requests unless a format change ties them together.
- **Commit messages**: one short line in the imperative that says what
  changed ("Add poisoning to the first-aid pack", "Fix the problems found in
  code review"). Add a body when the reason is not obvious.
- **Before you open it**: `validate` ends with `ok`, the builder tests pass,
  and for app changes `tools/test.sh` passes and you have looked at the
  screenshots.
- **In the description**, say:
  - what changed and why;
  - what you tested, and on what (PC, browser, which handheld and firmware);
  - what you could not test;
  - for content: who wrote it, whether an AI was used, and who has reviewed
    it.
- **Do not commit** built output (`packs/`, `dist/`), the speech cache
  (`builder/.cache/`), downloaded voices (`builder/voices/`), saved device
  data (`progress.json`, `stats.json`) or secrets such as API keys. The
  `.gitignore` covers these.
- **Never include data about real children, teachers or schools**, in
  content, tests, screenshots, issues or commit messages. A `stats.json`
  from a real device is anonymous by design, but do not post one together
  with the place it came from.

## Reporting a problem

Open an issue on GitHub. For a content problem, name the pack, the sheet and
the row, quote the text, and say what is wrong and what would be right. For
a bug, say what you did, what you expected and what happened, with the
version shown on the home screen.

If a problem could put someone at risk, for example wrong first-aid advice
or content that could endanger a class, say so in the first line so that it
is seen first.

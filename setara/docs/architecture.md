# Architecture

How the pieces of Setara fit together, with the real file and function names.
Paths are relative to the `setara/` folder.

## The big picture

```text
 content/                          builder/setara_builder/             packs/
 ---------------------             ---------------------------         -----------------
 <subject>/<level>/pack.json       cli.py     validate | build         core.zip
 <subject>/<level>/*.csv    ---->  build.py   sheets -> level JSON --> en-1.zip  fa-1.zip
 teacher/english-1/*.csv           tts.py     text -> Ogg Vorbis       math-1.zip garden-1.zip
 core/strings.csv                  shaping.py Dari -> drawing order    garden-4-rights.zip ...
 i18n/*.csv (English mode)         images.py  SVG -> small PNG         teacher-en-1.zip
 pictures/*.svg                    (cache: builder/.cache/)            (one checksummed zip each)
                                                                             |
                    +--------------------------------------------------------+
                    |                                                        |
                    v                                                        v
         image/make_card.py                                      tools/web/make_web.py
                    |                                                        |
                    v                                                        v
         dist/card/setara/                                       dist/web/
           setara.love   (zip of app/)                             the app compiled by love.js,
           Setara.sh, Setara.bat, Setara-English.*                 packs unpacked inside it
           update/       (drop new packs here)                     (static files, any web server)
           data/love/setara/packs/<pack>.v<version>.zip
           data/love/setara/data/progress.json, stats.json
                    |
                    v
         app/  (LÖVE 11, Lua)  on a PC today; on a handheld once phase 0 is done
```

Three things follow from this layout:

- The app never reads `content/`. It reads packs. New content needs no new
  code.
- Everything slow or clever happens at build time on a PC: speech, Dari
  shaping, line breaking, picture rendering, checksums. The device only plays
  clips and draws glyphs and PNGs.
- The same `app/` runs on a PC, in a browser and (as planned) on the
  handheld. It depends only on LÖVE 11.

The handheld part is a plan. The app has been run on a PC and in a browser
only. See [device.md](device.md).

## The app

### main.lua and the scene stack

`app/main.lua` owns the window, the scene stack, input routing, the crash
handler and the test driver. `app/conf.lua` sets a 640×480 window and turns
off the physics, video and touch modules.

A scene is a table with optional methods `enter`, `leave`, `resume(result)`,
`update(dt)`, `draw()` and `input(button)`.

| Function | Does |
| --- | --- |
| `app.push(scene)` | Puts a scene on top and calls `enter` |
| `app.pop(result)` | Removes the top scene (`leave`) and calls `resume(result)` on the one below. The first scene is never removed |
| `app.replace(scene)` | Swaps the top scene |
| `app.home()` | Drops everything above the first scene |
| `app.top()` | The top scene |

`love.update` advances input, audio and the top scene. `love.draw` draws the
top scene onto a 640×480 canvas and scales the canvas to the window. A scene
with `overlay = true` (the pause menu) is drawn over the scene below it.
Button presses reach the top scene through `input.listener`.

Rule: never call `app.pop` or `app.push` from a scene's `enter`.

`love.errorhandler` notes a crash in the log inside `stats.json` and restarts
the app, unless the crash came in the first ten seconds (so it cannot loop).

### Core modules (`app/core/`)

| File | One line |
| --- | --- |
| `input.lua` | Maps keyboard, game pad, raw joystick buttons, hats and sticks to eleven button names (`up down left right a b x y l r start`); holds a learned map from calibration |
| `audio.lua` | Speech: `audio.say(clips, opts)` plays a list of clips in order; `busy()`, `stop()`, `pause()`, `resume()`, `duration()`; the slow variant is `<name>.slow.ogg` |
| `sfx.lua` | Sound effects and the tune, synthesised at start. No audio assets |
| `text.lua` | Fonts (Andika, Noto Naskh Arabic) and text drawing; `text.fa` prints ready-made Dari lines; English mode lookup in `text.dict` |
| `ui.lua` | Colours, cards, `ui.thing` (draws a picture, counted pictures, Dari or Latin text, a speaker card), stars, the guide bird, button badges |
| `packs.lua` | Finds, checks, installs and mounts packs; `packs.round`, `packs.review`, `packs.string`, `packs.clips` |
| `store.lua` | The two saved files, `progress.json` and `stats.json`, with backup and safe writing |
| `quiz.lua` | The item loop shared by most engines: wrong items come back, the pace adapts, stars |
| `valley.lua` | Draws the home valley and its four places, which grow with the stars |
| `json.lua` | A small JSON reader and writer |

### Learner scenes (`app/scenes/`)

| File | Screen |
| --- | --- |
| `boot.lua` | Start: installs waiting packs, loads all packs, then goes home. Shows "No content packs found" if there is no `core` pack |
| `home.lua` | The valley with four places: Bazaar (English), Library (Dari), Workshop (math), Garden (health and environment). Holding L and R for two seconds opens teacher mode |
| `place.lua` | One place: level chips, "find my level", one or two players, and the game tiles. Every level is open |
| `play.lua` | One round: introduction, warm-up, the engine, the stars |
| `placement.lua` | "Find my level": four questions per level, three right to go on; suggests a level |
| `pause.lua` | Start button: volume, brightness, language, carry on, home; in teacher mode also the class size |
| `tutorial.lua` | First run: a spoken tour of the buttons. Start skips it |
| `calibrate.lua` | Learns the buttons of an unknown pad and saves `data/buttons.json` |

### Engines (`app/engines/`)

Ten game mechanics, one module each: `listen_pick`, `pairs`, `catch`,
`builder`, `say_it`, `story`, `journey`, `market`, `duel`, `sorter`.
`init.lua` is the registry (`engines.get(id)`) and documents the interface.
`common.lua` holds what the three choice games share: dealing choices to the
four directions (`common.deal`) and drawing them.

An engine module returns a table with `new(round, ctx)`. The instance has:

| Member | Meaning |
| --- | --- |
| `:start()` | Called when the spoken introduction is over |
| `:update(dt)`, `:draw()`, `:input(button)` | The usual three |
| `:again(slow)` | X button: say it again, slowly |
| `:help()` | Y button: explain in Dari |
| `.finished` | True when the round is over |
| `:stars()` | 1 to 3 |
| `:counts()` | Attempts and first-try right answers, for the anonymous counts |
| `:progress()` | Done and total, for the dots at the top |
| `.uses` | Optional: buttons the engine wants for itself (Duel takes A, B, X, Y) |

`ctx` gives the engine `ctx.root` (the pack's folder), `ctx.say(clips, opts)`,
`ctx.pair`, `ctx.player`, `ctx.next_player()` and `ctx.top`.

`listen_pick.lua` is the reference engine: 100 lines. The games are described
in [games.md](games.md).

### Teacher mode (`app/teacher/`)

`menu.lua` is the menu with today's lesson and nine tools: `lesson.lua`,
`preview.lua`, `phrases.lua`, `drill.lua`, `games.lua`, `story.lua`,
`stations.lua`, `check.lua`, `course.lua`. `common.lua` loads lessons from the
teacher pack and remembers the lesson number. See
[teacher-mode.md](teacher-mode.md).

## The life of a round

From the place screen to the stars. All of this is `app/scenes/play.lua`
unless another file is named.

1. **Choosing.** On the place screen the child presses A on a game tile.
   `place.lua` picks the first round of that game with fewer than three stars
   (`next_round`) and pushes `Play.new({pack, game, round_id, pair})`.
2. **Loading (`Play:enter`).** `packs.round` reads `levels/<id>.json` from
   the pack. The engine named in the file is created with `mod.new(round,
   ctx)`. If two players are chosen and the engine is `listen_pick`, the
   `duel` engine is used instead. A round that cannot be read is noted in the
   log and the screen closes; nothing crashes.
3. **Introduction (state `intro`).** The guide bird speaks the round's
   `intro_audio`, the Dari instruction. A skips it. The scene waits by
   watching `audio.busy()`, not by a callback.
4. **Warm-up five (state `warmup`, `Play:make_warmup`).** If the class has
   already earned stars in other rounds, up to five review questions are
   asked first. They come from `review.json` of this pack, or of the level
   below. Only questions from rounds with at least one star are used, never
   from the round about to be played, and no answer twice. At least five
   candidates and three questions are needed; otherwise the warm-up is left
   out. It runs in the `listen_pick` engine, shows a small sun, and does not
   count.
5. **The game (state `main`).** `engine:start()`, then `update`, `draw` and
   `input` every frame. Button routing in `Play:input`: Start opens the pause
   menu, B leaves the round, X calls `engine:again(true)`, Y calls
   `engine:help()`, everything else goes to `engine:input`. Buttons listed in
   `engine.uses` go straight to the engine.
6. **Result (state `result`, `Play:finish`).** When `engine.finished` is
   true, the stars are taken from `engine:stars()` and appear one by one. The
   guide praises. A plays the next round of the same game that has fewer than
   three stars; B goes back to the place.
7. **What is saved.**

| Call | File | What |
| --- | --- | --- |
| `store.set_stars(round_id, stars)` | `progress.json` | The best star count of the round, never lowered |
| `store.progress.last = {subject, level}` | `progress.json` | Where the device was last used |
| `store.count_round(round_id, attempts, correct, seconds, stars)` | `stats.json` | Adds one play to the round's anonymous counts |
| `store.add_minutes(subject, seconds)` | `stats.json` | Minutes of use, per ISO week and subject |

   Leaving a round early (`Play:leave`) still adds the minutes if more than
   five seconds were played. No stars and no round count are saved then.
8. **Pass it on.** After ten minutes of play in total (`SHARE_AFTER = 600`)
   the result screen also plays the "pass the device on" sentence and shows
   two children.

## From a CSV cell to the screen

### Speech

1. An author writes `say_fa` or `say_en` in a sheet.
2. `Pack.say` in `build.py` registers the text. `Speech.name` in `tts.py`
   gives the clip its path: language, a short slug and a hash of the text, for
   example `en/apple-a07ab697.ogg`. The same text is one clip, however often
   it is used.
3. `Speech.render` generates it with the chosen provider (piper, espeak,
   elevenlabs or silent), or takes it from `builder/.cache/audio/`. `f: … //
   m: …` makes two voices. Questions also get a slow variant,
   `….slow.ogg`.
4. `Speech._encode` calls ffmpeg: mono, 22.05 kHz, Ogg Vorbis quality 2.
5. The level file holds the path in a clip list such as `prompt_audio`.
6. In the app, `ctx.say(clips)` turns the paths into full paths
   (`packs.clips`) and `audio.say` plays them one after the other. With
   `slow = true` the slow file is used when it exists. A damaged clip is
   skipped.

Nobody has listened to the generated clips. See [speech.md](speech.md).

### Dari text

LÖVE 11 does not join Arabic-script letters and does not lay text out from
right to left. So the builder does it once:

1. An author types Dari normally, in logical order.
2. `shaping.shape` in `shaping.py` replaces the letters by their joined
   presentation forms (`arabic_reshaper`), puts each line into drawing order
   (`python-bidi`) and breaks lines for a 550 px column at 30 px, measured
   with the real font file. `shaping.letter_form` makes the four positional
   forms of a letter for `lf:` things.
3. `Pack.fa` checks that the device fonts have a glyph for every character.
   A missing glyph is a build error.
4. The level file carries a list of ready lines.
5. `text.fa` in the app prints each line as it is, right aligned. It never
   wraps again; a line that is too wide is narrowed.

This rendering has been checked on PC screenshots by the AI that wrote it. It
has not been read by a Dari reader on a device.

### English mode

`content/i18n/*.csv` map a Dari text to English. The builder writes
`en.json` into each pack: shaped Dari text → English (`texts`) and clip path →
caption (`clips`). `packs.load` fills `text.dict` and `packs.captions` from
them. When the locale is `en`, `text.fa` draws the English instead and
`love.draw` in `main.lua` shows the caption of the clip that is playing in a
band under the screen. See [english-mode.md](english-mode.md).

### Pictures

1. An author writes a picture name such as `apple`, or `p:sheep*5`.
2. `Pack.thing` turns it into `{"id": "apple", "img": "img/apple.png"}` and
   remembers the name.
3. `Pack.add_pictures` renders `content/pictures/apple.svg` with
   `images.render`: 160×160 px, or 400×300 px for names starting with
   `scene_`, reduced to 64 colours. A missing SVG becomes a labelled
   placeholder and a warning (an error with `--strict`).
4. In the app, `ui.thing` loads the PNG once (`ui.image`) and draws it;
   with `n` it draws the picture several times in rows, for counting.

## Packs: installed and updated safely

A pack is a zip with `manifest.json`, which lists every file with its SHA-256
(`Pack.write` in `build.py`). Formats: [pack-format.md](pack-format.md).

At every start `scenes/boot.lua` runs two functions of `core/packs.lua`:

`packs.install_updates`, for each zip in `update/`:

1. Mount it and `verify` it: the manifest must be readable, have format 1, a
   sane id and version, everything its kind needs (`usable`), and every
   listed file must match its checksum.
2. A pack that fails is noted in the log (`update rejected: …`) and removed.
   The installed pack stays.
3. A pack whose version is not higher than the installed one is removed
   without doing anything.
4. A good pack is written to `packs/<id>.v<version>.zip`, a new file name, and
   read back. Only if the copy is identical does it count.
5. One bad file never stops the others or the start of the app (`pcall`).

`packs.load`:

1. For each pack id, mounts the newest version that is usable. Older versions
   are removed only after a newer one has loaded, so a power cut between the
   steps leaves a working pack.
2. Sorts learner packs into `packs.subjects[subject][level]`. An optional
   pack (for example `garden-4-rights`) adds its games to that level of that
   place.
3. Loads the `core` strings and the English mode tables.

The launcher `Setara.sh` moves zips from `setara/update/` on the card into the
app's own `update/` folder before LÖVE starts.

`tests/update/run.sh` exercises this with a good newer pack, a pack cut off
half way, a pack with one damaged file, an empty shell and a pack that is
already installed.

## Where data is stored

The launcher sets `XDG_DATA_HOME` to the card folder's `data/`, so LÖVE's
save directory is on the card:

```text
dist/card/setara/data/love/setara/
  packs/<pack>.v<version>.zip    installed packs
  update/                        packs waiting to be checked
  data/progress.json (+ .bak)    stars, settings, last place, teacher's lesson
  data/stats.json    (+ .bak)    anonymous counts
  data/buttons.json              learned button map, if a pad was calibrated
  shots/                         screenshots, test runs only
  english, calibrate, start.png  optional switches a helper can put here
```

`store.lua` writes each file to `<name>.tmp` and renames it over the old one.
At every start a file that reads well refreshes its `.bak`. A damaged file
falls back to the backup, then to empty. Only that file resets.

The exact fields are listed in [privacy-and-safety.md](privacy-and-safety.md).

## The test driver

`main.lua` has a small driver for scripted runs. When the environment variable
`SETARA_SCRIPT` names a Lua file, the file runs as a coroutine next to the app
and gets one argument, a table:

| Function | Does |
| --- | --- |
| `t.press(button)` | Presses and releases a button |
| `t.hold(button)`, `t.release(button)` | For holding L and R |
| `t.wait(seconds)` | Lets the app run |
| `t.shot(name)` | Saves the 640×480 canvas to `shots/<name>.png` in the save folder |
| `t.skip_tutorial()` | Leaves the first-run tutorial if it is showing |
| `t.start_round(pack, game, index, {pair, review})` | Jumps straight into a round and returns the play scene |
| `t.top()`, `t.app` | The top scene and the app table, for assertions |
| `t.record(on)`, `t.mark(name)` | Used by the film tour |

Other variables: `SETARA_SPEED` (time factor), `SETARA_SEED` (fixed random
seed), `SETARA_LOCALE=en` (English mode), `SETARA_RECORD` (save every frame,
for `tools/film/make.py`). A script error ends the app with exit code 1.

`tools/shoot.sh` runs one script under `xvfb-run` with a null audio device.
`tools/test.sh` runs every script in `tests/` and then
`tests/update/run.sh`.

| Script | Covers |
| --- | --- |
| `tests/smoke.lua` | Tutorial, home, a place, a round starts |
| `tests/<engine>.lua` (nine files) | Full rounds of each engine, alone and in pair mode, with wrong answers, X and Y |
| `tests/teacher.lua` | Opens and uses every teacher tool |
| `tests/pause_resume.lua` | Pausing during speech never leaves a round standing |
| `tests/fuzz_rounds.lua` | Opens every round of every installed pack and presses random buttons: nothing may crash |
| `tests/update/run.sh` | Installing packs, including damaged ones |
| `builder/tests/test_builder.py` | The builder (pytest) |

A passing test says the app did not crash. It does not say the screen is
right, that the Dari is right, or that the audio is right.

## Other tools

| Tool | Does |
| --- | --- |
| `tools/picture_list.py [--missing]` | Lists the pictures the sheets use, with their drawing briefs |
| `tools/contact_sheet.py out.png name …` | Renders pictures at about the size a child sees them |
| `tools/maps.py` | Draws the map pictures of the geography pack from Natural Earth data |
| `tools/read_stats.py stats.json` | Summarises the anonymous counts of a device |
| `tools/content_table.py` | Rewrites the content table in `README.md` from the built packs |
| `tools/web/make_web.py` | Builds the browser version ([hosting.md](hosting.md)) |
| `tools/film/make.py` | Makes an introduction video from the app playing itself |
| `content/math/generate.py` | Generates the math sheets; do not edit those CSVs by hand |

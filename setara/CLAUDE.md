# Setara

Offline learning app for cheap Linux game handhelds, used in village
classrooms in Afghanistan by children (about 6 to 14, many cannot read yet)
and by teachers with little or no English. See `README.md` for the layout and
status. The product spec is a Claude Doc and the source of truth; read it with
the Claude Docs tools, not a web fetch:
https://claude.ai/code/artifact/2fe534af-594e-4b77-9ced-43470156379c

## Rules that come from the spec

These are product decisions, not preferences. Do not trade them away for
convenience.

- **Audio first.** Every instruction, word and question is spoken. Nothing may
  depend on the child reading. A prompt without audio is a bug.
- **No personal data.** No names, photos, voice recordings, location, school
  identifiers or profiles are stored, ever. Stats are anonymous counts with no
  timestamp finer than the week.
- **No network in version 1.** The app never opens a connection. Updates
  arrive as files on the SD card.
- **Eight buttons, no typing.** D-pad, A, B, X, Y, L, R, Start. Engines get
  button names from `app/core/input.lua`, never raw keys.
- **Screen is 640×480 at 3.5 inches.** Latin text at least 24 px, Dari at
  least 30 px, at most four answer choices on screen.
- **Weak hardware.** 1 GB RAM, slow quad-core. No video, no shaders, nothing
  allocated per frame. No microphone exists.
- **Same app on device and PC.** Depend only on LÖVE 11; no native extensions,
  no FFI.
- **Dari is shaped at build time.** The builder outputs glyphs in drawing
  order with line breaks fixed; the device only draws them. Do not add runtime
  shaping or bidi to the app, and do not move to LÖVE 12 without redoing this.
- **Data-driven.** One engine per mechanic, levels as JSON. New content must
  not need new code.
- **Nothing breaks the device.** A damaged pack is ignored and the old one
  stays. A corrupted data file resets only that file. Progress and stats
  survive every update. A crash restarts the app.
- **Gentle.** No lives, no game over, no ranking of children, no timer that
  punishes. Wrong answers come back later in the round.
- **Neutral.** No third-party games, branding or organisation logo.
- **Balanced.** Stories, names, voices and pictures show girls and boys in
  equal measure.

## How it fits together

- `content/` holds the sources: CSV sheets per pack, SVG pictures. Format:
  `docs/authoring.md`.
- `builder/` turns them into packs: validates, generates speech (cached),
  shapes Dari, renders pictures, writes checksummed zips to `packs/`.
- `image/make_card.py` assembles `dist/card/setara/`, the folder that goes on
  the SD card and also runs on a PC.
- `app/` is the LÖVE app. `main.lua` runs a scene stack (`app.push`,
  `app.pop`, `app.replace`, `app.home`). `scenes/` are the learner screens,
  `teacher/` is teacher mode, `engines/` the ten game mechanics, `core/` the
  shared modules. The engine interface is described at the top of
  `app/engines/init.lua`; `listen_pick.lua` is the reference engine.
- Formats that come out of the builder: `docs/level-format.md`,
  `docs/pack-format.md`.

## Conventions

- Engine ids: `listen_pick`, `pairs`, `catch`, `builder`, `say_it`, `story`,
  `journey`, `market`, `duel`, `sorter`.
- Subject codes: `en`, `fa` (Dari reading), `math`, `garden`. Round ids look
  like `en-1-03-a`: pack, round, the game's letter.
- Audio is Ogg Vorbis, not the Opus of the spec: LÖVE 11 cannot decode Opus.
- Waiting for speech: watch `audio.busy()` in `update` rather than rely on
  `on_done`. A speech that is stopped or replaced never calls `on_done`. The
  pause menu holds speech and lets it carry on, but X, Y and leaving a screen
  cut it off.
- Never call `app.pop` or `app.push` from a scene's `enter`.
- Content sources are the CSVs. Math is the exception: edit
  `content/math/generate.py` and run it; do not hand-edit math CSVs.
- When a format changes, update the builder, the app and the doc in one
  change.
- Code is MIT, content is CC BY-SA 4.0. Add no copyrighted songs, pictures or
  recordings. Fonts are under the SIL Open Font License.

## Commands

```sh
cd builder && python3 -m setara_builder.cli validate   # check every sheet, fast
cd builder && python3 -m setara_builder.cli build      # write packs/*.zip
python3 image/make_card.py                             # write dist/card/setara/
dist/card/setara/Setara.sh                             # run it (needs love 11)
tools/test.sh                                          # every test, headless
tools/shoot.sh tests/smoke.lua 4 /tmp/some-save-dir    # one script, with screenshots
python3 tools/picture_list.py --missing                # pictures still to draw
```

`builder/get_voices.sh` downloads the stand-in speech models. Without them the
builder falls back to espeak-ng, then to silence. See `docs/speech.md`.

## Testing

Tests are Lua scripts in `tests/` that drive the real app through its buttons
(`press`, `wait`, `shot`, `start_round`; see the test driver in `main.lua`).
They run headless under xvfb with a null audio device and write screenshots.
Look at the screenshots after changing anything visible: a test that passes
says the app did not crash, not that the screen is right.

`tests/fuzz_rounds.lua` opens every round of every pack. Run it after any
change to an engine or to the builder's output. `tests/update/run.sh` covers
installing packs from the card, including damaged ones.

Nothing has been run on a real handheld yet, and nobody has listened to the
audio. Do not describe either as verified.

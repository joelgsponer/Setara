# Setara

Offline learning app for cheap Linux game handhelds, used in village
classrooms in Afghanistan. See `README.md` for the layout. The product spec is
a Claude Doc and the source of truth; read it with the Claude Docs tools, not
a web fetch: https://claude.ai/code/artifact/2fe534af-594e-4b77-9ced-43470156379c

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
- **Eight buttons, no typing.** D-pad, A, B, X, Y, L, R, Start. Engines use
  the button names in `app/shell/input.lua`, never raw keys.
- **Screen is 640×480 at 3.5 inches.** Latin text at least 24 px, Dari at
  least 30 px, at most four answer choices on screen.
- **Weak hardware.** 1 GB RAM, slow quad-core. No video. Small PNGs, Opus
  audio at 24 kbit/s. No microphone exists.
- **Same app on device and PC.** Depend only on LÖVE; no native extensions.
- **Dari is shaped at build time.** The builder outputs glyphs in draw order
  with line breaks fixed; the device only draws them. Do not add runtime
  shaping or bidi to the app.
- **Data-driven.** One engine per mechanic, levels as JSON. New content must
  not need new code.
- **Nothing breaks the device.** A damaged pack is ignored and the old one
  stays. A corrupted data file resets only that file. Progress and stats
  survive every update.
- **Gentle.** No lives, no game over, no ranking of children. Wrong answers
  come back later in the round.
- **Neutral.** No third-party games, branding or organisation logo.
- **Balanced.** Stories, names, voices and pictures show girls and boys in
  equal measure.

## Conventions

- Engine ids: `listen_pick`, `pairs`, `catch`, `builder`, `say_it`, `story`,
  `journey`, `market`, `duel`, `sorter`.
- Subject codes: `en`, `fa` (Dari), `math`, `garden`. Level ids look like
  `en-1-03-a`.
- Formats in `docs/` are drafts. When an engine or the builder settles a
  point, update the doc and the schema in the same change.
- Code is MIT, content is CC BY-SA 4.0. Add no copyrighted songs, pictures or
  recordings.

## Commands

```sh
love app                                          # run the app
cd builder && python3 -m setara_builder.cli all   # run the builder (stub)
```

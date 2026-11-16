# Setara

One offline learning app ("star" in Dari) for a CHF 35–50 Linux game handheld.
It serves a teacher running a class of up to 50 through a loudspeaker, and
children playing alone or in pairs. Four subjects in levels: English, Dari
reading, math, and health and environment.

Version 1 is one SD card folder, identical on every device, with all content
on it. It never needs a connection, stores no personal data, and is fully
spoken: a child who cannot read can use it from the first minute.

The product spec is the source of truth:
https://claude.ai/code/artifact/2fe534af-594e-4b77-9ced-43470156379c

## Status

The software of the spec is built and runs on a PC. It has **not** been run on
a handheld, **nobody has listened to the audio**, and **no Dari speaker,
teacher or health professional has reviewed the content**. Those are the
gates of the spec's own roadmap, and they are still ahead.

| Part | State |
| --- | --- |
| App shell: valley home, places, levels, pause, tutorial, "find my level" | Built, tested headless |
| Ten game engines | Built, each with a test that plays full rounds |
| Teacher mode, all nine tools | Built, tested headless |
| Pack builder: validation, speech, Dari shaping, pictures, checksums | Built, unit tested |
| Card updates, damaged-pack handling, crash restart | Built, tested |
| Content | See the table below |
| Pictures | 1414 drawn as SVG, none reviewed locally |
| Speech | Stand-in local voices. ElevenLabs path written, never run |
| English mode for testers: English text and captions | Built. Translated by Claude, not checked by a native speaker |
| Browser version, with a Dockerfile for hosting | Built, tested in Chromium and as a Docker image |
| Introduction video (`tools/film/make.py`) | Built from the app playing itself |
| Running on the RG35XX H and R36S | Not done. See [docs/device.md](docs/device.md) |
| Direct updates over Wi-Fi, buzzers | Not in version 1, as the spec says |

### Content

<!-- content -->
| Pack | Games | Rounds | Size |
| --- | --- | --- | --- |
| `core` app strings and tutorial | | | 1 MB |
| `en-1-letters` English letters: the whole alphabet | 13 | 69 | 60 MB |
| `en-1` English 1: Hello | 15 | 123 | 44 MB |
| `en-2` English 2: My world | 16 | 129 | 55 MB |
| `en-3-stories` English story book | 4 | 16 | 31 MB |
| `en-3` English 3: My day | 15 | 104 | 35 MB |
| `en-4` English 4: At the bazaar | 16 | 90 | 34 MB |
| `en-5` English 5: Health and help | 13 | 132 | 56 MB |
| `en-6` English 6: The wider world | 13 | 129 | 67 MB |
| `fa-1-alphabet` The whole alphabet | 9 | 49 | 35 MB |
| `fa-1` Dari 1: Sounds and first letters | 9 | 68 | 42 MB |
| `fa-2` Dari 2: The whole alphabet | 9 | 68 | 42 MB |
| `fa-3-stories` Dari story book | 4 | 16 | 22 MB |
| `fa-3` Dari 3: Syllables and words | 10 | 66 | 27 MB |
| `fa-4` Dari 4: Sentences | 10 | 56 | 26 MB |
| `fa-5` Dari 5: Stories | 8 | 64 | 48 MB |
| `fa-6` Dari 6: Fluent reader | 11 | 63 | 44 MB |
| `garden-1` Garden 1: Me | 12 | 39 | 20 MB |
| `garden-2-nature` Nature and how things work | 10 | 43 | 26 MB |
| `garden-2` Garden 2: My Home | 13 | 36 | 21 MB |
| `garden-3-village` My village: staying well, land and weather | 11 | 46 | 40 MB |
| `garden-3` Health 3: First aid | 8 | 25 | 22 MB |
| `garden-4-rights` My rights, your rights | 6 | 13 | 8 MB |
| `garden-4-world` The world, Switzerland and Basel | 9 | 32 | 24 MB |
| `garden-4` Health and environment 4: My future | 15 | 40 | 25 MB |
| `guide-en-1` app strings and tutorial | | | 23 MB |
| `guide-en-2` app strings and tutorial | | | 22 MB |
| `guide-en-3` app strings and tutorial | | | 26 MB |
| `guide-en-4` app strings and tutorial | | | 24 MB |
| `guide-en-5` app strings and tutorial | | | 28 MB |
| `guide-en-6` app strings and tutorial | | | 28 MB |
| `guide-fa-1` app strings and tutorial | | | 16 MB |
| `guide-fa-2` app strings and tutorial | | | 17 MB |
| `guide-fa-3` app strings and tutorial | | | 14 MB |
| `guide-fa-4` app strings and tutorial | | | 14 MB |
| `guide-fa-5` app strings and tutorial | | | 21 MB |
| `guide-fa-6` app strings and tutorial | | | 23 MB |
| `guide-garden-1` app strings and tutorial | | | 11 MB |
| `guide-garden-2` app strings and tutorial | | | 17 MB |
| `guide-garden-3` app strings and tutorial | | | 28 MB |
| `guide-garden-4` app strings and tutorial | | | 19 MB |
| `guide-math-1` app strings and tutorial | | | 12 MB |
| `guide-math-2` app strings and tutorial | | | 11 MB |
| `guide-math-3` app strings and tutorial | | | 12 MB |
| `guide-math-4` app strings and tutorial | | | 14 MB |
| `guide-math-5` app strings and tutorial | | | 15 MB |
| `guide-math-6` app strings and tutorial | | | 13 MB |
| `math-1` Math 1: Counting to 20 | 10 | 71 | 48 MB |
| `math-2-puzzles` Logic Puzzles | 9 | 43 | 14 MB |
| `math-2` Math 2: Numbers to 100 | 10 | 70 | 60 MB |
| `math-3` Math 3: Numbers to 1,000 | 10 | 67 | 76 MB |
| `math-4` Math 4: Times Tables and Sharing | 11 | 63 | 64 MB |
| `math-5` Math 5: Large Numbers and Fractions | 12 | 63 | 75 MB |
| `math-6` Math 6: Percent, Ratio and Averages | 12 | 61 | 101 MB |
| `teacher-en-1` English 1 lessons | 20 lessons, Phrase Board, tips | | 10 MB |
| `teacher-en-2` English 2 lessons | 20 lessons, Phrase Board, tips | | 12 MB |
| **Total** | | **1954** | |
<!-- /content -->

Health 3 is the first-aid pack: burns, cuts, bites, nosebleed, choking, what
to do when someone collapses, and when to take a sick relative to the clinic.
Its facts and what was simplified are in `content/garden/3/SOURCES.md`.

Every level of the curriculum is written, with a teacher's guide for each.
Not written yet: classroom lesson scripts beyond English 2. The teaching design is in `docs/curriculum.md`. Most of
the content is days old and unchecked.

All of it is a first draft written by Claude. Before it reaches children it
needs what the spec asks for in section 9: review of text, audio and pictures
by a Dari-speaking educator, a check of the health content by someone
qualified, and a pilot with real children. This holds most of all for the first-aid
pack: it follows standard first-aid guidance as Claude understands it and has
not been seen by a health professional.

### Where this differs from the spec

- **Audio is Ogg Vorbis, not Opus.** LÖVE 11 cannot decode Opus. Pack sizes
  stay inside the spec's 5–15 MB (one pack is 16 MB).
- **Dari rendering is proven only on a PC screenshot**, read by Claude, not by
  a Dari reader on a device.
- **Authoring is CSV files**, one template per engine, rather than a shared
  spreadsheet with a sign-off column.
- **The card "image" is a folder** to copy onto a card that already has a
  firmware with LÖVE. A full firmware image waits for the firmware choice.
- **Brightness** in the pause menu dims the picture; it cannot reach the
  backlight from inside LÖVE.

## Run it

Needs [LÖVE 11.5](https://love2d.org), Python 3.11+, ffmpeg.

```sh
cd builder
pip install -e .[piper]        # builder and the stand-in speech engine
./get_voices.sh                # stand-in voices, about 190 MB, once
python3 -m setara_builder.cli build     # packs/*.zip (first run: about 20 minutes of speech)
cd ..
python3 image/make_card.py     # dist/card/setara/
dist/card/setara/Setara.sh     # run
```

To try it without Dari, start `dist/card/setara/Setara-English.sh` instead:
every text is in English and everything spoken has an English caption.

Keyboard: arrows = D-pad, Z = A, X = B, A = X, S = Y, Q/W = L/R, Enter =
Start, Esc = quit. Hold Q and W for two seconds on the home screen for
teacher mode.

## Layout

| Path | What | Built with |
| --- | --- | --- |
| `app/` | The app that runs on the device and on a PC | LÖVE 11 (Lua) |
| `app/core/` | Input, speech, text, saving, packs, the valley | |
| `app/scenes/` | Learner screens | |
| `app/engines/` | Ten game mechanics, one module each | |
| `app/teacher/` | Teacher mode | |
| `builder/` | Pack builder | Python |
| `content/` | Authored sources: sheets per pack, SVG pictures | CSV, SVG |
| `image/` | Assembles the SD card folder | Python |
| `tests/` | Scripts that drive the real app | Lua |
| `tools/` | Test runner, picture list, contact sheets, stats reader | |
| `docs/` | Authoring guide, formats, device guide, speech | |
| `packs/`, `dist/` | Built output (not committed) | |

## Documentation

- [Authoring content](docs/authoring.md)
- [Level files](docs/level-format.md)
- [Packs, the card and device data](docs/pack-format.md)
- [Putting it on a device](docs/device.md)
- [Speech](docs/speech.md)
- [English mode, for testers who do not read Dari](docs/english-mode.md)
- [In a browser, and hosting it](docs/hosting.md)

## Tests

```sh
tools/test.sh                        # all app tests, headless, with screenshots
cd builder && python3 -m pytest -q   # builder
```

## Licence

Code: MIT (`LICENSE`). Content: CC BY-SA 4.0 (`content/LICENSE.md`). Fonts:
Andika and Noto Naskh Arabic, SIL Open Font License (`app/assets/fonts/`).

# Getting started

From a fresh clone to the app running on a PC. All commands are run from the
`setara/` folder of the repository unless a line starts with `cd`.

This gets you the app on a PC. It has not been run on a handheld yet; the plan
for that is in [device.md](device.md).

## What you need

| Tool | Version | Used for |
| --- | --- | --- |
| [LÖVE](https://love2d.org) | 11.5 (11.4 also starts; not 12) | Running the app |
| Python | 3.11 or newer | The pack builder and the tools |
| ffmpeg | any recent, with `libvorbis` | Encoding speech, also for `--tts silent` |
| Cairo library | system package (`libcairo2` on Debian and Ubuntu) | Rendering the SVG pictures |
| piper voices | optional, about 190 MB | Stand-in speech |
| espeak-ng | optional | Robotic speech when piper is not installed |
| xvfb (`xvfb-run`) | optional, Linux | Running the tests without a window |

Do not use LÖVE 12. It shapes text by itself and would reverse the Dari lines
that the builder has already put in drawing order.

On Debian or Ubuntu:

```sh
sudo apt-get install python3 python3-pip ffmpeg libcairo2 espeak-ng xvfb
```

LÖVE 11.5 is a download from love2d.org (an AppImage on Linux). The package
`love` of your distribution works if it is version 11.

## 1. Install the builder

```sh
cd builder
pip install -e .            # the builder
pip install -e .[piper]     # optional: the builder plus the stand-in speech engine
cd ..
```

Optional, for speech you can listen to:

```sh
builder/get_voices.sh       # downloads the stand-in voices into builder/voices/, once
```

The voices are stand-ins. The Persian voice is Iranian, not Afghan, and it is
a man's voice. Nobody has listened to the clips they produce. See
[speech.md](speech.md).

## 2. Check the content

```sh
cd builder && python3 -m setara_builder.cli validate --quiet && cd ..
```

This reads every sheet, writes nothing and takes a few seconds. It ends with
`ok`, or it names the file and row of every problem. Without `--quiet` it also
lists the warnings (for example pictures that are not drawn yet).

## 3. Build the packs

```sh
cd builder && python3 -m setara_builder.cli build && cd ..
```

This writes one zip per pack into `packs/`.

| Variant | Command (inside `builder/`) | Time |
| --- | --- | --- |
| With the piper voices | `python3 -m setara_builder.cli build` | First run: about 20 minutes of speech generation, according to the project README. Later runs reuse `builder/.cache/` and take seconds to a minute |
| Without speech | `python3 -m setara_builder.cli build --tts silent` | About 6 minutes for the 14 packs that existed then (there are 25 now, so expect about twice that) on the machine this guide was written on (ffmpeg still encodes every clip). Every clip is half a second of silence |
| Robotic speech | `python3 -m setara_builder.cli build --tts espeak` | Faster than piper |
| One pack only | `python3 -m setara_builder.cli build --only en-1` | `--only` can be given several times |
| The smallest thing that runs | `python3 -m setara_builder.cli build --tts silent --only core --only en-1` | Under a minute on the machine this guide was written on |

Notes:

- Without `--tts` the builder picks piper when the package and the voices are
  there, then espeak-ng, then silence.
- The `core` pack (menus, guide, tutorial) is always needed. The app does not
  start without it.
- Pack ids are the `pack` field of each `pack.json`: `core`, `en-1`, `en-2`,
  `fa-1`, `fa-2`, `math-1`, `math-2`, `math-3`, `garden-1`, `garden-2`,
  `garden-3`, `garden-4-rights`, `garden-4-world`, `teacher-en-1`.
- A silent build is good for trying the screens. In Dari mode you will hear
  nothing. Use English mode, where everything spoken has a caption.
- A pack with errors is not written. The other packs are.

## 4. Make the card folder

```sh
python3 image/make_card.py
```

This writes `dist/card/setara/`: the app as `setara.love`, every pack from
`packs/`, and the launchers. It is the folder that would go on the SD card,
and it also runs on a PC. Running it again replaces the app and the packs and
keeps the saved stars.

## 5. Run it

```sh
dist/card/setara/Setara.sh            # in Dari
dist/card/setara/Setara-English.sh    # English mode
```

The launcher looks for `love` next to itself, in `/usr/bin`, in
`/usr/local/bin` and on the `PATH`. If your LÖVE is somewhere else, name it:

```sh
SETARA_LOVE=/path/to/love-11.5-x86_64.AppImage dist/card/setara/Setara.sh
```

On Windows use `Setara.bat` or `Setara-English.bat` in the same folder. They
expect LÖVE 11 in `%ProgramFiles%\LOVE`. The Windows launchers have not been
tested by the author of this guide.

English mode replaces the Dari on the screen with English and shows an
English caption for everything spoken. It exists for testers. Its English was
written by the same AI that wrote the Dari; it is not a check of the Dari. You
can also switch the language in the pause menu (Enter, the row with the
globe). See [english-mode.md](english-mode.md).

The first start shows a one-minute tutorial of the buttons. Enter skips it.

## Keyboard controls

| Key | Button on the handheld | Does |
| --- | --- | --- |
| Arrow keys | D-pad | Move, or answer directly |
| Z or Space | A | Yes, choose, continue |
| X or Backspace | B | Back one step |
| A | X | Say it again, slowly |
| S | Y | Explain in Dari |
| Q | L | |
| W | R | |
| Enter | Start | Pause: volume, brightness, language, home |
| F11 | | Full screen |
| Esc | | Quit |

Hold Q and W together for two seconds on the home screen to open teacher
mode. See [teacher-mode.md](teacher-mode.md).

A game pad works too. If the system does not know the pad, the app opens a
calibration screen by itself.

## Run the tests

Builder tests (fast, no LÖVE needed):

```sh
cd builder && python3 -m pytest -q && cd ..
```

App tests. They drive the real app through its buttons, headless, and write
screenshots. They need Linux with `xvfb-run`, built packs and the card folder
from steps 3 and 4:

```sh
SETARA_LOVE=/path/to/love tools/test.sh
```

`tools/shoot.sh` has a default path for LÖVE that only exists on the original
development machine, so set `SETARA_LOVE` (to `love` if it is on your `PATH`).
The run took about 5 minutes on that machine because one script opens every round of every
pack. It prints `ok` or `FAIL` per script and the folder with the
screenshots. Some scripts start rounds of particular packs (`en-1`, `fa-1`,
`math-1`, `math-2`, `garden-1` and others), so run them against a full build.

One script alone:

```sh
SETARA_LOVE=/path/to/love tools/shoot.sh tests/smoke.lua 4 /tmp/setara-save
```

The second argument is the speed (4 times real time). The third is a save
folder; it must hold the packs, so copy them first:

```sh
mkdir -p /tmp/setara-save/love/setara
cp -r dist/card/setara/data/love/setara/packs /tmp/setara-save/love/setara/
```

Screenshots land in `/tmp/setara-save/love/setara/shots/`. Look at them: a
test that passes says the app did not crash, not that the screen is right.

## Common problems

| What you see | Cause and fix |
| --- | --- |
| `no core pack in packs/: run the builder first` from `make_card.py` | Build the packs first (step 3). `core` must be among them |
| "No content packs found." on the start screen | The card folder has no packs. Build, then run `make_card.py` again |
| `love: not found` | LÖVE is not on the `PATH`. Set `SETARA_LOVE` |
| Dari text is mirrored or broken | You are running LÖVE 12. Use 11.5 |
| No sound in Dari mode | The packs were built with `--tts silent`, or the piper voices are missing and espeak-ng is not installed |
| `ffmpeg` errors during the build | ffmpeg is missing or was built without `libvorbis` |
| `OSError: no library called "cairo"` or similar | Install the Cairo system library (`libcairo2`) |
| Pictures are grey cards with a name | That picture is not drawn yet. The builder made a placeholder and printed a warning. `python3 tools/picture_list.py --missing` lists them |
| A changed sheet does not show up in the app | Build again and run `make_card.py` again. The app reads the packs in the card folder, not `content/` |
| The tutorial comes back, or stars are gone | You started with a different save folder. Stars live in `dist/card/setara/data/love/setara/data/progress.json` |
| Tests fail at once with a path under `/opt/tools` | `SETARA_LOVE` is not set |

## Where to go next

- How the parts fit: [architecture.md](architecture.md)
- The games: [games.md](games.md)
- Writing content: [authoring.md](authoring.md)
- In a browser: [hosting.md](hosting.md)

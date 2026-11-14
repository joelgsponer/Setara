# Setara

One offline learning app ("star" in Dari) for a CHF 35–50 Linux game handheld.
It serves a teacher running a class of up to 50 through a loudspeaker, and
children playing alone or in pairs. Four subjects in levels: English, Dari
reading, math, and health and environment.

Version 1 is one SD card image, identical on every device, with all content
on it. It never needs a connection.

The product spec is the source of truth:
https://claude.ai/code/artifact/2fe534af-594e-4b77-9ced-43470156379c

## Status

Scaffold. The structure, the level-file format draft and stubs exist; no game
is implemented. Next is phase 0 of the spec's roadmap: boot a LÖVE app on both
devices, prove Dari rendering, prove pack install, and make Listen and Pick
playable with 10 English words.

## Layout

| Path | What | Built with |
| --- | --- | --- |
| `app/` | The app that runs on the device and on a PC | LÖVE 11 (Lua) |
| `app/shell/` | Menus, shared progress, settings, card update | |
| `app/engines/` | Ten reusable game mechanics, one module each | |
| `builder/` | Pack builder: validates, generates speech, shapes Dari, packs | Python 3.11+ |
| `content/` | Authored sources, one folder per subject | Spreadsheets |
| `schemas/` | JSON Schemas for level files | |
| `image/` | Scripts for the SD card image | |
| `docs/` | Level-file and pack formats | |
| `packs/` | Built packs (not committed) | |

## Run

```sh
love app                      # the app, in a 640×480 window
cd builder && python3 -m setara_builder.cli all   # the builder (stub)
```

Keyboard on a PC: arrows = D-pad, Z = A, X = B, A = X, S = Y, Q/W = L/R,
Enter = Start, Esc = quit.

## Formats

- [Level files](docs/level-format.md)
- [Content packs and device data](docs/pack-format.md)

## Licence

Code: MIT (`LICENSE`). Content: CC BY-SA 4.0 (`content/LICENSE.md`).

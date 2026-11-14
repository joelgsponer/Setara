# Putting Setara on a device

Nothing in this guide has been run on real hardware yet. The app has only
been run on a PC, headless and in a window. Treat this as the plan for phase 0
of the spec, to be corrected as soon as the two test devices arrive.

## What the app needs

- **LÖVE 11.5** for the device's CPU (64-bit ARM on both the Anbernic RG35XX H
  and the R36S). Do not use LÖVE 12: it shapes text by itself and would
  reverse the Dari lines the builder has already put in drawing order.
- A way to start `Setara.sh` at boot or from the firmware's menu.
- About 100 MB on the card for version 1's content.

Community firmwares that ship LÖVE through PortMaster (muOS, Knulli, ArkOS,
ROCKNIX) are the likely route. Which firmware gives the cleanest boot straight
into the app is the first open point of phase 0.

## Making the card folder

```sh
cd builder && python3 -m setara_builder.cli build    # packs/*.zip
cd .. && python3 image/make_card.py                  # dist/card/setara/
```

Copy `dist/card/setara/` to the card. Start `Setara.sh`. If the firmware's
LÖVE is not on the `PATH`, put the `love` binary next to `Setara.sh` or set
`SETARA_LOVE` in the script.

The same folder runs on a PC: `./Setara.sh` on Linux, `Setara.bat` on Windows
(LÖVE 11 installed).

## First start on a new device model

1. **Buttons.** If the system does not know the pad, the app opens a
   calibration screen by itself: it lights each button on a picture of the
   device and remembers what is pressed. To run it again, put an empty file
   named `calibrate` in `setara/data/love/setara/`. The result is
   `data/buttons.json` on the card; copy it to the other cards of the same
   device model.
2. **Tutorial.** A spoken one-minute tour of the buttons. Start skips it.
3. **Check in a real room:** loudness and clarity through the speaker at the
   back, Dari text read by a Dari reader, battery life over a lesson.

## Controls

| Button | Does |
| --- | --- |
| D-pad | Move, or answer directly |
| A | Yes, choose, continue |
| B | Back one step |
| X | Say it again, slowly |
| Y | Explain in Dari |
| L / R | Hold both for two seconds on the home screen: teacher mode |
| Start | Pause: volume, brightness, home. In teacher mode also the class size |

On a PC: arrows, Z = A, X = B, A = X, S = Y, Q = L, W = R, Enter = Start,
F11 = full screen, Esc = quit.

"Brightness" dims the picture. It does not change the backlight; that stays
with the firmware's own hotkeys.

## Updating

Copy new pack zips into `setara/update/` and start the app. See
[pack-format.md](pack-format.md). The version number of the app is shown on
the start and home screens and in `VERSION.txt`.

## At a field visit

- Copy `setara/data/love/setara/data/stats.json` from each card and read it
  with `python3 tools/read_stats.py stats.json`.
- A neutral start picture can replace the bird: put a 640×480 `start.png`
  into `setara/data/love/setara/`.

## If something breaks

- **The card is dead:** write the card folder to a new branded card.
- **A pack is damaged:** copy that pack's zip into `update/` again.
- **Stars are gone:** `progress.json` was damaged twice over (file and
  backup). Only that file resets; the content is untouched.
- **The app crashed:** it restarts by itself and notes the cause in the log
  inside `stats.json`.

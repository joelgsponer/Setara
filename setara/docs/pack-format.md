# Content packs, the card and device data

## A pack

A pack is a zip file: one per subject and level (`en-1`, `fa-2`, `math-3`,
`garden-1`), one per set of teacher lessons (`teacher-en-1`), and `core` with
the app's own strings. Learner packs are 5 to 22 MB; `core` is 1 MB.

```
en-1.zip
  manifest.json
  review.json              questions for the warm-up and "find my level"
  levels/en-1-13-a.json    one file per round (see level-format.md)
  img/apple.png            pictures, 160 px (scenes 400×300)
  en/apple-a07ab697.ogg    English speech
  fa/x-b6837856.ogg        Dari speech
```

### manifest.json

```json
{
  "format": 1,
  "pack": "en-1",
  "kind": "learner",
  "version": 1,
  "optional": false,
  "title_en": "English 1: Hello",
  "title_fa": ["…"],
  "subject": "en",
  "level": 1,
  "games": [
    {"id": "word_stall", "engine": "listen_pick", "title_en": "Word Stall",
     "title_fa": ["…"], "title_audio": ["fa/…ogg"], "icon": {"id": "apple", "img": "img/apple.png"},
     "v1": true, "rounds": ["en-1-01-a", "en-1-02-a"]}
  ],
  "review": "review.json",
  "files": {"levels/en-1-01-a.json": "sha256:…", "img/apple.png": "sha256:…"}
}
```

- `kind`: `guide` (a teacher's guide: `guide` names `guide.json`, a list of
  chapters with pages, and `chapters` lists their titles), `learner`, `teacher` (has `lessons`, `phrases`, `tips` instead of
  `games`) or `core` (has `strings`).
- `files` lists every file of the pack with its SHA-256. This is what makes a
  pack self-checking.
- `optional: true` marks packs shipped only where the local team approves them.
- `format` is 1. The app ignores packs with another format.

A pack is ready for a signature (for later downloads) without a format change:
a signature over `manifest.json` covers every file through `files`.

## On the SD card

`image/make_card.py` writes this folder. It is the same on every device.

```
setara/
  setara.love            the app
  Setara.sh              launcher (handheld firmware, Linux PC)
  Setara.bat             launcher (Windows PC)
  VERSION.txt
  update/                drop new packs here
  data/love/setara/
    packs/en-1.v1.zip    installed packs: <pack>.v<version>.zip
    update/              where the launcher hands new packs to the app
    data/progress.json   stars, last place, settings
    data/stats.json      anonymous counts
    data/buttons.json    learned button map, if the pad needed calibrating
```

The launcher sets `XDG_DATA_HOME` so that LÖVE keeps everything on the card.

## Updates in version 1

1. A helper copies new pack zips into `setara/update/` from a PC, a phone with
   a card reader, or another card.
2. At the next start the app checks every file of each new pack against the
   checksums in its manifest.
3. A good pack is copied into `packs/` under its new version name and read
   back. Only then is the old version removed. If power is cut in between,
   the old pack is still there.
4. A damaged pack is ignored and removed, and the old one stays. So is an
   empty shell, a pack that lacks what its kind needs, and a pack whose
   version is not higher than the installed one. An installed pack is never
   written over. A rejection is noted in the log inside `stats.json`, without
   the file's name.
5. `data/` is never touched by an update.

If a card fails completely, write the card folder to a new card. Nothing else
needs setting up.

This is covered by `tests/update/run.sh`.

## Device data

`progress.json`: one shared record per device. Stars per round, the level last
chosen per subject, the teacher's current lesson, volume, brightness, class
size. There are no profiles.

`stats.json`: anonymous counts.

| Field | What |
| --- | --- |
| `device` | A random id. The team maps it to a classroom on paper, or not at all |
| `weeks` | Minutes of use per ISO week and per subject or `teacher` |
| `rounds` | Per round: plays, answers, first-try right answers, minutes, stars |
| `checks` | Quick Check per lesson: right answers out of class size times the number of questions |
| `teacher` | Lessons finished, previews run, tools opened, course lesson reached |
| `log` | The last 30 problems: app version, a short code, the week |

No names, no timestamps finer than the week. Version 1 uploads nothing: the
team copies the file at field visits and reads it with `tools/read_stats.py`.

Each file is written to a new file that is then swapped in, so a power cut
leaves the old state or the new one. At every start a file that reads well
refreshes its backup (`.json.bak`). A damaged file falls back to the backup
and then to empty: it resets only that file.

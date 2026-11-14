# Content pack format

Status: **draft proposal**. The product spec fixes only this much: a pack is a
zip of 5–15 MB holding level files (JSON), images (PNG) and audio (Opus), one
pack per subject and level, checked against a checksum at start, and ready for
a signature check when direct updates arrive later.

## Layout inside a pack

```
en-1.zip
  manifest.json
  levels/en-1-03-a.json
  img/apple.png
  en/apple.opus          English audio
  fa/apple_help.opus     Dari audio
```

## manifest.json (proposal)

```json
{
  "format": 1,
  "pack": "en-1",
  "subject": "en",
  "level": 1,
  "version": 3,
  "optional": false,
  "files": { "levels/en-1-03-a.json": "sha256:…" }
}
```

`optional: true` marks packs shipped only where the local team approves them.

## On the SD card (proposal)

```
setara/
  app/                the LÖVE app
  packs/              installed packs
  update/             drop new packs here; installed at next start
  data/progress.json  shared stars and last place visited
  data/stats.json     anonymous counts
```

## Update rules (from the spec)

- At start the app checks each pack in `update/` against its checksum and
  installs it. A damaged pack is ignored and the old one stays.
- `data/` survives every update.
- A corrupted data file resets only that file, never the device.
- Version 1 uses no network. Signatures and Wi-Fi download come later; the
  format must not need changing for them.

## Device data

- `progress.json`: one shared record per device, stars per level and the last
  place visited. No profiles.
- `stats.json`: anonymous counts per level and lesson (attempts, correct,
  minutes). No names, no timestamps finer than the week.

## Open points

- Where the checksum of the pack as a whole lives (sidecar file or a
  manifest of manifests in the update folder).
- Signature scheme for later direct updates.

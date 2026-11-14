# English mode

For testers, partners and funders who do not read or understand Dari. The app
is the same; only what is shown changes:

- Every Dari text on the screen is replaced by English: menus, game titles,
  teacher instructions, story captions, basket labels.
- Everything spoken gets an English caption along the bottom of the screen
  while it plays. The speech itself stays as it is (Dari or English).
- Dari that is the thing being learned stays Dari: letters, letter shapes,
  numerals, and the words on tiles and cards. Words get their meaning in
  small print underneath.

It is not a product for English-speaking children. It exists so that the
whole app can be tried, and the content judged, by people who cannot read it.

## Switching it on

- **Pause menu** (Start): the row with the globe switches between دری and
  English. The choice is remembered on the card.
- **Launcher:** `Setara-English.sh` or `Setara-English.bat` in the card folder.
- **On a device without a keyboard:** put an empty file named `english` into
  `setara/data/love/setara/`.

## Where the English comes from

`content/i18n/*.csv`, two columns: `fa` (the Dari text exactly as in the
sheet) and `en`. Pairs a sheet already carries are found by themselves (a
word and its meaning in `items.csv`, a title in both languages). The math
table is written by `content/math/generate.py` together with the sheets.

```sh
cd builder
python3 -m setara_builder.cli validate --untranslated /tmp/todo.csv
```

lists every Dari text without English, and where it is used. A text without
English is simply shown in Dari.

The English was written by Claude from the Dari, and the Dari was written by
Claude too. It tells a reader what the content is meant to say. It is not a
check of the Dari by a native speaker.

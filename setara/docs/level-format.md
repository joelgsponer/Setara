# Level file format

A level file is one JSON object: one playable round of one engine. Level files
are never written by hand. The pack builder generates them from the sheets in
`content/` (see [authoring.md](authoring.md)) and checks them as it does.

Inside a pack they sit at `levels/<id>.json`.

## Round

```json
{
  "engine": "listen_pick",
  "id": "en-1-13-a",
  "game": "word_stall",
  "intro_audio": ["fa/x-1a2b3c4d.ogg"],
  "items": [ ... ]
}
```

| Field | Meaning |
| --- | --- |
| `engine` | One of the ten engine ids |
| `id` | `<pack>-<round>-<letter>`: pack `en-1`, round `13` from the sheet, the game's letter `a` |
| `game` | The game this round belongs to |
| `intro_audio` | The guide's spoken Dari instruction, played before the round |
| `items` | The round's questions, pairs or pages, in order |
| `baskets` | Sorter only: the two to four baskets |

A round is two to four minutes: six to ten items.

## Shared building blocks

**Clip lists.** Every audio field is a list of paths inside the pack, played in
order. Audio is Ogg Vorbis, mono, 22.05 kHz. A clip `en/apple-a07ab697.ogg`
may have a slow variant next to it, `en/apple-a07ab697.slow.ogg`, used when
the child presses X.

**Things.** A choice, tile, card or basket is a *thing*:

| Thing | Drawn as |
| --- | --- |
| `{"id": "apple", "img": "img/apple.png"}` | A picture |
| `{"id": "p:sheep*5", "img": "img/sheep.png", "n": 5}` | The picture five times, to count |
| `{"id": "t:Seven", "t": "Seven"}` | Latin text |
| `{"id": "f:سیب", "fa": "…"}` | Dari text, already shaped |
| `{"id": "lf:ب:start", "fa": "…", "big": true}` | One positional form of a letter |
| `{"id": "snd", "snd": true}` | A speaker card |

`id` is what answers are compared by. The app also accepts a bare string
`"apple"` as a picture thing.

**Dari text.** Every Dari string is already in drawing order: letters replaced
by their joined forms, order reversed, lines broken for the screen. Multi-line
text is a list of lines. The device only draws the glyphs.

## Items by engine

### listen_pick, journey, duel

```json
{
  "prompt_audio": ["en/apple-a07ab697.ogg"],
  "help_audio": ["fa/x-b6837856.ogg"],
  "show": {"id": "p:sheep*5", "img": "img/sheep.png", "n": 5},
  "choices": [{"id": "apple", "img": "img/apple.png"}, {"id": "bread", "img": "img/bread.png"}],
  "answer": "apple",
  "hop": "3+2",
  "tags": ["food"]
}
```

`choices` holds the answer and up to three wrong choices. The app shows two to
four of them depending on how the child is doing. `show`, `help_audio`, `hop`
(journey: operands and result within 0 to 20) and `tags` are optional.

### say_it

`{"prompt_audio": [...], "text": "Good morning", "fa": ["…"], "show": thing, "help_audio": [...]}`

### sorter

Round: `"baskets": [thing + "audio": [...]]`. Item:
`{"thing": thing, "basket": "<basket id>", "prompt_audio": [...]}`

### builder

`{"prompt_audio": [...], "tiles": [things in the right order], "extra": [things], "rtl": true, "done_audio": [...], "help_audio": [...]}`

### catch

`{"prompt_audio": [...], "targets": [things], "others": [things], "need": 5, "help_audio": [...]}`

### pairs

`{"a": thing, "b": thing, "audio": [...]}`. Three to six per round.

### market

`{"prompt_audio": [...], "mode": "count" | "pay", "target": 25, "units": [1, 2, 5, 10, 20], "goods": thing, "help_audio": [...]}`

### story

One item per page:
`{"audio": [...], "img": thing, "text": "…", "fa": ["…"]}`, and for a decision
page also `"choices": [things], "answer": "<id>", "wrong_audio": [...], "wrong_img": thing`.

## review.json

Each learner pack also carries `review.json`: every listen-and-pick style
question of the pack with its round id. The warm-up five and the "find my
level" game draw from it.

# Level file format

Status: **draft**. Only the Listen and Pick example comes from the product
spec (section 9); everything else here is a first proposal to be settled when
the first engine is built.

A level file is one JSON object describing one playable round for one engine.
Level files are never written by hand: the pack builder generates them from
the authoring spreadsheets in `content/`.

## Fields common to every engine

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `engine` | string | yes | Engine id, one of the ten in `app/engines/init.lua` |
| `id` | string | yes | Unique level id, see below |
| `prompt_audio` | string | yes | Spoken question or instruction, path inside the pack |
| `help_audio` | string | no | Dari explanation played on Y |
| `review_tags` | string[] | no | Tags used to pick warm-up items from earlier levels |

Every prompt has audio. A level file with text and no audio is invalid: the
app must never depend on the child reading.

### Level ids

`<subject>-<level>-<unit>-<round>`, for example `en-1-03-a`: English, level 1,
lesson or unit 3, round a.

| Subject | Code | Place in the valley |
| --- | --- | --- |
| English | `en` | Bazaar |
| Dari reading | `fa` | Library |
| Math | `math` | Workshop |
| Health and environment | `garden` | Garden |

### Paths

Audio and image paths are relative to the pack root, use forward slashes, and
are lowercase ASCII. Audio is Opus at 24 kbit/s (`.opus`), images are small
PNGs at 128 or 256 px.

### Dari text

Any Dari string in a level file is already shaped and reordered into
ready-to-draw glyph order by the builder, with line breaks fixed for the
640 px screen. The device only draws glyphs. Source spreadsheets hold normal
logical-order Dari.

## Listen and Pick (`listen_pick`)

Hear a word or question, press the direction of the right picture.

```json
{
  "engine": "listen_pick",
  "id": "en-1-03-a",
  "prompt_audio": "en/apple.opus",
  "help_audio": "fa/apple_help.opus",
  "choices": ["apple", "bread", "water", "egg"],
  "answer": "apple",
  "review_tags": ["food", "en-l1"]
}
```

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `choices` | string[2..4] | yes | Picture names. At most four: up, down, left, right |
| `answer` | string | yes | Must be one of `choices` |

A picture name `apple` resolves to `img/apple.png` in the pack (proposal).

Schema: `schemas/level.listen_pick.schema.json`.

## Other engines

Not specified yet: `pairs`, `catch`, `builder`, `say_it`, `story`, `journey`,
`market`, `duel`, `sorter`. Add a section and a schema here when each engine
is built, together with its spreadsheet template in `content/templates/`.

## Open points

- One round per file, or one file per level holding a list of rounds?
- Slow-playback audio (X button): separate file by naming convention
  (`apple.slow.opus`) or an explicit field?
- Where the pair variant of a game is declared.

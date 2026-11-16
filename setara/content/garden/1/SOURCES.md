# garden-1 (Health and environment 1: Me), version 2

**Written by an AI (Claude). Not reviewed by a Dari speaker, a teacher or a
health professional; built with silent speech only, so nothing has been
heard.** `docs/review-notes.md` ("Health 1 and 2") holds the open health
points; version 2 adds none and settles none.

## What version 2 changes (16 November 2026)

The owner played version 1 and asked for more content and more variety.
Version 1 had 22 rounds that were the same at every play. Version 2 has 39
rounds; every round except the stories is a pool, so each play asks a
different part of it.

- **Existing games keep their ids, letters, rounds and every old row.** New
  rows were appended to the same sheets: the two sorters and the two picking
  games now hold 12 to 15 items per round and ask 8 (`"draw": 8`);
  `clean_hands` holds 6 sequences per round and asks 4.
- **New rounds in `good_plate`:** 05 hot day / cold day (clothes and things
  of summer and winter), 06 day / night.
- **New forms inside the old picking games:** riddles ("Who am I?") and
  questions about a picture that is shown.
- **Six new games:** `why_stories` (story, 4: why we wash hands, why a tooth
  hurts, why we sleep, how a seed becomes a plant), `first_next` (builder, 2:
  growth; day and year), `odd_one_out` (listen_pick, 2; what the others are
  is said aloud), `true_or_not` (sorter with a tick and a cross
  basket, 2), `go_together` (pairs, 3: mother and young; body part and its
  thing; animal and what it gives or likes), `quick_hands` (catch, 2).

## Health content: nothing new

Every health sentence in the new rows restates what version 1 already taught,
in its wording: wash hands with soap before eating, after the latrine, after
play in the dust, after touching an animal, after sneezing; germs are too
small to see; water alone is not enough, soap takes germs off (from garden-2);
brush twice a day, morning and before sleep; sweets damage teeth; milk,
carrot, apple are good for teeth; tell a parent when a tooth hurts and they
take you to the clinic; children need a lot of sleep and should go to bed
early. One new row says "after touching rubbish, wash" (the garden-2 rule).

Points a health professional should look at, because they extend the wording
slightly:
- "A decayed tooth turns black and hurts" (story 2, `my_body` round 04).
- "We spit the foam out and do not swallow it" (help text of one question).
- Sweet biscuits and chocolate are sorted as bad for teeth, next to sweets,
  fizzy drink and sugar.
- The morning sequence "wake up, wash hands and face, brush teeth" puts
  brushing before breakfast; version 1 does not say when in the morning.
- "When we sleep the body rests and gathers new strength."

## Other decisions and open points

- Seasons: wheat is harvested in summer; walnuts and grapes in autumn; lambs
  are born and flowers open in spring. Check for the region.
- Tame / wild: camel is tame; lion, elephant and frog were added as wild.
- "Three are sweet: sweets, sugar, honey; the egg is not."
- `go_together` round 03 mixes what an animal gives (milk, egg, wool, honey),
  where it lives (nest, river) and what it likes (mouse, bone).
- Stories: Mina (girl, twice), Hamid and Navid (boys); Omid stays in the old
  story. The sleep story reuses the picture of the pupil asleep in class.
- Words: چارمغز، بقه، طوطی، کره (foal)، ساقه، کمان رستم، بسکیت، چاکلیت،
  جراب، «شیر درنده» for lion (so that it is not heard as milk), «فاژه»
  (already in version 1).
- `tests/update/run.sh` names `garden-1.v1.zip`; after the next real build
  this pack is `garden-1.v2.zip` and that script must be told so. It was not
  changed here (code is outside this job).
- One spoken word still occurs three times in `good_plate` of garden-2
  («نان», from version 1); garden-1 has none above twice.

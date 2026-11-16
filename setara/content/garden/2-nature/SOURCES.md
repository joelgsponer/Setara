# Sources and review status of garden-2-nature (Nature and how things work)

**This pack is optional** (`"optional": true`): a separate zip that adds ten
games to Health and environment level 2. Leave it off the card and nothing of
it is there. No other pack refers to it. It is general knowledge of the
natural world for curious children; it contains no health advice.

**Written by an AI (Claude) in one pass on 16 November 2026. Not read or heard
by a Dari speaker, a teacher or a science teacher.** It was built only with
silent speech: nobody has heard a clip. Every statement in the sheets was
written from the fact sheet at the end of this file and from nothing else.
`content/i18n/nature.csv` carries the English of every Dari text.

## How it is built: explain first, then ask in different forms

Each idea is first told in a short story (two story games, twelve stories),
with one or two questions inside the story whose wrong answer is explained.
The other eight games then ask about the same ideas in different forms, so
that a fact is met several ways and not as one repeated question: a riddle
("I have no legs, I crawl and I hiss"), a direct question, a question about
a picture that is shown, category baskets, true or false, odd one out
(what the others are is always said aloud: "All but one are birds. Which one is not a bird?"), putting steps in
order, pairs, and catching what fits a rule. Every question row has a spoken
explanation on Y; every round has its own spoken introduction.

All games except the stories are pools (`"draw"`): a round holds more items
than one play asks, so a round is different each time.

| Game | Engine | Rounds | Items per round (asked per play) | What it is |
| --- | --- | --- | --- | --- |
| `nature_tales` | story | 6 | 9 to 11 pages, 2 questions | Tame and wild animals and their food, tracks; young ones and homes; how a seed grows; sun, moon and stars; weather; the five senses |
| `how_it_works` | story | 6 | 8 to 10 pages, 2 questions | Ice, water, steam; materials, floating and sinking; light and shadow; sound; magnets; wheel, lever, pulley, ramp |
| `nature_riddles` | listen_pick | 4 | 12 (8) | "What am I?": animals; plants, sky and weather; things; tracks, young and homes (with a picture shown) |
| `nature_journey` | journey | 4 | 11 or 12 (8) | Light, shadow, moon; sound and senses; water and weather; magnets, machines, materials. |
| `nature_baskets` | sorter | 6 | 12 or 14 (8) | Tame / wild; plant-eater / meat-eater; floats / sinks; magnet pulls / does not; hard / soft; burns / does not |
| `nature_order` | builder | 3 | 6 sequences (4) | Growth and food chain; moon, day, seasons, ice-water-steam; how things are made and moved |
| `nature_pairs` | pairs | 5 | 5 to 8 pairs (5) | Mother and young; animal and home; animal and food; tracks and what animals give; sense and thing sensed |
| `nature_catch` | catch | 3 | 6 rules (4) | Animals; sky, weather, plants; things and materials |
| `nature_true` | sorter | 3 | 15 statements (8) | True or false, into a tick basket or a cross basket |
| `nature_odd` | listen_pick | 3 | 12 (8) | Odd one out: living things; sky, weather, water; things and materials |

43 rounds, 433 rows. Nothing depends on reading: basket labels of the six
`nature_baskets` rounds are written Dari words, as in the other garden packs,
and each basket is spoken when the round starts; the true/false baskets are a
green tick and a red cross.

## "Try it" ideas

Only with water, shadow, sound and looking: look for tracks in mud after rain;
sow two seeds, one in the light and one in the dark; watch the moon for a
month; stand with your back to the sun after rain; put a bowl of water out on
a freezing night; drop a leaf, a pebble and a twig into a bowl of water; make
hand shadows in sunlight and pace out your shadow morning and noon; feel your
throat while you hum and tap a table with your ear on it; name a thing by
touch with eyes shut. No fire, no heights, no electricity, nothing eaten.

Safety sentences that are in the pack: never look straight at the sun; keep
away from the steam of boiling water; do not touch broken glass; stay indoors
during thunder and lightning; do not go near a snake; do not shout into
anyone's ear; do not touch a bird's nest; "never play with fire yourself" in
the introduction of the burns / does-not-burn round.

## Decisions

- **Simplifications a science teacher should confirm.** "Wood, leaves and
  feathers stay on the water; stones and iron things sink" (no word about
  density; an apple and an empty closed bottle are sorted as floating, a
  brick and a hammer as sinking). "The leaf makes food for the plant with
  sunlight, water and air." "Every sound is made by trembling." "The moon
  sends the sun's light back like a mirror." "The sun is a very large, hot
  ball that gives light of its own." "Ice is lighter than water."
  The rainbow is given six named colours (red, orange, yellow, green, blue,
  violet); a riddle says only "many colours".
- **Magnet:** only clearly iron or steel things are sorted as "sticks" (nail,
  needle, scissors, hammer head, axe, shovel and knife blades). Coins, keys,
  spoons and pots are never used in a magnet question, because many are not
  magnetic. One story page says copper and aluminium do not stick.
- **Plant-eater / meat-eater:** the fox, the hen, the dog, the frog and the
  mouse are left out of that round (they eat both or insects). The story says
  the hen eats both grain and insects. The cat is sorted as a meat-eater.
- **Tame / wild:** cat and dog are left out; the camel is tame.
- **Food chain** "grass, sheep, wolf" and the pair "wolf and meat" show
  hunting as a plain fact, without pictures of it.
- **Lever:** the story describes a father lifting a stone with a pole; it is
  not offered as something to try.
- **Children in the stories:** Zarmina, Nargis, Sadaf, Lina, Freshta, Homa
  (girls); Bashir, Fawad, Idris, Mansur, Qadir, Harun (boys). Common first
  names, no real person. Most pages show things, not people.

## Words a Dari-speaking reviewer should settle

آهن‌ربا (magnet), قرقره (pulley), اهرم (lever), تخته کج (ramp), کمان رستم
(rainbow), ژاله (hail), رعد و برق, پژواک (echo), قطب‌نما (compass), کندو
(beehive), سم (hoof), رد پا (track), بالشتک (pad of a paw), گیاه‌خور /
گوشت‌خور, ساقه (stem), گرد گل (pollen), شیره گل (nectar), کره (foal), بقه
(frog), توله (flute), دهل (drum), سموچ (cave), جهیل (lake), کراچی (cart),
بوجی (sack), خاشه (twigs), مس، المونیم، فولاد, «شیر درنده» (lion, said so
that it is not heard as milk), چارمغز (walnut), پنسل (pencil), قالین,
«می‌چسپد», «تیله کردن» (to push), «چپه» (upside down), «می‌پندد» (swells).

## Open points for human review

1. A science or primary teacher reads the fact sheet below and the
   simplifications above.
2. Is a pack about magnets and a compass useful where no child has a magnet?
   The magnet rounds can be answered from the story alone.
3. "About three weeks" for a hen's eggs; "about a month" for the moon; "two
   weeks" from new to full moon in one builder row.
4. "A foal stands on its legs on its very first day", "a kitten is born with
   its eyes closed": true, but check that they are wanted.
5. The moon pictures show the lit half on the right (waxing), as seen from
   the northern half of the Earth.
6. New pictures, drawn for this job by the same AI, need the eye of someone
   local: `lever`, `pulley`, `ramp`, `magnet`, `iron_nail`, `shadow_long`,
   `shadow_short`, `moon_new`, `moon_crescent`, `moon_half`, `track_bird`,
   `track_paw`, `track_hoof`, `rainbow`, `lightning`, `wind`, `feather`,
   `tongue`, `grass`, `stem`, `bone`, `beehive` (a straw skep, not a local
   box hive), `puppy`, `foal`. Least sure: `stem` (a red arrow points at the
   stem), `lever`, `shadow_long`, `foal`.
7. Existing pictures used in a new sense: `jar` is never used for "glass";
   `window` stands for glass; `notebook` stands for paper; `cloud` is a rain
   cloud; `hat` is the round cap; `walnut` stands for "hard shell".
8. Not heard: every riddle depends on the voice saying animal sounds
   (بع بع، عر عر، فش فش، قرقر، دُم دُم).

## Fact sheet (written first; the pack says nothing that is not here)

**Animals.** Tame (farm) animals live with people, who feed and water them:
cow, sheep, goat, donkey, horse, camel, hen. They give milk, eggs, wool and
carry loads. Wild animals find their own food: wolf, fox, lion, elephant,
snake, eagle, frog. Plant-eaters eat grass and leaves: cow, sheep, goat,
donkey, horse, camel, elephant. Meat-eaters hunt other animals: wolf, lion,
eagle, snake, cat; they have sharp teeth or claws. Some animals eat both; the
hen eats grain, worms and insects. A frog catches insects with its tongue.
Bees feed on the nectar of flowers and make honey in the hive. Birds have
feathers, two legs and two wings; only birds have feathers. Insects have six
legs (bee, ant, butterfly, fly). A snake has no legs. The elephant is the
largest land animal and has a trunk; the whale is the largest animal and
lives in the sea. A camel has a hump and can go many days without water. The
polar bear lives on the ice of the far north. Birds, snakes, fish and frogs
hatch from eggs; a hen sits on her eggs about three weeks. The young of cows,
sheep, cats, dogs and horses are born alive and drink their mother's milk:
calf, lamb, kitten (born with closed eyes), puppy, foal (stands on its first
day). Homes: a bird's nest of straw and twigs; honey bees together in a hive;
ants under the ground; fish always in water; frogs in water and on land;
eagles nest in high mountains. Tracks in soft earth and snow: a dog's (also
cat's and wolf's) has a pad and four toes; a cow's, sheep's or goat's has two
halves because the hoof is cloven; a hen's has three toes pointing forward; a
snake leaves a winding line.

**Plants.** A seed holds a tiny plant. With water it swells and its skin
splits; first the root grows downwards, then the shoot upwards towards the
light, whichever way up the seed lies. The root anchors the plant and takes
up water. The stem holds the plant up and carries water to the leaves. Green
leaves make the plant's food with sunlight, water and air; in the dark a
plant grows pale and weak. The flower becomes the fruit; bees carrying pollen
from flower to flower help this; the fruit holds the seeds. Blossom is the
flower of a tree. Plants need water, soil, light and air. In the end all
animals are fed by plants (grass, sheep, wolf).

**Sky.** The sun is a star: a very large, hot ball that gives its own light
and heat; it looks small because it is very far. Looking straight at it harms
the eyes. The Earth turns once a day; the side facing the sun has day. The
moon is smaller than the Earth and goes round it; it has no light of its own
and reflects sunlight. Over about a month we see it as new (not visible),
thin crescent, half, full, and shrinking again; about two weeks from new to
full; the moon itself is always round. Stars are suns very much farther
away; they are in the sky by day too, but sunlight hides them.

**Weather.** Wind is moving air. A cloud is made of very small drops of
water; dark heavy clouds bring rain. In cold air snow falls; hail is grains
of ice. Lightning and thunder happen together; light arrives much faster than
sound, so we see the flash first. A rainbow appears when the sun shines on
raindrops, which split white sunlight into colours; it stands opposite the
sun. Four seasons: spring, summer, autumn, winter; water freezes in winter.

**Water.** Three forms: liquid water pours and takes the shape of its
container; cooled enough it freezes to ice, which is the same water and melts
again in warmth; boiled it becomes steam, which is hot and scalds. Steam on a
cold lid turns back into drops. Water also evaporates slowly without boiling:
washing dries, puddles vanish; wind and sun speed it. Ice is lighter than
water and floats, so ponds freeze from the top and fish live underneath.

**Materials.** Wood comes from trees, is hard but can be sawn and nailed,
floats, burns (doors, tables, chairs, pencils). Metal such as iron is very
hard and strong, shines, heats quickly, sinks, does not burn (axe, shovel,
pot, key, needle, knife, scissors). Stone is hard and heavy, sinks, does not
burn (walls, mills). Cloth is soft, folds, is made from wool or cotton,
burns. Glass is hard, breaks easily, lets light through (windows). Bricks are
made from earth and water. Paper, twigs, charcoal and dry leaves burn; stone,
iron, water, sand and baked brick do not. Float: wood, leaf, feather, twigs,
a ball (full of air), an apple, an empty closed bottle, ice. Sink: stone,
key, coin, iron nail, hammer, brick.

**Light and shadow.** Light comes from the sun, fire, a lamp, a candle,
lightning; it travels in straight lines. A shadow is the dark place behind
something that blocks light; without light there is no shadow. With the sun
low (morning, evening) shadows are long; at midday they are short. A mirror
and still water reflect light. Window glass and clear water let light pass;
a wall and a door do not.

**Sound.** Every sound is made by something vibrating (a drum skin, the air
in a flute, the vocal folds in the throat). The vibration travels through the
air like a wave to the ear. Hit harder: louder; farther away: fainter. An
echo is sound coming back from a mountain wall. Very loud sound hurts ears.

**Magnets.** A magnet pulls iron and steel things (nail, needle, scissors)
with a force that cannot be seen. It does not pull wood, stone, cloth, glass,
paper or plastic, and not every metal: not copper or aluminium. The force
passes through a sheet of paper. A magnet has two ends; two magnets pull or
push each other depending on which ends face. A compass has a magnetic needle
that points north.

**Simple machines.** Wheel: rolling is easier than dragging (cart, lorry,
train). Lever: a long pole over a small stone lifts a heavy stone when the
far end is pressed down; the longer the pole the easier; scales are a lever.
Pulley: a small wheel over the well with the rope across it; pulling the rope
down brings the bucket up, and body weight helps. Ramp: a slanted plank; the
way is longer but needs less force; a winding mountain road is the same.

**Senses.** Five: sight (eye: colour, shape, light), hearing (ear), smell
(nose), taste (tongue: sweet, salty, sour, bitter), touch (skin, mostly hands
and fingers: warm or cold, soft or hard, smooth or rough). The senses also
warn us: the smell of smoke, the feel of heat.

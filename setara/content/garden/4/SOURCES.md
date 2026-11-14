# Sources and review status of garden-4 (Health and environment 4: My future)

**Not yet checked by a health professional, a Dari-speaking educator, a teacher
or the local team.** The pack was written by an AI (Claude). Every health
statement in it is taken from the fact sheet pasted in full below, which was
written first, from standard, conservative public-health guidance at the level
of WHO and UNICEF basics (UNICEF/WHO *Facts for Life*; WHO infant and young
child feeding; WHO child injury prevention; WHO/IFRC psychological first aid;
WHO and IFRC flood and drought messages). The fact sheet was written from the
author's knowledge of that guidance, not copied from a document that was open
at the time: **a qualified person must check the fact sheet itself, and then
every text of the pack against it.** `content/i18n/garden4.csv` carries the
faithful English of every Dari text.

No doses, no names of medicines, no diagnoses, no home remedies. Nothing
religious or political. "Growing up" (puberty) is **not** in this pack: the
spec makes it a separate optional pack for the local team, and nothing in
these sheets touches it.

The 32 pictures listed in `pictures.txt` are drawn; none has been seen by a
local reviewer. Nobody has listened to the audio.

## What the pack teaches

Curriculum (spec section 8), level 4, circle "My future".
Health: nutrition for growth, wellbeing and feelings, caring for small
children. Environment: drought and flood, energy, protecting land and water.

15 games, 40 rounds. All questions are spoken in Dari; pictures carry the
choices. The only written words are the short basket labels of the sorting
games, and each basket is spoken.

| Game (id, letter) | Engine | Rounds | Teaches |
| --- | --- | --- | --- |
| A Plate for Growing (`good_plate`, g) | sorter | 3 | three food groups with new foods; a fourth basket "only a little"; habits that help growth |
| Catch It (`growth_catch`, h) | catch | 3 | growth, protection and strength foods; soft food and safe things for a small child; what helps with feelings; water, soil, smokeless light, flood |
| Zainab's Morning Meal (`plate_story`, i) | story | 1 | a morning meal, a varied plate, girls and boys get the same, growth checks |
| My Feelings (`feelings`, j) | listen_pick | 3 | naming eight feelings; what helps; sleep and play |
| Three Stories about Feelings (`feelings_story`, k) | story | 3 | sad (a friend moves away), afraid (a storm at night), angry (a torn notebook) |
| Looking After the Little One (`little_one`, l) | story | 2 | keeping a two-year-old safe; feeding a one-year-old |
| A Safe Home for the Little One (`small_child`, m) | sorter | 3 | what to keep out of reach; do and don't; food for a small child |
| Step by Step (`right_order`, n) | builder | 4 | feeding and bedtime; feelings; flood; planting, solar lamp, saving firewood |
| Too Much Water, Too Little Water (`flood_story`, o) | story | 2 | a flash flood; a drought |
| Tree Keeper (`tree_keeper`, p) | journey | 4 | flood, drought, energy, soil and stream |
| Our Land and Our Water (`land_water`, q) | sorter | 3 | saving water; protecting soil; burning little firewood and fuel |
| The Story of the Sun Lamp (`energy_story`, r) | story | 1 | solar lamp, saving fuel and firewood, sparing trees |
| The Hill and the Stream (`land_story`, s) | story | 2 | trees hold soil; keeping the stream clean |
| Pairs (`future_pairs`, t) | pairs | 3 | feelings and their faces; problem and right action; where things come from |
| Quick Quiz for Two (`future_duel`, u) | duel | 3 | revision, two players |

Seven story rounds are about health and six about the environment; every one
of the eleven story rounds has decisions (37 in all). The right choice is first
in 13 of them and not first in 24. Nine are yes/no questions: "yes" is right
three times, "no" six times.

## Decisions taken by the author

- **Game letters g to u, and game ids** that do not occur in `garden-4-rights`
  (a to f, `rights_*`) or `garden-4-world` (a to f, `world_*`). `good_plate`
  and `tree_keeper` continue the games of the same name in levels 1 and 2.
- **Names** are common first names with no person meant: girls Zainab, Marjan,
  Shabnam, Mina, Laila, Zohra, Parwana, Nilab, Farzana, Hosna, Gulalai, Sitara,
  Nargis, Malalai, Parisa; boys Milad, Yama, Fawad, Farid, Harun, Jawid, Nasir,
  Elyas, Samim, Bashir, Omid, Tamim, Wali. Boys care for small children too
  (Bashir feeds his sister); girls decide in the flood and the energy story.
- **Feelings.** Every feeling is called normal. No text says or implies that a
  child is at fault for a feeling or for something that happened. Anger is
  normal; hitting and breaking are "not right". The three stories each end
  with "if it stays for many days … tell an adult you trust".
- **The older child helps; adults are responsible.** In both caring stories
  the mother is present ("I am right here"), and she says that looking after
  a small child is the adults' job, and that if something happens it is not
  the older child's fault and an adult must be told at once.
- **Poverty is not blamed.** Bread and tea are not called a bad meal. The
  story says that bread gives strength and that a growing body needs growth
  and protection foods too, and that beans and lentils are growth food "just
  as meat is".
- **Words chosen** (confirm or replace): سیلاب (flood), خشکسالی (drought),
  جای بلند (high ground), آب تیز (fast water), چراغ آفتابی and تخته آفتابی
  (solar lamp, solar panel; many people say سولر), چراغ تیلی (oil lamp),
  چارج (charge), گوگرد (matches), کارد (knife), تابلیت (tablet), تشت (basin),
  کوزه (jug), قهر (angry), پریشان (worried), مانده (tired), آرام (calm),
  غمگین (sad), خوش (happy), ترسیده (afraid), فاژه (yawn), دلش تیز تیز می‌زند
  (her heart beats fast), خوراک نرم و میده (soft, mashed food), مغز درسته
  (whole nuts), پدرکلان, بی‌بی, چهارمغز, مالته, تربوز, «خورد» for small as in
  garden-2 and garden-3.
- **Pictures reused from the library** wherever one fitted, including three
  that other packs added while this one was being written (`matches`, `lamp`
  for the oil lamp, `sun_noon` / `sun_evening`). `tell_adult` shows a boy and
  his mother; it is used for girls too.
- The sheets were generated from one authoring script so that every Dari text
  has its English twin. The CSVs are the source from now on.

## Where the pack simplifies the fact sheet, or goes a little beyond it

Nutrition
- The three groups keep the level-2 names قوت، نمو، محافظت. Nuts are not
  sorted into a group (walnuts appear only as a school snack and as a choking
  risk for a small child). Cheese, fish, orange, watermelon, maize are new.
- "Eat several times a day" is said only for the small child. For the school
  child the pack says: a morning meal, and fruit and nuts for break.
- "A child who is not growing, is very thin, or cannot eat goes to the
  clinic" is one spoken sentence. No sign of malnutrition is described and
  no measurement is taught.
- Iodised salt, iron-rich foods, vitamin A and worms are **not covered**.
- "Girls and boys both grow and both need good food; Mother gives both the
  same amount" is said once, in the story.

Breastfeeding and feeding a small child
- Breastfeeding is stated in general terms only, in two places: "Mother's
  milk is the best food for a baby, and in the first months a baby needs no
  other food" and "since she was about six months old she has been eating
  soft food as well". Nothing is said about how, how often, how long, or what
  to do when it is difficult; the story sends every such question to the
  health worker.
- "Six months" is the only age given for starting other foods. The fact
  sheet's "small amounts at first, more as the child grows" is reduced to
  "a little at a time, several times a day". No number of meals is given.
- The example meal (mashed potato, soft lentils, cooked pumpkin) is the
  author's, to show the three groups.
- "Tea and fizzy drinks are not for a small child" and tea in the "not for a
  small child" basket: see the open points.
- "Clean boiled water" is given to the one-year-old after the meal.
- Feeding a sick child is one sentence ("we still give her milk and food");
  level 2 teaches it.
- Choking: "whole nuts and hard sweets" stand for all small hard foods. First
  aid for choking is in level 3 and is not repeated.

Keeping small children safe
- Fire and hot things, water, sharp things and matches, small things, and
  the roof and stairs are in the story. Medicine, fuel and poison are one
  page (the child picks up a tablet and it is taken away *before* it reaches
  his mouth), because level 3 teaches poisoning. Roads and animals are not
  covered.
- "A small child can drown even in very little water, quickly and without a
  sound" is said plainly once, after a wrong choice.
- The "safe" basket (pillow, ball, blanket, bowl of soft food) is the
  author's. A ball is safe only if it is too big for the mouth; the picture
  shows a big ball.
- Sleeping place and position of a baby are **not covered**.

Feelings
- Eight feelings are named: happy, sad, afraid, angry, lonely, worried,
  tired, calm. "Shy", "ashamed", "jealous" and "proud" are left out.
- What helps: telling a trusted adult, going close to someone you trust,
  slow breathing ("in through the nose, out more slowly, five times"),
  play, drawing, sleep, a friend who listens. "If the first adult could not
  help, tell another" is one question.
- "After something frightening, fear and bad dreams stay for a while and
  slowly grow less" is one sentence at the end of the fear story. Nothing is
  said about war, violence, death or loss of a family member. The sad story
  is about a friend who moves away, deliberately a small loss.
- "Fear tells the body: take care" is the only explanation of what a feeling
  is for.
- No feeling is linked to an illness and no condition is named.

Sleep and play
- No number of hours of sleep or minutes of play is given (the fact sheet
  gives none either). "A child needs more sleep than an adult", "early, and
  at the same time every night".
- One question repeats the level-3 rule about burning charcoal in a closed
  room.

Flood
- The story is a flash flood after rain in the mountains. Snowmelt floods,
  mudslides and earthquakes are not covered.
- "Fast water, even when it is shallow, can knock down a grown person" is
  said without a depth. "Neither on foot nor in a car."
- The family walks "the longer way that climbs". Bridges are not discussed;
  `bridge` appears only as a wrong choice for "where do we go".
- After the flood: adults check the house first, children do not play in
  flood water, all drinking water is boiled, food touched by flood water is
  not eaten. Electricity, snakes and unexploded objects washed out by floods
  are **not covered** (the last belongs to the specialist optional pack).
- "People first, belongings can be found again" is the author's wording.

Drought
- "Do not save on drinking water or on washing hands" is said in the story,
  in two questions and in the summary. This is the health point of the round.
- Reusing water: only "water we washed vegetables or hands with" goes to the
  trees and the garden. Soapy laundry water is not mentioned.
- Rainwater from the roof is "for washing and for the garden"; one help text
  adds "if we drink it, we boil it first".
- "Water in the evening or early morning" is given the reason "the hot sun
  quickly turns the water to vapour".

Energy
- "The panel makes electricity from sunlight and charges the lamp" is the
  whole explanation. Batteries, wind and water power are not covered.
- Saving firewood: dry wood, a lid on the pot, soaked beans, a closed stove
  with a chimney, dry branches instead of a living tree. "Put the fire out
  when the food is cooked" is not said.
- The sun "dries the washing, and dries apricots and mulberries".

Land and water
- "Good soil takes hundreds of years to form" is a round figure.
- Planting "a small hollow beside each sapling, so that rainwater collects"
  stands for all water-harvesting and terracing.
- "We graze goats and sheep in a different place each time" is the only
  sentence on grazing.
- Stream: rubbish in the pit, animals drink lower down and people fetch
  higher up, clothes are washed in a basin away from the stream and the
  water poured on the ground, fuel, engine oil and field poison never go
  into the stream, latrine and pit far from stream and well. The story ends
  with "we still boil stream water before drinking".

## Points a health professional must decide

1. **The fact sheet itself** (below): is every line right for this place?
2. **Breastfeeding wording.** "In the first months a baby needs no other
   food" and "since about six months … soft food as well". Is this the
   wording the local programme wants, or should "six months" be said for
   both? Should anything be said about water for young babies?
3. **Tea.** "Tea … [is] not for a small child", and tea is sorted as "not
   for a small child". This follows common nutrition advice for young
   children; confirm it for this setting, or take the two places out
   (`little_one` round 02, `small_child` round 03).
4. **Boiled water for a one-year-old** after the meal: confirm.
5. **Whole nuts.** Said to be a choking risk for a "small child" without an
   age. Up to what age should this be said? Walnuts are given as a school
   snack to children of eight and ten.
6. **Egg, yoghurt and fish for a small child** are in the "good" basket
   without an age or any word about allergy.
7. **"If a child is not growing, is very thin, or cannot eat, we take the
   child to the clinic."** Is growth monitoring available at the local
   clinic? Is the sentence enough, or too much?
8. **Left out on purpose:** iodised salt, iron, vitamin A, deworming,
   vaccination, a pregnant or breastfeeding mother's own food, how a baby
   sleeps. Decide whether any belongs here.
9. **Drowning.** "Never leave him alone near a stream, a pond, a well or a
   full bucket." Confirm; add irrigation channels or water tanks if these
   are the local danger.
10. **"If one day something happens to the child, tell an adult at once. It
    is not your fault."** Confirm the wording with someone who knows how
    families will hear it.
11. **Feelings.** Is "tell an adult you trust: mother, father, grandmother,
    the teacher or the health worker" right here? Can the health worker
    actually help a child who has been sad or afraid for many days, and
    whom should a teacher turn to? Is slow breathing an acceptable thing to
    teach? Should children who have lived through violence or loss get
    anything more than this pack, and from whom?
12. **Flood.** "Go to high ground right now", "never cross fast water",
    "go back only when the adults say it is safe", "boil all drinking water
    after a flood", "food touched by flood water is not eaten". Confirm
    against local disaster guidance, and say whether a village has a known
    safe place the teacher should name.
13. **Drought.** Giving used washing water to food plants in the garden:
    acceptable, or trees only?

## Points a Dari-speaking educator and the local team must decide

- Every Dari sentence: the author is not a native speaker.
- The feeling words (list above), and whether «قهر» and «پریشان» mean to
  local children what the pack means by them.
- "Girls and boys both grow, and both need good food." (once, `plate_story`)
- "All children, girls and boys, need play every day." (once, `feelings`)
- A boy who feeds his baby sister, and a father who listens to an angry
  daughter and says "I understand that you are angry".
- Whether an older child being asked to mind a two-year-old near a fire is
  shown acceptably (the mother stays close and says so).
- The flood and drought stories may come close to what children have lived
  through. Decide whether the teacher should introduce them.
- A solar lamp "from the bazaar": is it something families here can get?
- Pictures of people: `feel_*`, `breathe_slow`, `listen_friend`,
  `hold_hand`, `feed_child`, `play_little`, `keep_high`, `toddler_fire`,
  `toddler_water`, `fast_water`, and the five scenes. The small children of
  one and two are drawn without a cap; the one-year-old girl has a small
  headscarf.

## Known weak points

- `high_ground`: the people on the hill are very small at 3 cm; the arrow
  and the water carry the meaning.
- `keep_high`: the things on the shelf are small.
- `listen_friend`: the two girls are cut off at the waist.
- `goat_sapling`: the sapling is small beside the goat.
- `tap_waste` is close to the older picture `tap`; they never appear
  together.
- `feel_calm` (closed eyes, small smile) and `feel_tired` (yawn, moon) must
  be told apart at 3 cm; try it with children.
- Several story pages are long (three to five sentences). The engine fits
  them, but nobody has heard how long they take.
- In the catch game a "growth food" has to be caught while bread or an
  apple, both good foods, fall past. Check that this does not read as "bread
  is bad".
- The duel engine has no earlier pack to compare with; the three rounds were
  built and validated but not played.

## The fact sheet

# Facts for garden-4 (use these; add nothing medical of your own)

Audience: village children of about 9 to 14 and their teachers, far from a
clinic. Standard, conservative public-health basics. The first rule for a
child is always: stay safe yourself, tell an adult, and ask the health worker
when unsure.

Food for growing
- A growing child needs a varied diet every day: staple foods for strength
  (bread, rice, potatoes, maize), foods for growth (beans, lentils,
  chickpeas, eggs, milk, yoghurt, cheese, meat, fish), and fruit and
  vegetables of different colours for protection. No single food is enough.
  Pulses are growth foods, as meat is.
- Eating in the morning before school helps a child to learn and play.
- Sweets, sugar and sweet fizzy drinks do not help growth and harm the
  teeth: only a little, and only sometimes. They do not replace a meal or
  water.
- Drink clean, safe water. Wash hands with soap before preparing food,
  before eating and before feeding a child.
- Girls and boys both grow and need the same good food.
- Health workers weigh and measure small children to see that they are
  growing well. A child who is not growing, is very thin, or cannot eat is
  taken to the clinic.
- Sleep and daily active play also help a child to grow.

Babies and small children: food
- Mother's milk is the best food for a baby. In the first months a baby
  needs no other food. (General terms only. Every question about feeding a
  baby goes to the health worker.)
- From about six months a child needs soft, mashed foods as well as
  mother's milk: small amounts at first, more as the child grows.
- A small child's stomach is small: small meals, several times a day. The
  child has its own clean bowl, so that the family sees how much it ate.
- Variety for the small child too: a mashed staple, with pulses, egg or
  yoghurt, and mashed vegetables or fruit.
- Clean hands (the helper's and the child's), a clean bowl and spoon, clean
  water, freshly prepared food.
- Feed patiently, talk to the child, never force. If the child refuses,
  wait and offer again a little later.
- A sick child still needs milk and food.
- Not for a small child: small hard foods that can block the throat (whole
  nuts, hard sweets); sweets and sweet fizzy drinks; tea.
- A small child eats sitting down and is never left alone with food.

Keeping small children safe
- A small child does not know danger and moves fast: an adult or an older
  child must always be close. Looking after a small child is the adults'
  responsibility; an older child helps. If something happens, tell an adult
  at once; it is not the older child's fault.
- Fire and hot things: keep small children away from the cooking fire, hot
  pots, tea and lamps. Matches are kept out of reach.
- Water: a small child can drown in very little water, quickly and silently.
  Never leave a small child alone near a stream, pond, well or full bucket.
  Cover wells and water containers. Hold the child's hand near water.
- Sharp things (knives, scissors, sickles) are kept high up.
- Medicines, fuel, poisons and cleaning liquids are kept high up or locked
  away. (First aid: level 3.)
- Small things (buttons, coins, beads, whole nuts) are kept away from small
  children: they put everything in the mouth and can choke.
- Roofs and stairs: a small child does not climb alone.
- Talking, singing and playing with a small child is good for the child.

Feelings and wellbeing
- Everyone has feelings: happy, sad, afraid, angry, worried, lonely, tired,
  calm. All feelings are normal, for girls and boys, children and adults.
  Having a feeling is never wrong and never the child's fault. Feelings come
  and go.
- Naming a feeling and telling someone helps.
- What helps when sad or afraid: telling an adult you trust (mother, father,
  grandmother, teacher, health worker); being close to someone you trust;
  breathing slowly; playing, moving, being with friends; drawing; sleep and
  ordinary daily routine.
- When angry: stop, breathe slowly, walk away; speak when calm. Anger is
  normal; hitting, hurting and breaking things are not right.
- A friend who is sad or afraid: sit with them, listen, do not laugh at
  them, invite them to play, help them to tell an adult.
- After a frightening event, fear and bad dreams are common in children and
  usually grow less with time, closeness and routine.
- If sadness or fear lasts many days, or the child cannot sleep, eat or
  play, or someone is hurting or frightening the child: tell a trusted
  adult; if the first cannot help, tell another.

Sleep and play
- Children need more sleep than adults: enough sleep every night, at a
  regular time. Babies and small children also sleep in the day.
- In sleep the body grows and the mind rests. A rested child learns better
  and feels better.
- Before sleep: brush teeth, do something quiet.
- Every child, girl and boy, needs active play every day: it makes bones
  and muscles strong and lifts the mood.
- Never sleep in a closed room with burning charcoal (level 3).

Flood (safety)
- Flash floods come quickly after heavy rain, sometimes rain that fell far
  away in the mountains. Signs: heavy rain, a rising, muddy, loud river.
- Move away from rivers and streams. Tell adults. Go to high ground at
  once; do not stop to collect belongings. Hold small children by the hand.
- Never walk, play or drive through moving flood water: even shallow fast
  water can knock an adult down, and holes and stones cannot be seen.
- Return only when adults say it is safe; water can come again after the
  rain stops. Adults check the house first: wet walls can fall.
- Flood water is dirty: do not play in it; wash hands with soap; boil all
  drinking water; do not eat food that flood water has touched.
- Trees and plants on slopes hold the soil and slow the water.

Drought (health)
- In a drought, save water in every use except two: keep drinking enough
  safe water, and keep washing hands with soap (a little water poured from
  a jug is enough).
- When water is scarce people use unsafe sources: boil water from ponds,
  streams and open wells before drinking.
- Ways to save: do not leave a tap open, mend drips, cover containers, give
  used washing water to trees and the garden, water plants in the early
  morning or evening, collect rainwater from the roof (for washing and
  plants; boil before drinking).

Energy (health and safety)
- Smoke from open fires and oil lamps harms the eyes and chest; oil lamps
  are a fire and poison danger for small children. A solar lamp has no
  smoke, flame or fuel.
- Dry wood, a lid on the pot, soaked pulses and a closed stove with a
  chimney use less wood and make less smoke.

Land and water (health)
- Rubbish, soap, fuel, oil, pesticide and animals make stream water unsafe
  for the people downstream. Latrines and rubbish pits are built far from
  streams and wells. Stream water is boiled before drinking even when it
  looks clear.

Never write: doses, names of medicines, diagnoses, home remedies, anything
about puberty (separate optional pack), anything religious or political,
anything that blames a child or a family.

# Sources and review status of garden-3-village (My village: staying well, land and weather)

**Written by an AI (Claude) on 16 November 2026. Not checked by a health
professional, a Dari-speaking educator, a teacher or anyone who farms in
Afghanistan. Built with silent speech only: nothing has been heard. Not run on
a handheld.** The health part can harm if it is wrong: nobody should see this
pack before a qualified person has read the fact sheet below and every text
(`content/i18n/village.csv` carries the faithful English of every Dari text).

This is the rest of level 3 of the curriculum ("My village"; `garden-3` is
first aid). It is an optional add-on (`"optional": true`): a separate zip that
adds its games to Garden level 3. Leave it off the card and nothing of it is
there. The teacher's guide `guide-garden-3` has ten chapters for it (14 to 23).

## How it was written

1. The fact sheet at the end of this file was written first, from standard
   public-health basics at the level of WHO and UNICEF material for families.
   It was written from general knowledge of that guidance, **not from a
   document**; no source was open while writing.
2. The sheets were written only from the fact sheet and from what `garden-1`,
   `garden-2`, `garden-2-nature` and `garden-3` already teach, in their words.
3. Explain first, then ask: three story games teach (14 short stories), eight
   pool games practise in other forms.

No medicine, dose, home remedy, vaccine name, schedule or diagnosis is in the
pack. The only illness words are «ریزش» and «سرفه» (cough and cold), «تب»
(fever) and «اسهال» (diarrhoea).

## What the pack holds

11 games, 46 rounds, 514 rows, every question spoken in Dari, nothing depends
on reading (two rounds use the spoken text baskets «بی‌خطر» / «خطر»; the
baskets are spoken).

| game | Dari title | engine | rounds | rows | each play asks |
|---|---|---|---|---|---|
| `village_health` | قصه‌های صحت قریه | story | 4 | 43 | all (story) |
| `village_safe` | بی‌خطر در بیرون | story | 4 | 46 | all (story) |
| `village_land` | زمین، آب و هوا | story | 6 | 66 | all (story) |
| `village_riddles` | من چه هستم؟ | listen_pick | 4 | 48 | 8 |
| `village_path` | راه قریه | journey | 4 | 55 | 8 |
| `village_baskets` | سبدهای قریه | sorter | 5 | 77 | 8 |
| `village_true` | درست است یا نه؟ | sorter | 4 | 57 | 8 |
| `village_order` | اول چه، بعد چه؟ | builder | 4 | 27 | 4 |
| `village_pairs` | جوره‌های قریه | pairs | 4 | 35 | 5 |
| `village_catch` | زود بگیر | catch | 4 | 23 | 4 |
| `village_odd` | کدام یک جور نیست؟ | listen_pick | 3 | 37 | 8 |

Repetition, counted by `stats.py`-style script over the sheets (identical
spoken texts in the whole pack; right answers per game):

| game | most-repeated spoken text | answer right most often |
|---|---|---|
| `village_health` | 1x | `clinic` 3x |
| `village_safe` | 1x | `stop` 2x |
| `village_land` | 1x | `worm` 1x |
| `village_riddles` | 1x | `germ` 1x |
| `village_path` | 1x | `water` 3x |
| `village_baskets` | 2x | not a picking game |
| `village_true` | 1x | not a picking game |
| `village_order` | 1x | not a picking game |
| `village_pairs` | 1x | not a picking game |
| `village_catch` | 1x | not a picking game |
| `village_odd` | 1x | `bridge` 2x |

No spoken text occurs more than twice in the pack. Three occur twice: "Where
do children get vaccines?" (a story and the journey), and two sorter cards
that stand in two different rounds with different baskets ("We dip a hand
into the drinking water", "We plant saplings").

## Where I held back (deliberately less than the curriculum line might suggest)

- **Unknown objects.** The pack says only, in these words: «چیز ناشناس روی
  زمین: به آن دست نمی‌زنیم، از آن دور می‌شویم، و به یک کلان می‌گوییم» ("An
  unknown object on the ground: we do not touch it, we move away from it, and
  we tell an adult"). It appears in `village_safe` round 04 (one page, one
  question, the closing line), and once each in `village_path` 02,
  `village_baskets` 02, `village_true` 02 and `village_order` 02. Nothing says
  what such an object is, looks like or does. **No picture of an object was
  drawn**: the pages show the existing `stop` and `tell_adult` pictures. The
  product spec leaves the specialist material on dangerous objects found
  outdoors to the local team; this pack does not replace it and must not be
  taken for it. One thing for the local team to look at: the wrong choice
  "touch it" uses the library picture `touch`, a finger touching a ball; if a
  ball there could be read as a hint about the object, replace the picture.
- **Vaccines.** Five statements only (fact sheet A2). Left out on purpose: the
  vaccination card, what may follow a vaccination (fever, swelling), how many
  visits, ages, any disease, any claim about how well a vaccine works, and
  anything about people who do not vaccinate. The story says the health worker
  "says on which day the child should come again", which implies more than
  one visit and nothing else.
- **Illnesses.** No names beyond cold, cough, fever, diarrhoea. No medicine of
  any kind, no remedy, no warm drinks or steam or honey, no "when to send a
  child back to school", no temperatures. The thermometer appears once as a
  riddle ("I show whether your body has a fever; the health worker has me")
  and nobody is told to use one. Diarrhoea is `garden-2`'s story retold with
  other children, sentence for sentence where possible.
- **Danger signs.** Only the first six lines of the `garden-3` list are
  repeated (drinking, sleepiness, fit, breathing, stiff neck and young baby,
  fever for days), in `garden-3`'s Dari. The rest stay in `garden-3`.
- **Water rescue.** "Do not go in; call the adults; from dry ground a stick or
  rope is held out" and no more. The adults do the reaching in every text. No
  swimming, no resuscitation after drowning (`garden-3` leaves that open too).
- **Cold injury.** "Warm numb fingers slowly, in a blanket or with body
  warmth; not with snow, not close to a fire; tell an adult; if they stay numb
  and white, the health worker." No warm-water bath, no word "frostbite".
- **Heat.** Shade, lying down, sips of water, a wet cloth, tell an adult;
  confusion or hard to wake is the `garden-3` danger sign. No salt, no word
  "heat stroke".
- **Animals.** Scorpions, spiders and bee stings are not covered. Snake and
  dog bites point back to `garden-3` and add nothing.
- **Floods** are `garden-4`'s subject; here only "do not stay in a gully or
  beside a stream in a storm" and "do not go into fast water".
- **Mouldy grain.** The pack says damp grain "goes mouldy and is spoiled". It
  does not say what happens to someone who eats it.
- **Compost.** General terms only. Nothing about human waste, about how long
  dung must rot before it goes on vegetables, or about composting toilets.
- **Karez.** Described in six plain sentences that I am sure of (underground,
  from the foot of the mountains, gentle slope, a row of shafts, flows by
  itself, cleaned by the village together). Nothing about water rights, the
  mirab, or who owns the water.

## Where the sheets simplify, or go a little beyond, the fact sheet

Health
- Reasons given after a wrong choice are the author's and minimal: "someone
  who runs does not see the car, and may fall"; "a dog runs after someone who
  runs"; "a snake bites when someone comes close to it"; "lightning strikes a
  single tree"; "a numb finger does not feel the heat and gets burned" (this
  one is in the fact sheet); "someone who walks further is found later"; "a
  mother (animal) defends her young".
- "We cough into the elbow because we do not touch things with our elbow" is
  the author's explanation of the fact sheet's rule.
- "A vaccine does not protect against all illnesses, so we still wash hands"
  is put into a child's question and the health worker's answer.
- Fever: "a fever of more than two or three days is a danger sign" and "any
  fever in a baby under three months" are `garden-3`'s lines. "If the fever
  lasts, or the sick person is very weak, we take them to the health worker"
  is the softer rule this pack adds before the danger signs; it gives no
  number of days.
- The cold story lets the boy go back to school "some days later". The fact
  sheet gives no duration.
- "At midday we rest in the shade" is shown with the library picture `rest`
  (a woman resting under a tree).
- Road: "walk on the side where the vehicles come towards you" is said without
  the words left or right.
- "Know the name of your village and of your father" is a rule for the child;
  the app stores nothing.

Environment (school-level statements a teacher or agronomist should check)
- "A finger's width of soil forms in hundreds of years."
- Farm calendar: wheat sown in autumn or spring and cut in summer; maize sown
  in spring, ripe in autumn; potatoes planted in spring, dug in late summer
  and autumn; apricots and mulberries in early summer, apples, grapes and
  walnuts in autumn; lambs in spring. True of much of the country, wrong in
  detail for many places. The guide tells the teacher to ask a local farmer
  and to teach his answer.
- "Because its way is under the ground, the sun turns little of it to vapour"
  (karez).
- "A cloudy sky keeps the ground warm like a blanket; a clear sky does not."
- "A winter with little snow brings a summer with little water."
- Added from general knowledge, outside the fact sheet: the scarecrow; locusts
  (the picture `grasshopper`) damage crops; cheese comes from milk; carrot,
  onion, turnip and radish grow under the ground; rice is a grain; rain water
  from the roof is collected for the garden and for washing (`garden-2`).
- Water: tap and pump are not sorted as clean or unclean anywhere in this
  pack. Every source is followed by "we boil drinking water", as `garden-2`
  teaches; the open `garden-2` points about boiling stay as they are.

## For a health professional to decide

1. Read the fact sheet below as a whole: is anything in it wrong, unsafe or
   unworkable where these children live?
2. Vaccines: are the five statements right as worded, and is "babies and
   children get them at the clinic or from the vaccinator who comes to the
   village" true locally? Should the vaccination card be mentioned? Should
   anything be said about a sore arm or a mild fever afterwards beyond "it may
   hurt a little and the arm may be a little sore"?
3. Cough and cold: is "rest, drink, keep eating, cover the cough, wash hands;
   health worker if it does not get better, if a fever lasts, or if the person
   is very young or very weak" enough, or must a number of days or more signs
   be given (ear pain, chest indrawing)?
4. Fever: "take the blanket and extra clothes off; no icy water, no ice"
   (from `garden-3`). Is a small child at night in an unheated house at risk
   of being cooled too much by this rule?
5. Is repeating only part of the danger-sign list acceptable, or should the
   whole list of `garden-3` be said again?
6. Diarrhoea: all open points of `garden-2` apply unchanged (no age for the
   baby, no zinc, sachet only, home first and clinic on danger signs).
7. Heat: are "headache, dizziness, great tiredness" the right three signs, and
   is a wet cloth on forehead and neck right?
8. Cold: is the advice for numb, white fingers right and complete enough? Is
   "with the warmth of the body" clear?
9. Lightning: "come down from the hilltop, away from single trees, water and
   tall metal things; not in a gully or beside a stream". Anything to add for
   children herding animals far from any house?
10. Water: is it right to tell children that adults "hold out a long stick or
    a rope from dry ground"? Should children over a certain age be allowed to
    do this themselves?
11. Dogs: "stand calmly, do not scream, do not run, walk away slowly".
12. Road: "walk on the side where the vehicles come towards you" on roads
    with no path. Right for the local roads?
13. Getting lost: "stop, stay where you are in an open place, call out, keep
    warm". Right in winter in the mountains?
14. Soil and compost: "wash hands with soap after working with soil, compost
    or dung" is the only health statement; is more needed about dung?

## For a Dari-speaking educator

Words chosen without certainty; confirm or replace:
- «واکسیناتور» (vaccinator), «کارمند صحی», «کلینیک» (as in `garden-2/3`).
- «ریزش» for a cold; «گلودرد»; «سرچرخی» (dizziness); «کرخت» (numb).
- «قات آرنج» (bend of the elbow) in the guide; the sheets say only «آرنج».
- «شبنم یخ‌زده» and «یخ شب» for frost. I did not use «قیرو»/«قیراو» because I
  was not sure of it; if that is the everyday word, use it.
- «طرف بالای آب» / «طرف پایین آب» for upstream and downstream. Irrigation
  language may say «سرآب» and «پایاب»; I was not sure.
- «علف هرزه» for weeds; the word «خیشاوه» (weeding) is not used.
- «قلبه» (ploughing), «درو», «داس», «بیل», «کندو» (grain bin), «بوجی»,
  «پوپنک» (mould), «پارو» (dung), «کود» (compost; schools may say «کمپوست»),
  «چقوری کود», «نقب» (tunnel), «دامنه کوه», «ناوه» (roof spout), «سنگچل»,
  «پته پته» (in steps), «ملی» (radish), «ناک» (pear), «چپلی», «بالاپوش»,
  «جراب», «ترمامیتر», «مترسک», «ملخ».
- «دریا» is used for river, as in the other packs.
- The riddles end «من چه هستم؟», one with «من کی هستم؟» and three with «من
  کدام تصویر هستم؟», where the answer is an action.
- Names: Maryam, Hasina, Fawzia, Roya, Nilab, Zarghona, Yasamin, Shima,
  Fereshta, Homa, Gulalai (girls); Karim, Basir, Nasim, Rahim, Daud, Wali,
  Sabur, Jamil, Aref, Naim, Zaher, Idris (boys). Eleven stories have a sister
  and a brother, the girl named first in five and the boy in six; one has a
  boy alone (Nasim), one a girl with her grandmother (Shima), and one (clean
  water) names no child.
- Who does what: a girl and a boy weed together; the father ploughs and mixes
  compost; a girl calls for help at the river; a girl fetches firewood and
  water; a boy herds goats; the health worker is a woman.

## The teacher's guide (chapters 14 to 23 of `guide-garden-3`)

The guide states the fact sheet and nothing medical beyond it. What it adds
for the teacher, and what needs the same sign-off:
- A chalk-dust demonstration of a cough into the palm and into the elbow
  (the level-one demonstration, reused).
- A comparison for vaccines: "before winter we gather firewood, so that we are
  ready when the cold comes; a vaccine too makes the body ready ahead of
  time". What an older child can do when a baby cries at a vaccination (hold
  her hand, sing, not frighten her). "Never threaten a child with an
  injection." The teacher is told to ask the clinic when the vaccinator comes
  and where families take a child, and to tell the class.
- A five-finger rule for a cold (tell, rest, drink, cover, wash) and body
  movements for every outdoor rule.
- Unknown object: the teacher is told to repeat the one sentence weekly with
  three movements, to say nothing about what the object looks like or could
  be, to draw nothing, to tell no frightening stories and to ask no pupil
  what she has seen; and, if a pupil says she has seen such a thing, to praise
  her for telling and to inform the head teacher and the village elders the
  same day. The "mistakes" page adds "not with a foot either" and "not to show
  a friend". **The local team should read chapter 19 before it is used.**
- Demonstrations with things in the yard: sorting a handful of soil, two
  small hills under "rain" from a tin with holes, a scratched "stream" with
  earth dropped in upstream, a handful of snow in a bowl, two pieces of dry
  bread kept damp and dry ("nobody eats the damp piece"), a weather diary on
  the board, a small school compost pit "if the school allows it, away from
  the well".
- The teacher is told to ask a local farmer for the real farm calendar and to
  teach that, and to ask an elder for the story of the village karez.
- Chapter 1 of the guide ("eight games in the Garden, level three") was left
  as it was; chapter 14 says what the add-on adds. "Looking back" was only
  renumbered (14 to 24).

## Pictures

296 library pictures are used; 15 are new (`pictures.txt`), drawn by the
author and looked at rendered. None has been seen by a local reviewer; two
show people. Weakest: `scene_upstream` (the cow in the stream is crude; the
brown water below it carries the idea), `scene_vaccination` (the baby is
simple), `lean_well`, `grain_wet` (the mould spots are small at 3 cm).
`scene_vaccination` shows a syringe at a baby's arm; a first version had a
red cross on a box, which was removed (no emblems).

## What was run

- `validate --only garden-3-village`: ok, 0 warnings; no Dari text of the pack
  without English.
- Silent build into a scratch folder: ok.
- `tests/fuzz_rounds.lua` with core and this pack in a scratch save folder:
  every round opened (57 openings), no error.
- Screenshots of one round of every game form were looked at.
- Not done: the piper build, any listening, any device.

## The fact sheet

# The facts for the pack "My village: staying well, land and weather" (use these; add nothing medical of your own)

Audience: village children about 8-14 and their teachers, far from a clinic. Written from standard public-health basics at the level of WHO and UNICEF material for families (hand hygiene, safe water, immunization, care of a sick child, child injury prevention). It was written from general knowledge of that guidance, not copied from a document, and no health professional has read it. The first rule for a child is always: stay safe yourself, tell an adult, get help.

## A. Health

### A1. Germs
- Germs are living things too small to see. Some of them make people ill. Hands, water or food that look clean can carry germs.
- Germs are in stool, in dirt and rubbish, and in unclean water.
- Four ways germs reach a person:
  1. Hands: after the latrine, after touching dirt, rubbish or animals, germs sit on the hands; the hands carry them to food and to the mouth.
  2. Water: stream water, open-well water and standing water can carry germs even when clear.
  3. Flies: a fly sits on dirt and then on food; germs stick to its legs.
  4. Coughs and sneezes: a sick person's cough or sneeze sends tiny drops with germs into the air and onto the hands; they reach people who are close.
- Closing the four ways (all as garden-1 and garden-2 already teach, plus covering a cough):
  1. Wash hands with soap and water: before eating and before preparing food, after the latrine, after touching animals, dirt or rubbish, after coughing, sneezing or wiping the nose. Water alone is not enough.
  2. Drink water that has been boiled, kept in a covered container, taken with a clean ladle.
  3. Cover food. Use the latrine, always. Keep rubbish in a pit away from the house and from water.
  4. Cover a cough or sneeze with the bend of the elbow or with a cloth, not with the palm. If you coughed into your hands, wash them with soap.

### A2. Vaccines (general terms only)
- A vaccine teaches the body to protect itself against some serious illnesses.
- Babies and children get vaccines at the clinic or from the vaccinator who comes to the village.
- A vaccine may hurt a little, and the arm may be sore afterwards. That is small and passes.
- Which vaccine and when: ask the health worker. She says when the child should come again.
- Vaccines protect against some serious illnesses, not against all illness: washing hands, safe water and covered food are still needed every day.
- Nothing else is to be said: no schedule, no vaccine names, no disease names, no ages, no statement about how well or how long a vaccine protects, no statement about what else may follow a vaccination.

### A3. Common illnesses: signs, and what to do in general
For all of them: tell an adult. Never give a medicine unless a health worker has said so. No medicine, dose, home remedy or name of an illness is taught beyond the everyday words "cough and cold", "fever" and "diarrhoea".

Cough and cold
- Signs: runny nose, sneezing, cough, sore throat.
- What to do: rest; drink plenty (clean water); keep eating; cover the cough; wash hands with soap so that others do not catch it.
- See the health worker if it does not get better, if a fever lasts, or if the person is very young or very weak. Fast or difficult breathing is a danger sign: clinic now.

Fever
- Fever means the body is hotter than usual.
- What to do: tell an adult; rest; drink clean water in small sips, often; take the blanket and extra clothes off; no icy water and no ice (same words as garden-3).
- See the health worker if the fever lasts, or if the person is very young or very weak.
- Danger signs, in the words of the garden-3 fact sheet ("go to the clinic NOW if the person"): cannot drink or breastfeed, or vomits everything; is very sleepy, hard to wake, or confused; has a fit; breathes fast or with difficulty, or the lips look blue; has a stiff neck with fever, or a baby under three months has any fever; has fever for more than two or three days. (The remaining points of that list are taught in garden-3 and not repeated here.)
- On the way or while waiting, as in garden-3: do not leave the person alone; small sips of clean water if they can swallow; never a medicine unless a health worker has said so.

Diarrhoea (exactly as garden-2 teaches it; nothing added)
- Tell an adult. Diarrhoea takes water out of the body, and that is dangerous for a small child.
- Oral rehydration salts (ORS) from the clinic, prepared by an adult: washed hands, a clean container, boiled and cooled water in the amount shown on the packet, the whole packet, stirred until dissolved. Given in small sips, often, with spoon and cup. If the child vomits, wait ten minutes and give more slowly.
- Keep giving breast milk and food. No fizzy drinks or very sweet drinks. No medicine on one's own.
- Danger signs: the child cannot drink, is very sleepy, has sunken eyes, has fever, or there is blood in the stool: clinic quickly.
- Prevention: hands washed with soap, boiled water, covered food, the latrine.

### A4. Staying safe outdoors
Roads and vehicles
- Walk at the side of the road, not in the middle; where there is no path, on the side where the vehicles come towards you, so that you see them.
- To cross: stop at the edge; look both ways and listen; cross when the road is clear; walk straight across, do not run. Do not cross from behind a standing vehicle or at a bend, where drivers cannot see you.
- A small child crosses only holding the hand of an older person.
- Do not play on the road; do not run after a ball onto the road; do not hang on to vehicles or carts.
- At dusk and at night drivers see people badly: come home before dark; in the dark wear light-coloured clothes or carry a light.

Rivers, streams, ponds and wells
- A small child is never alone near water: river, stream, pond, well.
- Do not go into fast or deep water. Muddy water hides how deep it is. Rivers are high and fast in spring (snowmelt) and after rain. Cross at a bridge.
- Someone has fallen in: do not jump in after them (then two people need help). Shout for adults. From the bank, hold out a long stick or throw a rope; the helper stays firmly on dry ground.
- Wells: do not lean over the rim or climb on it; keep the well covered; do not play near open wells or the shafts of a karez.
- In winter do not walk on the ice of a river or pond: it can break.

Heat
- In hot weather: drink clean water often, before you are very thirsty; cover the head; rest in the shade at midday.
- Signs of too much heat: headache, dizziness, great tiredness.
- What to do: go into the shade, lie down, drink clean water in small sips, put a wet cloth on forehead and neck, tell an adult. Someone who becomes confused or is hard to wake has a danger sign: clinic now.

Cold
- In the cold: several layers of clothes, cap, gloves, socks; change wet clothes for dry ones quickly.
- Strong shivering, or fingers or toes that are numb and white: go into a warm room and tell an adult. Warm numb fingers slowly, in a blanket or with the warmth of the body. Do not rub them with snow and do not hold them close to a fire (numb skin does not feel heat and burns). If they stay numb and white: health worker. Very sleepy or confused: danger sign, clinic now.

Storms and lightning
- When you hear thunder, go indoors quickly and stay there until the storm has passed.
- If no house is near: do not stand under a single tree; come down from a hilltop; stay away from water and from tall metal things. Do not stay in a gully or beside a stream either: rain water rises quickly there.

Animals
- Do not go near a dog you do not know; do not tease animals or throw stones at them; do not touch an animal that is eating, sleeping or has young.
- If a strange dog comes towards you: stand calmly, do not scream, do not run; walk away slowly.
- A bite or scratch, as garden-3 teaches: wash at once with soap and plenty of running water for 15 minutes; clinic the same day.
- Snakes hide under stones, in the woodpile and in long grass: wear shoes, look where you put feet and hands. Never touch a snake, even one that looks dead; move away calmly. Snake bite, as garden-3 teaches: keep the person calm and still; clinic now.
- Wash hands with soap after touching animals (garden-1).

Getting lost
- Before you go: tell an adult where you are going; do not go far alone; come back before dark.
- If you are lost: stop. Stay where you are, in an open place, and call out. The people looking for you find you sooner if you do not walk further. Keep warm.
- Know the name of your village and of your father, so that you can ask an adult for help.

An unknown object
- An unknown object on the ground: do not touch it, move away, tell an adult.
- Nothing more specific is to be written. The spec leaves the specialist material on dangerous objects to the local team.

## B. Environment (school-level facts; a teacher or agronomist checks them for the region)

Soil
- Soil is made of rock broken small over a very long time (sand, small stones, clay), of rotted leaves, roots and plants (the dark, soft part that feeds plants), of water and air, and of small living things such as earthworms and insects. Earthworms make holes that let water and air reach the roots.
- Soil forms very slowly (a finger's width in hundreds of years) and is lost quickly: on a bare slope rain runs down fast and carries the soil away; wind carries away dry bare soil.
- What holds soil: roots of trees and grass; leaves that break the force of rain; low stone walls and level steps across a slope, which slow the water; replanting where trees are cut; not letting animals graze a hillside bare.

Compost
- Kitchen peelings, leaves, straw and animal dung, gathered in a pit or heap, kept a little damp and turned now and then, rot in some months into a dark, soft material that smells of earth. Mixed into the field before sowing, it feeds the soil.
- Plastic, glass and tins do not rot and do not belong in it.
- The pit is kept away from the well and from water. Wash hands with soap after working with compost or dung.

Crops through the year
- A plant needs water, sun and good soil.
- The steps: prepare the soil (plough), sow, water, weed, harvest, dry and store.
- Weeds take water, food and light from the crop; they are pulled out with the root.
- Wheat: sown in autumn (it rests under the snow) or in spring; green in spring; ripe and yellow in summer; cut with the sickle, bound, and the grain separated from the straw.
- Maize: likes warmth; sown in spring when the soil is warm; ripe in autumn.
- Potatoes: a potato with eyes is planted in spring; new potatoes form under the ground; dug in late summer and autumn.
- Fruit trees: blossom in spring; every flower can become a fruit; apricots and mulberries ripen in early summer, apples, grapes and walnuts in autumn.
- Storing: grain is dried well in the sun and kept in a dry place, off the ground, in sacks or a closed bin, away from mice. Damp grain goes mouldy and is spoiled. The best grain is kept as seed for next year.

Water sources
- Rain and snow fall on the mountains. Part runs off in streams and rivers; part sinks into the ground and collects there.
- Spring: a place where the water under the ground comes out by itself.
- Well: people dig down until they reach the water under the ground; it is raised with bucket and rope or a pump.
- River and stream: water from snow and rain running down from the mountains; full in spring when the snow melts, low in late summer.
- Karez: an underground water channel dug by earlier generations. It starts at the foot of the mountains, where there is water under the ground, and runs as a long, gently sloping tunnel to the village. Along it is a row of shafts, through which the earth was taken out and through which the karez is cleaned. The water flows by itself, without any machine, and because it runs under the ground little of it is lost to the sun. The village cleans its karez together.
- Any source can carry germs even when the water is clear: drinking water is boiled, as garden-2 teaches.
- Keeping a source clean: the well covered; bucket and rope not laid on the ground; the place around the well clean, so that standing water does not run back in; latrine, rubbish pit and compost pit far from well and spring (garden-2); no rubbish in the water.
- Upstream and downstream: water always runs downhill. Whatever gets into the water higher up is carried to the people lower down. Drinking water is taken above the place where clothes are washed and animals drink. Every village is downstream of someone and upstream of someone else.

Weather
- A cloud is made of very small drops of water (garden-2). When the drops grow big and heavy, rain falls; when the air is very cold, snow falls instead.
- The snow on the mountains is the village's store of water: it gathers in winter and melts slowly in spring and summer into rivers, springs and karez. Little snow in winter means little water in summer.
- Hail is pieces of ice from a storm cloud; it damages blossom and fruit.
- Wind is moving air (garden-2 nature pack). It brings and takes the clouds, separates grain from chaff, and carries away dry bare soil.
- Frost: on clear, still, cold nights a white layer of ice forms on the ground and on leaves. A cloudy sky keeps the ground warmer, like a blanket. A frost in spring, when the trees are in blossom, kills the flowers, and there is little fruit that year.
- Lightning and thunder happen together; we see the lightning first because light is faster than sound (garden-2 nature pack).
- Signs of weather: dark, tall clouds, a rising wind and distant thunder mean a storm is near; a clear, still night in spring or autumn may bring frost.
- Seasons and farm work: spring (plough, sow, plant saplings and potatoes), summer (water, weed, harvest wheat), autumn (pick fruit, harvest maize and potatoes, sow autumn wheat, store, gather firewood), winter (clear snow from the roof, feed the animals dry fodder, mend tools).

Never write: doses, names of medicines, home remedies, names of vaccines or of the illnesses they prevent, a vaccination schedule, diagnoses, anything specific about dangerous objects, anything religious or political, anything that blames a family.

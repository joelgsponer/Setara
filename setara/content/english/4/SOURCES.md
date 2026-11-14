# English 4 "At the bazaar": what it teaches, what was decided, what is open

**Nothing here has been reviewed by a person.** The pack was written by an AI
(Claude) from the curriculum in the product spec (section 8: level 4, "Buy
and sell, ask prices and quantities, ask and answer questions politely; How
much / many, can, some / any, reading short sentences"). Nobody has heard the
audio, and it has not been run in the app (no LÖVE on the authoring machine);
the builder validated and built it.

## What the pack teaches

20 units, one per classroom lesson; the unit list with every word and
sentence is in `syllabus.md` (generated from `items.csv`).

| Units | Topic | Language |
| --- | --- | --- |
| 01-04 | The bazaar, buy and sell, prices, money | I want to buy ..., He sells ..., How much is it? It is ... afghani. Here is your change. |
| 05-06 | Fruit and vegetable stalls | How much are the ...? They are ... |
| 07-09 | Kilo, how many / how much, bottles and packets | a kilo of, half a kilo of, How many ... do you want? How much ... do you want? a bottle / packet / jar of |
| 10 | Review | |
| 11-12 | The food shop, some and any | I need ..., I have some ..., Do you have any ...? No, I don't have any. |
| 13-14 | Can, the bakery | Can I help you? I can / can't ..., Can I have ..., please? Of course. |
| 15-16 | The tailor, things for the house | metres of, I need a ... and some ... |
| 17-18 | Polite questions, bargaining | Excuse me, where ...? You're welcome. Anything else? That's all. It is too expensive. Can you make it cheaper? all together; hundreds |
| 19-20 | What do you sell?, review | open / closed, the whole shop dialogue |

Eleven games, 76 rounds, 564 items:

| Game | Engine | Rounds | What it adds |
| --- | --- | --- | --- |
| Word Stall | listen_pick (from items) | 20 | hear the word, pick the picture |
| Echo | say_it (from items) | 20 | every word, sentence and dialogue of the unit, spoken by the child |
| Basket Catch | catch | 3 | a rule spoken in English: the fruit, the money, things you can / can't eat |
| Sentence Train | builder | 8 | sentence order from written words; the extra tile is the typical mistake (is / are, much / many, some / any, can / can't) |
| Shopkeeper | market | 7 | count: fruit, one-kilo weights, bottles and packets; pay: tens, any price to 100, hundreds; round 20 is a whole purchase (serve, then pay) |
| Radio Stories | story | 3 | three stories with three decisions each (pick a thing, count, a price, the polite answer) and a caption to read along |
| Price Tags | listen_pick | 3 | hear a price, pick the number (thirty / thirteen, 65 / 56, 150 / 115) |
| Stall Pairs | pairs | 5 | reading: written word to picture |
| Which Basket? | sorter | 3 | fruit / vegetables; How many? / How much?; a / an / some |
| Bazaar Road | journey | 2 | mixed listening questions (who sells, how much change, what do you say) |
| Read and Pick | listen_pick | 2 | reading without hearing: the word or two-word phrase is only shown |

## Decisions taken

- **Size.** 76 rounds, not "about 60": Word Stall and Echo are derived from
  the word bank as in levels 1 and 2 (40 rounds), and the nine sheet games add
  36. Word Stall rounds have 4 to 7 pictures, like the model.
- **New words: fewer than the target.** The spec asks for about 250 new words.
  The pack has 266 different word forms; 126 of them do not occur in levels 1
  to 3 (about 100 dictionary words: plurals and "sells / wants" counted
  once). A unit is one Echo round of at most 11 items, and every pictured
  word needs a picture a child can read at 3 cm, so 20 units carry about 6
  new words each plus the new sentence patterns. Reaching 250 needs either
  second rounds per unit (`05b` ...) with some 100 more pictures, or a
  decision that level 4 is smaller. **Open.**
- **Level 3 was written at the same time.** Assumed known from level 3: daily
  routine, time, home, clothes, numbers to 100, do / does. Level 3 turned out
  to teach `scarf`, `carry`, `lamp`, `candle` and `button` too; they are kept
  here (tagged review) because the shop dialogues need them.
- **Dari help stays on Y, but less Dari is spoken up front**: the rules in
  Basket Catch and the questions in Bazaar Road are English only; sorter
  baskets are said in Dari and then English.
- **"Can"** is translated with the Afghan form the level 1 pack already uses
  («گپ زده می‌توانم»): «برده می‌توانم», «خورده نمی‌توانی», «کمک کرده
  می‌توانم؟».
- **"tin", not "can"**, for the container, so that it does not collide with
  the verb. British spelling as in levels 1 and 2 (metre, colour, yoghurt).
- **Shop talk is polite**: customers and shopkeepers say «شما», and "Here you
  are" in a shop is «بفرمایید» (levels 1 and 2 have «بفرما، بگیر» between
  children).
- **Prices are round teaching numbers**, not market prices (bread 10, a kilo
  of rice 90, a scarf 300 afghani).
- **Hundreds** (one hundred and fifty ...) appear from unit 18; level 3
  counts to 100.
- **Reading.** Text on a card is one line and must stay 24 px high, so cards
  carry single words or two short words. Sentences are read in the story
  captions and built in Sentence Train.
- **"sack"** got its own plain picture, because `rice_sack` beside `rice`
  would give two right answers. For the same reason "money" is not in the
  unit with "coin" and "note", "bread" is not in the bakery unit, and "shop"
  is not in the unit that reviews "bakery".
- **`scarf_red`, `scarf_blue`** copy the shape of level 3's `scarf.svg`.
- **Girls and boys.** Stories: Mina (girl), Hamid (boy), Roya and her brother
  Navid. Dialogue voices alternate; the woman's voice is the seller about as
  often as the man's. The pictures show the shopkeeper and the tailor as men
  and the customer as a girl; "help" shows a girl and a boy.
- **Names** (Mina, Hamid, Roya, Navid) are common first names, not people.

## New pictures (52, listed in `pictures.txt`)

40 things and 12 story scenes, drawn as SVG by the same AI and looked at
rendered. Weakest:

- `cheap` / `expensive`: a pot with one coin, the same pot with a pile of
  coins. The idea has to be taught; the picture alone does not say it.
- `price`: a tag with a coin on it (no digits allowed in pictures).
- `kilo`: an iron weight with a ring. Are weights in the local bazaar this
  shape, or flat pieces or stones?
- `bazaar` (three stalls) beside `shop` (one stall) in unit 01: the
  difference is "many shops" against "one shop".
- `tailor` is small on its card; `metre` can be read as "ruler"; `note` is a
  made-up green note; `melon` is an oblong yellow melon and must not be taken
  for a lemon.
- `pay` and `purse` both show a coin; in unit 04 they stand beside `coin`.
- Scenes: the figures are generated from one drawing each, so a person looks
  the same in every scene of a story. The shopkeeper of story 10 and the one
  of story 20 differ only by the colour of their clothes.

## For the Dari-speaking reviewer

Word choices to confirm or replace (Afghan Dari was intended throughout):

- expensive «گران» (colloquial «قیمت» was avoided because "price" is «قیمت»);
  cheaper «ارزانتر»; "How much is it?" «قیمتش چند است؟», "How much is the
  bread?" «نان چند است؟».
- change «باقی پول»; note «نوت»; purse «بکس پول»; coin «سکه».
- stall is not taught as a word (the picture `shop` is a stall). cart
  «کراچی»; street «سرک»; sack «بوجی»; tin «قطی»; jar «مرتبان»; packet
  «پاکت»; shelf «رف».
- pear «ناک»; banana «کیله»; melon «خربوزه»; peach «شفتالو»; cherries
  «گیلاس»; cucumber «بادرنگ»; eggplant «بادنجان سیاه»; pepper «مرچ»; cabbage
  «کرم»; lentils «دال»; biscuits «کلچه»; juice «آب میوه»; matches «گوگرد»;
  cloth «تکه»; thread «تار»; scarf «چادر» (as in level 3); firewood «هیزم»;
  charcoal «زغال»; umbrella «چتری».
- need: «به ... ضرورت دارم» (or «کار دارم»?). some «کمی» / «چند»; any in a
  negative «هیچ ندارم»; "Do you have any eggs?" is simply «شما تخم مرغ
  دارید؟».
- "You're welcome" «قابل تشکر نیست»; "Excuse me" «ببخشید» (the same word as
  "sorry"); "Of course" «البته»; "All right" «خوب است»; "That's all" «همین
  قدر بس است»; "Anything else?" «چیز دیگر؟»; "all together" «جمله چند
  می‌شود؟»; "sixty afghani a kilo" «کیلوی شصت افغانی».
- Hundreds are written «یکصد، دوصد، سه‌صد، چهارصد، پنجصد، نُه‌صد» as in the
  math packs.
- «پُر» (full) and «نُه» (nine) carry a vowel mark for the voice.
- The weights in Shopkeeper round 07 are called «سنگ یک کیلویی».
- The basket "an" is explained as «یک، پیش از حرف صدادار». Is «حرف صدادار»
  the school word for vowel?

## For the teacher or educator

- Is bargaining ("It is too expensive. Can you make it cheaper?") wanted as
  classroom language? It is how the bazaar works, and unit 18 and story 20
  teach it as polite speech.
- Story 15: a boy of twelve sells eggs from a cart on his own, and a woman
  customer asks him to carry her basket. Story 10: a girl goes to the bazaar
  alone with money. Acceptable everywhere the device goes?
- Story 20: the children get the scarf for 300 instead of 350 afghani
  because that is all they have. Good lesson or wrong one?
- The sorter round "a / an / some" and the round "How many? / How much?"
  teach grammar by sorting. Too abstract for the youngest in level 4?
- Shopkeeper has the child pay as the customer, although the game is called
  "Shopkeeper"; the spoken introduction of those rounds says so.
- In Read and Pick the spoken question is always the same Dari instruction
  ("Read and choose the right picture"), because the word must not be said.
  X repeats that instruction, Y says the Dari meaning.
- Echo rounds with three-turn dialogues are long to say back; two children
  can take the two voices.
- Numbers above one hundred are new in unit 18 and are only practised in
  three rounds.

## For whoever listens to the audio

- "a", "an" and "some" are spoken alone as basket names: a voice may say the
  letter name "ay" for "a".
- thirty / thirteen and the other tens against teens carry Price Tags
  round 03.
- "afghani", "kebab", "samosa", the names Mina, Hamid, Roya, Navid.
- Dialogues switch between the two voices up to four times in one clip.

## Not done

- No teacher lessons for level 4 (`content/teacher/`): this pack is the
  learner side only.
- Not run in the app: `tests/fuzz_rounds.lua` should be run once the pack is
  on a card.

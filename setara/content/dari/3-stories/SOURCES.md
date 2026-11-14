# Sources and review status of fa-3-stories (Dari story book)

**This pack is optional** (`"optional": true`): a separate zip that adds four
story games to Dari level 3. Leave it off the card and nothing of it is there.
No other pack refers to it.

It is for children who can already read: "real stories, maybe sometimes a
picture". Each round is one story with a beginning, a problem and an end,
told on reading pages (text only, the whole screen, 4 to 7 lines), with a
picture page at the start and one or two in between, and three questions
placed after the passage they ask about. Every page is still spoken.

**Not yet read or heard by a Dari speaker.** All of it was written by an AI
(Claude). `content/i18n/dari_stories.csv` carries a faithful English of every
Dari text, paragraph for paragraph, so that a reviewer who reads English can
follow what each page says.

## The games

| Game | Stories (rounds) | Reading pages | Words of Dari per story |
| --- | --- | --- | --- |
| `animal_tales` قصه‌های حیوانات | 4 | 6 each | about 240 to 255 |
| `village_tales` قصه‌های بچه‌های قریه | 4 | 7 each | about 275 to 305 |
| `mulla_tales` قصه‌های ملا نصرالدین | 4 | 6 each | about 255 to 270 |
| `wonder_tales` شگفتی‌های زمین و آسمان | 4 | 7 each | about 305 to 340 |

16 stories, 191 pages: 104 reading pages, 39 picture pages, 48 questions
(three per story). 44 questions have written answers, 4 have picture answers.
Every story has at least one "why" question (25 in all). The right answer is
first 14 times, second 20 times, third 14 times; the app shuffles the cards
as well. The games run from easier (short sentences, familiar fables) to
harder (longer sentences, facts about nature).

## Where every story comes from

Nothing was copied or translated from a modern book, website or published
translation. The traditional tales are old and in the public domain; they
are retold here from the bare plot, in new words, and some endings were made
gentler. Everything can be published under CC BY-SA 4.0.

| Round | Story | Source |
| --- | --- | --- |
| `animal_tales` 01 | زاغ تشنه, The thirsty crow | Retelling of the Aesop-type fable known across the region (crow, jar, pebbles). The scene in the dry village is added. |
| 02 | روباه و لک‌لک, The fox and the stork | Retelling of the Aesop-type fable. **The ending is new:** in the old fable the stork only pays the fox back; here the fox laughs, says sorry, and both eat. |
| 03 | سنگ‌پشت و خرگوش, The tortoise and the hare | Retelling of the Aesop-type fable. New ending: the hare takes it well and asks for another race. Nobody is mocked. |
| 04 | کبوترها و جال, The doves and the net | Retelling of the frame tale of the ring-dove and the mouse from Kalila wa Dimna / Anwar-i Suhayli (itself from the Panchatantra). Told from the plot only; no translation was used. |
| `village_tales` 01 | راز تخم‌های گمشده, The mystery of the missing eggs | Original. (That a broody hen hides her nest, and that eggs hatch after 21 days, are facts.) |
| 02 | راه خانه, The way home | Original. |
| 03 | گدی‌پران شبنم, Shabnam's kite | Original. |
| 04 | توپ تکه‌ای, The rag ball | Original. |
| `mulla_tales` 01 | ملا نصرالدین خرها را می‌شمارد | Traditional Mulla Nasruddin anecdote (he forgets to count the donkey he rides). In the old joke his wife or a passer-by puts him right; here it is a neighbour's daughter. |
| 02 | ملا نصرالدین و دیگ همسایه | Traditional Nasruddin anecdote (the pot that gave birth and died). **Ending softened:** traditionally the Mulla keeps the pot; here both laugh and he gives it back. |
| 03 | ملا نصرالدین و ماه در چاه | Traditional Nasruddin anecdote (the moon in the well). The last page, in which his daughter shows him the moon in a bowl of water, is added. |
| 04 | ملا، پسرش و خر | Traditional tale told of Nasruddin and in many other countries (the man, the boy and the donkey). In this version the donkey only gets wet and runs home. |
| `wonder_tales` 01 | چرا ماه شکلش را تغییر می‌دهد؟ | Original story around facts: the moon has no light of its own, half of it is always lit by the sun, it goes round the Earth in about a month. |
| 02 | سفر یک قطره آب | Original story of the water cycle: melting snow, stream, river, sea, evaporation (the salt stays behind), cloud, snow. |
| 03 | راز زنبورهای عسل | Original story around facts: a returning bee shows the others where flowers are by a "waggle dance" (direction relative to the sun, longer waggling for a greater distance); honey is made from nectar; one worker bee makes less than a teaspoon of honey in her life (the usual figure is about a twelfth of a teaspoon); worker bees are female. |
| 04 | ستاره‌ای که راه را نشان می‌دهد | Original story around facts: the Pole Star stays almost in place above the Earth's north pole while the other stars seem to turn because the Earth turns; it is found from the two stars at the edge of the bowl of the Big Dipper, about five times their distance. |

Heroes: four girls (Farida, Shabnam, Nasrin, Zohra) and three boys (Yasin,
Omid, Hamid) carry the original stories, the eighth is a drop of water; in the Nasruddin tales,
whose hero is a man by tradition, two girls (Zarghuna, Maryam) are the ones
who see how things really are. The names are ordinary first names, not real
people.

## Decisions taken

- **Reading is the exercise.** The written answer cards are not read aloud
  (`read_choices` is not set), as `docs/authoring.md` asks where reading the
  word is the point. The question itself and every page are spoken. After a
  wrong answer the guide gives a hint and the right answer; it never says
  "wrong".
- **Homographs and the synthetic voice.** Words a voice could misread carry a
  vowel mark, as in the earlier packs: نُه، خُرد، گُل، پُر، دُم، پُل، بُرد، مُرد،
  مَرد، گِل، گِرد، گَرد، دَور، تَر، کِشتزار، می‌بُرَد، می‌بَرد، دَم. The marks are also
  shown on the page. The word «نه» (no) is avoided, «قریه» is used for
  village (never «ده»), «دروازه» for door.
- **River and sea.** As in the rest of the app, a river is «دریا» and the sea
  is «بحر».
- **Pictures.** Of the 39 picture pages, 21 reuse library things (hen,
  stream, moon …), 8 use pictures drawn by others for the English story book at the same time
  (`scene_crow_jug`, `scene_tortoise_hare`, `scene_doves_net`,
  `scene_nasruddin_donkeys`, `scene_ball_lamp`, `scene_river_course`,
  `scene_boy_sheep_hill`, and the thing `kite`), and 10 scenes were drawn for
  this pack (`pictures.txt`). None has been seen by a local reviewer.
- The sheets were written out by a small script from the story texts; the
  CSV files are the source from now on.

## What a human reviewer has to decide

**Language (a Dari-speaking educator):**

- Read every story aloud. The AI aimed at simple written Afghan Dari with
  everyday words: گپ، ایلا کردن، ماندن (to put), کلان، خُرد، چوچه، بچه‌ام، بابه
  جان، بی‌بی، ماما، کاکا، تیار، خلاص شد، خفه (upset), مانده (tired), ناوقت،
  چک‌چک، پالیدن، چسپاند، پیسه، تکه، گول، موتر، مرغانچه، چپلی، لنگی، دسترخوان.
  Replace whatever sounds wrong, bookish or regional.
- Words I am least sure of: «نول» (beak; منقار?), «سنگریزه» (pebble),
  «غبار» for fog, «کُرک شده است» (the hen is broody; کُرچ?), «جال» (net),
  «شانه عسل» (honeycomb), «شیره گُل» (nectar), «شاخک» (a bee's feelers),
  «ملاقه» (ladle), «تیله کرد» (pushed), «دَم می‌گیرم» (I will rest),
  «خُر می‌زد» (snored), «علامه جمع / علامه سوال» (plus sign, question mark).
- **«هفت برادران»** is used for the Big Dipper and **«ستاره قطب»** for the
  Pole Star. Confirm that this is what the children's elders call them (دب
  اکبر is the book name).
- **«رقص زنبور»** (the bee's dance) is the scientific name of what the bee
  does. If the word dance is unwelcome, «حرکت» or «چرخیدن» can replace it in
  five places in `wonder_tales` round 03.
- Ezafe is written only where a reader could stumble (تهِ کوزه، کبوترِ پیر).
  The app as a whole has not settled this.
- Is the level right? Sentences are short in the first game and longer in
  the last; a page has 35 to 60 words. Level 3 of the curriculum is
  "syllables and words", so this book is for the children who are ahead.

**Content (the local team):**

- **Mulla Nasruddin.** The tales are folk humour with no religious content,
  but their hero carries the title «ملا» and is laughed at (he laughs first).
  If that is not wanted, the game `mulla_tales` can be removed from
  `pack.json` on its own, or the name changed.
- **A girl flies a kite on the hill** (village_tales 03) and children play
  football on a Friday (04). Both are ordinary in many places and not in
  others.
- In the pot story a pot "gives birth" and "dies". It is the old joke; say
  if it is not suitable.
- A girl and her maternal uncle walk home across the plain at night after
  their car breaks down (wonder_tales 04); a boy is caught in fog with the
  sheep and gets home safely (village_tales 02). Nothing bad happens in any
  story, and nobody is punished or shamed.
- The hunter in the doves' tale only sets a net and is left standing; no
  animal is hurt in any story.

**Facts (a teacher):**

- The four `wonder_tales` are simplified but meant to be true. Check the
  sentences "آب زمین همان آب است، فقط سفر می‌کند", "همیشه نیم ماه روشن است",
  "ماه در حدود یک ماه، یک بار به دَور زمین می‌چرخد", "پنج برابرِ فاصله آن دو"
  and "کمتر از یک قاشق چای‌خوری عسل".
- The water drop travels from a mountain by a river to the sea. Most rivers
  of Afghanistan do not reach the sea; the story names no place.

**Form:**

- Written answer cards hold two or three words and are drawn at 24 to 30 px
  by the engine (one line, shrunk to the card). 13 of the 133 written cards
  come out below 30 px, the smallest at 26 px. The project rule is Dari at
  least 30 px; shorter answers would make the "why" questions poorer.
- `scene_moon_phases` shows the moon's shapes right to left (the way Dari is
  read) with the waxing moon lit on its right side, as seen from Afghanistan.
- The pictures of Mulla Nasruddin come from two hands (`scene_nasruddin_donkeys`
  and `scene_moon_in_well`); he has a white turban and a blue coat in both.
- Nobody has listened to the speech. The stand-in Persian voice is Iranian.

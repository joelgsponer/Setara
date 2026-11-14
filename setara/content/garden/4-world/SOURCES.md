# Sources and review status of garden-4-world (The world, Switzerland and Basel)

**This pack is optional.** It ends by telling the children where the device
and its lessons come from: Basel, in Switzerland. The local team may or may
not want that said. It is a separate zip (`"optional": true`): leave it off
the card and nothing of it is there. No other pack refers to it.

**Version 2 is a rework.** Version 1 asked for the same seven continent
outlines and the same two country maps round after round, and quizzed more
than it taught. Version 2 keeps the journey (whole world, continents, Asia and
Afghanistan, the long way west, Europe, Switzerland, Basel) but every round
teaches something new, and every new idea is explained in a story before a
game asks for it.

**Not yet read or heard by a Dari speaker. Nothing has been heard at all:**
the pack was only built with silent speech. Every fact is taken from the fact
sheet at the end of this file: first the sheet the pack was started from,
then the extension written for version 2. `content/i18n/world.csv` carries the
faithful English of every Dari text.

## The games

| Game | Engine | Rounds | What it is |
| --- | --- | --- | --- |
| `world_session` | story | 3 (14, 15, 14 pages; 3, 4, 4 decisions) | The journey. Our round Earth and its seven continents; the long way west to Switzerland; Basel. For a teacher with the class (Story Time) or a child alone |
| `world_why` | story | 7 (7 to 13 pages; 2 decisions each) | The explanations, one idea per story: day and night; oceans, island and lake; hot and cold; what a map is; the sun, the four directions and the time in Basel; a river from the mountains to the sea; children far away |
| `world_continents` | listen_pick, choices read aloud | 4 of 7 or 8 | Shapes of the continents; the five oceans; landforms; hot and cold |
| `world_map` | listen_pick, choices read aloud | 2 of 7 | The signs and colours of a map; the long way on the map |
| `world_two_countries` | sorter | 5 of 7 or 8 | Five different sets of baskets: land / water; hot / cold; Africa / Asia / Oceania / Antarctica; land / water / air; Afghanistan / Switzerland / both |
| `world_journey` | journey, choices read aloud | 4 of 8 | The four directions; Afghanistan; Switzerland; Basel |
| `world_order` | builder | 2 of 6 sequences | Large to small, the way of water, the day, slow to fast, east to west, few to many |
| `world_pairs` | pairs | 3 (6, 4, 6 pairs) | Animal and its home; a greeting and its place; things of Switzerland and Basel |
| `world_catch` | catch | 2 of 4 rules | In the sea, on the mountain, in the air, for travelling; winter, waters, the festival, on the Rhine |

32 rounds. The game ids of version 1 are kept (`world_two_countries` is now
"World Baskets"), so `tools/film/tour.lua` and `tools/screenshots.lua`, which
open `world_session` rounds 1 and 3, need no change. Round 3 is still Basel.

## Explaining before asking

- Each story of `world_why` explains one idea with something a village child
  knows: a ball and a lamp for day and night; the cool slanting morning sun
  and the hot midday sun over the courtyard for the cold poles and the hot
  middle of the Earth; an eagle looking down on the village for what a map
  is; the right hand stretched towards the sunrise for the four directions;
  the stream by the village for the way of a river. Each story ends with a
  page that begins "Remember:".
- Every question in the listen_pick and journey games has a Dari help text on
  Y that says why the answer is right. Every builder and catch item has one
  too. Every wrong choice in a story explains what is wrong with it and gives
  a hint, without naming the answer where it can be avoided.
- Every round begins with an instruction of its own (`intro_fa`) that says
  what the round is about and the one thing to remember.
- Sorter and pairs have no help column in the sheet format. Their facts are
  explained in the stories and, for pairs, spoken when a card is turned.

Explanation pictures drawn for this: `scene_ball_lamp`, `scene_earth_sun`,
`scene_sun_poles`, `scene_village_map`, `scene_morning_night`,
`scene_directions`, `scene_river_course`, the series `sun_morning`,
`sun_noon`, `sun_evening`, the four `map_sign_*`, and the generated maps
`scene_map_hot_cold`, `scene_map_ocean_*`, `scene_map_afghanistan`,
`map_afghanistan_land`, `scene_map_rhine`.

## No fact is the answer more than twice

The rule: once to learn, at most once more as a review. It was counted over
the sheets with a script (the counts are in the hand-over report): the answer
of every question and story decision, every thing-and-basket of the sorter,
every pair, every builder sequence and every catch rule. 153 different
answers, 130 asked once, 23 asked twice, none more often. No continent
outline is an answer more than twice. The five sets of sorter baskets are all
different.

What the script cannot see is one fact asked in two different forms. Read by
hand, the facts that come close to a third use are: "Afghanistan is in Asia"
(a story decision, then the first builder sequence), "cheese is made from
milk" (a story decision, then a builder sequence), "the polar bear lives in
the cold north" (a story decision, then the hot / cold baskets), and the time
difference (night in Basel at sunrise in Kabul; morning in Basel at midday in
Kabul; the builder sequence from east to west), which is asked in three
different ways on purpose.

## Where the pack simplifies, or words something its own way

- The session and the explanation stories speak to the class in the plural
  (گوش کنید، انتخاب کنید). The other games speak to one child.
- **Day and night** is the turning Earth only. The seasons, the tilt of the
  axis and the long polar day and night are left out. "The sun does not move"
  is said in that sense.
- **Hot and cold** is explained by the slant of the sunlight and by height
  alone. Not every place near the equator is hot (high mountains) and deserts
  are cold at night; the pack does not say so.
- **The time in Basel** is "about three hours" behind Kabul. It is three and
  a half hours in winter and two and a half in summer. "When you are at
  school, the children of Basel are just waking up" is true for the later
  part of a school morning.
- **In the sun pictures and on maps east is on the right.** The three sun
  pictures are drawn looking north. If the pictures are redrawn, the sentence
  "in these pictures east is on the right" must follow.
- **The oceans** are shown with straight lines between them where there is
  open water (20 and 147 degrees east, 68 degrees west, 60 degrees south, the
  polar circle). The Mediterranean, Black and Caspian Seas are left pale.
- **The warm belt** on `scene_map_hot_cold` is the band between the tropics;
  the cold caps are inside the polar circles. The spoken text only says
  "hottest part" and "coldest part".
- **Animals as hooks for the continents.** Lions also live in a small part of
  India, a bison lives in Europe too, some kangaroos live on New Guinea, and
  penguins live on several southern coasts. The pack says "the lion lives on
  the plains of Africa", "the kangaroo lives only in Australia", "the panda
  lives only in Asia", "the penguins have their home in Antarctica". The
  elephant is used only as "lives in warm places" and as the largest land
  animal, because it lives in both Africa and Asia.
- **"The largest animal in the world" is the blue whale;** the reason given
  ("the water carries its weight") is a child's version.
- **The Amazon** is called the largest rainforest (جنگل بارانی), not the
  largest forest.
- **A map** uses blue for water, brown for mountains and green for trees, as
  many school maps do. "People have agreed to draw north at the top" is true
  of nearly all modern maps.
- **Afghanistan's neighbours** are named once in a story and once in a help
  text, as a plain list of six, and asked only as a number. No border is
  drawn or described. The maps outline Afghanistan and Switzerland and no
  other country, except the three colours at Basel. Version 1 left the
  neighbours out altogether: see the open questions.
- **Rivers of Afghanistan:** Amu "in the north", Helmand "the longest, to the
  south-west", Harirud "to the west", Kabul river "through Kabul". On the
  maps the Amu is drawn only where it runs along the edge of the country. The
  Kabul river is not in the map data and is not drawn.
- **The Salang tunnel** is named as "our tunnel in the Hindu Kush" beside the
  Swiss tunnels; "has dug tunnels under its mountains" is in the "both"
  basket.
- **Greetings:** Salaam (Afghanistan), Grüezi (Basel), Jambo (East Africa,
  Swahili), Hola (South America, "many people": Spanish; Portuguese Olá
  sounds almost the same). No other greeting is used.
- **Food:** tandoor bread here, bread and cheese in Switzerland, rice in East
  Asia, maize in much of Africa and America. One sentence each, no ranking.
- "The children of Switzerland go to school like you" says nothing about who
  goes to school here.
- A tram is explained as "like a small train that runs on rails in the middle
  of the city", a globe as "a small model of the Earth", a continent as "like
  a very large courtyard with room for many countries", the map of the world
  as the Earth's surface "flattened like the peel of an orange".
- The Rhine is "like a road of water to the sea"; the swim bag "is closed and
  full of air".
- The closing sentence is said once, on the last page of the Basel story,
  with no names: "The lessons and pictures on this device were made in Basel.
  They were made by people who wish you well."
- The zoo, the museums, the university, the port and the medicines are spoken
  but have no question. `scene_university` of version 1 is no longer used.
- Written Dari words are choices in `world_continents`, `world_map` and
  `world_journey`; all three have `"read_choices": true`, so each card is
  read aloud. The sorter has a few written cards and baskets (خشکه، آب، گرم،
  سرد، زمین، هوا، هر دو، کابل، برن، هندوکش، الپ، هلمند، اورست، بحر ندارد); each
  is spoken when it comes up and the baskets are spoken at the start and on
  Y. Counts are digits, as in the maths packs.

## Open questions for a reviewer

1. **Neighbours of Afghanistan.** The first fact sheet said not to name
   them. Version 2 names the six once as a list and asks "how many?" (6).
   If the local team would rather not, remove the page after the map of
   Afghanistan in `world_session` 02 and the last row of `world_journey` 02.
2. **Is "three hours" the right roundness** for the time difference, or
   should it be "two to three hours" or "three and a half"?
3. **Words for the continents and oceans** (below): which do the children's
   school books use?
4. **شیر** is both lion and milk in writing. The lion is always introduced
   with the animals (شیر و زرافه، شیر در دشت‌های افریقا) but the speech voice
   may say it like milk. Someone must listen.
5. **Greetings in other languages** written in Dari letters (گروتسی، جامبو،
   اولا) will be said by a Dari voice. Someone must listen, and decide whether
   the pairs round with the four greetings works by ear.
6. **The explanation of the cold poles** (`world_why` 03, picture
   `scene_sun_poles`): is the step from the morning sun in the courtyard to
   the slanting light at the pole clear to a child, with this picture?
7. **The experiment with the ball and the lamp** is described, not done. A
   teacher could do it in class; should the teacher pack say so?
8. **Catch, "on a high mountain":** snow, cave, eagle, goat, stone. Fair for
   the children here, or too loose? The other things in that rule are from
   the sea, so there is no doubtful case on screen.
9. **Small maps beside a question.** A map shown with a question is about
   120 pixels wide. The ocean maps, the route and the hot-and-cold map are
   first shown full screen in a story; the questions are worded so that the
   answer does not depend on fine detail. Check on a real screen.
10. **The 36 hand-drawn pictures and 9 generated maps of version 2 are
    unreviewed,** like the 23 of version 1. The girl in `scene_ball_lamp`,
    the boy in `scene_directions` and the swimmer in `swim_bag` are pictures
    of people and need the local reviewer.

## Dari wording a reviewer should check

- **Continent.** قاره is used throughout; the first mention adds "some people
  also say براعظم". Choose whichever the children's school books use.
- **Ocean.** Afghan Dari says بحر for the sea and for the oceans. The pack
  says "very large seas, called اقیانوس" and then names them the Afghan way:
  بحر آرام (Pacific; بحرالکاهل is also used), بحر اطلس (Atlantic), بحر هند
  (Indian), بحر منجمد جنوبی (Southern), بحر منجمد شمالی (Arctic).
- **Antarctica** is انترکتیکا with "at the South Pole" (در قطب جنوب).
  **Oceania** is اقیانوسیه with "Australia is in it"; some school books call
  the continent آسترالیا.
- **Equator** خط استوا; **poles** قطب شمال، قطب جنوب; **directions** شرق، غرب،
  شمال، جنوب; **compass** قطب‌نما, its needle سوزن, magnet آهن‌ربا.
- **Landforms:** island جزیره, lake جهیل, river دریا (so the sea is بحر),
  stream جوی, pond حوض, desert صحرا (دشت is used for a plain), sandy desert
  صحرای ریگی, forest جنگل, rainforest جنگل بارانی, iceberg کوه یخ, cave سموچ.
- **Sahara** is صحرای کبیر; صحرای اعظم is also heard. **Mount Everest** کوه
  اورست. **Amazon** امازون.
- **Animals:** شیر (lion), زرافه, پاندا, کانگرو, پنگوین, خرس قطبی, لاما,
  بایسن ("a very large wild ox"), نهنگ آبی (blue whale), شتر, فیل, طوطی, عقاب.
  The kangaroo's pouch is خریطه شکم, its young چوچه.
- **Afghanistan:** هندوکش، نوشاخ، تونل سالنگ، بند امیر، بامیان، هرات، دریای
  آمو، دریای هلمند، هریرود، دریای کابل. Neighbours: پاکستان، ایران،
  ترکمنستان، ازبکستان، تاجکستان، چین. Province is ولایت; national park پارک ملی.
- **Map words:** نقشه, sign نشانی, square چهارکنج, triangle مثلث, circle
  دایره, brown نصواری, dotted line خط نقطه‌دار.
- **Day:** morning صبح, midday چاشت, evening شام, a day and night شبانه‌روز,
  spinning top چرخک, experiment آزمایش, lamp چراغ.
- **Travel:** lorry لاری, car موتر, aeroplane طیاره, train قطار (ریل is also
  Afghan usage), tram ترام, tunnel تونل, ship کشتی, port بندر, donkey خر.
- **Sledge** is یخمالک چوبی ("wooden slider"); Dari has no settled word.
  سورتمه is Iranian and was avoided. Sledging is یخمالک‌بازی.
- **Swim bag** is خریطه شنا; swimming for fun is آب‌بازی.
- **Ferry** is کشتی خورد چوبی; "engine" ماشین; "cable" سیم; "pushes" تیله می‌کند.
- **Bridge** پل; the Middle Bridge is پل میانه. **Town hall** تعمیر شاروالی.
  **University** پوهنتون. **Zoo** باغ وحش, **museums** موزیم‌ها.
- **Festival** is جشن; drums دهل, flutes توله, lanterns فانوس.
- **Food:** tandoor bread نان تنوری, maize جواری, rice برنج, cheese پنیر,
  yoghurt ماست, chocolate چاکلیت, watermelon تربوز, coat کرتی.
- **Games:** توپ‌بازی، ریسمان‌بازی، چشم‌پتکان (hide and seek)، سنگ‌بازی.
- **Countries and languages:** سویس، آلمان (جرمنی is also Afghan usage)، فرانسه،
  ایتالیا، اتریش، لیختن‌شتاین؛ آلمانی، فرانسوی، ایتالیایی، رومانش. Bern is برن,
  Basel بازل, the Alps الپ, the Rhine راین, Japan and others are not named.
- **Grüezi** is written گروتسی for the voice and shown in Latin letters on
  its story page (`show_en`).
- **Numbers** are written as words in speech: پنج هزار کیلومتر، هفت ساعت،
  شانزده بار، پنجاه و هفت کیلومتر، بیست دقیقه، هشت صد سال، بیست و چهار ساعت،
  هفت و نیم هزار متر، بیست و پنج کیلومتر، ساعت چهار صبح.
- "People who wish you well" is کسانی که خیر شما را می‌خواهند. "Goodbye" is
  خداحافظ, as in the rest of the app.

## The fact sheet

### Facts for the geography pack (use these; add no other facts)

The world
- The Earth is round like a ball. A globe is a small model of it. Most of it, about seven parts in ten, is covered by water.
- There are seven continents: Asia (the largest, where most people live), Africa, North America, South America, Antarctica (covered in ice, the coldest; nobody lives there for good), Europe, and Oceania with Australia (the smallest).
- There are five oceans: the Pacific (the largest), the Atlantic, the Indian, the Southern and the Arctic.
- The highest mountain in the world, Mount Everest, is in Asia. The largest hot desert, the Sahara, is in Africa.

Afghanistan
- Afghanistan is in Asia. It has no sea coast: it is surrounded by land. It has high mountains, the Hindu Kush. Its capital is Kabul.

From Afghanistan to Switzerland
- Switzerland is in Europe, far to the west: about 5,000 kilometres from Afghanistan. A fast aeroplane needs about seven hours; walking would take many months.
- The sun rises earlier in Afghanistan: when it is noon in Afghanistan, it is still morning in Switzerland.

Switzerland
- A small country in the middle of Europe. Afghanistan is about sixteen times larger. About nine million people live there.
- Like Afghanistan it has no sea coast, and like Afghanistan it has high mountains with snow: the Alps.
- The capital is Bern. Its neighbours are Germany, France, Italy, Austria and Liechtenstein.
- People speak four languages there: German, French, Italian and Romansh. Many children learn two or three languages at school.
- It has many lakes and rivers. In winter there is much snow; children go sledging.
- Cows graze on the mountain meadows in summer. From their milk people make cheese, and Swiss chocolate is made with milk.
- Trains go almost everywhere, through long tunnels under the mountains. The longest railway tunnel in the world is in Switzerland: 57 kilometres.
- Watches and clocks are made there.

Basel
- Basel is a city in the north of Switzerland, where three countries meet: Switzerland, France and Germany. A person can walk from one country into the next.
- A big river, the Rhine, flows through the middle of the city. It comes from the mountains (the Alps) and flows on through other countries to the sea, far in the north.
- Ships carry goods on the Rhine between Basel and the sea. So Switzerland, which has no sea coast, has a port in Basel.
- In summer many people swim and float down the Rhine through the city, with a watertight bag that keeps their clothes dry and helps them float.
- Small wooden ferry boats cross the river without an engine: the flow of the river pushes them across along a cable.
- Green trams run through the streets. On the market square stands an old red town hall. The city has a zoo and many museums.
- Basel has the oldest university of Switzerland, more than five hundred years old. Medicines are made in Basel.
- Once a year there is a big three-day festival with drums, flutes and large painted lanterns. It begins at four o'clock in the morning, in the dark.
- People in Basel speak German. To say hello they say "Grüezi".

The link
- The lessons and pictures on this device were made in Basel, in Switzerland, by people who wish the children well. (Say this once, simply, near the end. No names of people or organisations.)

Do not include: flags or coats of arms, churches or anything religious, politics, borders and neighbours of Afghanistan, wars, wealth comparisons ("rich country"), alcohol, pork, names of real people or companies, or anything that makes one country sound better than the other. The tone is: the world is big and varied; children far away live in mountains too, go to school, play, and are curious about you.

Map pictures that already exist for you to use (real map outlines, generated from map data):
- scene_map_world — all continents, oceans blue.
- scene_map_asia, scene_map_africa, scene_map_europe, scene_map_north_america, scene_map_south_america, scene_map_oceania, scene_map_antarctica — the world with that one continent highlighted.
- map_asia, map_africa, map_europe, map_north_america, map_south_america, map_oceania, map_antarctica — the shape of each continent alone (square pictures, good as answer choices).
- scene_map_world_afghanistan, scene_map_world_switzerland — the world with that country marked.
- scene_map_asia_afghanistan — Asia with Afghanistan highlighted. scene_map_europe_switzerland — Europe with Switzerland highlighted.
- map_afghanistan, map_switzerland — the shape of each country alone (square).
- scene_map_route — Afghanistan and Switzerland on one map with a dashed line between them.
- scene_map_switzerland — Switzerland with its neighbours, mountains marked in the south, a white dot for Bern and a larger yellow dot for Basel in the north.
- scene_map_basel — the corner where the three countries meet, each in its own colour, with the Rhine flowing through Basel.
- globe — a globe on a stand (square).

### Extension of the fact sheet for version 2

Plain, checkable facts added before the new rounds were written. Nothing in
the pack goes beyond the two lists. Two lines of the first sheet are changed
by this extension: the neighbours of Afghanistan may now be named once as a
plain list (see the open questions), and the highest and largest things are
used as written there.

Land, water and the oceans
- A continent is a very large piece of land. An island is land with water all around it. A lake is water with land all around it; the water of most lakes is fresh. Sea water is salty and cannot be drunk.
- The oceans are all joined to each other. The Pacific lies between Asia and America and is larger than all the land of the Earth together. The Atlantic lies between America on one side and Europe and Africa on the other. The Indian Ocean lies south of Asia, between Africa and Australia; it is the ocean nearest to Afghanistan. The Arctic Ocean lies around the North Pole and is covered with ice for most of the year. The Southern Ocean lies around Antarctica.
- By size the continents are: Asia, Africa, North America, South America, Antarctica, Europe, Oceania.
- The largest rainforest in the world, the Amazon, is in South America, where it is warm and rainy all year. The Sahara is in the north of Africa.
- A desert is a dry place where very little rain falls. A forest needs plenty of rain. An iceberg is a very large block of ice floating in a cold sea.
- On a high mountain it gets colder the higher one goes: fields and villages lie low, forest higher up, and on the top there is only rock and snow, which can stay all summer.

Animals
- Lions and giraffes live on the grasslands of Africa. Elephants live in warm parts of Africa and Asia; the elephant is the largest land animal. The panda, a black and white bear, lives only in Asia. Kangaroos live in Australia and carry their young in a pouch. Penguins are black and white birds that cannot fly and swim well; they live in the southern half of the world, many of them in Antarctica. Polar bears live in the ice around the North Pole; penguins and polar bears never meet. The llama comes from the mountains of South America and carries loads. The bison, a very large wild ox, lives on the plains of North America. Parrots live in warm forests.
- The blue whale lives in the oceans and is the largest animal in the world.
- The camel lives in deserts, can go many days without drinking, and stores fat in its hump.

The sun, day and night, hot and cold
- The Earth turns round itself once in twenty-four hours, towards the east. The side that faces the sun has day, the other side has night. The sun does not go out.
- So the sun is seen to rise in the east and set in the west. At midday it is highest and its light is strongest; in the morning and evening it is low, its light falls at a slant, and shadows are long.
- Near the equator, the line around the middle of the Earth, the sun stands high all year and it is hot. Near the poles the light always arrives at a slant, spread over a large area, and it is cold; even the sea freezes.

Directions and maps
- There are four directions: north, south, east, west. A person who stretches the right hand towards the sunrise faces north, with south behind and west at the left hand.
- The needle of a compass is a small magnet and points north.
- A map is a picture of a place seen from above, drawn small. On nearly all maps north is at the top, so east is on the right and west on the left. Water is drawn blue; on many maps high land is brown and forest green. Things near each other in the place are near each other on the map.

Afghanistan
- Afghanistan has six neighbouring countries: Pakistan, Iran, Turkmenistan, Uzbekistan, Tajikistan and China.
- The Hindu Kush runs from the north-east into the middle of the country. The highest mountain of Afghanistan is Noshaq, 7,492 metres, in the Hindu Kush in the north-east.
- The rivers are fed by the snow of the mountains. The Amu river is in the north. The Helmand is the longest river of the country, about 1,150 kilometres; it begins in the mountains west of Kabul and flows to the south-west. The Harirud flows west. The Kabul river flows through the city of Kabul.
- In the south-west there is sandy desert.
- The lakes of Band-e Amir lie in the mountains of Bamyan province; they are deep blue, and they are Afghanistan's first national park.
- The Salang tunnel takes the road under the Hindu Kush and joins Kabul with the north.
- Kabul is the largest city of the country.

The journey and the time
- Afghanistan lies east of Switzerland, so the sun reaches it earlier. Afghan time is three and a half hours ahead of Swiss time in winter and two and a half in summer: about three hours. When the sun rises in Kabul it is still night in Basel.
- A person on foot covers about twenty-five kilometres in a day, so five thousand kilometres are several months. An aeroplane flies straight over mountains and sea.
- North America lies west of Europe; its morning comes later still.

Children elsewhere
- People greet each other in their own language: "Salaam" in Afghanistan, "Grüezi" in Basel, "Jambo" in East Africa (Swahili), "Hola" in most of South America (Spanish).
- In East Asia people eat rice every day; it grows in flooded fields. In much of Africa and the Americas the daily food is made from maize. In Switzerland people eat bread with cheese.
- Children everywhere play with balls and skipping ropes, play hide and seek and games with stones.

Switzerland and Basel
- A train passes through the 57-kilometre tunnel in about twenty minutes. Roads over the high passes are long and winding and are closed by snow in winter.
- Swiss watches are known all over the world for keeping exact time.
- The Rhine is more than a thousand kilometres long. In Basel an old bridge, the Middle Bridge, joins the two sides of the city; there has been a bridge at that place for about eight hundred years. Ships pass under it.
- The swim bag is closed by rolling its top tightly; it holds air, so it floats.
- The festival begins in the dark so that the lanterns show.

Map pictures added for version 2 (generated by `tools/maps.py` from the same map data):
- scene_map_ocean_pacific, _atlantic, _indian, _arctic, _southern — the world with that one ocean in a darker blue.
- scene_map_hot_cold — the world with a red belt around the middle and blue caps at the poles.
- scene_map_afghanistan — Afghanistan alone highlighted, with white triangles for the Hindu Kush, blue lines for the Amu, the Helmand and the Harirud, small dune marks in the south-west and a yellow dot for Kabul. map_afghanistan_land — the same, alone and square.
- scene_map_rhine — the Rhine from the Alps through Basel (yellow dot) to the sea in the north.

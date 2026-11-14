# Throwaway generator for content/garden/{1,2}. The CSVs it writes are the source of truth.
import csv, json, re, sys
from pathlib import Path

OUT = Path("/home/user/Setara/setara/content/garden")
AGAIN = " یک بار دیگر فکر کن."

# ---------------------------------------------------------------- pictures
# name: (english gloss, Dari word, what to draw)
P = {}
def pic(name, en, fa, draw):
    assert name not in P, name
    P[name] = (en, fa, draw)

# handwashing steps
pic("hw_wet", "wet the hands", "دست را تر کردن", "Two child hands under running water poured from a jug; no soap yet.")
pic("hw_soap", "put soap on", "صابون زدن", "Two wet child hands holding a bar of soap, a little foam.")
pic("hw_palms", "rub the palms", "مالیدن کف دست‌ها", "Two soapy hands rubbing palm against palm, foam between them.")
pic("hw_backs", "rub the backs of the hands", "مالیدن پشت دست‌ها", "One soapy palm rubbing the back of the other hand.")
pic("hw_fingers", "rub between the fingers", "مالیدن بین انگشت‌ها", "Two soapy hands with fingers interlaced, foam between the fingers.")
pic("hw_rinse", "rinse", "آب کشیدن", "Two hands under clean pouring water, the foam washing away.")
pic("hw_dry", "dry", "خشک کردن", "Two clean hands being dried with a clean cloth towel.")
pic("wash_hands", "washing hands with soap", "دست شستن با صابون", "Two hands with soap foam under water from a jug, a bar of soap beside them. The general 'wash your hands' picture.")
pic("clean_hands", "clean hands", "دست‌های پاک", "Two open clean child hands with small sparkle marks.")
pic("dirty_hands", "dirty hands", "دست‌های چتل", "Two open child hands covered with brown mud and dust.")
# teeth
pic("tooth", "tooth", "دندان", "One big white tooth.")
pic("tooth_clean", "healthy tooth", "دندان سالم", "One white, shining tooth with a small sparkle.")
pic("tooth_decayed", "decayed tooth", "دندان خراب", "One tooth with a dark brown hole in it, looking dull.")
pic("toothbrush", "toothbrush", "برس دندان", "A simple toothbrush.")
pic("toothpaste", "toothpaste", "کریم دندان", "A plain tube of toothpaste with no brand or text.")
pic("tb_paste", "put toothpaste on the brush", "کریم را روی برس ماندن", "A toothbrush with a small amount of toothpaste being squeezed onto it from a tube.")
pic("tb_brush", "brush the teeth", "برس کردن دندان", "A child's face, smiling mouth open, brushing the teeth with a toothbrush. Use a girl with headscarf.")
pic("tb_spit", "spit out the foam", "تف کردن کف", "A child bending over a basin, spitting out toothpaste foam. Use a boy.")
pic("tb_wash_brush", "wash the toothbrush", "شستن برس", "A toothbrush held under pouring clean water.")
# daily routine
pic("sleep", "sleeping", "خواب", "A child asleep on a mattress on the floor under a blanket, head on a pillow, eyes closed. Use a boy.")
pic("wake_up", "waking up", "بیدار شدن", "A child sitting up on the mattress, stretching arms, morning sun in the window. Use a girl with headscarf.")
pic("wash_face", "washing hands and face", "دست و روی شستن", "A child washing the face with water from a jug over a basin. Use a boy.")
pic("dinner", "evening meal", "نان شب", "A family meal on a cloth on the floor: bread, a bowl of food, an oil lamp, night in the window. No people needed.")
pic("breakfast", "breakfast", "نان صبح", "Breakfast on a cloth: flat bread, a cup of milk, an egg, morning light.")
pic("play", "playing", "بازی", "Two children running after a ball in a yard. One girl with headscarf, one boy.")
pic("school", "school", "مکتب", "A simple village school building with an open door.")
pic("eating", "eating", "نان خوردن", "A child sitting at a cloth on the floor with bread and a bowl, about to eat. Use a girl with headscarf.")
pic("petting_sheep", "touching an animal", "دست زدن به حیوان", "A child stroking a sheep with one hand. Use a boy.")
pic("sneeze", "sneezing", "عطسه", "A child sneezing into a cloth held at the nose. Use a girl with headscarf.")
pic("reading", "reading a book", "کتاب خواندن", "A child sitting and reading an open book. Use a boy.")
pic("night", "night", "شب", "A dark blue sky with a moon and stars over a village house.")
# body
pic("hand", "hand", "دست", "One open child hand.")
pic("foot", "foot", "پا", "One child foot, seen from the side.")
pic("leg", "leg", "لنگ", "A child's leg in loose trousers from hip to foot, the whole leg highlighted.")
pic("arm", "arm", "بازو", "A child's arm in a long sleeve from shoulder to wrist, the whole arm highlighted.")
pic("finger", "finger", "انگشت", "A hand with one finger pointing up, that finger highlighted.")
pic("nail", "fingernail", "ناخن", "Close view of a fingertip with the nail highlighted.")
pic("knee", "knee", "زانو", "A bent leg in trousers with the knee highlighted.")
pic("tummy", "tummy", "شکم", "A fully dressed child with both hands resting on the tummy. Use a boy; clothes cover the body.")
pic("head", "head", "سر", "A child's head seen from the front. Use a boy with a cap.")
pic("face", "face", "روی", "A smiling child's face. Use a girl with headscarf.")
pic("hair", "hair", "موی", "A boy's head from the side with short dark hair, the hair highlighted.")
pic("eye", "eye", "چشم", "One eye with eyebrow.")
pic("ear", "ear", "گوش", "One ear.")
pic("nose", "nose", "بینی", "One nose, seen from the front.")
pic("mouth", "mouth", "دهن", "One smiling mouth, lips closed.")
# household things
pic("soap", "soap", "صابون", "A bar of soap with a few bubbles.")
pic("towel", "towel", "دستمال", "A folded clean cloth towel.")
pic("water_jug", "water jug", "جک آب", "A plastic or metal jug with a handle, full of water.")
pic("water", "water", "آب", "A clear glass of clean water.")
pic("pillow", "pillow", "بالشت", "A pillow.")
pic("blanket", "blanket", "کمپل", "A folded warm blanket.")
pic("mattress", "mattress", "توشک", "A floor mattress as used in Afghan homes.")
pic("clean_clothes", "clean clothes", "کالای شسته", "Clean clothes hanging on a line in the sun.")
pic("plate_clean", "clean plate", "بشقاب پاک", "A clean shining empty plate.")
pic("plate_dirty", "dirty plate", "بشقاب چتل", "A plate with food remains and two flies on it.")
pic("garbage", "rubbish", "کثافات", "A small heap of rubbish: peels, a plastic bag, a tin, flies above.")
pic("comb", "comb", "شانه", "A comb.")
pic("spoon", "spoon", "قاشق", "A spoon.")
pic("book", "book", "کتاب", "A closed book.")
pic("ball", "ball", "توپ", "A ball.")
pic("table", "table", "میز", "A small table.")
pic("plate", "plate", "بشقاب", "An empty plate.")
pic("stone", "stone", "سنگ", "A grey stone.")
pic("shoe", "shoe", "بوت", "One shoe.")
pic("house", "house", "خانه", "A mud-brick village house with a flat roof and a wooden door.")
pic("umbrella", "umbrella", "چتری", "An open umbrella.")
pic("sandals", "sandals", "چپلک", "A pair of plastic sandals.")
pic("coat", "warm coat", "بالاپوش", "A thick warm winter coat.")
pic("parents", "mother and father", "مادر و پدر", "A mother (headscarf, long dress) and a father (cap, long shirt) standing together, friendly.")
pic("mother", "mother", "مادر", "A friendly mother in headscarf and long dress.")
pic("clinic", "clinic", "کلینیک", "A small health-post building with an open door and a health worker (a woman in headscarf and white coat) at the door. No cross, crescent or logo.")
# food
pic("bread", "bread", "نان", "A flat Afghan naan.")
pic("rice", "rice", "برنج", "A plate of cooked white rice.")
pic("potato", "potato", "کچالو", "Two potatoes.")
pic("corn", "maize", "جواری", "A cob of maize.")
pic("egg", "egg", "تخم مرغ", "One egg.")
pic("milk", "milk", "شیر", "A cup of white milk.")
pic("yoghurt", "yoghurt", "ماست", "A bowl of white yoghurt.")
pic("beans", "beans", "لوبیا", "A bowl of red beans.")
pic("lentils", "lentils", "دال", "A bowl of cooked yellow lentils.")
pic("chickpeas", "chickpeas", "نخود", "A bowl of chickpeas.")
pic("meat", "meat", "گوشت", "A piece of cooked meat on a plate.")
pic("apple", "apple", "سیب", "A red apple.")
pic("carrot", "carrot", "زردک", "A carrot with green leaves.")
pic("tomato", "tomato", "بادنجان رومی", "A red tomato.")
pic("spinach", "spinach", "پالک", "A bunch of green spinach leaves.")
pic("pumpkin", "pumpkin", "کدو", "A pumpkin.")
pic("grape", "grapes", "انگور", "A bunch of grapes.")
pic("apricot", "apricot", "زردآلو", "Two orange apricots.")
pic("pomegranate", "pomegranate", "انار", "A red pomegranate, one cut open.")
pic("watermelon", "watermelon", "تربوز", "A watermelon with one slice cut.")
pic("candy", "sweets", "شیرینی", "A few wrapped sweets, no brand.")
pic("soda", "fizzy sweet drink", "نوشابه", "A bottle of dark fizzy drink with bubbles, no brand or text.")
pic("sugar", "sugar", "بوره", "A small bowl of white sugar with a spoon.")
pic("food_bowl", "bowl of soft food", "خوراک نرم", "A bowl of soft food (rice porridge or mashed potato) with a small spoon.")
pic("bowl_empty", "empty bowl", "کاسه خالی", "An empty bowl pushed aside.")
pic("food_covered", "covered food", "خوراک سرپوشیده", "A dish of food covered with a lid or a clean cloth.")
pic("food_uncovered", "uncovered food with flies", "خوراک سرباز", "A dish of food left open with flies on it.")
# animals
pic("sheep", "sheep", "گوسفند", "A sheep.")
pic("lamb", "lamb", "بره", "A small lamb.")
pic("cow", "cow", "گاو", "A cow.")
pic("calf", "calf", "گوساله", "A small calf.")
pic("goat", "goat", "بز", "A goat.")
pic("donkey", "donkey", "خر", "A donkey.")
pic("horse", "horse", "اسپ", "A horse.")
pic("hen", "hen", "مرغ", "A hen.")
pic("rooster", "rooster", "خروس", "A rooster crowing.")
pic("chick", "chick", "چوچه مرغ", "A yellow chick.")
pic("cat", "cat", "پشک", "A cat.")
pic("kitten", "kitten", "چوچه پشک", "A small kitten.")
pic("dog", "dog", "سگ", "A village guard dog sitting outside.")
pic("fish", "fish", "ماهی", "A fish.")
pic("pigeon", "pigeon", "کبوتر", "A pigeon flying.")
pic("sparrow", "sparrow", "گنجشک", "A sparrow on a twig.")
pic("eagle", "eagle", "عقاب", "An eagle.")
pic("wolf", "wolf", "گرگ", "A wolf.")
pic("fox", "fox", "روباه", "A fox.")
pic("snake", "snake", "مار", "A snake.")
pic("bee", "bee", "زنبور عسل", "A honey bee.")
pic("butterfly", "butterfly", "پروانه", "A butterfly.")
pic("ant", "ant", "مورچه", "An ant.")
pic("fly", "fly", "مگس", "A housefly, large and clear.")
# plants, seasons, sky
pic("tree", "tree", "درخت", "A green leafy tree.")
pic("flower", "flower", "گل", "A red flower with green leaves.")
pic("wheat", "wheat", "گندم", "Golden ears of wheat.")
pic("root", "root", "ریشه", "The lower part of a plant with its roots spreading in brown soil, roots highlighted.")
pic("leaf", "leaf", "برگ", "One green leaf.")
pic("sprout", "sprout", "سبزه نو", "A tiny green seedling with two leaves coming out of the soil.")
pic("blossom", "tree in blossom", "شکوفه", "A tree branch covered in pink-white blossom.")
pic("leaf_yellow", "falling yellow leaves", "برگ زرد", "Yellow and orange leaves falling from a branch.")
pic("spring", "spring", "بهار", "A blossoming tree, green grass and light rain. No people.")
pic("summer", "summer", "تابستان", "A strong sun over a golden wheat field. No people.")
pic("autumn", "autumn", "خزان", "A tree with yellow leaves falling. No people.")
pic("winter", "winter", "زمستان", "A bare tree and a house under falling snow. No people.")
pic("sun", "sun", "آفتاب", "A bright yellow sun.")
pic("moon", "moon", "مهتاب", "A plain round full moon in a dark sky.")
pic("star", "star", "ستاره", "A few small stars in a dark sky.")
pic("cloud", "cloud", "ابر", "A grey rain cloud.")
pic("snow", "snow", "برف", "Snowflakes falling on white ground.")
pic("ice", "ice", "یخ", "A block of ice and icicles.")
pic("steam", "steam", "بخار", "A pot with white steam rising from it.")
pic("fire", "fire", "آتش", "A small wood fire.")
pic("sand", "sand", "ریگ", "A heap of sand.")
pic("mountain", "mountain", "کوه", "A high mountain with snow on top.")
pic("river", "river", "دریا", "A wide river running through a valley.")
pic("soil", "soil", "خاک", "A heap of dark brown soil with a hand spade mark.")
# water
pic("water_boiled", "boiled water", "آب جوش‌داده", "A clean kettle or pot with a lid and a glass of clear water beside it; a little steam shows it was boiled.")
pic("water_boiling", "boiling water", "آب در حال جوش", "A pot of water on a fire with big bubbles and steam.")
pic("water_covered", "covered water container", "ظرف آب سرپوش‌دار", "A clean water container with a tight lid and a clean ladle hanging beside it.")
pic("water_bucket", "bucket of fetched water", "سطل آب", "A bucket full of water just carried from the well.")
pic("water_bucket_open", "uncovered bucket", "سطل سرباز", "An open bucket of water standing on the ground with dust and flies above it.")
pic("water_cloudy", "muddy water", "آب گل‌آلود", "A bucket of brownish cloudy water.")
pic("water_filter_cloth", "filtering water through a clean cloth", "صاف کردن آب با تکه", "Water being poured from a bucket through a clean white cloth stretched over a pot. Hands only.")
pic("water_tap", "tap", "نل آب", "A water tap with clean water running.")
pic("water_pump", "hand pump", "بمبه آب", "A village hand pump on a concrete base with clean water coming out.")
pic("water_puddle", "puddle", "آب ایستاده", "A muddy brown puddle on the ground.")
pic("water_stream", "open stream", "آب جوی", "A small open irrigation channel with water, grass on the banks.")
pic("water_pond", "pond", "آب حوض", "A still green pond with leaves floating.")
pic("water_ladle", "taking water with a clean ladle", "آب گرفتن با چمچه", "A hand taking water out of a covered container with a long-handled clean ladle.")
pic("water_cup_dirty", "dirty cup", "گیلاس چتل", "A cup with mud marks and a fly on its rim.")
pic("water_hand_dip", "dipping a hand into the water pot", "دست در آب زدن", "A hand with a cup dipped deep inside the water container, fingers in the water.")
pic("water_animal", "animal drinking from the family water", "حیوان از ظرف آب می‌نوشد", "A hen and a goat drinking from an open household water bucket.")
pic("well_covered", "covered well", "چاه سرپوشیده", "A well with a raised wall and a cover on top, clean ground around it.")
pic("well_open", "open well", "چاه سرباز", "An open well at ground level with no cover, leaves and dust falling in.")
pic("well", "well", "چاه", "A village well with a rope and bucket.")
pic("latrine_far", "latrine far from the well", "تشناب دور از چاه", "A well in the front and a small latrine hut far away in the background.")
pic("latrine_near_well", "latrine next to the well", "تشناب نزدیک چاه", "A small latrine hut standing right beside a well.")
pic("bucket_clean", "clean bucket", "سطل پاک", "A clean bucket hanging on a hook, off the ground.")
pic("bucket_dirty", "dirty bucket", "سطل چتل", "A muddy bucket and rope lying on the dirty ground.")
pic("waste_pit", "rubbish pit", "چقوری کثافات", "A dug pit with rubbish in it and a board cover beside it, away from houses.")
pic("garbage_water", "rubbish in the stream", "کثافات در جوی", "Plastic bags and tins floating in a stream.")
pic("animals_water", "animals standing in the water", "حیوان در آب", "Cows standing in a stream.")
# latrine
pic("latrine", "latrine", "تشناب", "A small mud-brick latrine hut with a closed wooden door, seen from outside. No person.")
pic("latrine_cover", "cover on the latrine hole", "سرپوش تشناب", "A latrine floor slab seen from above with a wooden lid closing the hole. No person.")
pic("latrine_open", "uncovered latrine hole", "تشناب سرباز", "A latrine floor slab with the hole open and flies above. No person.")
pic("latrine_clean", "clean latrine", "تشناب پاک", "A tidy latrine hut with a door, a broom and a water jug with soap outside.")
pic("latrine_dirty", "dirty latrine", "تشناب چتل", "A latrine hut with a broken door, flies and dirt around. No person.")
pic("field", "open field", "دشت", "An open field with a few bushes. No person.")
pic("street", "village lane", "کوچه", "A village lane between mud walls. No person.")
pic("broom", "broom", "جاروب", "A hand broom.")
pic("germ", "germs", "میکروب", "A few small round green germs with tiny spikes, seen as through a magnifying glass.")
# smoke
pic("window", "open window", "کلکین", "An open window in a mud wall.")
pic("door", "door", "دروازه", "An open wooden door.")
pic("chimney", "chimney", "دودکش", "A stove pipe going out through a roof with smoke leaving outside.")
pic("stove", "cooking fire", "دیگدان", "A cooking pot on a simple fireplace with smoke.")
pic("stove_chimney", "stove with a chimney", "دیگدان دودکش‌دار", "A closed clay stove with a pot on it and a pipe taking the smoke out through the wall.")
pic("stove_open", "open fire indoors", "آتش سرباز در خانه", "An open three-stone fire inside a room, the room full of grey smoke.")
pic("kitchen_smoky", "smoky kitchen", "آشپزخانه پر دود", "A closed room with a cooking fire, thick grey smoke filling it, window shut.")
pic("yard", "yard, fresh air", "حویلی", "An open yard with a tree and blue sky.")
pic("wood_dry", "dry firewood", "هیزم خشک", "A bundle of dry split firewood.")
pic("wood_wet", "wet firewood", "هیزم تر", "Dark wet branches with drops of water on them.")
pic("charcoal", "charcoal", "زغال", "A small heap of black charcoal.")
pic("twigs", "twigs", "خاشه", "A bundle of thin dry twigs.")
pic("plastic_bag", "plastic bag", "خریطه پلاستیکی", "A crumpled plastic bag.")
# waste and trees
pic("peel", "fruit peel", "پوست میوه", "Apple and melon peels.")
pic("bottle", "bottle", "بوتل", "An empty plastic bottle, no label.")
pic("can", "tin can", "قطی", "An empty tin can.")
pic("bottle_reuse", "bottle used again", "بوتل دوباره کار گرفته شده", "A plastic bottle cut and used as a pot for a small plant.")
pic("garbage_street", "rubbish in the lane", "کثافات در کوچه", "Rubbish scattered in a village lane.")
pic("plastic_fire", "burning plastic", "سوختاندن پلاستیک", "Plastic bags burning with thick black smoke.")
pic("yard_clean", "clean yard", "حویلی پاک", "A swept clean yard with a tree and a broom against the wall.")
pic("yard_dirty", "dirty yard", "حویلی چتل", "A yard with rubbish lying around and flies.")
pic("nest", "nest", "آشیانه", "A bird's nest with eggs on a tree branch.")
pic("sapling", "sapling", "نهال", "A small young tree just planted, with a ring of soil around it.")
pic("axe", "axe", "تبر", "An axe.")
pic("fence", "fence", "کتاره", "A small fence of sticks around a young tree.")
pic("shovel", "shovel", "بیل", "A shovel.")
pic("bucket", "bucket", "سطل", "An empty bucket.")
# ORS
pic("ors_packet", "ORS packet", "پاکت او آر اس", "A small plain sachet with a simple drop symbol, no brand or text.")
pic("ors_water", "clean water measured into a clean container", "آب پاک در ظرف پاک", "A clean jug filled with clear water to a marked line, an ORS sachet lying beside it.")
pic("ors_pour", "pour the whole packet in", "تمام پاکت را در آب انداختن", "A hand emptying the whole sachet of powder into the jug of water.")
pic("ors_stir", "stir until dissolved", "شور دادن", "A hand stirring the jug with a clean spoon.")
pic("ors_sip", "give small sips", "کم‌کم نوشاندن", "A mother (headscarf) giving a small child a sip from a spoon with a small cup in her other hand.")
# scenes
def scene(name, draw):
    pic(name, "", "", draw)
scene("scene_boy_playing", "A boy of about 8 (cap, long shirt, trousers) playing with a ball in a dusty yard; his hands are dusty.")
scene("scene_mother_calls", "A mother (headscarf, long dress) at the house door calling; behind her a cloth with bread laid on the floor.")
scene("scene_boy_dirty_hands", "The boy standing between a water jug with soap on one side and the bread on the cloth on the other, looking at his dusty hands.")
scene("scene_boy_tummy_ache", "The boy sitting with both hands on his tummy, looking unwell but not frightening; mother comforting him.")
scene("scene_boy_washing", "The boy washing his hands with soap and foam under water poured from a jug.")
scene("scene_family_eating", "The family (mother, father, the boy, a small sister with headscarf) sitting around a cloth on the floor eating bread.")
scene("scene_boy_latrine", "The boy outside the closed door of a latrine hut; a jug and soap stand near; two friends (a boy and a girl with headscarf) wave with a ball in the distance.")
scene("scene_germs_hands", "Close view of two hands with small green germs on them, as through a magnifying glass. Gentle, not scary.")
scene("scene_boy_friends", "The boy with clean hands playing ball with a boy and a girl (headscarf).")
scene("scene_boy_night", "Evening in the room: the boy yawning beside his mattress; a toothbrush and cup on a shelf; moon in the window.")
scene("scene_boy_toothache", "The boy holding his cheek with a sore tooth, mother beside him. Gentle.")
scene("scene_boy_brushing", "The boy brushing his teeth over a basin.")
scene("scene_boy_sleeping", "The boy asleep on his mattress under a blanket, moon and stars in the window.")
scene("scene_girl_walking_home", "A girl of about 9 (headscarf, long dress, school bag) walking home on a village path under a hot sun.")
scene("scene_girl_stream", "The girl standing beside a small open stream that looks clear; upstream in the distance a cow stands in the water.")
scene("scene_girl_tummy_ache", "The girl sitting with her hands on her tummy, looking unwell, her mother comforting her. Gentle.")
scene("scene_girl_mother_pot", "At home: the girl looks into an empty pot; her mother (headscarf) sets down a bucket of slightly brown water.")
scene("scene_filter_cloth", "Mother pouring water from the bucket through a clean white cloth stretched over a pot; the girl holds the cloth.")
scene("scene_filtered_water", "A pot of clear-looking water; the muddy cloth beside it; the girl and mother looking at it.")
scene("scene_germs_water", "A glass of clear-looking water with a magnifying glass showing small green germs in it. Gentle.")
scene("scene_boiling", "A pot of water boiling on the fire with big bubbles; mother beside it, the girl standing well back.")
scene("scene_two_pots", "Side by side: a clean container with a lid and ladle, and an open bucket.")
scene("scene_flies_bucket", "The open bucket of water with dust and flies falling in.")
scene("scene_girl_drinking", "The girl pouring water with a ladle into a clean glass, smiling.")
scene("scene_girl_teaching_brother", "The girl showing her small brother the covered water container and ladle.")
scene("scene_baby_sick", "A girl (headscarf) and a boy of school age kneeling beside their two-year-old brother, who lies tired on a mattress, fully dressed.")
scene("scene_mother_ors_packet", "Mother (headscarf) kneeling by the small child, holding up a small plain sachet; the two older children listen.")
scene("scene_ors_mixing", "Mother stirring a clean jug of water after emptying the sachet into it; soap and a wash jug behind her.")
scene("scene_ors_sips", "Mother giving the small child a spoonful from a cup; the older girl holds the cup, the older boy sits near.")
scene("scene_baby_weak", "The small child lying weak and tired, an empty bowl beside him. Gentle.")
scene("scene_mother_feeding", "Mother holding the small child on her lap and feeding him soft food with a small spoon; all fully dressed.")
scene("scene_baby_danger", "Evening: the small child very sleepy with sunken eyes, turning away from the cup; the older sister looks worried and calls her mother.")
scene("scene_clinic", "Father carrying the small child, mother beside him, at the door of a small clinic where a woman health worker (headscarf, white coat) welcomes them. No logo or symbol.")

# ---------------------------------------------------------------- helpers
used = {1: set(), 2: set()}
def note(level, cell):
    for s in cell.split("|"):
        s = s.strip()
        if not s or s[:2] in ("t:", "f:") or s.startswith("lf:"):
            continue
        m = re.match(r"^p:([a-z0-9_]+)\*\d+$", s)
        used[level].add(m.group(1) if m else s)

def write(level, name, header, rows, piccols):
    for r in rows:
        assert len(r) == len(header), (name, r)
        for c in piccols:
            note(level, r[header.index(c)])
    d = OUT / str(level)
    d.mkdir(parents=True, exist_ok=True)
    with (d / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)

BH = ["round", "intro_fa", "say_en", "say_fa", "tiles", "extra", "rtl", "done_en", "done_fa", "help_fa"]
def builder(level, name, rounds):
    rows = []
    for rnd, intro, items in rounds:
        for i, (say, tiles, extra, done, help_) in enumerate(items):
            assert 2 <= len(tiles.split("|")) + (len(extra.split("|")) if extra else 0) <= 8
            rows.append([rnd, intro if i == 0 else "", "", say, tiles, extra, "yes", "", done, help_])
    write(level, name, BH, rows, ["tiles", "extra"])

SH = ["round", "intro_fa", "thing", "say_en", "say_fa", "basket", "basket_say_fa"]
def sorter(level, name, rounds):
    rows = []
    for rnd, intro, baskets, items in rounds:
        assert 6 <= len(items) <= 10, (name, rnd)
        seen = set()
        for i, (thing, say, b) in enumerate(items):
            bt, bsay = baskets[b]
            rows.append([rnd, intro if i == 0 else "", thing, "", say, bt, bsay if b not in seen else ""])
            seen.add(b)
        assert seen == set(baskets), (name, rnd)
    write(level, name, SH, rows, ["thing", "basket"])

LH = ["round", "intro_fa", "say_en", "say_fa", "show", "answer", "distractors", "help_fa"]
def picker(level, name, rounds):
    rows = []
    for rnd, intro, items in rounds:
        assert 6 <= len(items) <= 10, (name, rnd)
        for i, (say, answer, distractors, help_) in enumerate(items):
            if distractors:
                ds = distractors.split("|")
                assert len(ds) == 3 and answer not in ds and len(set(ds)) == 3, (name, say)
            rows.append([rnd, intro if i == 0 else "", "", say, "", answer, distractors, help_])
    write(level, name, LH, rows, ["answer", "distractors"])

TH = ["round", "picture", "say_en", "say_fa", "show_fa", "choices", "right", "wrong_say_fa", "wrong_picture"]
def story(level, name, pages):
    assert 8 <= len(pages) <= 10
    rows = []
    for p in pages:
        if len(p) == 2:
            picture, say = p
            one = say.count(".") + say.count("!") + say.count("؟") <= 1
            rows.append(["01", picture, "", say, say if one else "", "", "", "", ""])
        else:
            picture, say, choices, right, wrong, wrongpic = p
            rows.append(["01", picture, "", say, "", choices, right, wrong + AGAIN, wrongpic])
    assert sum(1 for r in rows if r[5]) == 3
    write(level, name, TH, rows, ["picture", "choices", "right", "wrong_picture"])

# =================================================================== LEVEL 1
builder(1, "clean_hands.csv", [
 ("01", "دست شستن را یاد می‌گیریم. گوش کن و تصویرها را به ترتیب درست بمان.", [
  ("اول دست‌ها را تر کن. بعد صابون بزن. بعد کف دست‌ها را به هم بمال.", "hw_wet|hw_soap|hw_palms", "",
   "آفرین! اول آب، بعد صابون، بعد مالیدن.",
   "اول دست‌ها را با آب تر می‌کنیم. بعد صابون می‌زنیم. بعد کف دست‌ها را به هم می‌مالیم."),
  ("حالا خوب بمال: کف دست‌ها، پشت دست‌ها، و بین انگشت‌ها.", "hw_palms|hw_backs|hw_fingers", "",
   "آفرین! صابون به همه جای دست رسید.",
   "صابون باید به همه جای دست برسد: کف دست، پشت دست، بین انگشت‌ها و زیر ناخن‌ها."),
  ("آخر کار: بین انگشت‌ها را بمال، با آب پاک آب بکش، و دست‌ها را خشک کن.", "hw_fingers|hw_rinse|hw_dry", "",
   "آفرین! دست‌هایت پاک شد.",
   "بعد از مالیدن، صابون را با آب پاک می‌شوییم. بعد دست‌ها را با دستمال پاک خشک می‌کنیم، یا می‌مانیم که در هوا خشک شود."),
 ]),
 ("02", "حالا همه قدم‌های دست شستن را از اول تا آخر به ترتیب بمان.", [
  ("چهار قدم: تر کن، صابون بزن، بمال، آب بکش.", "hw_wet|hw_soap|hw_palms|hw_rinse", "",
   "آفرین! همین طور دست می‌شوییم.",
   "اول آب، بعد صابون، بعد مالیدن، و در آخر آب کشیدن."),
  ("پنج قدم: تر کن، صابون بزن، بمال، آب بکش، خشک کن.", "hw_wet|hw_soap|hw_palms|hw_rinse|hw_dry", "",
   "آفرین! دست‌های پاک و خشک.",
   "دست‌ها را با دستمال پاک خشک می‌کنیم، یا می‌مانیم که در هوا خشک شود."),
  ("حالا همه هفت قدم. دست شستن را از اول تا آخر جور کن.", "hw_wet|hw_soap|hw_palms|hw_backs|hw_fingers|hw_rinse|hw_dry", "",
   "آفرین! وقتی دست‌ها را با صابون می‌مالی، آهسته تا بیست بشمار. حالا دست‌هایت پاکِ پاک است.",
   "تر کن. صابون بزن. کف دست‌ها، پشت دست‌ها و بین انگشت‌ها را بمال. آب بکش. خشک کن."),
 ]),
 ("03", "حالا نوبت دندان‌ها است. قدم‌های برس کردن دندان را به ترتیب بمان.", [
  ("کمی کریم دندان را روی برس بمان. دندان‌ها را برس کن. کف را تف کن.", "tb_paste|tb_brush|tb_spit", "",
   "آفرین! دندان‌هایت پاک شد.",
   "کمی کریم دندان بس است. همه دندان‌ها را نرم‌نرم برس می‌کنیم: پیش، پشت و روی دندان‌ها."),
  ("کریم را روی برس بمان، دندان‌ها را برس کن، کف را تف کن، و برس را بشوی.", "tb_paste|tb_brush|tb_spit|tb_wash_brush", "",
   "آفرین! برس پاک برای فردا تیار است.",
   "هر کس برس دندان خودش را دارد. بعد از کار، برس را با آب پاک می‌شوییم."),
  ("شب شده است. نان شب را خوردی. بعد چه می‌کنی؟ به ترتیب بمان. یک تصویر زیادی است.", "dinner|tb_brush|sleep", "candy",
   "آفرین! بعد از نان شب دندان را برس می‌کنیم و می‌خوابیم. بعد از برس، دیگر شیرینی نمی‌خوریم.",
   "دندان‌ها را روز دو بار برس می‌کنیم: صبح، و شب پیش از خواب."),
 ]),
 ("04", "وقت خواب است. کارها را به ترتیب درست بمان.", [
  ("پیش از خواب: دست و رویت را بشوی، دندانت را برس کن، و بخواب.", "wash_face|tb_brush|sleep", "",
   "آفرین! پاک و آرام می‌خوابیم.",
   "پیش از خواب دست و روی را می‌شوییم و دندان را برس می‌کنیم."),
  ("از بازی تا خواب: بازی، نان شب، برس دندان، خواب.", "play|dinner|tb_brush|sleep", "",
   "آفرین! اطفال به خواب زیاد ضرورت دارند. شب وقت بخواب.",
   "روز بازی می‌کنیم. شام نان می‌خوریم. بعد دندان را برس می‌کنیم و وقت می‌خوابیم."),
  ("صبح شد! بیدار شو، دست و رویت را بشوی، نان صبح را بخور، و به مکتب برو.", "wake_up|wash_face|breakfast|school", "",
   "آفرین! کسی که شب خوب خوابیده، صبح تازه و خوشحال است.",
   "خواب خوب به ما کمک می‌کند که کلان شویم، خوب یاد بگیریم و خوش باشیم."),
 ]),
])

W = {"w": ("f:بشوی", "اول دست‌ها را با صابون بشوی"), "n": ("f:لازم نیست", "حالا دست شستن لازم نیست")}
CD = {"c": ("f:پاک", "پاک"), "d": ("f:چتل", "چتل")}
GB = {"g": ("f:خوب", "برای دندان خوب است"), "b": ("f:بد", "دندان را خراب می‌کند")}
HTS = {"h": ("f:دست", "برای دست شستن"), "t": ("f:دندان", "برای دندان"), "s": ("f:خواب", "برای خواب")}
sorter(1, "safe_water.csv", [
 ("01", "چه وقت باید دست‌ها را بشوییم؟ هر تصویر را در سبد درست بینداز.", W, [
  ("eating", "پیش از نان خوردن", "w"),
  ("latrine", "بعد از تشناب", "w"),
  ("reading", "کتاب می‌خوانم", "n"),
  ("dirty_hands", "بعد از بازی در خاک", "w"),
  ("clean_hands", "همین حالا دست‌هایم را با صابون شسته‌ام", "n"),
  ("petting_sheep", "بعد از دست زدن به حیوان", "w"),
  ("sleep", "خواب هستم", "n"),
  ("sneeze", "بعد از عطسه و پاک کردن بینی", "w"),
 ]),
 ("02", "کدام پاک است و کدام چتل؟ هر تصویر را در سبد درست بینداز.", CD, [
  ("soap", "صابون", "c"),
  ("dirty_hands", "دست‌های خاک‌پر", "d"),
  ("water", "آب پاک در گیلاس", "c"),
  ("plate_dirty", "بشقاب ناشسته با مگس", "d"),
  ("clean_clothes", "کالای شسته", "c"),
  ("garbage", "کثافات", "d"),
  ("plate_clean", "بشقاب شسته", "c"),
  ("water_puddle", "آب ایستاده و گل‌آلود", "d"),
 ]),
 ("03", "کدام برای دندان خوب است و کدام دندان را خراب می‌کند؟", GB, [
  ("toothbrush", "برس دندان", "g"),
  ("candy", "شیرینی", "b"),
  ("milk", "شیر", "g"),
  ("water", "آب", "g"),
  ("soda", "نوشابه شیرین", "b"),
  ("apple", "سیب", "g"),
  ("sugar", "بوره زیاد", "b"),
  ("carrot", "زردک", "g"),
 ]),
 ("04", "هر چیز برای چه کار است؟ برای دست، برای دندان، یا برای خواب؟", HTS, [
  ("soap", "صابون", "h"),
  ("toothbrush", "برس دندان", "t"),
  ("pillow", "بالشت", "s"),
  ("water_jug", "جک آب", "h"),
  ("blanket", "کمپل", "s"),
  ("toothpaste", "کریم دندان", "t"),
  ("towel", "دستمال پاک", "h"),
  ("mattress", "توشک", "s"),
 ]),
])

story(1, "hygiene_story.csv", [
 ("scene_boy_playing", "امید در حویلی توپ‌بازی می‌کند. دست‌هایش خاک‌پر شده است."),
 ("scene_mother_calls", "مادرش صدا می‌کند: امید جان، بیا، نان تیار است!"),
 ("scene_boy_dirty_hands", "امید گشنه است. اول چه کند؟ دست‌هایش را با صابون بشوید، یا همین طور نان بخورد؟",
  "wash_hands|bread", "wash_hands",
  "دست‌های امید چتل است. چتلی با نان به شکمش می‌رود و شکمش درد می‌گیرد.", "scene_boy_tummy_ache"),
 ("scene_boy_washing", "امید دست‌هایش را تر می‌کند و صابون می‌زند. کف دست، پشت دست و بین انگشت‌ها را می‌مالد و آهسته تا بیست می‌شمارد. بعد آب می‌کشد."),
 ("scene_family_eating", "حالا دست‌هایش پاک است. امید با فامیل خود نان می‌خورد. نان بسیار مزه‌دار است!"),
 ("scene_boy_latrine", "بعد از نان، امید به تشناب می‌رود. دوستانش صدا می‌کنند: بیا بازی! امید چه کند؟ اول دست‌هایش را با صابون بشوید، یا زود به بازی برود؟",
  "wash_hands|ball", "wash_hands",
  "بعد از تشناب دست‌ها میکروب دارد. میکروب آن‌قدر خورد است که دیده نمی‌شود، مگر ما را مریض می‌کند.", "scene_germs_hands"),
 ("scene_boy_friends", "امید دست‌هایش را با آب و صابون می‌شوید. بعد با دست‌های پاک پیش دوستانش می‌رود و بازی می‌کنند."),
 ("scene_boy_night", "شب شد. امید خسته است و خوابش می‌آید. پیش از خواب چه کند؟ دندان‌هایش را برس کند، یا همین طور بخوابد؟",
  "toothbrush|sleep", "toothbrush",
  "ریزه‌های نان تمام شب روی دندان می‌ماند و دندان را خراب می‌کند.", "scene_boy_toothache"),
 ("scene_boy_brushing", "امید دندان‌هایش را نرم‌نرم برس می‌کند: پیش، پشت و روی دندان‌ها."),
 ("scene_boy_sleeping", "امید در بستر گرم خود می‌خوابد. خواب خوب او را قوی و خوشحال می‌سازد. شب بخیر، امید!"),
])

AP = {"a": ("f:حیوان", "حیوان"), "p": ("f:گیاه", "گیاه")}
SE = {"sp": ("f:بهار", "بهار"), "su": ("f:تابستان", "تابستان"), "au": ("f:خزان", "خزان"), "wi": ("f:زمستان", "زمستان")}
FW = {"f": ("f:اهلی", "حیوان اهلی. پیش ما زندگی می‌کند."), "w": ("f:وحشی", "حیوان وحشی. در کوه و دشت زندگی می‌کند.")}
BQI = {"b": ("f:پرنده", "پرنده. بال دارد."), "q": ("f:چهارپا", "چهارپا. چهار پا دارد."), "i": ("f:حشره", "حشره. بسیار خورد است و شش پا دارد.")}
sorter(1, "good_plate.csv", [
 ("01", "کدام حیوان است و کدام گیاه؟ هر تصویر را در سبد درست بینداز.", AP, [
  ("sheep", "گوسفند", "a"), ("tree", "درخت", "p"), ("hen", "مرغ", "a"), ("flower", "گل", "p"),
  ("wheat", "گندم", "p"), ("fish", "ماهی", "a"), ("carrot", "زردک", "p"), ("butterfly", "پروانه", "a"),
 ]),
 ("02", "سال چهار فصل دارد: بهار، تابستان، خزان و زمستان. هر تصویر از کدام فصل است؟", SE, [
  ("blossom", "درخت شکوفه کرده است", "sp"),
  ("snow", "برف می‌بارد", "wi"),
  ("watermelon", "تربوز رسیده است", "su"),
  ("leaf_yellow", "برگ‌های زرد می‌ریزد", "au"),
  ("sprout", "سبزه نو از خاک برآمده است", "sp"),
  ("sun", "آفتاب بسیار گرم است", "su"),
  ("coat", "بالاپوش گرم می‌پوشیم", "wi"),
  ("pomegranate", "انار رسیده است", "au"),
 ]),
 ("03", "کدام حیوان اهلی است و پیش ما زندگی می‌کند؟ کدام حیوان وحشی است؟", FW, [
  ("cow", "گاو", "f"), ("wolf", "گرگ", "w"), ("goat", "بز", "f"), ("fox", "روباه", "w"),
  ("donkey", "خر", "f"), ("eagle", "عقاب", "w"), ("hen", "مرغ", "f"), ("snake", "مار", "w"),
 ]),
 ("04", "پرنده، چهارپا، یا حشره؟ هر حیوان را در سبد درست بینداز.", BQI, [
  ("pigeon", "کبوتر", "b"), ("cow", "گاو", "q"), ("bee", "زنبور عسل", "i"), ("sparrow", "گنجشک", "b"),
  ("cat", "پشک", "q"), ("ant", "مورچه", "i"), ("rooster", "خروس", "b"), ("horse", "اسپ", "q"),
 ]),
])

picker(1, "tree_keeper.csv", [
 ("01", "حیوان‌های دور و بر ما. گوش کن و تصویر درست را انتخاب کن.", [
  ("کدام حیوان به ما شیر می‌دهد؟", "cow", "hen|fish|cat", "گاو به ما شیر می‌دهد. بز و گوسفند هم شیر می‌دهند."),
  ("کدام حیوان تخم می‌دهد؟", "hen", "cow|donkey|sheep", "مرغ تخم می‌دهد."),
  ("پشم از کدام حیوان است؟", "sheep", "hen|fish|donkey", "پشم از گوسفند است. از پشم کالای گرم جور می‌شود."),
  ("کدام حیوان بار می‌برد؟", "donkey", "hen|cat|fish", "خر بار می‌برد و به مردم کمک می‌کند."),
  ("کدام حیوان در آب زندگی می‌کند؟", "fish", "hen|sheep|cat", "ماهی در آب زندگی می‌کند."),
  ("کدام حیوان در آسمان پرواز می‌کند؟", "pigeon", "cow|sheep|fish", "کبوتر بال دارد و پرواز می‌کند."),
  ("عسل را کدام یک می‌سازد؟", "bee", "butterfly|ant|pigeon", "زنبور عسل از گل‌ها عسل می‌سازد."),
  ("کدام حیوان از خانه و رمه نگهبانی می‌کند؟", "dog", "sheep|hen|fish", "سگ از خانه و رمه نگهبانی می‌کند."),
 ]),
 ("02", "گیاه‌های دور و بر ما. گوش کن و تصویر درست را انتخاب کن.", [
  ("کدام یک گیاه است؟", "flower", "sheep|stone|fish", "گل یک گیاه است. گیاه از خاک می‌روید."),
  ("کدام قسمت درخت زیر خاک است؟", "root", "leaf|flower|apple", "ریشه زیر خاک است. درخت با ریشه آب می‌نوشد."),
  ("گیاه برای کلان شدن به چه ضرورت دارد؟", "water", "stone|shoe|candy", "گیاه به آب، خاک و آفتاب ضرورت دارد."),
  ("سیب در کجا می‌روید؟", "tree", "river|stone|house", "سیب روی درخت می‌روید."),
  ("نان از کدام گیاه جور می‌شود؟", "wheat", "watermelon|flower|carrot", "گندم را آرد می‌کنیم و از آرد نان می‌پزیم."),
  ("وقتی دانه را در خاک می‌کاریم و آب می‌دهیم، چه از خاک می‌براید؟", "sprout", "stone|egg|shoe", "از دانه یک سبزه خورد می‌براید و آهسته‌آهسته کلان می‌شود."),
  ("کدام یک زیر خاک کلان می‌شود؟", "carrot", "apple|watermelon|grape", "زردک زیر خاک کلان می‌شود. کچالو و پیاز هم همین طور."),
  ("در روز گرم زیر سایه چه می‌نشینیم؟", "tree", "flower|carrot|wheat", "درخت به ما سایه می‌دهد."),
 ]),
 ("03", "فصل‌ها و آسمان. گوش کن و تصویر درست را انتخاب کن.", [
  ("برف در کدام فصل می‌بارد؟", "winter", "spring|summer|autumn", "برف در زمستان می‌بارد. زمستان سرد است."),
  ("در کدام فصل هوا بسیار گرم است؟", "summer", "winter|spring|autumn", "تابستان بسیار گرم است."),
  ("در کدام فصل برگ درخت‌ها زرد می‌شود و می‌ریزد؟", "autumn", "winter|spring|summer", "در خزان برگ‌ها زرد می‌شود و می‌ریزد."),
  ("در کدام فصل درخت‌ها شکوفه می‌کنند؟", "spring", "winter|summer|autumn", "در بهار درخت‌ها شکوفه می‌کنند و زمین سبز می‌شود."),
  ("در زمستان سرد چه می‌پوشیم؟", "coat", "sandals|watermelon|umbrella", "در زمستان بالاپوش گرم می‌پوشیم."),
  ("در روز چه در آسمان می‌تابد و ما را گرم می‌کند؟", "sun", "moon|star|snow", "آفتاب در روز می‌تابد و زمین را گرم می‌کند."),
  ("شب در آسمان چه می‌بینیم؟", "moon", "sun|tree|fish", "شب مهتاب و ستاره‌ها را می‌بینیم."),
  ("باران از کجا می‌بارد؟", "cloud", "sun|moon|star", "باران از ابر می‌بارد."),
 ]),
 ("04", "حالا همه را یکجا امتحان می‌کنیم. گوش کن و تصویر درست را انتخاب کن.", [
  ("چوچه گوسفند کدام است؟", "lamb", "chick|calf|kitten", "چوچه گوسفند را بره می‌گوییم."),
  ("چوچه مرغ کدام است؟", "chick", "lamb|calf|kitten", "چوچه مرغ از تخم می‌براید."),
  ("تربوز در کدام فصل می‌رسد؟", "summer", "winter|spring|autumn", "تربوز در گرمی تابستان می‌رسد."),
  ("کدام حیوان دو پا و دو بال دارد؟", "hen", "cow|sheep|donkey", "مرغ دو پا و دو بال دارد."),
  ("کدام حیوان پا ندارد و در آب شنا می‌کند؟", "fish", "hen|cow|ant", "ماهی پا ندارد. با باله شنا می‌کند."),
  ("کدام یک حیوان است؟", "goat", "tree|flower|stone", "بز یک حیوان است."),
  ("کدام یک حشره است؟", "ant", "pigeon|cat|fish", "مورچه یک حشره است."),
  ("کدام یک میوه است و روی درخت می‌روید؟", "apple", "carrot|bread|egg", "سیب میوه است و روی درخت می‌روید."),
 ]),
])

picker(1, "my_body.csv", [
 ("01", "بدن من. گوش کن و تصویر درست را انتخاب کن.", [
  ("سر", "head", "", "این سر است."), ("موی", "hair", "", "روی سر ما موی است."),
  ("چشم", "eye", "", "با چشم می‌بینیم."), ("گوش", "ear", "", "با گوش می‌شنویم."),
  ("بینی", "nose", "", "با بینی بوی می‌کنیم و نفس می‌کشیم."), ("دهن", "mouth", "", "با دهن می‌خوریم و گپ می‌زنیم."),
  ("دندان", "tooth", "", "با دندان نان را می‌جویم."), ("دست", "hand", "", "با دست چیزها را می‌گیریم."),
 ]),
 ("02", "باز هم بدن من. گوش کن و تصویر درست را انتخاب کن.", [
  ("پا", "foot", "", "با پا راه می‌رویم."), ("لنگ", "leg", "", "ما دو لنگ داریم."),
  ("بازو", "arm", "", "ما دو بازو داریم."), ("انگشت", "finger", "", "هر دست پنج انگشت دارد."),
  ("شکم", "tummy", "", "نانی که می‌خوریم به شکم می‌رود."), ("روی", "face", "", "چشم، بینی و دهن در روی ما است."),
  ("زانو", "knee", "", "لنگ از زانو قات می‌شود."), ("ناخن", "nail", "", "ناخن‌ها را کوتاه و پاک نگه می‌کنیم."),
 ]),
 ("03", "هر قسمت بدن چه کار می‌کند؟ گوش کن و تصویر درست را انتخاب کن.", [
  ("با چه می‌بینیم؟", "eye", "ear|nose|foot", "با چشم می‌بینیم."),
  ("با چه می‌شنویم؟", "ear", "eye|mouth|hand", "با گوش می‌شنویم."),
  ("با چه بوی می‌کنیم؟", "nose", "ear|foot|hair", "با بینی بوی می‌کنیم."),
  ("با چه گپ می‌زنیم؟", "mouth", "ear|knee|hair", "با دهن گپ می‌زنیم."),
  ("نان را با چه می‌جویم؟", "tooth", "nose|ear|finger", "با دندان می‌جویم."),
  ("با چه راه می‌رویم؟", "foot", "ear|hair|tooth", "با پا راه می‌رویم."),
  ("قلم را با چه می‌گیریم؟", "hand", "foot|ear|nose", "قلم را با دست می‌گیریم."),
  ("نانی که خوردیم به کجا می‌رود؟", "tummy", "knee|hair|ear", "نان به شکم می‌رود و به ما قوت می‌دهد."),
 ]),
 ("04", "دندان‌های سالم. گوش کن و تصویر درست را انتخاب کن.", [
  ("دندان را با چه پاک می‌کنیم؟", "toothbrush", "comb|spoon|soap", "دندان را با برس دندان پاک می‌کنیم، روز دو بار."),
  ("روی برس دندان چه می‌مانیم؟", "toothpaste", "soap|candy|sugar", "کمی کریم دندان روی برس می‌مانیم."),
  ("کدام یک دندان را خراب می‌کند؟", "candy", "carrot|milk|water", "شیرینی زیاد دندان را خراب می‌کند."),
  ("کدام یک برای دندان خوب است؟", "milk", "candy|soda|sugar", "شیر دندان و استخوان را قوی می‌سازد."),
  ("کدام را با دندان می‌جویم؟", "bread", "water|milk|soda", "نان را با دندان خوب می‌جویم."),
  ("دندانت درد می‌کند. به کی می‌گویی؟", "parents", "cat|ball|candy", "اگر دندانت درد کرد، به مادر یا پدرت بگو. آنها تو را به کلینیک می‌برند."),
  ("بعد از خوردن شیرینی، دهن را با چه می‌شوییم؟", "water", "soda|candy|sugar", "بعد از شیرینی دهن را با آب پاک می‌شوییم."),
  ("کدام دندان سالم است؟", "tooth_clean", "tooth_decayed|candy|soda", "دندان سالم سفید و پاک است."),
 ]),
 ("05", "خواب خوب. گوش کن و تصویر درست را انتخاب کن.", [
  ("چه وقت می‌خوابیم؟", "night", "sun|school|ball", "شب می‌خوابیم. اطفال باید شب وقت بخوابند."),
  ("روی چه می‌خوابیم؟", "mattress", "stone|table|tree", "روی توشک می‌خوابیم."),
  ("سر خود را روی چه می‌مانیم؟", "pillow", "stone|plate|book", "سر را روی بالشت می‌مانیم."),
  ("در شب سرد چه بالای خود می‌کشیم؟", "blanket", "plate|sandals|umbrella", "کمپل ما را گرم نگه می‌کند."),
  ("پیش از خواب دندان را با چه پاک می‌کنیم؟", "toothbrush", "candy|ball|soda", "پیش از خواب دندان را برس می‌کنیم."),
  ("طفل خسته است و فاژه می‌کشد. به چه ضرورت دارد؟", "sleep", "ball|candy|school", "طفل خسته به خواب ضرورت دارد. خواب به ما قوت می‌دهد."),
  ("صبح وقت کدام مرغ بانگ می‌دهد؟", "rooster", "fish|cat|sheep", "خروس صبح وقت بانگ می‌دهد و ما بیدار می‌شویم."),
  ("شب در آسمان چه می‌تابد؟", "moon", "sun|tree|flower", "شب مهتاب می‌تابد. وقت خواب است."),
 ]),
])

# =================================================================== LEVEL 2
builder(2, "clean_hands.csv", [
 ("01", "آب را چطور پاک بسازیم؟ تصویرها را به ترتیب بمان. آب جوش داغ است. این کار را همیشه با یک کلان بکن.", [
  ("آب آوردیم. اول جوش می‌دهیم. بعد در ظرف سرپوش‌دار نگه می‌کنیم.", "water_bucket|water_boiling|water_covered", "",
   "آفرین! آب جوش‌داده و سرپوشیده پاک است.",
   "آب را روی آتش می‌مانیم تا خوب جوش بزند و قل‌قل کند. جوش دادن میکروب‌ها را می‌کشد."),
  ("آب بیاور، جوش بده، سرپوش بمان، و در گیلاس پاک بنوش.", "water_bucket|water_boiling|water_covered|water", "",
   "آفرین! حالا آب پاک می‌نوشیم.",
   "بعد از جوش دادن می‌مانیم که آب در همان ظرف سرپوشیده خودش سرد شود. آب ناجوش را با آن یکجا نمی‌کنیم."),
  ("آب گل‌آلود است. اول از تکه پاک تیر کن. بعد جوش بده، سرپوش بمان، و در گیلاس پاک بنوش.", "water_cloudy|water_filter_cloth|water_boiling|water_covered|water", "",
   "آفرین! اول صاف، بعد جوش، بعد سرپوش.",
   "تکه پاک گل و خاشاک را می‌گیرد، مگر میکروب را نمی‌گیرد. برای همین بعد از صاف کردن، آب را جوش می‌دهیم."),
 ]),
 ("02", "قدم‌های تشناب رفتن را به ترتیب درست بمان.", [
  ("به تشناب می‌رویم. سوراخ تشناب را می‌پوشانیم. دست‌ها را با صابون می‌شوییم.", "latrine|latrine_cover|wash_hands", "",
   "آفرین! بعد از تشناب همیشه دست‌ها را با صابون می‌شوییم.",
   "سرپوش تشناب نمی‌ماند که مگس داخل شود و چتلی را به خوراک ما ببرد."),
  ("اول چپلک می‌پوشیم. به تشناب می‌رویم. سوراخ را می‌پوشانیم. دست‌ها را با صابون می‌شوییم.", "sandals|latrine|latrine_cover|wash_hands", "",
   "آفرین! چپلک، تشناب، سرپوش، صابون.",
   "با پای برهنه به تشناب نمی‌رویم. چپلک پای ما را از چتلی نگه می‌کند."),
  ("بعد از تشناب: دست را تر کن، صابون بزن، خوب بمال، و آب بکش.", "latrine|hw_wet|hw_soap|hw_palms|hw_rinse", "",
   "آفرین! دست‌های پاک ما را از اسهال نگه می‌کند.",
   "بعد از تشناب دست‌ها میکروب دارد. آب تنها بس نیست. با صابون می‌شوییم."),
 ]),
 ("03", "طفلی که اسهال دارد به او آر اس ضرورت دارد. او آر اس را همیشه یک کلان تیار می‌کند. تو قدم‌ها را یاد بگیر و کمک کن.", [
  ("آب پاک در ظرف پاک. تمام پاکت در آب. شور بده تا حل شود.", "ors_water|ors_pour|ors_stir", "",
   "آفرین! او آر اس تیار شد.",
   "آب باید جوش‌داده و سرد شده باشد، همان اندازه که روی پاکت نشان داده شده یا کارمند صحی گفته است. نه کم، نه زیاد."),
  ("از اول تا آخر: دست‌ها را با صابون بشوی. آب پاک را در ظرف پاک بریز. تمام پاکت را در آب بینداز. شور بده. کم‌کم به طفل بده.", "wash_hands|ors_water|ors_pour|ors_stir|ors_sip", "",
   "آفرین! او آر اس را کم‌کم و زودزود به طفل می‌دهیم. او آر اس تیار شده را تنها یک شبانه‌روز کار می‌گیریم. بعد از آن دور می‌ریزیم و نو جور می‌کنیم.",
   "پاکت او آر اس را از کلینیک می‌گیریم. اگر طفل بدتر شد، در اسهالش خون بود، نوشیده نتوانست، یا بسیار خواب‌آلود بود، زود به کلینیک می‌رویم."),
 ]),
])

SU = {"s": ("f:پاک", "آب پاک. می‌توانیم بنوشیم."), "u": ("f:ناپاک", "آب ناپاک. ما را مریض می‌کند.")}
GD = {"g": ("f:خوب", "کار خوب. آب پاک می‌ماند."), "b": ("f:خطر", "خطر دارد. آب ناپاک می‌شود.")}
KD = {"k": ("f:پاک می‌ماند", "آب را پاک نگه می‌کند."), "d": ("f:چتل می‌شود", "آب را چتل می‌کند.")}
DB = {"d": ("f:بنوش", "این آب را می‌توانم بنوشم."), "b": ("f:اول جوش", "این آب را اول باید جوش بدهیم.")}
sorter(2, "safe_water.csv", [
 ("01", "کدام آب پاک است و کدام ناپاک؟ هر تصویر را در سبد درست بینداز.", SU, [
  ("water_boiled", "آب جوش‌داده", "s"),
  ("water_puddle", "آب ایستاده", "u"),
  ("water_pump", "آب بمبه دستی", "s"),
  ("water_stream", "آب جوی", "u"),
  ("water_covered", "آب جوش‌داده در ظرف سرپوش‌دار", "s"),
  ("water_pond", "آب حوض", "u"),
  ("water_tap", "آب نل", "s"),
  ("river", "آب دریا", "u"),
 ]),
 ("02", "آب پاک را در خانه چطور نگه کنیم؟ کدام کار خوب است و کدام خطر دارد؟", GD, [
  ("water_boiling", "آب را جوش می‌دهیم", "g"),
  ("water_hand_dip", "دست را در ظرف آب می‌زنیم", "b"),
  ("water_covered", "سرپوش ظرف آب را می‌مانیم", "g"),
  ("water_bucket_open", "سطل آب را سرباز می‌مانیم", "b"),
  ("water_ladle", "با چمچه پاک آب می‌گیریم", "g"),
  ("water_cup_dirty", "با گیلاس چتل آب می‌نوشیم", "b"),
  ("water", "در گیلاس پاک می‌نوشیم", "g"),
  ("water_animal", "حیوان از ظرف آب ما می‌نوشد", "b"),
 ]),
 ("03", "چه چیز آب چاه و جوی را پاک نگه می‌کند، و چه چیز آن را چتل می‌کند؟", KD, [
  ("well_covered", "چاه سرپوشیده", "k"),
  ("garbage_water", "کثافات در جوی", "d"),
  ("latrine_far", "تشناب دور از چاه", "k"),
  ("latrine_near_well", "تشناب نزدیک چاه", "d"),
  ("bucket_clean", "سطل پاک", "k"),
  ("animals_water", "حیوان در آب", "d"),
  ("waste_pit", "کثافات در چقوری، دور از آب", "k"),
  ("bucket_dirty", "سطل چتل روی زمین", "d"),
 ]),
 ("04", "کدام آب را حالا می‌توانم بنوشم؟ کدام را اول باید جوش بدهیم؟", DB, [
  ("water_boiled", "آب جوش‌داده", "d"),
  ("water_stream", "آب جوی", "b"),
  ("water_covered", "آب جوش‌داده در ظرف سرپوش‌دار", "d"),
  ("river", "آب دریا", "b"),
  ("water_pump", "آب بمبه دستی", "d"),
  ("water_cloudy", "آب گل‌آلود. اول صاف می‌کنیم، بعد جوش می‌دهیم.", "b"),
  ("water_tap", "آب نل", "d"),
  ("well_open", "آب چاه سرباز", "b"),
 ]),
])

story(2, "safe_water_story.csv", [
 ("scene_girl_walking_home", "شیرین از مکتب به خانه می‌رود. هوا گرم است و او بسیار تشنه است."),
 ("scene_girl_stream", "در راه یک جوی آب است. آب آن صاف و خنک معلوم می‌شود."),
 ("scene_girl_stream", "شیرین کدام آب را بنوشد؟ آب جوی را، یا آب جوش‌داده خانه را؟",
  "water_stream|water_boiled", "water_boiled",
  "آب جوی صاف معلوم می‌شود، مگر میکروب دارد. میکروب بسیار خورد است و به چشم دیده نمی‌شود. از این آب شکم شیرین درد می‌گیرد و اسهال می‌شود.", "scene_girl_tummy_ache"),
 ("scene_girl_mother_pot", "شیرین صبر می‌کند و به خانه می‌رسد. مگر ظرف آب جوش خالی است. مادرش تازه آب آورده است. آب کمی گل‌آلود است."),
 ("scene_filter_cloth", "مادر می‌گوید: اول آب را از تکه پاک تیر می‌کنیم تا گل و خاشاک آن گرفته شود."),
 ("scene_filtered_water", "حالا آب صاف شد. بعد چه کنند؟ آب را جوش بدهند، یا همین طور بنوشند؟",
  "water_boiling|water", "water_boiling",
  "تکه گل را می‌گیرد، مگر میکروب‌ها هنوز در آب است. جوش دادن میکروب‌ها را می‌کشد.", "scene_germs_water"),
 ("scene_boiling", "مادر دیگ را روی آتش می‌ماند. آب خوب جوش می‌زند و قل‌قل می‌کند. شیرین از آتش و آب جوش دور می‌ایستد. بعد می‌مانند که آب خودش سرد شود."),
 ("scene_two_pots", "آب جوش‌داده را در کجا نگه کنند؟ در ظرف پاک سرپوش‌دار، یا در سطل سرباز؟",
  "water_covered|water_bucket_open", "water_covered",
  "در سطل سرباز خاک و مگس می‌افتد و آب دوباره ناپاک می‌شود.", "scene_flies_bucket"),
 ("scene_girl_drinking", "شیرین با چمچه پاک آب می‌گیرد، نه با دست. در گیلاس پاک می‌ریزد و می‌نوشد. آب پاک چه مزه‌دار است!"),
 ("scene_girl_teaching_brother", "شیرین به برادر خوردش می‌گوید: آب را جوش می‌دهیم، سرپوش می‌مانیم، و با گیلاس پاک می‌نوشیم. اگر از آب مریض شدی، زود به مادر یا پدر بگو."),
])

EGP = {"e": ("f:قوت", "خوراک‌های قوت. برای دویدن، بازی و کار به ما قوت می‌دهد."),
       "g": ("f:نمو", "خوراک‌های نمو. بدن را کلان و استخوان را قوی می‌سازد."),
       "p": ("f:محافظت", "خوراک‌های محافظت. میوه و ترکاری، بدن را از مریضی نگه می‌کند.")}
EV = {"e": ("f:هر روز", "هر روز خوب است."), "s": ("f:کم‌کم", "تنها کم‌کم و گاهی.")}
sorter(2, "good_plate.csv", [
 ("01", "خوراک‌ها سه گروه است: قوت، نمو و محافظت. هر خوراک را در سبد خودش بینداز.", EGP, [
  ("bread", "نان", "e"), ("egg", "تخم مرغ", "g"), ("apple", "سیب", "p"), ("rice", "برنج", "e"),
  ("milk", "شیر", "g"), ("carrot", "زردک", "p"), ("potato", "کچالو", "e"), ("beans", "لوبیا", "g"),
 ]),
 ("02", "باز هم سه گروه: قوت، نمو و محافظت. هر خوراک را در سبد خودش بینداز.", EGP, [
  ("lentils", "دال", "g"), ("tomato", "بادنجان رومی", "p"), ("corn", "جواری", "e"), ("yoghurt", "ماست", "g"),
  ("spinach", "پالک", "p"), ("rice", "برنج", "e"), ("meat", "گوشت", "g"), ("grape", "انگور", "p"),
 ]),
 ("03", "یک بشقاب خوب از هر سه گروه دارد. هر خوراک را در سبد خودش بینداز.", EGP, [
  ("chickpeas", "نخود", "g"), ("pumpkin", "کدو", "p"), ("potato", "کچالو", "e"), ("fish", "ماهی", "g"),
  ("apricot", "زردآلو", "p"), ("bread", "نان", "e"), ("milk", "شیر", "g"), ("pomegranate", "انار", "p"),
 ]),
 ("04", "کدام خوراک هر روز خوب است؟ کدام را تنها کم‌کم و گاهی می‌خوریم؟", EV, [
  ("bread", "نان", "e"), ("candy", "شیرینی", "s"), ("egg", "تخم مرغ", "e"), ("apple", "سیب", "e"),
  ("soda", "نوشابه شیرین", "s"), ("beans", "لوبیا", "e"), ("sugar", "بوره زیاد", "s"), ("spinach", "پالک", "e"),
 ]),
])

story(2, "little_nurse.csv", [
 ("scene_baby_sick", "لیلا و فرید از مکتب آمدند. برادر خوردشان بی‌حال است. او چند بار اسهال کرده است."),
 ("scene_baby_sick", "لیلا و فرید چه کنند؟ زود به مادر بگویند، یا بروند بازی کنند؟",
  "mother|ball", "mother",
  "طفل مریض به کمک کلان‌ها ضرورت دارد. هر وقت کسی مریض است، زود به مادر، پدر یا یک کلان دیگر بگو.", "scene_baby_weak"),
 ("scene_mother_ors_packet", "مادر می‌گوید: آفرین که زود گفتید. اسهال آب بدن را می‌برد و این برای طفل خطر دارد. باید آب رفته پس به بدنش برسد. از کلینیک پاکت او آر اس داریم."),
 ("scene_ors_mixing", "مادر دست‌هایش را با صابون می‌شوید. در ظرف پاک، آب جوش‌داده و سرد شده می‌ریزد، همان اندازه که روی پاکت نشان داده شده. تمام پاکت را در آب می‌اندازد و شور می‌دهد تا حل شود."),
 ("scene_ors_sips", "مادر با قاشق و پیاله، کم‌کم و زودزود به طفل او آر اس می‌دهد. لیلا و فرید کمک می‌کنند. اگر طفل استفراغ کند، ده دقیقه صبر می‌کنند و باز آهسته‌تر می‌دهند."),
 ("scene_mother_ors_packet", "حالا وقت نان است. به طفل مریض خوراک بدهند، یا هیچ خوراک ندهند؟",
  "food_bowl|bowl_empty", "food_bowl",
  "طفل مریض به خوراک ضرورت دارد تا قوت بگیرد. شیر مادر و خوراک را بس نمی‌کنیم.", "scene_baby_weak"),
 ("scene_mother_feeding", "مادر مثل هر روز به طفل شیر خود را می‌دهد، و کم‌کم خوراک نرم هم می‌دهد. نوشابه و شربت بسیار شیرین نمی‌دهد. دوا را هم خودسر نمی‌دهد. دوا را تنها داکتر یا کارمند صحی می‌گوید."),
 ("scene_baby_danger", "شام، لیلا می‌بیند که طفل بدتر شده است. چشم‌هایش فرورفته است، بسیار خواب‌آلود است، و چیزی نوشیده نمی‌تواند. لیلا زود به مادر می‌گوید."),
 ("scene_baby_danger", "مادر می‌گوید: اگر طفل نوشیده نتواند، بسیار خواب‌آلود باشد، چشم‌هایش فرورفته باشد، تب داشته باشد، یا در اسهالش خون باشد، این نشانه خطر است. فامیل چه کند؟ زود طفل را به کلینیک ببرند، یا تا فردا در خانه صبر کنند؟",
  "clinic|house", "clinic",
  "صبر کردن خطرناک است. طفلی که نشانه خطر دارد باید زود به کلینیک برود.", "scene_baby_danger"),
 ("scene_clinic", "پدر و مادر طفل را زود به کلینیک می‌برند. کارمند صحی طفل را تداوی می‌کند و او آهسته‌آهسته خوب می‌شود. لیلا و فرید یاد گرفتند: به کلان‌ها بگو، او آر اس بده، خوراک را بس نکن، و اگر نشانه خطر بود، زود به کلینیک برو."),
])

picker(2, "tree_keeper.csv", [
 ("01", "آب از کجا می‌آید و به کجا می‌رود؟ گوش کن و تصویر درست را انتخاب کن.", [
  ("باران و برف از کجا می‌بارد؟", "cloud", "sun|moon|tree", "باران و برف از ابر می‌بارد."),
  ("چه چیز آب را گرم می‌کند تا بخار شود و به آسمان برود؟", "sun", "moon|snow|stone", "آفتاب آب را گرم می‌کند. آب بخار می‌شود، به آسمان می‌رود و ابر جور می‌شود."),
  ("در زمستان روی کوه‌ها چه جمع می‌شود؟", "snow", "fire|leaf|flower", "در زمستان روی کوه‌ها برف جمع می‌شود."),
  ("در بهار برف کوه آب می‌شود. این آب به کجا می‌ریزد؟", "river", "house|sun|star", "برف آب می‌شود و به جوی و دریا می‌ریزد."),
  ("آب باران در زمین فرو می‌رود. از کجا آن را دوباره بالا می‌کشیم؟", "well", "cloud|sun|mountain", "آب زیر زمین جمع می‌شود. ما آن را از چاه بالا می‌کشیم."),
  ("وقتی آب بسیار سرد شود، به چه بدل می‌شود؟", "ice", "fire|sand|leaf", "آب در سردی یخ می‌شود."),
  ("وقتی آب جوش می‌زند، چه از آن بالا می‌رود؟", "steam", "ice|snow|stone", "از آب جوش بخار بالا می‌رود."),
  ("کدام یک به آب ضرورت ندارد؟", "stone", "tree|sheep|flower", "آدم‌ها، حیوان‌ها و گیاه‌ها همه به آب ضرورت دارند. آب را ضایع نمی‌کنیم."),
 ]),
 ("02", "با کثافات چه کنیم؟ گوش کن و تصویر درست را انتخاب کن.", [
  ("کثافات را در کجا می‌اندازیم؟", "waste_pit", "water_stream|street|well", "کثافات را در چقوری کثافات می‌اندازیم، دور از آب و خانه."),
  ("کدام یک در خاک زود می‌پوسد؟", "peel", "plastic_bag|bottle|can", "پوست میوه زود می‌پوسد و خاک می‌شود."),
  ("کدام یک سال‌های سال در زمین می‌ماند و نمی‌پوسد؟", "plastic_bag", "peel|leaf|bread", "پلاستیک سال‌های سال نمی‌پوسد. آن را در زمین و آب نمی‌اندازیم."),
  ("شیشه شکسته خطر دارد. کی آن را بردارد؟", "parents", "cat|hen|sheep", "به شیشه شکسته و چیزهای تیز دست نمی‌زنیم. به یک کلان می‌گوییم."),
  ("خوراک را از مگس چطور نگه کنیم؟", "food_covered", "food_uncovered|garbage|plastic_bag", "مگس از کثافات میکروب می‌آورد. سر خوراک را می‌پوشانیم."),
  ("با بوتل خالی چه کنیم؟", "bottle_reuse", "garbage_water|garbage_street|plastic_fire", "بوتل پاک را دوباره کار می‌گیریم. پلاستیک را نمی‌سوزانیم، چون دود آن ضرر دارد."),
  ("بعد از دست زدن به کثافات چه می‌کنیم؟", "wash_hands", "bread|ball|sleep", "بعد از دست زدن به کثافات، دست‌ها را با صابون می‌شوییم."),
  ("کدام حویلی پاک است؟", "yard_clean", "yard_dirty|garbage_street|garbage_water", "حویلی پاک مگس و موش کم دارد و ما را سالم نگه می‌کند."),
 ]),
 ("03", "چرا درخت مهم است؟ گوش کن و تصویر درست را انتخاب کن.", [
  ("در روز گرم چه به ما سایه می‌دهد؟", "tree", "sun|fire|sand", "درخت به ما سایه می‌دهد و هوا را تازه می‌کند."),
  ("ریشه درخت چه را محکم می‌گیرد تا باران و سیلاب آن را نبرد؟", "soil", "sun|moon|bottle", "ریشه درخت خاک را محکم می‌گیرد."),
  ("کدام را درخت به ما می‌دهد؟", "apple", "plastic_bag|stone|bottle", "درخت به ما میوه، سایه و چوب می‌دهد."),
  ("پرنده خانه خود را روی درخت می‌سازد. خانه پرنده کدام است؟", "nest", "bucket|bottle|stove", "پرنده روی درخت آشیانه می‌سازد."),
  ("نهال نو به چه ضرورت دارد؟", "water", "fire|plastic_bag|stone", "نهال نو را آب می‌دهیم تا کلان شود."),
  ("اگر درختی قطع شد، به جای آن چه می‌نشانیم؟", "sapling", "axe|fire|garbage", "به جای هر درخت قطع شده، نهال نو می‌نشانیم."),
  ("از چوب درخت چه جور می‌کنیم؟", "door", "bottle|stone|plastic_bag", "از چوب درخت دروازه و کلکین جور می‌کنیم."),
  ("بز نهال خورد را می‌خورد. دور نهال چه می‌مانیم؟", "fence", "bottle|fire|plastic_bag", "دور نهال کتاره می‌مانیم تا حیوان‌ها آن را نخورند."),
 ]),
 ("04", "حالا همه را یکجا امتحان می‌کنیم. گوش کن و تصویر درست را انتخاب کن.", [
  ("برف و باران، هر دو از چه جور شده است؟", "water", "sand|fire|stone", "برف و باران هر دو آب است."),
  ("کدام یک در آسمان است؟", "cloud", "well|river|tree", "ابر در آسمان است. باران از ابر می‌بارد."),
  ("خریطه پلاستیکی را در کجا می‌اندازیم؟", "waste_pit", "water_stream|well|street", "پلاستیک را در چقوری کثافات می‌اندازیم، نه در جوی و نه در کوچه."),
  ("کدام یک ریشه دارد؟", "tree", "stone|bottle|cloud", "درخت ریشه دارد."),
  ("با کدام یک آب را از زیر زمین بالا می‌کشیم؟", "water_pump", "plastic_bag|stove|fence", "با بمبه دستی آب را از زیر زمین بالا می‌کشیم."),
  ("کدام یک می‌پوسد و خاک را قوی می‌سازد؟", "leaf", "bottle|can|plastic_bag", "برگ‌ها می‌پوسند و خاک را قوی می‌سازند."),
  ("برای نشاندن نهال، زمین را با چه می‌کنیم؟", "shovel", "axe|can|plastic_bag", "با بیل زمین را می‌کنیم و نهال را می‌نشانیم."),
  ("آب دریا از کجا شروع می‌شود؟", "mountain", "well|house|waste_pit", "برف کوه آب می‌شود و دریا از کوه شروع می‌شود."),
 ]),
])

picker(2, "my_body.csv", [
 ("01", "دود دیگدان. گوش کن و تصویر درست را انتخاب کن.", [
  ("دود کدام را می‌سوزاند و اشک می‌آورد؟", "eye", "foot|tooth|finger", "دود چشم را می‌سوزاند و برای سینه و نفس ما ضرر دارد."),
  ("وقت پخت‌وپز، برای بیرون شدن دود چه را باز می‌کنیم؟", "window", "book|bottle|bucket", "کلکین و دروازه را باز می‌کنیم تا دود بیرون برود و هوای تازه بیاید."),
  ("دود دیگدان از کجا باید بیرون برود؟", "chimney", "bucket|pillow|well", "دودکش دود را از خانه بیرون می‌برد."),
  ("کدام هیزم کمتر دود می‌کند؟", "wood_dry", "wood_wet|plastic_bag|garbage", "هیزم خشک کمتر دود می‌کند. هیزم تر بسیار دود می‌کند."),
  ("کدام را هیچ وقت در آتش نمی‌اندازیم؟", "plastic_bag", "wood_dry|charcoal|twigs", "پلاستیک را نمی‌سوزانیم. دود آن بسیار ضرر دارد."),
  ("از دود سرفه می‌کنی. به کجا می‌روی؟", "yard", "kitchen_smoky|stove|fire", "از دود دور می‌شویم و به هوای تازه می‌رویم. طفل‌های خورد را هم از دود دور نگه می‌کنیم."),
  ("طفل خورد را از چه دور نگه می‌کنیم تا نسوزد؟", "fire", "ball|book|pillow", "طفل‌های خورد را از آتش و دیگ داغ دور نگه می‌کنیم."),
  ("کسی از دود بسیار سرفه می‌کند و نفسش تنگ است. به یک کلان می‌گوییم. او را به کجا می‌برند؟", "clinic", "well|tree|stove", "اگر کسی نفس‌تنگ شد یا بسیار سرفه کرد، به یک کلان بگو تا او را به کلینیک ببرد."),
 ]),
 ("02", "تشناب پاک. گوش کن و تصویر درست را انتخاب کن.", [
  ("وقتی به تشناب ضرورت داریم، به کجا می‌رویم؟", "latrine", "water_stream|field|street", "همیشه به تشناب می‌رویم، نه به دشت و نه کنار جوی."),
  ("بعد از تشناب دست را با آب و چه می‌شوییم؟", "soap", "stone|leaf|sand", "بعد از تشناب دست‌ها را با آب و صابون می‌شوییم."),
  ("به تشناب با چه می‌رویم؟", "sandals", "pillow|book|ball", "با چپلک می‌رویم، نه با پای برهنه."),
  ("بعد از کار، سوراخ تشناب را چه می‌کنیم؟", "latrine_cover", "latrine_open|plate|pillow", "سوراخ تشناب را می‌پوشانیم تا مگس داخل نشود."),
  ("کدام یک از تشناب به خوراک ما میکروب می‌برد؟", "fly", "butterfly|bee|ant", "مگس روی چتلی می‌نشیند و بعد روی خوراک ما."),
  ("تشناب باید از چه دور باشد؟", "well", "tree|stone|fence", "تشناب باید از چاه و آب نوشیدنی دور باشد تا آب چتل نشود."),
  ("تشناب را با چه پاک می‌کنیم؟", "broom", "ball|book|pillow", "تشناب را با جاروب و آب پاک نگه می‌کنیم و بعد دست‌ها را با صابون می‌شوییم."),
  ("بعد از تشناب و پیش از نان خوردن چه می‌کنیم؟", "wash_hands", "bread|ball|sleep", "دست‌ها را با صابون می‌شوییم."),
 ]),
 ("03", "خانه سالم. گوش کن و تصویر درست را انتخاب کن.", [
  ("کدام دیگدان دود را از خانه بیرون می‌برد؟", "stove_chimney", "stove_open|bucket|pillow", "دیگدان دودکش‌دار دود را بیرون می‌برد."),
  ("بعد از تشناب روی دست‌ها چه است که به چشم دیده نمی‌شود؟", "germ", "flower|star|candy", "میکروب دیده نمی‌شود، مگر ما را مریض می‌کند. صابون آن را می‌برد."),
  ("در اتاق پر دود چه را باز می‌کنیم؟", "door", "book|bottle|bucket", "دروازه و کلکین را باز می‌کنیم."),
  ("دست‌های شسته را با چه خشک می‌کنیم؟", "towel", "sand|broom|leaf", "با دستمال پاک خشک می‌کنیم."),
  ("دود از چه می‌براید؟", "fire", "water|ice|snow", "دود از آتش می‌براید. در اتاقی که آتش یا زغال می‌سوزد، همیشه یک راه برای هوای تازه باز می‌مانیم."),
  ("مگس از کثافات می‌آید. اگر روی کدام بنشیند، ما مریض می‌شویم؟", "food_uncovered", "stone|fence|chimney", "سر خوراک را می‌پوشانیم تا مگس روی آن ننشیند."),
  ("از دود چشمت می‌سوزد و سرت درد می‌کند. به کی می‌گویی؟", "parents", "cat|hen|ball", "به مادر یا پدر بگو، و به هوای تازه برو."),
  ("کدام تشناب خوب است؟", "latrine_clean", "latrine_dirty|field|water_stream", "تشناب خوب پاک است، سرپوش و دروازه دارد، و آب و صابون نزدیک آن است."),
 ]),
])

# ---------------------------------------------------------------- pack.json
def game(id_, engine, letter, en, fa, intro, icon, v1=False):
    g = {"id": id_, "engine": engine, "letter": letter, "title_en": en, "title_fa": fa, "intro_fa": intro, "icon": icon}
    if v1:
        g["v1"] = True
    g["sheet"] = id_ + ".csv"
    return g

packs = {
 1: {"pack": "garden-1", "subject": "garden", "level": 1, "version": 1,
     "title_en": "Garden 1: Me", "title_fa": "باغ ۱: من",
     "games": [
      game("clean_hands", "builder", "a", "Clean Hands", "دست‌های پاک", "تصویرها را به ترتیب درست بمان.", "soap", True),
      game("safe_water", "sorter", "b", "Clean or Dirty", "پاک یا چتل", "هر تصویر را در سبد درست بینداز.", "water", True),
      game("hygiene_story", "story", "c", "Omid's Day", "روز امید", "قصه را گوش کن و به امید کمک کن که کار درست را بکند.", "toothbrush"),
      game("good_plate", "sorter", "d", "Garden Baskets", "سبدهای باغ", "هر تصویر را در سبد درست بینداز.", "sheep"),
      game("tree_keeper", "journey", "e", "Tree Keeper", "باغبان خورد", "گوش کن و تصویر درست را انتخاب کن.", "tree"),
      game("my_body", "listen_pick", "f", "My Body", "بدن من", "گوش کن و تصویر درست را انتخاب کن.", "hand"),
     ]},
 2: {"pack": "garden-2", "subject": "garden", "level": 2, "version": 1,
     "title_en": "Garden 2: My Home", "title_fa": "باغ ۲: خانه من",
     "games": [
      game("clean_hands", "builder", "a", "Clean Hands", "دست‌های پاک", "تصویرها را به ترتیب درست بمان.", "soap", True),
      game("safe_water", "sorter", "b", "Safe Water", "آب پاک", "هر تصویر را در سبد درست بینداز.", "water", True),
      game("safe_water_story", "story", "c", "Shirin and the Safe Water", "شیرین و آب پاک", "قصه را گوش کن و به شیرین کمک کن که کار درست را بکند.", "water_boiled"),
      game("good_plate", "sorter", "d", "Good Plate", "بشقاب خوب", "هر خوراک را در سبد خودش بینداز.", "bread"),
      game("tree_keeper", "journey", "e", "Tree Keeper", "باغبان خورد", "گوش کن و تصویر درست را انتخاب کن.", "tree"),
      game("my_body", "listen_pick", "f", "Healthy Home", "خانه سالم", "گوش کن و تصویر درست را انتخاب کن.", "house"),
      game("little_nurse", "story", "g", "Little Nurse", "پرستار خورد", "قصه را گوش کن و به لیلا و فرید کمک کن که کار درست را بکنند.", "ors_packet"),
     ]},
}
for lvl, p in packs.items():
    for g in p["games"]:
        used[lvl].add(g["icon"])
    (OUT / str(lvl) / "pack.json").write_text(json.dumps(p, ensure_ascii=False, indent=1) + "\n", "utf-8")

# ---------------------------------------------------------------- items.csv and pictures.txt
missing = sorted((used[1] | used[2]) - set(P))
unused = sorted(set(P) - used[1] - used[2])
if missing or unused:
    sys.exit(f"missing descriptions: {missing}\nunused: {unused}")

def tag(n):
    if n.startswith(("hw_", "tb_", "ors_")): return "steps"
    if n.startswith(("water", "well")): return "water"
    if n.startswith("latrine"): return "latrine"
    return ""
order = list(P)
for lvl in (1, 2):
    rows = [["01", n, P[n][0], P[n][1], n, tag(n)] for n in order if n in used[lvl] and not n.startswith("scene_")]
    with (OUT / str(lvl) / "items.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["unit", "key", "en", "fa", "picture", "tags"])
        w.writerows(rows)
with (OUT / "pictures.txt").open("w", encoding="utf-8") as f:
    for n in order:
        lv = "+".join(str(l) for l in (1, 2) if n in used[l])
        f.write(f"{n}: {P[n][2]} [garden-{lv}]\n")
print(len(P), "pictures;", len(used[1]), "in L1;", len(used[2]), "in L2")

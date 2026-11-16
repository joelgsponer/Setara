# The whole alphabet (`fa-1-alphabet`), an add-on to Dari reading 1

Written by an AI (Claude). **No Dari speaker, teacher or child has seen or
heard any of it.** This file says what the pack teaches, what was decided
while writing it, and what a human reviewer has to decide.

## Why it exists

Dari reading 1 (`fa-1`) teaches twelve frequent letters, as the curriculum
asks. The owner wanted a child who opens level 1 to be able to meet **all**
letters. This pack is that: an optional add-on (`"optional": true`) that adds
nine games to Library level 1. Leave the zip off the card and nothing of it
is there; `fa-1` and `fa-2` do not depend on it.

It teaches recognition, not reading: for each of the 32 letters (and آ, which
`fa-1` treats as its own sign) the child meets its **name**, its **sound**, a
**key word with a picture**, its **place in the alphabet** and its
**look-alike family**. Nothing has to be read; every question is spoken, Y
explains every answer, every round starts by saying what it is about.

## The games

| Game | Engine | Rounds | What the child does |
| --- | --- | --- | --- |
| Letter Names `a` | listen_pick | 7 | Hears a letter's name (with its key word, then alone), picks the letter among look-alikes. Rounds 1-5 go through the alphabet in five groups, 6-7 mix everything |
| Letter Sounds `b` | listen_pick | 4 | Hears three syllables that start alike («با، بو، بی») or a word, picks the letter of that sound. Round 4: letters that share one sound (س ص ث, ز ذ ض ظ, ت ط, ح ه, ا ع) |
| A Picture for Every Letter `c` | listen_pick | 6 | Sees the key picture and hears its word, picks the first letter; sees a letter, picks the picture. Round 6 uses second and third pictures |
| The Alphabet Row `d` | listen_pick | 5 | Sees a row of four letters with a gap and hears it («ثِ، جیم، خالی، حِ»), picks the missing letter; which letter comes after, which before |
| Alphabet Builder `e` | builder | 4 | Puts four or five letters into alphabet order, right to left: first with the order spoken, then only the first letter, then letters from far-apart places |
| Dots and Families `f` | sorter | 6 | Sorts letters by where the dots are (above, below, none), by how many dots (0 to 3), and into look-alike families (ب پ ت ث / ج چ ح خ / د ذ / ر ز ژ / س ش / ص ض / ط ظ / ع غ / ف ق / ک گ), also in their joined shapes |
| Letter Catch `g` | catch | 4 | Catches the called letter among its look-alikes; catches all letters that fit a rule (no dots, three dots, a family, one sound, the non-joining letters); catches the letter that comes next in the alphabet |
| Letter Pairs `h` | pairs | 6 | Letter to key picture (4 rounds), a speaking card that says a name to the letter (2 rounds) |
| Alphabet Journey `i` | journey | 7 | Six stops through the alphabet and a last stop for all of it: letter to picture, name among look-alikes, "it looks like جیم but has three dots", "دال، ذال، رِ: which comes next?", the letter's joined shape |

49 rounds, 778 items. Every game is a pool (`"draw"`): a round has 12 to 24
items and each play asks eight of them (five in the builder, six pairs), so a
round is not the same twice.

## Decisions

- **Letter names** are written exactly as `fa-2` writes them for the voice
  (بِ، پِ، تِ، ثِ، جیم، چِ، حِ، خِ، دال، ذال، رِ، زِ، ژِ، سین، شین، صاد، ضاد،
  طا، ظا، عین، غین، فِ، قاف، کاف، گاف، لام، میم، نون، واو، هِ، یا).
- **Key words** are the ones of `fa-1` and `fa-2`: آب، انار، بز، پشک، توت،
  ثمر، جاروب، چشم، حوض، خر، دست، روباه، زنبور، ژاله، سیب، شتر، صابون، ضعیف،
  طوطی، ظرف، عینک، غار، فیل، قلم، کتاب، گاو، لیمو، مار، نان، واسکت، هیزم، یخ.
  One exception: for ذ the key word with a picture is **ذره‌بین** (magnifying
  glass), because «ذره» (a speck) cannot be drawn. The word still starts with
  the syllables of «ذره».
- **ح and ه are both spoken "he"**, and the stand-in voice also merges ق and
  غ. A script check makes sure that two letters with one name never stand
  among the choices of one question, are never in the same catch item, and
  never lie on the table in the same pairs round. Where the name alone would
  not tell them apart the key word is said with it («حِ، مثل حوض»).
- **Letters that share a sound** (س ص ث; ز ذ ض ظ; ت ط; ح ه; ا ع) are never
  wrong choices for each other in a sound question or a first-letter question,
  because by ear both would be right. Round 4 of Letter Sounds teaches exactly
  this fact instead of hiding it.
- **Sounds** are given as three syllables («کا، کو، کی») because a synthetic
  voice cannot say a bare consonant. For آ and ا three words are used.
- **Dots**: ج and چ are sorted as "dots below" (their dot sits in the bowl of
  the letter standing alone and under the line when joined). ی is left out of
  the dot rounds (no dots alone, two below when joined). گ counts as "no dots";
  its second stroke is described as "one more stroke on top".
- **Pictures**: all from the library except three drawn for this pack:
  `fruit_branch` (ثمر), `magnifier` (ذره‌بین), `weak_plant` (ضعیف, a wilting
  seedling). «ظرف» uses the library's `bowl_empty`.
- **Repetition** was measured with a script over the sheets: no spoken
  question occurs more than twice in the pack, and no letter or picture is the
  right answer more than three times in one game.

## For the reviewer

1. **Hear the letter names and the syllable sounds.** «وا، وی», «یا، یو»,
   «ها، هو، هی», «ژا، ژو، ژی» and the like depend entirely on the voice.
2. Should ط and ظ be «طوی، ظوی»? Should ح and ه be «حِ جیمی» and «هِ دوچشمه»?
   (Same open question as in `fa-2`; change it in all three packs together.)
3. Is **ذره‌بین** acceptable as the picture word for ذ, **ضعیف** shown as a
   wilting seedling, **ثمر** as fruit on a branch, **ظرف** as a bowl?
4. The **order** taught is ا ب پ ت ث ج چ ح خ د ذ ر ز ژ س ش ص ض ط ظ ع غ ف ق ک
   گ ل م ن و ه ی. Confirm «و» before «ه» (Afghan school order).
5. "Dots below" for ج and چ, and leaving ی out of the dot rounds.
6. «خانواده» (family) for a group of look-alike letters, and the sentence
   "letters are like sisters and brothers".
7. The round "one sound, several letters" says ا and ع sound alike at the
   start of a word (انار، عینک). Acceptable for beginners?
8. The Alphabet Row shows a question mark «؟» for the gap. Check on the device
   that it reads as a gap.
9. Is a full alphabet too much beside level 1? The pack is optional for that
   reason; the local team decides per class.

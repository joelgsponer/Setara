# Teacher mode

A guide for the programme team and for whoever trains teachers. It describes
teacher mode as the code has it (`app/teacher/*.lua`), button by button.

**Read this first.** Teacher mode has been run on a PC only, by scripts and by
the AI that wrote it. No teacher has used it. The lessons, the Dari
instructions and the teaching tips were written by an AI (Claude) and have not
been reviewed by a Dari-speaking educator. The English voice is a stand-in
that nobody has listened to. Do not put it in front of a class before that
review.

## The idea

One handheld and a loudspeaker serve a class of up to 50. The teacher may
speak little or no English. The device supplies the correct English and a
ready lesson plan. The teacher runs the room: she points, mimes, organises
the children and decides when to move on. The screen tells her in Dari what
to do. The device never advances by itself.

Each lesson can be practised alone the evening before (Tonight's Preview), so
the teacher learns the English one lesson ahead of her class.

## Opening teacher mode

1. Go to the home screen (the valley).
2. Hold L and R together for two seconds. A ring fills in the middle of the
   screen while you hold.
3. The teacher menu opens with a chime.

On a PC, hold Q and W. In the browser version, use the "Teacher mode" button
under the screen.

There is no password. A child who holds both shoulder buttons gets in too.
Nothing in teacher mode can break the device or delete anything.

B leaves teacher mode. Start opens the pause menu, which in teacher mode has
one more row: the **class size** (1 to 80, starts at 30). Set it once. Quick
Check uses it.

## The menu

The top row shows today's lesson: its number and title. Below are the nine
tools in three rows of three.

| Where | Buttons |
| --- | --- |
| On the tools | D-pad moves, A opens a tool |
| Up from the first row of tools | Goes to the lesson row |
| On the lesson row | Left and right change today's lesson; down or A goes back to the tools |

The lesson number is remembered on the device. It moves on by one when a
lesson is finished in the Lesson Runner.

| | | |
| --- | --- | --- |
| 1 Lesson Runner | 2 Tonight's Preview | 3 Phrase Board |
| 4 Drill Master | 5 Class Games | 6 Story Time |
| 7 Station Timer | 8 Quick Check | 9 Teacher's Course |

In every tool: **B goes back**. X is "slowly" and Y is "the meaning in Dari"
wherever there is English to play. A bar at the bottom of each screen shows
the buttons that work there.

## The nine tools

### 1. Lesson Runner

One complete lesson, step by step. Each screen shows one line: what the
teacher does, in Dari, and usually an English phrase to play.

| Button | Does |
| --- | --- |
| A | Plays the English through the speaker. On a line with no English, goes to the next line. On a "tune" line, starts and stops the tune (for passing games). On a Quick Check line, opens the Quick Check |
| X | Plays the English slowly |
| Y | Shows and speaks the Dari meaning |
| Down | Next line |
| Up | Previous line |
| Right | Next step |
| Left | Previous step |
| Start | Pause menu (volume, class size) |
| B | Leave the lesson |

A timer counts up for each step and shows the suggested minutes next to it.
It informs and never stops anything.

After the last line the lesson is marked finished, the guide says so, and
today's lesson moves on by one. Leaving with B in the middle does not move it.

### 2. Tonight's Preview

The same lesson, alone, in about ten minutes. It lists every English phrase
of today's lesson once, including the replies. For each phrase the device
runs a fixed sequence by itself:

1. the phrase,
2. its meaning in Dari,
3. the phrase slowly,
4. "Now you say it", and a pause to say it aloud,
5. the phrase again.

| Button | Does |
| --- | --- |
| A | Runs the sequence again for this phrase |
| X | The phrase slowly, once |
| Y | The Dari meaning, once |
| Right or down | Next phrase |
| Left or up | Previous phrase |

### 3. Phrase Board

Classroom phrases to use all day, one press each. In the English 1 pack:
five pages of eight phrases. The page titles, in the AI's English
translation: Starting the lesson, Instructions, Working together, Praise and
encouragement, Ending the lesson.

| Button | Does |
| --- | --- |
| D-pad | Moves over the phrases (two columns) |
| A | Speaks the phrase in English |
| X | Speaks it slowly |
| Y | Speaks the Dari meaning |
| L, R | Previous page, next page |

### 4. Drill Master

Call and response with timed gaps, so that every child speaks many times. It
lists the drill lines of today's lesson.

Before starting:

| Button | Does |
| --- | --- |
| Up, down | Choose a drill |
| X | Hear it slowly |
| Y | Hear the Dari meaning |
| A | Start |

A running drill is a row of beats. The screen shows a picture of the room and
lights the half that speaks.

| Kind of drill | Beats |
| --- | --- |
| A phrase alone | Three times: the device says it, the whole class repeats. Then twice: the device says it, the class repeats row by row |
| A question with a reply | Three times: the device says it, the whole class repeats. Then the device models question and reply once. Then twice: the left half asks, the right half answers. Then twice: the right half asks, the left half answers |

The gaps are as long as the phrase needs (1.4 times its length plus 0.8
seconds).

While it runs:

| Button | Does |
| --- | --- |
| Right | Skip to the next beat |
| A or B | Stop |

### 5. Class Games

Five games for the whole class with one device. Up and down choose, A
starts, B goes back to the list.

| Game | What happens | Buttons |
| --- | --- | --- |
| Row quiz | The device asks questions from the lessons taught so far (their check and drill lines). Rows of the class are teams and collect points | A next question; X slowly; Y shows the meaning; left and right choose the row; up gives it a point, down takes one back; L and R set the number of rows (2 to 4, starts at 3) |
| Listen and Do | The device gives a command from the lessons so far ("Stand up"). The class does it | A next; X slowly; Y meaning |
| Picture bingo | The device calls a word of the English level and shows its picture. The last eight calls stay visible. The children need their own bingo cards; the app does not make them | A next; X slowly; Y meaning |
| Number caller | The device calls a number | A next; X slowly; left or right switch between 1 to 10 and 1 to 20 |
| Mental math | The device says a sum (plus or minus, within 10 or 20) | A speaks the answer, A again gives the next sum; X slowly; left or right switch between 10 and 20 |

"The lessons so far" means lesson 1 up to today's lesson.

### 6. Story Time

A list of every story on the device: the Dari, English and Garden stories of
all installed levels, including those of optional packs. Up and down choose,
A plays the story. It plays like the Story game (A turns the page, left goes
back; see [games.md](games.md#6-story-story)), without a warm-up. The class
answers the decisions together and the teacher presses.

The reference handheld has an HDMI output, so the pictures could be shown on
a TV where there is one. This has not been tried.

### 7. Station Timer

Splits the class into three groups that rotate through three stations: with
the teacher, with the devices, writing. Each group visits each station once.

| Button | Does |
| --- | --- |
| Left or down, right or up | Minutes per turn, 3 to 20 (starts at 10), before starting |
| A | Start. While running: pause and carry on |

When a turn is over, a chime sounds and the device says, in Dari, that the
groups change places. After three turns it says that all groups have
finished.

### 8. Quick Check

Five spoken questions at the end of a lesson. It opens from the menu, or by
pressing A on the check line in the Lesson Runner's last step.

For each question: the device asks, the children who know raise a hand, and
the teacher enters how many hands were right.

| Button | Does |
| --- | --- |
| Up, down | One more, one fewer |
| Right, left | Five more, five fewer |
| X | The question slowly |
| Y | The Dari meaning |
| A | Save this count and ask the next question |

The count starts at half the class size and cannot go above the class size.
After the fifth question the screen shows one to three stars and one of two
sentences: "The class is ready for the next lesson" (60 % or more right) or
"Repeat this lesson tomorrow".

**What Quick Check records.** One entry per lesson in `stats.json`, nothing
else:

| Field | Meaning |
| --- | --- |
| `times` | How often the check was completed for this lesson |
| `right` | The hands counted, added up over the questions and over all times |
| `size` | Class size times the number of questions, added up over all times |

No names, no faces, no record of which child answered, no date finer than
the week of use. A check that is left before the last question records
nothing. `tools/read_stats.py` prints it as "right/size (percent), taught N
times".

### 9. Teacher's Course

Two tabs. Left, right, L or R switch between them.

| Tab | Content | Buttons |
| --- | --- | --- |
| Lessons | Every lesson of the pack, in order | A opens that lesson as a Preview (tool 2), whatever today's lesson is |
| Tips | Short teaching tips in Dari audio | A plays the tip; on the tip's page A plays it again and B goes back |

The English 1 pack has ten tips. Their titles, in the AI's English
translation: Repetition with the whole class; Half the class and rows;
Practice the night before; Praising effort; Shy students; A little, every
day; Real things; Pair work without materials; The big ones help the small
ones; One sentence for home.

## The six steps of every lesson

Every lesson has the same shape, about 35 minutes.

| Step | Minutes | What happens |
| --- | --- | --- |
| 1. Hello | 3 | Greeting routine; the teacher says in Dari what today is about |
| 2. Listen | 5 | The device says the new words and phrases. The teacher points and mimes. The class only listens |
| 3. Say | 8 | Drills: the whole class repeats, then halves and rows |
| 4. Do | 8 | The class uses the language: commands, pairs, short exchanges |
| 5. Play | 8 | A game with the new words |
| 6. Goodbye | 3 | The five Quick Check questions, then the goodbye routine |

The minutes are the suggestion shown next to the timer. What exactly happens
in "Do" and "Play" differs from lesson to lesson; the Dari line on the screen
says it.

A line of a lesson is one of six kinds:

| Kind | What the teacher sees and does |
| --- | --- |
| `line` | An instruction and an English phrase to play |
| `drill` | The same; also offered in Drill Master |
| `command` | A command the class carries out; also used in Listen and Do |
| `check` | One of the five Quick Check questions |
| `tune` | The device plays a tune until A is pressed again |
| `note` | An instruction only, nothing to play |

## The 20 lessons of English level 1

Pack `teacher-en-1`, from `content/teacher/english-1/lessons.csv`. Each
lesson has five check questions. The lesson numbers match the units of the
learner pack `en-1` (see
[../content/english/1/syllabus.md](../content/english/1/syllabus.md)).

| # | Title |
| --- | --- |
| 1 | Hello! |
| 2 | Stand up, sit down |
| 3 | What's your name? |
| 4 | Boy and girl, yes and no |
| 5 | Numbers 1-5 |
| 6 | Numbers 6-10 |
| 7 | How old are you? |
| 8 | Classroom things 1 |
| 9 | Classroom things 2 |
| 10 | Commands 2 |
| 11 | Colours 1 |
| 12 | Colours 2 |
| 13 | Food |
| 14 | My friend |
| 15 | Commands 3 |
| 16 | How are you? |
| 17 | Big and small |
| 18 | Please and thank you |
| 19 | Review: my classroom |
| 20 | Review: I can speak English |

There are lesson packs for English 1 and English 2 (20 lessons each). Packs
follow each other: after lesson 20 of English 1, right on the lesson row
moves to lesson 1 of English 2, and left goes back. With more than one pack
installed the small number before the lesson number says which book it is.
The Phrase Board, the tips and the class games are those of the book the
teacher is in. There are no teacher lessons for other subjects yet.

## What else teacher mode records

All of it is anonymous and stays on the card. See
[privacy-and-safety.md](privacy-and-safety.md).

| What | Where |
| --- | --- |
| Minutes spent in teacher mode, per week | `stats.json`, `weeks` |
| How often each tool was opened | `stats.json`, `teacher.open_<tool>` |
| How often each lesson was started and finished | `teacher.lesson_<id>`, `teacher.done_<id>` |
| How often each lesson was previewed, and the highest lesson previewed | `teacher.preview_<id>`, `teacher.course_lesson` |
| How many tips were played | `teacher.tip` |
| Today's lesson number and the class size | `progress.json` |

## A half-day introduction for teachers (a suggestion)

**This part is a suggestion, not a tested plan.** The product spec names "a
half-day hands-on introduction" as a way to help teachers adopt the device;
it does not say what is in it. Nobody has run one. The local team knows the
teachers and should change it freely.

| Time | What | Why |
| --- | --- | --- |
| 20 min | The device in the hand: on and off, charging, the speaker cable, volume. The button tutorial. Let each teacher play one children's game | To lose the fear of breaking it |
| 20 min | Open teacher mode. Set the class size. Find today's lesson | The way in |
| 40 min | Tonight's Preview of lesson 1, each teacher alone or in pairs, saying the phrases aloud | This is how she will prepare every evening |
| 60 min | Lesson Runner, lesson 1, in full. One teacher teaches, the others are the class. Swap for lesson 2 | The six steps, the timer, A, X and Y |
| 20 min | Drill Master with the room split into halves | The largest change from reading aloud to the class |
| 20 min | Quick Check with raised hands. Talk about what it records and what it does not | Trust: it counts hands, not children |
| 20 min | Phrase Board, one Class Game, Station Timer | Tools for the rest of the day |
| 20 min | What to do when something goes wrong; who to ask; what the team would like to hear back at the next visit | Feedback |

Things the trainer should say plainly: the device does not replace her; the
timer is not a test; a wrong button never breaks anything; B always goes
back.

## My class (Y in the teacher menu)

One list, most useful first:

- **Today's lesson**: the learner games of the unit that belongs to the
  lesson on the lesson row. A starts the round on the loudspeaker, so the
  class can play it together right after the lesson.
- **Hard for the class**: the rounds with the fewest first-try answers on
  this device (at least eight answers given, under 80 % right), with a bar.
  A starts the round again.
- **Quick Check**: the lessons whose check went worst, with a bar.

These are counts for the device, never for a child.

## Teacher's guide (Teacher's Course, third tab)

For every subject and level a guide in chapters: the goal, what the teacher
should know, how to explain it, figures, examples, common mistakes, class
activities, the games that practise it, how to check. A reads the page
aloud, left and right turn pages. The same guides print with
`python3 tools/guide_book.py` (add `--english` for reviewers).

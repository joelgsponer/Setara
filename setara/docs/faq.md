# Questions and answers

Short, honest answers for newcomers, funders and people who train teachers.
Where an answer rests on the product spec rather than on the code, it says
so.

## 1. What is Setara, in one paragraph?

An offline learning app ("star" in Dari) for cheap Linux game handhelds, for
village classrooms in Afghanistan. One device with a loudspeaker lets a
teacher with little English run an English lesson for up to 50 children.
Children can also play alone or in pairs: English, Dari reading, math, and
health and environment. Everything is spoken, so a child who cannot read can
use it.

## 2. Is it ready to use?

No. The software runs on a PC and in a browser. It has not been run on a
handheld yet. Nobody has listened to the generated speech. All content was
written by an AI and has not been reviewed by a Dari-speaking educator, a
health professional or the local team. See question 12.

## 3. Why a game handheld and not a tablet or a phone?

What the spec and the code give as reasons for the handheld:

- **Price.** CHF 35 to 50 per device (spec estimate).
- **Buttons.** Eight buttons, no typing, no keyboard, no accounts. A child
  who has never used a computer answers with one press of the D-pad.
- **One simple card.** The whole product is a folder on an SD card,
  identical on every device. A dead card is replaced by copying the folder
  again.
- **Open system.** The handhelds run Linux firmwares that can start a LÖVE
  app, and the same app runs on a PC for authoring and testing.
- **A TV where there is one.** The reference device has HDMI out.

The spec does not contain a comparison with tablets or phones, so this page
does not claim one. The choice of a handheld is itself still to be proven:
running on the two test devices is the first open step ("phase 0").

## 4. Why no internet?

Because the classrooms have none. The spec assumes no connectivity in class
and at best a weak phone hotspot at a teacher's home in some weeks. So
version 1 ships everything on the card and updates arrive as files on a
card. A second reason is safety: a device that never connects cannot send
anything about anyone. Direct updates are left for a later version.

## 5. Does it replace the teacher?

No, and it is designed not to. In teacher mode the device supplies the
correct English and a lesson plan; the teacher runs the room. The lesson
never advances by itself, and the timer only informs. The device has no
microphone and cannot hear or judge a child. Each lesson has a private
preview so the teacher can learn the English the evening before. See
[teacher-mode.md](teacher-mode.md). Whether teachers take to it is untested.

## 6. Why is everything spoken?

Many of the children cannot read yet, and the teachers may be unsure of
English pronunciation. So every instruction, word and question has audio,
and nothing may depend on reading. The builder refuses a question without
speech. X repeats slowly; Y explains in Dari.

## 7. Which devices?

The spec names two to test: the Anbernic RG35XX H (reference) and the R36S
(budget). The app is drawn for a 640×480 screen. Neither device has been
tried. The app also runs on any PC with LÖVE 11 (Linux has
been used; a Windows launcher is included but was not tested for these
docs) and in a browser. See [device.md](device.md) and
[hosting.md](hosting.md).

## 8. How much does a classroom cost?

Estimates from the product spec, in approximate retail prices of November
2026. The spec itself says they "need a real quote".

| Item | Estimate |
| --- | --- |
| One handheld | CHF 35 to 50 (RG35XX H 45 to 50, R36S 30 to 40) |
| Classroom kit: one device, one loudspeaker and charging | roughly CHF 90 to 130 |
| Each extra learner device | CHF 30 to 50 |

Not in these figures: transport, spares, the work of reviewing content,
recording or buying voices, illustration, training teachers and field
visits.

## 9. Is the content reviewed?

No. See question 2. The review the spec asks for: a Dari-speaking educator
reads and hears every text; a fluent English speaker spot-checks the audio;
a local reviewer approves every picture of a person; someone qualified
checks the health content; a trial with real children. None of this has
happened. The first-aid pack must not be used before a health professional
has checked it. Details in [content-overview.md](content-overview.md) and
[privacy-and-safety.md](privacy-and-safety.md).

## 10. What does it store about children?

Nothing about any child. The device keeps stars per round (for the device,
not per child) and anonymous counts such as minutes per week and plays per
round. No names, no photos, no recordings, no location, nothing finer than
the week. Nothing is sent anywhere. The exact fields are in
[privacy-and-safety.md](privacy-and-safety.md).

## 11. Can it be translated to Pashto, or another language?

The engines do not care about the language: content is data, and the Dari
shaping in the builder handles Arabic-script text. Pashto has letters that
Dari does not; the builder would report any letter the device font cannot
draw, and whether the font and the shaper cover Pashto fully has not been
tried. The work is in the content: translating and reviewing every sheet,
a Pashto voice, new letter and reading games (the Dari reading packs teach
the Dari alphabet and cannot be translated word for word), and the app's
own strings in `content/core/strings.csv`. The spec notes that Pashto
"changes nothing in the engine but doubles recording work". The licences
(MIT for code, CC BY-SA 4.0 for content) allow it.

## 12. How is new content added?

1. Write rows in CSV sheets under `content/` (one folder per pack, one sheet
   per game). The format is in [authoring.md](authoring.md).
2. Check: `cd builder && python3 -m setara_builder.cli validate`.
3. Build the packs and try them on a PC
   ([getting-started.md](getting-started.md)).
4. Have it reviewed (question 9).
5. Raise the pack's `version`, build, and copy the zip into `setara/update/`
   on each card. The app checks and installs it at the next start.

No programming is needed unless a new kind of game is wanted.

## 13. Why is the audio Ogg Vorbis and not Opus?

The spec asked for Opus at 24 kbit/s. LÖVE 11, the engine the app runs on,
cannot decode Opus. So the builder writes Ogg Vorbis, mono, 22.05 kHz,
quality 2 (about 32 kbit/s). The packs came out at 7 to 16 MB, which is
about the size the spec budgeted (one pack is slightly over its 15 MB).

## 14. Why is the Dari text shaped at build time?

Dari is written from right to left in joined letters. LÖVE 11 neither joins
Arabic-script letters nor lays text out from right to left. So the builder
does it once on a PC: it picks the joined form of every letter, puts each
line in drawing order and breaks the lines for the screen. The device only
draws ready glyphs. This keeps the app small and the same everywhere. It is
also why the app must stay on LÖVE 11: LÖVE 12 shapes text by itself and
would reverse the prepared lines. The result has been checked on PC
screenshots only, not by a Dari reader on a device.

## 15. Whose voices are these?

Machine voices. The builds so far use free stand-in voices (piper): two
American English voices and one Iranian Persian man's voice. Afghan Dari
sounds different, and a woman's voice is the intended default. Nobody has
listened to the clips. The spec plans ElevenLabs voices, with human
recording where they fall short; that path is written and has never been
run. A Dari speaker has to judge any voice before children hear it. See
[speech.md](speech.md).

## 16. Who wrote the content, and can an AI's lessons be trusted?

Claude, an AI model, wrote all of it, following a product spec and fact
sheets. It should be treated as a first draft by an author who does not
speak Dari natively, has never been in the classroom and can be wrong with
confidence. That is why the review gates exist and why this documentation
repeats the warning. The math is the exception in one respect: the sums are
computed and checked by a program.

## 17. What happens when something breaks in the village?

The design goals, all tested on a PC only: a damaged pack is ignored and the
old one stays; a damaged save file resets only that file; a crash restarts
the app; a dead card is replaced by copying the card folder to a new card.
See the last section of [device.md](device.md).

## 18. How can I help?

Review Dari, review the health content, look at the pictures, test on a
device, translate, or write code. See
[../../CONTRIBUTING.md](../../CONTRIBUTING.md).

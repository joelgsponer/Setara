#!/usr/bin/env python3
"""Make the introduction video from a recorded tour of the app.

  tools/film/make.py            record the tour, then build dist/setara-intro.mp4
  tools/film/make.py --reuse    build again from the last recording

The footage is the real app playing by itself in English mode (tour.lua).
Its sound is rebuilt from the log of what the app played. Title cards are
drawn here and narrated with the builder's stand-in English voice.

Needs: built packs and card folder, LÖVE (SETARA_LOVE), xvfb, ffmpeg, numpy,
Pillow, and the piper voice from builder/get_voices.sh.
"""
import json
import os
import subprocess
import sys
import wave
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "dist" / "film"
SAVE = WORK / "save"
FRAMES = SAVE / "love" / "setara" / "film"
OUT = ROOT / "dist" / "setara-intro.mp4"
FONTS = ROOT / "app" / "assets" / "fonts"
RATE, FPS = 22050, 30
W, H = 1280, 720

INK, PAPER, BG = "#3b2f2f", "#fffbf0", "#f6eedc"
GOLD, TEAL, ORANGE, BLUE, PURPLE, GREEN = "#f2b705", "#2f6f73", "#e07a3f", "#3f7fbf", "#8e5bb5", "#4e9a51"

# The film, in order. A card is narrated; a clip shows the app from a mark of
# the tour: (mark, seconds after the mark, seconds shown).
FILM = [
    ("card", "title", GOLD, "Setara", ["A learning handheld", "for village classrooms"],
     "This is Setara. It means star, in Dari. It is one small learning app, on a game handheld that costs less "
     "than fifty francs, built for village classrooms in Afghanistan."),
    ("card", "list", ORANGE, "The classroom as it is",
     ["One teacher with little training", "Up to 50 children of mixed ages", "No computer, little power", "No internet"],
     "We start from the classroom as it is. One teacher, with little training. Up to fifty children of mixed ages. "
     "No computer, little power, and no internet."),
    ("card", "list", TEAL, "The kit",
     ["One handheld, CHF 35 to 50", "One loudspeaker", "A small solar panel", "Everything on one memory card",
      "No names, no accounts, no personal data"],
     "The kit is one handheld, one loudspeaker, and a small solar panel. About a hundred francs for a classroom. "
     "Everything is on one memory card. It never needs a connection, and it stores no names and no personal data."),
    ("card", "list", BLUE, "For children",
     ["Four subjects in levels", "Every word and question is spoken", "Eight buttons, no typing",
      "No lives, no game over, no ranking"],
     "Everything is spoken. A child who cannot read yet can use it from the first minute, with eight buttons and "
     "no typing. What you see next is the real app, playing by itself. The English captions are a test mode. "
     "The children hear Dari."),
    ("clip", "tutorial", 0, 9, BLUE, "First minute",
     ["A spoken tour of the buttons.", "The child learns them by pressing them.", "No text to read."]),
    ("clip", "valley", 0, 10, BLUE, "The valley",
     ["Four places, four subjects:", "English, Dari reading,", "math, health and environment."]),
    ("clip", "english", 5, 20, ORANGE, "English",
     ["Hear a word, press towards", "the picture.", "", "A wrong answer is never punished:", "it comes back later."]),
    ("clip", "dari", 6, 18, BLUE, "Dari reading",
     ["Each Dari letter changes shape", "at the start, middle and end", "of a word.", "",
      "The step where most early", "readers stumble."]),
    ("clip", "math", 6, 16, PURPLE, "Math",
     ["Hop along the number line.", "", "After the answer the child", "sees why it is right."]),
    ("clip", "health", 5, 16, GREEN, "Health",
     ["Put the steps of handwashing", "in order.", "", "Knowledge a child can use", "at home the same day."]),
    ("clip", "story", 7, 22, GREEN, "Stories with choices",
     ["Which water is safe to drink?", "", "A wrong choice shows what", "happens, gently, and the", "story asks again."]),
    ("clip", "firstaid", 6, 20, GREEN, "First aid",
     ["A burn: what comes first?", "", "Away from the heat, cool water for a long time, a clean cloth, and the clinic if it is big."]),
    ("clip", "lifesupport", 5, 20, GREEN, "When someone collapses",
     ["For older children and teachers.", "", "A small child's job is said first: run and bring an adult."]),
    ("clip", "world", 5, 18, GREEN, "The wider world",
     ["From the globe to the seven continents, with maps drawn from real map data."]),
    ("clip", "basel", 5, 18, GREEN, "And where it comes from",
     ["The journey ends in Basel, in Switzerland, where these lessons are made.", "",
      "An optional pack: the local team decides."]),
    ("clip", "pair", 1, 13, PURPLE, "Two children, one device",
     ["One uses the D-pad,", "the other the four buttons.", "", "Devices are shared:", "every game works in pairs."]),
    ("clip", "grows", 0, 6.5, GOLD, "The valley grows",
     ["Stars repair and grow", "the valley for the whole class.", "", "No profiles, no passwords."]),
    ("card", "list", TEAL, "For the teacher",
     ["A correct English voice", "A complete lesson, step by step", "Private practice the evening before",
      "She stays the teacher"],
     "The same device turns into a co teacher. It gives a teacher with no English a correct voice, and a complete "
     "lesson, step by step. She stays the teacher."),
    ("clip", "teacher", 0, 6, TEAL, "Teacher mode",
     ["Nine tools for a class of", "up to 50, with one device", "and a loudspeaker."]),
    ("clip", "lesson", 0, 20, TEAL, "Lesson Runner",
     ["The screen tells her what", "to do, in Dari.", "", "One press plays the English", "through the loudspeaker.", "",
      "Every lesson has the same", "six steps."]),
    ("clip", "drill", 2, 12, TEAL, "Drill Master",
     ["The speaker says it,", "the class repeats.", "", "Then one half of the room asks", "and the other half answers."]),
    ("clip", "check", 0, 12, TEAL, "Quick Check",
     ["Five questions at the end.", "She enters how many hands", "were right.", "",
      "Anonymous counts only:", "never a child's name."]),
    ("clip", "tools", 0, 11, TEAL, "More tools",
     ["Phrase Board, class games,", "story time, a timer for", "working in groups."]),
    ("card", "list", PURPLE, "Content is data",
     ["Lessons and levels are spreadsheets", "One command builds speech, pictures and Dari text",
      "450 rounds, 600 pictures, 20 lessons so far", "Updates travel on a memory card"],
     "Games are data. Lessons and levels are written as spreadsheets, and one command turns them into packs, "
     "with speech, pictures, and Dari text. So far there are four hundred and fifty rounds, six hundred pictures, and twenty classroom lessons. New content travels on a memory card."),
    ("card", "list", ORANGE, "Where we are",
     ["The software runs on a computer today", "Not yet tried on the handheld", "Content is a first draft",
      "Voices are placeholders",
      "Next: test devices, Dari-speaking reviewers, a real classroom"],
     "Where are we? The software runs on a computer today. It has not yet run on the handheld. The content is a "
     "first draft, and the voices are placeholders. Next come two test devices, and review by Dari speaking "
     "teachers and a health professional, before any child uses it."),
    ("card", "title", GOLD, "Setara", ["Open code, open content", "Free to reuse and translate"],
     "Setara is open. The code and the content are free for others to reuse, and to translate."),
]


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ("Andika-Bold.ttf" if bold else "Andika-Regular.ttf")), size)


def wrap(text, fnt, width):
    """Break a text into lines that fit a width in pixels."""
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if line and fnt.getlength(trial) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


def run(cmd, **kw):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, **kw)


# -- recording -------------------------------------------------------------------

def record():
    packs = SAVE / "love" / "setara" / "packs"
    packs.parent.mkdir(parents=True, exist_ok=True)
    if FRAMES.exists():
        for f in FRAMES.iterdir():
            f.unlink()
    src = ROOT / "dist" / "card" / "setara" / "data" / "love" / "setara" / "packs"
    packs.mkdir(exist_ok=True)
    for z in src.glob("*.zip"):
        (packs / z.name).write_bytes(z.read_bytes())
    for name in ("progress.json", "progress.json.bak", "stats.json", "stats.json.bak"):
        p = SAVE / "love" / "setara" / "data" / name
        if p.exists():
            p.unlink()
    env = dict(os.environ, SETARA_LOCALE="en", SETARA_RECORD="film", SETARA_SEED="11")
    subprocess.run([str(ROOT / "tools" / "shoot.sh"), str(ROOT / "tools" / "film" / "tour.lua"), "1", str(SAVE)],
                   check=True, env=env)


def read_log():
    marks, sounds = {}, []
    for line in (FRAMES / "sounds.tsv").read_text().splitlines():
        frame, kind, name = line.split("\t")
        if kind == "mark":
            marks[name] = int(frame)
        else:
            sounds.append((int(frame), kind, name))
    return marks, sounds


# -- sound -----------------------------------------------------------------------

def sfx(name):
    """The app's own effects, synthesised the same way as app/core/sfx.lua."""
    c4, e4, a4 = 261.6, 329.6, 440.0
    c5, d5, e5, g5, a5, c6 = 523.3, 587.3, 659.3, 784.0, 880.0, 1046.5
    defs = {
        "move": ([(e5, 0.04, 0.25)], 30), "right": ([(g5, 0.09, 0.5), (c6, 0.22, 0.5)], 8),
        "wrong": ([(e4, 0.12, 0.4), (c4, 0.2, 0.4)], 7),
        "star": ([(c5, 0.08, 0.5), (e5, 0.08, 0.5), (g5, 0.08, 0.5), (c6, 0.3, 0.5)], 6),
        "flip": ([(a4, 0.05, 0.3)], 25), "hop": ([(d5, 0.06, 0.4), (a5, 0.08, 0.4)], 14),
        "buzz": ([(a5, 0.07, 0.5), (a5, 0.07, 0.5)], 12), "chime": ([(e5, 0.3, 0.5), (c5, 0.3, 0.5), (g5, 0.6, 0.5)], 3),
        "done": ([(c5, 0.12, 0.5), (e5, 0.12, 0.5), (g5, 0.12, 0.5), (e5, 0.12, 0.5), (c6, 0.4, 0.5)], 4),
        "tick": ([(c6, 0.02, 0.2)], 60),
    }
    if name not in defs:
        return np.zeros(1, np.float32)
    notes, decay = defs[name]
    out = []
    for f, d, v in notes:
        n = int(d * RATE)
        t = np.arange(n) / RATE
        env = np.minimum(1, t * 200) * np.exp(-t * decay) * np.minimum(1, (n - np.arange(n)) / (0.01 * RATE))
        out.append((np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * v * env)
    return np.concatenate(out).astype(np.float32) * 0.5


_clips = {}


def clip(path):
    """A speech clip of a pack ('p/en-1/en/apple-x.ogg') as samples."""
    if path not in _clips:
        _, pack, rel = path.split("/", 2)
        data = zipfile.ZipFile(ROOT / "packs" / f"{pack}.zip").read(rel)
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", str(RATE), "pipe:1"],
                             input=data, capture_output=True, check=True).stdout
        _clips[path] = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    return _clips[path]


def soundtrack(sounds, frames):
    track = np.zeros(int(frames / FPS * RATE) + RATE, np.float32)
    speech = [(f, k, n) for f, k, n in sounds if k in ("clip", "stop")]
    for i, (frame, kind, name) in enumerate(speech):
        if kind != "clip":
            continue
        data = clip(name)
        start = int(frame / FPS * RATE)
        if i + 1 < len(speech):  # the next clip, or a stop, cuts this one off
            data = data[: max(0, int(speech[i + 1][0] / FPS * RATE) - start)]
        end = min(len(track), start + len(data))
        track[start:end] += data[: end - start]
    for frame, kind, name in sounds:
        if kind == "sfx":
            data = sfx(name)
            start = int(frame / FPS * RATE)
            end = min(len(track), start + len(data))
            track[start:end] += data[: end - start]
    return np.clip(track, -1, 1)


def write_wav(path, samples):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((samples * 32767).astype(np.int16).tobytes())


def narrate(text, path):
    from piper import PiperVoice, SynthesisConfig
    global _voice
    try:
        _voice
    except NameError:
        _voice = PiperVoice.load(str(ROOT / "builder" / "voices" / "en_US-amy-medium.onnx"))
    with wave.open(str(path), "wb") as w:
        _voice.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=1.08))


# -- pictures --------------------------------------------------------------------

def backdrop(marks):
    """The valley, softened: the background of every card."""
    frame = Image.open(FRAMES / f"f{marks['grows'] + 150:06d}.png").convert("RGB")
    view = frame.crop((40, 0, 600, 420)).resize((W, int(W * 420 / 560)), Image.LANCZOS)
    view = view.crop((0, (view.height - H) // 2, W, (view.height - H) // 2 + H)).filter(ImageFilter.GaussianBlur(10))
    return Image.blend(view, Image.new("RGB", (W, H), BG), 0.72)


def card(kind, colour, title, lines, base):
    img = base.copy()
    d = ImageDraw.Draw(img)
    if kind == "title":
        d.text((W / 2, 250), title, font=font(150, True), fill=INK, anchor="mm")
        d.rounded_rectangle((W / 2 - 90, 345, W / 2 + 90, 357), 6, fill=colour)
        for i, line in enumerate(lines):
            d.text((W / 2, 420 + i * 62), line, font=font(46), fill=INK, anchor="mm")
    else:
        d.rounded_rectangle((90, 70, W - 90, H - 70), 28, fill=PAPER, outline=INK, width=5)
        d.rounded_rectangle((90, 70, W - 90, 190), 28, fill=colour)
        d.rectangle((90, 160, W - 90, 190), fill=colour)
        d.line((90, 190, W - 90, 190), fill=INK, width=5)
        d.rounded_rectangle((90, 70, W - 90, H - 70), 28, outline=INK, width=5)
        d.text((140, 130), title, font=font(60, True), fill="white", anchor="lm")
        # the largest size at which every point fits the card, wrapped where needed
        for size in (42, 38, 34, 30, 26):
            fnt = font(size)
            rows = [wrap(line, fnt, W - 90 - 196 - 50) for line in lines]
            height = sum(len(r) for r in rows) * size * 1.3 + (len(rows) - 1) * size * 0.55
            if height <= 400:
                break
        y = 230 + (410 - height) / 2
        for row in rows:
            d.ellipse((150, y + size * 0.65 - 9, 168, y + size * 0.65 + 9), fill=colour)
            for part in row:
                d.text((196, y), part, font=fnt, fill=INK, anchor="la")
                y += size * 1.3
            y += size * 0.55
    return img


def _groups(lines):
    out, cur = [], []
    for line in lines:
        if line:
            cur.append(line)
        elif cur:
            out.append(cur)
            cur = []
    return out + ([cur] if cur else [])


def panel(colour, title, lines):
    """The frame around the footage: the app on the left, a note on the right."""
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    d.rectangle((960, 0, W, H), fill=PAPER)
    d.rectangle((960, 0, W, 96), fill=colour)
    d.text((982, 48), title, font=font(30 if len(title) < 16 else 23, True), fill="white", anchor="lm")
    fnt, y = font(22), 126
    for para in "\n".join(" ".join(g) for g in _groups(lines)).split("\n"):
        for part in wrap(para, fnt, 320 - 44):
            d.text((982, y), part, font=fnt, fill=INK, anchor="la")
            y += 31
        y += 16
    d.text((984, H - 34), "Setara, running by itself", font=font(17), fill="#8a7b6a", anchor="lm")
    return img


# -- assembling ------------------------------------------------------------------

ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2"]


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    if "--reuse" not in sys.argv or not (FRAMES / "sounds.tsv").exists():
        record()
    marks, sounds = read_log()
    last = max(int(p.stem[1:]) for p in FRAMES.glob("f*.png"))
    track = soundtrack(sounds, last)
    base = backdrop(marks)
    parts = []
    for n, item in enumerate(FILM):
        out = WORK / f"part{n:02d}.mp4"
        if item[0] == "card":
            _, kind, colour, title, lines, text = item
            png, wav = WORK / f"card{n:02d}.png", WORK / f"card{n:02d}.wav"
            card(kind, colour, title, lines, base).save(png)
            narrate(text, wav)
            with wave.open(str(wav)) as w:
                length = w.getnframes() / w.getframerate() + 1.1
            run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-t", f"{length:.2f}", "-i", str(png),
                 "-i", str(wav), "-af", f"adelay=450:all=1,apad=whole_dur={length:.2f}",
                 "-vf", f"fade=t=in:d=0.3,fade=t=out:st={length - 0.3:.2f}:d=0.3", "-t", f"{length:.2f}", *ENC, str(out)])
        else:
            _, mark, after, seconds, colour, title, lines = item
            first = marks[mark] + int(after * FPS)
            count = min(int(seconds * FPS), last - first)
            png, wav = WORK / f"panel{n:02d}.png", WORK / f"clip{n:02d}.wav"
            panel(colour, title, lines).save(png)
            a = int(first / FPS * RATE)
            write_wav(wav, track[a: a + int(count / FPS * RATE)])
            run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(png),
                 "-framerate", str(FPS), "-start_number", str(first), "-i", str(FRAMES / "f%06d.png"),
                 "-i", str(wav), "-frames:v", str(count),
                 "-filter_complex", "[1:v]scale=960:720:flags=lanczos[app];[0:v][app]overlay=0:0",
                 "-map", "2:a", *ENC, str(out)])
        parts.append(out)
        print(f"  {out.name}: {item[0]} {item[3] if item[0] == 'card' else item[5]}")
    listing = WORK / "parts.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy",
         "-movflags", "+faststart", str(OUT)])
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_format", "-of", "json", str(OUT)],
                                     capture_output=True, text=True).stdout)
    print(f"{OUT}  {float(info['format']['duration']):.0f} s  {OUT.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

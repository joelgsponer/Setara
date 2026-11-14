"""Turns the authored sources in content/ into content packs.

See docs/authoring.md for the source formats and docs/level-format.md and
docs/pack-format.md for what comes out.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from . import images, shaping
from .tts import Speech

ENGINES = (
    "listen_pick", "pairs", "catch", "builder", "say_it",
    "story", "journey", "market", "duel", "sorter",
)
SUBJECTS = {"en": 6, "fa": 6, "math": 6, "garden": 4}
STEPS = ("hello", "listen", "say", "do", "play", "goodbye")
LINE_KINDS = ("line", "drill", "check", "command", "tune", "note")
NAME = re.compile(r"^[a-z0-9_]+$")
FORMAT = 1


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def read_csv(path: Path) -> list[dict]:
    """Rows as dicts with a _row number. Blank rows and # comments are skipped."""
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for n, row in enumerate(csv.DictReader(f), start=2):
            clean = {(k or "").strip(): (v or "").strip() for k, v in row.items() if k}
            first = next(iter(clean.values()), "")
            if not any(clean.values()) or first.startswith("#"):
                continue
            clean["_row"] = n
            rows.append(clean)
    return rows


def split(cell: str) -> list[str]:
    return [p.strip() for p in cell.split("|") if p.strip()]


class Pack:
    """One pack being built: collects files, audio, pictures and problems."""

    def __init__(self, src: Path, content: Path, speech: Speech, report: Report, make_audio: bool):
        self.src = src
        self.content = content
        self.speech = speech
        self.report = report
        self.make_audio = make_audio
        self.meta = json.loads((src / "pack.json").read_text("utf-8"))
        self.id = self.meta["pack"]
        self.files: dict[str, bytes | Path] = {}
        self.pictures: set[str] = set()
        self.where = str(src.relative_to(content))

    # -- building blocks ------------------------------------------------------

    def say(self, lang: str, text: str, where: str, slow: bool = False) -> list[str]:
        """Register a spoken text; returns the clip list for the level file."""
        text = " ".join(text.split())
        if not text:
            return []
        if lang == "fa" and not shaping.has_arabic(text):
            self.report.warn(where, f"Dari speech has no Dari letters: {text!r}")
        if lang == "en" and shaping.has_arabic(text):
            self.report.error(where, f"English speech contains Dari letters: {text!r}")
        name = self.speech.name(lang, text)
        if name not in self.files:
            self.files[name] = self.speech.render(lang, text) if self.make_audio else b""
        if slow:
            slow_name = self.speech.name(lang, text, slow=True)
            if slow_name not in self.files:
                self.files[slow_name] = self.speech.render(lang, text, slow=True) if self.make_audio else b""
        return [name]

    def fa(self, text: str, where: str, wrap: bool = True) -> list[str]:
        """Dari text to draw: shaped lines."""
        if not text:
            return []
        lines = shaping.shape(text) if wrap else [shaping.shape_line(text)]
        for line in lines:
            missing = shaping.missing_glyphs(line)
            if missing:
                self.report.error(where, f"no glyph for {missing} in {text!r}")
        return lines

    def thing(self, spec: str, where: str) -> dict | None:
        """Parse the 'thing' notation used for choices, tiles, cards, baskets."""
        spec = spec.strip()
        if not spec:
            self.report.error(where, "empty thing")
            return None
        if spec == "snd":
            return {"id": "snd", "snd": True}
        if spec.startswith("t:"):
            return {"id": spec, "t": spec[2:].strip()}
        if spec.startswith("f:"):
            return {"id": spec, "fa": self.fa(spec[2:].strip(), where, wrap=False)[0]}
        if spec.startswith("lf:"):
            try:
                _, letter, form = spec.split(":")
                return {"id": spec, "fa": shaping.letter_form(letter, form), "big": True}
            except (ValueError, KeyError):
                self.report.error(where, f"bad letter form {spec!r}, want lf:<letter>:<alone|start|middle|end>")
                return None
        count = None
        name = spec
        if spec.startswith("p:"):
            m = re.match(r"^p:([a-z0-9_]+)\*(\d+)$", spec)
            if not m:
                self.report.error(where, f"bad picture count {spec!r}, want p:<name>*<n>")
                return None
            name, count = m.group(1), int(m.group(2))
            if not 1 <= count <= 20:
                self.report.error(where, f"{spec!r}: count must be 1 to 20")
        if not NAME.match(name):
            self.report.error(where, f"bad thing {spec!r}: picture names are lowercase letters, digits and _")
            return None
        self.pictures.add(name)
        thing = {"id": spec, "img": f"img/{name}.png"}
        if count:
            thing["n"] = count
        return thing

    def things(self, cell: str, where: str) -> list[dict]:
        return [t for t in (self.thing(s, where) for s in split(cell)) if t]

    def prompt(self, row: dict, where: str, slow: bool = True) -> list[str]:
        """Dari first, then English, when a row gives both."""
        return self.say("fa", row.get("say_fa", ""), where, slow) + self.say("en", row.get("say_en", ""), where, slow)

    def add_json(self, path: str, data) -> None:
        self.files[path] = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    # -- writing --------------------------------------------------------------

    def add_pictures(self, strict: bool) -> None:
        for name in sorted(self.pictures):
            svg = self.content / "pictures" / f"{name}.svg"
            if svg.exists():
                try:
                    self.files[f"img/{name}.png"] = images.render(name, svg)
                    continue
                except Exception as exc:  # a broken drawing must not stop the build
                    self.report.error(f"pictures/{name}.svg", f"cannot render: {exc}")
            elif strict:
                self.report.error(self.where, f"missing picture: pictures/{name}.svg")
            else:
                self.report.warn(self.where, f"missing picture: pictures/{name}.svg (placeholder used)")
            self.files[f"img/{name}.png"] = images.placeholder(name)

    def write(self, out_dir: Path, manifest: dict) -> Path:
        blobs = {p: (v.read_bytes() if isinstance(v, Path) else v) for p, v in self.files.items()}
        manifest["files"] = {p: "sha256:" + hashlib.sha256(b).hexdigest() for p, b in sorted(blobs.items())}
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"{self.id}.zip"
        with zipfile.ZipFile(out, "w") as z:
            def put(path: str, data: bytes, compress: bool) -> None:
                info = zipfile.ZipInfo(path, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
                z.writestr(info, data)

            put("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=1).encode("utf-8"), True)
            for path, data in sorted(blobs.items()):
                put(path, data, path.endswith(".json"))
        return out


# -- learner packs ---------------------------------------------------------------


def _lp_item(pack: Pack, row: dict, where: str) -> dict | None:
    """A listen-and-pick style question. Shared by listen_pick, journey, duel."""
    item: dict = {"prompt_audio": pack.prompt(row, where)}
    if not item["prompt_audio"] and not row.get("show"):
        pack.report.error(where, "needs say_en or say_fa (every question is spoken)")
    if row.get("show"):
        item["show"] = pack.thing(row["show"], where)
    answer = pack.thing(row.get("answer", ""), where)
    if not answer:
        return None
    item["answer"] = answer["id"]
    item["choices"] = [answer] + pack.things(row.get("distractors", ""), where)
    help_fa = row.get("help_fa", "")
    if help_fa:
        item["help_audio"] = pack.say("fa", help_fa, where)
    if row.get("hop"):
        if not re.match(r"^\d+[+-]\d+$", row["hop"]):
            pack.report.error(where, f"bad hop {row['hop']!r}, want for example 3+2 or 7-3")
        item["hop"] = row["hop"]
    if row.get("tags"):
        item["tags"] = split(row["tags"])
    return item


def _fill_distractors(pack: Pack, items: list[dict], pool: list[dict], where: str, seed: str) -> None:
    """Give every question up to three wrong choices, drawn from its round first."""
    rng = random.Random(seed)
    for item in items:
        if len(item["choices"]) > 4:
            pack.report.error(where, f"more than four choices for {item['answer']!r}")
            item["choices"] = item["choices"][:4]
        if len(item["choices"]) >= 4:
            continue
        have = {c["id"] for c in item["choices"]}
        kind = _kind(item["choices"][0])
        near = [i["choices"][0] for i in items if i["answer"] not in have and _kind(i["choices"][0]) == kind]
        far = [c for c in pool if c["id"] not in have and _kind(c) == kind]
        for source in (near, far):
            source = list({c["id"]: c for c in source}.values())
            rng.shuffle(source)
            for cand in source:
                if len(item["choices"]) >= 4:
                    break
                if cand["id"] not in have:
                    item["choices"].append(cand)
                    have.add(cand["id"])
        if len(item["choices"]) < 2:
            pack.report.error(where, f"no wrong choice available for {item['answer']!r}: add distractors")


def _kind(thing: dict) -> str:
    return "img" if "img" in thing else "fa" if "fa" in thing else "t"


def parse_sheet(pack: Pack, game: dict, rows: list[dict], sheet: str) -> dict[str, dict]:
    """Rows of one game sheet to rounds, keyed by the round column."""
    engine = game["engine"]
    rounds: dict[str, dict] = {}
    for row in rows:
        where = f"{pack.where}/{sheet} row {row['_row']}"
        key = row.get("round", "")
        if not re.match(r"^[a-z0-9.]+$", key):
            pack.report.error(where, f"bad round {key!r}: use digits and lowercase letters, for example 03")
            continue
        rnd = rounds.setdefault(key, {"items": []})
        if row.get("intro_fa"):
            rnd["intro_audio"] = pack.say("fa", row["intro_fa"], where)
        item = None

        if engine in ("listen_pick", "journey", "duel"):
            item = _lp_item(pack, row, where)

        elif engine == "say_it":
            audio = pack.prompt(row, where)
            if not audio:
                pack.report.error(where, "needs say_en or say_fa")
            item = {"prompt_audio": audio}
            if row.get("say_en"):
                item["text"] = re.sub(r"\b[mf]:\s*", "", row["say_en"]).replace("//", "\n")
            elif row.get("say_fa"):
                item["fa"] = pack.fa(row["say_fa"], where)
            if row.get("picture"):
                item["show"] = pack.thing(row["picture"], where)
            if row.get("meaning_fa"):
                item["help_audio"] = pack.say("fa", row["meaning_fa"], where)

        elif engine == "sorter":
            thing = pack.thing(row.get("thing", ""), where)
            basket = pack.thing(row.get("basket", ""), where)
            if thing and basket:
                baskets = rnd.setdefault("baskets", [])
                if basket["id"] not in [b["id"] for b in baskets]:
                    if row.get("basket_say_fa"):
                        basket["audio"] = pack.say("fa", row["basket_say_fa"], where)
                    if row.get("basket_say_en"):
                        basket["audio"] = basket.get("audio", []) + pack.say("en", row["basket_say_en"], where)
                    baskets.append(basket)
                item = {"thing": thing, "basket": basket["id"], "prompt_audio": pack.prompt(row, where)}

        elif engine == "builder":
            tiles = pack.things(row.get("tiles", ""), where)
            if len(tiles) < 2:
                pack.report.error(where, "builder needs at least two tiles")
            if len(tiles) + len(split(row.get("extra", ""))) > 8:
                pack.report.error(where, "at most eight tiles fit on the screen")
            item = {
                "prompt_audio": pack.prompt(row, where),
                "tiles": tiles,
                "extra": pack.things(row.get("extra", ""), where),
                "rtl": row.get("rtl", "").lower() in ("1", "yes", "true", "y"),
                "done_audio": pack.say("fa", row.get("done_fa", ""), where) + pack.say("en", row.get("done_en", ""), where),
            }
            if row.get("help_fa"):
                item["help_audio"] = pack.say("fa", row["help_fa"], where)

        elif engine == "catch":
            targets = pack.things(row.get("targets", ""), where)
            others = pack.things(row.get("others", ""), where)
            if not targets or not others:
                pack.report.error(where, "catch needs targets and others")
            need = row.get("need", "") or "5"
            if not need.isdigit():
                pack.report.error(where, f"need must be a number, got {need!r}")
                need = "5"
            item = {"prompt_audio": pack.prompt(row, where), "targets": targets, "others": others, "need": int(need)}
            if row.get("help_fa"):
                item["help_audio"] = pack.say("fa", row["help_fa"], where)

        elif engine == "pairs":
            a, b = pack.thing(row.get("a", ""), where), pack.thing(row.get("b", ""), where)
            if a and b:
                item = {"a": a, "b": b, "audio": pack.prompt(row, where, slow=False)}
                if (a.get("snd") or b.get("snd")) and not item["audio"]:
                    pack.report.error(where, "a snd card needs say_en or say_fa")

        elif engine == "market":
            try:
                target = int(row.get("target", ""))
                units = [int(u) for u in split(row.get("units", "") or "1")]
            except ValueError:
                pack.report.error(where, "target and units must be whole numbers")
                continue
            mode = row.get("mode", "") or "count"
            if mode not in ("count", "pay"):
                pack.report.error(where, f"mode must be count or pay, got {mode!r}")
            if not _reachable(target, units):
                pack.report.error(where, f"target {target} cannot be made from units {units}")
            item = {"prompt_audio": pack.prompt(row, where), "target": target, "units": units, "mode": mode}
            if row.get("goods"):
                item["goods"] = pack.thing(row["goods"], where)
            if row.get("help_fa"):
                item["help_audio"] = pack.say("fa", row["help_fa"], where)

        elif engine == "story":
            item = {"audio": pack.prompt(row, where)}
            if not item["audio"]:
                pack.report.error(where, "every story page is spoken: needs say_en or say_fa")
            if row.get("picture"):
                item["img"] = pack.thing(row["picture"], where)
            if row.get("show_fa"):
                item["fa"] = pack.fa(row["show_fa"], where)
            if row.get("show_en"):
                item["text"] = row["show_en"]
            if row.get("choices"):
                item["choices"] = pack.things(row["choices"], where)
                right = pack.thing(row.get("right", ""), where)
                if not right or right["id"] not in [c["id"] for c in item["choices"]]:
                    pack.report.error(where, "right must be one of choices")
                else:
                    item["answer"] = right["id"]
                if not 2 <= len(item["choices"]) <= 4:
                    pack.report.error(where, "a story question has two to four choices")
                item["wrong_audio"] = pack.say("fa", row.get("wrong_say_fa", ""), where)
                if row.get("wrong_picture"):
                    item["wrong_img"] = pack.thing(row["wrong_picture"], where)

        if item:
            if engine != "story" and engine != "pairs" and not item.get("prompt_audio") and engine != "sorter":
                pack.report.error(where, "no spoken prompt")
            rnd["items"].append(item)
    return rounds


def _reachable(target: int, units: list[int]) -> bool:
    if target <= 0 or not units or min(units) <= 0:
        return False
    ok = [True] + [False] * target
    for t in range(1, target + 1):
        ok[t] = any(u <= t and ok[t - u] for u in units)
    return ok[target]


def rounds_from_items(pack: Pack, game: dict, items: list[dict]) -> dict[str, dict]:
    """Derive rounds straight from the word bank (items.csv), one per unit."""
    engine = game["engine"]
    lang = game.get("say", "en")
    rounds: dict[str, dict] = {}
    units: dict[str, list[dict]] = {}
    for it in items:
        units.setdefault(it["unit"], []).append(it)
    for unit, members in units.items():
        where = f"{pack.where}/items.csv unit {unit}"
        out = []
        for it in members:
            w = f"{pack.where}/items.csv row {it['_row']}"
            spoken = it.get(lang, "")
            if not spoken:
                continue
            row = {f"say_{lang}": spoken}
            meaning = it.get("fa", "") if lang == "en" else ""
            if engine in ("listen_pick", "duel", "journey"):
                if not it.get("picture"):
                    continue
                row.update(answer=it["picture"], help_fa=meaning, tags=it.get("tags", ""))
                item = _lp_item(pack, row, w)
            elif engine == "say_it":
                item = {"prompt_audio": pack.prompt(row, w)}
                if lang == "en":
                    item["text"] = re.sub(r"\b[mf]:\s*", "", spoken).replace("//", "\n")
                else:
                    item["fa"] = pack.fa(spoken, w)
                if it.get("picture"):
                    item["show"] = pack.thing(it["picture"], w)
                if meaning:
                    item["help_audio"] = pack.say("fa", meaning, w)
            elif engine == "pairs":
                if not it.get("picture") or len(out) >= 6:
                    continue
                item = {"a": {"id": "snd", "snd": True}, "b": pack.thing(it["picture"], w),
                        "audio": pack.prompt(row, w, slow=False)}
            else:
                pack.report.error(where, f"source items is not supported for engine {engine}")
                return {}
            if item:
                out.append(item)
        if engine == "pairs" and len(out) < 3:
            continue
        if out:
            rounds[unit] = {"items": out}
    return rounds


def build_learner(pack: Pack) -> dict:
    meta = pack.meta
    subject, level = meta.get("subject"), meta.get("level")
    if subject not in SUBJECTS or not isinstance(level, int) or not 1 <= level <= SUBJECTS.get(subject, 0):
        pack.report.error(f"{pack.where}/pack.json", f"bad subject/level {subject!r}/{level!r}")
    items = []
    if (pack.src / "items.csv").exists():
        items = read_csv(pack.src / "items.csv")
        seen = set()
        for it in items:
            w = f"{pack.where}/items.csv row {it['_row']}"
            if not it.get("unit"):
                pack.report.error(w, "missing unit")
            if it.get("key") in seen:
                pack.report.error(w, f"duplicate key {it.get('key')!r}")
            seen.add(it.get("key"))

    games_out, review, order = [], [], 0
    letters = set()
    for game in meta.get("games", []):
        gw = f"{pack.where}/pack.json game {game.get('id')}"
        engine = game.get("engine")
        if engine not in ENGINES:
            pack.report.error(gw, f"unknown engine {engine!r}")
            continue
        letter = game.get("letter", "")
        if not re.match(r"^[a-z]$", letter) or letter in letters:
            pack.report.error(gw, f"letter must be one unique lowercase letter per game, got {letter!r}")
        letters.add(letter)
        if game.get("source") == "items":
            rounds = rounds_from_items(pack, game, items)
        else:
            sheet = game.get("sheet", "")
            if not (pack.src / sheet).is_file():
                pack.report.error(gw, f"sheet not found: {sheet!r}")
                continue
            rounds = parse_sheet(pack, game, read_csv(pack.src / sheet), sheet)
        if not rounds:
            pack.report.warn(gw, "no rounds")
        default_intro = pack.say("fa", game.get("intro_fa", ""), gw)
        if not default_intro:
            pack.report.error(gw, "intro_fa is required: the spoken Dari instruction for the game")
        ids = []
        pool_things = []
        for key, rnd in rounds.items():
            for item in rnd["items"]:
                if "choices" in item:
                    pool_things.append(item["choices"][0])
        for key, rnd in rounds.items():
            rid = f"{pack.id}-{key}-{letter}"
            where = f"{gw} round {key}"
            if engine in ("listen_pick", "journey", "duel"):
                _fill_distractors(pack, rnd["items"], pool_things, where, rid)
            if engine == "sorter" and not 2 <= len(rnd.get("baskets", [])) <= 4:
                pack.report.error(where, "a sorter round needs two to four baskets")
            if engine == "pairs" and not 3 <= len(rnd["items"]) <= 6:
                pack.report.error(where, f"a pairs round needs three to six pairs, has {len(rnd['items'])}")
            if not rnd["items"]:
                pack.report.error(where, "round has no items")
            rnd.setdefault("intro_audio", default_intro)
            data = {"engine": engine, "id": rid, "game": game["id"], **rnd}
            pack.add_json(f"levels/{rid}.json", data)
            ids.append(rid)
            order += 1
            if engine in ("listen_pick", "journey", "duel"):
                for item in rnd["items"]:
                    entry = {k: item[k] for k in ("prompt_audio", "help_audio", "show", "choices", "answer", "tags") if k in item}
                    entry["round"] = rid
                    entry["order"] = order
                    review.append(entry)
        out = {
            "id": game["id"], "engine": engine, "rounds": ids,
            "title_en": game.get("title_en", game["id"]),
            "title_fa": pack.fa(game.get("title_fa", ""), gw, wrap=False),
            "title_audio": pack.say("fa", game.get("title_fa", ""), gw),
            "v1": bool(game.get("v1")),
        }
        if not game.get("title_fa"):
            pack.report.error(gw, "title_fa is required")
        if game.get("icon"):
            icon = pack.thing(game["icon"], gw)
            if icon:
                out["icon"] = icon
        games_out.append(out)
    pack.add_json("review.json", review)
    return {"subject": subject, "level": level, "games": games_out, "review": "review.json"}


# -- teacher pack ----------------------------------------------------------------


def build_teacher(pack: Pack) -> dict:
    meta = pack.meta
    out: dict = {"subject": meta.get("subject", "en"), "level": meta.get("level", 1)}
    lessons: dict[str, dict] = {}
    path = pack.src / "lessons.csv"
    for row in read_csv(path) if path.exists() else []:
        where = f"{pack.where}/lessons.csv row {row['_row']}"
        n = row.get("lesson", "")
        if not n.isdigit():
            pack.report.error(where, f"lesson must be a number, got {n!r}")
            continue
        lesson = lessons.setdefault(n, {"n": int(n), "id": f"{pack.id}-{int(n):02d}", "steps": [{"step": s, "lines": []} for s in STEPS]})
        if row.get("title_en"):
            lesson["title_en"] = row["title_en"]
            lesson["title_fa"] = pack.fa(row.get("title_fa", ""), where, wrap=False)
            lesson["title_audio"] = pack.say("fa", row.get("title_fa", ""), where)
        step = row.get("step", "")
        if step not in STEPS:
            pack.report.error(where, f"step must be one of {', '.join(STEPS)}, got {step!r}")
            continue
        kind = row.get("kind", "") or "line"
        if kind not in LINE_KINDS:
            pack.report.error(where, f"kind must be one of {', '.join(LINE_KINDS)}, got {kind!r}")
        if not row.get("teacher_fa"):
            pack.report.error(where, "teacher_fa is required: tell the teacher what to do")
        line = {"kind": kind, "teacher_fa": pack.fa(row.get("teacher_fa", ""), where)}
        if row.get("play_en"):
            line["text"] = re.sub(r"\b[mf]:\s*", "", row["play_en"]).replace("//", "\n")
            line["audio"] = pack.say("en", row["play_en"], where, slow=True)
        elif kind in ("drill", "check", "command"):
            pack.report.error(where, f"a {kind} row needs play_en")
        if row.get("meaning_fa"):
            line["meaning_fa"] = pack.fa(row["meaning_fa"], where)
            line["meaning_audio"] = pack.say("fa", row["meaning_fa"], where)
        if row.get("answer_en"):
            line["answer_text"] = row["answer_en"]
            line["answer_audio"] = pack.say("en", row["answer_en"], where, slow=True)
        lesson["steps"][STEPS.index(step)]["lines"].append(line)
    index = []
    for n in sorted(lessons, key=int):
        lesson = lessons[n]
        where = f"{pack.where}/lessons.csv lesson {n}"
        if "title_en" not in lesson:
            pack.report.error(where, "first row of a lesson needs title_en and title_fa")
        for step in lesson["steps"]:
            if not step["lines"]:
                pack.report.error(where, f"step {step['step']} has no lines")
        checks = sum(1 for s in lesson["steps"] for l in s["lines"] if l["kind"] == "check")
        if checks != 5:
            pack.report.warn(where, f"Quick Check wants five check rows, lesson has {checks}")
        pack.add_json(f"lessons/{lesson['id']}.json", lesson)
        index.append({"id": lesson["id"], "n": lesson["n"], "title_en": lesson.get("title_en", ""),
                      "title_fa": lesson.get("title_fa", []), "title_audio": lesson.get("title_audio", [])})
    out["lessons"] = index

    pages: dict[str, dict] = {}
    path = pack.src / "phrases.csv"
    for row in read_csv(path) if path.exists() else []:
        where = f"{pack.where}/phrases.csv row {row['_row']}"
        page = pages.setdefault(row.get("page", "1"), {"title_fa": [], "phrases": []})
        if row.get("page_title_fa"):
            page["title_fa"] = pack.fa(row["page_title_fa"], where, wrap=False)
        if not row.get("en"):
            pack.report.error(where, "missing en")
            continue
        page["phrases"].append({
            "text": row["en"], "audio": pack.say("en", row["en"], where, slow=True),
            "fa": pack.fa(row.get("fa", ""), where, wrap=False), "fa_audio": pack.say("fa", row.get("fa", ""), where),
        })
    if pages:
        for key, page in pages.items():
            if len(page["phrases"]) > 8:
                pack.report.error(f"{pack.where}/phrases.csv page {key}", "at most eight phrases per page")
        pack.add_json("phrases.json", [pages[k] for k in sorted(pages, key=lambda k: int(k) if k.isdigit() else 0)])
        out["phrases"] = "phrases.json"

    tips = []
    path = pack.src / "tips.csv"
    for row in read_csv(path) if path.exists() else []:
        where = f"{pack.where}/tips.csv row {row['_row']}"
        tips.append({"title_fa": pack.fa(row.get("title_fa", ""), where, wrap=False),
                     "fa": pack.fa(row.get("say_fa", ""), where), "audio": pack.say("fa", row.get("say_fa", ""), where)})
    if tips:
        pack.add_json("tips.json", tips)
        out["tips"] = "tips.json"
    return out


# -- core pack -------------------------------------------------------------------


def build_core(pack: Pack) -> dict:
    strings = {}
    for row in read_csv(pack.src / "strings.csv"):
        where = f"{pack.where}/strings.csv row {row['_row']}"
        key = row.get("key", "")
        if not key or key in strings:
            pack.report.error(where, f"missing or duplicate key {key!r}")
            continue
        entry: dict = {}
        if row.get("en"):
            entry["en"] = row["en"]
        if row.get("fa"):
            entry["fa"] = pack.fa(row["fa"], where)
        say = row.get("say", "") or "fa"
        audio = []
        if "fa" in say or say == "both":
            audio += pack.say("fa", row.get("fa", ""), where)
        if "en" in say or say == "both":
            audio += pack.say("en", row.get("en", ""), where, slow=True)
        if audio:
            entry["audio"] = audio
        strings[key] = entry
    pack.add_json("strings.json", strings)
    for name in split(pack.meta.get("pictures", "")):
        pack.thing(name, f"{pack.where}/pack.json")
    return {"strings": "strings.json"}


# -- entry point -----------------------------------------------------------------


def find_packs(content: Path) -> list[Path]:
    return sorted(p.parent for p in content.rglob("pack.json"))


def build(content: Path, out_dir: Path | None, tts: str | None = None, only: list[str] | None = None,
          strict: bool = False) -> Report:
    """Validate everything; write packs too when out_dir is given."""
    report = Report()
    speech = Speech(tts)
    seen: dict[str, Path] = {}
    for src in find_packs(content):
        where = str(src.relative_to(content))
        try:
            pack = Pack(src, content, speech, report, make_audio=out_dir is not None)
        except (json.JSONDecodeError, KeyError) as exc:
            report.error(f"{where}/pack.json", f"cannot read: {exc}")
            continue
        if only and pack.id not in only:
            continue
        if pack.id in seen:
            report.error(f"{where}/pack.json", f"pack id {pack.id!r} already used by {seen[pack.id]}")
            continue
        seen[pack.id] = src
        kind = pack.meta.get("kind", "learner")
        before = len(report.errors)
        try:
            body = {"learner": build_learner, "teacher": build_teacher, "core": build_core}[kind](pack)
        except KeyError:
            report.error(f"{where}/pack.json", f"unknown kind {kind!r}")
            continue
        pack.add_pictures(strict)
        manifest = {
            "format": FORMAT, "pack": pack.id, "kind": kind, "version": int(pack.meta.get("version", 1)),
            "optional": bool(pack.meta.get("optional", False)),
            "title_en": pack.meta.get("title_en", pack.id),
            "title_fa": pack.fa(pack.meta.get("title_fa", ""), f"{where}/pack.json", wrap=False),
            **body,
        }
        if out_dir is not None and len(report.errors) == before:
            path = pack.write(out_dir, manifest)
            print(f"  {path.name}: {len(pack.files)} files, {path.stat().st_size / 1e6:.1f} MB")
    if speech.generated:
        print(f"  speech: {speech.generated} new clips with '{speech.provider}'")
    return report

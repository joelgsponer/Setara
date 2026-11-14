"""Builder tests. Run: cd builder && python3 -m pytest -q"""
import json
import zipfile
from pathlib import Path

from setara_builder import shaping
from setara_builder.build import build, _reachable
from setara_builder.tts import parse_segments


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def pack(tmp: Path, sheet: str, engine: str = "listen_pick") -> Path:
    content = tmp / "content"
    write(content / "x" / "pack.json", json.dumps({
        "pack": "en-1", "subject": "en", "level": 1, "version": 3, "title_en": "T", "title_fa": "سلام",
        "games": [{"id": "g", "engine": engine, "letter": "a", "title_en": "G", "title_fa": "بازی",
                   "intro_fa": "گوش کن", "sheet": "g.csv"}],
    }))
    write(content / "x" / "g.csv", sheet)
    return content


def test_dari_is_joined_and_reversed():
    # سلام: the four letters in their joined forms, last letter first
    assert shaping.shape_line("سلام") == "ﻡﻼﺳ"
    # non-joining alef: the letter after it starts a new group
    assert shaping.shape_line("باغ") == "ﻍﺎﺑ"


def test_zwnj_breaks_the_join_and_is_removed():
    shaped = shaping.shape_line("می‌روم")
    assert "‌" not in shaped
    assert shaped.endswith("ﯽﻣ")  # final yeh after initial meem, drawn last


def test_latin_inside_dari_keeps_its_order():
    assert "Hello" in shaping.shape_line("بگویید Hello")


def test_wrapping_fits_the_screen():
    lines = shaping.shape("این یک جملهٔ بسیار دراز است که باید در چند سطر روی صفحهٔ کوچک دستگاه نوشته شود تا خوانده شود")
    assert len(lines) >= 2
    assert all(shaping.width(line) <= shaping.BODY_WIDTH for line in lines)


def test_letter_forms_differ():
    forms = {shaping.letter_form("ب", f) for f in ("alone", "start", "middle", "end")}
    assert len(forms) == 4


def test_every_shaped_glyph_is_in_the_font():
    assert shaping.missing_glyphs(shaping.shape_line("آب پاک را بنوشید؛ ۱۲۳ ژاله گچ")) == []


def test_two_voices():
    assert parse_segments("f: Hi // m: Hello") == [("f", "Hi"), ("m", "Hello")]
    assert parse_segments("Hello") == [("f", "Hello")]


def test_market_targets():
    assert _reachable(25, [5, 10, 20])
    assert not _reachable(3, [2, 4])


def test_builds_a_checksummed_pack(tmp_path):
    content = pack(tmp_path, "round,say_en,answer,distractors\n01,apple,apple,bread|egg\n01,bread,bread,\n")
    report = build(content, tmp_path / "out", tts="silent")
    assert report.errors == []
    with zipfile.ZipFile(tmp_path / "out" / "en-1.zip") as z:
        manifest = json.loads(z.read("manifest.json"))
        level = json.loads(z.read("levels/en-1-01-a.json"))
        assert set(manifest["files"]) == set(z.namelist()) - {"manifest.json"}
    assert manifest["version"] == 3 and manifest["games"][0]["rounds"] == ["en-1-01-a"]
    assert level["items"][0]["answer"] == "apple"
    # the second question got its wrong choice from the round
    assert len(level["items"][1]["choices"]) >= 2
    # prompts have a slow variant
    assert any(name.endswith(".slow.ogg") for name in manifest["files"])


def test_unspoken_question_is_an_error(tmp_path):
    content = pack(tmp_path, "round,say_en,answer,distractors\n01,,apple,bread\n")
    report = build(content, None, tts="silent")
    assert any("spoken" in e for e in report.errors)


def test_bad_rows_are_reported_with_file_and_row(tmp_path):
    content = pack(tmp_path, "round,say_en,tiles\n01,I am,t:I\n", engine="builder")
    report = build(content, None, tts="silent")
    assert any("g.csv row 2" in e and "two tiles" in e for e in report.errors)


def test_a_pack_with_errors_is_not_written(tmp_path):
    content = pack(tmp_path, "round,say_en,answer,distractors\n01,,apple,bread\n")
    build(content, tmp_path / "out", tts="silent")
    assert not (tmp_path / "out" / "en-1.zip").exists()

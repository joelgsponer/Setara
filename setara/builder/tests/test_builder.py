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


def test_brackets_are_mirrored_in_dari():
    from setara_builder import shaping
    line = shaping.shape_line("او گفت «کتاب» را (نه) بخوان.")
    # in drawing order, from the left: the closing mark, the word, the opening mark,
    # each turned so that it opens towards the word
    assert line.index("«") < line.index("»")
    assert line.index("(") < line.index(")")
    # between Latin letters nothing is turned
    assert "(a cat)" in shaping.shape_line("بگویید hello (a cat) now حالا")


def test_speech_cache_only_generates_new_or_changed_texts(tmp_path):
    cache = tmp_path / "cache"
    sheet = "round,say_en,answer,distractors\n01,apple,apple,bread|egg\n01,bread,bread,\n"
    content = pack(tmp_path, sheet)
    first = build(content, tmp_path / "out1", tts="silent", tts_cache=cache).speech
    assert first.misses > 0 and first.hits == 0
    with zipfile.ZipFile(tmp_path / "out1" / "en-1.zip") as z:
        clips1 = {n: z.read(n) for n in z.namelist() if n.endswith(".ogg")}

    # the same content again: everything comes from the cache, packs are identical
    again = build(content, tmp_path / "out2", tts="silent", tts_cache=cache).speech
    assert (again.hits, again.misses) == (first.misses, 0)
    assert (tmp_path / "out1" / "en-1.zip").read_bytes() == (tmp_path / "out2" / "en-1.zip").read_bytes()

    # one prompt changed: only it is generated, at normal speed and slow
    write(content / "x" / "g.csv", sheet.replace("01,bread,bread,", "01,bread please,bread,"))
    changed = build(content, tmp_path / "out3", tts="silent", tts_cache=cache).speech
    assert changed.misses == 2 and changed.hits == first.misses - 2
    with zipfile.ZipFile(tmp_path / "out3" / "en-1.zip") as z:
        clips3 = {n for n in z.namelist() if n.endswith(".ogg")}
    assert len(clips3 - set(clips1)) == 2


def test_speech_cache_key_follows_the_sound(tmp_path, monkeypatch):
    from setara_builder import tts
    s = tts.Speech("silent", cache=tmp_path)
    k = s.key("en", "Hello  there")
    assert k == s.key("en", "Hello there")  # spacing does not change the sound
    assert k != s.key("en", "Hello there", slow=True)
    assert k != s.key("fa", "Hello there")
    assert k != s.key("en", "m: Hello there")  # another voice
    monkeypatch.setattr(tts, "RECIPE", tts.RECIPE + 1)
    assert k != tts.Speech("silent", cache=tmp_path).key("en", "Hello there")


def test_speech_cache_key_follows_the_voice_model(tmp_path, monkeypatch):
    from setara_builder import tts
    models = tmp_path / "voices"
    models.mkdir()
    for name in ("en_US-amy-medium", "en_US-ryan-medium", "fa_IR-amir-medium"):
        (models / f"{name}.onnx").write_bytes(b"model")
        (models / f"{name}.onnx.json").write_text("{}")
    monkeypatch.setitem(tts.DEFAULT_VOICES["piper"], "dir", str(models))
    k = tts.Speech("piper", cache=tmp_path / "c").key("en", "Hello")
    (models / "en_US-ryan-medium.onnx").write_bytes(b"other")  # not the voice of this clip
    assert k == tts.Speech("piper", cache=tmp_path / "c").key("en", "Hello")
    (models / "en_US-amy-medium.onnx").write_bytes(b"retrained")
    assert k != tts.Speech("piper", cache=tmp_path / "c").key("en", "Hello")


def test_eli_falls_back_to_the_fallback_voice_in_the_key(tmp_path, monkeypatch):
    from setara_builder import tts
    monkeypatch.setitem(tts.DEFAULT_VOICES["piper"], "dir", str(tmp_path))
    eli = tts.Speech("eli", cache=tmp_path / "c")
    # English has an eli voice; Persian is spoken by piper, so its key follows piper's model
    assert eli._voice_fingerprint("en", "f")["voice"] == "maat"
    fa = eli.key("fa", "سلام")
    (tmp_path / "fa_IR-amir-medium.onnx").write_bytes(b"model")
    assert fa != tts.Speech("eli", cache=tmp_path / "c").key("fa", "سلام")


def test_speech_cache_is_seeded_from_an_old_cache(tmp_path, monkeypatch):
    from setara_builder import tts
    content = pack(tmp_path, "round,say_en,answer,distractors\n01,apple,apple,bread|egg\n01,bread,bread,\n")
    # an old cache (names before RECIPE 2) made on another machine, with only some clips
    old = tmp_path / "old"
    old.mkdir()
    monkeypatch.setenv("SETARA_TTS_SEED", str(old))
    monkeypatch.setenv("SETARA_TTS_SEED_PIPER_DIR", "/elsewhere/voices")
    s = tts.Speech("silent", cache=tmp_path / "unused")
    (old / f"{s.legacy_key('en', 'apple')}.ogg").write_bytes(b"old apple")
    (old / f"{s.legacy_key('en', 'apple', slow=True)}.ogg").write_bytes(b"old slow apple")
    run = build(content, tmp_path / "out", tts="silent", tts_cache=tmp_path / "cache").speech
    assert run.seeded == 2 and run.misses > 0 and run.hits == 0
    with zipfile.ZipFile(tmp_path / "out" / "en-1.zip") as z:
        assert b"old apple" in [z.read(n) for n in z.namelist()]
    # the seeded clips are now in the cache: no seed needed the next time
    monkeypatch.delenv("SETARA_TTS_SEED")
    again = build(content, tmp_path / "out2", tts="silent", tts_cache=tmp_path / "cache").speech
    assert (again.misses, again.seeded) == (0, 0)


def test_legacy_key_is_the_old_cache_name(monkeypatch):
    import hashlib
    import json as js
    from setara_builder import tts
    monkeypatch.setenv("SETARA_TTS_SEED_PIPER_DIR", "/home/x/voices")
    s = tts.Speech("piper")
    cfg = js.loads(js.dumps(s.voices["piper"]))
    cfg["dir"] = "/home/x/voices"
    want = hashlib.sha1(f"piper|{js.dumps(cfg, sort_keys=True)}|fa|True|سلام دوست".encode()).hexdigest()
    assert s.legacy_key("fa", "سلام  دوست", slow=True) == want

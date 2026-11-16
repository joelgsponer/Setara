"""Speech generation with a file cache.

Every spoken text becomes one Ogg Vorbis file. The cache keeps one file per
clip, named by a hash of everything that changes the sound: the text, the
language, normal or slow, the provider, the voice model files, the provider's
version, the synthesis and encoding settings and RECIPE. So a phrase is only
ever generated once, and a rebuild after a content change only generates the
new or changed texts.

The cache is builder/.cache/audio, or the folder in SETARA_TTS_CACHE (the
Dockerfile keeps it in a BuildKit cache mount, so it outlives image builds).
Raise RECIPE whenever code here changes the sound in a way the key cannot see.

Providers, chosen with --tts or the SETARA_TTS environment variable:

  piper       local neural voices (default when models are installed). Good
              enough to build and test with. The Persian voice is Iranian.
  espeak      espeak-ng, robotic, needs no model files.
  elevenlabs  the production voices of the spec. Needs ELEVENLABS_API_KEY and
              voice ids in builder/voices.json.
  silent      half a second of silence per clip, for tests and CI.

LÖVE cannot decode Opus, so audio is Ogg Vorbis, mono, 22.05 kHz.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
from importlib import metadata
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "audio"
VOICES_FILE = ROOT / "voices.json"

RECIPE = 2  # raise when synthesis or encoding code changes the sound
SLOW = 1.45  # length scale for the "say it again, slowly" variant
SHORT = 1.15  # length scale for one or two words at normal speed
NORMAL = 1.05  # length scale for longer texts at normal speed
GAP_MS = 350  # pause between two voices in a dialogue
ELI_SLOW = 0.8  # eli has no speed control: "slow" is a time stretch (atempo)
RATE = 22050  # output sample rate
QUALITY = "2"  # libvorbis -q:a

DEFAULT_VOICES = {
    "piper": {
        "dir": os.environ.get("SETARA_PIPER_DIR", str(ROOT / "voices")),
        "en": {"f": "en_US-amy-medium", "m": "en_US-ryan-medium"},
        "fa": {"f": "fa_IR-amir-medium", "m": "fa_IR-amir-medium"},
    },
    "espeak": {"en": {"f": "en-us+f3", "m": "en-us"}, "fa": {"f": "fa+f3", "m": "fa"}},
    # eli-tts on ladon (Qwen3-TTS, cloned voices; Joel's pick, intercom #239).
    # No Persian in Qwen3-TTS: a language without a voice here uses `fallback`.
    "eli": {
        "url": os.environ.get("SETARA_ELI_TTS_URL", "http://127.0.0.1:8179"),
        "fallback": "piper",
        "en": {"f": "maat", "m": "humboldt"},
    },
    "elevenlabs": {
        "model": "eleven_multilingual_v2",
        "en": {"f": "", "m": ""},
        "fa": {"f": "", "m": ""},
    },
}


def load_voices() -> dict:
    voices = json.loads(json.dumps(DEFAULT_VOICES))
    if VOICES_FILE.exists():
        for provider, cfg in json.loads(VOICES_FILE.read_text("utf-8")).items():
            voices.setdefault(provider, {}).update(cfg)
    return voices


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:24] or "x"


def parse_segments(text: str) -> list[tuple[str, str]]:
    """'f: Hello // m: Hi' -> [('f', 'Hello'), ('m', 'Hi')]. Default voice is f."""
    out = []
    for part in text.split("//"):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^([mf]):\s*(.+)$", part, re.S)
        out.append((m.group(1), m.group(2).strip()) if m else ("f", part))
    return out


def _file_hash(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _tool_version(cmd: list[str]) -> str:
    """First line of a tool's version output, or 'missing'."""
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return "missing"
    lines = (done.stdout or done.stderr).strip().splitlines()
    return lines[0] if lines else "unknown"


def _ffmpeg_version() -> str:
    """ffmpeg major.minor: patch and distribution builds do not change the encoder."""
    m = re.search(r"version n?(\d+\.\d+)", _tool_version(["ffmpeg", "-version"]))
    return m.group(1) if m else "unknown"


class Speech:
    def __init__(self, provider: str | None = None, cache: Path | str | None = None):
        self.voices = load_voices()
        self.provider = provider or os.environ.get("SETARA_TTS") or self._pick()
        self._piper: dict[str, object] = {}
        self.cache = Path(cache or os.environ.get("SETARA_TTS_CACHE") or CACHE)
        self.cache.mkdir(parents=True, exist_ok=True)
        self._fingerprints: dict[tuple[str, str], object] = {}
        self._encoder: dict | None = None
        self._clips: dict[str, bool] = {}  # cache key -> came from the cache
        self.hits = 0  # clips found in the cache
        self.seeded = 0  # clips copied in from the seed folder
        self.misses = 0  # clips generated in this run
        # A seed: clips made elsewhere (another machine's cache) that fill this
        # cache instead of generating. Its files may have this cache's names, or
        # the names of the old cache (before RECIPE 2), which held the piper
        # voice folder of the machine that made them: give that folder as
        # SETARA_TTS_SEED_PIPER_DIR. Read only; see docs/speech.md.
        seed = os.environ.get("SETARA_TTS_SEED")
        self.seed = Path(seed) if seed and Path(seed).is_dir() and any(Path(seed).iterdir()) else None
        self.seed_piper_dir = os.environ.get("SETARA_TTS_SEED_PIPER_DIR") or None

    @property
    def generated(self) -> int:
        return self.misses

    def _pick(self) -> str:
        cfg = self.voices["piper"]
        try:
            import piper  # noqa: F401

            if (Path(cfg["dir"]) / (cfg["en"]["f"] + ".onnx")).exists():
                return "piper"
        except ImportError:
            pass
        if shutil.which("espeak-ng"):
            return "espeak"
        return "silent"

    # -- public ---------------------------------------------------------------

    def name(self, lang: str, text: str, slow: bool = False) -> str:
        """Path of the clip inside a pack, for example en/apple-1a2b3c.ogg."""
        text = " ".join(text.split())
        digest = hashlib.sha1(f"{lang}|{text}".encode("utf-8")).hexdigest()[:8]
        return f"{lang}/{slug(text)}-{digest}{'.slow' if slow else ''}.ogg"

    def key(self, lang: str, text: str, slow: bool = False) -> str:
        """Cache key of a clip: a hash of everything that changes its sound."""
        text = " ".join(text.split())
        segments = parse_segments(text)
        recipe = {
            "recipe": RECIPE,
            "provider": self.provider,
            "lang": lang,
            "slow": bool(slow),
            "segments": segments,
            "voices": {v: self._voice_fingerprint(lang, v) for v in sorted({v for v, _ in segments})},
            "encoder": self._encoder_fingerprint(),
        }
        return hashlib.sha256(json.dumps(recipe, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    def render(self, lang: str, text: str, slow: bool = False) -> Path:
        """Return the cached Ogg file for a text, generating it if needed."""
        text = " ".join(text.split())
        key = self.key(lang, text, slow)
        out = self.cache / key[:2] / f"{key}.ogg"
        if key in self._clips:
            return out
        if out.exists() and out.stat().st_size > 0:
            self._clips[key] = True
            self.hits += 1
            return out
        out.parent.mkdir(parents=True, exist_ok=True)
        found = self._from_seed(lang, text, slow, key)
        if found is not None:
            tmp = out.with_name(f"{out.stem}.{os.getpid()}.{os.urandom(4).hex()}.tmp.ogg")
            try:
                shutil.copyfile(found, tmp)
                tmp.replace(out)
            finally:
                tmp.unlink(missing_ok=True)
            self._clips[key] = True
            self.seeded += 1
            return out
        with tempfile.TemporaryDirectory() as tmp:
            wavs = []
            for i, (voice, part) in enumerate(parse_segments(text)):
                wav = Path(tmp) / f"{i}.wav"
                self._synth(lang, voice, part, slow, wav)
                wavs.append(wav)
            self._encode(wavs, out)
        self._clips[key] = False
        self.misses += 1
        return out

    def summary(self) -> str:
        seeded = f", {self.seeded} from the seed" if self.seed else ""
        return (f"speech ({self.provider}): {len(self._clips)} clips, {self.hits} from cache{seeded}, "
                f"{self.misses} generated")

    def legacy_key(self, lang: str, text: str, slow: bool = False) -> str:
        """The cache name of a clip before RECIPE 2, for seeding from an old cache."""
        cfg = json.loads(json.dumps(self.voices.get(self.provider)))
        if self.provider == "piper" and self.seed_piper_dir and isinstance(cfg, dict):
            cfg["dir"] = self.seed_piper_dir
        text = " ".join(text.split())
        return hashlib.sha1(f"{self.provider}|{json.dumps(cfg, sort_keys=True)}|{lang}|{slow}|{text}".encode()).hexdigest()

    def _from_seed(self, lang: str, text: str, slow: bool, key: str) -> Path | None:
        if self.seed is None:
            return None
        for cand in (self.seed / key[:2] / f"{key}.ogg", self.seed / f"{key}.ogg",
                     self.seed / f"{self.legacy_key(lang, text, slow)}.ogg"):
            if cand.is_file() and cand.stat().st_size > 0:
                return cand
        return None

    # -- cache key parts ------------------------------------------------------

    def _voice_fingerprint(self, lang: str, voice: str, provider: str | None = None) -> object:
        """What identifies one voice of the provider: model files and versions."""
        p = provider or self.provider
        if (p, lang, voice) in self._fingerprints:
            return self._fingerprints[(p, lang, voice)]
        cfg = self.voices.get(p, {})
        if p == "eli":
            name = (cfg.get(lang) or {}).get(voice)
            if name:
                # the server's model and cloned voices are not visible from here:
                # set "version" for eli in voices.json when they change
                fp: object = {"voice": name, "version": cfg.get("version", ""), "slow": ELI_SLOW}
            else:  # a language without an eli voice is spoken by the fallback
                fallback = cfg.get("fallback", "piper")
                fp = {"fallback": fallback, "voice": self._voice_fingerprint(lang, voice, fallback)}
        elif p == "piper":
            model = cfg[lang][voice]
            base = Path(cfg["dir"]) / model
            try:
                version = metadata.version("piper-tts")
            except metadata.PackageNotFoundError:
                version = "missing"
            fp = {
                "model": model,
                "onnx": _file_hash(base.with_name(model + ".onnx")),
                "config": _file_hash(base.with_name(model + ".onnx.json")),
                "piper": version,
                "scale": [SLOW, SHORT, NORMAL],
            }
        elif p == "espeak":
            fp = {"voice": cfg[lang][voice], "espeak": _tool_version(["espeak-ng", "--version"]), "speed": [105, 150]}
        elif p == "elevenlabs":
            fp = {"voice": cfg[lang][voice], "model": cfg.get("model", "eleven_multilingual_v2"),
                  "settings": [0.6, 0.8, 0.75, 1.0]}
        else:
            fp = {"provider": p}
        self._fingerprints[(p, lang, voice)] = fp
        return fp

    def _encoder_fingerprint(self) -> dict:
        if self._encoder is None:
            self._encoder = {"ffmpeg": _ffmpeg_version(), "rate": RATE, "q": QUALITY, "gap_ms": GAP_MS}
        return self._encoder

    # -- providers ------------------------------------------------------------

    def _synth(self, lang: str, voice: str, text: str, slow: bool, wav: Path) -> None:
        getattr(self, f"_synth_{self.provider}")(lang, voice, text, slow, wav)

    def _synth_silent(self, lang, voice, text, slow, wav: Path) -> None:
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(b"\0\0" * (RATE // 2))

    def _synth_piper(self, lang, voice, text, slow, wav: Path) -> None:
        from piper import PiperVoice, SynthesisConfig

        cfg = self.voices["piper"]
        model = cfg[lang][voice]
        if model not in self._piper:
            self._piper[model] = PiperVoice.load(str(Path(cfg["dir"]) / f"{model}.onnx"))
        # Single words come out clipped at normal speed; give them a little room.
        scale = SLOW if slow else (SHORT if len(text.split()) <= 2 else NORMAL)
        with wave.open(str(wav), "wb") as w:
            self._piper[model].synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=scale))

    def _synth_espeak(self, lang, voice, text, slow, wav: Path) -> None:
        v = self.voices["espeak"][lang][voice]
        speed = "105" if slow else "150"
        subprocess.run(["espeak-ng", "-v", v, "-s", speed, "-w", str(wav), text], check=True)

    def _synth_eli(self, lang, voice, text, slow, wav: Path) -> None:
        cfg = self.voices["eli"]
        name = (cfg.get(lang) or {}).get(voice)
        if not name:
            return getattr(self, f"_synth_{cfg.get('fallback', 'piper')}")(lang, voice, text, slow, wav)
        token = os.environ.get("SETARA_ELI_TTS_TOKEN", "")
        tf = Path.home() / ".config/setara/eli-tts-token"
        if not token and tf.exists():
            token = tf.read_text().strip()
        body = {"input": text, "voice": name, "language": lang, "response_format": "wav"}
        req = urllib.request.Request(
            cfg["url"] + "/v1/audio/speech", data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        )
        raw = wav.with_suffix(".eli.wav")
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw.write_bytes(resp.read())
        # The stream's WAV header has no sizes; ffmpeg rewrites it. Qwen has no speed
        # control, so "slow" is a pitch-keeping time stretch.
        af = ["-af", f"atempo={ELI_SLOW}"] if slow else []
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw), *af, str(wav)], check=True)

    def _synth_elevenlabs(self, lang, voice, text, slow, wav: Path) -> None:
        cfg = self.voices["elevenlabs"]
        key = os.environ.get("ELEVENLABS_API_KEY")
        voice_id = cfg[lang][voice]
        if not key or not voice_id:
            raise SystemExit("elevenlabs: set ELEVENLABS_API_KEY and voice ids in builder/voices.json")
        body = {
            "text": text,
            "model_id": cfg.get("model", "eleven_multilingual_v2"),
            "voice_settings": {"stability": 0.6, "similarity_boost": 0.8, "speed": 0.75 if slow else 1.0},
        }
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
            data=json.dumps(body).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json"},
        )
        mp3 = wav.with_suffix(".mp3")
        with urllib.request.urlopen(req, timeout=120) as resp:
            mp3.write_bytes(resp.read())
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), str(wav)], check=True
        )

    # -- encoding -------------------------------------------------------------

    def _encode(self, wavs: list[Path], out: Path) -> None:
        """Join the parts with a short gap, trim silence, write mono Vorbis."""
        cmd = ["ffmpeg", "-loglevel", "error", "-y"]
        for w in wavs:
            cmd += ["-i", str(w)]
        chains = []
        for i in range(len(wavs)):
            pad = f",apad=pad_dur={GAP_MS / 1000}" if i < len(wavs) - 1 else ""
            chains.append(f"[{i}:a]aresample={RATE},aformat=channel_layouts=mono{pad}[a{i}]")
        joined = "".join(f"[a{i}]" for i in range(len(wavs)))
        graph = ";".join(chains) + f";{joined}concat=n={len(wavs)}:v=0:a=1[out]"
        # a name of its own, so two builds sharing the cache never write one file
        tmp = out.with_name(f"{out.stem}.{os.getpid()}.{os.urandom(4).hex()}.tmp.ogg")
        cmd += ["-filter_complex", graph, "-map", "[out]", "-c:a", "libvorbis", "-q:a", QUALITY, str(tmp)]
        try:
            subprocess.run(cmd, check=True)
            tmp.replace(out)
        finally:
            tmp.unlink(missing_ok=True)

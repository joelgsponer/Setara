"""Speech generation with a file cache.

Every spoken text becomes one Ogg Vorbis file, named from the language, voice,
speed and text, so the same phrase is only ever generated once.

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
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "audio"
VOICES_FILE = ROOT / "voices.json"

SLOW = 1.45  # length scale for the "say it again, slowly" variant
GAP_MS = 350  # pause between two voices in a dialogue

DEFAULT_VOICES = {
    "piper": {
        "dir": os.environ.get("SETARA_PIPER_DIR", str(ROOT / "voices")),
        "en": {"f": "en_US-amy-medium", "m": "en_US-ryan-medium"},
        "fa": {"f": "fa_IR-amir-medium", "m": "fa_IR-amir-medium"},
    },
    "espeak": {"en": {"f": "en-us+f3", "m": "en-us"}, "fa": {"f": "fa+f3", "m": "fa"}},
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


class Speech:
    def __init__(self, provider: str | None = None):
        self.voices = load_voices()
        self.provider = provider or os.environ.get("SETARA_TTS") or self._pick()
        self._piper: dict[str, object] = {}
        self.generated = 0
        CACHE.mkdir(parents=True, exist_ok=True)

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

    def render(self, lang: str, text: str, slow: bool = False) -> Path:
        """Return the cached Ogg file for a text, generating it if needed."""
        text = " ".join(text.split())
        key = hashlib.sha1(
            f"{self.provider}|{json.dumps(self.voices.get(self.provider), sort_keys=True)}|{lang}|{slow}|{text}".encode()
        ).hexdigest()
        out = CACHE / f"{key}.ogg"
        if out.exists() and out.stat().st_size > 0:
            return out
        with tempfile.TemporaryDirectory() as tmp:
            wavs = []
            for i, (voice, part) in enumerate(parse_segments(text)):
                wav = Path(tmp) / f"{i}.wav"
                self._synth(lang, voice, part, slow, wav)
                wavs.append(wav)
            self._encode(wavs, out)
        self.generated += 1
        return out

    # -- providers ------------------------------------------------------------

    def _synth(self, lang: str, voice: str, text: str, slow: bool, wav: Path) -> None:
        getattr(self, f"_synth_{self.provider}")(lang, voice, text, slow, wav)

    def _synth_silent(self, lang, voice, text, slow, wav: Path) -> None:
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(22050)
            w.writeframes(b"\0\0" * 11025)

    def _synth_piper(self, lang, voice, text, slow, wav: Path) -> None:
        from piper import PiperVoice, SynthesisConfig

        cfg = self.voices["piper"]
        model = cfg[lang][voice]
        if model not in self._piper:
            self._piper[model] = PiperVoice.load(str(Path(cfg["dir"]) / f"{model}.onnx"))
        # Single words come out clipped at normal speed; give them a little room.
        scale = SLOW if slow else (1.15 if len(text.split()) <= 2 else 1.05)
        with wave.open(str(wav), "wb") as w:
            self._piper[model].synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=scale))

    def _synth_espeak(self, lang, voice, text, slow, wav: Path) -> None:
        v = self.voices["espeak"][lang][voice]
        speed = "105" if slow else "150"
        subprocess.run(["espeak-ng", "-v", v, "-s", speed, "-w", str(wav), text], check=True)

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
            chains.append(f"[{i}:a]aresample=22050,aformat=channel_layouts=mono{pad}[a{i}]")
        joined = "".join(f"[a{i}]" for i in range(len(wavs)))
        graph = ";".join(chains) + f";{joined}concat=n={len(wavs)}:v=0:a=1[out]"
        tmp = out.with_suffix(".tmp.ogg")
        cmd += ["-filter_complex", graph, "-map", "[out]", "-c:a", "libvorbis", "-q:a", "2", str(tmp)]
        subprocess.run(cmd, check=True)
        tmp.replace(out)

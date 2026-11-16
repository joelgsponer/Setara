# Speech

Everything in Setara is spoken, so every text in every sheet becomes an audio
clip. The builder generates the clips and keeps them in `builder/.cache/`, so
a phrase is only ever generated once.

## The cache

Each clip is stored under a hash of everything that changes its sound: the
text, the language, normal or slow, the provider and its version, the voice
model files, and the synthesis and encoding settings. A rebuild after a
content change only generates the new or changed texts; the builder prints
how many clips came from the cache and how many it generated, also with
`--quiet`.

The cache is `builder/.cache/audio`, or the folder given with `--tts-cache`
or `SETARA_TTS_CACHE`. The Dockerfile keeps it in a BuildKit cache mount
(`id=setara-tts`), so it outlives image builds until the build cache is
pruned (`docker builder prune`). After a prune the next build generates
everything once. When code changes the sound in a way the key cannot see,
raise `RECIPE` in `builder/setara_builder/tts.py`.

### Seeding

Clips made on another machine can fill the cache instead of being generated
again. Give the folder as `SETARA_TTS_SEED`. Its files may have the cache's
own names, or the flat names of the old cache (before `RECIPE` 2). The old
names contain the piper voice folder of the machine that made them; give
that folder as `SETARA_TTS_SEED_PIPER_DIR`. The build then reports how many
clips came from the seed. A seeded clip is used as it is: seed only from a
machine with the same voice models.

For the Docker build, a one-off build on the same Docker host fills the
cache mount:

```sh
docker buildx build --target build --build-context speech-seed=/path/to/clips \
  --build-arg TTS_SEED_PIPER_DIR=/home/someone/Setara/setara/builder/voices .
```

The next normal build then finds those clips in the cache.

## Where the speech is made

At build time, on the team's PC. The handheld cannot synthesise speech inside
LÖVE, and a recorded clip sounds the same on every device.

## Providers

| `--tts` | What | Use |
| --- | --- | --- |
| `piper` | Local neural voices, downloaded once with `builder/get_voices.sh` | Building and testing. The default when the models are present |
| `espeak` | espeak-ng, robotic, no model files | When nothing else is installed |
| `elevenlabs` | The voices the spec decides on | Production |
| `silent` | Half a second of silence per clip | Tests and CI |

The piper voices are **stand-ins**. Two things about them matter:

- The Persian voice is Iranian, not Afghan, and it is a man's voice: no
  woman's Persian voice exists in that set. A Dari speaker has to judge any
  voice before children hear it (spec, phase 0).
- No one has listened to the generated clips. They were made in a container
  without a loudspeaker. Mispronounced words, clipped starts and wrong stress
  will exist and are not found yet.

## Switching to ElevenLabs

1. Put the voice ids in `builder/voices.json`:

   ```json
   {"elevenlabs": {"model": "eleven_multilingual_v2",
     "en": {"f": "<voice id>", "m": "<voice id>"},
     "fa": {"f": "<voice id>", "m": "<voice id>"}}}
   ```

2. `ELEVENLABS_API_KEY=… python3 -m setara_builder.cli build --tts elevenlabs`

This path is written but has never been run: there was no key to test it with.
The clips are cached per provider and voice, so switching regenerates all of
them once (about 6,900 clip files, slow variants included, for the current content).

## Format

Ogg Vorbis, mono, 22.05 kHz, quality 2 (about 32 kbit/s). The spec asks for
Opus at 24 kbit/s, but LÖVE 11 cannot decode Opus. Vorbis at this setting
gives packs of 7 to 16 MB, inside the spec's budget.

Prompts are generated twice, at normal speed and slow (`.slow.ogg`), for the
X button.

## Two voices

A woman's voice is the default. `f: … // m: …` in a sheet makes a dialogue of
two voices with a short pause between them.

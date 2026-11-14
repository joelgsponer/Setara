# Speech

Everything in Setara is spoken, so every text in every sheet becomes an audio
clip. The builder generates the clips and keeps them in `builder/.cache/`, so
a phrase is only ever generated once.

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

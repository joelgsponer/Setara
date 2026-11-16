# Setara in a browser: builds the content packs and the web version from
# source, then serves them as static files.
#
#   docker build -t setara-web .
#   docker run -p 8080:80 setara-web        ->  http://localhost:8080
#
# The first build generates all speech with the stand-in voices and takes
# 20 to 40 minutes on a small server (hours on two cores). The clips are kept
# in a BuildKit cache mount (id setara-tts), so a rebuild after a content
# change only generates the new or changed texts. Needs BuildKit, the default
# builder since Docker 23. `docker builder prune` empties the cache; the next
# build then generates everything once. Build arguments:
#   TTS=piper    stand-in neural voices (default; downloads about 190 MB)
#   TTS=espeak   robotic voices, much faster to build, nothing to download
#   TTS=silent   no speech at all: English captions only, builds in minutes
#   START=english | dari    the language the page starts in

# Clips to fill the speech cache with, instead of generating them: empty
# unless a one-off build passes a folder (docs/speech.md, "Seeding"):
#   docker buildx build --target build --build-context speech-seed=<clips> \
#     --build-arg TTS_SEED_PIPER_DIR=<voices folder of the old cache> .
FROM scratch AS speech-seed

FROM python:3.12-slim AS build
ARG TTS=piper
ARG START=english
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg espeak-ng libcairo2 curl ca-certificates nodejs npm \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY builder/pyproject.toml builder/pyproject.toml
COPY builder/setara_builder builder/setara_builder
RUN pip install --no-cache-dir ./builder && \
    if [ "$TTS" = "piper" ]; then pip install --no-cache-dir "piper-tts>=1.3"; fi
COPY builder/get_voices.sh builder/get_voices.sh
RUN if [ "$TTS" = "piper" ]; then sh builder/get_voices.sh; fi
RUN mkdir -p tools/web && cd tools/web && npm init -y >/dev/null && npm install --no-audit --no-fund love.js@11.4.1
COPY app app
COPY content content
# The speech cache lives in a cache mount, which is not part of the image: the
# builder copies every clip into packs/*.zip, inside the layer, before the RUN
# ends. Same for the smaller web copies of the clips below.
ARG TTS_SEED_PIPER_DIR=
RUN --mount=type=cache,id=setara-tts,target=/cache/tts \
    --mount=type=bind,from=speech-seed,target=/seed \
    cd builder && SETARA_TTS_CACHE=/cache/tts SETARA_TTS_SEED=/seed SETARA_TTS_SEED_PIPER_DIR="$TTS_SEED_PIPER_DIR" \
    python3 -m setara_builder.cli build --quiet --tts "$TTS"
COPY tools/web tools/web-src
RUN --mount=type=cache,id=setara-web-audio,target=/src/dist/web-work/audio \
    cp -r tools/web-src/make_web.py tools/web-src/index.html tools/web-src/assets tools/web-src/manifest.webmanifest tools/web-src/sw.js tools/web/ && \
    if [ "$START" = "dari" ]; then python3 tools/web/make_web.py --dari; else python3 tools/web/make_web.py; fi

FROM nginx:1.27-alpine
COPY tools/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/dist/web /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q -O /dev/null http://127.0.0.1/version.json || exit 1

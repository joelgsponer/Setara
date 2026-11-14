# Setara in a browser: builds the content packs and the web version from
# source, then serves them as static files.
#
#   docker build -t setara-web .
#   docker run -p 8080:80 setara-web        ->  http://localhost:8080
#
# The first build generates all speech with the stand-in voices and takes
# 20 to 40 minutes on a small server. Build arguments:
#   TTS=piper    stand-in neural voices (default; downloads about 190 MB)
#   TTS=espeak   robotic voices, much faster to build, nothing to download
#   TTS=silent   no speech at all: English captions only, builds in minutes
#   START=english | dari    the language the page starts in

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
RUN cd builder && python3 -m setara_builder.cli build --quiet --tts "$TTS"
COPY tools/web tools/web-src
RUN cp tools/web-src/make_web.py tools/web-src/index.html tools/web/ && \
    if [ "$START" = "dari" ]; then python3 tools/web/make_web.py --dari; else python3 tools/web/make_web.py; fi

FROM nginx:1.27-alpine
COPY tools/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/dist/web /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q -O /dev/null http://127.0.0.1/version.json || exit 1

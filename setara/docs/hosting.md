# Setara in a browser

The same app, compiled to run on a web page, for trying it and showing it.
The product is still the handheld: nothing here changes what runs on the
device. The page starts in [English mode](english-mode.md) and has on-screen
buttons, so it also works on a phone.

## Hosting it with Docker (Dokploy, Coolify, a plain server)

The `Dockerfile` in this folder builds everything from source (content packs,
speech, the web version) and serves the result with nginx on port 80.

On Dokploy:

1. Create an **Application** and connect the Git repository
   `joelgsponer/Setara`, with the branch you want to show.
2. Build type **Dockerfile**. Docker file: `setara/Dockerfile`. Docker context
   path: `setara`.
3. Port **80**. Add your domain; Dokploy provides HTTPS.
4. Deploy. The first build generates all speech and takes 20 to 40 minutes
   on a small server. Later builds reuse Docker's layers unless the content
   changed.

Build arguments (Dokploy: Advanced, Build args):

| Argument | Values | Effect |
| --- | --- | --- |
| `TTS` | `piper` (default) | Stand-in neural voices; downloads about 190 MB |
| | `espeak` | Robotic voices; much faster to build |
| | `silent` | No speech, captions only; builds in a few minutes |
| `START` | `english` (default), `dari` | The language the page starts in |

The server needs outbound access while building (Python and Node packages,
and the voices from huggingface.co when `TTS=piper`). Running it needs
nothing but the static files: about 230 MB.

By hand:

```sh
cd setara
docker build -t setara-web .
docker run -p 8080:80 setara-web      # http://localhost:8080
```

## Without Docker

```sh
cd builder && python3 -m setara_builder.cli build && cd ..
(cd tools/web && npm install love.js@11.4.1)
python3 tools/web/make_web.py         # writes dist/web/
cd dist/web && python3 -m http.server 8000
```

`dist/web/` is plain static files: any web server or static host can serve
it. `--only en-1 --only garden-1` makes a smaller page with just those packs.

## What to know

- **The first load is large**: about 225 MB with all 25 packs, because every
  lesson, picture and clip of speech is in it. The browser's ordinary cache
  keeps it for the next visit. To stay at that size the browser build leaves
  out the slow speech variants (X repeats at normal speed). For a smaller
  page: `make_web.py --light-audio` (speech at 16 kHz, about 160 MB, duller
  sound) or `--only <pack>` for a selection; `--slow` puts the slow variants
  back (about 360 MB).
- **Sound starts after the first click or key press.** Browsers do not let a
  page play sound before that.
- **Keys:** arrows, Z = A, X = B, A = X, S = Y, Q and W = L and R, Enter =
  Start. The "Teacher mode" button under the screen holds L and R for you.
- **Nothing is sent anywhere.** Stars and settings stay in the browser.
- **Robustness differs from the device.** In the browser an internal error
  cannot be caught and restarts are not possible, so a damaged file stops
  the page. The app therefore asks whether a file exists before every read.
- It runs LÖVE 11.4 compiled to WebAssembly by the `love.js` project, with
  plain Lua instead of LuaJIT. It needs WebGL.

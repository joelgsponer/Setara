// Keeps the page and the lessons on the phone, so that the app opens without
// a connection once it has been loaded. The name carries the build: a new
// build is fetched afresh and the old copy is dropped.
const CACHE = 'setara-__BUILD__';
const FILES = ['./', 'index.html', 'game.js', 'love.js', 'love.wasm', 'game.data', 'version.json', 'manifest.webmanifest'];
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).catch(() => {})); });
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {}); }
    return res;
  })));
});

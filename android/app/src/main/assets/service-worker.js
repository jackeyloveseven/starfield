// Bump CACHE_VERSION together with version.json on every web release.
const CACHE_PREFIX = 'starfield-focus-';
const CACHE_VERSION = 'v1.9.2-b131';
const CACHE_NAME = CACHE_PREFIX + CACHE_VERSION;
const SHELL = './starfield.html';
const PRECACHE = [
  SHELL,
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './libs/three.min.js',
  './libs/OrbitControls.js',
  './libs/tween.umd.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await Promise.allSettled(
      PRECACHE.map((url) => cache.add(new Request(url, { cache: 'reload' })))
    );
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(
      keys
        .filter((key) => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
        .map((key) => caches.delete(key))
    );
    await self.clients.claim();
  })());
});

async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  try {
    // A release-scoped URL defeats any stale browser/CDN copy on browser restart.
    const networkUrl = new URL(request.url);
    networkUrl.searchParams.set('__sw', CACHE_VERSION);
    const response = await fetch(networkUrl.toString(), { cache: 'reload' });
    if (response.ok) {
      cache.put(request, response.clone()).catch(() => {});
    }
    return response;
  } catch (error) {
    return (await cache.match(request)) ||
      (await cache.match(SHELL)) ||
      Response.error();
  }
}

async function staleWhileRevalidate(event, request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  const update = fetch(request, { cache: 'no-cache' }).then((response) => {
    if (response.ok) {
      cache.put(request, response.clone()).catch(() => {});
    }
    return response;
  });

  event.waitUntil(update.then(() => undefined, () => undefined));
  if (cached) return cached;
  return (await update.catch(() => null)) || Response.error();
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  // OTA metadata must never be served from a stale cache.
  if (url.pathname.endsWith('/version.json')) return;
  if (request.headers.has('range')) return;

  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request));
  } else {
    event.respondWith(staleWhileRevalidate(event, request));
  }
});

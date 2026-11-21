const CACHE_VERSION = 'osteomyo-v5';

// App shell: everything index.html needs to render, so a first visit followed by
// an offline reload works. Installed atomically (install fails if any is missing).
const SHELL_URLS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './favicon.svg',
  './icons/icon-192.png',
  './assets/index-eK-aaN5l.js',
  './assets/anatomyData-Cqk5KDrX.js',
  './assets/organsNervousData-D8Vb_utx.js',
  './assets/three-JquuAaC5.js',
  './assets/index-DgeA0hN7.css',
  './extras/credits.css',
  './extras/credits.js',
  './models/manifest.json'
];

// Hashed build output (name-<hash>.js/css) never changes for a given URL.
const HASHED_RE = /-[A-Za-z0-9_-]{8}\.(?:js|css)$/;

self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_VERSION);
      await cache.addAll(SHELL_URLS);
      // Warm the 3D models in the background; failures here must not block install.
      event.waitUntil(warmModels(cache).catch(() => {}));
      await self.skipWaiting();
    })()
  );
});

async function warmModels(cache) {
  const res = await fetch('./models/manifest.json', { cache: 'no-cache' });
  if (!res.ok) return;
  const manifest = await res.json();
  for (const name of Object.keys(manifest.models || {})) {
    const url = `./models/${name}.bin`;
    if (await cache.match(url)) continue;
    try {
      const r = await fetch(url);
      if (r.ok) await cache.put(url, r);
    } catch (_) { /* offline or flaky: it will be cached on first use instead */ }
  }
}

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_VERSION).map((key) => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// The app asks for a .bin for every structure, but only the models listed in
// models/manifest.json exist. Answer the rest with an instant 404 (the app already
// falls back to its built-in geometry) instead of making ~190 doomed network requests.
let knownModels = null;
async function getKnownModels() {
  if (knownModels) return knownModels;
  try {
    const res = await caches.match('./models/manifest.json');
    if (!res) return null; // can't tell: let requests through
    knownModels = new Set(Object.keys((await res.json()).models || {}));
  } catch (_) { return null; }
  return knownModels;
}

// Fetch and store a fresh copy. Resolves to the response; storing never blocks it.
function fetchAndCache(req, init) {
  return fetch(init ? req.url : req, init).then((res) => {
    if (res && res.status === 200) {
      const copy = res.clone();
      caches.open(CACHE_VERSION).then((cache) => cache.put(init ? req.url : req, copy)).catch(() => {});
      if (/\/models\/manifest\.json$/.test(new URL(req.url).pathname)) knownModels = null;
    }
    return res;
  });
}

function staleWhileRevalidateResponse(event, req) {
  return caches.match(req).then((cached) => {
    const network = fetchAndCache(req).catch(() => cached);
    if (cached) {
      event.waitUntil(network.catch(() => {}));
      return cached;
    }
    return network.then((res) => res || Response.error());
  });
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Navigations: network-first, but fall back to the cached shell if the network
  // is offline or slower than 3.5s. A late network response still refreshes the cache.
  if (req.mode === 'navigate') {
    event.respondWith(
      (async () => {
        const fallback = () => caches.match('./index.html');
        // no-cache: revalidate with the server instead of trusting a heuristically-fresh HTTP cache entry
        const network = fetchAndCache(req, { cache: 'no-cache', credentials: 'same-origin' });
        const timeout = new Promise((resolve) => setTimeout(() => resolve(null), 3500));
        try {
          const first = await Promise.race([network, timeout]);
          if (first) return first;
          const cached = await fallback();
          if (cached) {
            event.waitUntil(network.catch(() => {}));
            return cached;
          }
          return await network; // nothing cached yet: keep waiting for the network
        } catch (_) {
          return (await fallback()) || new Response('Offline - please reconnect', { status: 503 });
        }
      })()
    );
    return;
  }

  // Hashed build output is immutable: cache-first.
  if (HASHED_RE.test(url.pathname)) {
    event.respondWith(
      caches.match(req).then((cached) => cached || fetchAndCache(req))
    );
    return;
  }

  // Models the manifest doesn't list don't exist: skip the network.
  const modelMatch = url.pathname.match(/\/models\/([^/]+)\.bin$/);
  if (modelMatch) {
    event.respondWith(
      getKnownModels().then((known) =>
        known && !known.has(modelMatch[1])
          ? new Response(null, { status: 404, statusText: 'Model not in manifest' })
          : staleWhileRevalidateResponse(event, req)
      )
    );
    return;
  }

  // Everything else (models/*.bin, credits.*, icons, ...) is not content-hashed, so
  // serve the cached copy instantly and refresh it in the background.
  event.respondWith(staleWhileRevalidateResponse(event, req));
});

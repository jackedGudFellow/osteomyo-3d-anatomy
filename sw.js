const CACHE_VERSION = 'osteomyo-v4';
const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './favicon.svg',
  './icons/icon-192.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_VERSION) {
            return caches.delete(key);
          }
        })
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Cross-origin: let standard network handle
  if (url.origin !== self.location.origin) return;

  // Navigation requests: network-first with timeout fallback to cached index
  if (req.mode === 'navigate') {
    event.respondWith(
      new Promise((resolve) => {
        let timedOut = false;
        const timer = setTimeout(() => {
          timedOut = true;
          caches.match('./index.html').then((cached) => {
            if (cached) resolve(cached);
          });
        }, 3500);

        fetch(req)
          .then((response) => {
            clearTimeout(timer);
            if (!timedOut) {
              const resClone = response.clone();
              caches.open(CACHE_VERSION).then((cache) => cache.put(req, resClone));
              resolve(response);
            }
          })
          .catch(() => {
            clearTimeout(timer);
            caches.match('./index.html').then((cached) => {
              if (cached) resolve(cached);
              else resolve(new Response('Offline - please reconnect', { status: 503 }));
            });
          });
      })
    );
    return;
  }

  // Hashed / Versioned assets & static 3D models: Cache-First
  if (url.pathname.includes('/assets/') || url.pathname.includes('/models/')) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((res) => {
          if (res && res.status === 200) {
            const resClone = res.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(req, resClone));
          }
          return res;
        });
      })
    );
    return;
  }

  // Other assets: Stale-While-Revalidate
  event.respondWith(
    caches.match(req).then((cached) => {
      const fetchPromise = fetch(req)
        .then((networkRes) => {
          if (networkRes && networkRes.status === 200) {
            const resClone = networkRes.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(req, resClone));
          }
          return networkRes;
        })
        .catch(() => cached);
      return cached || fetchPromise;
    })
  );
});

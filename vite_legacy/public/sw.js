// Service Worker — Cẩm nang Cá biển Việt Nam
// Strategy: App Shell (cache-first) + Data (stale-while-revalidate)

const CACHE_VERSION = 'v1';
const SHELL_CACHE = `shell-${CACHE_VERSION}`;
const DATA_CACHE = `data-${CACHE_VERSION}`;

// App shell — cached on install, served cache-first
const SHELL_ASSETS = [
  '/',
  '/index.html',
  '/browse.html',
  '/species.html',
  '/tap.html',
  '/assets/icons/icon-192.png',
];

// Data files — stale-while-revalidate
const DATA_URLS = [
  '/data/species.json',
  '/data/taxonomy_tree.json',
  '/data/fishbase_sync.json',
];

// Install: pre-cache app shell
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(SHELL_CACHE)
      .then(cache => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate: purge old caches
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== SHELL_CACHE && k !== DATA_CACHE)
            .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// Fetch strategy
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  // Skip non-GET
  if (e.request.method !== 'GET') return;

  // Data files: stale-while-revalidate
  if (DATA_URLS.some(d => url.pathname.endsWith(d.replace('/', '')))) {
    e.respondWith(
      caches.open(DATA_CACHE).then(cache =>
        cache.match(e.request).then(cached => {
          const fetched = fetch(e.request).then(response => {
            if (response.ok) cache.put(e.request, response.clone());
            return response;
          }).catch(() => cached); // network fail → use cache
          return cached || fetched;
        })
      )
    );
    return;
  }

  // App shell + other assets: cache-first, fallback to network
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(response => {
        // Cache successful responses for CSS/JS/images
        if (response.ok && (
          url.pathname.endsWith('.css') ||
          url.pathname.endsWith('.js') ||
          url.pathname.endsWith('.png') ||
          url.pathname.endsWith('.html')
        )) {
          const clone = response.clone();
          caches.open(SHELL_CACHE).then(cache => cache.put(e.request, clone));
        }
        return response;
      });
    }).catch(() => {
      // Offline fallback for navigation
      if (e.request.mode === 'navigate') {
        return caches.match('/index.html');
      }
    })
  );
});

// Listen for messages from the app
self.addEventListener('message', (e) => {
  if (e.data === 'skipWaiting') self.skipWaiting();
});

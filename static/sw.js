// Service Worker v2 - Force Clear Cache
const CACHE_NAME = 'moodbloom-cache-v2';

self.addEventListener('install', (e) => {
    console.log('[Service Worker] Installed v2');
    self.skipWaiting(); // Force the waiting service worker to become the active one
});

self.addEventListener('activate', (e) => {
    console.log('[Service Worker] Activated v2');
    // Clear old caches
    e.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    return self.clients.claim(); // Take control of all open pages immediately
});

self.addEventListener('fetch', (e) => {
    // Return early if it's a Chrome DevTools or internal request
    if (e.request.url.startsWith('chrome-extension') || e.request.url.includes('com.chrome.devtools')) {
        return;
    }

    // For now, bypass cache for HTML to ensure sync during development
    if (e.request.mode === 'navigate') {
        e.respondWith(fetch(e.request));
        return;
    }

    e.respondWith(
        caches.match(e.request).then((response) => {
            return response || fetch(e.request);
        })
    );
});
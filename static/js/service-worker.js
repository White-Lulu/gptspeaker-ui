const CACHE_NAME = 'module-cache-v1';
const urlsToCache = [
    '/static/js/service-worker.js',
    '/static/js/utils.js',
    '/static/js/speaker.js',
    '/static/js/notes.js',
    '/static/js/setting.js',
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Cache opened, starting to cache files');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                console.log('All files successfully cached');
                self.skipWaiting();
            })
            .catch(error => {
                console.log('Cache failed:', error);
            })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    console.log('Returning from cache:', event.request.url);
                    return response;
                }
                console.log('Loading from network:', event.request.url);
                return fetch(event.request);
            })
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        clients.claim()
    );
});
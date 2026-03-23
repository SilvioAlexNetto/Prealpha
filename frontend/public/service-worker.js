const CACHE_NAME = "healthcare-cache-v1";
const urlsToCache = [
    "/",
    "/index.html",
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener("fetch", event => {
    const url = new URL(event.request.url);

    // 🚨 IGNORA chamadas para API externa
    if (url.origin !== location.origin) {
        return; // deixa o browser fazer a requisição normal
    }

    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
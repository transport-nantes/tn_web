console.log("Service worker script started")
const staticMobilito = 'mobilito';


self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(staticMobilito)
        .then(function(cache) {
            return cache.addAll(assets);
        })
    );
});

self.addEventListener("fetch", fetchEvent => {
    fetchEvent.respondWith(
      caches.match(fetchEvent.request).then(res => {
        return res || fetch(fetchEvent.request)
      })
    )
  })

/* عامل الخدمة — يجعل «مصاريفي» يعمل بلا إنترنت.
   الاستراتيجية: الشبكة أولًا مع الرجوع للمخزّن عند انقطاعها،
   حتى لا يعلق المستخدم على نسخة قديمة بعد كل تحديث. */

const CACHE = 'masareefi-v3';
const SHELL = [
  './', './index.html', './manifest.webmanifest', './icon.svg',
  './icon-192.png', './icon-512.png',
  './icon-maskable-512.png', './apple-touch-icon.png',
];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).catch(() => {}));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;

  // اطلبات غير GET أو خارج نطاق التطبيق (Firebase مثلًا) تمرّ كما هي
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;

  e.respondWith(
    fetch(req)
      .then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(req).then(hit => hit || caches.match('./index.html')))
  );
});

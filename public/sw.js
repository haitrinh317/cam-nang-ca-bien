// Service worker tối giản cho PWA (Chrome/Edge cài đặt được).
// ponytail: chỉ cache vỏ offline + tài nguyên tĩnh; KHÔNG cache dữ liệu loài/HTML (dữ liệu đổi liên tục).
// Đổi VERSION khi sửa file này để xóa cache cũ.
const VERSION = 'svbvn-v1'
const PRECACHE = ['/offline.html', '/icons/icon-192x192.png', '/icons/icon-512x512.png', '/logo.png']

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()))
})

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', (e) => {
  const req = e.request
  const url = new URL(req.url)
  if (req.method !== 'GET' || url.origin !== self.location.origin) return
  if (url.pathname.startsWith('/admin') || url.pathname.startsWith('/api')) return

  // Điều hướng trang: luôn lấy mạng; mất mạng thì hiện trang offline
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).catch(() => caches.match('/offline.html')))
    return
  }

  // Tài nguyên tĩnh bất biến: cache-first
  if (url.pathname.startsWith('/_next/static/') || url.pathname.startsWith('/icons/')) {
    e.respondWith(
      caches.match(req).then((hit) => hit || fetch(req).then((res) => {
        const copy = res.clone()
        caches.open(VERSION).then((c) => c.put(req, copy))
        return res
      }))
    )
  }
})

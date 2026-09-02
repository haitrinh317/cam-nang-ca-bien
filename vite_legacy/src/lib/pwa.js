// PWA: Register Service Worker + update toast
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').then(reg => {
    setInterval(() => reg.update(), 30 * 60 * 1000)

    reg.addEventListener('updatefound', () => {
      const w = reg.installing
      w.addEventListener('statechange', () => {
        if (w.state === 'activated' && navigator.serviceWorker.controller) {
          const t = document.createElement('div')
          t.className = 'pwa-update-toast'
          t.innerHTML = '<span>🔄 Phiên bản mới</span><button onclick="location.reload()">Cập nhật</button><button onclick="this.parentElement.remove()" class="dismiss">✕</button>'
          document.body.appendChild(t)
          requestAnimationFrame(() => t.classList.add('visible'))
        }
      })
    })
  }).catch(() => {})
}

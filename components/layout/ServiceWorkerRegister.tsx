'use client'

import { useEffect } from 'react'

// Đăng ký service worker để Chrome/Edge cho phép cài đặt PWA
export function ServiceWorkerRegister() {
  useEffect(() => {
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      navigator.serviceWorker.register('/sw.js').catch(() => {})
    }
  }, [])
  return null
}

'use client'

import { useState, useEffect } from 'react'
import { Download, X, Share } from 'lucide-react'
import '@/styles/pwa.css'

// ponytail: Safari PWA APIs not in standard TS lib
declare global {
  interface Navigator { standalone?: boolean }
  interface Window { MSStream?: unknown }
  interface BeforeInstallPromptEvent extends Event {
    prompt(): Promise<void>
    userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
  }
}

// Nút "Cài đặt" trên thanh Nav. Không tự bật popup; chỉ hiện khi cài được.
export function PwaInstallPrompt() {
  const [isIos, setIsIos] = useState(false)
  const [installed, setInstalled] = useState(true) // ẩn cho đến khi biết chắc
  const [sheetOpen, setSheetOpen] = useState(false)
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)

  useEffect(() => {
    const isStandalone =
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true
    if (isStandalone) return

    // eslint-disable-next-line react-hooks/set-state-in-effect -- browser-only state read after hydration
    setInstalled(false)
    setIsIos(/iPad|iPhone|iPod/.test(window.navigator.userAgent) && !window.MSStream)

    const onPrompt = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e as BeforeInstallPromptEvent)
    }
    const onInstalled = () => setInstalled(true)
    window.addEventListener('beforeinstallprompt', onPrompt)
    window.addEventListener('appinstalled', onInstalled)
    return () => {
      window.removeEventListener('beforeinstallprompt', onPrompt)
      window.removeEventListener('appinstalled', onInstalled)
    }
  }, [])

  const handleClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt()
      await deferredPrompt.userChoice
      setDeferredPrompt(null)
    } else {
      setSheetOpen(true)
    }
  }

  if (installed || (!deferredPrompt && !isIos)) return null

  return (
    <>
      <button type="button" className="pwa-nav-btn" onClick={handleClick} aria-label="Cài đặt ứng dụng SVBVN">
        <Download size={16} />
        <span>Cài đặt</span>
      </button>

      {sheetOpen && (
        <div className="pwa-prompt-backdrop" onClick={() => setSheetOpen(false)} role="dialog" aria-modal="true" aria-labelledby="pwa-title">
          <div className="pwa-prompt-sheet" onClick={e => e.stopPropagation()}>
            <button type="button" className="pwa-prompt-close" onClick={() => setSheetOpen(false)} aria-label="Đóng hướng dẫn">
              <X size={18} />
            </button>
            <div className="pwa-prompt-header">
              <div className="pwa-prompt-app-icon">
                <img src="/icons/icon-192x192.png" alt="SVBVN App Icon" width={52} height={52} style={{ borderRadius: 12, display: 'block' }} />
              </div>
              <div className="pwa-prompt-header-text">
                <h3 id="pwa-title" className="pwa-prompt-title">Cài đặt ứng dụng SVBVN</h3>
                <p className="pwa-prompt-subtitle">Hướng dẫn trên iPhone / iPad</p>
              </div>
            </div>
            <div className="pwa-prompt-body">
              <div className="pwa-prompt-steps">
                <div className="pwa-step-item">
                  <span className="pwa-step-number">1</span>
                  <span className="pwa-step-content">
                    Nhấn nút <strong>Chia sẻ</strong>{' '}
                    <span className="pwa-icon-pill"><Share size={15} /></span>{' '}
                    ở thanh công cụ Safari.
                  </span>
                </div>
                <div className="pwa-step-item">
                  <span className="pwa-step-number">2</span>
                  <span className="pwa-step-content">Chọn <strong>&quot;Thêm vào Màn hình chính&quot;</strong>.</span>
                </div>
                <div className="pwa-step-item">
                  <span className="pwa-step-number">3</span>
                  <span className="pwa-step-content">Nhấn <strong>&quot;Thêm&quot;</strong> để hoàn tất.</span>
                </div>
              </div>
            </div>
            <div className="pwa-prompt-footer">
              <button type="button" className="pwa-btn-primary" onClick={() => setSheetOpen(false)}>Đã hiểu</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

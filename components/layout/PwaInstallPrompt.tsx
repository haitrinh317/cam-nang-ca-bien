'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'

export function PwaInstallPrompt() {
  const [isOpen, setIsOpen] = useState(false)
  const [isIos, setIsIos] = useState(false)
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null)

  useEffect(() => {
    // 1. Kiểm tra nếu đang mở trong ứng dụng PWA đã cài đặt (Standalone Mode)
    const isStandalone =
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as any).standalone === true
    if (isStandalone) return

    // 2. Kiểm tra nếu người dùng đã bấm bỏ qua gần đây (trong vòng 14 ngày)
    const dismissedTime = localStorage.getItem('svbvn_pwa_dismissed')
    if (dismissedTime) {
      const daysPassed = (Date.now() - parseInt(dismissedTime, 10)) / (1000 * 60 * 60 * 24)
      if (daysPassed < 14) return
    }

    // 3. Nhận diện thiết bị iOS
    const ua = window.navigator.userAgent
    const isAppleDevice = /iPad|iPhone|iPod/.test(ua) && !(window as any).MSStream
    setIsIos(isAppleDevice)

    // 4. Bắt sự kiện beforeinstallprompt trên Android Chrome / Chromium
    const handleBeforeInstall = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e)
    }
    window.addEventListener('beforeinstallprompt', handleBeforeInstall)

    // 5. Hiển thị popup sau 3 giây để người dùng không bị bất ngờ
    const timer = setTimeout(() => {
      setIsOpen(true)
    }, 3000)

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall)
      clearTimeout(timer)
    }
  }, [])

  const handleDismiss = () => {
    localStorage.setItem('svbvn_pwa_dismissed', Date.now().toString())
    setIsOpen(false)
  }

  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt()
      const { outcome } = await deferredPrompt.userChoice
      if (outcome === 'accepted') {
        handleDismiss()
      }
      setDeferredPrompt(null)
    } else {
      handleDismiss()
    }
  }

  if (!isOpen) return null

  return (
    <div className="pwa-prompt-backdrop" onClick={handleDismiss} role="dialog" aria-modal="true" aria-labelledby="pwa-title">
      <div className="pwa-prompt-sheet" onClick={e => e.stopPropagation()}>
        {/* Nút đóng */}
        <button
          type="button"
          className="pwa-prompt-close"
          onClick={handleDismiss}
          aria-label="Đóng hướng dẫn"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>

        {/* Header với Icon App */}
        <div className="pwa-prompt-header">
          <div className="pwa-prompt-app-icon">
            <img
              src="/icons/icon-192x192.png"
              alt="SVBVN App Icon"
              width={52}
              height={52}
              style={{ borderRadius: 12, display: 'block' }}
            />
          </div>
          <div className="pwa-prompt-header-text">
            <span className="pwa-prompt-badge">Ứng dụng Web (PWA)</span>
            <h3 id="pwa-title" className="pwa-prompt-title">Cài đặt ứng dụng SVBVN</h3>
            <p className="pwa-prompt-subtitle">Tra cứu 2.436+ loài sinh vật biển tiện lợi ngay trên màn hình chính</p>
          </div>
        </div>

        {/* Hướng dẫn chi tiết theo hệ điều hành */}
        <div className="pwa-prompt-body">
          {isIos ? (
            <div className="pwa-prompt-steps">
              <p className="pwa-prompt-guide-lead">Hướng dẫn cài đặt trên <strong>iPhone / iPad</strong>:</p>
              <div className="pwa-step-item">
                <span className="pwa-step-number">1</span>
                <span className="pwa-step-content">
                  Nhấn vào nút <strong>Chia sẻ</strong>{' '}
                  <span className="pwa-icon-pill">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
                      <polyline points="16 6 12 2 8 6"/>
                      <line x1="12" y1="2" x2="12" y2="15"/>
                    </svg>
                  </span>{' '}
                  ở thanh công cụ dưới màn hình Safari.
                </span>
              </div>
              <div className="pwa-step-item">
                <span className="pwa-step-number">2</span>
                <span className="pwa-step-content">
                  Cuộn xuống danh sách tùy chọn và chọn <strong>"Thêm vào Màn hình chính"</strong> (Add to Home Screen).
                </span>
              </div>
              <div className="pwa-step-item">
                <span className="pwa-step-number">3</span>
                <span className="pwa-step-content">
                  Nhấn <strong>"Thêm"</strong> ở góc trên bên phải để hoàn tất. Biểu tượng <strong>SVBVN</strong> sẽ xuất hiện trên điện thoại của bạn!
                </span>
              </div>
            </div>
          ) : (
            <div className="pwa-prompt-steps">
              <p className="pwa-prompt-guide-lead">Hướng dẫn cài đặt trên <strong>Android / Thiết bị khác</strong>:</p>
              {deferredPrompt ? (
                <div className="pwa-step-item">
                  <span className="pwa-step-number">✓</span>
                  <span className="pwa-step-content">
                    Thiết bị của bạn đã sẵn sàng! Nhấn nút <strong>"Cài đặt ngay"</strong> bên dưới để đưa ứng dụng <strong>SVBVN</strong> ra màn hình chính.
                  </span>
                </div>
              ) : (
                <>
                  <div className="pwa-step-item">
                    <span className="pwa-step-number">1</span>
                    <span className="pwa-step-content">
                      Nhấn vào biểu tượng <strong>Menu 3 chấm (⋮)</strong> ở góc trên bên phải trình duyệt Chrome.
                    </span>
                  </div>
                  <div className="pwa-step-item">
                    <span className="pwa-step-number">2</span>
                    <span className="pwa-step-content">
                      Chọn mục <strong>"Cài đặt ứng dụng"</strong> hoặc <strong>"Thêm vào màn hình chính"</strong>.
                    </span>
                  </div>
                  <div className="pwa-step-item">
                    <span className="pwa-step-number">3</span>
                    <span className="pwa-step-content">
                      Nhấn <strong>"Cài đặt"</strong> để tạo biểu tượng <strong>SVBVN</strong> mở toàn màn hình siêu tốc!
                    </span>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* Nút hành động */}
        <div className="pwa-prompt-footer">
          <button
            type="button"
            className="pwa-btn-secondary"
            onClick={handleDismiss}
          >
            Để sau
          </button>
          {deferredPrompt ? (
            <button
              type="button"
              className="pwa-btn-primary"
              onClick={handleInstallClick}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <span>Cài đặt ngay</span>
            </button>
          ) : (
            <button
              type="button"
              className="pwa-btn-primary"
              onClick={handleDismiss}
            >
              <span>Đã hiểu</span>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

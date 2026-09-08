'use client'
import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Fish, Leaf, Shrimp, Layers, X, ArrowRight, Sparkles } from 'lucide-react'

interface CollectionItem {
  slug: string
  name: string
  nameEn: string
  desc: string
  stats: string
  icon: React.ReactNode
  accent: string
  available: boolean
}

const COLLECTIONS_LIST: CollectionItem[] = [
  {
    slug: 'ca-bien',
    name: 'Cá biển Việt Nam',
    nameEn: 'Marine Fish of Vietnam',
    desc: 'Cá sụn, cá xương rạn san hô và đáy',
    stats: '1,764 loài • 6 tập',
    icon: <Fish size={24} color="#6fffe8" />,
    accent: '#6fffe8',
    available: true,
  },
  {
    slug: 'thuc-vat-bien',
    name: 'Thực vật & Rong biển',
    nameEn: 'Marine Plants & Algae',
    desc: 'Thanh tảo, lục tảo, hồng tảo ven bờ',
    stats: '672 loài • 2 tập',
    icon: <Leaf size={24} color="#a7f3d0" />,
    accent: '#a7f3d0',
    available: true,
  },
  {
    slug: 'giap-xac',
    name: 'Giáp xác biển',
    nameEn: 'Marine Crustaceans',
    desc: 'Tôm biển, tôm hùm, tôm tít, cua, ghẹ',
    stats: '132 loài • 1 tập',
    icon: <Shrimp size={24} color="#fca5a5" />,
    accent: '#fca5a5',
    available: true,
  },
  {
    slug: 'ran-bien',
    name: 'Rắn biển Việt Nam',
    nameEn: 'Sea Snakes in Vietnam',
    desc: 'Đẻn biển, rắn rầm ri & độc tố học',
    stats: '27 loài • Chuyên khảo',
    icon: <span style={{ fontSize: '24px', lineHeight: 1 }}>🐍</span>,
    accent: '#f59e0b',
    available: true,
  },
  {
    slug: 'san-ho',
    name: 'San hô biển',
    nameEn: 'Marine Corals',
    desc: 'San hô cứng tạo rạn, san hô mềm',
    stats: 'Dự kiến 350+ loài',
    icon: <span style={{ fontSize: '24px', lineHeight: 1 }}>🪸</span>,
    accent: '#fb7185',
    available: false,
  },
  {
    slug: 'than-mem',
    name: 'Động vật thân mềm',
    nameEn: 'Marine Mollusca',
    desc: 'Ốc, sò, mực, bạch tuộc biển',
    stats: 'Dự kiến 500+ loài',
    icon: <span style={{ fontSize: '24px', lineHeight: 1 }}>🐚</span>,
    accent: '#cbd5e1',
    available: false,
  },
]

export function BottomNav() {
  const pathname = usePathname()
  const [isHidden, setIsHidden] = useState(false)
  const [isSheetOpen, setIsSheetOpen] = useState(false)
  const lastScrollY = useRef(0)

  // Close sheet on route change
  useEffect(() => {
    setIsHidden(false)
    setIsSheetOpen(false)
  }, [pathname])

  // Lock body scroll when sheet is open
  useEffect(() => {
    if (isSheetOpen) {
      const originalStyle = window.getComputedStyle(document.body).overflow
      document.body.style.overflow = 'hidden'
      return () => {
        document.body.style.overflow = originalStyle
      }
    }
  }, [isSheetOpen])

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isSheetOpen) {
        setIsSheetOpen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isSheetOpen])

  // Auto-hide floating dock on scroll down
  useEffect(() => {
    let ticking = false

    const handleScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const currentY = window.scrollY || window.pageYOffset || 0
          const diff = currentY - lastScrollY.current

          const docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.offsetHeight
          )
          const windowHeight = window.innerHeight || document.documentElement.clientHeight || 0
          const isNearBottom = currentY + windowHeight >= docHeight - 70

          if (isSheetOpen) {
            // Keep visible if sheet is open
            setIsHidden(false)
          } else if (currentY <= 40 || isNearBottom) {
            setIsHidden(false)
          } else if (diff > 12 && currentY > 80) {
            setIsHidden(true)
          } else if (diff < -8) {
            setIsHidden(false)
          }

          lastScrollY.current = Math.max(0, currentY)
          ticking = false
        })
        ticking = true
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [isSheetOpen])

  // Don't show on admin or auth pages
  if (pathname.startsWith('/admin') || pathname.startsWith('/login')) return null

  // Check active states
  const isHomeActive = pathname === '/'
  const isFishActive = pathname === '/ca-bien' || pathname.startsWith('/ca-bien/')
  const isAlgaeActive = pathname === '/thuc-vat-bien' || pathname.startsWith('/thuc-vat-bien/')

  // Is viewing other collections?
  const isCrustaceanActive = pathname === '/giap-xac' || pathname.startsWith('/giap-xac/')
  const isSnakeActive = pathname === '/ran-bien' || pathname.startsWith('/ran-bien/')
  const isOtherActive = isCrustaceanActive || isSnakeActive

  // Dynamic 4th tab presentation based on current page
  let fourthTabIcon = <Layers size={20} strokeWidth={2} aria-hidden="true" />
  let fourthTabLabel = 'Nhóm khác'
  if (isCrustaceanActive) {
    fourthTabIcon = <Shrimp size={20} strokeWidth={2} aria-hidden="true" />
    fourthTabLabel = 'Giáp xác'
  } else if (isSnakeActive) {
    fourthTabIcon = <span style={{ fontSize: '18px', lineHeight: 1 }} aria-hidden="true">🐍</span>
    fourthTabLabel = 'Rắn biển'
  }

  return (
    <>
      {/* ─── Floating Island Dock (4 Balanced Tabs) ─── */}
      <nav
        className={`bottom-nav${isHidden && !isSheetOpen ? ' is-hidden' : ''}`}
        aria-label="Menu chính"
      >
        {/* Tab 1: Trang chủ */}
        <Link
          href="/"
          className={`bottom-nav__tab${isHomeActive ? ' active' : ''}`}
          aria-current={isHomeActive ? 'page' : undefined}
          onClick={() => setIsSheetOpen(false)}
        >
          <span className="bottom-nav__icon">
            <Home size={20} strokeWidth={2} aria-hidden="true" />
          </span>
          <span className="bottom-nav__label">Trang chủ</span>
          {isHomeActive && <span className="bottom-nav__dot" aria-hidden="true" />}
        </Link>

        {/* Tab 2: Cá biển */}
        <Link
          href="/ca-bien"
          className={`bottom-nav__tab${isFishActive ? ' active' : ''}`}
          aria-current={isFishActive ? 'page' : undefined}
          onClick={() => setIsSheetOpen(false)}
        >
          <span className="bottom-nav__icon">
            <Fish size={20} strokeWidth={2} aria-hidden="true" />
          </span>
          <span className="bottom-nav__label">Cá biển</span>
          {isFishActive && <span className="bottom-nav__dot" aria-hidden="true" />}
        </Link>

        {/* Tab 3: Rong biển */}
        <Link
          href="/thuc-vat-bien"
          className={`bottom-nav__tab${isAlgaeActive ? ' active' : ''}`}
          aria-current={isAlgaeActive ? 'page' : undefined}
          onClick={() => setIsSheetOpen(false)}
        >
          <span className="bottom-nav__icon">
            <Leaf size={20} strokeWidth={2} aria-hidden="true" />
          </span>
          <span className="bottom-nav__label">Rong biển</span>
          {isAlgaeActive && <span className="bottom-nav__dot" aria-hidden="true" />}
        </Link>

        {/* Tab 4: Nhóm khác / Mở Bottom Sheet */}
        <button
          type="button"
          onClick={() => setIsSheetOpen(prev => !prev)}
          className={`bottom-nav__tab${isOtherActive || isSheetOpen ? ' active' : ''}`}
          aria-haspopup="dialog"
          aria-expanded={isSheetOpen}
          aria-label="Xem tất cả nhóm sinh vật biển"
        >
          <span className="bottom-nav__icon">
            {fourthTabIcon}
            {!isOtherActive && (
              <span className="bottom-nav__badge-dot" aria-hidden="true" />
            )}
          </span>
          <span className="bottom-nav__label">{fourthTabLabel}</span>
          {(isOtherActive || isSheetOpen) && (
            <span className="bottom-nav__dot" aria-hidden="true" />
          )}
        </button>
      </nav>

      {/* ─── Bottom Sheet Modal (Drawer danh mục sinh vật) ─── */}
      <div
        className={`bottom-sheet-backdrop${isSheetOpen ? ' is-open' : ''}`}
        onClick={() => setIsSheetOpen(false)}
        aria-hidden={!isSheetOpen}
      />

      <div
        className={`bottom-sheet-container${isSheetOpen ? ' is-open' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="bottom-sheet-title"
      >
        {/* Drag handle */}
        <div className="bottom-sheet__handle-wrapper" onClick={() => setIsSheetOpen(false)}>
          <div className="bottom-sheet__handle" />
        </div>

        {/* Header */}
        <div className="bottom-sheet__header">
          <div>
            <h2 id="bottom-sheet-title" className="bottom-sheet__title">
              Nhóm Sinh Vật Biển
            </h2>
            <p className="bottom-sheet__subtitle">
              Hệ sinh thái số hóa • 2,595 loài tại vùng biển Việt Nam
            </p>
          </div>
          <button
            type="button"
            className="bottom-sheet__close-btn"
            onClick={() => setIsSheetOpen(false)}
            aria-label="Đóng bảng chọn nhóm"
          >
            <X size={18} />
          </button>
        </div>

        {/* Collection Grid */}
        <div className="bottom-sheet__grid">
          {COLLECTIONS_LIST.map(item => {
            const isItemActive =
              item.available &&
              (pathname === `/${item.slug}` || pathname.startsWith(`/${item.slug}/`))

            if (!item.available) {
              return (
                <div key={item.slug} className="bottom-sheet__card is-disabled">
                  <div className="bottom-sheet__card-header">
                    <span className="bottom-sheet__card-icon">{item.icon}</span>
                    <span className="bottom-sheet__tag">Sắp có</span>
                  </div>
                  <h3 className="bottom-sheet__card-title">{item.name}</h3>
                  <p className="bottom-sheet__card-desc">{item.desc}</p>
                  <span className="bottom-sheet__card-stats">{item.stats}</span>
                </div>
              )
            }

            return (
              <Link
                key={item.slug}
                href={`/${item.slug}`}
                onClick={() => setIsSheetOpen(false)}
                className={`bottom-sheet__card${isItemActive ? ' is-active' : ''}`}
                style={
                  isItemActive
                    ? { borderColor: item.accent, boxShadow: `0 0 16px ${item.accent}33` }
                    : undefined
                }
              >
                <div className="bottom-sheet__card-header">
                  <span className="bottom-sheet__card-icon">{item.icon}</span>
                  {isItemActive ? (
                    <span
                      className="bottom-sheet__tag is-current"
                      style={{ background: `${item.accent}26`, color: item.accent }}
                    >
                      Đang xem
                    </span>
                  ) : (
                    <ArrowRight size={16} className="bottom-sheet__card-arrow" />
                  )}
                </div>
                <h3 className="bottom-sheet__card-title">{item.name}</h3>
                <p className="bottom-sheet__card-desc">{item.desc}</p>
                <span className="bottom-sheet__card-stats" style={{ color: item.accent }}>
                  {item.stats}
                </span>
              </Link>
            )
          })}
        </div>

        {/* Footer shortcuts */}
        <div className="bottom-sheet__footer">
          <Link
            href="/ca-bien/taxonomy"
            onClick={() => setIsSheetOpen(false)}
            className="bottom-sheet__footer-link"
          >
            <Sparkles size={15} color="#00f0d0" />
            <span>Cây Phân Loại Học Toàn Diện</span>
          </Link>
        </div>
      </div>
    </>
  )
}

'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { t } from '@/lib/i18n'
import HeaderControls from './HeaderControls'
import { Fish, Leaf, Shrimp, ChevronDown, Layers } from 'lucide-react'

interface DropdownCollection {
  slug: string
  nameVn: string
  nameEn: string
  stats: string
  icon: React.ReactNode
  accentColor: string
}

const DROPDOWN_COLLECTIONS: DropdownCollection[] = [
  {
    slug: 'thuc-vat-bien',
    nameVn: 'Thực vật & Rong biển',
    nameEn: 'Marine Plants & Algae',
    stats: '672 loài • 2 tập',
    icon: <Leaf size={17} color="#a7f3d0" />,
    accentColor: '#a7f3d0',
  },
  {
    slug: 'giap-xac',
    nameVn: 'Giáp xác biển',
    nameEn: 'Marine Crustaceans',
    stats: '132 loài • 1 tập',
    icon: <Shrimp size={17} color="#fca5a5" />,
    accentColor: '#fca5a5',
  },
  {
    slug: 'ran-bien',
    nameVn: 'Rắn biển Việt Nam',
    nameEn: 'Sea Snakes in Vietnam',
    stats: '27 loài • Chuyên khảo',
    icon: <span style={{ fontSize: '17px', lineHeight: 1 }}>🐍</span>,
    accentColor: '#f59e0b',
  },
  {
    slug: 'sinh-vat-doc',
    nameVn: 'Động vật độc biển',
    nameEn: 'Venomous Animals',
    stats: '76 loài • Độc tố học',
    icon: <span style={{ fontSize: '17px', lineHeight: 1 }}>☣️</span>,
    accentColor: '#fb7185',
  },
  {
    slug: 'than-mem',
    nameVn: 'Động vật thân mềm',
    nameEn: 'Marine Mollusca',
    stats: 'Ốc, mực, trai biển',
    icon: <span style={{ fontSize: '17px', lineHeight: 1 }}>🐚</span>,
    accentColor: '#e8c4ff',
  },
  {
    slug: 'san-ho',
    nameVn: 'San hô Việt Nam',
    nameEn: 'Corals of Vietnam',
    stats: 'San hô rạn Việt Nam',
    icon: <span style={{ fontSize: '17px', lineHeight: 1 }}>🪸</span>,
    accentColor: '#f9a8d4',
  },
]

export default function Nav() {
  const pathname = usePathname()
  const [menuOpen, setMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  const toggleMenu = () => setMenuOpen(prev => !prev)

  // Kiểm tra xem trang hiện tại có thuộc nhóm trong dropdown không
  const isDropdownActive = DROPDOWN_COLLECTIONS.some(col =>
    pathname.startsWith(`/${col.slug}`)
  )

  const handleMouseEnter = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    setDropdownOpen(true)
  }

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setDropdownOpen(false)
    }, 180)
  }

  // Lắng nghe click bên ngoài và phím Escape để đóng dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleKeyDown)
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])

  return (
    <>
      <header className="site-header" role="banner">
        <Link href="/" className="logo">
          <img src="/logo.png" alt="Logo Tra cứu sinh vật biển" />
          <span className="logo-full">Tra cứu sinh vật biển</span>
          <span className="logo-short">TCSB</span>
        </Link>

        <nav
          className={`nav-links${menuOpen ? ' open' : ''}`}
          id="navLinks"
          aria-label="Điều hướng chính"
        >
          {/* 1. Trang chủ */}
          <Link
            href="/"
            className={`nav-link${pathname === '/' ? ' active' : ''}`}
            onClick={() => {
              setMenuOpen(false)
              setDropdownOpen(false)
            }}
          >
            {t('nav.home')}
          </Link>

          {/* 2. Cá biển (Bộ dữ liệu chủ lực lớn nhất 1.764 loài) */}
          <Link
            href="/ca-bien"
            className={`nav-link${pathname.startsWith('/ca-bien') ? ' active' : ''}`}
            onClick={() => {
              setMenuOpen(false)
              setDropdownOpen(false)
            }}
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              <Fish size={15} />
              {t('nav.fish') || 'Cá biển'}
            </span>
          </Link>

          {/* 3. Bộ sưu tập ▾ (Dropdown kính mờ các nhóm sinh vật còn lại) */}
          <div
            className="nav-dropdown"
            ref={dropdownRef}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
          >
            <button
              type="button"
              className={`nav-dropdown-trigger${isDropdownActive ? ' active' : ''}`}
              onClick={() => setDropdownOpen(prev => !prev)}
              aria-expanded={dropdownOpen}
              aria-haspopup="true"
              aria-label={t('nav.collections') || 'Bộ sưu tập'}
            >
              <Layers size={15} />
              <span>{t('nav.collections') || 'Bộ sưu tập'}</span>
              <span className="nav-dropdown-icon">
                <ChevronDown size={14} />
              </span>
            </button>

            {dropdownOpen && (
              <div className="nav-dropdown-menu" role="menu">
                {DROPDOWN_COLLECTIONS.map(col => {
                  const isItemActive = pathname.startsWith(`/${col.slug}`)
                  return (
                    <Link
                      key={col.slug}
                      href={`/${col.slug}`}
                      role="menuitem"
                      className={`nav-dropdown-card${isItemActive ? ' active' : ''}`}
                      onClick={() => {
                        setDropdownOpen(false)
                        setMenuOpen(false)
                      }}
                    >
                      <div
                        className="nav-dropdown-card-icon"
                        style={{
                          background: `${col.accentColor}18`,
                          borderColor: `${col.accentColor}40`,
                        }}
                      >
                        {col.icon}
                      </div>
                      <div className="nav-dropdown-card-info">
                        <span className="nav-dropdown-card-title">{col.nameVn}</span>
                        <span className="nav-dropdown-card-stats">{col.stats}</span>
                      </div>
                    </Link>
                  )
                })}
              </div>
            )}
          </div>
        </nav>

        <HeaderControls />

        <button
          className={`hamburger-btn${menuOpen ? ' active' : ''}`}
          onClick={toggleMenu}
          aria-label={menuOpen ? t('nav.closeMenu') : t('nav.openMenu')}
          aria-expanded={menuOpen}
          type="button"
        >
          <span />
          <span />
          <span />
        </button>
      </header>

      <div
        className={`nav-overlay${menuOpen ? ' active' : ''}`}
        onClick={toggleMenu}
      />
    </>
  )
}

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { t } from '@/lib/i18n'
import { getActiveCollections } from '@/lib/collections-static'
import HeaderControls from './HeaderControls'

export default function Nav() {
  const pathname = usePathname()
  const [menuOpen, setMenuOpen] = useState(false)
  const collections = getActiveCollections()

  // Detect which collection is active from URL
  const activeCollection = collections.find(c => pathname.startsWith(`/${c.slug}`))

  const toggleMenu = () => setMenuOpen(prev => !prev)

  return (
    <>
      <header className="site-header" role="banner">
        <Link href="/" className="logo">
          <img src="/logo.png" alt="Logo Bảo tàng Hải dương học" />
          <span className="logo-full">Bảo tàng Hải dương học</span>
          <span className="logo-short">BTHD</span>
        </Link>
        <nav className={`nav-links${menuOpen ? ' open' : ''}`} id="navLinks" aria-label="Điều hướng chính">
          <Link
            href="/"
            className={`nav-link${pathname === '/' ? ' active' : ''}`}
            onClick={() => setMenuOpen(false)}
          >
            {t('nav.home')}
          </Link>

          {/* Collection links */}
          {collections.map(col => (
            <div key={col.slug} className="nav-group">
              <span className="nav-group-label">{col.icon} {col.nameVn}</span>
              <Link
                href={`/${col.slug}`}
                className={`nav-link${pathname === `/${col.slug}` ? ' active' : ''}`}
                onClick={() => setMenuOpen(false)}
              >
                Duyệt Theo Tập
              </Link>
              <Link
                href={`/${col.slug}/taxonomy`}
                className={`nav-link${pathname === `/${col.slug}/taxonomy` ? ' active' : ''}`}
                onClick={() => setMenuOpen(false)}
              >
                Cây Phân Loại
              </Link>
            </div>
          ))}
        </nav>
        <HeaderControls />
        <button
          className={`hamburger-btn${menuOpen ? ' active' : ''}`}
          onClick={toggleMenu}
          aria-label={menuOpen ? t('nav.closeMenu') : t('nav.openMenu')}
          aria-expanded={menuOpen}
          type="button"
        >
          <span /><span /><span />
        </button>
      </header>
      <div
        className={`nav-overlay${menuOpen ? ' active' : ''}`}
        onClick={toggleMenu}
      />
    </>
  )
}

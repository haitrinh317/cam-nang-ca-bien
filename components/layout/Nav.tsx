'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { t } from '@/lib/i18n'
import { getActiveCollections } from '@/lib/collections'
import HeaderControls from './HeaderControls'
import { Fish, Leaf } from 'lucide-react'

export default function Nav() {
  const pathname = usePathname()
  const [menuOpen, setMenuOpen] = useState(false)
  const collections = getActiveCollections()

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

          {/* One flat link per collection */}
          {collections.map(col => (
            <Link
              key={col.slug}
              href={`/${col.slug}`}
              className={`nav-link${pathname.startsWith(`/${col.slug}`) ? ' active' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                {col.slug === 'ca-bien' ? <Fish size={16} /> : col.slug === 'thuc-vat-bien' ? <Leaf size={16} /> : col.icon}
                {col.nameVn}
              </span>
            </Link>
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

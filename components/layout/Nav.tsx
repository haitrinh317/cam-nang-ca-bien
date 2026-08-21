'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { t } from '@/lib/i18n'
import HeaderControls from './HeaderControls'

export default function Nav() {
  const pathname = usePathname()
  const [menuOpen, setMenuOpen] = useState(false)

  const links = [
    { href: '/', label: t('nav.home') },
    { href: '/ca-bien', label: '🐟 Cá biển' },
    { href: '/ca-bien/taxonomy', label: t('nav.browse') },
    { href: '/thuc-vat-bien', label: '🌿 Thực vật biển' },
  ]

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
          {links.map(link => (
            <Link
              key={link.href}
              href={link.href}
              className={`nav-link${pathname === link.href ? ' active' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
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

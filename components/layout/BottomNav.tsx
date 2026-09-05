'use client'
import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const TABS = [
  {
    href: '/',
    label: 'Trang chủ',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
    ),
  },
  {
    href: '/ca-bien',
    label: 'Cá biển',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M6.5 12c0-3.5 2.5-7 8.5-9-1 3-1 6 0 9s1 6 0 9c-6-2-8.5-5.5-8.5-9z"/>
        <path d="M15 12h4"/>
        <path d="M19 9l2 3-2 3"/>
        <circle cx="8" cy="11" r="1" fill="currentColor" stroke="none"/>
      </svg>
    ),
  },
  {
    href: '/thuc-vat-bien',
    label: 'Rong biển',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 22V12"/>
        <path d="M12 12C12 8 9 5 5 5c0 4 3 7 7 7z"/>
        <path d="M12 12c0-4 3-7 7-7-1 4-4 7-7 7z"/>
        <path d="M12 17c0-3 2-5 5-5-1 3-3 5-5 5z"/>
        <path d="M12 17c0-3-2-5-5-5 1 3 3 5 5 5z"/>
      </svg>
    ),
  },
]

export function BottomNav() {
  const pathname = usePathname()
  const [isHidden, setIsHidden] = useState(false)
  const lastScrollY = useRef(0)

  useEffect(() => {
    setIsHidden(false) // Always show on route change
  }, [pathname])

  useEffect(() => {
    let ticking = false

    const handleScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const currentY = window.scrollY || window.pageYOffset || 0
          const diff = currentY - lastScrollY.current

          // Thresholds to prevent jitter
          if (currentY <= 40) {
            // Near top: always visible
            setIsHidden(false)
          } else if (diff > 12 && currentY > 80) {
            // Scrolling DOWN fast enough: hide
            setIsHidden(true)
          } else if (diff < -8) {
            // Scrolling UP: reveal immediately
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
  }, [])

  // Don't show on admin pages
  if (pathname.startsWith('/admin') || pathname.startsWith('/login')) return null

  return (
    <nav className={`bottom-nav${isHidden ? ' is-hidden' : ''}`} aria-label="Menu chính">
      {TABS.map(tab => {
        const isActive =
          tab.href === '/'
            ? pathname === '/'
            : pathname === tab.href || pathname.startsWith(tab.href + '/')
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`bottom-nav__tab${isActive ? ' active' : ''}`}
            aria-current={isActive ? 'page' : undefined}
          >
            <span className="bottom-nav__icon">{tab.icon}</span>
            <span className="bottom-nav__label">{tab.label}</span>
            {isActive && <span className="bottom-nav__dot" aria-hidden="true" />}
          </Link>
        )
      })}
    </nav>
  )
}

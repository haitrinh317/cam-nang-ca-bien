'use client'
import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Fish, Leaf, Shrimp } from 'lucide-react'

const TABS = [
  {
    href: '/',
    label: 'Trang chủ',
    icon: <Home size={20} strokeWidth={2} aria-hidden="true" />,
  },
  {
    href: '/ca-bien',
    label: 'Cá biển',
    icon: <Fish size={20} strokeWidth={2} aria-hidden="true" />,
  },
  {
    href: '/thuc-vat-bien',
    label: 'Rong biển',
    icon: <Leaf size={20} strokeWidth={2} aria-hidden="true" />,
  },
  {
    href: '/giap-xac',
    label: 'Giáp xác',
    icon: <Shrimp size={20} strokeWidth={2} aria-hidden="true" />,
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
          const docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.offsetHeight
          )
          const windowHeight = window.innerHeight || document.documentElement.clientHeight || 0
          const isNearBottom = currentY + windowHeight >= docHeight - 70

          if (currentY <= 40 || isNearBottom) {
            // Near top or near bottom: always visible
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

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import AuthStatus from '@/components/layout/AuthStatus'

import { BarChart3, Fish, Leaf } from 'lucide-react'

interface NavItem { href: string; icon: React.ReactNode; label: string; exact?: boolean }

const NAV_ITEMS: { section: string; items: NavItem[] }[] = [
  { section: 'Tổng quan', items: [
    { href: '/admin', icon: <BarChart3 size={18} />, label: 'Thống kê', exact: true },
  ]},
  { section: 'Bộ sưu tập', items: [
    { href: '/admin/ca-bien', icon: <Fish size={18} />, label: 'Cá biển' },
    { href: '/admin/thuc-vat-bien', icon: <Leaf size={18} />, label: 'Thực vật biển' },
  ]},
]

export default function AdminSidebar() {
  const pathname = usePathname()

  const isActive = (href: string, exact?: boolean) =>
    exact ? pathname === href : pathname.startsWith(href)

  return (
    <aside className="admin-sidebar">
      <div className="admin-sidebar__brand">
        <div className="brand-icon"><Fish size={24} /></div>
        <div>
          <span className="brand-label">Admin Panel</span>
          <span className="brand-sub">Bảo tàng Hải dương học</span>
        </div>
      </div>
      <nav className="admin-sidebar__nav">
        {NAV_ITEMS.map(group => (
          <div key={group.section}>
            <span className="admin-nav-section-label">{group.section}</span>
            {group.items.map(item => (
              <Link
                key={item.href}
                href={item.href}
                className={`admin-nav-link${isActive(item.href, item.exact) ? ' active' : ''}`}
                aria-current={isActive(item.href, item.exact) ? 'page' : undefined}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>
        ))}
      </nav>
      <div className="admin-sidebar__footer">
        <AuthStatus />
        <span className="admin-sidebar__version">v3.0.0 — Next.js</span>
      </div>
    </aside>
  )
}

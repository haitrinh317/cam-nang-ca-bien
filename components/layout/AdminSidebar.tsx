'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import AuthStatus from '@/components/layout/AuthStatus'
import { BarChart3, Fish, Leaf, Shrimp, BookOpen, ExternalLink } from 'lucide-react'

interface NavItem {
  href: string
  icon: React.ReactNode
  label: string
  badge?: string
  exact?: boolean
}

const NAV_GROUPS: { section: string; items: NavItem[] }[] = [
  {
    section: 'Bảng Điều Khiển',
    items: [
      { href: '/admin', icon: <BarChart3 size={18} />, label: 'Thống kê tổng quan', exact: true },
      { href: '/admin/literature', icon: <BookOpen size={18} />, label: 'Quản lý Tài liệu gốc' },
    ],
  },
  {
    section: 'Dữ Liệu Đa Dạng Sinh Học',
    items: [
      { href: '/admin/ca-bien', icon: <Fish size={18} />, label: 'Cá biển Việt Nam', badge: '1.764' },
      { href: '/admin/thuc-vat-bien', icon: <Leaf size={18} />, label: 'Thực vật biển', badge: '672' },
      { href: '/admin/giap-xac', icon: <Shrimp size={18} />, label: 'Giáp xác biển', badge: '132' },
      { href: '/admin/ran-bien', icon: <span style={{ fontSize: '15px', lineHeight: 1 }}>🐍</span>, label: 'Rắn biển Việt Nam', badge: '27' },
    ],
  },
]

export default function AdminSidebar() {
  const pathname = usePathname()

  const isActive = (href: string, exact?: boolean) =>
    exact ? pathname === href : pathname.startsWith(href)

  return (
    <aside className="admin-sidebar" aria-label="Thanh điều hướng quản trị">
      <div className="admin-sidebar__brand">
        <div className="brand-icon" aria-hidden="true">
          <Fish size={22} />
        </div>
        <div>
          <span className="brand-label">Cổng Quản Trị</span>
          <span className="brand-sub">Phát triển bởi haitrinh</span>
        </div>
      </div>

      <div className="admin-sidebar__extlink">
        <Link href="/" className="admin-back-btn" title="Mở trang tra cứu công cộng">
          <span>← Ra trang tra cứu</span>
          <ExternalLink size={12} aria-hidden="true" />
        </Link>
      </div>

      <nav className="admin-sidebar__nav">
        {NAV_GROUPS.map((group) => (
          <div key={group.section} className="admin-nav-group">
            <span className="admin-nav-section-label">{group.section}</span>
            {group.items.map((item) => {
              const active = isActive(item.href, item.exact)
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`admin-nav-link${active ? ' active' : ''}`}
                  aria-current={active ? 'page' : undefined}
                >
                  <span className="nav-icon" aria-hidden="true">{item.icon}</span>
                  <span style={{ flex: 1 }}>{item.label}</span>
                  {item.badge && (
                    <span
                      style={{
                        fontFamily: 'var(--font-outlier)',
                        fontSize: '0.72rem',
                        padding: '0.1rem 0.4rem',
                        borderRadius: '4px',
                        background: active ? 'rgba(0, 212, 184, 0.25)' : 'rgba(255, 255, 255, 0.08)',
                        color: active ? '#00f0d0' : 'rgba(240, 253, 249, 0.6)',
                      }}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              )
            })}
          </div>
        ))}
      </nav>

      <div className="admin-sidebar__footer">
        <AuthStatus />
        <span className="admin-sidebar__version">
          v3.0.0 · Supabase RLS Protected
        </span>
      </div>
    </aside>
  )
}

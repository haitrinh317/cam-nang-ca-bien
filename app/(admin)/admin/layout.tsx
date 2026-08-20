import type { Metadata } from 'next'
import AuthStatus from '@/components/layout/AuthStatus'

export const metadata: Metadata = {
  title: 'Admin — Quản trị Cơ sở dữ liệu',
  robots: 'noindex,nofollow',
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="admin-wrapper">
      <aside className="admin-sidebar">
        <div className="admin-sidebar__brand">
          <div className="brand-icon">⚙</div>
          <div>
            <span className="brand-label">Admin Panel</span>
            <span className="brand-sub">Bảo tàng Hải dương học</span>
          </div>
        </div>
        <nav className="admin-sidebar__nav">
          <span className="admin-nav-section-label">Tổng quan</span>
          <a href="/admin" className="admin-nav-link">
            <span className="nav-icon">📊</span> Thống kê
          </a>
          <span className="admin-nav-section-label">Bộ sưu tập</span>
          <a href="/admin/ca-bien" className="admin-nav-link">
            <span className="nav-icon">🐟</span> Cá biển
          </a>
          <a href="/admin/thuc-vat-bien" className="admin-nav-link">
            <span className="nav-icon">🌿</span> Thực vật biển
          </a>
        </nav>
        <div className="admin-sidebar__footer">
          <AuthStatus />
          <span style={{ color: 'var(--color-muted)', fontSize: '0.75rem', marginTop: '0.5rem', display: 'block' }}>v4.0.0 — Next.js</span>
        </div>
      </aside>
      <main className="admin-content">
        {children}
      </main>
    </div>
  )
}

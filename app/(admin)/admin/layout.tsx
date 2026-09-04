import type { Metadata } from 'next'
import AdminSidebar from '@/components/layout/AdminSidebar'
import '@/styles/admin.css'

export const metadata: Metadata = {
  title: 'Admin — Quản trị Cơ sở dữ liệu — Bảo tàng Hải dương học',
  robots: 'noindex,nofollow',
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="admin-wrapper">
      <AdminSidebar />
      <main className="admin-content">
        {children}
      </main>
    </div>
  )
}

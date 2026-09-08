import type { Metadata } from 'next'
import AdminSidebar from '@/components/layout/AdminSidebar'
import '@/styles/admin.css'

export const metadata: Metadata = {
  title: 'Admin — Quản trị CSDL Sinh Vật Biển — haitrinh',
  description: 'Hệ thống quản trị cơ sở dữ liệu số hóa sinh vật biển Việt Nam — Dự án cá nhân phát triển bởi haitrinh.',
  robots: {
    index: false,
    follow: false,
    nocache: true,
  },
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

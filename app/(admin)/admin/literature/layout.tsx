import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Quản lý Tài liệu gốc — Admin haitrinh',
  description: 'Quản lý danh mục chuyên khảo và tài liệu nghiên cứu nguồn — Dự án cá nhân phát triển bởi haitrinh.',
  robots: {
    index: false,
    follow: false,
  },
}

export default function AdminLiteratureLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}

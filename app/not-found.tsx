import Link from 'next/link'
import type { Metadata } from 'next'
import { Fish } from 'lucide-react'

export const metadata: Metadata = {
  title: '404 — Trang không tìm thấy',
  robots: 'noindex',
}

export default function NotFound() {
  return (
    <div className="not-found-page">
      <div className="not-found-content">
        <div className="not-found-icon"><Fish size={48} className="text-cyan-400 mx-auto" /></div>
        <h1>404 — Không tìm thấy</h1>
        <p>Trang hoặc loài sinh vật này không tồn tại trong cơ sở dữ liệu.</p>
        <div className="not-found-actions">
          <Link href="/" className="btn btn-primary">← Về trang chủ</Link>
          <Link href="/ca-bien" className="btn btn-outline">Duyệt Cá biển</Link>
        </div>
      </div>
    </div>
  )
}

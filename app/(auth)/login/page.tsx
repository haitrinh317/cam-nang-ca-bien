import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowLeft, ShieldCheck } from 'lucide-react'
import LoginForm from './LoginForm'
import '@/styles/auth.css'

export const metadata: Metadata = {
  title: 'Đăng nhập Quản trị — CSDL Sinh Vật Biển · haitrinh',
  description: 'Cổng xác thực quản trị dữ liệu sinh vật biển Việt Nam — Dự án cá nhân phát triển bởi haitrinh.',
  robots: {
    index: false,
    follow: false,
    nocache: true,
  },
}

interface Props {
  searchParams: Promise<{ next?: string }>
}

export default async function LoginPage({ searchParams }: Props) {
  const { next } = await searchParams

  return (
    <main className="auth-viewport">
      {/* Top back navigation */}
      <nav className="auth-top-nav" aria-label="Điều hướng">
        <Link href="/" className="auth-back-link">
          <ArrowLeft size={16} aria-hidden="true" />
          <span>Về trang tra cứu</span>
        </Link>
      </nav>

      {/* Centered Vault Card */}
      <section className="auth-card-vault" aria-labelledby="auth-heading">
        <header className="auth-card-header">
          <div className="auth-seal-ring">
            <img
              src="/logo.png"
              alt="Biểu trưng Tra cứu thông tin Sinh Vật Biển Việt Nam"
              className="auth-seal-logo"
              width={44}
              height={44}
            />
          </div>

          <div className="auth-system-badge">
            <ShieldCheck size={18} aria-hidden="true" />
            <span>HỆ THỐNG QUẢN TRỊ NỘI BỘ</span>
          </div>

          <h1 id="auth-heading" className="auth-title">
            Đăng nhập Quản trị
          </h1>
          <p className="auth-subtitle">
            Dự án cá nhân phát triển bởi haitrinh
          </p>
        </header>

        <LoginForm redirectTo={next || '/admin'} />

        <footer className="auth-card-footer">
          <p className="auth-security-note">
            Khu vực giới hạn. Mọi phiên đăng nhập và thao tác dữ liệu đều được ghi nhận tự động vào Nhật ký kiểm toán (Audit Log).
          </p>
          <div className="auth-system-stamp">
            DỰ ÁN CÁ NHÂN HAITRINH · CSDL 3.072 LOÀI SINH VẬT BIỂN
          </div>
        </footer>
      </section>
    </main>
  )
}

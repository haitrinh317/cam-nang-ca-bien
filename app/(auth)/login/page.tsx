import type { Metadata } from 'next'
import Link from 'next/link'
import LoginForm from './LoginForm'
import '@/styles/auth.css'

export const metadata: Metadata = {
  title: 'Đăng nhập Quản trị — Tra cứu thông tin Sinh Vật Biển Việt Nam',
  description: 'Cổng xác thực quản trị dữ liệu sinh vật biển Việt Nam — Một dự án được phát triển bởi haitrinh.',
  robots: {
    index: false,
    follow: false,
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
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="m15 18-6-6 6-6" />
          </svg>
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
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            <span>HỆ THỐNG QUẢN TRỊ NỘI BỘ</span>
          </div>

          <h1 id="auth-heading" className="auth-title">
            Đăng nhập Quản trị
          </h1>
          <p className="auth-subtitle">
            Một dự án được phát triển bởi haitrinh
          </p>
        </header>

        <LoginForm redirectTo={next || '/admin'} />

        <footer className="auth-card-footer">
          <p className="auth-security-note">
            Khu vực giới hạn. Mọi phiên đăng nhập và thao tác dữ liệu đều được ghi nhận tự động vào Nhật ký kiểm toán (Audit Log).
          </p>
          <div className="auth-system-stamp">
            12°12&apos;04&quot;N 109°12&apos;58&quot;E · CSDL 2.436+ LOÀI SINH VẬT BIỂN
          </div>
        </footer>
      </section>
    </main>
  )
}

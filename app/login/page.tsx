import type { Metadata } from 'next'
import LoginForm from './LoginForm'

export const metadata: Metadata = {
  title: 'Đăng nhập — Admin',
  robots: 'noindex,nofollow',
}

interface Props {
  searchParams: Promise<{ next?: string }>
}

export default async function LoginPage({ searchParams }: Props) {
  const { next } = await searchParams
  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card__logo">
          <img src="/logo.png" alt="Logo Bảo tàng Hải dương học" style={{ width: 48, height: 48, objectFit: 'contain' }} />
        </div>
        <h1 className="auth-card__title">Đăng nhập</h1>
        <p className="auth-card__sub">Bảo tàng Hải dương học — Hệ thống quản trị</p>
        <LoginForm redirectTo={next || '/admin'} />
        <p className="auth-card__footer">
          Chỉ dành cho người quản trị được phân quyền.
        </p>
      </div>
    </div>
  )
}

'use client'

import { useState } from 'react'
import { db } from '@/lib/supabase-browser'

interface Props {
  redirectTo: string
}

export default function LoginForm({ redirectTo }: Props) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const { data, error: authError } = await db.auth.signInWithPassword({
        email: email.trim(),
        password,
      })

      if (authError) {
        setError(
          authError.message === 'Invalid login credentials'
            ? 'Email hoặc mật khẩu không chính xác. Vui lòng kiểm tra lại.'
            : authError.message
        )
        setLoading(false)
        return
      }

      if (!data?.session) {
        setError('Không nhận được phiên đăng nhập hợp lệ. Vui lòng thử lại.')
        setLoading(false)
        return
      }

      // Sync cookie & hard redirect to requested dashboard
      window.location.href = redirectTo
    } catch (err) {
      console.error('[Login] unexpected error:', err)
      setError('Đã xảy ra lỗi không xác định trong quá trình xác thực. Vui lòng thử lại.')
      setLoading(false)
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit} noValidate={false}>
      {error && (
        <div className="auth-alert-error" role="alert" aria-live="polite">
          <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <span>{error}</span>
        </div>
      )}

      <div className="auth-field">
        <label className="auth-label" htmlFor="login-email">
          <span>EMAIL QUẢN TRỊ VIÊN</span>
        </label>
        <div className="auth-input-wrapper">
          <svg
            className="auth-input-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <rect width="20" height="16" x="2" y="4" rx="2" />
            <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
          </svg>
          <input
            id="login-email"
            className="auth-input"
            type="email"
            name="email"
            autoComplete="email"
            required
            autoFocus
            disabled={loading}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@tracuusinhvatbien.app"
          />
        </div>
      </div>

      <div className="auth-field">
        <label className="auth-label" htmlFor="login-password">
          <span>MẬT KHẨU</span>
        </label>
        <div className="auth-input-wrapper">
          <svg
            className="auth-input-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <input
            id="login-password"
            className="auth-input"
            type={showPassword ? 'text' : 'password'}
            name="password"
            autoComplete="current-password"
            required
            disabled={loading}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••••••"
          />
          <button
            type="button"
            className="auth-toggle-btn"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
            title={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
            tabIndex={0}
          >
            {showPassword ? (
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                <line x1="2" x2="22" y1="2" y2="22" />
              </svg>
            ) : (
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            )}
          </button>
        </div>
      </div>

      <button className="auth-submit-btn" type="submit" disabled={loading}>
        {loading ? (
          <>
            <span className="auth-spinner" aria-hidden="true" />
            <span>Đang xác thực bảo mật...</span>
          </>
        ) : (
          <>
            <span>Đăng nhập hệ thống</span>
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
          </>
        )}
      </button>
    </form>
  )
}

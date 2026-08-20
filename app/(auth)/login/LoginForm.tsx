'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { db } from '@/lib/supabase-browser'

interface Props { redirectTo: string }

export default function LoginForm({ redirectTo }: Props) {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const { data, error } = await db.auth.signInWithPassword({ email, password })

      console.log('[Login] result:', { session: !!data?.session, error: error?.message })

      if (error) {
        setError(
          error.message === 'Invalid login credentials'
            ? 'Email hoặc mật khẩu không đúng.'
            : error.message
        )
        setLoading(false)
        return
      }

      if (!data?.session) {
        setError('Đăng nhập thất bại — không nhận được session. Thử lại.')
        setLoading(false)
        return
      }

      // Redirect using window.location to force full page reload (sync cookie)
      window.location.href = redirectTo
    } catch (err) {
      console.error('[Login] unexpected error:', err)
      setError('Lỗi không xác định. Thử lại.')
      setLoading(false)
    }
  }


  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      {error && <div className="auth-error">{error}</div>}

      <div className="form-field">
        <label className="form-label" htmlFor="login-email">Email</label>
        <input
          id="login-email"
          className="form-input"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="haitrinh082@gmail.com"
        />
      </div>

      <div className="form-field">
        <label className="form-label" htmlFor="login-password">Mật khẩu</label>
        <input
          id="login-password"
          className="form-input"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="••••••••"
        />
      </div>

      <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: '0.5rem' }}>
        {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
      </button>
    </form>
  )
}

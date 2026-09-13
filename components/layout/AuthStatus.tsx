'use client'

import { useEffect, useState } from 'react'
import { db } from '@/lib/supabase-browser'
import { LogOut, ShieldCheck } from 'lucide-react'

interface Props {
  collapsed?: boolean
}

export default function AuthStatus({ collapsed }: Props) {
  const [email, setEmail] = useState<string | null>(null)

  useEffect(() => {
    db.auth.getUser().then(({ data }) => setEmail(data.user?.email || null))
    const { data: { subscription } } = db.auth.onAuthStateChange((_, session) => {
      setEmail(session?.user?.email || null)
    })
    return () => subscription.unsubscribe()
  }, [])

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' })
    window.location.href = '/login'
  }

  if (!email) return null

  const initial = email.charAt(0).toUpperCase()
  const name = email.split('@')[0]

  if (collapsed) {
    return (
      <div className="auth-status auth-status--collapsed">
        <div className="auth-status__avatar" title={`${email} (Admin)`}>
          {initial}
        </div>
        <button
          className="auth-status__logout-icon-btn"
          data-class="btn"
          onClick={handleLogout}
          type="button"
          title="Đăng xuất khỏi phiên làm việc"
        >
          <LogOut size={13} aria-hidden="true" />
        </button>
      </div>
    )
  }

  return (
    <div className="auth-status">
      <div className="auth-status__card">
        <div className="auth-status__avatar" aria-hidden="true">
          {initial}
        </div>
        <div className="auth-status__info">
          <div className="auth-status__email" title={email}>
            {name}
          </div>
          <div className="auth-status__role-badge">
            <span className="auth-status__dot" aria-hidden="true" />
            <ShieldCheck size={11} aria-hidden="true" />
            <span>ADMIN PRO</span>
          </div>
        </div>
      </div>

      <button
        className="auth-status__logout"
        data-class="btn"
        onClick={handleLogout}
        type="button"
        title="Đăng xuất khỏi phiên làm việc"
      >
        <LogOut size={13} aria-hidden="true" />
        <span>Đăng xuất</span>
      </button>
    </div>
  )
}

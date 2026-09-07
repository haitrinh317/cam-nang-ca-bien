'use client'

import { useEffect, useState } from 'react'
import { db } from '@/lib/supabase-browser'
import { LogOut, ShieldCheck } from 'lucide-react'

export default function AuthStatus() {
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

  return (
    <div className="auth-status">
      <div className="auth-status__card">
        <div className="auth-status__avatar" aria-hidden="true">
          {initial}
        </div>
        <div className="auth-status__info">
          <div className="auth-status__email" title={email}>
            {email}
          </div>
          <div className="auth-status__role-badge">
            <span className="auth-status__dot" aria-hidden="true" />
            <ShieldCheck size={11} aria-hidden="true" />
            <span>QUẢN TRỊ VIÊN</span>
          </div>
        </div>
      </div>

      <button
        className="auth-status__logout"
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

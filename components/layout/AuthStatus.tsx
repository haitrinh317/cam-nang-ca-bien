'use client'

import { useEffect, useState } from 'react'
import { db } from '@/lib/supabase-browser'

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

  return (
    <div className="auth-status">
      <div className="auth-status__email" title={email}>
        <span className="auth-status__dot" />
        {email.split('@')[0]}
      </div>
      <button className="auth-status__logout" onClick={handleLogout} type="button">
        Đăng xuất
      </button>
    </div>
  )
}

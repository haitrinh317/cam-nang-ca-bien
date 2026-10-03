'use client'

import { useEffect, useState } from 'react'
import { getTheme, toggleTheme, initTheme } from '@/lib/theme'
import { Sun, Moon } from 'lucide-react'

export function ThemeToggleBtn() {
  const [theme, setThemeState] = useState('light')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    initTheme()
    setThemeState(getTheme())
    setMounted(true)
  }, [])

  if (!mounted) return null

  const handleToggle = () => {
    const next = toggleTheme()
    setThemeState(next)
  }

  return (
    <button
      type="button"
      onClick={handleToggle}
      className="footer-theme-toggle"
      title={theme === 'dark' ? 'Chuyển sang giao diện Sáng' : 'Chuyển sang giao diện Tối'}
      aria-label={theme === 'dark' ? 'Chuyển sang giao diện Sáng' : 'Chuyển sang giao diện Tối'}
    >
      {theme === 'dark' ? (
        <>
          <Sun size={13} aria-hidden="true" />
          <span>Tối</span>
        </>
      ) : (
        <>
          <Moon size={13} aria-hidden="true" />
          <span>Sáng</span>
        </>
      )}
    </button>
  )
}

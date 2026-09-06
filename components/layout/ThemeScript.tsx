/**
 * ThemeScript — Inline script to apply theme before first paint.
 * Uses Next.js Script with beforeInteractive to avoid React hydration warning.
 */
import Script from 'next/script'

export function ThemeScript() {
  return (
    <Script
      id="theme-init"
      strategy="beforeInteractive"
      dangerouslySetInnerHTML={{
        __html: `(function(){var t=localStorage.getItem('cabien-theme')||'light';document.documentElement.setAttribute('data-theme',t);})()`
      }}
    />
  )
}

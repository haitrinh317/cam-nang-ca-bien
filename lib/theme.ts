/**
 * theme.ts — Light/Dark mode toggle (port from vanilla JS)
 */

const STORAGE_KEY = 'cabien-theme'
const DEFAULT_THEME = 'light'

export function getTheme(): string {
  if (typeof window === 'undefined') return DEFAULT_THEME
  return localStorage.getItem(STORAGE_KEY) || DEFAULT_THEME
}

export function setTheme(theme: string): void {
  localStorage.setItem(STORAGE_KEY, theme)
  document.documentElement.setAttribute('data-theme', theme)
}

export function toggleTheme(): string {
  const next = getTheme() === 'dark' ? 'light' : 'dark'
  setTheme(next)
  return next
}

export function initTheme(): void {
  setTheme(getTheme())
}

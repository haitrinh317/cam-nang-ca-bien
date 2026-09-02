/**
 * theme.js — Light/Dark mode toggle
 * Stores preference in localStorage. Applies [data-theme="dark"] on <html>.
 * Default: 'light' (current design is light ocean theme).
 */

const STORAGE_KEY = 'cabien-theme'
const DEFAULT_THEME = 'light'

export function getTheme() {
  return localStorage.getItem(STORAGE_KEY) || DEFAULT_THEME
}

export function setTheme(theme) {
  localStorage.setItem(STORAGE_KEY, theme)
  document.documentElement.setAttribute('data-theme', theme)
  document.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }))
}

export function toggleTheme() {
  setTheme(getTheme() === 'dark' ? 'light' : 'dark')
}

/** Call once at page load — applies saved preference immediately */
export function initTheme() {
  setTheme(getTheme())
}

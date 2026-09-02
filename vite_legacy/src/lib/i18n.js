/**
 * i18n.js — Lightweight i18n module
 * Stores locale in localStorage, applies data-i18n attributes to DOM.
 * Usage:
 *   import { t, setLocale, getLocale, applyLocale } from '../lib/i18n.js'
 *
 * HTML markup: <span data-i18n="nav.home">Trang Chủ</span>
 *              <input data-i18n-placeholder="home.searchPlaceholder">
 */

const STORAGE_KEY = 'cabien-locale'
const DEFAULT_LOCALE = 'vi'

let _locale = localStorage.getItem(STORAGE_KEY) || DEFAULT_LOCALE
let _strings = {}

/**
 * Load and cache locale JSON. Returns promise.
 */
async function loadLocale(locale) {
  try {
    const res = await fetch(`/src/locales/${locale}.json`)
    if (!res.ok) throw new Error(`Locale ${locale} not found`)
    return await res.json()
  } catch (e) {
    console.warn('[i18n] Failed to load locale:', locale, e)
    return {}
  }
}

/**
 * Resolve dot-path key from strings object.
 * t('nav.home') → 'Trang Chủ'
 */
export function t(key, fallback = key) {
  const parts = key.split('.')
  let val = _strings
  for (const p of parts) {
    if (val == null) return fallback
    val = val[p]
  }
  return val ?? fallback
}

/** Get current locale code */
export function getLocale() { return _locale }

/**
 * Switch locale, persist, and re-apply to DOM.
 */
export async function setLocale(locale) {
  _locale = locale
  localStorage.setItem(STORAGE_KEY, locale)
  _strings = await loadLocale(locale)
  applyLocale()
  document.documentElement.lang = locale
  document.dispatchEvent(new CustomEvent('localechange', { detail: { locale } }))
}

/**
 * Apply current strings to all elements with data-i18n* attributes.
 * Called once after init and after every setLocale().
 */
export function applyLocale() {
  // Text content
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n
    const val = t(key)
    if (val !== key) el.textContent = val
  })
  // Placeholder
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.dataset.i18nPlaceholder
    const val = t(key)
    if (val !== key) el.placeholder = val
  })
  // Aria-label
  document.querySelectorAll('[data-i18n-aria]').forEach(el => {
    const key = el.dataset.i18nAria
    const val = t(key)
    if (val !== key) el.setAttribute('aria-label', val)
  })
  // Title attribute
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.dataset.i18nTitle
    const val = t(key)
    if (val !== key) el.title = val
  })
}

/**
 * Init: load locale from storage and apply. Call once at page load.
 */
export async function initI18n() {
  _strings = await loadLocale(_locale)
  document.documentElement.lang = _locale
  applyLocale()
  return _locale
}

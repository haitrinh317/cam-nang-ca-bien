/**
 * i18n.ts — Lightweight i18n (port from vanilla JS)
 */

import viStrings from '@/locales/vi.json'
import enStrings from '@/locales/en.json'

const STORAGE_KEY = 'cabien-locale'
const DEFAULT_LOCALE = 'vi'

type Strings = Record<string, unknown>

const localeMap: Record<string, Strings> = { vi: viStrings, en: enStrings }

export function getLocale(): string {
  if (typeof window === 'undefined') return DEFAULT_LOCALE
  return localStorage.getItem(STORAGE_KEY) || DEFAULT_LOCALE
}

export function setLocale(locale: string): void {
  localStorage.setItem(STORAGE_KEY, locale)
  document.documentElement.lang = locale
}

/** Resolve dot-path key: t('nav.home') → 'Trang Chủ' */
export function t(key: string, locale?: string): string {
  const lang = locale || getLocale()
  const strings = localeMap[lang] || localeMap[DEFAULT_LOCALE]
  const parts = key.split('.')
  let val: unknown = strings
  for (const p of parts) {
    if (val == null || typeof val !== 'object') return key
    val = (val as Record<string, unknown>)[p]
  }
  return typeof val === 'string' ? val : key
}

/** Get all strings for a locale */
export function getStrings(locale?: string): Strings {
  const lang = locale || getLocale()
  return localeMap[lang] || localeMap[DEFAULT_LOCALE]
}

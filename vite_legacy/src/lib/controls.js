/**
 * controls.js — Header controls: theme toggle + lang toggle
 * Import once per page after DOM is ready.
 * Injects toggle buttons into .nav-controls slot in the header.
 */
import { getTheme, setTheme } from './theme.js'
import { getLocale, setLocale } from './i18n.js'

/**
 * Inject theme + lang toggles into the header.
 * Expects a <div class="nav-controls"> to exist in the header.
 */
export function mountHeaderControls() {
  const controls = document.querySelector('.nav-controls')
  if (!controls) return

  // ── Lang toggle ──────────────────────────────
  const langBtn = document.createElement('button')
  langBtn.className = 'ctrl-btn ctrl-lang'
  langBtn.id = 'langToggle'
  langBtn.setAttribute('aria-label', 'Chuyển ngôn ngữ')
  langBtn.setAttribute('type', 'button')
  _updateLangBtn(langBtn)

  langBtn.addEventListener('click', async () => {
    const next = getLocale() === 'vi' ? 'en' : 'vi'
    await setLocale(next)
    _updateLangBtn(langBtn)
    _updateThemeBtn(themeBtn)
  })

  // ── Theme toggle ─────────────────────────────
  const themeBtn = document.createElement('button')
  themeBtn.className = 'ctrl-btn ctrl-theme'
  themeBtn.id = 'themeToggle'
  themeBtn.setAttribute('type', 'button')
  _updateThemeBtn(themeBtn)

  themeBtn.addEventListener('click', () => {
    const next = getTheme() === 'dark' ? 'light' : 'dark'
    setTheme(next)
    _updateThemeBtn(themeBtn)
  })

  controls.appendChild(langBtn)
  controls.appendChild(themeBtn)

  // Re-sync on locale change (if triggered externally)
  document.addEventListener('localechange', () => {
    _updateLangBtn(langBtn)
    _updateThemeBtn(themeBtn)
  })
}

function _updateLangBtn(btn) {
  const current = getLocale()
  const next = current === 'vi' ? 'EN' : 'VN'
  btn.textContent = next
  btn.title = current === 'vi' ? 'Switch to English' : 'Chuyển sang Tiếng Việt'
}

function _updateThemeBtn(btn) {
  const isDark = getTheme() === 'dark'
  btn.innerHTML = isDark ? _iconSun() : _iconMoon()
  btn.title = isDark ? 'Chế độ sáng' : 'Chế độ tối'
  btn.setAttribute('aria-label', btn.title)
}

function _iconMoon() {
  return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`
}

function _iconSun() {
  return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`
}

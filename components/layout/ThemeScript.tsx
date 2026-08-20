/**
 * ThemeScript — Inline script to apply theme before first paint.
 * Must be a Server Component that renders a <script> tag.
 */
export function ThemeScript() {
  const script = `(function(){var t=localStorage.getItem('cabien-theme')||'light';document.documentElement.setAttribute('data-theme',t);})()`
  return <script dangerouslySetInnerHTML={{ __html: script }} />
}

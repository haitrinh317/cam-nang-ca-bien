import { useEffect, useRef } from 'react'

/**
 * Adds `.is-revealed` to every child matching `itemSelector`
 * when the item enters the viewport.
 * Respects `prefers-reduced-motion` — skips observation if motion is reduced.
 *
 * @param containerRef  ref to the parent element containing items
 * @param itemSelector  CSS selector for the items inside the container
 * @param threshold     Intersection threshold (0–1). Default 0.08
 */
export function useScrollReveal<T extends HTMLElement>(
  containerRef: React.RefObject<T | null>,
  itemSelector: string,
  threshold = 0.08
) {
  useEffect(() => {
    if (typeof window === 'undefined') return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    const container = containerRef.current
    if (!container) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed')
            observer.unobserve(entry.target) // once only
          }
        })
      },
      { threshold, rootMargin: '0px 0px -32px 0px' }
    )

    const items = container.querySelectorAll(itemSelector)
    items.forEach((el) => observer.observe(el))

    return () => observer.disconnect()
    // ponytail: re-run when container or selector changes (e.g. page filter changes)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemSelector])
}

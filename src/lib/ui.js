/**
 * Shared UI utilities — loading states, error handling, back-to-top
 */

/** Show a loading spinner inside a container */
export function showLoading(container) {
  container.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Đang tải dữ liệu...</p>
    </div>`
}

/** Show an error message inside a container */
export function showError(container, message = 'Không thể tải dữ liệu. Vui lòng thử lại.') {
  container.innerHTML = `
    <div class="error-state">
      <p>⚠️ ${message}</p>
      <button onclick="location.reload()">Tải lại</button>
    </div>`
}

/** Inject back-to-top button (from shared.js logic) */
export function initBackToTop() {
  const btn = document.createElement('button')
  btn.className = 'back-to-top'
  btn.innerHTML = '↑'
  btn.title = 'Về đầu trang'
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }))
  document.body.appendChild(btn)

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 300)
  })
}

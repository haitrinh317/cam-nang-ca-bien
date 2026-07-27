// shared.js — injected into all pages
(function () {
    // Inject back-to-top button
    const btn = document.createElement('button');
    btn.id = 'backToTop';
    btn.setAttribute('aria-label', 'Lên đầu trang');
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>`;
    document.body.appendChild(btn);

    // Show/hide on scroll
    window.addEventListener('scroll', function () {
        if (window.scrollY > 300) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    }, { passive: true });

    // Scroll to top on click
    btn.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
})();

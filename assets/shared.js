/* shared.js — Back-to-top button injection cho tất cả trang */
(function () {
    // Tạo button
    const btn = document.createElement('button');
    btn.id = 'backToTop';
    btn.title = 'Lên đầu trang';
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>`;
    btn.style.cssText = [
        'position:fixed',
        'bottom:2rem',
        'right:2rem',
        'z-index:999',
        'width:44px',
        'height:44px',
        'border-radius:50%',
        'border:1px solid rgba(255,255,255,0.15)',
        'background:rgba(10,10,15,0.85)',
        'backdrop-filter:blur(12px)',
        '-webkit-backdrop-filter:blur(12px)',
        'color:#fff',
        'cursor:pointer',
        'display:flex',
        'align-items:center',
        'justify-content:center',
        'opacity:0',
        'visibility:hidden',
        'transition:opacity 0.3s,visibility 0.3s,transform 0.3s',
        'transform:translateY(8px)',
        'box-shadow:0 4px 16px rgba(0,0,0,0.4)',
    ].join(';');
    btn.querySelector('svg').style.cssText = 'width:18px;height:18px;';

    document.body.appendChild(btn);

    // Hiện/ẩn theo scroll
    window.addEventListener('scroll', function () {
        if (window.scrollY > 300) {
            btn.style.opacity = '1';
            btn.style.visibility = 'visible';
            btn.style.transform = 'translateY(0)';
        } else {
            btn.style.opacity = '0';
            btn.style.visibility = 'hidden';
            btn.style.transform = 'translateY(8px)';
        }
    }, { passive: true });

    // Click scroll lên đầu
    btn.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Hover effect
    btn.addEventListener('mouseenter', function () {
        btn.style.background = 'rgba(88,101,242,0.3)';
        btn.style.borderColor = 'rgba(88,101,242,0.5)';
    });
    btn.addEventListener('mouseleave', function () {
        btn.style.background = 'rgba(10,10,15,0.85)';
        btn.style.borderColor = 'rgba(255,255,255,0.15)';
    });
})();

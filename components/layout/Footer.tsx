import Link from 'next/link'
import { t } from '@/lib/i18n'
import { ExternalLink } from 'lucide-react'
import { ThemeToggleBtn } from './ThemeToggleBtn'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="site-footer" role="contentinfo">
      <div className="site-footer__inner">
        {/* ─── Tầng 1: Nhận diện Viện & Slogan di sản ─── */}
        <div className="site-footer__top">
          <div className="footer-brand">
            <img
              src="/logo.png"
              alt="Logo Bảo tàng Hải dương học"
              className="footer-logo"
              width={36}
              height={36}
            />
            <div className="footer-brand__text">
              <div className="footer-org__title">
                <a
                  href="http://vnio.org.vn/"
                  target="_blank"
                  rel="noopener"
                  className="footer-org__link"
                >
                  <strong>{t('footer.org')}</strong>
                </a>
                <span className="footer-org__parent">, {t('footer.orgParent')}</span>
              </div>
              <div className="footer-org__sub">
                <span>{t('footer.mission')}</span>
              </div>
            </div>
          </div>

          <div className="footer-status">
            <span className="footer-statement-badge">
              <span className="statement-dot" aria-hidden="true" />
              {t('footer.statement')}
            </span>
            <ThemeToggleBtn />
            <span className="footer-version-badge">v1.0.0 (Thử nghiệm)</span>
          </div>
        </div>

        {/* ─── Đường chia Hairline tinh tế ─── */}
        <div className="footer-divider" aria-hidden="true" />

        {/* ─── Tầng 2: Liên kết điều hướng, Đối soát quốc tế & Bản quyền ─── */}
        <div className="site-footer__bottom">
          <div className="footer-nav-cluster">
            {/* Nhóm điều hướng nội bộ */}
            <nav className="footer-nav" aria-label="Liên kết chân trang">
              <Link href="/about" className="footer-link">
                Giới thiệu
              </Link>
              <span className="footer-nav-dot" aria-hidden="true">•</span>
              <Link href="/faq" className="footer-link">
                Câu hỏi thường gặp
              </Link>
            </nav>

            {/* Nhóm CSDL quốc tế đối soát */}
            <div className="footer-external-links" aria-label="Cơ sở dữ liệu danh pháp quốc tế">
              <span className="footer-ext-label">Đối soát dữ liệu:</span>
              <a
                href="https://www.marinespecies.org"
                target="_blank"
                rel="noopener"
                className="footer-link footer-link--ext"
                title="World Register of Marine Species"
              >
                WoRMS <ExternalLink size={11} aria-hidden="true" />
              </a>
              <a
                href="https://www.fishbase.se"
                target="_blank"
                rel="noopener"
                className="footer-link footer-link--ext"
                title="Global Information System on Fishes"
              >
                FishBase <ExternalLink size={11} aria-hidden="true" />
              </a>
              <a
                href="https://www.algaebase.org"
                target="_blank"
                rel="noopener"
                className="footer-link footer-link--ext"
                title="World Algae Database"
              >
                AlgaeBase <ExternalLink size={11} aria-hidden="true" />
              </a>
              <a
                href="https://www.inaturalist.org"
                target="_blank"
                rel="noopener"
                className="footer-link footer-link--ext"
                title="Biodiversity Observations"
              >
                iNaturalist <ExternalLink size={11} aria-hidden="true" />
              </a>
            </div>
          </div>

          <div className="footer-copyright">
            {t('footer.developedBy')}
          </div>
        </div>
      </div>
    </footer>
  )
}

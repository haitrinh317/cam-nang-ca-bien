import Link from 'next/link'
import { t } from '@/lib/i18n'

export default function Footer() {
  return (
    <footer role="contentinfo">
      <div className="footer-inner">
        <p className="footer__statement">{t('footer.statement')}</p>
        <div className="footer__meta">
          <div className="footer__org">
            <a href="http://vnio.org.vn" target="_blank" rel="noopener" style={{ color: 'inherit', textDecoration: 'none' }}>
              <strong>{t('footer.org')}</strong>
            </a>
            <span>{t('footer.dept')}</span><br />
            <span>{t('footer.mission')}</span>
          </div>
          <span className="footer__version">v1.0.0 (Phiên bản thử nghiệm)</span>
        </div>
        <div className="footer__links">
          <Link href="/about">Giới thiệu</Link>
          <Link href="/faq">Câu hỏi thường gặp</Link>
          <a href="https://www.marinespecies.org" target="_blank" rel="noopener">WoRMS</a>
          <a href="https://www.fishbase.se" target="_blank" rel="noopener">FishBase</a>
          <a href="https://www.algaebase.org" target="_blank" rel="noopener">AlgaeBase</a>
          <a href="https://www.inaturalist.org" target="_blank" rel="noopener">iNaturalist</a>
        </div>
      </div>
    </footer>
  )
}

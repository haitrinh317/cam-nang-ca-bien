import { t } from '@/lib/i18n'

export default function Footer() {
  return (
    <footer role="contentinfo">
      <div className="footer-inner">
        <p className="footer__statement">{t('footer.statement')}</p>
        <div className="footer__meta">
          <div className="footer__org">
            <strong>{t('footer.org')}</strong>
            <span>{t('footer.dept')}</span><br />
            <span>{t('footer.mission')}</span>
          </div>
          <span className="footer__version">v4.0.0</span>
        </div>
      </div>
    </footer>
  )
}

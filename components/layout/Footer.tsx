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
          <span className="footer__version">v4.1.0</span>
        </div>
        <div className="footer__links">
          <a href="https://www.marinespecies.org" target="_blank" rel="noopener">WoRMS</a>
          <a href="https://www.fishbase.se" target="_blank" rel="noopener">FishBase</a>
          <a href="https://www.algaebase.org" target="_blank" rel="noopener">AlgaeBase</a>
          <a href="https://github.com/haitrinh317/cam-nang-ca-bien" target="_blank" rel="noopener">GitHub</a>
        </div>
      </div>
    </footer>
  )
}

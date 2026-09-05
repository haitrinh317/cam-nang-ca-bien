'use client'

import React, { useState } from 'react'
import PhotoGallery from './PhotoGallery'
import SpecimenVisualWidgets from './SpecimenVisualWidgets'
import { 
  ExternalLink, 
  CheckCircle, 
  AlertTriangle,
  Tag,
  Globe,
  Fish,
  Compass,
  Sparkles,
  Archive,
  Building2,
  CheckCircle2,
  MapPin,
  Calendar,
  BookOpen,
  Waves,
  Network,
  ShieldCheck,
  CornerDownRight
} from 'lucide-react'
import BiologyDashboard, { BiologyData } from './BiologyDashboard'
import {
  getResolvedMorphologyVn,
  getResolvedEcologyVn,
  getResolvedEconomicValueVn
} from '@/lib/species-text'
import './SpecimenCard.css'

function parseLiterature(lit?: string | null): string[] {
  if (!lit) return []
  const trimmed = lit.trim()
  const numSplit = trimmed.split(/(?=\b\d+\.\s+)/)
  if (numSplit.length > 1) {
    return numSplit.map(s => s.replace(/^\d+\.\s*/, '').trim()).filter(Boolean)
  }
  const lineSplit = trimmed.split(/\r?\n/).map(s => s.trim()).filter(Boolean)
  if (lineSplit.length > 1) return lineSplit
  const semiSplit = trimmed.split(/;\s*/).map(s => s.trim()).filter(Boolean)
  if (semiSplit.length > 1) return semiSplit
  return [trimmed]
}

function parseLocations(str?: string | null): string[] {
  if (!str) return []
  const clean = str.trim().replace(/\.$/, '')
  const parts = clean.split(/[,;]\s+/).map(s => s.trim()).filter(Boolean)
  return parts.length > 0 ? parts : [clean]
}



interface Species {

  id: string
  volume: number
  species_index: number | null
  vn_name: string
  scientific_name: string
  authorship: string | null
  worms_status: string | null
  worms_id: number | null
  worms_accepted_name: string | null
  worms_synced_at: string | null
  tax_class_vn: string | null
  tax_class_latin: string | null
  tax_order_vn: string | null
  tax_order_latin: string | null
  tax_family_vn: string | null
  tax_family_latin: string | null
  tax_genus_vn: string | null
  tax_genus_latin: string | null
  vn_alternate_names: string | null
  vn_size: string | null
  vn_distribution: string | null
  vn_specimen: string | null
  vn_status: string | null
  vn_literature: string | null
  en_common_name: string | null
  en_size: string | null
  en_distribution: string | null
  en_specimen: string | null
  en_status: string | null
  en_literature: string | null
  synonyms: string | string[] | null
  biology: BiologyData | null
  // Morphology + Ecology + Economic Value — from Atlas (Vol 6) format
  morphology_vn: string | null
  morphology_en: string | null
  ecology_vn: string | null
  ecology_en: string | null
  economic_value_vn: string | null
  economic_value_en: string | null
  photo_place: string | null
  photo_depth: string | null
  photo_date: string | null
  photo_url: string | null
  collection_id: string | null
}

type Biology = BiologyData

// ── WoRMS Curatorial Badge (Phương án 1 - Chuẩn /hallmark) ────────
function WormsBadge({ sp }: { sp: Species }) {
  if (!sp.worms_status && !sp.worms_id) return null

  const statusRaw = (sp.worms_status || '').toLowerCase().trim()
  const isValid = statusRaw === 'valid' || statusRaw === 'accepted'
  const isSynonym = statusRaw === 'synonym' || statusRaw === 'unaccepted' ||
                    statusRaw.includes('synonym') || statusRaw.includes('misspelling') ||
                    statusRaw.includes('superseded')
  const isUncertain = statusRaw === 'uncertain' || statusRaw === 'doubtful' || statusRaw === 'nomen dubium'

  let badgeType: 'valid' | 'synonym' | 'uncertain' | 'unknown' = 'unknown'
  let label = 'Chưa có trên WoRMS'
  let tooltip = 'Chưa tìm thấy bản ghi tương ứng trong CSDL WoRMS'
  let icon = <AlertTriangle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
  let inlineTheme = {
    bg: 'rgba(148, 163, 184, 0.12)',
    color: '#64748b',
    border: '1px solid rgba(148, 163, 184, 0.28)'
  }

  if (isValid || (sp.worms_id && !isSynonym && !isUncertain && statusRaw !== 'not_found' && statusRaw !== 'parse_error')) {
    badgeType = 'valid'
    label = 'WoRMS: Tên hợp lệ'
    tooltip = `Tên được xác nhận trên WoRMS (AphiaID: ${sp.worms_id || '—'})${sp.worms_synced_at ? ` · Cập nhật: ${sp.worms_synced_at.substring(0, 10)}` : ''}`
    icon = <CheckCircle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
    inlineTheme = {
      bg: 'rgba(16, 185, 129, 0.08)',
      color: '#047857',
      border: '1px solid rgba(16, 185, 129, 0.3)'
    }
  } else if (isSynonym) {
    badgeType = 'synonym'
    label = 'WoRMS: Danh pháp cũ'
    tooltip = `Danh pháp đồng nghĩa (Synonym). Tên hiện hành: ${sp.worms_accepted_name || '?'}`
    icon = <AlertTriangle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
    inlineTheme = {
      bg: 'rgba(245, 158, 11, 0.08)',
      color: '#b45309',
      border: '1px solid rgba(245, 158, 11, 0.35)'
    }
  } else if (isUncertain) {
    badgeType = 'uncertain'
    label = 'WoRMS: Chưa rõ phân loại'
    tooltip = sp.worms_accepted_name ? `Ghi nhận: ${sp.worms_accepted_name}` : 'Trạng thái phân loại học chưa được xác định chắc chắn'
    icon = <AlertTriangle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
  } else if (statusRaw === 'parse_error') {
    badgeType = 'unknown'
    label = 'WoRMS: Lỗi cú pháp'
    tooltip = 'Lỗi cú pháp định dạng danh pháp khoa học'
    icon = <AlertTriangle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
  }

  const wormsUrl = sp.worms_id
    ? `https://www.marinespecies.org/aphia.php?p=taxdetails&id=${sp.worms_id}` : null

  const pillStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    height: '24px',
    padding: '0 10px',
    borderRadius: '9999px',
    fontSize: '0.72rem',
    fontWeight: 600,
    lineHeight: 1,
    textDecoration: 'none',
    whiteSpace: 'nowrap',
    backgroundColor: inlineTheme.bg,
    color: inlineTheme.color,
    border: inlineTheme.border,
    boxSizing: 'border-box'
  }

  return (
    <div className="worms-badge-wrap" style={{ display: 'inline-flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
      {wormsUrl ? (
        <a
          href={wormsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className={`worms-pill worms-pill--${badgeType}`}
          style={pillStyle}
          title={`${tooltip} — Bấm để mở hồ sơ CSDL WoRMS`}
        >
          <span className="worms-pill__icon" style={{ display: 'inline-flex', alignItems: 'center', marginRight: '2px' }}>{icon}</span>
          <span className="worms-pill__label">{label}</span>
          <ExternalLink size={11} className="worms-pill__ext" style={{ marginLeft: '4px', opacity: 0.7 }} aria-hidden="true" />
        </a>
      ) : (
        <span className={`worms-pill worms-pill--${badgeType}`} style={pillStyle} title={tooltip}>
          <span className="worms-pill__icon" style={{ display: 'inline-flex', alignItems: 'center', marginRight: '2px' }}>{icon}</span>
          <span className="worms-pill__label">{label}</span>
        </span>
      )}

      {isSynonym && sp.worms_accepted_name && (
        <span className="worms-pill__synonym-note" style={{ fontSize: '0.76rem', color: 'var(--color-ink-3, #64748b)', marginLeft: '4px' }}>
          Tên hiện hành: <em className="worms-pill__accepted-name" style={{ fontStyle: 'italic', fontWeight: 600 }}>{sp.worms_accepted_name}</em>
        </span>
      )}
    </div>
  )
}

// BiologyPanel has been upgraded to BiologyDashboard (see BiologyDashboard.tsx)

// ── KV row helpers ────────────────────────────────────────────────
function KvRow({ labelVn, valVn, labelEn, valEn }: { labelVn: string; valVn?: string | null; labelEn?: string; valEn?: string | null }) {
  if (!valVn && !valEn) return null
  return (
    <div className="kv-row">
      <div className="kv-cell"><div className="kv-label">{labelVn}</div><div className="kv-value">{valVn || '—'}</div></div>
      {labelEn && <div className="kv-cell"><div className="kv-label kv-label-en">{labelEn}</div><div className="kv-value kv-value-en">{valEn || '—'}</div></div>}
    </div>
  )
}

// ── Synonym formatting ────────────────────────────────────────────
function formatSynonym(text: string) {
  if (text.includes('<span class="syn-name">')) return text.replace('<span class="syn-name">', '<i>').replace('</span>', '</i>')
  return text.replace(/^([A-Z][a-z\-]+(?: \([A-Z][a-z\-]+\))? [a-z\-]+)(.*)/, '<i>$1</i>$2')
}

// ── Helper chuẩn hóa tên phân loại học (Loại bỏ lặp Latin & rác OCR) ────────
function cleanTaxonHierarchy(rank: string, vnRaw?: string | null, latRaw?: string | null) {
  let vn = (vnRaw || '').trim()
  let lat = (latRaw || '').trim()

  // 1. Bỏ tiền tố rank: Lớp, Bộ, Họ, Giống, Chi
  vn = vn.replace(new RegExp(`^(Lớp|Bộ|Họ|Giống|Chi)\\s*`, 'i'), '')
  // Bỏ số thứ tự (ví dụ "11: ", "12. ")
  vn = vn.replace(/^\d+[\s:\.\-]+/, '')

  // 2. Làm sạch Latin: bỏ tiền tố "Family ", "Order ", "Class "
  lat = lat.replace(/^(Class|Order|Family|Genus)\s+/i, '')

  // 3. Chuẩn hóa Latin cho Chi/Giống: nếu quá dài hoặc chứa trích dẫn sách, chỉ lấy danh pháp chi chính
  if (rank === 'Giống' || rank === 'Chi') {
    const genusWord = lat.split(/\s+/)[0]
    if (lat.length > 35 || lat.includes('Ann.') || lat.includes('Vol.') || lat.includes('pp.') || lat.includes('Type:')) {
      lat = genusWord
    }
  }

  // 4. Chuẩn hóa TitleCase cho Latin nếu bị ALL CAPS (CALLIONYMIDAE -> Callionymidae)
  if (/^[A-Z]{4,}$/.test(lat)) {
    lat = lat.charAt(0) + lat.slice(1).toLowerCase()
  }

  // 5. Tách tên Latin nếu bị dính đuôi vào tên tiếng Việt (ví dụ "Cá Nhám Râu Orectolobidae" -> "Cá Nhám Râu")
  if (lat) {
    const mainLatWord = lat.split(/\s+/)[0]
    if (mainLatWord && mainLatWord.length > 2) {
      const regex = new RegExp(`\\s*\\b${mainLatWord}\\b.*$`, 'i')
      if (regex.test(vn)) {
        const stripped = vn.replace(regex, '').trim()
        if (stripped) vn = stripped
      }
    }
  }

  // 6. Bỏ ngoặc đơn thừa
  vn = vn.replace(/^\((.*)\)$/, '$1').trim()
  lat = lat.replace(/^\((.*)\)$/, '$1').trim()

  return { vn: vn || lat, lat }
}

// ── Main Specimen Card ────────────────────────────────────────────
export default function SpecimenCard({ sp, initialPhotos }: { sp: Species; initialPhotos?: unknown[] }) {
  // Parse synonyms
  let syns: string[] = []
  try { syns = typeof sp.synonyms === 'string' ? JSON.parse(sp.synonyms) : (sp.synonyms || []) } catch { syns = [] }

  // Parse biology
  let bio: Biology | null = null
  try { bio = typeof sp.biology === 'string' ? JSON.parse(sp.biology) : sp.biology } catch { bio = null }

  const cleanAuthor = (sp.authorship || '').replace(/"/g, '').trim()

  // Taxonomy breadcrumb — normalized
  const rawCrumbs = [
    sp.tax_class_vn  ? { rank: 'Lớp',   rankKey: 'class'  as const, vn: sp.tax_class_vn,  lat: sp.tax_class_latin }  : null,
    sp.tax_order_vn  ? { rank: 'Bộ',    rankKey: 'order'  as const, vn: sp.tax_order_vn,  lat: sp.tax_order_latin }  : null,
    sp.tax_family_vn ? { rank: 'Họ',    rankKey: 'family' as const, vn: sp.tax_family_vn, lat: sp.tax_family_latin } : null,
    sp.tax_genus_vn  ? { rank: sp.collection_id === 'thuc-vat-bien' ? 'Chi' : 'Giống', rankKey: 'genus' as const, vn: sp.tax_genus_vn,  lat: sp.tax_genus_latin }  : null,
  ].filter(Boolean) as { rank: string; rankKey: 'class' | 'order' | 'family' | 'genus'; vn: string; lat: string | null }[]

  const crumbs = rawCrumbs.map(c => {
    const cleaned = cleanTaxonHierarchy(c.rank, c.vn, c.lat)
    return {
      rank: c.rank,
      rankKey: c.rankKey,
      vn: cleaned.vn,
      lat: cleaned.lat,
    }
  })

  const familyCrumb = crumbs.find(c => c.rankKey === 'family')
  const isSeaweed = sp.collection_id === 'thuc-vat-bien' || sp.id.startsWith('thucvat-')

  return (
    <div className={`specimen vol-${sp.volume}`}>
      {/* Hero */}
      <header className="specimen__hero">
        <div className="specimen__meta">
          <span className="specimen__index">#{sp.species_index || ''}</span>
          <span className="specimen__vol">
            {sp.collection_id === 'thuc-vat-bien' 
              ? (sp.volume === 2 ? 'Tập II · Rong biển VN (1969)' : 'Tập I · Thực vật phía Nam') 
              : `Tập ${sp.volume || ''}`}
          </span>
        </div>
        <h1 className="specimen__name">{sp.vn_name}</h1>
        <div className="specimen__sci-row" style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px 14px', marginTop: '4px', marginBottom: '8px' }}>
          <p className="specimen__sci" style={{ margin: 0, lineHeight: 1.35 }}>
            <em className="specimen__sci-name" style={{ fontStyle: 'italic' }}>{sp.scientific_name}</em>
            {cleanAuthor && <span className="specimen__author" style={{ fontStyle: 'normal', color: 'var(--color-ink-3, #64748b)', marginLeft: '4px' }}> {cleanAuthor}</span>}
          </p>
          <WormsBadge sp={sp} />
          {familyCrumb && (
            <span className="specimen__family-pill" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.74rem', color: 'var(--color-ink-3, #64748b)', padding: '2px 8px', borderRadius: '4px', background: 'var(--color-paper-2, #f8fafc)', border: '1px solid var(--color-rule-2, rgba(0,0,0,0.06))' }}>
              <span style={{ fontWeight: 600 }}>Họ {familyCrumb.vn}</span>
              {familyCrumb.lat && <em style={{ fontStyle: 'italic', opacity: 0.85 }}>({familyCrumb.lat})</em>}
            </span>
          )}
        </div>
      </header>

      {/* Photo Gallery */}
      <PhotoGallery speciesId={sp.id} fallbackUrl={sp.photo_url} initialPhotos={initialPhotos as any} />

      {/* ── Tab Strip ── */}
      <TabStrip
        sp={sp}
        bio={bio}
        syns={syns}
        speciesId={sp.id}
        crumbs={crumbs}
        cleanAuthor={cleanAuthor}
      />
    </div>
  )
}

// ── Tab Strip sub-component (client state) ───────────────────────
type TabId = 'thongso' | 'sinhhoc' | 'phanloai'

interface TabStripProps {
  sp: Species
  bio: Biology | null
  syns: string[]
  speciesId: string
  crumbs: { rank: string; rankKey: 'class' | 'order' | 'family' | 'genus'; vn: string; lat: string | null }[]
  cleanAuthor: string
}

function TabStrip({ sp, bio, syns, speciesId, crumbs, cleanAuthor }: TabStripProps) {
  const [active, setActive] = useState<TabId>('thongso')
  const isSeaweed = sp.collection_id === 'thuc-vat-bien' || sp.id.startsWith('thucvat-')

  const TABS: { id: TabId; label: string }[] = [
    { id: 'thongso',  label: 'Thông số' },
    { id: 'sinhhoc',  label: 'Sinh học' },
    { id: 'phanloai', label: 'Phân loại' },
  ]

  return (
    <>
      {/* Tab navigation */}
      <div className="detail-tabs" role="tablist">
        {TABS.map(tab => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={active === tab.id}
            aria-controls={`tab-panel-${tab.id}`}
            id={`tab-${tab.id}`}
            className={`detail-tab${active === tab.id ? ' active' : ''}`}
            onClick={() => setActive(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Panel 1: Thông số — Cấu trúc Bento Archive đồng bộ toàn diện */}
      <div
        id="tab-panel-thongso"
        role="tabpanel"
        aria-labelledby="tab-thongso"
        className={`detail-tab-panel${active === 'thongso' ? ' active' : ''}`}
      >
        <div className="specimen-thongso-container">
          {/* 1. Thẻ Định Danh Tên Gọi (Identifier Card) */}
          {(sp.vn_alternate_names || sp.en_common_name) && (
            <div className="specimen-identity-card">
              {sp.vn_alternate_names && (
                <div className="specimen-identity-col">
                  <span className="specimen-identity-label">
                    <Tag size={13} />
                    <span>Tên gọi khác:</span>
                  </span>
                  <span className="specimen-identity-val">{sp.vn_alternate_names}</span>
                </div>
              )}
              {sp.en_common_name && (
                <div className="specimen-identity-col">
                  <span className="specimen-identity-label">
                    <Globe size={13} />
                    <span>Common Name:</span>
                  </span>
                  <span className="specimen-identity-val specimen-identity-val--en">{sp.en_common_name}</span>
                </div>
              )}
            </div>
          )}

          {/* 2. Trực quan hóa dữ liệu sinh trắc học (Kích thước, Độ sâu sinh thái, Vùng biển phân bố) */}
          <SpecimenVisualWidgets
            vnSizeStr={sp.vn_size}
            enSizeStr={sp.en_size}
            maxLengthStr={bio?.maxLength}
            depthStr={bio?.depth}
            depthVnStr={bio?.depthVn}
            distributionStr={sp.vn_distribution || sp.en_distribution}
          />

          {/* 3. Lưới Bento 2 cột (Hình thái học & Sinh thái dinh dưỡng từ sách gốc OCR) */}
          {(() => {
            const displayMorph = getResolvedMorphologyVn(sp, bio)
            const displayEcology = getResolvedEcologyVn(sp)
            if (!displayMorph && !displayEcology) return null

            return (
              <div className="specimen-bento-grid">
                {displayMorph && (
                  <div className="specimen-bento-card">
                    <div className="specimen-bento-card__header">
                      <div className="specimen-bento-card__title-group">
                        <span className="specimen-bento-card__icon">
                          <Fish size={16} />
                        </span>
                        <h3 className="specimen-bento-card__title">Đặc điểm hình thái</h3>
                      </div>
                      <span className="specimen-bento-card__badge">Hình thái học</span>
                    </div>
                    <p
                      className="specimen-bento-card__content"
                      style={{
                        maxWidth: 'none',
                        width: '100%',
                        textWrap: 'pretty',
                      }}
                    >
                      {displayMorph}
                    </p>
                  </div>
                )}

                {displayEcology && (
                  <div className="specimen-bento-card">
                    <div className="specimen-bento-card__header">
                      <div className="specimen-bento-card__title-group">
                        <span className="specimen-bento-card__icon specimen-bento-card__icon--blue">
                          <Compass size={16} />
                        </span>
                        <h3 className="specimen-bento-card__title">Sinh thái &amp; Dinh dưỡng</h3>
                      </div>
                      <span className="specimen-bento-card__badge">Tập tính sinh thái</span>
                    </div>
                    <p
                      className="specimen-bento-card__content"
                      style={{
                        maxWidth: 'none',
                        width: '100%',
                        textWrap: 'pretty',
                      }}
                    >
                      {displayEcology}
                    </p>
                  </div>
                )}
              </div>
            )
          })()}

          {/* 4. Giá trị kinh tế & Sử dụng (Từ sách gốc OCR) */}
          {(() => {
            const displayEconomic = getResolvedEconomicValueVn(sp)
            if (!displayEconomic) return null

            const lower = displayEconomic.toLowerCase()
            const isAquarium = lower.includes('cá cảnh') || lower.includes('làm cảnh') || lower.includes('thủy sinh')
            const isFood = lower.includes('thực phẩm') || lower.includes('thương phẩm') || lower.includes('hải sản') || lower.includes('tươi sống') || lower.includes('ăn thịt')

            return (
              <div className="specimen-value-card">
                <div className="specimen-bento-card__header">
                  <div className="specimen-bento-card__title-group">
                    <span className="specimen-bento-card__icon specimen-bento-card__icon--amber">
                      <Sparkles size={16} />
                    </span>
                    <h3 className="specimen-bento-card__title">Giá trị sử dụng &amp; Kinh tế</h3>
                  </div>
                  <div className="specimen-value-tags">
                    {isAquarium && <span className="specimen-value-tag specimen-value-tag--aquarium">Cá cảnh</span>}
                    {isFood && <span className="specimen-value-tag specimen-value-tag--food">Thực phẩm</span>}
                  </div>
                </div>
                <p
                  className="specimen-bento-card__content"
                  style={{
                    maxWidth: 'none',
                    width: '100%',
                    textWrap: 'pretty',
                  }}
                >
                  {displayEconomic}
                </p>
              </div>
            )
          })()}

          {/* 5. Hồ sơ Mẫu vật & Tài liệu dẫn (Specimen Archive Vault) */}
          {(() => {
            const spec = sp.vn_specimen || sp.en_specimen
            const stat = sp.vn_status || sp.en_status
            const lit = sp.vn_literature || sp.en_literature
            const hasField = sp.photo_place || sp.photo_depth || sp.photo_date
            if (!spec && !stat && !lit && !hasField) return null

            const specList = spec ? parseLocations(spec) : []
            const litList = lit ? parseLiterature(lit) : []

            return (
              <div className="specimen-vault-card">
                <div className="specimen-bento-card__header">
                  <div className="specimen-bento-card__title-group">
                    <span className="specimen-bento-card__icon specimen-bento-card__icon--purple">
                      <Archive size={16} />
                    </span>
                    <h3 className="specimen-bento-card__title">Hồ sơ Mẫu vật &amp; Tài liệu dẫn</h3>
                  </div>
                  {litList.length > 0 && (
                    <span className="specimen-bento-card__badge">
                      <BookOpen size={12} style={{ marginRight: 3 }} />
                      {litList.length} tài liệu dẫn
                    </span>
                  )}
                </div>

                {(specList.length > 0 || stat) && (
                  <div className="specimen-vault-grid">
                    {specList.length > 0 && (
                      <div className="specimen-vault-item">
                        <span className="specimen-vault-item__label">
                          <Building2 size={13} />
                          <span>Nơi lưu trữ mẫu vật</span>
                        </span>
                        {specList.length === 1 ? (
                          <span className="specimen-vault-item__val">{specList[0]}</span>
                        ) : (
                          <div className="specimen-vault-locations">
                            {specList.map((loc, i) => (
                              <div key={i} className="specimen-vault-location-row">
                                <span className="specimen-vault-dot" />
                                <span>{loc}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {stat && (
                      <div className="specimen-vault-item">
                        <span className="specimen-vault-item__label">
                          <CheckCircle2 size={13} />
                          <span>Tình trạng mẫu / ghi nhận</span>
                        </span>
                        <span className="specimen-vault-item__val">{stat}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Thông tin thu mẫu thực địa nếu có */}
                {hasField && (
                  <div className="specimen-vault-meta">
                    {sp.photo_place && (
                      <span className="specimen-meta-pill">
                        <MapPin size={12} />
                        <span>{sp.photo_place}</span>
                      </span>
                    )}
                    {sp.photo_depth && (
                      <span className="specimen-meta-pill">
                        <Waves size={12} />
                        <span>Độ sâu: {sp.photo_depth}</span>
                      </span>
                    )}
                    {sp.photo_date && (
                      <span className="specimen-meta-pill">
                        <Calendar size={12} />
                        <span>Ngày thu mẫu: {sp.photo_date}</span>
                      </span>
                    )}
                  </div>
                )}

                {/* Danh mục tài liệu tham khảo */}
                {litList.length > 0 && (
                  <div className="specimen-literature-box">
                    {litList.map((item, idx) => (
                      <div key={idx} className="specimen-lit-item">
                        <span className="specimen-lit-idx">[{idx + 1}]</span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })()}
        </div>
      </div>

      {/* Panel 2: Sinh học */}
      <div
        id="tab-panel-sinhhoc"
        role="tabpanel"
        aria-labelledby="tab-sinhhoc"
        className={`detail-tab-panel${active === 'sinhhoc' ? ' active' : ''}`}
      >
        {bio
          ? <BiologyDashboard bio={bio} speciesId={speciesId} collectionId={sp.collection_id} />
          : <p className="specimen__empty">Chưa có dữ liệu sinh học cho loài này.</p>
        }
      </div>

      {/* Panel 3: Phân loại */}
      <div
        id="tab-panel-phanloai"
        role="tabpanel"
        aria-labelledby="tab-phanloai"
        className={`detail-tab-panel${active === 'phanloai' ? ' active' : ''}`}
      >
        <div className="specimen-phanloai-container">
          {/* 1. Hệ thống Phân loại học (Taxonomic Stepped Tree) */}
          <div className="specimen-bento-card specimen-tax-lineage-card">
            <div className="specimen-bento-card__header">
              <div className="specimen-bento-card__title-group">
                <span className="specimen-bento-card__icon specimen-bento-card__icon--blue">
                  <Network size={16} />
                </span>
                <h3 className="specimen-bento-card__title">Cây Phân loại học</h3>
              </div>
              <span className="specimen-bento-card__badge">
                {crumbs.length + 1} bậc phân loại
              </span>
            </div>

            <div className="tax-tree-container">
              {crumbs.map((c, idx) => (
                <div
                  key={c.rankKey}
                  className={`tax-tree-node tax-tree-node--${c.rankKey}`}
                  data-level={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '4px 8px',
                    marginLeft: `calc(${idx} * var(--tax-indent, 24px))`
                  }}
                >
                  {idx > 0 && (
                    <span className="tax-tree-branch" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                      <CornerDownRight size={14} />
                    </span>
                  )}
                  <span
                    className={`rank-badge rank-${c.rankKey}`}
                    style={{
                      flexShrink: 0,
                      fontSize: 'var(--text-xs, 0.82rem)',
                      padding: '2px 7px',
                      borderRadius: '4px',
                      letterSpacing: '0.04em'
                    }}
                  >
                    {c.rank}
                  </span>
                  <span
                    className="tax-tree-vn"
                    style={{
                      fontSize: '0.95rem',
                      fontWeight: 600
                    }}
                  >
                    {c.vn}
                  </span>
                  {c.lat && (
                    <em
                      className="tax-tree-lat"
                      style={{
                        fontSize: '0.88rem',
                        fontStyle: 'italic'
                      }}
                    >
                      ({c.lat})
                    </em>
                  )}
                </div>
              ))}

              {/* Bậc Loài cuối cùng (Current Target Specimen) */}
              <div
                className="tax-tree-node tax-tree-node--species tax-tree-node--current"
                data-level={crumbs.length}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '4px 8px',
                  marginLeft: `calc(${crumbs.length} * var(--tax-indent, 24px))`
                }}
              >
                <span className="tax-tree-branch tax-tree-branch--current" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                  <CornerDownRight size={16} />
                </span>
                <span
                  className="rank-badge rank-species"
                  style={{
                    flexShrink: 0,
                    fontSize: 'var(--text-xs, 0.82rem)',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    letterSpacing: '0.05em'
                  }}
                >
                  Loài
                </span>
                <span
                  className="tax-tree-vn tax-tree-vn--current"
                  style={{
                    fontSize: '0.98rem',
                    fontWeight: 600
                  }}
                >
                  {sp.vn_name}
                </span>
                <em
                  className="tax-tree-lat tax-tree-lat--current"
                  style={{
                    fontSize: '0.92rem',
                    fontStyle: 'italic',
                    fontWeight: 600
                  }}
                >
                  {sp.scientific_name}
                </em>
                {cleanAuthor && (
                  <span
                    className="tax-tree-author"
                    style={{
                      fontSize: '0.82rem'
                    }}
                  >
                    {' '}{cleanAuthor}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* 2. Thẩm Định Danh Pháp Quốc Tế (WoRMS Curatorial Dossier) */}
          {(sp.worms_id || sp.worms_status) && (
            <div className="specimen-bento-card specimen-worms-dossier-card">
              <div className="specimen-bento-card__header">
                <div className="specimen-bento-card__title-group">
                  <span className="specimen-bento-card__icon specimen-bento-card__icon--emerald">
                    <ShieldCheck size={16} />
                  </span>
                  <div>
                    <h3 className="specimen-bento-card__title" style={{ fontSize: 'var(--text-lg, 1.15rem)' }}>
                      Hồ sơ Thẩm định Danh pháp Quốc tế
                    </h3>
                    <span style={{ fontSize: 'var(--text-xs, 0.85rem)', color: 'var(--color-ink-3, #64748b)', fontWeight: 500, display: 'block', marginTop: '2px' }}>
                      World Register of Marine Species (WoRMS)
                    </span>
                  </div>
                </div>
              </div>

              <div className="worms-dossier-grid" style={{ marginTop: '6px' }}>
                {/* Tile 1: Trạng thái danh pháp */}
                <div className="worms-tile">
                  <span className="worms-tile__label">
                    Trạng thái danh pháp
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', minHeight: '26px' }}>
                    <WormsBadge sp={sp} />
                  </div>
                  <span className="worms-tile__sub">
                    {(sp.worms_status?.toLowerCase() === 'accepted' || sp.worms_status?.toLowerCase() === 'valid')
                      ? 'Tên hợp lệ được công nhận toàn cầu trong CSDL sinh vật biển'
                      : (sp.worms_status?.toLowerCase().includes('synonym')
                        ? 'Danh pháp đồng nghĩa (tên phân loại cũ trong lịch sử)'
                        : 'Dữ liệu đối soát phân loại học')}
                  </span>
                </div>

                {/* Tile 2: Mã số AphiaID */}
                {sp.worms_id && (
                  <div className="worms-tile">
                    <span className="worms-tile__label">
                      Mã định danh Quốc tế (AphiaID)
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', minHeight: '26px' }}>
                      <code
                        style={{
                          fontFamily: 'var(--font-outlier, monospace)',
                          fontSize: 'var(--text-base, 1.05rem)',
                          fontWeight: 700,
                          color: 'var(--color-ink, #0b1329)',
                          background: 'rgba(11, 19, 41, 0.05)',
                          padding: '2px 8px',
                          borderRadius: '4px'
                        }}
                      >
                        #{sp.worms_id}
                      </code>
                    </div>
                    <span className="worms-tile__sub">
                      Mã số tra cứu định danh duy nhất trong CSDL WoRMS
                    </span>
                  </div>
                )}

                {/* Tile 3: Danh pháp khoa học hiện hành */}
                <div className="worms-tile worms-tile--full">
                  <span className="worms-tile__label">
                    Danh pháp khoa học hiện hành được WoRMS công nhận
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px', minHeight: '26px' }}>
                    <em
                      style={{
                        fontStyle: 'italic',
                        fontWeight: 700,
                        fontSize: '1.05rem',
                        color: 'var(--color-accent, #00d4b8)'
                      }}
                    >
                      {sp.worms_accepted_name || sp.scientific_name}
                    </em>
                    {cleanAuthor && (
                      <span style={{ fontSize: 'var(--text-sm, 0.95rem)', color: 'var(--color-ink-3, #64748b)' }}>
                        {cleanAuthor}
                      </span>
                    )}
                  </div>
                  <span className="worms-tile__sub">
                    {sp.worms_accepted_name
                      ? (sp.worms_status?.toLowerCase().includes('synonym')
                        ? 'Tên khoa học chính thức hiện nay (thay thế cho danh pháp cũ)'
                        : 'Danh pháp mô tả ban đầu được bảo lưu hợp lệ')
                      : 'Danh pháp hiện hành bảo toàn theo công bố phân loại'}
                  </span>
                </div>

                {/* Tile 4: Thời điểm đồng bộ xác thực */}
                {sp.worms_synced_at && (
                  <div className="worms-tile">
                    <span className="worms-tile__label">
                      Thời điểm đồng bộ xác thực
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', minHeight: '26px' }}>
                      <span style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--color-ink, #0b1329)' }}>
                        {sp.worms_synced_at.substring(0, 10)}
                      </span>
                    </div>
                    <span className="worms-tile__sub">
                      Tự động cập nhật qua WoRMS REST API
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 3. Danh pháp đồng nghĩa & Lịch sử mô tả gốc */}
          <div className="specimen-bento-card specimen-synonyms-card">
            <div className="specimen-bento-card__header">
              <div className="specimen-bento-card__title-group">
                <span className="specimen-bento-card__icon specimen-bento-card__icon--purple">
                  <BookOpen size={16} />
                </span>
                <h3 className="specimen-bento-card__title" style={{ fontSize: 'var(--text-lg, 1.15rem)' }}>
                  Danh pháp đồng nghĩa &amp; Phân loại gốc
                </h3>
              </div>
              {syns.length > 0 && (
                <span className="specimen-bento-card__badge" style={{ fontSize: 'var(--text-xs, 0.85rem)' }}>
                  {syns.length} danh pháp ghi nhận
                </span>
              )}
            </div>

            {syns.length > 0 ? (
              <div className="specimen-synonyms-list">
                {syns.map((syn, idx) => {
                  const html = formatSynonym(syn)
                  if (!html) return null
                  return (
                    <div
                      key={idx}
                      className="specimen-synonym-item"
                      style={{
                        display: 'flex',
                        alignItems: 'baseline',
                        gap: '10px',
                        padding: '8px 12px'
                      }}
                    >
                      <span
                        className="specimen-synonym-idx"
                        style={{
                          flexShrink: 0,
                          fontSize: '0.78rem',
                          fontFamily: 'var(--font-outlier, monospace)',
                          fontWeight: 700
                        }}
                      >
                        [{idx + 1}]
                      </span>
                      <div 
                        className="specimen-synonym-text"
                        style={{
                          flex: 1,
                          minWidth: 0,
                          fontSize: '0.82rem',
                          lineHeight: 1.5
                        }}
                        dangerouslySetInnerHTML={{ __html: html }} 
                      />
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="specimen-tax-empty">
                <p className="specimen-tax-empty-text" style={{ fontSize: 'var(--text-sm, 0.95rem)' }}>
                  Chưa ghi nhận danh pháp đồng nghĩa. Danh pháp khoa học hiện hành được công nhận trực tiếp từ công bố mô tả gốc ban đầu.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

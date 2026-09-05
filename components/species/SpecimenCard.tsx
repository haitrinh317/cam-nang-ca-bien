'use client'

import React, { useState } from 'react'
import PhotoGallery from './PhotoGallery'
import SpecimenVisualWidgets from './SpecimenVisualWidgets'
import { ExternalLink, CheckCircle, AlertTriangle } from 'lucide-react'
import BiologyDashboard, { BiologyData } from './BiologyDashboard'

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

// ── WoRMS Badge ───────────────────────────────────────────────────
function WormsBadge({ sp }: { sp: Species }) {
  if (!sp.worms_status && !sp.worms_id) return null

  const statusRaw = (sp.worms_status || '').toLowerCase().trim()
  const isValid = statusRaw === 'valid' || statusRaw === 'accepted'
  const isSynonym = statusRaw === 'synonym' || statusRaw === 'unaccepted' ||
                    statusRaw.includes('synonym') || statusRaw.includes('misspelling') ||
                    statusRaw.includes('superseded')
  const isUncertain = statusRaw === 'uncertain' || statusRaw === 'doubtful' || statusRaw === 'nomen dubium'

  let s = {
    cls: 'fb-valid',
    icon: <CheckCircle size={14} />,
    label: 'Tên hợp lệ trên WoRMS'
  }
  let detail = ''

  if (isValid || (sp.worms_id && !isSynonym && !isUncertain && statusRaw !== 'not_found' && statusRaw !== 'parse_error')) {
    s = { cls: 'fb-valid', icon: <CheckCircle size={14} />, label: 'Tên hợp lệ trên WoRMS' }
    detail = `Tên được xác nhận${sp.worms_synced_at ? ` · cập nhật WoRMS: ${sp.worms_synced_at.substring(0, 10)}` : ''}`
  } else if (isSynonym) {
    s = { cls: 'fb-synonym', icon: <AlertTriangle size={14} />, label: 'Tên cũ — đã được cập nhật' }
    detail = `Tên hiện hành: <span class="fb-accepted">${sp.worms_accepted_name || '?'}</span>`
  } else if (isUncertain) {
    s = { cls: 'fb-synonym', icon: <AlertTriangle size={14} />, label: 'Trạng thái phân loại chưa rõ' }
    detail = sp.worms_accepted_name ? `Ghi nhận: ${sp.worms_accepted_name}` : 'Cần thêm tư liệu khảo sát thực địa'
  } else if (statusRaw === 'parse_error') {
    s = { cls: 'fb-unknown', icon: <AlertTriangle size={14} />, label: 'Không phân tích được tên khoa học' }
    detail = 'Lỗi cú pháp định dạng danh pháp'
  } else {
    s = { cls: 'fb-not-found', icon: <AlertTriangle size={14} />, label: 'Chưa xác minh được trên WoRMS' }
    detail = 'Chưa tìm thấy bản ghi tương ứng trong CSDL WoRMS'
  }

  const wormsUrl = sp.worms_id
    ? `https://www.marinespecies.org/aphia.php?p=taxdetails&id=${sp.worms_id}` : null

  return (
    <div className={`fishbase-bar ${s.cls}`}>
      <span className="fb-icon">{s.icon}</span>
      <div className="fb-body">
        <div className="fb-label">WoRMS — {s.label}</div>
        <div className="fb-detail" dangerouslySetInnerHTML={{ __html: detail }} />
        {wormsUrl && (
          <a href={wormsUrl} className="fb-link" target="_blank" rel="noopener">
            <ExternalLink size={12} /> Xem trên WoRMS (marinespecies.org)
          </a>
        )}
      </div>
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

  const isSeaweed = sp.collection_id === 'thuc-vat-bien' || sp.id.startsWith('thucvat-')
  const enSourceTag = isSeaweed ? 'EN · AlgaeBase' : 'EN · FishBase/GBIF'

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
        <p className="specimen__sci">{sp.scientific_name} <span className="specimen__author">{cleanAuthor}</span></p>
        <WormsBadge sp={sp} />
      </header>

      {/* Photo Gallery */}
      <PhotoGallery speciesId={sp.id} fallbackUrl={sp.photo_url} initialPhotos={initialPhotos as any} />

      {/* Taxonomy breadcrumb — always visible, above tabs */}
      {crumbs.length > 0 && (
        <nav className="specimen__taxonomy" aria-label="Phân loại học">
          {crumbs.map((c, i) => (
            <React.Fragment key={c.rankKey}>
              {i > 0 && <span className="specimen-taxon-sep" aria-hidden="true">›</span>}
              <div className={`specimen-taxon-item taxon-item--${c.rankKey}`}>
                <span className={`specimen-taxon-rank rank-badge rank-${c.rankKey}`}>
                  {c.rank}
                </span>
                <span className="specimen-taxon-names">
                  <span className="specimen-taxon-vn">{c.vn}</span>
                  {c.lat && (
                    <span className="specimen-taxon-lat">
                      {' '}({c.lat})
                    </span>
                  )}
                </span>
              </div>
            </React.Fragment>
          ))}
        </nav>
      )}

      {/* ── Tab Strip ── */}
      <TabStrip
        sp={sp}
        bio={bio}
        syns={syns}
        speciesId={sp.id}
      />
    </div>
  )
}

// ── Tab Strip sub-component (client state) ───────────────────────
type TabId = 'thongso' | 'sinhhoc' | 'phanloai'

function TabStrip({ sp, bio, syns, speciesId }: {
  sp: Species
  bio: Biology | null
  syns: string[]
  speciesId: string
}) {
  const [active, setActive] = useState<TabId>('thongso')
  const isSeaweed = sp.collection_id === 'thuc-vat-bien' || sp.id.startsWith('thucvat-')
  const enSourceTag = isSeaweed ? 'EN · AlgaeBase' : 'EN · FishBase/GBIF'

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

      {/* Panel 1: Thông số — 9 trường tra cứu chuẩn theo format Atlas */}
      <div
        id="tab-panel-thongso"
        role="tabpanel"
        aria-labelledby="tab-thongso"
        className={`detail-tab-panel${active === 'thongso' ? ' active' : ''}`}
      >
        {/* 1–3: Tên + Kích thước & Trực quan hóa dữ liệu sinh học */}
        <section className="specimen__section">
          <h2 className="specimen__section-title">Thông tin chính</h2>
          <KvRow labelVn="Tên gọi khác" valVn={sp.vn_alternate_names} labelEn="Common Name" valEn={sp.en_common_name} />

          {/* Trực quan hóa dữ liệu sinh học (Thước đo kích thước song ngữ VN/EN, Độ sâu sinh thái, Vùng biển Việt Nam & Thế giới) */}
          <SpecimenVisualWidgets
            vnSizeStr={sp.vn_size}
            enSizeStr={sp.en_size}
            maxLengthStr={bio?.maxLength}
            depthStr={bio?.depth}
            depthVnStr={bio?.depthVn}
            distributionStr={sp.vn_distribution || sp.en_distribution}
          />
        </section>

        {/* 4: Mô tả hình thái */}
        {(sp.morphology_vn || sp.morphology_en) && (
          <section className="specimen__section">
            <h2 className="specimen__section-title">Mô tả hình thái</h2>
            <div className="kv-row">
              <div className="kv-cell kv-full">
                {sp.morphology_vn
                  ? <div className="kv-value" style={{ whiteSpace: 'pre-line' }}>{sp.morphology_vn}</div>
                  : sp.morphology_en && (
                    <div className="kv-value" style={{ whiteSpace: 'pre-line' }}>
                      {sp.morphology_en}
                      <span className="source-tag">{enSourceTag}</span>
                    </div>
                  )
                }
              </div>
            </div>
          </section>
        )}

        {/* 5+6: Sinh thái & dinh dưỡng */}
        {(sp.ecology_vn || sp.ecology_en) && (
          <section className="specimen__section">
            <h2 className="specimen__section-title">Sinh thái &amp; Dinh dưỡng</h2>
            <div className="kv-row">
              <div className="kv-cell kv-full">
                {sp.ecology_vn
                  ? <div className="kv-value" style={{ whiteSpace: 'pre-line' }}>{sp.ecology_vn}</div>
                  : sp.ecology_en && (
                    <div className="kv-value" style={{ whiteSpace: 'pre-line' }}>
                      {sp.ecology_en}
                      <span className="source-tag">{enSourceTag}</span>
                    </div>
                  )
                }
              </div>
            </div>
          </section>
        )}


        {/* 8: Giá trị kinh tế */}
        {(sp.economic_value_vn || sp.economic_value_en) && (
          <section className="specimen__section">
            <h2 className="specimen__section-title">Giá trị kinh tế</h2>
            <div className="kv-row">
              <div className="kv-cell kv-full">
                {sp.economic_value_vn
                  ? <div className="kv-value" style={{ whiteSpace: 'pre-line' }}>{sp.economic_value_vn}</div>
                  : sp.economic_value_en && (
                    <div className="kv-value" style={{ whiteSpace: 'pre-line' }}>
                      {sp.economic_value_en}
                      <span className="source-tag">{enSourceTag}</span>
                    </div>
                  )
                }
              </div>
            </div>
          </section>
        )}

        {/* 9: Mẫu vật & Tình trạng */}
        <section className="specimen__section">
          <h2 className="specimen__section-title">Mẫu vật &amp; Tài liệu</h2>
          <KvRow labelVn="Nơi lưu trữ mẫu" valVn={sp.vn_specimen} labelEn="Specimen" valEn={sp.en_specimen} />
          <KvRow labelVn="Tình trạng" valVn={sp.vn_status} labelEn="Status" valEn={sp.en_status} />
          <KvRow labelVn="Tài liệu dẫn" valVn={sp.vn_literature} labelEn="Literature" valEn={sp.en_literature} />
        </section>

        {/* Thu mẫu (nếu có) */}
        {(sp.photo_place || sp.photo_depth || sp.photo_date) && (
          <section className="specimen__section">
            <h2 className="specimen__section-title">Thông tin thu mẫu</h2>
            {sp.photo_place && <KvRow labelVn="Địa điểm" valVn={sp.photo_place} />}
            {sp.photo_depth && <KvRow labelVn="Độ sâu" valVn={sp.photo_depth} />}
            {sp.photo_date && <KvRow labelVn="Ngày thu mẫu" valVn={sp.photo_date} />}
          </section>
        )}
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
        {syns.length > 0 ? (
          <section className="specimen__section">
            <h2 className="specimen__section-title">Danh pháp đồng nghĩa &amp; Phân loại gốc</h2>
            {syns.map((syn, idx) => {
              const html = formatSynonym(syn)
              if (!html) return null
              return (
                <div key={idx} className="kv-row">
                  <div className="kv-cell kv-full kv-value" dangerouslySetInnerHTML={{ __html: html }} />
                </div>
              )
            })}
          </section>
        ) : (
          <p className="specimen__empty">Chưa có danh pháp đồng nghĩa.</p>
        )}
      </div>
    </>
  )
}

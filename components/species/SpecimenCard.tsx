'use client'
import React, { useState } from 'react'
import BilingualNoteBlock from './BilingualNoteBlock'
import PhotoGallery from './PhotoGallery'
import { ExternalLink, CheckCircle, AlertTriangle } from 'lucide-react'

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
  biology: Biology | null
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

interface Biology {
  fbName?: string
  maxLength?: string
  maxWeight?: string
  longevity?: string
  depth?: string
  habitat?: string
  iucnStatus?: string
  dangerous?: string
  feedingType?: string
  trophicLevel?: number
  reproduction?: string
  spawning?: string
  spawnAggregation?: boolean
  parentalCare?: string
  importance?: string
  aquaculture?: string
  biologySummary?: string
  biologySummaryVn?: string
  ecologyNotes?: string
  ecologyNotesVn?: string
  reproductionNotes?: string
  reproductionNotesVn?: string
  morphDescription?: string
  morphDescriptionVn?: string
}

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

// ── Biology Panel ────────────────────────────────────────────────
const IUCN_COLOR: Record<string, string> = {
  LC: '#22c55e', NT: '#84cc16', VU: '#f59e0b',
  EN: '#f97316', CR: '#ef4444', EX: '#7c3aed', DD: '#94a3b8',
}

// Static label translations (EN → VN)
const LABEL_VN: Record<string, string> = {
  'English name (FishBase)': 'Tên tiếng Anh (FishBase)',
  'English name (AlgaeBase)': 'Tên tiếng Anh (AlgaeBase)',
  'Max length': 'Chiều dài tối đa',
  'Max weight': 'Trọng lượng tối đa',
  'Longevity': 'Tuổi thọ',
  'Depth range': 'Độ sâu phân bố',
  'Habitat': 'Môi trường sống',
  'IUCN Red List': 'Sách Đỏ IUCN',
  'Danger to humans': 'Nguy hiểm cho người',
  'Feeding type': 'Kiểu ăn',
  'Trophic level': 'Bậc dinh dưỡng',
  'Reproduction': 'Hình thức sinh sản',
  'Spawning': 'Mùa sinh sản',
  'Spawn aggregation': 'Tập hợp sinh sản',
  'Parental care': 'Chăm sóc con',
  'Importance': 'Giá trị thương mại',
  'Aquaculture': 'Nuôi trồng thủy sản',
}

// Common FishBase enum value translations
const VALUE_VN: Record<string, string> = {
  'hunting macrofauna (predator)': 'Săn mồi lớn (ăn thịt)',
  'browsing on substrate': 'Kiếm ăn trên nền đáy',
  'grazing on substrate': 'Gặm cỏ trên nền đáy',
  'filter feeding': 'Lọc thức ăn',
  'herbivores': 'Ăn thực vật',
  'omnivores': 'Ăn tạp',
  'carnivores': 'Ăn thịt',
  'planktivores': 'Ăn sinh vật phù du',
  'corallivores': 'Ăn san hô',
  'detritivores': 'Ăn mùn bã hữu cơ',
  'dioecism, internal (oviduct) fertilization': 'Phân giới tính, thụ tinh trong (ống dẫn trứng)',
  'dioecism, external fertilization': 'Phân giới tính, thụ tinh ngoài',
  'hermaphroditic': 'Lưỡng tính',
  'oviparous': 'Đẻ trứng',
  'viviparous': 'Đẻ con',
  'ovoviviparous': 'Noãn thai sinh',
  'neritic': 'Vùng ven bờ (neritic)',
  'neritic, coral reefs': 'Vùng ven bờ, rạn san hô',
  'coral reefs': 'Rạn san hô',
  'demersal': 'Tầng đáy',
  'pelagic': 'Tầng nổi',
  'benthopelagic': 'Tầng trung – đáy',
  'bathydemersal': 'Đáy sâu',
  'reef-associated': 'Gần rạn san hô',
  'minor commercial': 'Thương mại nhỏ',
  'commercial': 'Thương mại',
  'of no interest': 'Không có giá trị',
  'no interest': 'Không có giá trị',
  'highly commercial': 'Thương mại lớn',
  'subsistence fisheries': 'Khai thác tự cung tự cấp',
  'gamefish': 'Cá thể thao câu cá',
  'never/rarely': 'Không/hiếm khi',
  'experimental': 'Thử nghiệm',
  'one clear seasonal peak per year': 'Một đỉnh sinh sản rõ ràng mỗi năm',
  'multiple spawning per year': 'Nhiều lần trong năm',
  'traumatogenic': 'Gây thương tích cơ học',
  'venomous': 'Có nọc độc',
  'poisonous to eat': 'Độc khi ăn',
  'harmless': 'Vô hại',
  'potential pest': 'Gây hại tiềm tàng',
  'yes — forms spawning aggregations': 'Có — tập hợp sinh sản theo đàn',
  'other': 'Khác',
}

function tvn(val: string): string {
  return VALUE_VN[val.toLowerCase().trim()] || VALUE_VN[val.trim()] || ''
}

function BioRow({ label, val }: { label: string; val?: string | number | null }) {
  if (!val && val !== 0) return null
  const labelVn = LABEL_VN[label] || label
  const valStr = String(val)
  const valVn = typeof val === 'string' ? tvn(val) : ''
  return (
    <div className="kv-row">
      <div className="kv-cell">
        <div className="kv-label">{labelVn}</div>
        <div className="kv-value">{valVn || valStr}</div>
      </div>
      <div className="kv-cell">
        <div className="kv-label kv-label-en">{label}</div>
        <div className="kv-value kv-value-en">{valStr}</div>
      </div>
    </div>
  )
}

function BiologyPanel({ bio, speciesId, collectionId }: { bio: Biology; speciesId: string; collectionId?: string | null }) {
  const isSeaweed = collectionId === 'thuc-vat-bien' || speciesId.startsWith('thucvat-')
  const srcName = isSeaweed ? 'AlgaeBase' : 'FishBase'
  const iucn = bio.iucnStatus
  const iucnColor = iucn ? (IUCN_COLOR[iucn] || '#94a3b8') : ''
  return (
    <>
      <section className="specimen__section">
        <h2 className="specimen__section-title">Sinh học — Sinh thái <span className="panel-badge">BIO</span></h2>
        <BioRow label={`English name (${srcName})`} val={bio.fbName} />
        <BioRow label="Max length" val={bio.maxLength} />
        <BioRow label="Max weight" val={bio.maxWeight} />
        <BioRow label="Longevity" val={bio.longevity} />
        <BioRow label="Depth range" val={bio.depth} />
        <BioRow label="Habitat" val={bio.habitat} />
        {iucn && (
          <div className="kv-row">
            <div className="kv-cell">
              <div className="kv-label">Sách Đỏ IUCN</div>
              <div className="kv-value">
                <span style={{
                  display: 'inline-block', padding: '0.15rem 0.5rem', borderRadius: '4px',
                  background: `${iucnColor}22`, border: `1px solid ${iucnColor}55`,
                  color: iucnColor, fontWeight: 700, fontSize: '0.82rem', letterSpacing: '.05em',
                }}>{iucn}</span>
              </div>
            </div>
            <div className="kv-cell">
              <div className="kv-label kv-label-en">IUCN Red List</div>
              <div className="kv-value kv-value-en">{iucn}</div>
            </div>
          </div>
        )}
        <BioRow label="Danger to humans" val={bio.dangerous} />
        <BioRow label="Feeding type" val={bio.feedingType} />
        {bio.trophicLevel != null && <BioRow label="Trophic level" val={bio.trophicLevel.toFixed(2)} />}
        <BioRow label="Reproduction" val={bio.reproduction} />
        <BioRow label="Spawning" val={bio.spawning} />
        {bio.spawnAggregation && <BioRow label="Spawn aggregation" val="Yes — forms spawning aggregations" />}
        <BioRow label="Parental care" val={bio.parentalCare} />
        <BioRow label="Importance" val={bio.importance} />
        <BioRow label="Aquaculture" val={bio.aquaculture} />
      </section>

      {(bio.biologySummary || bio.ecologyNotes || bio.reproductionNotes || bio.morphDescription) && (
        <section className="specimen__section">
          <h2 className="specimen__section-title">Ghi chú chi tiết</h2>
          {bio.biologySummary && (
            <BilingualNoteBlock
              labelEn={`Biology summary (${srcName})`} labelVn={`Tóm tắt sinh học (${srcName})`}
              text={bio.biologySummary} textVn={bio.biologySummaryVn} cacheKey={`bio_summary_${speciesId}`}
            />
          )}
          {bio.ecologyNotes && (
            <BilingualNoteBlock
              labelEn="Ecology notes" labelVn="Ghi chú sinh thái"
              text={bio.ecologyNotes} textVn={bio.ecologyNotesVn} cacheKey={`ecology_${speciesId}`}
            />
          )}
          {bio.reproductionNotes && (
            <BilingualNoteBlock
              labelEn="Reproduction notes" labelVn="Ghi chú sinh sản"
              text={bio.reproductionNotes} textVn={bio.reproductionNotesVn} cacheKey={`repro_${speciesId}`}
            />
          )}
          {bio.morphDescription && (
            <BilingualNoteBlock
              labelEn="Morphological description (GBIF)" labelVn="Mô tả hình thái (GBIF)"
              text={bio.morphDescription} textVn={bio.morphDescriptionVn} cacheKey={`morph_${speciesId}`}
            />
          )}
        </section>
      )}
    </>
  )
}

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

// ── Main Specimen Card ────────────────────────────────────────────
export default function SpecimenCard({ sp }: { sp: Species }) {
  // Parse synonyms
  let syns: string[] = []
  try { syns = typeof sp.synonyms === 'string' ? JSON.parse(sp.synonyms) : (sp.synonyms || []) } catch { syns = [] }

  // Parse biology
  let bio: Biology | null = null
  try { bio = typeof sp.biology === 'string' ? JSON.parse(sp.biology) : sp.biology } catch { bio = null }

  const cleanAuthor = (sp.authorship || '').replace(/"/g, '').trim()

  // Taxonomy breadcrumb
  const crumbs = [
    sp.tax_class_vn  ? { rank: 'Lớp',   vn: sp.tax_class_vn,  lat: sp.tax_class_latin }  : null,
    sp.tax_order_vn  ? { rank: 'Bộ',    vn: sp.tax_order_vn,  lat: sp.tax_order_latin }  : null,
    sp.tax_family_vn ? { rank: 'Họ',    vn: sp.tax_family_vn, lat: sp.tax_family_latin } : null,
    sp.tax_genus_vn  ? { rank: sp.collection_id === 'thuc-vat-bien' ? 'Chi' : 'Giống', vn: sp.tax_genus_vn,  lat: sp.tax_genus_latin }  : null,
  ].filter(Boolean) as { rank: string; vn: string; lat: string | null }[]

  return (
    <div className={`specimen vol-${sp.volume}`}>
      {/* Hero */}
      <header className="specimen__hero">
        <div className="specimen__meta">
          <span className="specimen__index">#{sp.species_index || ''}</span>
          <span className="specimen__vol">
            {sp.collection_id === 'thuc-vat-bien' ? 'Sách Thực vật' : `Tập ${sp.volume || ''}`}
          </span>
        </div>
        <h1 className="specimen__name">{sp.vn_name}</h1>
        <p className="specimen__sci">{sp.scientific_name} <span className="specimen__author">{cleanAuthor}</span></p>
        <WormsBadge sp={sp} />
      </header>

      {/* Photo Gallery */}
      <PhotoGallery speciesId={sp.id} fallbackUrl={sp.photo_url} />

      {/* Taxonomy breadcrumb — always visible, above tabs */}
      <nav className="specimen__taxonomy" aria-label="Phân loại học">
        {crumbs.map((c, i) => {
          const cleanName = c.vn.replace(new RegExp(`^${c.rank}\\s+`, 'i'), '')
          return (
            <React.Fragment key={c.rank}>
              {i > 0 && <span className="crumb-sep">›</span>}
              <span className="crumb">
                <span className="crumb-rank">{c.rank}</span> {cleanName} <em>({c.lat || ''})</em>
              </span>
            </React.Fragment>
          )
        })}
      </nav>

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
        {/* 1–3: Tên + Kích thước */}
        <section className="specimen__section">
          <h2 className="specimen__section-title">Thông tin chính</h2>
          <KvRow labelVn="Tên gọi khác" valVn={sp.vn_alternate_names} labelEn="Common Name (EN)" valEn={sp.en_common_name} />
          <KvRow labelVn="Kích thước" valVn={sp.vn_size} labelEn="Size" valEn={sp.en_size} />
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
                      <span className="source-tag">EN · FishBase/GBIF</span>
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
                      <span className="source-tag">EN · FishBase/GBIF</span>
                    </div>
                  )
                }
              </div>
            </div>
          </section>
        )}

        {/* 7: Phân bố */}
        {(sp.vn_distribution || sp.en_distribution) && (
          <section className="specimen__section">
            <h2 className="specimen__section-title">Phân bố</h2>
            <div className="kv-row">
              <div className="kv-cell kv-full">
                {sp.vn_distribution
                  ? <div className="kv-value" style={{ whiteSpace: 'pre-line' }}>{sp.vn_distribution}</div>
                  : sp.en_distribution && (
                    <div className="kv-value" style={{ whiteSpace: 'pre-line' }}>
                      {sp.en_distribution}
                      <span className="source-tag">EN · FishBase/GBIF</span>
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
                      <span className="source-tag">EN · FishBase/GBIF</span>
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
          ? <BiologyPanel bio={bio} speciesId={speciesId} collectionId={sp.collection_id} />
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

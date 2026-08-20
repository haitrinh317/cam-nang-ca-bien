import React from 'react'

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
  // Morphology + Photo data — shared across all collections
  morphology_vn: string | null
  morphology_en: string | null
  photo_place: string | null
  photo_depth: string | null
  photo_date: string | null
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
  ecologyNotes?: string
  reproductionNotes?: string
  morphDescription?: string
}

// ── WoRMS Badge ───────────────────────────────────────────────────
function WormsBadge({ sp }: { sp: Species }) {
  if (!sp.worms_status) return null

  const statusMap: Record<string, { cls: string; icon: string; label: string }> = {
    valid:       { cls: 'fb-valid',     icon: '✅', label: 'Tên hợp lệ trên WoRMS' },
    synonym:     { cls: 'fb-synonym',   icon: '🔄', label: 'Tên cũ — đã được cập nhật' },
    uncertain:   { cls: 'fb-synonym',   icon: '⚠️', label: 'Trạng thái phân loại chưa rõ' },
    not_found:   { cls: 'fb-not-found', icon: '❓', label: 'Chưa xác minh được trên WoRMS' },
    parse_error: { cls: 'fb-unknown',   icon: '⚠️', label: 'Không phân tích được tên khoa học' },
  }
  const s = statusMap[sp.worms_status] || statusMap['not_found']
  const wormsUrl = sp.worms_id
    ? `https://www.marinespecies.org/aphia.php?p=taxdetails&id=${sp.worms_id}` : null

  let detail = 'Chưa xác minh được trên WoRMS'
  if (sp.worms_status === 'valid') {
    detail = `Tên được xác nhận${sp.worms_synced_at ? ` · cập nhật WoRMS: ${sp.worms_synced_at.substring(0, 10)}` : ''}`
  } else if (sp.worms_status === 'synonym') {
    detail = `Tên hiện hành: <span class="fb-accepted">${sp.worms_accepted_name || '?'}</span>`
  }

  return (
    <div className={`fishbase-bar ${s.cls}`}>
      <span className="fb-icon">{s.icon}</span>
      <div className="fb-body">
        <div className="fb-label">WoRMS — {s.label}</div>
        <div className="fb-detail" dangerouslySetInnerHTML={{ __html: detail }} />
        {wormsUrl && (
          <a href={wormsUrl} className="fb-link" target="_blank" rel="noopener">
            → Xem trên WoRMS (marinespecies.org)
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

function BioRow({ label, val }: { label: string; val?: string | number | null }) {
  if (!val && val !== 0) return null
  return (
    <div className="info-item">
      <div className="info-label">{label}</div>
      <div className="info-value">{val}</div>
    </div>
  )
}

function BiologyPanel({ bio }: { bio: Biology }) {
  const iucn = bio.iucnStatus
  const iucnColor = iucn ? (IUCN_COLOR[iucn] || '#94a3b8') : ''
  return (
    <div className="biology-panel">
      <div className="panel-title">Sinh học — Sinh thái <span className="panel-badge">BIO</span></div>
      <div className="bio-grid">
        <div>
          <BioRow label="English name (FishBase)" val={bio.fbName} />
          <BioRow label="Max length" val={bio.maxLength} />
          <BioRow label="Max weight" val={bio.maxWeight} />
          <BioRow label="Longevity" val={bio.longevity} />
          <BioRow label="Depth range" val={bio.depth} />
          <BioRow label="Habitat" val={bio.habitat} />
          {iucn && (
            <div className="info-item">
              <div className="info-label">IUCN Red List</div>
              <div className="info-value">
                <span style={{
                  display: 'inline-block', padding: '0.2rem 0.55rem', borderRadius: '5px',
                  background: `${iucnColor}22`, border: `1px solid ${iucnColor}55`,
                  color: iucnColor, fontWeight: 700, fontSize: '0.85rem', letterSpacing: '.05em',
                }}>{iucn}</span>
              </div>
            </div>
          )}
          <BioRow label="Danger to humans" val={bio.dangerous} />
        </div>
        <div>
          <BioRow label="Feeding type" val={bio.feedingType} />
          {bio.trophicLevel != null && <BioRow label="Trophic level" val={bio.trophicLevel.toFixed(2)} />}
          <BioRow label="Reproduction" val={bio.reproduction} />
          <BioRow label="Spawning" val={bio.spawning} />
          {bio.spawnAggregation && <BioRow label="Spawn aggregation" val="Yes — forms spawning aggregations" />}
          <BioRow label="Parental care" val={bio.parentalCare} />
          <BioRow label="Importance" val={bio.importance} />
          <BioRow label="Aquaculture" val={bio.aquaculture} />
        </div>
      </div>
      {(bio.biologySummary || bio.ecologyNotes || bio.reproductionNotes || bio.morphDescription) && (
        <div className="bio-notes">
          {bio.biologySummary && <div className="bio-notes-block"><div className="info-label">Biology summary (FishBase)</div><div className="bio-notes-text">{bio.biologySummary}</div></div>}
          {bio.ecologyNotes && <div className="bio-notes-block"><div className="info-label">Ecology notes</div><div className="bio-notes-text">{bio.ecologyNotes}</div></div>}
          {bio.reproductionNotes && <div className="bio-notes-block"><div className="info-label">Reproduction notes</div><div className="bio-notes-text">{bio.reproductionNotes}</div></div>}
          {bio.morphDescription && <div className="bio-notes-block"><div className="info-label">Morphological description (GBIF)</div><div className="bio-notes-text">{bio.morphDescription}</div></div>}
        </div>
      )}
    </div>
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
    sp.tax_genus_vn  ? { rank: 'Giống', vn: sp.tax_genus_vn,  lat: sp.tax_genus_latin }  : null,
  ].filter(Boolean) as { rank: string; vn: string; lat: string | null }[]

  return (
    <div className={`specimen vol-${sp.volume}`}>
      {/* Hero */}
      <header className="specimen__hero">
        <div className="specimen__meta">
          <span className="specimen__index">#{sp.species_index || ''}</span>
          <span className="specimen__vol">Tập {sp.volume || ''}</span>
        </div>
        <h1 className="specimen__name">{sp.vn_name}</h1>
        <p className="specimen__sci">{sp.scientific_name} <span className="specimen__author">{cleanAuthor}</span></p>
        <WormsBadge sp={sp} />
      </header>

      {/* Taxonomy breadcrumb */}
      <nav className="specimen__taxonomy" aria-label="Phân loại học">
        {crumbs.map((c, i) => (
          <React.Fragment key={c.rank}>
            {i > 0 && <span className="crumb-sep">›</span>}
            <span className="crumb">
              <span className="crumb-rank">{c.rank}</span> {c.vn} <em>({c.lat || ''})</em>
            </span>
          </React.Fragment>
        ))}

      </nav>

      {/* Section: Thông số chính */}
      <section className="specimen__section">
        <h2 className="specimen__section-title">Thông số chính</h2>
        <KvRow labelVn="Tên gọi khác" valVn={sp.vn_alternate_names} labelEn="Common Name" valEn={sp.en_common_name} />
        <KvRow labelVn="Kích thước" valVn={sp.vn_size} labelEn="Size" valEn={sp.en_size} />
        <KvRow labelVn="Phân bố" valVn={sp.vn_distribution} labelEn="Distribution" valEn={sp.en_distribution} />
      </section>

      {/* Section: Mẫu vật & Tình trạng */}
      <section className="specimen__section">
        <h2 className="specimen__section-title">Mẫu vật &amp; Tình trạng</h2>
        <KvRow labelVn="Nơi lưu trữ mẫu" valVn={sp.vn_specimen} labelEn="Specimen" valEn={sp.en_specimen} />
        <KvRow labelVn="Tình trạng" valVn={sp.vn_status} labelEn="Status" valEn={sp.en_status} />
        <KvRow labelVn="Tài liệu dẫn" valVn={sp.vn_literature} labelEn="Literature" valEn={sp.en_literature} />
      </section>

      {/* Section: Hình thái học — hiện khi có morphology */}
      {(sp.morphology_vn || sp.morphology_en) && (
        <section className="specimen__section">
          <h2 className="specimen__section-title">Hình thái học</h2>
          <KvRow labelVn="Mô tả (VN)" valVn={sp.morphology_vn} labelEn="Morphology (EN)" valEn={sp.morphology_en} />
        </section>
      )}

      {/* Section: Thông tin thu mẫu — hiện khi có photo data */}
      {(sp.photo_place || sp.photo_depth || sp.photo_date) && (
        <section className="specimen__section">
          <h2 className="specimen__section-title">Thông tin thu mẫu</h2>
          {sp.photo_place && <KvRow labelVn="Địa điểm" valVn={sp.photo_place} />}
          {sp.photo_depth && <KvRow labelVn="Độ sâu" valVn={sp.photo_depth} />}
          {sp.photo_date && <KvRow labelVn="Ngày thu mẫu" valVn={sp.photo_date} />}
        </section>
      )}

      {/* Synonyms */}
      {syns.length > 0 && (
        <details className="synonym-details">
          <summary className="synonym-summary">Danh pháp đồng nghĩa (Synonyms) &amp; Phân loại học gốc</summary>
          <div className="synonym-content-inner">
            <div className="synonym-content" dangerouslySetInnerHTML={{
              __html: syns.map(formatSynonym).filter(Boolean).join('<br><br>')
            }} />
          </div>
        </details>
      )}

      {/* Biology */}
      {bio && <BiologyPanel bio={bio} />}
    </div>
  )
}

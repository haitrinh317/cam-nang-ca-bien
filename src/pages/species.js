/**
 * species.js — Chi tiết loài: query Supabase 1 row thay fetch 2 file lớn
 */
import { createClient } from '@supabase/supabase-js'
import '../assets/shared.css'
import '../lib/pwa.js'

const db = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

const speciesId   = new URLSearchParams(window.location.search).get('id')
const loadingEl   = document.getElementById('loadingState')
const errorEl     = document.getElementById('errorState')
const containerEl = document.getElementById('speciesDetail')

if (!speciesId) {
  loadingEl.style.display = 'none'
  errorEl.style.display   = 'block'
} else {
  loadSpecies(speciesId)
}

async function loadSpecies(id) {
  const { data, error } = await db
    .from('species')
    .select('*')
    .eq('id', id)
    .single()

  loadingEl.style.display = 'none'

  if (error || !data) {
    errorEl.style.display = 'block'
    return
  }

  renderSpecies(data)
}

// ── WoRMS Badge ──────────────────────────────────────────────────
function buildWormsBadge(sp) {
  if (!sp.worms_status) return ''

  const statusMap = {
    valid:       { cls: 'fb-valid',     icon: '✅', label: 'Tên hợp lệ trên WoRMS' },
    synonym:     { cls: 'fb-synonym',   icon: '🔄', label: 'Tên cũ — đã được cập nhật' },
    uncertain:   { cls: 'fb-synonym',   icon: '⚠️', label: 'Trạng thái phân loại chưa rõ' },
    not_found:   { cls: 'fb-not-found', icon: '❓', label: 'Chưa xác minh được trên WoRMS' },
    parse_error: { cls: 'fb-unknown',   icon: '⚠️', label: 'Không phân tích được tên khoa học' },
  }

  const s      = statusMap[sp.worms_status] || statusMap['not_found']
  const wormsUrl = sp.worms_id
    ? `https://www.marinespecies.org/aphia.php?p=taxdetails&id=${sp.worms_id}` : null

  let detail = ''
  if (sp.worms_status === 'valid') {
    detail = `Tên được xác nhận${sp.worms_synced_at ? ` · cập nhật WoRMS: ${sp.worms_synced_at.substring(0,10)}` : ''}`
  } else if (sp.worms_status === 'synonym') {
    detail = `Tên hiện hành: <span class="fb-accepted">${sp.worms_accepted_name || '?'}</span>`
  } else {
    detail = 'Chưa xác minh được trên WoRMS'
  }

  const linkHtml = wormsUrl
    ? `<a href="${wormsUrl}" class="fb-link" target="_blank" rel="noopener">→ Xem trên WoRMS (marinespecies.org)</a>` : ''

  return `
  <div class="fishbase-bar ${s.cls}">
    <span class="fb-icon">${s.icon}</span>
    <div class="fb-body">
      <div class="fb-label">WoRMS — ${s.label}</div>
      <div class="fb-detail">${detail}</div>
      ${linkHtml}
    </div>
  </div>`
}

// ── Biology Panel (FishBase + GBIF) ─────────────────────────────
function buildBiologyPanel(bio) {
  if (!bio) return ''

  const iucnColor = {
    LC: '#22c55e', NT: '#84cc16', VU: '#f59e0b',
    EN: '#f97316', CR: '#ef4444', EX: '#7c3aed', DD: '#94a3b8'
  }

  function row(label, val) {
    if (!val && val !== 0) return ''
    return `<div class="info-item">
      <div class="info-label">${label}</div>
      <div class="info-value">${val}</div>
    </div>`
  }

  const iucn = bio.iucnStatus
  const iucnBadge = iucn ? `<span style="
    display:inline-block;padding:0.2rem 0.55rem;border-radius:5px;
    background:${iucnColor[iucn] || '#94a3b8'}22;
    border:1px solid ${iucnColor[iucn] || '#94a3b8'}55;
    color:${iucnColor[iucn] || '#94a3b8'};
    font-weight:700;font-size:0.85rem;letter-spacing:.05em;
  ">${iucn}</span>` : ''

  const cols = [
    // Left col
    [
      row('English name (FishBase)', bio.fbName),
      row('Max length', bio.maxLength),
      row('Max weight', bio.maxWeight),
      row('Longevity', bio.longevity),
      row('Depth range', bio.depth),
      row('Habitat', bio.habitat),
      iucn ? `<div class="info-item"><div class="info-label">IUCN Red List</div><div class="info-value">${iucnBadge}</div></div>` : '',
      row('Danger to humans', bio.dangerous),
    ].filter(Boolean).join(''),
    // Right col
    [
      row('Feeding type', bio.feedingType),
      bio.trophicLevel ? row('Trophic level', bio.trophicLevel.toFixed(2)) : '',
      row('Reproduction', bio.reproduction),
      row('Spawning', bio.spawning),
      bio.spawnAggregation ? row('Spawn aggregation', 'Yes — forms spawning aggregations') : '',
      row('Parental care', bio.parentalCare),
      row('Importance', bio.importance),
      row('Aquaculture', bio.aquaculture),
    ].filter(Boolean).join(''),
  ]

  // Long text blocks (full width)
  const notes = [
    bio.biologySummary   ? `<div class="bio-notes-block"><div class="info-label">Biology summary (FishBase)</div><div class="bio-notes-text">${bio.biologySummary}</div></div>` : '',
    bio.ecologyNotes     ? `<div class="bio-notes-block"><div class="info-label">Ecology notes</div><div class="bio-notes-text">${bio.ecologyNotes}</div></div>` : '',
    bio.reproductionNotes? `<div class="bio-notes-block"><div class="info-label">Reproduction notes</div><div class="bio-notes-text">${bio.reproductionNotes}</div></div>` : '',
    bio.morphDescription ? `<div class="bio-notes-block"><div class="info-label">Morphological description (GBIF)</div><div class="bio-notes-text">${bio.morphDescription}</div></div>` : '',
  ].filter(Boolean).join('')

  const hasData = cols[0] || cols[1] || notes
  if (!hasData) return ''

  return `
  <div class="biology-panel">
    <div class="panel-title">Sinh học — Sinh thái <span class="panel-badge">BIO</span></div>
    <div class="bio-grid">
      <div>${cols[0]}</div>
      <div>${cols[1]}</div>
    </div>
    ${notes ? `<div class="bio-notes">${notes}</div>` : ''}
  </div>`
}

// ── Helpers ──────────────────────────────────────────────────────
function formatOneSynonym(text) {
  if (!text) return ''
  let s = text.trim()
  if (s.includes('<span class="syn-name">')) {
    return s.replace('<span class="syn-name">', '<i>').replace('</span>', '</i>')
  }
  return s.replace(/^([A-Z][a-z\-]+(?: \([A-Z][a-z\-]+\))? [a-z\-]+)(.*)/, '<i>$1</i>$2')
}

// ── Render ───────────────────────────────────────────────────────
function renderSpecies(sp) {
  // Taxonomy badges (flat columns từ Supabase)
  const taxParts = [
    sp.tax_class_vn  ? `<div class="tax-badge"><span class="tax-badge-label">Lớp:</span> <span class="tax-badge-value">${sp.tax_class_vn.toUpperCase()}</span> <span class="tax-badge-en">(${sp.tax_class_latin || ''})</span></div>` : '',
    sp.tax_order_vn  ? `<div class="tax-badge"><span class="tax-badge-label">Bộ:</span> <span class="tax-badge-value">${sp.tax_order_vn.toUpperCase()}</span> <span class="tax-badge-en">(${sp.tax_order_latin || ''})</span></div>` : '',
    sp.tax_family_vn ? `<div class="tax-badge"><span class="tax-badge-label">Họ:</span> <span class="tax-badge-value">${sp.tax_family_vn.toUpperCase()}</span> <span class="tax-badge-en">(${sp.tax_family_latin || ''})</span></div>` : '',
    sp.tax_genus_vn  ? `<div class="tax-badge"><span class="tax-badge-label">Giống:</span> <span class="tax-badge-value">${sp.tax_genus_vn}</span> <span class="tax-badge-en">(${sp.tax_genus_latin || ''})</span></div>` : '',
  ].filter(Boolean).join('')

  // Synonyms — stored as JSONB string
  let syns = []
  try {
    syns = typeof sp.synonyms === 'string' ? JSON.parse(sp.synonyms) : (sp.synonyms || [])
  } catch { syns = [] }
  const synsHtml = syns.length
    ? `<details class="synonym-details">
        <summary class="synonym-summary">Danh pháp đồng nghĩa (Synonyms) &amp; Phân loại học gốc</summary>
        <div class="synonym-content-inner">
          <div class="synonym-content">${syns.map(formatOneSynonym).filter(Boolean).join('<br><br>')}</div>
        </div>
       </details>` : ''

  const cleanAuthor = (sp.authorship || '').replace(/"/g, '').trim()

  containerEl.innerHTML = `
    <div class="species-card vol-${sp.volume}">
      <div class="sp-header">
        <h1 class="sp-title">${sp.vn_name}</h1>
        <div class="sp-sci-title">${sp.scientific_name} <span class="sp-author">${cleanAuthor}</span></div>
        ${buildWormsBadge(sp)}
      </div>

      <div class="taxonomy-bar">${taxParts}</div>

      <div class="grid-info">
        <!-- Tiếng Việt -->
        <div class="info-panel">
          <div class="panel-title">Thông số tiếng Việt <span class="panel-badge">VN</span></div>
          <div class="info-item info-item-featured">
            <div class="info-label">Tên gọi khác</div>
            <div class="info-value">${sp.vn_alternate_names || '—'}</div>
          </div>
          <div class="info-item"><div class="info-label">Kích thước</div><div class="info-value">${sp.vn_size || '—'}</div></div>
          <div class="info-item"><div class="info-label">Phân bố</div><div class="info-value">${sp.vn_distribution || '—'}</div></div>
          <div class="info-item"><div class="info-label">Nơi lưu trữ mẫu</div><div class="info-value">${sp.vn_specimen || '—'}</div></div>
          <div class="info-item"><div class="info-label">Tình trạng</div><div class="info-value">${sp.vn_status || '—'}</div></div>
          <div class="info-item"><div class="info-label">Tài liệu dẫn</div><div class="info-value">${sp.vn_literature || '—'}</div></div>
        </div>

        <!-- English -->
        <div class="info-panel">
          <div class="panel-title">English Specifications <span class="panel-badge">EN</span></div>
          <div class="info-item info-item-featured">
            <div class="info-label">Common Name</div>
            <div class="info-value">${sp.en_common_name || '—'}</div>
          </div>
          <div class="info-item"><div class="info-label">Size</div><div class="info-value">${sp.en_size || '—'}</div></div>
          <div class="info-item"><div class="info-label">Distribution</div><div class="info-value">${sp.en_distribution || '—'}</div></div>
          <div class="info-item"><div class="info-label">Conservation / Specimen</div><div class="info-value">${sp.en_specimen || '—'}</div></div>
          <div class="info-item"><div class="info-label">Status</div><div class="info-value">${sp.en_status || '—'}</div></div>
          <div class="info-item"><div class="info-label">Literature</div><div class="info-value">${sp.en_literature || '—'}</div></div>
        </div>
      </div>

      ${synsHtml}
      ${buildBiologyPanel(sp.biology)}
    </div>`

  containerEl.style.display = 'block'
  document.title = `${sp.vn_name} — Danh Mục Cá Biển Việt Nam`
}

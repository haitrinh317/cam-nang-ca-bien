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

// ── Render — Museum Specimen Card ────────────────────────────────
function renderSpecies(sp) {
  // Taxonomy breadcrumb: Lớp › Bộ › Họ › Giống
  const taxCrumbs = [
    sp.tax_class_vn  ? `<span class="crumb"><span class="crumb-rank">Lớp</span> ${sp.tax_class_vn} <em>(${sp.tax_class_latin || ''})</em></span>` : '',
    sp.tax_order_vn  ? `<span class="crumb"><span class="crumb-rank">Bộ</span> ${sp.tax_order_vn} <em>(${sp.tax_order_latin || ''})</em></span>` : '',
    sp.tax_family_vn ? `<span class="crumb"><span class="crumb-rank">Họ</span> ${sp.tax_family_vn} <em>(${sp.tax_family_latin || ''})</em></span>` : '',
    sp.tax_genus_vn  ? `<span class="crumb"><span class="crumb-rank">Giống</span> ${sp.tax_genus_vn} <em>(${sp.tax_genus_latin || ''})</em></span>` : '',
  ].filter(Boolean).join('<span class="crumb-sep">›</span>')

  // Synonyms
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

  // Key-value row helper
  function kv(labelVn, valVn, labelEn, valEn) {
    if (!valVn && !valEn) return ''
    const vnPart = `<div class="kv-cell"><div class="kv-label">${labelVn}</div><div class="kv-value">${valVn || '—'}</div></div>`
    const enPart = labelEn
      ? `<div class="kv-cell"><div class="kv-label kv-label-en">${labelEn}</div><div class="kv-value kv-value-en">${valEn || '—'}</div></div>`
      : ''
    return `<div class="kv-row">${vnPart}${enPart}</div>`
  }

  // Single key-value (no bilingual pair)
  function kvSingle(label, val, extra) {
    if (!val) return ''
    return `<div class="kv-row"><div class="kv-cell kv-full"><div class="kv-label">${label}</div><div class="kv-value">${val}${extra || ''}</div></div></div>`
  }

  containerEl.innerHTML = `
    <div class="specimen vol-${sp.volume}">
      <!-- Hero -->
      <header class="specimen__hero">
        <div class="specimen__meta">
          <span class="specimen__index">#${sp.species_index || ''}</span>
          <span class="specimen__vol">Tập ${sp.volume || ''}</span>
        </div>
        <h1 class="specimen__name">${sp.vn_name}</h1>
        <p class="specimen__sci">${sp.scientific_name} <span class="specimen__author">${cleanAuthor}</span></p>
        ${buildWormsBadge(sp)}
      </header>

      <!-- Taxonomy breadcrumb -->
      <nav class="specimen__taxonomy" aria-label="Phân loại học">
        ${taxCrumbs}
      </nav>

      <!-- Section: Thông số chính -->
      <section class="specimen__section">
        <h2 class="specimen__section-title">Thông số chính</h2>
        ${kv('Tên gọi khác', sp.vn_alternate_names, 'Common Name', sp.en_common_name)}
        ${kv('Kích thước', sp.vn_size, 'Size', sp.en_size)}
        ${kv('Phân bố', sp.vn_distribution, 'Distribution', sp.en_distribution)}
      </section>

      <!-- Section: Mẫu vật & Tình trạng -->
      <section class="specimen__section">
        <h2 class="specimen__section-title">Mẫu vật & Tình trạng</h2>
        ${kv('Nơi lưu trữ mẫu', sp.vn_specimen, 'Specimen', sp.en_specimen)}
        ${kv('Tình trạng', sp.vn_status, 'Status', sp.en_status)}
        ${kv('Tài liệu dẫn', sp.vn_literature, 'Literature', sp.en_literature)}
      </section>

      <!-- Synonyms -->
      ${synsHtml}

      <!-- Biology -->
      ${buildBiologyPanel(sp.biology)}
    </div>`

  containerEl.style.display = 'block'
  document.title = `${sp.vn_name} — Danh Mục Cá Biển Việt Nam`
}

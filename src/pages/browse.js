/**
 * browse.js — Cây phân loại, dùng Supabase thay taxonomy_tree.json
 * Lớp → Bộ → Họ → Giống → Loài
 */
import { createClient } from '@supabase/supabase-js'
import '../assets/shared.css'
import '../lib/pwa.js'

const db = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

// ── SVG helpers ──────────────────────────────────────────────────
const arrowSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>`

function createNode(title, rankClass, rankName, childrenHTML) {
  return `
    <div class="tree-node" data-search="${title.toLowerCase()}">
      <div class="node-header" onclick="toggleNode(this)">
        <div class="node-toggle">${arrowSvg}</div>
        <span class="rank-badge ${rankClass}">${rankName}</span>
        <span>${title}</span>
      </div>
      <div class="tree-level">${childrenHTML}</div>
    </div>`
}

// toggleNode cần global (gọi từ onclick attribute trong HTML)
window.toggleNode = function (headerEl) {
  headerEl.querySelector('.node-toggle').classList.toggle('expanded')
  headerEl.nextElementSibling.classList.toggle('expanded')
}

// ── Build tree từ flat Supabase rows ─────────────────────────────
function buildTreeHTML(rows) {
  // Group: class → order → family → genus → species[]
  const tree = {}

  rows.forEach(sp => {
    const cl  = sp.tax_class_latin  || 'Unknown'
    const clv = sp.tax_class_vn     || cl
    const or  = sp.tax_order_latin  || 'Unknown'
    const orv = sp.tax_order_vn     || or
    const fa  = sp.tax_family_latin || 'Unknown'
    const fav = sp.tax_family_vn    || fa
    const ge  = sp.tax_genus_latin  || 'Unknown'
    const gev = sp.tax_genus_vn     || ge

    if (!tree[cl]) tree[cl] = { vn: clv, orders: {} }
    const clNode = tree[cl]
    if (!clNode.orders[or]) clNode.orders[or] = { vn: orv, families: {} }
    const orNode = clNode.orders[or]
    if (!orNode.families[fa]) orNode.families[fa] = { vn: fav, genera: {} }
    const faNode = orNode.families[fa]
    if (!faNode.genera[ge]) faNode.genera[ge] = { vn: gev, species: [] }
    faNode.genera[ge].species.push(sp)
  })

  let html = ''
  Object.entries(tree).forEach(([clLatin, clData]) => {
    let classHTML = ''
    Object.entries(clData.orders).forEach(([orLatin, orData]) => {
      let orderHTML = ''
      Object.entries(orData.families).forEach(([faLatin, faData]) => {
        let familyHTML = ''
        Object.entries(faData.genera).forEach(([geLatin, geData]) => {
          const speciesHTML = geData.species.map(sp => `
            <a href="species.html?id=${sp.id}" class="species-item" data-search="${sp.vn_name.toLowerCase()} ${sp.scientific_name.toLowerCase()}">
              <div>
                <span class="sp-name">${sp.vn_name}</span>
                <span class="sp-sci">${sp.scientific_name}</span>
              </div>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--brand-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </a>`).join('')
          const genusTile = geLatin && geLatin !== 'Unknown' ? `${geData.vn} (${geLatin})` : geData.vn
          familyHTML += createNode(genusTile, 'rank-genus', 'Giống', speciesHTML)
        })
        const familyTitle = faLatin && faLatin !== 'Unknown' ? `${faData.vn} (${faLatin})` : faData.vn
        orderHTML += createNode(familyTitle, 'rank-family', 'Họ', familyHTML)
      })
      const orderTitle = orLatin && orLatin !== 'Unknown' ? `${orData.vn} (${orLatin})` : orData.vn
      classHTML += createNode(orderTitle, 'rank-order', 'Bộ', orderHTML)
    })
    const classTitle = clLatin && clLatin !== 'Unknown' ? `${clData.vn} (${clLatin})` : clData.vn
    html += createNode(classTitle, 'rank-class', 'Lớp', classHTML)
  })
  return html
}

// ── Search (filter in-memory sau khi load) ────────────────────────
let allSpecies = []

const searchPanel = document.getElementById('searchResults')
const searchList  = document.getElementById('searchResultsList')
const treeWrap    = document.getElementById('treeContainer')

document.getElementById('treeFilter')?.addEventListener('input', function (e) {
  const query = e.target.value.trim()
  if (!query) {
    searchPanel.classList.remove('active')
    searchPanel.style.display = 'none'
    treeWrap.style.display = ''
    return
  }
  const q    = query.toLowerCase()
  const hits = allSpecies.filter(sp =>
    sp.vn_name.toLowerCase().includes(q) || sp.scientific_name.toLowerCase().includes(q)
  ).slice(0, 60)

  treeWrap.style.display    = 'none'
  searchPanel.style.display = 'block'
  
  // Thêm class active để hiển thị vì CSS mới ẩn opacity 0
  setTimeout(() => searchPanel.classList.add('active'), 10)

  searchList.innerHTML = hits.length === 0
    ? `<p style="color:var(--text-muted);padding:2rem;text-align:center">Không tìm thấy loài nào phù hợp.</p>`
    : hits.map(sp => `
        <a href="species.html?id=${sp.id}" class="species-item">
          <div>
            <span class="sp-name">${sp.vn_name}</span>
            <span class="sp-sci">${sp.scientific_name}</span>
          </div>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--brand-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </a>`).join('')
})

// ── Load & Render ────────────────────────────────────────────────
const COLS = 'id, vn_name, scientific_name, tax_class_vn, tax_class_latin, tax_order_vn, tax_order_latin, tax_family_vn, tax_family_latin, tax_genus_vn, tax_genus_latin, species_index'

async function loadTree() {
  const container = document.getElementById('treeContainer')
  container.innerHTML = '<div style="text-align:center;padding:3rem;color:var(--text-muted)">Đang tải cây phân loại...</div>'

  // ponytail: Supabase server-side max-rows = 1000. Fetch 2 pages to get all ~1200 rows.
  const [r1, r2] = await Promise.all([
    db.from('species').select(COLS).range(0, 999),
    db.from('species').select(COLS).range(1000, 1999),
  ])

  if (r1.error) {
    container.innerHTML = `<div style="text-align:center;padding:3rem;color:#f87171">Lỗi tải dữ liệu: ${r1.error.message}</div>`
    return
  }

  const data = [...(r1.data || []), ...(r2.data || [])]

  // Sort client-side: lớp → bộ → họ → số thứ tự
  data.sort((a, b) => {
    const cl = (a.tax_class_latin || '').localeCompare(b.tax_class_latin || '')
    if (cl !== 0) return cl
    const or = (a.tax_order_latin || '').localeCompare(b.tax_order_latin || '')
    if (or !== 0) return or
    const fa = (a.tax_family_latin || '').localeCompare(b.tax_family_latin || '')
    if (fa !== 0) return fa
    return (a.species_index || 0) - (b.species_index || 0)
  })

  allSpecies = data
  container.innerHTML = buildTreeHTML(data)
}

loadTree()


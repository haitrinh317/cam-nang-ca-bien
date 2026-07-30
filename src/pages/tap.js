/**
 * tap.js — Duyệt loài theo Tập, dùng Supabase thay fetch species.json
 */
import { createClient } from '@supabase/supabase-js'
import '../assets/shared.css'

const db = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

// Đọc vol từ URL param, fallback tab đang active
const urlParams  = new URLSearchParams(window.location.search)
let currentVol   = parseInt(urlParams.get('vol')) || 4

// Set active tab theo URL
document.querySelectorAll('.vol-tab').forEach(t => t.classList.remove('active'))
const activeTab = document.querySelector(`.vol-tab[data-vol="${currentVol}"]`)
if (activeTab) activeTab.classList.add('active')

// Tab click
document.querySelectorAll('.vol-tab').forEach(tab => {
  tab.addEventListener('click', function () {
    document.querySelectorAll('.vol-tab').forEach(t => t.classList.remove('active'))
    this.classList.add('active')
    currentVol = parseInt(this.getAttribute('data-vol'))
    document.getElementById('localFilter').value = ''

    const url = new URL(window.location)
    url.searchParams.set('vol', currentVol)
    window.history.pushState({}, '', url)

    renderGrid(currentVol)
  })
})

// Local filter (client-side, đã load)
document.getElementById('localFilter')?.addEventListener('input', function (e) {
  const q = e.target.value.toLowerCase().trim()
  document.querySelectorAll('.species-card-mini').forEach(card => {
    card.style.display = card.innerText.toLowerCase().includes(q) ? 'flex' : 'none'
  })
})

async function renderGrid(vol) {
  const container = document.getElementById('gridContainer')
  container.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:3rem;color:var(--text-muted)">Đang tải...</div>'

  const { data, error } = await db
    .from('species')
    .select('id, volume, species_index, vn_name, scientific_name, tax_order_vn, tax_family_vn')
    .eq('volume', vol)
    .order('species_index')
    .limit(700) // ponytail: Tập lớn nhất ~518 loài

  if (error || !data) {
    container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:3rem;color:#f87171">Lỗi tải dữ liệu. Thử lại sau.</div>`
    return
  }

  if (data.length === 0) {
    container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:3rem;color:var(--text-muted)">Tập ${vol} chưa có dữ liệu hoặc đang được trích xuất.</div>`
    return
  }

  container.innerHTML = data.map(sp => `
    <a href="species.html?id=${sp.id}" class="species-card-mini">
      <div class="scm-id">#${sp.species_index}</div>
      <div class="scm-name">${sp.vn_name}</div>
      <div class="scm-sci">${sp.scientific_name}</div>
      <div class="scm-tax">${sp.tax_order_vn || ''}${sp.tax_family_vn ? ' → ' + sp.tax_family_vn : ''}</div>
    </a>`).join('')
}

// Render lần đầu
renderGrid(currentVol)

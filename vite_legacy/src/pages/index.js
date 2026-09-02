/**
 * index.js — Trang chủ: Search Supabase thay Fuse.js
 */
import { createClient } from '@supabase/supabase-js'
import '../assets/shared.css'
import '../lib/pwa.js'

const db = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

const searchInput  = document.getElementById('globalSearch')
const searchResults = document.getElementById('searchResults')

let debounceTimer = null

searchInput?.addEventListener('input', function () {
  clearTimeout(debounceTimer)
  const query = this.value.trim()

  if (query.length < 2) {
    searchResults.classList.remove('active')
    return
  }

  searchResults.innerHTML = '<div style="padding:1.5rem;text-align:center;color:var(--text-muted)">Đang tìm kiếm...</div>'
  searchResults.classList.add('active')

  debounceTimer = setTimeout(() => doSearch(query), 280)
})

async function doSearch(query) {
  // Search theo vn_name HOẶC scientific_name (ilike = case-insensitive LIKE)
  const { data, error } = await db
    .from('species')
    .select('id, volume, vn_name, scientific_name, authorship')
    .or(`vn_name.ilike.%${query}%,scientific_name.ilike.%${query}%,en_common_name.ilike.%${query}%`)
    .order('volume')
    .limit(12)

  if (error) {
    searchResults.innerHTML = '<div style="padding:1.5rem;text-align:center;color:#f87171">Lỗi kết nối. Thử lại sau.</div>'
    return
  }

  if (!data || data.length === 0) {
    searchResults.innerHTML = '<div style="padding:1.5rem;text-align:center;color:var(--text-muted)">Không tìm thấy loài cá nào phù hợp.</div>'
    return
  }

  searchResults.innerHTML = data.map(item => `
    <a href="species.html?id=${item.id}" class="result-item">
      <div>
        <div class="ri-name">${item.vn_name}</div>
        <div class="ri-sci">${item.scientific_name} ${item.authorship || ''}</div>
      </div>
      <span class="vol-badge v${item.volume}">Tập ${item.volume}</span>
    </a>`).join('')
}

document.addEventListener('click', e => {
  if (!e.target.closest('.search-wrapper')) {
    searchResults?.classList.remove('active')
  }
})

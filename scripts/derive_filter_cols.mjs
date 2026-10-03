// Điền cột lọc nâng cao (migration 013) từ biology.* gốc. Mặc định DRY-RUN.
//   node --env-file=.env.local scripts/derive_filter_cols.mjs           # chỉ thống kê
//   node --env-file=.env.local scripts/derive_filter_cols.mjs --apply   # ghi thật (cần migration 013 trước)
// Quy tắc cố định, KHÔNG dùng AI đoán. Giá trị không parse được -> NULL (và được báo cáo).
import assert from 'node:assert/strict'

const IUCN = new Set(['LC', 'NT', 'VU', 'EN', 'CR', 'EW', 'EX', 'DD', 'NE'])

export function parseIucn(s) {
  const c = String(s ?? '').trim().toUpperCase()
  return IUCN.has(c) ? c : null
}

// "0 - 45 m" | "0 – 200 m (Epipelagic)" | "đến 30 m" | "lên đến 30 m" | "12 m" | "? - 9 m" | "None - 9 m"
export function parseDepth(s) {
  const t = String(s ?? '').trim().toLowerCase()
  if (!t) return null
  let m = t.match(/^(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)\s*m\b/)
  if (m) return { min: num(m[1]), max: num(m[2]) }
  m = t.match(/^(?:\?|none)\s*[-–]\s*(\d+(?:[.,]\d+)?)\s*m\b/)
  if (m) return { min: null, max: num(m[1]) }
  m = t.match(/^(?:lên\s+)?đến\s+(\d+(?:[.,]\d+)?)\s*m\b/)
  if (m) return { min: null, max: num(m[1]) }
  m = t.match(/^(\d+(?:[.,]\d+)?)\s*m\b/)
  if (m) return { min: num(m[1]), max: num(m[1]) }
  return null
}

// "30.0 cm TL" | "F: 12-18 mm, M: 10 mm" | "30" (không đơn vị -> null) | "... up to 9 m" (null)
export function parseLengthCm(s) {
  const t = String(s ?? '').trim().toLowerCase()
  if (!t || /\btentacles?\b/.test(t)) return null
  const unit = t.match(/\b(mm|cm)\b/)
  if (!unit) return null
  const nums = [...t.matchAll(/(\d+(?:[.,]\d+)?)/g)].map(x => num(x[1]))
  if (!nums.length) return null
  const max = Math.max(...nums)
  return unit[1] === 'mm' ? Math.round(max) / 10 : max
}


// ── Môi trường sống (đợt 2): 7 nhãn, nhiều nhãn/loài. Quy tắc từ khóa trên habitat + habitatVn. ──
// Không ánh xạ: benthic / demersal / neritic / marine (mô tả tầng nước, không phải loại môi trường) -> loài chỉ có
// các từ này sẽ KHÔNG có nhãn (bị ẩn khi lọc môi trường; UI ghi chú rõ).
const L = '[^\\p{L}]' // ranh giới từ cho tiếng Việt có dấu (\b của JS chỉ hiểu ASCII)
const w = (s) => `(?:^|${L})(?:${s})(?:${L}|$)`
export const HABITAT_RULES = {
  'ran-san-ho': new RegExp(`coral reef|reef|rạn`, 'iu'),
  'day-cat-bun': new RegExp(`soft bottom|\\bmud|\\bsand|bùn|cát|đáy mềm`, 'iu'),
  'day-da': new RegExp(`rocky|\\brocks?\\b|rubble|boulder|hard substrate|hard bottom|${w('đá')}|đáy cứng|nền đáy cứng|hang hốc`, 'iu'),
  'tham-co-bien': new RegExp(`seagrass|sea grass|seaweed|algae|algal|kelp|cỏ biển|${w('rong')}`, 'iu'),
  'ngap-man-cua-song': new RegExp(`mangrove|estuar|brackish|river mouth|ngập mặn|cửa sông|nước lợ`, 'iu'),
  'bien-khoi': new RegExp(`(?<!meso|bathy|bentho)pelagic|oceanic|tầng mặt|biển khơi`, 'iu'),
  'bien-sau': new RegExp(`bathy|mesopelagic|abyss|\\bdeep|tầng sâu|tầng giữa|biển sâu`, 'iu'),
}
export function parseHabitat(biology) {
  const t = `${biology?.habitat ?? ''} ; ${biology?.habitatVn ?? ''}`
  return Object.entries(HABITAT_RULES).filter(([, re]) => re.test(t)).map(([k]) => k)
}

// ── Vùng biển (đợt 3): 7 vùng theo địa danh trong vn_distribution. ──
// KHÔNG dùng vn_specimen: cột đó ghi nơi LƯU TRỮ mẫu (viện ở Nha Trang/Hải Phòng...), không phải nơi loài phân bố
// (đã đo: dùng nó làm "Nha Trang" khớp 1389 loài — sai).
// Bảng địa danh -> vùng DO CHÚ DUYỆT (5 vùng; sách thường chỉ ghi "miền Trung"/"Nam Bộ" nên không tách được
// Bắc/Nam Trung Bộ hay Đông/Tây Nam Bộ — gộp để mọi loài lọc đúng). Địa danh không có trong bảng thì KHÔNG đoán.
// "Biển Đông" chung chung không gán vùng nào.
export const REGION_KEYWORDS = {
  'bac-bo': ['vinh bac bo', 'bac bo', 'mien bac', 'hai phong', 'quang ninh', 'ha long', 'cat ba', 'bach long vi', 'co to', 'do son', 'mong cai', 'van don'],
  'trung-bo': ['trung bo', 'mien trung', 'thanh hoa', 'nghe an', 'cua lo', 'ha tinh', 'quang binh', 'quang tri', 'con co', 'thua thien', 'hue', 'lang co',
    'da nang', 'quang nam', 'hoi an', 'cu lao cham', 'quang ngai', 'ly son', 'binh dinh', 'quy nhon', 'phu yen', 'khanh hoa', 'nha trang', 'cam ranh', 'van phong', 'ninh thuan', 'phan rang', 'binh thuan', 'phan thiet', 'phu quy', 'mui ne'],
  'nam-bo': ['nam bo', 'mien nam', 'vung tau', 'ba ria', 'con dao', 'can gio', 'ho chi minh', 'sai gon', 'dong nai',
    'ca mau', 'kien giang', 'phu quoc', 'tho chu', 'nam du', 'ha tien', 'bac lieu', 'soc trang', 'tra vinh', 'ben tre', 'tien giang', 'rach gia', 'hon chong'],
  'hoang-sa': ['hoang sa', 'paracel'],
  'truong-sa': ['truong sa', 'spratly', 'nam yet', 'song tu tay', 'sinh ton', 'an bang'],
}
export const fold = (s) => String(s ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi, 'd').toLowerCase()
const wordRe = (k) => new RegExp(`(?<![a-z0-9])${k}(?![a-z0-9])`)
const REGION_RES = Object.fromEntries(Object.entries(REGION_KEYWORDS).map(([r, ks]) => [r, ks.map(wordRe)]))
export function parseRegions(row) {
  const t = fold(row.vn_distribution)
  return Object.entries(REGION_RES).filter(([, res]) => res.some(re => re.test(t))).map(([r]) => r)
}

const num = x => Number(String(x).replace(',', '.'))

// ── Self-check: fail ngay nếu quy tắc parse bị hỏng ──
assert.equal(parseIucn(' vu '), 'VU'); assert.equal(parseIucn('common'), null)
assert.deepEqual(parseDepth('0 - 45 m'), { min: 0, max: 45 })
assert.deepEqual(parseDepth('0 – 200 m (Epipelagic)'), { min: 0, max: 200 })
assert.deepEqual(parseDepth('lên đến 30 m'), { min: null, max: 30 })
assert.deepEqual(parseDepth('đến 5 m'), { min: null, max: 5 })
assert.deepEqual(parseDepth('? - 9 m'), { min: null, max: 9 })
assert.deepEqual(parseDepth('7 m'), { min: 7, max: 7 })
assert.equal(parseDepth('Surface (pelagic)'), null)
assert.deepEqual(parseHabitat({ habitat: 'reef-associated, Rạn san hô' }), ['ran-san-ho'])
assert.deepEqual(parseHabitat({ habitat: 'benthic, soft bottom, mud' }), ['day-cat-bun'])
assert.deepEqual(parseHabitat({ habitat: 'mangroves, estuaries' }), ['ngap-man-cua-song'])
assert.deepEqual(parseHabitat({ habitat: 'benthic' }), [])
assert.deepEqual(parseHabitat({ habitatVn: 'tầng sâu hải dương (bathypelagic' }), ['bien-sau'])
assert.deepEqual(parseHabitat({ habitatVn: 'tầng mặt hải dương (epipelagic' }), ['bien-khoi'])
assert.deepEqual(parseHabitat({ habitat: 'benthopelagic' }), [])
assert.ok(!parseHabitat({ habitatVn: 'sống trong hang đáy' }).includes('tham-co-bien'), '"trong" không được khớp "rong"')
assert.ok(!parseHabitat({ habitatVn: 'tầng đáy' }).includes('day-da'), '"đáy" không được khớp "đá"')
assert.deepEqual(parseRegions({ vn_distribution: 'Trung Quốc, Việt Nam. Vịnh Bắc Bộ.' }), ['bac-bo'])
assert.deepEqual(parseRegions({ vn_distribution: 'Vịnh Bắc Bộ, Trung Bộ.' }).sort(), ['bac-bo', 'trung-bo'])
assert.deepEqual(parseRegions({ vn_distribution: 'Nơi phát hiện mẫu vật: Lý Sơn, Vịnh Nha Trang, Nam Yết, Thổ Chu' }).sort(), ['nam-bo', 'trung-bo', 'truong-sa'])
assert.deepEqual(parseRegions({ vn_specimen: 'Mẫu lưu trữ: Viện Hải dương học, Nha Trang' }), [], 'vn_specimen không được dùng')
assert.deepEqual(parseRegions({ vn_distribution: 'Biển Đông. Nam Trung Bộ' }), ['trung-bo'])
assert.deepEqual(parseRegions({ vn_distribution: 'Đông Nam Bộ' }), ['nam-bo'])
assert.deepEqual(parseRegions({ vn_distribution: 'Biển Đông, Ấn Độ Dương' }), [])
assert.equal(parseLengthCm('30.0 cm TL'), 30)
assert.equal(parseLengthCm('F: 12-18 mm, M: 10 mm'), 1.8)
assert.equal(parseLengthCm('41'), null)
assert.equal(parseLengthCm('9 cm float, tentacles up to 9 m'), null)

if (process.argv[1]?.endsWith('derive_filter_cols.mjs')) await main()

async function main() {
  const apply = process.argv.includes('--apply')
  const withTags = process.argv.includes('--tags') // ghi habitat_tags/region_tags (cần migration 015)
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL, key = process.env.SUPABASE_SERVICE_ROLE_KEY
  const H = { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' }
  const cols = 'id,collection_id,biology,vn_distribution,vn_specimen' + (apply ? ',iucn_code,depth_min,depth_max,max_length_cm' : '') + (apply && withTags ? ',habitat_tags,region_tags' : '')
  const rows = []
  for (let o = 0; ; o += 1000) {
    const r = await fetch(`${url}/rest/v1/species?select=${cols}&deleted_at=is.null&order=id&offset=${o}&limit=1000`, { headers: H })
    const b = await r.json()
    if (!Array.isArray(b)) throw new Error(`Fetch lỗi (đã chạy migration 013 chưa?): ${JSON.stringify(b)}`)
    rows.push(...b); if (b.length < 1000) break
  }

  const tagStat = { hab: new Map(), reg: new Map(), habAny: 0, regAny: 0, habSrc: 0, regSrc: 0, regMiss: [] }
  const stat = { iucn: 0, depth: 0, len: 0, iucnBad: new Map(), depthBad: new Map(), lenBad: new Map() }
  const patches = []
  const bump = (m, v) => m.set(String(v).slice(0, 50), (m.get(String(v).slice(0, 50)) || 0) + 1)
  for (const r of rows) {
    const b = r.biology || {}
    const iucn = parseIucn(b.iucnStatus)
    const d = parseDepth(b.depth)
    const len = parseLengthCm(b.maxLength)
    if (iucn) stat.iucn++; else if (b.iucnStatus) bump(stat.iucnBad, b.iucnStatus)
    if (d) stat.depth++; else if (b.depth) bump(stat.depthBad, b.depth)
    if (len != null) stat.len++; else if (b.maxLength) bump(stat.lenBad, b.maxLength)
    const hab = parseHabitat(b), reg = parseRegions(r)
    if (b.habitat || b.habitatVn) { tagStat.habSrc++; if (hab.length) tagStat.habAny++ }
    if (r.vn_distribution) { tagStat.regSrc++; if (reg.length) tagStat.regAny++; else if (tagStat.regMiss.length < 12 && r.vn_distribution) tagStat.regMiss.push(r.vn_distribution.slice(0, 110)) }
    for (const h of hab) tagStat.hab.set(h, (tagStat.hab.get(h) || 0) + 1)
    for (const g of reg) tagStat.reg.set(g, (tagStat.reg.get(g) || 0) + 1)
    const next = { iucn_code: iucn, depth_min: d?.min ?? null, depth_max: d?.max ?? null, max_length_cm: len, ...(withTags ? { habitat_tags: hab, region_tags: reg } : {}) }
    if (apply && Object.keys(next).some(k => (Array.isArray(next[k]) ? JSON.stringify([...(r[k] ?? [])].sort()) !== JSON.stringify([...next[k]].sort()) : (r[k] == null ? null : Number.isNaN(Number(r[k])) ? r[k] : Number(r[k])) !== next[k]))) {
      patches.push({ id: r.id, ...next })
    }
  }

  const fmt = m => [...m].sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k, c]) => `${k} (${c})`).join(' | ') || '(không có)'
  console.log(`${apply ? 'APPLY' : 'DRY-RUN'} — ${rows.length} loài`)
  console.log(`iucn_code     : ${stat.iucn}  | bỏ qua: ${fmt(stat.iucnBad)}`)
  console.log(`depth min/max : ${stat.depth}  | bỏ qua: ${fmt(stat.depthBad)}`)
  console.log(`max_length_cm : ${stat.len}  | bỏ qua: ${fmt(stat.lenBad)}`)
  const fmtT = m => [...m].sort((a, b) => b[1] - a[1]).map(([k, c]) => `${k}: ${c}`).join(' | ') || '(không có)'
  console.log(`\nmôi trường : ${tagStat.habAny}/${tagStat.habSrc} loài có dữ liệu gốc được gán ≥1 nhãn\n  ${fmtT(tagStat.hab)}`)
  console.log(`vùng biển  : ${tagStat.regAny}/${tagStat.regSrc} loài có dữ liệu gốc được gán ≥1 vùng\n  ${fmtT(tagStat.reg)}`)
  console.log('  mẫu phân bố KHÔNG gán được vùng (kiểm tra bảng địa danh):\n   - ' + tagStat.regMiss.join('\n   - '))
  if (!apply) return console.log('\nChưa ghi gì. Thêm --apply sau khi áp migration 013.')

  console.log(`\nCần cập nhật: ${patches.length} dòng`)
  let done = 0
  for (let i = 0; i < patches.length; i += 10) {
    await Promise.all(patches.slice(i, i + 10).map(async ({ id, ...body }) => {
      const r = await fetch(`${url}/rest/v1/species?id=eq.${encodeURIComponent(id)}`, { method: 'PATCH', headers: H, body: JSON.stringify(body) })
      if (!r.ok) throw new Error(`PATCH ${id} lỗi ${r.status}: ${await r.text()}`)
      done++
    }))
  }
  console.log(`Đã ghi ${done}/${patches.length} dòng.`)
}

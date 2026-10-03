// Smoke check for migration 012 (run AFTER applying it in Supabase SQL Editor):
//   node scripts/check_search_rpc.mjs
import { readFileSync } from 'node:fs'
import assert from 'node:assert/strict'
import { createClient } from '@supabase/supabase-js'

const env = Object.fromEntries(
  readFileSync('.env.local', 'utf8').split('\n').filter(l => l.includes('=') && !l.startsWith('#'))
    .map(l => [l.slice(0, l.indexOf('=')), l.slice(l.indexOf('=') + 1).replace(/^["']|["']$/g, '')]),
)
const db = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
const run = async (q, c = null) => {
  const { data, error } = await db.rpc('search_species', { p_query: q, p_collection: c, p_limit: 5, p_offset: 0 })
  assert.ifError(error)
  return data
}

for (const [plain, accented] of [['ca map', 'cá mập'], ['ca thu', 'cá thu'], ['ca chinh', 'cá chình']]) {
  const a = await run(plain), b = await run(accented)
  assert.ok(a.length > 0, `"${plain}" returned nothing`)
  assert.equal(a[0].total, b[0].total, `"${plain}" vs "${accented}" differ`)
}
assert.ok((await run('shark')).length > 0, 'English name search failed')
assert.ok((await run('ca map', 'ca-bien')).every(r => r.collection_id === 'ca-bien'), 'collection scope broken')
const { data: counts, error } = await db.rpc('search_species_counts', { p_query: 'ca map' })
assert.ifError(error)
assert.ok(counts.length > 0)
// ── Migration 014: bộ lọc nâng cao (bỏ qua nếu chưa áp 014) ──
const f = async (args) => (await db.rpc('search_species', { p_limit: 50, ...args }))
const probe = await f({ p_iucn: ['CR'] })
if (probe.error) {
  console.log('SKIP filters — chưa áp migration 014:', probe.error.message)
} else {
  assert.ok(probe.data.length > 0, 'filter CR returned nothing')
  const ids = probe.data.map(r => r.id)
  const { data: rows } = await db.from('species').select('id,iucn_code').in('id', ids)
  assert.ok(rows.every(r => r.iucn_code === 'CR'), 'IUCN filter leaked non-CR rows')
  const deep = await f({ p_depth_min: 200, p_depth_max: 1000 })
  assert.ok(deep.data.length > 0, 'depth filter returned nothing')
  const { data: d } = await db.from('species').select('id,depth_min,depth_max').in('id', deep.data.map(r => r.id))
  assert.ok(d.every(r => r.depth_max >= 200 && (r.depth_min ?? 0) <= 1000), 'depth filter leaked rows outside range')
  const big = await f({ p_len_min: 100, p_len_max: 500 })
  const { data: l } = await db.from('species').select('id,max_length_cm').in('id', big.data.map(r => r.id))
  assert.ok(l.length > 0 && l.every(r => r.max_length_cm >= 100 && r.max_length_cm <= 500), 'length filter leaked rows')
  console.log('OK — filter RPC (014) passes')
}
// ── Migration 015: môi trường sống + vùng biển + facets (bỏ qua nếu chưa áp 015) ──
const p15 = await f({ p_region: ['hoang-sa'] })
if (p15.error) {
  console.log('SKIP habitat/region — chưa áp migration 015:', p15.error.message)
} else if (p15.data.length === 0) {
  console.log('SKIP habitat/region — đã áp 015 nhưng chưa chạy: node --env-file=.env.local scripts/derive_filter_cols.mjs --apply --tags')
} else {
  const { data: hs } = await db.from('species').select('id,region_tags').in('id', p15.data.map(r => r.id))
  assert.ok(hs.every(r => r.region_tags.includes('hoang-sa')), 'region filter leaked rows')
  const hab = await f({ p_habitat: ['ran-san-ho'] })
  const { data: hb } = await db.from('species').select('id,habitat_tags').in('id', hab.data.map(r => r.id))
  assert.ok(hb.length > 0 && hb.every(r => r.habitat_tags.includes('ran-san-ho')), 'habitat filter leaked rows')
  const { data: fx, error: e3 } = await db.rpc('search_species_facets', { p_query: 'ca map' })
  assert.ifError(e3)
  for (const k of ['iucn', 'habitat', 'region']) assert.ok(fx.some(r => r.facet === k), `facet ${k} missing`)
  console.log('OK — habitat/region/facets RPC (015) passes')
}
console.log('OK — search_species RPC passes all checks')

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
console.log('OK — search_species RPC passes all checks')

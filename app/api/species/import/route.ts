/**
 * API: /api/species/import
 * POST — Bulk upsert species from JSON array
 * Body: { species: [...], collection_id: string }
 */
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase-server'

const MAX_BATCH = 200

export async function POST(req: NextRequest) {
  const db = createServerClient()

  // Auth check
  const { data: { user } } = await db.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const body = await req.json()
  const { species, collection_id } = body

  if (!Array.isArray(species) || species.length === 0) {
    return NextResponse.json({ error: 'species array is required and must not be empty' }, { status: 400 })
  }
  if (!collection_id) {
    return NextResponse.json({ error: 'collection_id is required' }, { status: 400 })
  }
  if (species.length > MAX_BATCH) {
    return NextResponse.json({ error: `Max ${MAX_BATCH} species per import` }, { status: 400 })
  }

  // Ensure collection_id on every row
  const rows = species.map((sp: Record<string, unknown>) => ({
    ...sp,
    collection_id,
  }))

  const { data, error, count } = await db
    .from('species')
    .upsert(rows, { onConflict: 'id' })
    .select('id')

  if (error) return NextResponse.json({ error: error.message }, { status: 400 })

  // Audit log
  await db.from('audit_log').insert({
    user_email: user.email,
    action: 'bulk_import',
    collection_id,
    details: `Imported ${data?.length ?? 0} species`,
  }).then(() => {}) // fire-and-forget

  return NextResponse.json({
    success: true,
    imported: data?.length ?? 0,
    message: `Đã import ${data?.length ?? 0} loài thành công.`,
  }, { status: 200 })
}

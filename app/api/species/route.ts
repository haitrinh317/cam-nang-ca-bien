/**
 * API: /api/species
 * GET  ?collection=ca-bien&vol=1&search=...&page=1  → paginated list
 * POST → create new species
 * PATCH ?id=xxx → update species
 * DELETE ?id=xxx → delete species
 */
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase-server'

const PAGE_SIZE = 20

async function auditLog(db: ReturnType<typeof createServerClient>, action: string, opts: {
  collection_id?: string; species_id?: string; details?: string
  old_data?: unknown; new_data?: unknown
}) {
  const { data: { user } } = await db.auth.getUser()
  await db.from('audit_log').insert({
    user_email: user?.email || 'anonymous',
    action,
    collection_id: opts.collection_id || null,
    species_id: opts.species_id || null,
    details: opts.details || null,
    old_data: opts.old_data || null,
    new_data: opts.new_data || null,
  })
}

export async function GET(req: NextRequest) {
  const db = createServerClient()
  const { searchParams } = req.nextUrl
  const collection = searchParams.get('collection') || 'ca-bien'
  const vol        = searchParams.get('vol')
  const search     = searchParams.get('search') || ''
  const page       = parseInt(searchParams.get('page') || '1')

  let query = db
    .from('species')
    .select('id, volume, species_index, vn_name, scientific_name, tax_family_latin, collection_id', { count: 'exact' })
    .eq('collection_id', collection)

  if (vol) query = query.eq('volume', parseInt(vol))
  if (search) query = query.or(`vn_name.ilike.%${search}%,scientific_name.ilike.%${search}%`)

  const from = (page - 1) * PAGE_SIZE
  query = query.range(from, from + PAGE_SIZE - 1).order('volume').order('species_index')

  const { data, error, count } = await query
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json({ data, total: count, page, pageSize: PAGE_SIZE })
}

export async function POST(req: NextRequest) {
  const db = createServerClient()
  const body = await req.json()
  const { data, error } = await db.from('species').insert(body).select().single()
  if (error) return NextResponse.json({ error: error.message }, { status: 400 })

  auditLog(db, 'create', {
    collection_id: body.collection_id,
    species_id: data.id,
    details: `Thêm loài: ${data.vn_name} (${data.scientific_name})`,
    new_data: data,
  })

  return NextResponse.json({ data }, { status: 201 })
}

export async function PATCH(req: NextRequest) {
  const db = createServerClient()
  const id = req.nextUrl.searchParams.get('id')
  if (!id) return NextResponse.json({ error: 'id required' }, { status: 400 })

  // Get old data for audit
  const { data: old } = await db.from('species').select('*').eq('id', id).single()

  const body = await req.json()
  const { data, error } = await db.from('species').update(body).eq('id', id).select().single()
  if (error) return NextResponse.json({ error: error.message }, { status: 400 })

  auditLog(db, 'update', {
    collection_id: data.collection_id,
    species_id: id,
    details: `Cập nhật: ${data.vn_name} (${data.scientific_name})`,
    old_data: old,
    new_data: data,
  })

  return NextResponse.json({ data })
}

export async function DELETE(req: NextRequest) {
  const db = createServerClient()
  const id = req.nextUrl.searchParams.get('id')
  if (!id) return NextResponse.json({ error: 'id required' }, { status: 400 })

  // Get old data for audit
  const { data: old } = await db.from('species').select('vn_name, scientific_name, collection_id').eq('id', id).single()

  const { error } = await db.from('species').delete().eq('id', id)
  if (error) return NextResponse.json({ error: error.message }, { status: 400 })

  auditLog(db, 'delete', {
    collection_id: old?.collection_id,
    species_id: id,
    details: `Xóa: ${old?.vn_name || id} (${old?.scientific_name || ''})`,
    old_data: old,
  })

  return NextResponse.json({ success: true })
}

/**
 * API: /api/species
 * GET  ?collection=ca-bien&vol=1&search=...&page=1  → paginated list
 * POST → create new species (admin only)
 * PATCH ?id=xxx → update species (admin only)
 * DELETE ?id=xxx → delete species (admin only)
 */
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient, createSSRClient } from '@/lib/supabase-server'
import { sanitizeSearch, SPECIES_PAGE_SIZE, applySpeciesFilters } from '@/lib/species-query'

export const dynamic = 'force-dynamic'

/** Check if current user has admin role. Returns user email or null. */
async function requireAdmin(db: Awaited<ReturnType<typeof createSSRClient>>): Promise<{ email: string } | null> {
  const { data: { user } } = await db.auth.getUser()
  if (!user?.email) return null

  // Use service client to bypass broken RLS on user_roles
  const adminDb = createServerClient()
  const { data: role } = await adminDb
    .from('user_roles')
    .select('role')
    .eq('user_id', user.id)
    .single()

  if (role?.role !== 'admin') return null
  return { email: user.email }
}

async function auditLog(db: Awaited<ReturnType<typeof createSSRClient>>, action: string, userEmail: string, opts: {
  collection_id?: string; species_id?: string; details?: string
  old_data?: unknown; new_data?: unknown
}) {
  await db.from('audit_log').insert({
    user_email: userEmail,
    action,
    collection_id: opts.collection_id || null,
    species_id: opts.species_id || null,
    details: opts.details || null,
    old_data: opts.old_data || null,
    new_data: opts.new_data || null,
  })
}

export async function GET(req: NextRequest) {
  // GET is public, doesn't need cookies
  const db = createServerClient()
  const { searchParams } = req.nextUrl
  const collection      = searchParams.get('collection') || 'ca-bien'
  const vol             = searchParams.get('vol')
  const search          = sanitizeSearch(searchParams.get('search') || '')
  const page            = parseInt(searchParams.get('page') || '1')
  const includeDeleted  = searchParams.get('include_deleted') === 'true'

  let query = applySpeciesFilters(
    db.from('species').select('id, volume, species_index, vn_name, scientific_name, tax_family_latin, collection_id', { count: 'exact' }),
    collection,
    includeDeleted
  )

  if (vol) query = query.eq('volume', parseInt(vol))
  if (search) query = query.or(`vn_name.ilike.%${search}%,scientific_name.ilike.%${search}%`)

  const from = (page - 1) * SPECIES_PAGE_SIZE
  query = query.range(from, from + SPECIES_PAGE_SIZE - 1).order('volume').order('species_index')

  const { data, error, count } = await query
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json({ data, total: count, page, pageSize: SPECIES_PAGE_SIZE })
}

export async function POST(req: NextRequest) {
  const db = await createSSRClient()
  const admin = await requireAdmin(db)
  if (!admin) return NextResponse.json({ error: 'Forbidden: admin role required' }, { status: 403 })

  const body = await req.json()
  const { data, error } = await db.from('species').insert(body).select().single()
  if (error) return NextResponse.json({ error: error.message }, { status: 400 })

  await auditLog(db, 'create', admin.email, {
    collection_id: body.collection_id,
    species_id: data.id,
    details: `Thêm loài: ${data.vn_name} (${data.scientific_name})`,
    new_data: data,
  })

  return NextResponse.json({ data }, { status: 201 })
}

export async function PATCH(req: NextRequest) {
  const db = await createSSRClient()
  const admin = await requireAdmin(db)
  if (!admin) return NextResponse.json({ error: 'Forbidden: admin role required' }, { status: 403 })

  const id = req.nextUrl.searchParams.get('id')
  if (!id) return NextResponse.json({ error: 'id required' }, { status: 400 })

  const { data: old } = await db.from('species').select('*').eq('id', id).single()

  const body = await req.json()
  const { data, error } = await db.from('species').update(body).eq('id', id).select().single()
  if (error) return NextResponse.json({ error: error.message }, { status: 400 })

  await auditLog(db, 'update', admin.email, {
    collection_id: data.collection_id,
    species_id: id,
    details: `Cập nhật: ${data.vn_name} (${data.scientific_name})`,
    old_data: old,
    new_data: data,
  })

  return NextResponse.json({ data })
}

export async function DELETE(req: NextRequest) {
  const db = await createSSRClient()
  const admin = await requireAdmin(db)
  if (!admin) return NextResponse.json({ error: 'Forbidden: admin role required' }, { status: 403 })

  const id   = req.nextUrl.searchParams.get('id')
  const hard = req.nextUrl.searchParams.get('hard') === 'true'
  if (!id) return NextResponse.json({ error: 'id required' }, { status: 400 })

  const { data: old } = await db
    .from('species')
    .select('vn_name, scientific_name, collection_id')
    .eq('id', id)
    .single()

  let error: unknown
  if (hard) {
    // Hard delete — permanent, no recovery
    ;({ error } = await db.from('species').delete().eq('id', id))
  } else {
    // Soft delete — set deleted_at, record preserved in DB
    ;({ error } = await db
      .from('species')
      .update({ deleted_at: new Date().toISOString() })
      .eq('id', id))
  }

  if (error) return NextResponse.json({ error: (error as Error).message }, { status: 400 })

  await auditLog(db, hard ? 'hard_delete' : 'soft_delete', admin.email, {
    collection_id: old?.collection_id,
    species_id: id,
    details: `${hard ? 'Xóa vĩnh viễn' : 'Xóa mềm'}: ${old?.vn_name || id} (${old?.scientific_name || ''})`,
    old_data: old,
  })

  return NextResponse.json({ success: true, mode: hard ? 'hard' : 'soft' })
}

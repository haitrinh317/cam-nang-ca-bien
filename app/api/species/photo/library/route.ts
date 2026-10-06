import { NextRequest, NextResponse } from 'next/server'
import { createServerClient, createSSRClient } from '@/lib/supabase-server'

async function requireAdmin(db: Awaited<ReturnType<typeof createSSRClient>>) {
  const { data: { user } } = await db.auth.getUser()
  if (!user?.email) return null
  const adminDb = createServerClient()
  const { data: role } = await adminDb.from('user_roles').select('role').eq('user_id', user.id).single()
  if (role?.role !== 'admin') return null
  return { email: user.email }
}

export async function GET(req: NextRequest) {
  const db = await createSSRClient()
  const admin = await requireAdmin(db)
  if (!admin) return NextResponse.json({ error: 'Forbidden: admin role required' }, { status: 403 })

  const adminDb = createServerClient()
  const searchParams = req.nextUrl.searchParams
  const q = searchParams.get('q')?.trim() || ''
  const source = searchParams.get('source') || 'manual' // 'manual' | 'all' | 'inaturalist'
  const page = Math.max(1, parseInt(searchParams.get('page') || '1'))
  const limit = Math.min(60, Math.max(10, parseInt(searchParams.get('limit') || '30')))
  const offset = (page - 1) * limit

  let query = adminDb
    .from('species_photos')
    .select(`
      id,
      species_id,
      storage_path,
      source,
      photographer,
      license,
      is_primary,
      created_at,
      species:species_id (
        id,
        vn_name,
        scientific_name
      )
    `, { count: 'exact' })
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1)

  if (source !== 'all') {
    query = query.eq('source', source)
  }

  if (q) {
    // Check if query matches any species
    const { data: matchedSpecies } = await adminDb
      .from('species')
      .select('id')
      .or(`vn_name.ilike.%${q}%,scientific_name.ilike.%${q}%`)
      .limit(30)

    const speciesIds = (matchedSpecies || []).map(s => s.id)

    if (speciesIds.length > 0) {
      query = query.or(`photographer.ilike.%${q}%,storage_path.ilike.%${q}%,species_id.in.(${speciesIds.join(',')})`)
    } else {
      query = query.or(`photographer.ilike.%${q}%,storage_path.ilike.%${q}%`)
    }
  }

  const { data, count, error } = await query

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json({
    photos: data || [],
    total: count || 0,
    page,
    limit,
    totalPages: Math.ceil((count || 0) / limit),
  })
}

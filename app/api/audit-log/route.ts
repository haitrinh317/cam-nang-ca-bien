/**
 * API: /api/audit-log
 * GET ?collection=xxx&limit=50 → audit log (admin only, server-side)
 */
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient, createSSRClient } from '@/lib/supabase-server'

export const dynamic = 'force-dynamic'

export async function GET(req: NextRequest) {
  const db = await createSSRClient()
  const { data: { user } } = await db.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  // Check admin via service_role (bypasses RLS on user_roles)
  const adminDb = createServerClient()
  const { data: role } = await adminDb
    .from('user_roles')
    .select('role')
    .eq('user_id', user.id)
    .single()

  if (role?.role !== 'admin') {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
  }

  const { searchParams } = req.nextUrl
  const collection = searchParams.get('collection')
  const limit = Math.min(parseInt(searchParams.get('limit') || '50'), 200)

  let query = adminDb
    .from('audit_log')
    .select('id, created_at, user_email, action, collection_id, species_id, details')
    .order('created_at', { ascending: false })
    .limit(limit)

  if (collection) query = query.eq('collection_id', collection)

  const { data, error } = await query
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })

  return NextResponse.json({ data })
}

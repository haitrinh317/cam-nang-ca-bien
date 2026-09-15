/**
 * API: /api/audit-log
 * GET ?collection=xxx&action=xxx&fromDate=YYYY-MM-DD&toDate=YYYY-MM-DD&page=1&pageSize=20
 * Audit log with multi-filtering and pagination (admin only, server-side)
 */
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient, createSSRClient } from '@/lib/supabase-server'
import { z } from 'zod'

export const dynamic = 'force-dynamic'

const COLLECTION_PREFIXES: Record<string, string[]> = {
  'ca-bien': ['tap'],
  'thuc-vat-bien': ['thucvat'],
  'giap-xac': ['giapxac'],
  'bo-sat-bien': ['ruabien', 'ranbien'],
  'sinh-vat-doc': ['sinhvatdoc'],
  'than-mem': ['thanmem'],
  'san-ho': ['sanho'],
  'thu-bien': ['thubien'],
}

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
  const qSchema = z.object({
    collection: z.string().max(30).optional(),
    action: z.string().max(20).optional(),
    fromDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
    toDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(20),
  })
  const parsed = qSchema.safeParse({
    collection: searchParams.get('collection') || undefined,
    action: searchParams.get('action') || undefined,
    fromDate: searchParams.get('fromDate') || undefined,
    toDate: searchParams.get('toDate') || undefined,
    page: searchParams.get('page') || 1,
    pageSize: searchParams.get('pageSize') || searchParams.get('limit') || 20,
  })
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.issues[0]?.message || 'Invalid params' }, { status: 400 })
  }
  const { collection, action, fromDate, toDate, page, pageSize } = parsed.data

  let query = adminDb
    .from('audit_log')
    .select('id, created_at, user_email, action, collection_id, species_id, details', { count: 'exact' })
    .order('created_at', { ascending: false })

  // 1. Filter by collection (with species_id prefix fallback for legacy logs)
  if (collection && collection !== 'all') {
    const prefixes = COLLECTION_PREFIXES[collection] || []
    if (prefixes.length > 0) {
      const orClauses = [`collection_id.eq.${collection}`]
      for (const p of prefixes) {
        orClauses.push(`species_id.ilike.${p}%`)
      }
      query = query.or(orClauses.join(','))
    } else {
      query = query.eq('collection_id', collection)
    }
  }

  // 2. Filter by action
  if (action && action !== 'all') {
    if (action === 'merge') {
      query = query.ilike('action', 'merge%')
    } else if (action === 'create') {
      query = query.in('action', ['create', 'bulk_import'])
    } else if (action === 'delete') {
      query = query.in('action', ['delete', 'bulk_delete'])
    } else if (action === 'update') {
      query = query.eq('action', 'update')
    } else {
      query = query.eq('action', action)
    }
  }

  // 3. Filter by date range
  if (fromDate) {
    query = query.gte('created_at', `${fromDate}T00:00:00.000Z`)
  }
  if (toDate) {
    query = query.lte('created_at', `${toDate}T23:59:59.999Z`)
  }

  // 4. Pagination
  const from = (page - 1) * pageSize
  const to = from + pageSize - 1
  query = query.range(from, to)

  const { data, count, error } = await query
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })

  const total = count || 0
  const totalPages = Math.ceil(total / pageSize)

  return NextResponse.json({
    data: data || [],
    total,
    page,
    pageSize,
    totalPages,
  })
}

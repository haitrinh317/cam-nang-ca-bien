/**
 * API: /api/species/import
 * POST — Bulk upsert species from JSON array
 * Body: { species: [...], collection_id: string }
 */
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient, createSSRClient } from '@/lib/supabase-server'
import { importSchema } from '@/lib/schemas'

export async function POST(req: NextRequest) {
  const db = await createSSRClient()

  // Auth check
  const { data: { user } } = await db.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const raw = await req.json()
  const parsed = importSchema.safeParse(raw)
  if (!parsed.success) {
    return NextResponse.json({ error: 'Dữ liệu không hợp lệ', details: parsed.error.flatten().fieldErrors }, { status: 400 })
  }

  const { species, collection_id } = parsed.data

  // Ensure collection_id on every row
  const rows = species.map(sp => ({
    ...sp,
    collection_id,
  }))

  const { data, error, count } = await db
    .from('species')
    .upsert(rows, { onConflict: 'id' })
    .select('id')

  if (error) return NextResponse.json({ error: error.message }, { status: 400 })

  // ponytail: must use service_role — RLS on audit_log only allows service_role INSERT
  await createServerClient().from('audit_log').insert({
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

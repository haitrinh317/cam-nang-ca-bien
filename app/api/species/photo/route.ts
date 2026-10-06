/**
 * API: /api/species/photo
 * POST — Upload photo for a species (multipart/form-data)
 * DELETE ?id=xxx — Remove photo for a species (from species_photos table)
 * PATCH ?id=xxx — Set photo as primary
 */
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient, createSSRClient } from '@/lib/supabase-server'
import { SPECIES_PHOTOS_BUCKET as BUCKET } from '@/lib/species-photos'
import { z } from 'zod'

const MAX_SIZE = 5 * 1024 * 1024 // 5MB

async function requireAdmin(db: Awaited<ReturnType<typeof createSSRClient>>): Promise<{ email: string } | null> {
  const { data: { user } } = await db.auth.getUser()
  if (!user?.email) return null
  
  const adminDb = createServerClient()
  const { data: role } = await adminDb.from('user_roles').select('role').eq('user_id', user.id).single()
  
  if (role?.role !== 'admin') return null
  return { email: user.email }
}

export async function POST(req: NextRequest) {
  const db = await createSSRClient()
  const admin = await requireAdmin(db)
  if (!admin) return NextResponse.json({ error: 'Forbidden: admin role required' }, { status: 403 })

  const adminDb = createServerClient()
  const formData = await req.formData()
  const file = formData.get('file') as File | null
  const speciesId = formData.get('species_id') as string | null
  const photographer = formData.get('photographer') as string | null
  const isPrimary = formData.get('is_primary') === 'true'
  const idx = parseInt((formData.get('idx') as string) || '1')

  if (!file || !speciesId) {
    return NextResponse.json({ error: 'file and species_id required' }, { status: 400 })
  }
  if (file.size > MAX_SIZE) {
    return NextResponse.json({ error: 'File quá lớn (tối đa 5MB)' }, { status: 400 })
  }
  if (!file.type.startsWith('image/')) {
    return NextResponse.json({ error: 'Chỉ chấp nhận file ảnh' }, { status: 400 })
  }

  // Build storage path: ca-bien/{speciesId}/{idx}.{ext}
  const ext = file.name.split('.').pop()?.toLowerCase() || 'jpg'
  const storagePath = `ca-bien/${speciesId}/${String(idx).padStart(2, '0')}.${ext}`

  // Upload to Supabase Storage (overwrite if exists)
  const buffer = Buffer.from(await file.arrayBuffer())
  const { error: uploadErr } = await adminDb.storage
    .from(BUCKET)
    .upload(storagePath, buffer, {
      contentType: file.type,
      upsert: true,
    })

  if (uploadErr) {
    return NextResponse.json({ error: uploadErr.message }, { status: 500 })
  }

  // Insert DB row
  const { error: dbErr, data } = await adminDb.from('species_photos').insert({
    species_id: speciesId,
    storage_path: storagePath,
    source: 'manual',
    photographer: photographer || null,
    license: null,
    is_primary: isPrimary,
    sort_order: idx - 1,
  }).select().single()

  if (dbErr) {
    return NextResponse.json({ error: dbErr.message }, { status: 500 })
  }

  // Audit log
  await adminDb.from('audit_log').insert({
    user_email: admin.email,
    action: 'update',
    species_id: speciesId,
    details: `Upload ảnh: ${file.name} (${(file.size / 1024).toFixed(0)}KB)`,
  })

  // Get public URL
  const { data: { publicUrl } } = adminDb.storage.from(BUCKET).getPublicUrl(storagePath)

  return NextResponse.json({ photo: data, publicUrl })
}

export async function DELETE(req: NextRequest) {
  const db = await createSSRClient()
  const admin = await requireAdmin(db)
  if (!admin) return NextResponse.json({ error: 'Forbidden: admin role required' }, { status: 403 })

  const adminDb = createServerClient()
  const photoId = req.nextUrl.searchParams.get('id')
  if (!photoId) return NextResponse.json({ error: 'id required' }, { status: 400 })

  // Get current photo to find the file path
  const { data: sp } = await adminDb.from('species_photos').select('*').eq('id', photoId).single()
  if (!sp) return NextResponse.json({ error: 'No photo to delete' }, { status: 400 })

  // Remove from storage
  await adminDb.storage.from(BUCKET).remove([sp.storage_path])

  // Remove from DB
  await adminDb.from('species_photos').delete().eq('id', photoId)

  // Audit
  await adminDb.from('audit_log').insert({
    user_email: admin.email,
    action: 'update',
    species_id: sp.species_id,
    details: 'Xóa ảnh loài',
  })

  return NextResponse.json({ success: true })
}

export async function PATCH(req: NextRequest) {
  const db = await createSSRClient()
  const admin = await requireAdmin(db)
  if (!admin) return NextResponse.json({ error: 'Forbidden: admin role required' }, { status: 403 })

  const adminDb = createServerClient()
  const raw = await req.json()
  const parsed = z.object({
    species_id: z.string().min(1),
    photo_id: z.string().uuid(),
    action: z.enum(['set_primary', 'update_metadata']).optional(),
    photographer: z.string().nullable().optional(),
    license: z.string().nullable().optional(),
    source: z.string().nullable().optional(),
    source_url: z.string().nullable().optional(),
    is_primary: z.boolean().optional(),
  }).safeParse(raw)

  if (!parsed.success) return NextResponse.json({ error: parsed.error.issues[0]?.message || 'Invalid params' }, { status: 400 })
  const { species_id, photo_id, action, photographer, license, source, source_url, is_primary } = parsed.data

  // Handle setting primary photo
  if (action === 'set_primary' || (is_primary === true) || (!action && photographer === undefined && license === undefined && source === undefined && source_url === undefined)) {
    // Unset all primary
    await adminDb.from('species_photos')
      .update({ is_primary: false })
      .eq('species_id', species_id)
    
    // Set this one as primary
    const { data: updatedPhoto } = await adminDb.from('species_photos')
      .update({ is_primary: true })
      .eq('id', photo_id)
      .select()
      .single()

    return NextResponse.json({ success: true, photo: updatedPhoto })
  }

  // Handle updating metadata (photographer, source, license, source_url)
  const updates: Record<string, unknown> = {}
  if (photographer !== undefined) updates.photographer = photographer && photographer.trim() !== '' ? photographer.trim() : null
  if (license !== undefined) updates.license = license && license.trim() !== '' ? license.trim() : null
  if (source !== undefined) updates.source = source && source.trim() !== '' ? source.trim() : null
  if (source_url !== undefined) updates.source_url = source_url && source_url.trim() !== '' ? source_url.trim() : null
  if (is_primary !== undefined) updates.is_primary = is_primary

  const { data: updatedPhoto, error: updateErr } = await adminDb.from('species_photos')
    .update(updates)
    .eq('id', photo_id)
    .select()
    .single()

  if (updateErr) {
    return NextResponse.json({ error: updateErr.message }, { status: 500 })
  }

  await adminDb.from('audit_log').insert({
    user_email: admin.email,
    action: 'update',
    species_id,
    details: `Cập nhật thông tin ảnh: ${photographer ? `Tác giả "${photographer}"` : 'Xóa thông tin tác giả'}`,
  })

  return NextResponse.json({ success: true, photo: updatedPhoto })
}

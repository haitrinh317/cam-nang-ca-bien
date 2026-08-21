/**
 * API: /api/species/photo
 * POST — Upload photo for a species (multipart/form-data)
 * DELETE ?id=xxx — Remove photo for a species
 */
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase-server'

const BUCKET = 'species-photos'
const MAX_SIZE = 5 * 1024 * 1024 // 5MB

export async function POST(req: NextRequest) {
  const db = createServerClient()

  const formData = await req.formData()
  const file = formData.get('file') as File | null
  const speciesId = formData.get('species_id') as string | null

  if (!file || !speciesId) {
    return NextResponse.json({ error: 'file and species_id required' }, { status: 400 })
  }
  if (file.size > MAX_SIZE) {
    return NextResponse.json({ error: 'File quá lớn (tối đa 5MB)' }, { status: 400 })
  }
  if (!file.type.startsWith('image/')) {
    return NextResponse.json({ error: 'Chỉ chấp nhận file ảnh' }, { status: 400 })
  }

  // Build storage path: species-photos/{speciesId}.{ext}
  const ext = file.name.split('.').pop()?.toLowerCase() || 'jpg'
  const path = `${speciesId}.${ext}`

  // Upload to Supabase Storage (overwrite if exists)
  const buffer = Buffer.from(await file.arrayBuffer())
  const { error: uploadErr } = await db.storage
    .from(BUCKET)
    .upload(path, buffer, {
      contentType: file.type,
      upsert: true,
    })

  if (uploadErr) {
    return NextResponse.json({ error: uploadErr.message }, { status: 500 })
  }

  // Get public URL
  const { data: { publicUrl } } = db.storage.from(BUCKET).getPublicUrl(path)

  // Update species record
  const { error: updateErr } = await db
    .from('species')
    .update({ photo_url: publicUrl })
    .eq('id', speciesId)

  if (updateErr) {
    return NextResponse.json({ error: updateErr.message }, { status: 500 })
  }

  // Audit log
  const { data: { user } } = await db.auth.getUser()
  await db.from('audit_log').insert({
    user_email: user?.email || 'anonymous',
    action: 'update',
    species_id: speciesId,
    details: `Upload ảnh: ${file.name} (${(file.size / 1024).toFixed(0)}KB)`,
  })

  return NextResponse.json({ photo_url: publicUrl })
}

export async function DELETE(req: NextRequest) {
  const db = createServerClient()
  const speciesId = req.nextUrl.searchParams.get('id')
  if (!speciesId) return NextResponse.json({ error: 'id required' }, { status: 400 })

  // Get current photo_url to find the file path
  const { data: sp } = await db.from('species').select('photo_url').eq('id', speciesId).single()
  if (!sp?.photo_url) return NextResponse.json({ error: 'No photo to delete' }, { status: 400 })

  // Extract path from URL
  const urlParts = sp.photo_url.split(`/storage/v1/object/public/${BUCKET}/`)
  const filePath = urlParts[1]

  if (filePath) {
    await db.storage.from(BUCKET).remove([filePath])
  }

  // Clear photo_url
  await db.from('species').update({ photo_url: '' }).eq('id', speciesId)

  // Audit
  const { data: { user } } = await db.auth.getUser()
  await db.from('audit_log').insert({
    user_email: user?.email || 'anonymous',
    action: 'update',
    species_id: speciesId,
    details: 'Xóa ảnh loài',
  })

  return NextResponse.json({ success: true })
}

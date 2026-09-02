'use client'

import { useEffect, useState, useCallback } from 'react'
import { db } from '@/lib/supabase-browser'
import { Camera, Upload, Star, Trash2, Loader2, User } from 'lucide-react'

interface Photo {
  id: string
  storage_path: string
  source: string
  photographer: string | null
  license: string | null
  source_url: string | null
  is_primary: boolean
  sort_order: number
}

interface Props {
  speciesId: string
  currentUrl: string | null     // legacy photo_url
  onUpdated: (url: string) => void
}

const BUCKET = 'species-photos'

export default function PhotoManager({ speciesId, currentUrl, onUpdated }: Props) {
  const [photos, setPhotos] = useState<Photo[]>([])
  const [uploading, setUploading] = useState(false)
  const [photographer, setPhotographer] = useState('')
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL

  const publicUrl = (path: string) =>
    `${supabaseUrl}/storage/v1/object/public/${BUCKET}/${path}`

  const loadPhotos = useCallback(async () => {
    const { data } = await db
      .from('species_photos')
      .select('*')
      .eq('species_id', speciesId)
      .order('is_primary', { ascending: false })
      .order('sort_order')
    if (data) setPhotos(data)
  }, [speciesId])

  useEffect(() => { loadPhotos() }, [loadPhotos])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)

    try {
      const idx = photos.length + 1
      
      const formData = new FormData()
      formData.append('file', file)
      formData.append('species_id', speciesId)
      formData.append('idx', String(idx))
      formData.append('is_primary', photos.length === 0 ? 'true' : 'false')
      if (photographer) formData.append('photographer', photographer)

      const res = await fetch('/api/species/photo', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.error || 'Upload failed')

      // Update legacy photo_url to first photo
      if (photos.length === 0) {
        onUpdated(json.publicUrl)
      }

      await loadPhotos()
      setPhotographer('')
    } catch (err) {
      alert(`Upload lỗi: ${err instanceof Error ? err.message : err}`)
    } finally {
      setUploading(false)
      // Reset file input
      e.target.value = ''
    }
  }

  const handleDelete = async (photo: Photo) => {
    if (!confirm(`Xóa ảnh này?`)) return
    const res = await fetch(`/api/species/photo?id=${photo.id}`, { method: 'DELETE', credentials: 'include' })
    if (res.ok) await loadPhotos()
  }

  const handleSetPrimary = async (photo: Photo) => {
    const res = await fetch('/api/species/photo', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ species_id: speciesId, photo_id: photo.id })
    })
    if (res.ok) {
      onUpdated(publicUrl(photo.storage_path))
      await loadPhotos()
    }
  }

  return (
    <div className="photo-manager">
      <div className="admin-modal__header">
        <h3 style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '0.75rem', color: 'var(--color-ink)' }}>
          <Camera size={20} /> Quản lý ảnh ({photos.length} ảnh)
        </h3>
      </div>

      {/* Existing photos */}
      {photos.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1rem' }}>
          {photos.map(p => (
            <div key={p.id} style={{
              border: p.is_primary ? '2px solid var(--color-accent)' : '1px solid var(--color-border)',
              borderRadius: '8px', padding: '0.5rem', textAlign: 'center',
              background: 'var(--color-paper)', maxWidth: '150px',
            }}>
              <img
                src={publicUrl(p.storage_path)}
                alt=""
                style={{ width: '120px', height: '90px', objectFit: 'cover', borderRadius: '4px' }}
              />
              {p.source === 'inaturalist' ? (
                <div style={{ fontSize: '0.75rem', color: 'var(--color-ink-3)', display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '0.25rem' }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><User size={12} /> {p.photographer}<br />{p.license?.toUpperCase()}</span>
                </div>
              ) : (
                <div style={{ fontSize: '0.75rem', color: 'var(--color-ink-3)', display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '0.25rem' }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><Upload size={12} /> {p.photographer || 'Tự upload'}</span>
                </div>
              )}
              {p.is_primary && (
                <div style={{ fontSize: '0.75rem', color: 'var(--color-accent)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <Star size={12} fill="currentColor" /> Ảnh chính
                </div>
              )}
              <div style={{ display: 'flex', gap: '0.25rem', marginTop: '0.25rem', justifyContent: 'center' }}>
                {!p.is_primary && (
                  <button
                    className="btn btn-outline"
                    style={{ padding: '0.1rem 0.3rem', fontSize: '0.7rem' }}
                    onClick={() => handleSetPrimary(p)}
                    title="Đặt làm ảnh chính"
                  ><Star size={14} /></button>
                )}
                <button
                  className="btn btn-outline"
                  style={{ padding: '0.1rem 0.3rem', fontSize: '0.7rem', color: '#dc2626' }}
                  onClick={() => handleDelete(p)}
                  title="Xóa ảnh"
                ><Trash2 size={14} /></button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Legacy URL */}
      {currentUrl && photos.length === 0 && (
        <div style={{ marginBottom: '1rem', padding: '0.5rem', background: 'var(--color-tint)', borderRadius: '8px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-ink-3)', marginBottom: '0.25rem' }}>Ảnh cũ (photo_url):</div>
          <img src={currentUrl} alt="" style={{ maxWidth: '200px', borderRadius: '4px' }} />
        </div>
      )}

      {/* Upload new */}
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-end', flexWrap: 'wrap' }}>
        <div>
          <label style={{ fontSize: '0.75rem', display: 'block', marginBottom: '0.25rem', color: 'var(--color-ink-2)' }}>
            Tác giả ảnh (tùy chọn)
          </label>
          <input
            type="text"
            className="form-input"
            placeholder="Tên photographer..."
            value={photographer}
            onChange={e => setPhotographer(e.target.value)}
            style={{ width: '180px', fontSize: '0.8rem' }}
          />
        </div>
        <label className="btn btn-primary" style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
          cursor: uploading ? 'wait' : 'pointer',
          padding: '0.4rem 0.8rem',
          fontSize: '0.8rem', opacity: uploading ? 0.6 : 1,
        }}>
          {uploading ? <><Loader2 size={14} className="animate-spin" /> Đang upload...</> : <><Upload size={14} /> Thêm ảnh</>}
          <input
            type="file"
            accept="image/*"
            onChange={handleUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
        </label>
      </div>
    </div>
  )
}

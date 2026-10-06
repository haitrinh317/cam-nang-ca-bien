'use client'

import { useEffect, useState, useCallback } from 'react'
import { db } from '@/lib/supabase-browser'
import { getSpeciesPhotoUrl } from '@/lib/species-photos'
import { Camera, Upload, Star, Trash2, Loader2, User, Check, Images } from 'lucide-react'
import PhotoLibraryModal, { type LibraryPhoto } from './PhotoLibraryModal'

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

/**
 * Nén và chuyển đổi ảnh sang WebP độ phân giải cao tại client trước khi upload.
 * Giúp triệt tiêu lỗi HTTP 413 "Request Entity Too Large" (>4.5MB) của Vercel Serverless.
 */
async function compressImageForUpload(file: File, maxDim = 1920, quality = 0.85): Promise<File> {
  // Nếu đã là WebP và <= 1.5MB thì giữ nguyên
  if (file.size <= 1.5 * 1024 * 1024 && file.type === 'image/webp') {
    return file
  }

  // Bỏ qua định dạng không phải ảnh bitmap (ví dụ svg)
  if (!file.type.startsWith('image/') || file.type.includes('svg')) {
    return file
  }

  return new Promise((resolve) => {
    const img = new Image()
    const url = URL.createObjectURL(file)

    img.onload = () => {
      URL.revokeObjectURL(url)
      let { width, height } = img

      // Scale tỷ lệ nếu lớn hơn kích thước maxDim
      if (width > maxDim || height > maxDim) {
        if (width > height) {
          height = Math.round((height * maxDim) / width)
          width = maxDim
        } else {
          width = Math.round((width * maxDim) / height)
          height = maxDim
        }
      }

      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        resolve(file)
        return
      }

      ctx.drawImage(img, 0, 0, width, height)

      canvas.toBlob(
        (blob) => {
          if (!blob) {
            resolve(file)
            return
          }
          const baseName = file.name.replace(/\.[^/.]+$/, '')
          const newFile = new File([blob], `${baseName}.webp`, {
            type: 'image/webp',
            lastModified: Date.now(),
          })
          resolve(newFile)
        },
        'image/webp',
        quality
      )
    }

    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve(file)
    }

    img.src = url
  })
}

export default function PhotoManager({ speciesId, currentUrl, onUpdated }: Props) {
  const [photos, setPhotos] = useState<Photo[]>([])
  const [uploading, setUploading] = useState(false)
  const [photographer, setPhotographer] = useState('')
  const [editingPhotographer, setEditingPhotographer] = useState<Record<string, string>>({})
  const [savingPhotoId, setSavingPhotoId] = useState<string | null>(null)
  const [savedPhotoId, setSavedPhotoId] = useState<string | null>(null)
  const [showLibrary, setShowLibrary] = useState(false)

  const publicUrl = (path: string) => getSpeciesPhotoUrl(path)

  const loadPhotos = useCallback(async () => {
    const { data } = await db
      .from('species_photos')
      .select('*')
      .eq('species_id', speciesId)
      .order('is_primary', { ascending: false })
      .order('sort_order')
    if (data) {
      setPhotos(data)
      const initialMap: Record<string, string> = {}
      data.forEach((p: Photo) => {
        initialMap[p.id] = p.photographer || ''
      })
      setEditingPhotographer(initialMap)
    }
  }, [speciesId])

  useEffect(() => { loadPhotos() }, [loadPhotos])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const originalFile = e.target.files?.[0]
    if (!originalFile) return
    setUploading(true)

    try {
      // Tối ưu ảnh tại client: resize và nén sang WebP để không chạm trần 4.5MB Vercel
      const file = await compressImageForUpload(originalFile)

      if (file.size > 4.5 * 1024 * 1024) {
        throw new Error(`Ảnh quá lớn (${(file.size / 1024 / 1024).toFixed(1)}MB). Vui lòng chọn ảnh dưới 4.5MB.`)
      }

      const idx = photos.length + 1
      
      const formData = new FormData()
      formData.append('file', file)
      formData.append('species_id', speciesId)
      formData.append('idx', String(idx))
      formData.append('is_primary', photos.length === 0 ? 'true' : 'false')
      if (photographer.trim()) formData.append('photographer', photographer.trim())

      const res = await fetch('/api/species/photo', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      })

      if (!res.ok) {
        let errMsg = `Lỗi máy chủ (${res.status})`
        try {
          const errJson = await res.json()
          errMsg = errJson.error || errMsg
        } catch {
          const text = await res.text()
          if (res.status === 413 || text.includes('Request Entity Too Large')) {
            errMsg = 'File ảnh quá lớn (> 4.5MB). Vui lòng chọn ảnh nhỏ hơn.'
          } else {
            errMsg = text.slice(0, 100) || errMsg
          }
        }
        throw new Error(errMsg)
      }

      const json = await res.json()

      // Update legacy photo_url to first photo
      if (photos.length === 0 && json.publicUrl) {
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

  const handleAttachFromLibrary = async (libraryPhoto: LibraryPhoto) => {
    const res = await fetch('/api/species/photo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        species_id: speciesId,
        storage_path: libraryPhoto.storage_path,
        photographer: libraryPhoto.photographer,
        source: libraryPhoto.source || 'manual',
        is_primary: photos.length === 0,
      }),
    })

    if (!res.ok) {
      let errMsg = `Lỗi (${res.status})`
      try {
        const j = await res.json()
        errMsg = j.error || errMsg
      } catch {
        const text = await res.text()
        errMsg = text.slice(0, 100) || errMsg
      }
      throw new Error(errMsg)
    }

    const json = await res.json()
    if (photos.length === 0 && json.publicUrl) {
      onUpdated(json.publicUrl)
    }

    await loadPhotos()
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
      body: JSON.stringify({ species_id: speciesId, photo_id: photo.id, action: 'set_primary' })
    })
    if (res.ok) {
      onUpdated(publicUrl(photo.storage_path))
      await loadPhotos()
    }
  }

  const handleUpdatePhotographer = async (photoId: string) => {
    const val = editingPhotographer[photoId]
    if (val === undefined) return
    const photo = photos.find(p => p.id === photoId)
    if (photo && (photo.photographer || '') === val.trim()) return // Không có thay đổi

    setSavingPhotoId(photoId)
    try {
      const res = await fetch('/api/species/photo', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          species_id: speciesId,
          photo_id: photoId,
          action: 'update_metadata',
          photographer: val.trim() || null,
        }),
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.error || 'Lỗi cập nhật tác giả ảnh')

      setSavedPhotoId(photoId)
      setTimeout(() => setSavedPhotoId(null), 2500)
      await loadPhotos()
    } catch (err) {
      alert(`Lỗi lưu tác giả: ${err instanceof Error ? err.message : err}`)
    } finally {
      setSavingPhotoId(null)
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
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          {photos.map(p => {
            const isEditing = editingPhotographer[p.id] !== undefined ? editingPhotographer[p.id] : (p.photographer || '')
            const isSaved = savedPhotoId === p.id
            const isSaving = savingPhotoId === p.id

            return (
              <div key={p.id} style={{
                border: p.is_primary ? '2px solid var(--color-accent)' : '1px solid var(--color-border)',
                borderRadius: '8px', padding: '0.6rem',
                background: 'var(--color-paper)', width: '210px',
                display: 'flex', flexDirection: 'column', gap: '0.35rem',
                position: 'relative',
              }}>
                <div style={{ position: 'relative', width: '100%', height: '120px', borderRadius: '4px', overflow: 'hidden', background: '#0f172a' }}>
                  <img
                    src={publicUrl(p.storage_path)}
                    alt=""
                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                  />
                  {p.is_primary && (
                    <div style={{
                      position: 'absolute', top: '4px', left: '4px',
                      background: 'rgba(15, 118, 110, 0.9)', color: '#ffffff',
                      fontSize: '0.7rem', fontWeight: 600, padding: '2px 6px',
                      borderRadius: '4px', display: 'inline-flex', alignItems: 'center', gap: '3px',
                      backdropFilter: 'blur(4px)',
                    }}>
                      <Star size={10} fill="currentColor" /> Ảnh chính
                    </div>
                  )}
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--color-ink-3)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  {p.source === 'inaturalist' ? (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <User size={12} /> iNaturalist {p.license ? `(${p.license.toUpperCase()})` : ''}
                    </span>
                  ) : (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <Upload size={12} /> Tải lên thủ công
                    </span>
                  )}
                </div>

                {/* Editable Photographer / Source Field */}
                <div style={{ marginTop: '0.2rem' }}>
                  <label style={{ fontSize: '0.7rem', color: 'var(--color-ink-2)', display: 'block', marginBottom: '2px', fontWeight: 500 }}>
                    Nguồn / Tác giả ảnh:
                  </label>
                  <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                    <input
                      type="text"
                      className="form-input"
                      style={{
                        fontSize: '0.75rem', padding: '3px 6px', height: '26px', flex: 1,
                        borderColor: isSaved ? '#059669' : undefined,
                      }}
                      placeholder="VD: Bảo tàng Hải dương học"
                      value={isEditing}
                      onChange={(e) => setEditingPhotographer(prev => ({ ...prev, [p.id]: e.target.value }))}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          handleUpdatePhotographer(p.id)
                        }
                      }}
                      onBlur={() => handleUpdatePhotographer(p.id)}
                    />
                    <button
                      type="button"
                      className="btn btn-outline"
                      style={{
                        padding: '0.2rem 0.4rem', height: '26px',
                        fontSize: '0.7rem',
                        color: isSaved ? '#059669' : undefined,
                        borderColor: isSaved ? '#059669' : undefined,
                      }}
                      disabled={isSaving}
                      onClick={() => handleUpdatePhotographer(p.id)}
                      title="Lưu tên tác giả / nguồn ảnh"
                    >
                      {isSaving ? <Loader2 size={12} className="animate-spin" /> : isSaved ? <Check size={12} /> : <Check size={12} />}
                    </button>
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: '0.25rem', marginTop: '0.25rem', justifyContent: 'space-between', alignItems: 'center' }}>
                  {!p.is_primary ? (
                    <button
                      type="button"
                      className="btn btn-outline"
                      style={{ padding: '0.2rem 0.4rem', fontSize: '0.7rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                      onClick={() => handleSetPrimary(p)}
                      title="Đặt làm ảnh chính cho loài"
                    >
                      <Star size={12} /> Đặt làm chính
                    </button>
                  ) : <span />}

                  <button
                    type="button"
                    className="btn btn-outline"
                    style={{ padding: '0.2rem 0.4rem', fontSize: '0.7rem', color: '#dc2626', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                    onClick={() => handleDelete(p)}
                    title="Xóa ảnh này"
                  >
                    <Trash2 size={12} /> Xóa
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Legacy URL */}
      {currentUrl && photos.length === 0 && (
        <div style={{ marginBottom: '1rem', padding: '0.5rem', background: 'var(--color-tint)', borderRadius: '8px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-ink-3)', marginBottom: '0.25rem' }}>Ảnh cũ (photo_url):</div>
          <img src={currentUrl} alt="" style={{ maxWidth: '200px', borderRadius: '4px' }} />
        </div>
      )}

      {/* Upload new photo & Pick from Library toolbar */}
      <div style={{
        display: 'flex', gap: '0.75rem', alignItems: 'flex-end', flexWrap: 'wrap',
        padding: '0.85rem', background: 'var(--color-tint)', borderRadius: '8px', border: '1px dashed var(--color-border)',
      }}>
        <div>
          <label style={{ fontSize: '0.75rem', display: 'block', marginBottom: '0.25rem', color: 'var(--color-ink-2)', fontWeight: 500 }}>
            Tác giả / Nguồn ảnh mới (tùy chọn)
          </label>
          <input
            type="text"
            className="form-input"
            placeholder="VD: Bảo tàng Hải dương học..."
            value={photographer}
            onChange={e => setPhotographer(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') e.preventDefault() }}
            style={{ width: '220px', fontSize: '0.8rem' }}
          />
        </div>

        <label className="btn btn-primary" style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
          cursor: uploading ? 'wait' : 'pointer',
          padding: '0.45rem 0.9rem',
          fontSize: '0.8rem', opacity: uploading ? 0.6 : 1,
        }}>
          {uploading ? <><Loader2 size={14} className="animate-spin" /> Đang tối ưu & tải ảnh...</> : <><Upload size={14} /> Tải ảnh mới</>}
          <input
            type="file"
            accept="image/*"
            onChange={handleUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
        </label>

        <button
          type="button"
          className="btn btn-outline"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
            padding: '0.45rem 0.9rem', fontSize: '0.8rem',
            background: 'var(--color-paper)',
          }}
          onClick={() => setShowLibrary(true)}
          title="Chọn một ảnh đã có sẵn trong thư viện hệ thống"
        >
          <Images size={14} /> Chọn từ thư viện đã upload
        </button>
      </div>

      {/* Modal Thư Viện Ảnh */}
      {showLibrary && (
        <PhotoLibraryModal
          currentSpeciesId={speciesId}
          onSelect={handleAttachFromLibrary}
          onClose={() => setShowLibrary(false)}
        />
      )}
    </div>
  )
}

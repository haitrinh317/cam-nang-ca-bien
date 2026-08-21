'use client'

import { useState, useRef } from 'react'

interface Props {
  speciesId: string
  currentUrl: string | null
  onUpdated: (newUrl: string) => void
}

export default function PhotoManager({ speciesId, currentUrl, onUpdated }: Props) {
  const [uploading, setUploading] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setError('')
    setUploading(true)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('species_id', speciesId)

    try {
      const res = await fetch('/api/species/photo', { method: 'POST', body: formData })
      const json = await res.json()
      if (!res.ok) { setError(json.error); return }
      onUpdated(json.photo_url)
    } catch (err) {
      setError(`Upload thất bại: ${err}`)
    } finally {
      setUploading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  const handleDelete = async () => {
    if (!confirm('Xóa ảnh này?')) return
    setDeleting(true)
    setError('')

    try {
      const res = await fetch(`/api/species/photo?id=${speciesId}`, { method: 'DELETE' })
      const json = await res.json()
      if (!res.ok) { setError(json.error); return }
      onUpdated('')
    } catch (err) {
      setError(`Xóa thất bại: ${err}`)
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="photo-manager">
      {/* Preview */}
      {currentUrl ? (
        <div className="photo-preview">
          <img src={currentUrl} alt="Ảnh loài" className="photo-preview__img" />
          <div className="photo-preview__actions">
            <label className="btn btn-outline btn-sm" style={{ cursor: 'pointer' }}>
              📷 Đổi ảnh
              <input ref={inputRef} type="file" accept="image/*" onChange={handleUpload} style={{ display: 'none' }} />
            </label>
            <button
              className="btn btn-outline btn-sm"
              style={{ borderColor: '#ef4444', color: '#ef4444' }}
              onClick={handleDelete}
              disabled={deleting}
              type="button"
            >
              {deleting ? '...' : '🗑️ Xóa ảnh'}
            </button>
          </div>
        </div>
      ) : (
        <label className="photo-upload-zone" style={{ cursor: uploading ? 'wait' : 'pointer' }}>
          <input ref={inputRef} type="file" accept="image/*" onChange={handleUpload} style={{ display: 'none' }} />
          {uploading ? (
            <span className="photo-upload-text">Đang upload...</span>
          ) : (
            <>
              <span className="photo-upload-icon">📷</span>
              <span className="photo-upload-text">Chọn ảnh minh họa</span>
              <span className="photo-upload-hint">JPG, PNG, WebP — tối đa 5MB</span>
            </>
          )}
        </label>
      )}

      {error && <div className="photo-error">{error}</div>}
    </div>
  )
}

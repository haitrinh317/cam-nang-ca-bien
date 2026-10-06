'use client'

import { useState, useEffect, useCallback } from 'react'
import { getSpeciesPhotoUrl } from '@/lib/species-photos'
import { Search, X, Check, Loader2, User, Image as ImageIcon, RefreshCw } from 'lucide-react'

export interface LibraryPhoto {
  id: string
  species_id: string
  storage_path: string
  source: string
  photographer: string | null
  license: string | null
  created_at: string
  species?: {
    id: string
    vn_name: string
    scientific_name: string
  } | null
}

interface Props {
  currentSpeciesId: string
  onSelect: (photo: LibraryPhoto) => Promise<void>
  onClose: () => void
}

export default function PhotoLibraryModal({ currentSpeciesId, onSelect, onClose }: Props) {
  const [photos, setPhotos] = useState<LibraryPhoto[]>([])
  const [loading, setLoading] = useState(true)
  const [selectingId, setSelectingId] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [source, setSource] = useState<'manual' | 'all' | 'inaturalist'>('manual')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [hasMore, setHasMore] = useState(false)

  const publicUrl = (path: string) => getSpeciesPhotoUrl(path)

  const fetchLibrary = useCallback(async (reset = false, searchOverride?: string, sourceOverride?: string) => {
    setLoading(true)
    const targetPage = reset ? 1 : page
    const q = searchOverride !== undefined ? searchOverride : search
    const s = sourceOverride !== undefined ? sourceOverride : source

    try {
      const url = `/api/species/photo/library?q=${encodeURIComponent(q)}&source=${s}&page=${targetPage}&limit=24`
      const res = await fetch(url)
      const data = await res.json()
      if (res.ok && data.photos) {
        setPhotos(prev => (reset ? data.photos : [...prev, ...data.photos]))
        setTotal(data.total || 0)
        setHasMore(targetPage < (data.totalPages || 0))
      }
    } catch (err) {
      console.error('Lỗi tải thư viện ảnh:', err)
    } finally {
      setLoading(false)
    }
  }, [page, search, source])

  useEffect(() => {
    fetchLibrary(true, search, source)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [source])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchLibrary(true, search, source)
  }

  const handleLoadMore = () => {
    const nextPage = page + 1
    setPage(nextPage)
    // fetch next page
    const q = search
    const s = source
    setLoading(true)
    fetch(`/api/species/photo/library?q=${encodeURIComponent(q)}&source=${s}&page=${nextPage}&limit=24`)
      .then(res => res.json())
      .then(data => {
        if (data.photos) {
          setPhotos(prev => [...prev, ...data.photos])
          setHasMore(nextPage < (data.totalPages || 0))
        }
      })
      .finally(() => setLoading(false))
  }

  const handleSelectPhoto = async (photo: LibraryPhoto) => {
    setSelectingId(photo.id)
    try {
      await onSelect(photo)
      onClose()
    } catch (err) {
      alert(`Lỗi khi gán ảnh: ${err instanceof Error ? err.message : err}`)
    } finally {
      setSelectingId(null)
    }
  }

  return (
    <div className="admin-modal-overlay" onClick={onClose} style={{ zIndex: 1100 }}>
      <div
        className="admin-modal admin-modal--photo-library"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="admin-modal__header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', margin: 0, color: 'var(--color-ink)' }}>
              <ImageIcon size={20} /> Thư viện ảnh đã tải lên
            </h3>
            <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: 'var(--color-ink-3)' }}>
              Chọn một ảnh có sẵn trong hệ thống để gắn cho loài hiện tại ({total.toLocaleString('vi-VN')} ảnh)
            </p>
          </div>
          <button
            type="button"
            className="btn btn-outline"
            style={{ padding: '0.3rem', borderRadius: '50%' }}
            onClick={onClose}
            aria-label="Đóng thư viện"
          >
            <X size={18} />
          </button>
        </div>

        {/* Search & Filter Toolbar */}
        <div style={{ padding: '0.75rem 1.25rem', borderBottom: '1px solid var(--color-border)', background: 'var(--color-paper)' }}>
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={15} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-ink-3)' }} />
              <input
                type="text"
                className="form-input"
                style={{ paddingLeft: '32px', fontSize: '0.85rem', width: '100%' }}
                placeholder="Tìm theo tên loài, tên khoa học, tác giả ảnh..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}>
              Tìm kiếm
            </button>
            {search && (
              <button
                type="button"
                className="btn btn-outline"
                style={{ fontSize: '0.8rem', padding: '0.4rem 0.7rem' }}
                onClick={() => {
                  setSearch('')
                  setPage(1)
                  fetchLibrary(true, '', source)
                }}
              >
                Xóa tìm
              </button>
            )}
          </form>

          {/* Filter chips */}
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-ink-3)' }}>Nguồn:</span>
            <button
              type="button"
              className={`btn ${source === 'manual' ? 'btn-primary' : 'btn-outline'}`}
              style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}
              onClick={() => { setSource('manual'); setPage(1) }}
            >
              Ảnh tải lên thủ công
            </button>
            <button
              type="button"
              className={`btn ${source === 'all' ? 'btn-primary' : 'btn-outline'}`}
              style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}
              onClick={() => { setSource('all'); setPage(1) }}
            >
              Tất cả ảnh
            </button>
            <button
              type="button"
              className={`btn ${source === 'inaturalist' ? 'btn-primary' : 'btn-outline'}`}
              style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}
              onClick={() => { setSource('inaturalist'); setPage(1) }}
            >
              iNaturalist
            </button>
          </div>
        </div>

        {/* Photo Grid */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', minHeight: '320px' }}>
          {loading && photos.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-ink-3)' }}>
              <Loader2 size={24} className="animate-spin" style={{ margin: '0 auto 0.5rem' }} />
              <div>Đang tải danh sách ảnh thư viện...</div>
            </div>
          ) : photos.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-ink-3)' }}>
              <ImageIcon size={32} style={{ margin: '0 auto 0.5rem', opacity: 0.5 }} />
              <div>Không tìm thấy ảnh nào phù hợp với bộ lọc.</div>
            </div>
          ) : (
            <div className="photo-library-grid">
              {photos.map(p => {
                const isCurrent = p.species_id === currentSpeciesId
                const isSelecting = selectingId === p.id

                return (
                  <div
                    key={p.id}
                    style={{
                      border: '1px solid var(--color-border)',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      background: 'var(--color-paper)',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: 'border-color 0.15s ease, transform 0.15s ease',
                    }}
                  >
                    <div style={{ position: 'relative', height: '140px', background: '#0f172a', overflow: 'hidden' }}>
                      <img
                        src={publicUrl(p.storage_path)}
                        alt=""
                        loading="lazy"
                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                      />
                      {isCurrent && (
                        <div style={{
                          position: 'absolute', top: '6px', right: '6px',
                          background: 'rgba(15, 118, 110, 0.92)', color: '#fff',
                          fontSize: '0.7rem', fontWeight: 600, padding: '2px 7px', borderRadius: '4px',
                        }}>
                          Đang dùng
                        </div>
                      )}
                    </div>

                    <div style={{ padding: '0.65rem 0.75rem', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '0.5rem' }}>
                      <div>
                        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-ink)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {p.species?.vn_name || p.species_id}
                        </div>
                        {p.species?.scientific_name && (
                          <div style={{ fontSize: '0.75rem', fontStyle: 'italic', color: 'var(--color-ink-3)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {p.species.scientific_name}
                          </div>
                        )}
                        <div style={{ fontSize: '0.72rem', color: 'var(--color-ink-2)', marginTop: '3px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <User size={12} />
                          <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {p.photographer || (p.source === 'manual' ? 'Tự upload' : 'iNaturalist')}
                          </span>
                        </div>
                      </div>

                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{
                          width: '100%',
                          padding: '0.35rem 0.5rem',
                          fontSize: '0.78rem',
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '6px',
                          background: 'var(--color-tint)',
                        }}
                        disabled={isSelecting}
                        onClick={() => handleSelectPhoto(p)}
                      >
                        {isSelecting ? <Loader2 size={13} className="animate-spin" /> : <Check size={13} />}
                        Chọn ảnh này
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {/* Load More Button */}
          {hasMore && (
            <div style={{ textAlign: 'center', marginTop: '1.25rem' }}>
              <button
                type="button"
                className="btn btn-outline"
                style={{ fontSize: '0.8rem', padding: '0.4rem 1.25rem' }}
                disabled={loading}
                onClick={handleLoadMore}
              >
                {loading ? <><Loader2 size={13} className="animate-spin" /> Đang tải...</> : 'Tải thêm ảnh khác'}
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="admin-modal__footer" style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button type="button" className="btn btn-outline" onClick={onClose}>
            Đóng
          </button>
        </div>
      </div>
    </div>
  )
}

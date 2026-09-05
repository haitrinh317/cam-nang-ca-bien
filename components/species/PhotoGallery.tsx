'use client'

import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { db } from '@/lib/supabase-browser'
import { getSpeciesPhotoUrl } from '@/lib/species-photos'
import { Camera, X, ChevronLeft, ChevronRight } from 'lucide-react'

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
  fallbackUrl?: string | null  // legacy photo_url from species table
  initialPhotos?: Photo[]      // server-fetched photos — eliminates client waterfall
}

function sortPhotos(data: Photo[]): Photo[] {
  return [...data].sort((a, b) => {
    if (a.source === 'manual' && b.source !== 'manual') return -1
    if (a.source !== 'manual' && b.source === 'manual') return 1
    if (a.is_primary && !b.is_primary) return -1
    if (!a.is_primary && b.is_primary) return 1
    return a.sort_order - b.sort_order
  })
}

export default function PhotoGallery({ speciesId, fallbackUrl, initialPhotos }: Props) {
  const [photos, setPhotos] = useState<Photo[]>(initialPhotos ? sortPhotos(initialPhotos) : [])
  const [mainIdx, setMainIdx] = useState(0)
  const [loaded, setLoaded] = useState(!!initialPhotos)
  const [lightbox, setLightbox] = useState(false)
  const [fading, setFading] = useState(false)

  function switchPhoto(idx: number) {
    setFading(true)
    setTimeout(() => { setMainIdx(idx); setFading(false) }, 150)
  }

  // ponytail: only client-fetch if server didn't provide initialPhotos
  useEffect(() => {
    if (initialPhotos) return // already have data from server
    let cancelled = false
    db.from('species_photos')
      .select('*')
      .eq('species_id', speciesId)
      .order('is_primary', { ascending: false })
      .order('sort_order')
      .then(({ data }) => {
        if (!cancelled && data) {
          setPhotos(sortPhotos(data))
          setLoaded(true)
        }
      })
    return () => { cancelled = true }
  }, [speciesId, initialPhotos])

  function publicUrl(path: string) {
    return getSpeciesPhotoUrl(path)
  }

  // Fallback: use legacy photo_url if no photos in species_photos
  if (loaded && photos.length === 0) {
    if (!fallbackUrl) return null
    return (
      <figure className="specimen__photo">
        <img src={fallbackUrl} alt="" decoding="async" fetchPriority="high" />
      </figure>
    )
  }

  if (!loaded || photos.length === 0) return null

  const main = photos[mainIdx]
  const mainUrl = publicUrl(main.storage_path)

  return (
    <>
      <div className="specimen__gallery">
        {/* Main photo — LCP critical image */}
        <figure
          className="specimen__photo specimen__photo--main"
          onClick={() => setLightbox(true)}
          role="button"
          tabIndex={0}
          aria-label="Phóng to ảnh"
          onKeyDown={e => e.key === 'Enter' && setLightbox(true)}
        >
          <img src={mainUrl} alt="" decoding="async" fetchPriority="high" style={{ opacity: fading ? 0 : 1, transition: 'opacity 0.15s ease' }} />
        </figure>

        {/* Thumbnails (Desktop) */}
        {photos.length > 1 && (
          <div className="specimen__photo-thumbs">
            {photos.map((p, i) => (
              <button
                key={p.id}
                className={`specimen__thumb${i === mainIdx ? ' active' : ''}`}
                onClick={() => switchPhoto(i)}
                type="button"
                aria-label={`Ảnh ${i + 1}`}
              >
                <img src={publicUrl(p.storage_path)} alt="" loading="lazy" decoding="async" width={72} height={54} />
              </button>
            ))}
          </div>
        )}

        {/* Dot Indicators (Mobile) */}
        {photos.length > 1 && (
          <div className="specimen__photo-dots">
            {photos.map((p, i) => (
              <button
                key={`dot-${p.id}`}
                className={`specimen__dot${i === mainIdx ? ' active' : ''}`}
                onClick={() => switchPhoto(i)}
                type="button"
                aria-label={`Chuyển đến ảnh ${i + 1}`}
              />
            ))}
          </div>
        )}

        {/* Credit */}
        <div className="specimen__photo-credit">
          {main.source === 'inaturalist' ? (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <Camera size={14} /> {main.photographer || 'Unknown'} ·{' '}
              {main.source_url ? (
                <a href={main.source_url} target="_blank" rel="noopener">iNaturalist</a>
              ) : 'iNaturalist'}
              {main.license && ` (${main.license.toUpperCase()})`}
            </span>
          ) : (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><Camera size={14} /> {main.photographer || 'Ảnh cung cấp bởi tác giả'}</span>
          )}
        </div>
      </div>

      {/* Lightbox */}
      {lightbox && typeof document !== 'undefined' && createPortal(
        <div
          className="photo-lightbox"
          onClick={() => setLightbox(false)}
          role="dialog"
          aria-label="Xem ảnh phóng to"
        >
          <button
            className="photo-lightbox__close"
            onClick={() => setLightbox(false)}
            aria-label="Đóng"
            type="button"
          ><X size={24} /></button>
          <img
            src={mainUrl}
            alt=""
            onClick={e => e.stopPropagation()}
          />
          <div className="photo-lightbox__credit" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <Camera size={14} /> {main.photographer || 'Unknown'}
            {main.source === 'inaturalist' && main.source_url && (
              <> · <a href={main.source_url} target="_blank" rel="noopener">iNaturalist</a>
              {main.license && ` (${main.license.toUpperCase()})`}</>
            )}
          </div>
          {/* Nav arrows */}
          {photos.length > 1 && (
            <>
              <button
                className="photo-lightbox__nav photo-lightbox__nav--prev"
                onClick={e => { e.stopPropagation(); setMainIdx((mainIdx - 1 + photos.length) % photos.length) }}
                aria-label="Ảnh trước"
                type="button"
              ><ChevronLeft size={36} /></button>
              <button
                className="photo-lightbox__nav photo-lightbox__nav--next"
                onClick={e => { e.stopPropagation(); setMainIdx((mainIdx + 1) % photos.length) }}
                aria-label="Ảnh tiếp"
                type="button"
              ><ChevronRight size={36} /></button>
            </>
          )}
        </div>,
        document.body
      )}
    </>
  )
}

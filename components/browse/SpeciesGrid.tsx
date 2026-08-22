'use client'

import { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'
import { db } from '@/lib/supabase-browser'
import { getCollectionBySlug } from '@/lib/collections-static'

interface Species {
  id: string
  volume: number
  species_index: number
  vn_name: string
  scientific_name: string
  tax_order_vn: string | null
  tax_family_vn: string | null
}

interface Props {
  collection: string // e.g. 'ca-bien'
  initialVol?: number
}

const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

export default function SpeciesGrid({ collection, initialVol = 1 }: Props) {
  const col = getCollectionBySlug(collection)
  const volumes = Array.from({ length: col?.volumeCount || 1 }, (_, i) => i + 1)

  const [currentVol, setCurrentVol] = useState(initialVol)
  const [species, setSpecies] = useState<Species[]>([])
  const [filtered, setFiltered] = useState<Species[]>([])
  const [status, setStatus] = useState<'loading' | 'error' | 'ok'>('loading')
  const [filterQuery, setFilterQuery] = useState('')

  const loadVolume = useCallback(async (vol: number) => {
    setStatus('loading')
    setFilterQuery('')
    const { data, error } = await db
      .from('species')
      .select('id, volume, species_index, vn_name, scientific_name, tax_order_vn, tax_family_vn')
      .eq('collection_id', collection)  // ← FIX: filter by collection
      .eq('volume', vol)
      .order('species_index')
      .limit(700) // ponytail: largest volume ~518 species

    if (error || !data) { setStatus('error'); return }
    setSpecies(data)
    setFiltered(data)
    setStatus('ok')
  }, [collection])

  useEffect(() => { loadVolume(currentVol) }, [currentVol, loadVolume])

  // Reset to vol 1 if collection changes
  useEffect(() => { setCurrentVol(1) }, [collection])

  const handleFilter = (e: React.ChangeEvent<HTMLInputElement>) => {
    const q = e.target.value.toLowerCase()
    setFilterQuery(e.target.value)
    setFiltered(
      q ? species.filter(sp =>
        sp.vn_name.toLowerCase().includes(q) ||
        sp.scientific_name.toLowerCase().includes(q)
      ) : species
    )
  }

  return (
    <>
      {/* Volume tabs — dynamic from collection config */}
      {volumes.length > 1 && (
        <nav className="vol-tabs" aria-label="Chọn tập">
          {volumes.map(v => (
            <button
              key={v}
              className={`vol-tab${currentVol === v ? ' active' : ''}`}
              onClick={() => setCurrentVol(v)}
              type="button"
            >
              Tập {ROMAN[v - 1]}
            </button>
          ))}
        </nav>
      )}

      {/* Filter input */}
      <div className="search-input-container" style={{ maxWidth: '540px', marginBottom: 'var(--space-3xl)' }}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          id="localFilter"
          className="search-input"
          placeholder={`Lọc nhanh tên loài trong ${volumes.length > 1 ? `tập ${ROMAN[currentVol - 1]}` : 'bộ sưu tập'}...`}
          autoComplete="off"
          value={filterQuery}
          onChange={handleFilter}
        />
      </div>

      {/* Grid */}
      <section id="gridContainer" className="grid-species" aria-label="Danh sách loài trong tập">
        {status === 'loading' && (
          <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '3rem', color: 'var(--color-muted)' }}>
            Đang tải dữ liệu loài...
          </div>
        )}
        {status === 'error' && (
          <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '3rem', color: '#f87171' }}>
            Lỗi tải dữ liệu. Thử lại sau.
          </div>
        )}
        {status === 'ok' && filtered.length === 0 && (
          <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '3rem', color: 'var(--color-muted)' }}>
            {filterQuery ? 'Không tìm thấy loài phù hợp.' : `Chưa có dữ liệu.`}
          </div>
        )}
        {status === 'ok' && filtered.map(sp => (
          <Link key={sp.id} href={`/${collection}/${sp.id}`} className="species-card-mini">
            <div className="scm-id">#{sp.species_index}</div>
            <div className="scm-name">{sp.vn_name}</div>
            <div className="scm-sci">{sp.scientific_name}</div>
            <div className="scm-tax">
              {sp.tax_order_vn || ''}
              {sp.tax_family_vn ? ` → ${sp.tax_family_vn}` : ''}
            </div>
          </Link>
        ))}
      </section>
    </>
  )
}

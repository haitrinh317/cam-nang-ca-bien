'use client'

import { useEffect, useState, useCallback, useMemo } from 'react'
import Link from 'next/link'
import { useSearchParams, useRouter } from 'next/navigation'
import { db } from '@/lib/supabase-browser'
import { getBooksForCollection, BookMetadata, VolumeMetadata } from '@/lib/books-data'
import { BookOpen, Layers, Search, ArrowRight, CheckCircle2 } from 'lucide-react'

interface SpeciesItem {
  id: string
  volume: number
  species_index: number
  vn_name: string
  scientific_name: string
  authorship: string | null
}

interface Props {
  collection: string // e.g. 'ca-bien'
  initialVol?: number
}

export default function SpeciesGrid({ collection, initialVol = 1 }: Props) {
  const books = useMemo(() => getBooksForCollection(collection), [collection])
  const searchParams = useSearchParams()
  const router = useRouter()

  // Determine initial volume and book from URL or props
  const volFromUrl = parseInt(searchParams.get('vol') || '') || initialVol

  // Find which book contains this volume
  const initialBook = useMemo(() => {
    if (!books.length) return null
    const found = books.find(b => b.volumes.some(v => v.volume === volFromUrl))
    return found || books[0]
  }, [books, volFromUrl])

  const [selectedBookId, setSelectedBookId] = useState<string>(initialBook?.id || '')
  const [currentVol, setCurrentVol] = useState<number>(volFromUrl)
  const [speciesList, setSpeciesList] = useState<SpeciesItem[]>([])
  const [status, setStatus] = useState<'loading' | 'error' | 'ok'>('loading')
  const [localFilter, setLocalFilter] = useState<string>('')

  // Active book object
  const activeBook = useMemo(() => {
    return books.find(b => b.id === selectedBookId) || books[0] || null
  }, [books, selectedBookId])

  // Active volume metadata
  const activeVolumeMeta = useMemo(() => {
    return activeBook?.volumes.find(v => v.volume === currentVol) || activeBook?.volumes[0] || null
  }, [activeBook, currentVol])

  // Fetch species for current volume (only text columns, no photos, super fast)
  const loadVolumeData = useCallback(async (vol: number) => {
    setStatus('loading')
    setLocalFilter('')
    const { data, error } = await db
      .from('species')
      .select('id, volume, species_index, vn_name, scientific_name, authorship')
      .eq('collection_id', collection)
      .eq('volume', vol)
      .is('deleted_at', null)
      .order('species_index')
      .limit(800)

    if (error || !data) {
      setStatus('error')
      return
    }

    setSpeciesList(data as SpeciesItem[])
    setStatus('ok')
  }, [collection])

  // When volume changes, load data
  useEffect(() => {
    if (currentVol) {
      loadVolumeData(currentVol)
    }
  }, [currentVol, loadVolumeData])

  // Sync when URL parameter changes
  useEffect(() => {
    const urlVol = parseInt(searchParams.get('vol') || '')
    if (urlVol && urlVol !== currentVol) {
      setCurrentVol(urlVol)
      const parentBook = books.find(b => b.volumes.some(v => v.volume === urlVol))
      if (parentBook && parentBook.id !== selectedBookId) {
        setSelectedBookId(parentBook.id)
      }
    }
  }, [searchParams, books, currentVol, selectedBookId])

  // Handle switching Book
  const handleSelectBook = (book: BookMetadata) => {
    setSelectedBookId(book.id)
    const targetVol = book.volumes[0]?.volume || 1
    setCurrentVol(targetVol)

    const params = new URLSearchParams(searchParams.toString())
    params.set('vol', String(targetVol))
    router.replace(`?${params.toString()}`, { scroll: false })
  }

  // Handle switching Volume
  const handleSelectVolume = (vol: number) => {
    setCurrentVol(vol)
    const params = new URLSearchParams(searchParams.toString())
    params.set('vol', String(vol))
    router.replace(`?${params.toString()}`, { scroll: false })
  }

  // In-memory filter for the list
  const filteredSpecies = useMemo(() => {
    if (!localFilter.trim()) return speciesList
    const q = localFilter.toLowerCase().trim()
    return speciesList.filter(sp =>
      (sp.vn_name && sp.vn_name.toLowerCase().includes(q)) ||
      (sp.scientific_name && sp.scientific_name.toLowerCase().includes(q)) ||
      String(sp.species_index).includes(q)
    )
  }, [speciesList, localFilter])

  return (
    <div className="book-browser-container">
      {/* ─── 1. BỘ CHỌN ĐẦU SÁCH ─── */}
      <section className="book-selector-section" aria-label="Chọn đầu sách tra cứu">
        <div className="section-label">
          <BookOpen size={18} />
          <span>CHỌN ĐẦU SÁCH KHOA HỌC GỐC</span>
        </div>

        <div className="book-cards-grid">
          {books.map(book => {
            const isSelected = book.id === selectedBookId
            return (
              <div
                key={book.id}
                role="button"
                tabIndex={0}
                className={`book-card ${isSelected ? 'is-selected' : ''}`}
                onClick={() => handleSelectBook(book)}
                onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') handleSelectBook(book) }}
              >
                <div className="bc-top">
                  <span className="bc-badge">{book.badge}</span>
                  {isSelected && (
                    <span className="bc-status-pill">
                      <CheckCircle2 size={14} /> Đang xem
                    </span>
                  )}
                </div>
                <h3 className="bc-title">{book.title}</h3>
                <p className="bc-author">{book.author}</p>
                <p className="bc-desc">{book.description}</p>
                <div className="bc-meta">
                  <span>{book.publisher} ({book.yearRange})</span>
                  <span className="bc-species-total">{book.totalSpecies.toLocaleString()} loài</span>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* ─── 2. DANH SÁCH TẬP CỦA ĐẦU SÁCH ĐÃ CHỌN ─── */}
      {activeBook && (
        <section className="volume-selector-section" aria-label="Chọn tập trong đầu sách">
          <div className="section-label">
            <Layers size={18} />
            <span>CÁC TẬP TRONG BỘ SÁCH: <strong>{activeBook.title.toUpperCase()}</strong></span>
          </div>

          {activeBook.volumes.length > 1 ? (
            <div className="volume-full-tabs">
              {activeBook.volumes.map(v => {
                const isActive = v.volume === currentVol
                return (
                  <button
                    key={v.volume}
                    type="button"
                    className={`volume-full-tab ${isActive ? 'is-active' : ''}`}
                    onClick={() => handleSelectVolume(v.volume)}
                  >
                    <div className="vft-roman">TẬP {v.roman}</div>
                    <div className="vft-content">
                      <div className="vft-title">{v.title}</div>
                      <div className="vft-sub">{v.subTitle}</div>
                    </div>
                    <div className="vft-count">{v.speciesCount} loài</div>
                  </button>
                )
              })}
            </div>
          ) : (
            <div className="single-volume-banner">
              <div className="svb-title">{activeBook.volumes[0]?.title}</div>
              <div className="svb-sub">{activeBook.volumes[0]?.subTitle} — {activeBook.volumes[0]?.speciesCount} loài</div>
            </div>
          )}
        </section>
      )}

      {/* ─── 3. BẢNG DANH SÁCH LOÀI DẠNG LIST (SIÊU NHẸ, KHÔNG ẢNH) ─── */}
      <section className="species-list-section" aria-label="Danh sách loài dạng bảng">
        <div className="species-list-toolbar">
          <div className="slt-info">
            <h2 className="slt-volume-title">
              {activeVolumeMeta?.title || `Tập ${currentVol}`}
            </h2>
            <span className="slt-counter">
              Hiển thị {filteredSpecies.length} / {speciesList.length} loài
            </span>
          </div>

          <div className="slt-filter-box">
            <Search size={16} className="slt-filter-icon" />
            <input
              type="text"
              placeholder={`Lọc nhanh trong tập này...`}
              value={localFilter}
              onChange={e => setLocalFilter(e.target.value)}
              className="slt-filter-input"
            />
            {localFilter && (
              <button
                type="button"
                className="slt-filter-clear"
                onClick={() => setLocalFilter('')}
                aria-label="Xóa bộ lọc"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Trạng thái tải */}
        {status === 'loading' && (
          <div className="list-status-message">
            <div className="spinner" />
            <span>Đang tải danh sách loài...</span>
          </div>
        )}

        {status === 'error' && (
          <div className="list-status-message is-error">
            <span>Không thể tải dữ liệu từ máy chủ. Vui lòng thử lại sau.</span>
          </div>
        )}

        {status === 'ok' && (
          <div className="species-table-wrapper">
            <table className="species-list-table">
              <thead>
                <tr>
                  <th className="th-stt">STT</th>
                  <th className="th-vn">Tên loài & Tên khoa học</th>
                  <th className="th-sci desktop-only">Tên khoa học & Tác giả</th>
                  <th className="th-action"></th>
                </tr>
              </thead>
              <tbody>
                {filteredSpecies.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="td-empty">
                      {localFilter ? `Không tìm thấy loài nào khớp với từ khóa "${localFilter}".` : 'Không có dữ liệu loài trong tập này.'}
                    </td>
                  </tr>
                ) : (
                  filteredSpecies.map(sp => (
                    <tr
                      key={sp.id}
                      className="species-row"
                      onClick={() => router.push(`/${collection}/${sp.id}`)}
                    >
                      <td className="td-stt">
                        <span className="stt-badge">#{sp.species_index}</span>
                      </td>
                      <td className="td-vn">
                        <Link
                          href={`/${collection}/${sp.id}`}
                          className="species-vn-link"
                          onClick={e => e.stopPropagation()}
                        >
                          {sp.vn_name}
                        </Link>
                        <div className="species-mobile-sci">
                          <span className="sci-name">{sp.scientific_name}</span>
                          {sp.authorship && (
                            <span className="sci-author">{sp.authorship}</span>
                          )}
                        </div>
                      </td>
                      <td className="td-sci desktop-only">
                        <span className="sci-name">{sp.scientific_name}</span>
                        {sp.authorship && (
                          <span className="sci-author">{sp.authorship}</span>
                        )}
                      </td>
                      <td className="td-action">
                        <ArrowRight size={18} className="row-arrow" />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

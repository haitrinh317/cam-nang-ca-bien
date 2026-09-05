'use client'

import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import Link from 'next/link'
import { useSearchParams, useRouter } from 'next/navigation'
import { db } from '@/lib/supabase-browser'
import { getBooksForCollection, BookMetadata, VolumeMetadata } from '@/lib/books-data'
import { applySpeciesFilters } from '@/lib/species-query'
import { getSpecialGroup, SpecialGroupConfig } from '@/lib/special-groups'
import { BookOpen, Layers, Search, ArrowRight, ArrowLeft, CheckCircle2, Sparkles, X } from 'lucide-react'
import './SpecialGroupBanner.css'

// ponytail: sessionStorage key for scroll restoration when returning from species detail
const SCROLL_KEY = 'speciesGrid_scrollY'

interface SpeciesItem {
  id: string
  volume: number
  species_index: number
  vn_name: string
  scientific_name: string
  authorship: string | null
  biology?: {
    iucnStatus?: string
  } | null
  vn_distribution?: string | null
  en_distribution?: string | null
  vn_specimen?: string | null
  collection_id?: string | null
}

export const isHSLocation = (s: SpeciesItem) => {
  const str = `${s.vn_distribution || ''} ${s.en_distribution || ''} ${s.vn_specimen || ''} ${s.vn_name || ''}`.toLowerCase()
  return str.includes('hoàng sa') || str.includes('hoang sa') || str.includes('paracel') || str.includes('hoàng-sa')
}

export const isTSLocation = (s: SpeciesItem) => {
  const str = `${s.vn_distribution || ''} ${s.en_distribution || ''} ${s.vn_specimen || ''} ${s.vn_name || ''}`.toLowerCase()
  return str.includes('trường sa') || str.includes('truong sa') || str.includes('spratly') || str.includes('nam yết') || str.includes('trường-sa')
}

import IucnBadge, { IUCN_COLOR } from '@/components/species/IucnBadge'

const BADGE_THEMES: Record<string, { bg: string; color: string; border: string }> = {
  cyan: { bg: 'rgba(0, 212, 184, 0.12)', color: '#008f7a', border: 'rgba(0, 212, 184, 0.3)' },
  rose: { bg: 'rgba(225, 29, 72, 0.1)', color: '#be123c', border: 'rgba(225, 29, 72, 0.25)' },
  amber: { bg: 'rgba(217, 119, 6, 0.1)', color: '#b45309', border: 'rgba(217, 119, 6, 0.25)' },
  emerald: { bg: 'rgba(5, 150, 105, 0.1)', color: '#047857', border: 'rgba(5, 150, 105, 0.25)' },
}

interface Props {
  collection: string // e.g. 'ca-bien'
  initialVol?: number
  initialGroup?: string
}

export default function SpeciesGrid({ collection, initialVol = 1, initialGroup }: Props) {
  const books = useMemo(() => getBooksForCollection(collection), [collection])
  const searchParams = useSearchParams()
  const router = useRouter()

  // Kiểm tra nếu có tham số chuyên đề ?group=...
  const groupParam = searchParams.get('group') ?? initialGroup
  const activeGroup = useMemo(() => groupParam ? getSpecialGroup(groupParam) : null, [groupParam])

  // Lọc phụ theo phân hạng IUCN (ALL | CR | EN | VU | NT)
  const [iucnSubFilter, setIucnSubFilter] = useState<string>('ALL')

  // Lọc phụ theo phạm vi biển đảo Hoàng Sa / Trường Sa (ALL | HS | TS | BOTH)
  const [archipelagoSubFilter, setArchipelagoSubFilter] = useState<'ALL' | 'HS' | 'TS' | 'BOTH'>('ALL')

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
  const hasRestoredScroll = useRef(false)

  // Active book object
  const activeBook = useMemo(() => {
    return books.find(b => b.id === selectedBookId) || books[0] || null
  }, [books, selectedBookId])

  // Active volume metadata
  const activeVolumeMeta = useMemo(() => {
    return activeBook?.volumes.find(v => v.volume === currentVol) || activeBook?.volumes[0] || null
  }, [activeBook, currentVol])

  // Tải dữ liệu theo chuyên đề (nếu có activeGroup) hoặc theo volume thông thường
  const loadData = useCallback(async () => {
    setStatus('loading')
    setLocalFilter('')

    let query = db
      .from('species')
      .select('id, volume, species_index, vn_name, scientific_name, authorship, biology, vn_distribution, en_distribution, vn_specimen, collection_id')
      .is('deleted_at', null)

    if (activeGroup?.id === 'hoang-sa-truong-sa') {
      // Truy vấn toàn bộ 148 loài Hoàng Sa & Trường Sa (bao gồm cả cá biển và thực vật biển)
      query = query
        .or('vn_distribution.ilike.%Hoàng Sa%,vn_distribution.ilike.%Trường Sa%,vn_distribution.ilike.%Hoàng-sa%,vn_distribution.ilike.%Trường-sa%,vn_distribution.ilike.%Nam Yết%,vn_specimen.ilike.%Hoàng-sa%,vn_specimen.ilike.%Trường-sa%,vn_name.ilike.%Trường Sa%')
        .order('volume')
        .order('species_index')
        .limit(800)
    } else if (activeGroup) {
      query = applySpeciesFilters(query, collection)
      if (activeGroup.filterType === 'families' && activeGroup.filterValues?.length) {
        query = query.in('tax_family_latin', activeGroup.filterValues)
      } else if (activeGroup.filterType === 'orders' && activeGroup.filterValues?.length) {
        query = query.in('tax_order_latin', activeGroup.filterValues)
      } else if (activeGroup.filterType === 'iucn' && activeGroup.filterValues?.length) {
        query = query.in('biology->>iucnStatus', activeGroup.filterValues)
      }
      query = query.order('vn_name').limit(800)
    } else {
      query = applySpeciesFilters(query, collection)
        .eq('volume', currentVol)
        .order('species_index')
        .limit(800)
    }

    const { data, error } = await query

    if (error || !data) {
      setStatus('error')
      return
    }

    setSpeciesList(data as SpeciesItem[])
    setStatus('ok')

    // Restore scroll position after data loads (only once, on initial mount)
    if (!hasRestoredScroll.current) {
      hasRestoredScroll.current = true
      const saved = sessionStorage.getItem(SCROLL_KEY)
      if (saved) {
        sessionStorage.removeItem(SCROLL_KEY)
        requestAnimationFrame(() => window.scrollTo(0, parseInt(saved)))
      }
    }
  }, [collection, activeGroup, currentVol])

  useEffect(() => {
    loadData()
  }, [loadData])

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

  // Handle clearing special group filter to return to standard book browsing
  const handleClearGroup = () => {
    const params = new URLSearchParams(searchParams.toString())
    params.delete('group')
    router.replace(`?${params.toString()}`, { scroll: false })
  }

  // In-memory filter for the list
  const filteredSpecies = useMemo(() => {
    let list = speciesList
    if (activeGroup?.id === 'nguy-cap' && iucnSubFilter !== 'ALL') {
      list = list.filter(sp => (sp.biology?.iucnStatus || '').toUpperCase() === iucnSubFilter)
    }
    if (activeGroup?.id === 'hoang-sa-truong-sa') {
      if (archipelagoSubFilter === 'HS') {
        list = list.filter(isHSLocation)
      } else if (archipelagoSubFilter === 'TS') {
        list = list.filter(isTSLocation)
      } else if (archipelagoSubFilter === 'BOTH') {
        list = list.filter(s => isHSLocation(s) && isTSLocation(s))
      }
    }
    if (!localFilter.trim()) return list
    const q = localFilter.toLowerCase().trim()
    return list.filter(sp =>
      (sp.vn_name && sp.vn_name.toLowerCase().includes(q)) ||
      (sp.scientific_name && sp.scientific_name.toLowerCase().includes(q)) ||
      String(sp.species_index).includes(q)
    )
  }, [speciesList, localFilter, activeGroup, iucnSubFilter, archipelagoSubFilter])

  return (
    <div className="book-browser-container">
      {/* ─── CHẾ ĐỘ 1: XEM THEO CHUYÊN ĐỀ SINH THÁI & BẢO TỒN ─── */}
      {activeGroup ? (
        <section
          className={`special-group-banner special-group-banner--${activeGroup.badgeColor}`}
          aria-label="Chuyên đề đang xem"
          style={{
            border: activeGroup.badgeColor === 'rose'
              ? '1.5px solid rgba(225, 29, 72, 0.25)'
              : activeGroup.badgeColor === 'amber'
              ? '1.5px solid rgba(217, 119, 6, 0.25)'
              : '1.5px solid var(--color-cyan-border, rgba(0, 212, 184, 0.3))',
            borderRadius: '16px',
            padding: '24px 24px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
            background: activeGroup.badgeColor === 'rose'
              ? 'linear-gradient(135deg, rgba(225, 29, 72, 0.06) 0%, rgba(244, 63, 94, 0.02) 100%)'
              : activeGroup.badgeColor === 'amber'
              ? 'linear-gradient(135deg, rgba(217, 119, 6, 0.08) 0%, rgba(245, 158, 11, 0.02) 100%)'
              : 'linear-gradient(135deg, rgba(14, 165, 233, 0.08) 0%, rgba(14, 165, 233, 0.02) 100%)',
            boxShadow: '0 4px 20px -2px rgba(0, 0, 0, 0.04)',
            marginBottom: '16px',
            position: 'relative',
          }}
        >
          <div
            className="sgb-header-row"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '12px',
              width: '100%',
            }}
          >
            <div className="sgb-badge-wrap">
              <span
                className={`sgb-badge sgb-badge--${activeGroup.badgeColor}`}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  borderRadius: '9999px',
                  fontSize: '0.78rem',
                  fontWeight: 800,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  background: (BADGE_THEMES[activeGroup.badgeColor] || BADGE_THEMES.cyan).bg,
                  color: (BADGE_THEMES[activeGroup.badgeColor] || BADGE_THEMES.cyan).color,
                  border: `1px solid ${(BADGE_THEMES[activeGroup.badgeColor] || BADGE_THEMES.cyan).border}`,
                }}
              >
                <Sparkles size={14} />
                {activeGroup.badge}
              </span>
            </div>
            <button
              type="button"
              className="sgb-clear-btn"
              onClick={handleClearGroup}
              aria-label="Quay lại danh mục theo sách"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                background: 'var(--color-paper-2, #ffffff)',
                border: '1px solid var(--color-rule, #e2e8f0)',
                color: 'var(--color-ink-2, #475569)',
                padding: '6px 14px',
                borderRadius: '9999px',
                fontSize: '0.82rem',
                fontWeight: 600,
                cursor: 'pointer',
                outline: 'none',
                appearance: 'none',
                WebkitAppearance: 'none',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                transition: 'all 0.15s ease-out',
              }}
            >
              <ArrowLeft size={14} />
              <span>Quay lại xem theo sách gốc</span>
            </button>
          </div>
          <h1 className="sgb-title">{activeGroup.title}</h1>
          <p className="sgb-desc">{activeGroup.subTitle}</p>

          {/* Bộ lọc nhanh theo phân hạng Danh lục đỏ IUCN */}
          {activeGroup.id === 'nguy-cap' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginTop: '16px', paddingTop: '16px', borderTop: '1px dashed var(--color-rule)' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--color-ink-3)', marginRight: '4px' }}>
                Sách Đỏ IUCN:
              </span>
              <button
                type="button"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  fontWeight: iucnSubFilter === 'ALL' ? 700 : 500,
                  background: iucnSubFilter === 'ALL' ? 'var(--color-navy-raw)' : 'var(--color-paper-2)',
                  color: iucnSubFilter === 'ALL' ? '#ffffff' : 'var(--color-ink)',
                  border: '1px solid var(--color-rule)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                onClick={() => setIucnSubFilter('ALL')}
              >
                Tất cả ({speciesList.length})
              </button>
              {(['CR', 'EN', 'VU', 'NT'] as const).map(code => {
                const count = speciesList.filter(s => (s.biology?.iucnStatus || '').toUpperCase() === code).length
                const isSelected = iucnSubFilter === code
                const color = IUCN_COLOR[code]
                return (
                  <button
                    key={code}
                    type="button"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontSize: '0.82rem',
                      fontWeight: isSelected ? 700 : 500,
                      background: isSelected ? `${color}25` : 'var(--color-paper-2)',
                      color: isSelected ? color : 'var(--color-ink)',
                      border: isSelected ? `2px solid ${color}` : '1px solid var(--color-rule)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                    onClick={() => setIucnSubFilter(code)}
                  >
                    <IucnBadge status={code} />
                    <span style={{ fontSize: '0.82rem', fontWeight: 600 }}>({count})</span>
                  </button>
                )
              })}
            </div>
          )}

          {/* Bộ lọc nhanh theo Hoàng Sa & Trường Sa */}
          {activeGroup.id === 'hoang-sa-truong-sa' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginTop: '16px', paddingTop: '16px', borderTop: '1px dashed var(--color-rule)' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--color-ink-3)', marginRight: '4px' }}>
                Phạm vi biển đảo:
              </span>
              <button
                type="button"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  fontWeight: archipelagoSubFilter === 'ALL' ? 700 : 500,
                  background: archipelagoSubFilter === 'ALL' ? 'var(--color-navy-raw)' : 'var(--color-paper-2)',
                  color: archipelagoSubFilter === 'ALL' ? '#ffffff' : 'var(--color-ink)',
                  border: '1px solid var(--color-rule)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                onClick={() => setArchipelagoSubFilter('ALL')}
              >
                Tất cả ({speciesList.length})
              </button>
              <button
                type="button"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  fontWeight: archipelagoSubFilter === 'HS' ? 700 : 500,
                  background: archipelagoSubFilter === 'HS' ? '#b45309' : 'var(--color-paper-2)',
                  color: archipelagoSubFilter === 'HS' ? '#ffffff' : '#b45309',
                  border: archipelagoSubFilter === 'HS' ? '1px solid #b45309' : '1px solid var(--color-rule)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                onClick={() => setArchipelagoSubFilter('HS')}
              >
                🏝️ Hoàng Sa ({speciesList.filter(isHSLocation).length})
              </button>
              <button
                type="button"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  fontWeight: archipelagoSubFilter === 'TS' ? 700 : 500,
                  background: archipelagoSubFilter === 'TS' ? '#0369a1' : 'var(--color-paper-2)',
                  color: archipelagoSubFilter === 'TS' ? '#ffffff' : '#0369a1',
                  border: archipelagoSubFilter === 'TS' ? '1px solid #0369a1' : '1px solid var(--color-rule)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                onClick={() => setArchipelagoSubFilter('TS')}
              >
                🌊 Trường Sa ({speciesList.filter(isTSLocation).length})
              </button>
              <button
                type="button"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  fontWeight: archipelagoSubFilter === 'BOTH' ? 700 : 500,
                  background: archipelagoSubFilter === 'BOTH' ? '#047857' : 'var(--color-paper-2)',
                  color: archipelagoSubFilter === 'BOTH' ? '#ffffff' : '#047857',
                  border: archipelagoSubFilter === 'BOTH' ? '1px solid #047857' : '1px solid var(--color-rule)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                onClick={() => setArchipelagoSubFilter('BOTH')}
              >
                ⭐ Cả 2 quần đảo ({speciesList.filter(s => isHSLocation(s) && isTSLocation(s)).length})
              </button>
            </div>
          )}
        </section>
      ) : (
        /* ─── CHẾ ĐỘ 2: XEM THEO ĐẦU SÁCH & TẬP TÀI LIỆU GỐC ─── */
        <>
          {/* 1. BỘ CHỌN ĐẦU SÁCH */}
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

          {/* 2. DANH SÁCH TẬP CỦA ĐẦU SÁCH ĐÃ CHỌN */}
          {activeBook && activeBook.volumes.length > 1 && (
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
                        <div className="vft-header">
                          <span className="vft-roman">TẬP {v.roman}</span>
                          <span className="vft-count">{v.speciesCount} loài</span>
                        </div>
                        <div className="vft-body">
                          <div className="vft-title">{v.title}</div>
                          {v.subTitle && <div className="vft-sub">{v.subTitle}</div>}
                        </div>
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
        </>
      )}

      {/* ─── 3. BẢNG DANH SÁCH LOÀI DẠNG LIST (SIÊU NHẸ, KHÔNG ẢNH) ─── */}
      <section className="species-list-section" aria-label="Danh sách loài dạng bảng">
        <div className="species-list-toolbar">
          <div className="slt-info">
            <h2 className="slt-volume-title">
              {activeGroup ? activeGroup.title : (activeVolumeMeta?.title || `Tập ${currentVol}`)}
            </h2>
            <span className="slt-counter">
              Hiển thị {filteredSpecies.length} / {speciesList.length} loài
            </span>
          </div>

          <div className="slt-filter-box">
            <Search size={16} className="slt-filter-icon" />
            <input
              type="text"
              placeholder={activeGroup ? 'Lọc trong chuyên đề này (STT, tên loài)...' : 'Lọc trong tập đang chọn (STT, tên loài)...'}
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

        {/* Trạng thái tải: Skeleton rows thanh lịch */}
        {status === 'loading' && (
          <div className="species-table-wrapper" aria-busy="true" aria-label="Đang tải danh sách loài">
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
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <tr key={i} className="species-row skeleton-row">
                    <td className="td-stt">
                      <span className="skeleton-shimmer skeleton-shimmer--stt" />
                    </td>
                    <td className="td-vn">
                      <span className="skeleton-shimmer skeleton-shimmer--title" />
                      <span className="skeleton-shimmer skeleton-shimmer--subtitle" />
                    </td>
                    <td className="td-sci desktop-only">
                      <span className="skeleton-shimmer skeleton-shimmer--full" />
                    </td>
                    <td className="td-action">
                      <span className="skeleton-shimmer skeleton-shimmer--btn" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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
                      onClick={() => { sessionStorage.setItem(SCROLL_KEY, String(window.scrollY)); router.push(`/${sp.collection_id || collection}/${sp.id}`) }}
                    >
                      <td className="td-stt">
                        <span className="stt-badge">#{sp.species_index}</span>
                      </td>
                      <td className="td-vn">
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                          <Link
                            href={`/${sp.collection_id || collection}/${sp.id}`}
                            className="species-vn-link"
                            onClick={e => { e.stopPropagation(); sessionStorage.setItem(SCROLL_KEY, String(window.scrollY)) }}
                          >
                            {sp.vn_name}
                          </Link>
                          {sp.biology?.iucnStatus && (
                            <IucnBadge status={sp.biology.iucnStatus} />
                          )}
                          {activeGroup?.id === 'hoang-sa-truong-sa' && (
                            <>
                              {isHSLocation(sp) && isTSLocation(sp) ? (
                                <span style={{ fontSize: '0.72rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(5, 150, 105, 0.1)', color: '#047857', border: '1px solid rgba(5, 150, 105, 0.25)', fontWeight: 600 }}>
                                  Hoàng Sa & Trường Sa
                                </span>
                              ) : isHSLocation(sp) ? (
                                <span style={{ fontSize: '0.72rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(217, 119, 6, 0.1)', color: '#b45309', border: '1px solid rgba(217, 119, 6, 0.25)', fontWeight: 600 }}>
                                  Hoàng Sa
                                </span>
                              ) : (
                                <span style={{ fontSize: '0.72rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(2, 132, 199, 0.1)', color: '#0284c7', border: '1px solid rgba(2, 132, 199, 0.25)', fontWeight: 600 }}>
                                  Trường Sa
                                </span>
                              )}
                              {sp.collection_id === 'thuc-vat-bien' && (
                                <span style={{ fontSize: '0.72rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.1)', color: '#059669', border: '1px solid rgba(16, 185, 129, 0.25)', fontWeight: 600 }}>
                                  Rong biển (PHH 1969)
                                </span>
                              )}
                            </>
                          )}
                        </div>
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

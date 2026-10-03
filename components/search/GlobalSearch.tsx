'use client'

import { useState, useRef, useCallback, useId } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Search, X } from 'lucide-react'
import { db } from '@/lib/supabase-browser'
import { searchSpecies, speciesHref, resultsHref, MATCH_HINT, type SearchHit } from '@/lib/search'
import './GlobalSearch.css'

interface GlobalSearchProps {
  initialQuery?: string
  collectionId?: string
  collectionName?: string
  placeholder?: string
  className?: string
}

function getBadgeInfo(item: SearchHit) {
  switch (item.collection_id) {
    case 'thuc-vat-bien':
      return { className: 'vol-badge v-plant', label: 'Thực vật' }
    case 'giap-xac':
      return { className: 'vol-badge v-crustacean', label: 'Giáp xác' }
    case 'san-ho':
      return { className: 'vol-badge v-coral', label: 'San hô' }
    case 'than-mem':
      return { className: 'vol-badge v-mollusk', label: 'Thân mềm' }
    case 'da-gai':
      return { className: 'vol-badge v-echinoderm', label: 'Da gai' }
    case 'bo-sat-bien':
    case 'ran-bien': {
      const reptileLabel = item.volume === 2 ? 'Rùa biển' : item.volume === 3 ? 'Cá sấu' : 'Rắn biển'
      return { className: 'vol-badge v-reptile', label: reptileLabel }
    }
    case 'sinh-vat-doc':
      return { className: 'vol-badge v-toxic', label: 'Độc biển' }
    default:
      return { className: `vol-badge v${item.volume || 1}`, label: item.volume ? `Tập ${item.volume}` : 'Cá biển' }
  }
}

export default function GlobalSearch({
  initialQuery = '',
  collectionId,
  collectionName,
  placeholder,
  className = '',
}: GlobalSearchProps) {
  const router = useRouter()
  const listId = useId()
  const [query, setQuery] = useState(initialQuery)
  const [results, setResults] = useState<SearchHit[]>([])
  const [status, setStatus] = useState<'idle' | 'loading' | 'empty' | 'error'>('idle')
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState(-1)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  // ponytail: stale-response guard — only the latest request may write state
  const seq = useRef(0)
  // ponytail: flag prevents onBlur closing dropdown before touch navigation fires
  const clickingResult = useRef(false)

  const total = results[0] ? Number(results[0].total) : 0
  // option indexes: 0..results.length-1 = species, results.length = "xem tất cả" footer
  const showFooter = status === 'idle' && results.length > 0
  const optionId = (i: number) => `${listId}-opt-${i}`

  const doSearch = useCallback(async (q: string) => {
    const mine = ++seq.current
    setStatus('loading')
    try {
      // RPC: accent-insensitive, ranked, matches vn_name / alt names / en name / scientific name
      const data = await searchSpecies(db, q, { collection: collectionId, limit: 8 })
      if (mine !== seq.current) return
      setResults(data)
      setActive(-1)
      setStatus(data.length === 0 ? 'empty' : 'idle')
    } catch {
      if (mine === seq.current) setStatus('error')
    }
  }, [collectionId])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setQuery(val)
    if (timer.current) clearTimeout(timer.current)
    if (val.trim().length < 2) {
      seq.current++
      setOpen(false)
      setStatus('idle')
      return
    }
    setOpen(true)
    timer.current = setTimeout(() => doSearch(val.trim()), 280)
  }

  const handleClear = () => {
    seq.current++
    setQuery('')
    setResults([])
    setOpen(false)
    setStatus('idle')
  }

  const goAll = () => {
    const q = query.trim()
    if (q.length < 2) return
    if (timer.current) clearTimeout(timer.current)
    setOpen(false)
    router.push(resultsHref(q, collectionId))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    const count = results.length + (showFooter ? 1 : 0)
    if (e.key === 'Escape') {
      setOpen(false)
    } else if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && open && count > 0) {
      e.preventDefault()
      setActive(a => (e.key === 'ArrowDown' ? (a + 1) % count : (a - 1 + count) % count))
    } else if (e.key === 'Enter') {
      e.preventDefault()
      const hit = results[active]
      if (open && hit) {
        setOpen(false)
        router.push(speciesHref(hit))
      } else {
        goAll()
      }
    }
  }

  const inputId = collectionId ? `search-${collectionId}` : 'globalSearch'
  const defaultPlaceholder = collectionName
    ? `Tìm kiếm trong ${collectionName} (tên Việt, tên gọi khác, tên khoa học)...`
    : 'Tìm theo tên Việt, tên gọi khác, tên khoa học...'

  return (
    <div
      className={`search-wrapper ${className} ${open ? 'is-open' : ''}`.trim()}
      style={{ zIndex: open ? 1000 : 50, position: 'relative', overflow: 'visible' }}
      onBlur={(e) => {
        // Only close if focus left the wrapper AND we're not mid-tap on a result
        if (!e.currentTarget.contains(e.relatedTarget) && !clickingResult.current) {
          setOpen(false)
        }
      }}
    >
      <div className="search-input-container">
        <Search size={18} className="search-input-icon" aria-hidden="true" />
        <input
          type="text"
          id={inputId}
          className="search-input"
          placeholder={placeholder || defaultPlaceholder}
          autoComplete="off"
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          aria-activedescendant={open && active >= 0 ? optionId(active) : undefined}
          value={query}
          onChange={handleChange}
          onFocus={() => query.trim().length >= 2 && results.length > 0 && setOpen(true)}
          onKeyDown={handleKeyDown}
        />
        {query && (
          <button
            type="button"
            className="search-clear-btn"
            onClick={handleClear}
            aria-label="Xóa từ khóa tìm kiếm"
          >
            <X size={15} aria-hidden="true" />
          </button>
        )}
      </div>

      {open && (
        <div
          id={listId}
          role="listbox"
          className="search-results active"
          style={{ zIndex: 99999, position: 'absolute', top: 'calc(100% + 6px)', left: 0, right: 0 }}
        >
          {status === 'loading' && (
            <div className="search-state-msg">Đang tìm kiếm...</div>
          )}
          {status === 'error' && (
            <div className="search-state-msg search-state-msg--error">Lỗi kết nối. Thử lại sau.</div>
          )}
          {status === 'empty' && (
            <div className="search-state-msg">
              Không tìm thấy loài nào phù hợp trong {collectionName ? `danh mục ${collectionName}` : 'hệ thống'}.
            </div>
          )}
          {status === 'idle' && results.map((item, i) => {
            const badge = getBadgeInfo(item)
            const hint = MATCH_HINT[item.matched]
            return (
              <Link
                key={item.id}
                id={optionId(i)}
                role="option"
                aria-selected={active === i}
                href={speciesHref(item)}
                className={`result-item${active === i ? ' is-active' : ''}`}
                onPointerDown={() => { clickingResult.current = true }}
                onClick={() => {
                  clickingResult.current = false
                  setOpen(false)
                }}
              >
                <div className="ri-info">
                  <div className="ri-name">{item.vn_name || item.scientific_name}</div>
                  <div className="ri-sci">
                    {item.scientific_name} {item.authorship || ''}
                    {hint && <span className="ri-hint"> · {hint}</span>}
                  </div>
                </div>
                <span className={badge.className}>
                  {badge.label}
                </span>
              </Link>
            )
          })}
          {showFooter && (
            <Link
              id={optionId(results.length)}
              role="option"
              aria-selected={active === results.length}
              href={resultsHref(query.trim(), collectionId)}
              className={`result-item result-item--all${active === results.length ? ' is-active' : ''}`}
              onPointerDown={() => { clickingResult.current = true }}
              onClick={() => {
                clickingResult.current = false
                setOpen(false)
              }}
            >
              Xem tất cả {total} kết quả
            </Link>
          )}
        </div>
      )}
    </div>
  )
}

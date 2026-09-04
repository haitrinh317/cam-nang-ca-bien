'use client'

import { useState, useRef, useCallback } from 'react'
import Link from 'next/link'
import { db } from '@/lib/supabase-browser'

interface SearchResult {
  id: string
  volume: number
  vn_name: string
  scientific_name: string
  authorship: string | null
  collection_id: string
}

export default function GlobalSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [status, setStatus] = useState<'idle' | 'loading' | 'empty' | 'error'>('idle')
  const [open, setOpen] = useState(false)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  // ponytail: flag prevents onBlur closing dropdown before touch navigation fires
  const clickingResult = useRef(false)

  const doSearch = useCallback(async (q: string) => {
    setStatus('loading')
    // ponytail: sanitize to prevent PostgREST filter injection (same as API route)
    const safe = q.replace(/[%_(),.]/g, '').trim().slice(0, 100)
    if (!safe) { setStatus('idle'); return }
    const { data, error } = await db
      .from('species')
      .select('id, volume, vn_name, scientific_name, authorship, collection_id')
      .is('deleted_at', null)
      .or(`vn_name.ilike.%${safe}%,scientific_name.ilike.%${safe}%,en_common_name.ilike.%${safe}%,vn_alternate_names.ilike.%${safe}%`)
      .order('volume')
      .limit(12)

    if (error) { setStatus('error'); return }
    setResults(data || [])
    setStatus(data?.length === 0 ? 'empty' : 'idle')
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setQuery(val)
    if (timer.current) clearTimeout(timer.current)
    if (val.trim().length < 2) {
      setOpen(false)
      setStatus('idle')
      return
    }
    setOpen(true)
    timer.current = setTimeout(() => doSearch(val.trim()), 280)
  }

  return (
    <div
      className={`search-wrapper${open ? ' is-open' : ''}`}
      style={{ zIndex: open ? 1000 : 50 }}
      onBlur={(e) => {
        // Only close if focus left the wrapper AND we're not mid-tap on a result
        if (!e.currentTarget.contains(e.relatedTarget) && !clickingResult.current) {
          setOpen(false)
        }
      }}
    >
      <div className="search-input-container">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0 }}>
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          id="globalSearch"
          className="search-input"
          placeholder="Tìm kiếm theo Tên Việt Nam, Tên khoa học..."
          autoComplete="off"
          value={query}
          onChange={handleChange}
          onFocus={() => query.length >= 2 && setOpen(true)}
        />
      </div>

      {open && (
        <div id="searchResults" className="search-results active">
          {status === 'loading' && (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--color-muted)' }}>Đang tìm kiếm...</div>
          )}
          {status === 'error' && (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: '#f87171' }}>Lỗi kết nối. Thử lại sau.</div>
          )}
          {status === 'empty' && (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--color-muted)' }}>Không tìm thấy loài nào phù hợp.</div>
          )}
          {status === 'idle' && results.map(item => (
            <Link
              key={item.id}
              href={`/${item.collection_id || 'ca-bien'}/${item.id}`}
              className="result-item"
              onPointerDown={() => { clickingResult.current = true }}
              onClick={() => {
                clickingResult.current = false
                setOpen(false)
              }}
            >
              <div>
                <div className="ri-name">{item.vn_name}</div>
                <div className="ri-sci">{item.scientific_name} {item.authorship || ''}</div>
              </div>
              <span className={`vol-badge ${item.collection_id === 'thuc-vat-bien' ? 'v-plant' : `v${item.volume}`}`}>
                {item.collection_id === 'thuc-vat-bien' ? 'Thực vật' : `Tập ${item.volume}`}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

import '@/styles/search-results.css'
import Link from 'next/link'
import type { Metadata } from 'next'
import { Search } from 'lucide-react'
import GlobalSearch from '@/components/search/GlobalSearch'
import FilterPanel from '@/components/search/FilterPanel'
import IucnBadge from '@/components/species/IucnBadge'
import { createServerClient } from '@/lib/supabase-server'
import { STATIC_COLLECTIONS } from '@/lib/collection-registry'
import {
  searchSpecies, searchCounts, searchFacets, speciesHref, resultsHref, parseFilters, hasFilters, MATCH_HINT, HABITAT_LABEL, REGION_LABEL,
} from '@/lib/search'

const PAGE_SIZE = 24

interface Props {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}

export const metadata: Metadata = {
  title: 'Kết quả tìm kiếm',
  robots: { index: false, follow: true },
}

const collectionName = (id: string) =>
  STATIC_COLLECTIONS.find(c => c.id === id || c.slug === id)?.nameVn ?? id

const fmtDepth = (min: number | null, max: number | null) =>
  max === null ? '—' : min === null ? `đến ${max} m` : min === max ? `${max} m` : `${min}–${max} m`

export default async function SearchResultsPage({ searchParams }: Props) {
  const sp = await searchParams
  const one = (v?: string | string[]) => (Array.isArray(v) ? v[0] : v)
  const q = (one(sp.q) ?? '').trim().slice(0, 100)
  const c = one(sp.c) && STATIC_COLLECTIONS.some(x => x.id === one(sp.c)) ? one(sp.c)! : null
  const page = Math.max(1, parseInt(one(sp.page) ?? '1', 10) || 1)
  const filters = parseFilters(sp)
  const filtered = hasFilters(filters)
  // Chế độ duyệt: không gõ chữ nhưng có phân hệ/bộ lọc (vd mở từ trang phân hệ)
  const browse = q.length === 0 && (filtered || c !== null)
  const tooShort = !browse && q.length < 2

  let hits: Awaited<ReturnType<typeof searchSpecies>> = []
  let counts: Awaited<ReturnType<typeof searchCounts>> = []
  let facets: Awaited<ReturnType<typeof searchFacets>> = { iucn: new Map(), habitat: new Map(), region: new Map(), iucnMissing: 0 }
  let extra = new Map<string, { iucn_code: string | null; depth_min: number | null; depth_max: number | null; max_length_cm: number | null; habitat_tags: string[] | null; region_tags: string[] | null }>()
  let failed = false
  if (!tooShort) {
    try {
      const db = createServerClient()
      ;[hits, counts, facets] = await Promise.all([
        searchSpecies(db, q, { collection: c, filters, limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE }),
        searchCounts(db, q, filters),
        searchFacets(db, q, c, filters),
      ])
      // Mã IUCN/độ sâu/kích thước/môi trường/vùng không nằm trong kết quả RPC -> tra thêm theo id (tối đa 24 dòng)
      if (hits.length) {
        const { data } = await db.from('species').select('id,iucn_code,depth_min,depth_max,max_length_cm,habitat_tags,region_tags').in('id', hits.map(h => h.id))
        extra = new Map((data ?? []).map(r => [r.id as string, r]))
      }
    } catch {
      failed = true
    }
  }

  const grandTotal = counts.reduce((s, x) => s + Number(x.total), 0)
  const total = hits[0] ? Number(hits[0].total) : 0
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const pageHref = (p: number) => resultsHref(q, c, filters, p)
  const scope = c ? ` trong ${collectionName(c)}` : ''

  return (
    <main className="sr-page">
      <div className="sr-container">
        <h1 className="sr-title">Kết quả tìm kiếm</h1>
        <GlobalSearch key={q} initialQuery={q} collectionId={c ?? undefined} collectionName={c ? collectionName(c) : undefined} />

        {tooShort && (
          <p className="sr-note">Nhập ít nhất 2 ký tự để tìm theo tên Việt, tên gọi khác, tên tiếng Anh hoặc tên khoa học.</p>
        )}
        {failed && <p className="sr-note sr-note--error">Không kết nối được dữ liệu. Vui lòng thử lại sau.</p>}

        {!tooShort && !failed && (
          <div className="sr-layout">
            <aside className="sr-aside">
              <FilterPanel q={q} collection={c} filters={filters} facets={facets} />
            </aside>
            <div className="sr-main">
            <nav className="sr-chips" aria-label="Lọc theo phân hệ">
              <Link href={resultsHref(q, null, filters)} className={`sr-chip${!c ? ' is-active' : ''}`} aria-current={!c ? 'true' : undefined}>
                Tất cả <span>{grandTotal}</span>
              </Link>
              {counts.map(x => (
                <Link
                  key={x.collection_id}
                  href={resultsHref(q, x.collection_id, filters)}
                  className={`sr-chip${c === x.collection_id ? ' is-active' : ''}`}
                  aria-current={c === x.collection_id ? 'true' : undefined}
                >
                  {collectionName(x.collection_id)} <span>{x.total}</span>
                </Link>
              ))}
            </nav>

            <p className="sr-summary" role="status">
              {total > 0
                ? <>{total} kết quả{q ? <> cho “<strong>{q}</strong>”</> : ''}{scope}{filtered ? ' (đã lọc)' : ''}</>
                : <>Không tìm thấy loài nào{q ? <> cho “<strong>{q}</strong>”</> : ''}{scope}{filtered ? ' với bộ lọc hiện tại' : ''}.</>}
            </p>

            {total === 0 && c && grandTotal > 0 && (
              <p className="sr-note">
                Có {grandTotal} kết quả ở phân hệ khác. <Link href={resultsHref(q, null, filters)}>Xem tất cả phân hệ</Link>
              </p>
            )}
            {total === 0 && !c && (
              <p className="sr-note">
                <Search size={16} aria-hidden="true" /> Thử bỏ bớt từ khóa hoặc nới bộ lọc; có thể dùng tên khoa học / tên tiếng Anh.
              </p>
            )}

            <ul className="sr-list">
              {hits.map(h => {
                const hint = MATCH_HINT[h.matched]
                const x = extra.get(h.id)
                const facts = x ? [
                  filters.dmin !== undefined || filters.dmax !== undefined ? `Sâu ${fmtDepth(x.depth_min, x.depth_max)}` : '',
                  filters.lmin !== undefined || filters.lmax !== undefined ? `Dài tối đa ${x.max_length_cm ?? '—'} cm` : '',
                  x.region_tags?.length || filters.region.length ? `Vùng: ${(x.region_tags ?? []).map(t => REGION_LABEL[t] ?? t).join(', ') || '—'}` : '',
                  x.habitat_tags?.length || filters.habitat.length ? `Môi trường: ${(x.habitat_tags ?? []).map(t => HABITAT_LABEL[t] ?? t).join(', ') || '—'}` : '',
                ].filter(Boolean).join(' · ') : ''
                return (
                  <li key={h.id}>
                    <Link href={speciesHref(h)} className="sr-item">
                      <span className="sr-item-name">
                        {h.vn_name || h.scientific_name}
                        <IucnBadge status={x?.iucn_code} className="sr-iucn" />
                      </span>
                      <span className="sr-item-sci">{h.scientific_name} {h.authorship || ''}</span>
                      {facts && <span className="sr-item-facts">{facts}</span>}
                      <span className="sr-item-meta">
                        <span className="sr-tag">{collectionName(h.collection_id)}</span>
                        {hint && <span className="sr-hint">{hint}</span>}
                      </span>
                    </Link>
                  </li>
                )
              })}
            </ul>

            {pages > 1 && (
              <nav className="sr-pager" aria-label="Phân trang">
                {page > 1 ? <Link href={pageHref(page - 1)} rel="prev">Trang trước</Link> : <span />}
                <span>Trang {page} / {pages}</span>
                {page < pages ? <Link href={pageHref(page + 1)} rel="next">Trang sau</Link> : <span />}
              </nav>
            )}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

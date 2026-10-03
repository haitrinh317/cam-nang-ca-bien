import '@/styles/search-results.css'
import Link from 'next/link'
import type { Metadata } from 'next'
import { Search } from 'lucide-react'
import GlobalSearch from '@/components/search/GlobalSearch'
import { createServerClient } from '@/lib/supabase-server'
import { STATIC_COLLECTIONS } from '@/lib/collection-registry'
import { searchSpecies, searchCounts, speciesHref, resultsHref, MATCH_HINT } from '@/lib/search'

const PAGE_SIZE = 24

interface Props {
  searchParams: Promise<{ q?: string; c?: string; page?: string }>
}

export const metadata: Metadata = {
  title: 'Kết quả tìm kiếm',
  robots: { index: false, follow: true },
}

const collectionName = (id: string) =>
  STATIC_COLLECTIONS.find(c => c.id === id || c.slug === id)?.nameVn ?? id

export default async function SearchResultsPage({ searchParams }: Props) {
  const sp = await searchParams
  const q = (sp.q ?? '').trim().slice(0, 100)
  const c = sp.c && STATIC_COLLECTIONS.some(x => x.id === sp.c) ? sp.c : null
  const page = Math.max(1, parseInt(sp.page ?? '1', 10) || 1)
  const tooShort = q.length < 2

  let hits: Awaited<ReturnType<typeof searchSpecies>> = []
  let counts: Awaited<ReturnType<typeof searchCounts>> = []
  let failed = false
  if (!tooShort) {
    try {
      const db = createServerClient()
      ;[hits, counts] = await Promise.all([
        searchSpecies(db, q, { collection: c, limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE }),
        searchCounts(db, q),
      ])
    } catch {
      failed = true
    }
  }

  const grandTotal = counts.reduce((s, x) => s + Number(x.total), 0)
  const total = hits[0] ? Number(hits[0].total) : 0
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const pageHref = (p: number) => `${resultsHref(q, c)}${p > 1 ? `&page=${p}` : ''}`

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
          <>
            <nav className="sr-chips" aria-label="Lọc theo phân hệ">
              <Link href={resultsHref(q)} className={`sr-chip${!c ? ' is-active' : ''}`} aria-current={!c ? 'true' : undefined}>
                Tất cả <span>{grandTotal}</span>
              </Link>
              {counts.map(x => (
                <Link
                  key={x.collection_id}
                  href={resultsHref(q, x.collection_id)}
                  className={`sr-chip${c === x.collection_id ? ' is-active' : ''}`}
                  aria-current={c === x.collection_id ? 'true' : undefined}
                >
                  {collectionName(x.collection_id)} <span>{x.total}</span>
                </Link>
              ))}
            </nav>

            <p className="sr-summary" role="status">
              {total > 0
                ? <>{total} kết quả cho “<strong>{q}</strong>”{c ? ` trong ${collectionName(c)}` : ''}</>
                : <>Không tìm thấy loài nào cho “<strong>{q}</strong>”{c ? ` trong ${collectionName(c)}` : ''}.</>}
            </p>

            {total === 0 && c && grandTotal > 0 && (
              <p className="sr-note">
                Có {grandTotal} kết quả ở phân hệ khác. <Link href={resultsHref(q)}>Xem tất cả phân hệ</Link>
              </p>
            )}
            {total === 0 && !c && (
              <p className="sr-note">
                <Search size={16} aria-hidden="true" /> Thử bỏ bớt từ khóa, hoặc dùng tên khoa học / tên tiếng Anh.
              </p>
            )}

            <ul className="sr-list">
              {hits.map(h => {
                const hint = MATCH_HINT[h.matched]
                return (
                  <li key={h.id}>
                    <Link href={speciesHref(h)} className="sr-item">
                      <span className="sr-item-name">{h.vn_name || h.scientific_name}</span>
                      <span className="sr-item-sci">{h.scientific_name} {h.authorship || ''}</span>
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
          </>
        )}
      </div>
    </main>
  )
}

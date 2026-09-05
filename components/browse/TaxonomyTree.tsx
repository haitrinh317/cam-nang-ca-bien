'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { db } from '@/lib/supabase-browser'
import { TAXONOMY_COLS, SpeciesRow, sortTaxonomyRows, buildTaxonomyTree } from '@/lib/taxonomy'

interface Props { 
  collection: string 
  initialSpecies?: SpeciesRow[]
}

// Accordion node
function TreeNode({ title, rankClass, rankName, children }: {
  title: string
  rankClass: string
  rankName: string
  children: React.ReactNode
}) {
  const [open, setOpen] = useState(false)
  return (
    <div className="tree-node" data-search={title.toLowerCase()}>
      <div className="node-header" onClick={() => setOpen(o => !o)} role="button" tabIndex={0}
        onKeyDown={e => e.key === 'Enter' && setOpen(o => !o)}>
        <div className={`node-toggle${open ? ' expanded' : ''}`}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </div>
        <span className={`rank-badge ${rankClass}`}>{rankName}</span>
        <span>{title}</span>
      </div>
      <div className={`tree-level${open ? ' expanded' : ''}`}>{children}</div>
    </div>
  )
}

export default function TaxonomyTree({ collection, initialSpecies }: Props) {
  const [allSpecies, setAllSpecies] = useState<SpeciesRow[]>(initialSpecies || [])
  const [filtered, setFiltered] = useState<SpeciesRow[] | null>(null)
  const [status, setStatus] = useState<'loading' | 'error' | 'ok'>(initialSpecies && initialSpecies.length > 0 ? 'ok' : 'loading')
  const [query, setQuery] = useState('')
  const [showTree, setShowTree] = useState(true)

  useEffect(() => {
    // Nếu đã có dữ liệu khởi tạo từ Server (ISR), không cần query client nữa
    if (initialSpecies && initialSpecies.length > 0) return

    async function load() {
      // ponytail: Supabase max-rows = 1000. Fetch 2 pages for collection.
      const [r1, r2] = await Promise.all([
        db.from('species').select(TAXONOMY_COLS).eq('collection_id', collection).is('deleted_at', null).range(0, 999),
        db.from('species').select(TAXONOMY_COLS).eq('collection_id', collection).is('deleted_at', null).range(1000, 1999),
      ])
      if (r1.error) { setStatus('error'); return }

      setAllSpecies(sortTaxonomyRows([...(r1.data || []), ...(r2.data || [])] as SpeciesRow[]))
      setStatus('ok')
    }
    load()
  }, [collection, initialSpecies])

  const handleFilter = (e: React.ChangeEvent<HTMLInputElement>) => {
    const q = e.target.value
    setQuery(q)
    if (!q.trim()) {
      setFiltered(null)
      setShowTree(true)
      return
    }
    const ql = q.toLowerCase()
    setFiltered(allSpecies.filter(sp =>
      (sp.vn_name || '').toLowerCase().includes(ql) || (sp.scientific_name || '').toLowerCase().includes(ql)
    ).slice(0, 60))
    setShowTree(false)
  }


  const ArrowRight = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--brand-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  )

  const label = (latin: string, vn: string) =>
    latin && latin !== 'Unknown' ? `${vn} (${latin})` : vn

  return (
    <>
      {/* Search filter */}
      <div className="search-input-container" style={{ maxWidth: '540px', marginBottom: 'var(--space-2xl)' }}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          id="treeFilter"
          className="search-input"
          placeholder="Lọc nhanh tên loài tiếng Việt hoặc tên khoa học..."
          autoComplete="off"
          value={query}
          onChange={handleFilter}
        />
      </div>

      {/* Search results */}
      {!showTree && (
        <div id="searchResults" className="search-results active" style={{ position: 'relative', top: 0, marginBottom: 'var(--space-xl)' }}>
          <div id="searchResultsList">
            {filtered && filtered.length === 0 ? (
              <p style={{ color: 'var(--color-muted)', padding: '2rem', textAlign: 'center' }}>Không tìm thấy loài nào phù hợp.</p>
            ) : filtered?.map(sp => (
              <Link key={sp.id} href={`/${collection}/${sp.id}`} className="species-item">
                <div>
                  <span className="sp-name">{sp.vn_name}</span>
                  <span className="sp-sci">{sp.scientific_name}</span>
                </div>
                <ArrowRight />
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Taxonomy tree */}
      <section className="taxonomy-container" id="treeContainer" aria-label="Cây phân loại" style={{ display: showTree ? '' : 'none' }}>
        {status === 'loading' && (
          <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--color-muted)' }}>
            Đang tải cây phân loại...
          </div>
        )}
        {status === 'error' && (
          <div style={{ textAlign: 'center', padding: '4rem', color: '#f87171' }}>
            Lỗi tải dữ liệu phân loại học.
          </div>
        )}
        {status === 'ok' && Object.entries(buildTaxonomyTree(allSpecies)).map(([clLatin, clData]) => (
          <TreeNode key={clLatin} title={label(clLatin, clData.vn)} rankClass="rank-class" rankName="Lớp">
            {Object.entries(clData.orders).map(([orLatin, orData]) => (
              <TreeNode key={orLatin} title={label(orLatin, orData.vn)} rankClass="rank-order" rankName="Bộ">
                {Object.entries(orData.families).map(([faLatin, faData]) => (
                  <TreeNode key={faLatin} title={label(faLatin, faData.vn)} rankClass="rank-family" rankName="Họ">
                    {Object.entries(faData.genera).map(([geLatin, geData]) => (
                      <TreeNode key={geLatin} title={label(geLatin, geData.vn)} rankClass="rank-genus" rankName="Giống">
                        {geData.species.map(sp => (
                          <Link key={sp.id} href={`/${collection}/${sp.id}`} className="species-item" data-search={`${sp.vn_name.toLowerCase()} ${sp.scientific_name.toLowerCase()}`}>
                            <div>
                              <span className="sp-name">{sp.vn_name}</span>
                              <span className="sp-sci">{sp.scientific_name}</span>
                            </div>
                            <ArrowRight />
                          </Link>
                        ))}
                      </TreeNode>
                    ))}
                  </TreeNode>
                ))}
              </TreeNode>
            ))}
          </TreeNode>
        ))}
      </section>
    </>
  )
}

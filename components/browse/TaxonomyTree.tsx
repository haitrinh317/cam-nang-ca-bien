'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { db } from '@/lib/supabase-browser'

interface SpeciesRow {
  id: string
  vn_name: string
  scientific_name: string
  tax_class_vn: string | null
  tax_class_latin: string | null
  tax_order_vn: string | null
  tax_order_latin: string | null
  tax_family_vn: string | null
  tax_family_latin: string | null
  tax_genus_vn: string | null
  tax_genus_latin: string | null
  species_index: number | null
}

interface Props { collection: string }

const COLS = 'id, vn_name, scientific_name, tax_class_vn, tax_class_latin, tax_order_vn, tax_order_latin, tax_family_vn, tax_family_latin, tax_genus_vn, tax_genus_latin, species_index'

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

export default function TaxonomyTree({ collection }: Props) {
  const [allSpecies, setAllSpecies] = useState<SpeciesRow[]>([])
  const [filtered, setFiltered] = useState<SpeciesRow[] | null>(null)
  const [status, setStatus] = useState<'loading' | 'error' | 'ok'>('loading')
  const [query, setQuery] = useState('')
  const [showTree, setShowTree] = useState(true)

  useEffect(() => {
    async function load() {
      // ponytail: Supabase max-rows = 1000. Fetch 2 pages for ~1200 rows.
      const [r1, r2] = await Promise.all([
        db.from('species').select(COLS).range(0, 999),
        db.from('species').select(COLS).range(1000, 1999),
      ])
      if (r1.error) { setStatus('error'); return }

      const data = [...(r1.data || []), ...(r2.data || [])] as SpeciesRow[]
      data.sort((a, b) => {
        const cl = (a.tax_class_latin || '').localeCompare(b.tax_class_latin || '')
        if (cl !== 0) return cl
        const or = (a.tax_order_latin || '').localeCompare(b.tax_order_latin || '')
        if (or !== 0) return or
        const fa = (a.tax_family_latin || '').localeCompare(b.tax_family_latin || '')
        if (fa !== 0) return fa
        return (a.species_index || 0) - (b.species_index || 0)
      })

      setAllSpecies(data)
      setStatus('ok')
    }
    load()
  }, [])

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

  // Build tree from flat rows
  type GenusNode = { vn: string; species: SpeciesRow[] }
  type FamilyNode = { vn: string; genera: Record<string, GenusNode> }
  type OrderNode = { vn: string; families: Record<string, FamilyNode> }
  type ClassNode = { vn: string; orders: Record<string, OrderNode> }
  type Tree = Record<string, ClassNode>

  function buildTree(rows: SpeciesRow[]) {
    const tree: Tree = {}
    rows.forEach(sp => {
      const cl  = sp.tax_class_latin  || 'Unknown'
      const clv = sp.tax_class_vn     || cl
      const or  = sp.tax_order_latin  || 'Unknown'
      const orv = sp.tax_order_vn     || or
      const fa  = sp.tax_family_latin || 'Unknown'
      const fav = sp.tax_family_vn    || fa
      const ge  = sp.tax_genus_latin  || 'Unknown'
      const gev = sp.tax_genus_vn     || ge

      if (!tree[cl]) tree[cl] = { vn: clv, orders: {} }
      if (!tree[cl].orders[or]) tree[cl].orders[or] = { vn: orv, families: {} }
      if (!tree[cl].orders[or].families[fa]) tree[cl].orders[or].families[fa] = { vn: fav, genera: {} }
      if (!tree[cl].orders[or].families[fa].genera[ge]) tree[cl].orders[or].families[fa].genera[ge] = { vn: gev, species: [] }
      tree[cl].orders[or].families[fa].genera[ge].species.push(sp)
    })
    return tree
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
        {status === 'ok' && Object.entries(buildTree(allSpecies)).map(([clLatin, clData]) => (
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

'use client'

import { useEffect, useState, useMemo } from 'react'
import Link from 'next/link'
import { Dna, BookOpen, Search, ChevronRight, Info } from 'lucide-react'
import { db } from '@/lib/supabase-browser'
import {
  TAXONOMY_COLS,
  SpeciesRow,
  TaxonomyMode,
  sortTaxonomyRows,
  buildTaxonomyTree,
  getTaxonomyStats
} from '@/lib/taxonomy'

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
      <div
        className="node-header"
        onClick={() => setOpen(o => !o)}
        role="button"
        tabIndex={0}
        onKeyDown={e => e.key === 'Enter' && setOpen(o => !o)}
      >
        <div className={`node-toggle${open ? ' expanded' : ''}`}>
          <ChevronRight size={16} strokeWidth={2.5} />
        </div>
        <span className={`rank-badge ${rankClass}`}>{rankName}</span>
        <span>{title}</span>
      </div>
      <div className={`tree-level${open ? ' expanded' : ''}`}>{children}</div>
    </div>
  )
}

export default function TaxonomyTree({ collection, initialSpecies }: Props) {
  const [mode, setMode] = useState<TaxonomyMode>('modern')
  const [allSpecies, setAllSpecies] = useState<SpeciesRow[]>(initialSpecies || [])
  const [filtered, setFiltered] = useState<SpeciesRow[] | null>(null)
  const [status, setStatus] = useState<'loading' | 'error' | 'ok'>(
    initialSpecies && initialSpecies.length > 0 ? 'ok' : 'loading'
  )
  const [query, setQuery] = useState('')
  const [showTree, setShowTree] = useState(true)

  useEffect(() => {
    if (initialSpecies && initialSpecies.length > 0) return

    async function load() {
      // Fetch up to 3000 rows for large collections
      const [r1, r2, r3] = await Promise.all([
        db.from('species').select(TAXONOMY_COLS).eq('collection_id', collection).is('deleted_at', null).range(0, 999),
        db.from('species').select(TAXONOMY_COLS).eq('collection_id', collection).is('deleted_at', null).range(1000, 1999),
        db.from('species').select(TAXONOMY_COLS).eq('collection_id', collection).is('deleted_at', null).range(2000, 2999),
      ])
      if (r1.error) {
        setStatus('error')
        return
      }

      setAllSpecies(sortTaxonomyRows([...(r1.data || []), ...(r2.data || []), ...(r3.data || [])] as SpeciesRow[], mode))
      setStatus('ok')
    }
    load()
  }, [collection, initialSpecies, mode])

  // Build tree based on active mode
  const currentTree = useMemo(() => {
    if (!allSpecies || allSpecies.length === 0) return {}
    return buildTaxonomyTree(allSpecies, mode)
  }, [allSpecies, mode])

  // Stats calculation
  const stats = useMemo(() => {
    return getTaxonomyStats(currentTree)
  }, [currentTree])

  const handleFilter = (e: React.ChangeEvent<HTMLInputElement>) => {
    const q = e.target.value
    setQuery(q)
    if (!q.trim()) {
      setFiltered(null)
      setShowTree(true)
      return
    }
    const ql = q.toLowerCase()
    setFiltered(
      allSpecies.filter(sp =>
        (sp.vn_name || '').toLowerCase().includes(ql) ||
        (sp.scientific_name || '').toLowerCase().includes(ql)
      ).slice(0, 60)
    )
    setShowTree(false)
  }

  const label = (latin: string, vn: string) =>
    latin && latin !== 'Unknown' ? `${vn} (${latin})` : vn

  return (
    <>
      {/* Search filter */}
      <div className="search-input-container" style={{ maxWidth: '580px', marginBottom: 'var(--space-xl)' }}>
        <Search size={20} strokeWidth={2} aria-hidden="true" />
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

      {/* Dual Taxonomy Segmented Toggle & Context Banner */}
      <div className="taxonomy-controls">
        <div className="taxonomy-toggle-wrapper">
          <div className="taxonomy-segmented-switch" role="tablist" aria-label="Chế độ phân loại">
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'modern'}
              className={`taxonomy-switch-btn ${mode === 'modern' ? 'active' : ''}`}
              onClick={() => setMode('modern')}
            >
              <Dna size={16} strokeWidth={2.2} />
              <span>Chuẩn Hiện Đại (WoRMS 2026)</span>
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'classic'}
              className={`taxonomy-switch-btn ${mode === 'classic' ? 'active--classic' : ''}`}
              onClick={() => setMode('classic')}
            >
              <BookOpen size={16} strokeWidth={2.2} />
              <span>Sách Gốc (Viện Hải dương học)</span>
            </button>
          </div>

          <div className="taxonomy-stats-pill">
            <span>
              <strong>{stats.orderCount}</strong> Bộ · <strong>{stats.familyCount}</strong> Họ · <strong>{stats.speciesCount}</strong> Loài
            </span>
          </div>
        </div>

        {/* Scientific Context Banner */}
        {mode === 'modern' ? (
          <div className="taxonomy-context-banner">
            <Info size={18} strokeWidth={2} style={{ color: 'var(--brand-primary)' }} />
            <div>
              <strong>Hệ thống Phát sinh Chủng loài Phân tử (WoRMS 2026 / Nelson et al. 2016):</strong> Siêu bộ Cá Vược <em>Perciformes</em> truyền thống đã được giải thể và phân tách thành hơn 15 bộ độc lập (như <em>Gobiiformes</em>, <em>Carangiformes</em>, <em>Acanthuriformes</em>, <em>Blenniiformes</em>, <em>Scombriformes</em>...) phản ánh chính xác tiến hóa sinh học biển thế giới.
            </div>
          </div>
        ) : (
          <div className="taxonomy-context-banner taxonomy-context-banner--classic">
            <Info size={18} strokeWidth={2} style={{ color: '#38bdf8' }} />
            <div>
              <strong>Trật tự Phân loại Học Cổ điển (Viện Hải dương học Nha Trang):</strong> Giữ nguyên vẹn 100% cấu trúc phân loại hình thái và thứ bậc theo bộ sách chuyên khảo <em>Danh mục Cá biển Việt Nam</em> (Tập I đến VI, 1990–2005) phục vụ đối chiếu số trang và tài liệu dẫn học thuật truyền thống.
            </div>
          </div>
        )}
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
                <ChevronRight size={18} strokeWidth={2} style={{ color: 'var(--brand-primary)' }} />
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
        {status === 'ok' && Object.entries(currentTree).map(([clLatin, clData]) => (
          <TreeNode key={clLatin} title={label(clLatin, clData.vn)} rankClass="rank-class" rankName="Lớp">
            {Object.entries(clData.orders).map(([orLatin, orData]) => (
              <TreeNode key={orLatin} title={label(orLatin, orData.vn)} rankClass="rank-order" rankName="Bộ">
                {Object.entries(orData.families).map(([faLatin, faData]) => (
                  <TreeNode key={faLatin} title={label(faLatin, faData.vn)} rankClass="rank-family" rankName="Họ">
                    {Object.entries(faData.genera).map(([geLatin, geData]) => (
                      <TreeNode key={geLatin} title={label(geLatin, geData.vn)} rankClass="rank-genus" rankName="Giống">
                        {geData.species.map(sp => (
                          <Link
                            key={sp.id}
                            href={`/${collection}/${sp.id}`}
                            className="species-item"
                            data-search={`${sp.vn_name.toLowerCase()} ${sp.scientific_name.toLowerCase()}`}
                          >
                            <div>
                              <span className="sp-name">{sp.vn_name}</span>
                              <span className="sp-sci">{sp.scientific_name}</span>
                            </div>
                            <ChevronRight size={18} strokeWidth={2} style={{ color: 'var(--brand-primary)' }} />
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

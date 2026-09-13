'use client'

import { useEffect, useState, useCallback, useMemo } from 'react'
import Link from 'next/link'
import { db } from '@/lib/supabase-browser'
import { 
  BookOpen, Plus, Pencil, Trash2, Eye, EyeOff, Search, 
  LayoutGrid, Table as TableIcon, ExternalLink, Compass, 
  Leaf, Fish, Anchor, Shell, Waves, X, Check, BookMarked,
  Library, Sparkles, Layers, Bookmark, ChevronLeft, ChevronRight
} from 'lucide-react'
import { STATIC_COLLECTIONS } from '@/lib/collection-registry'
import '@/styles/admin-command.css'

interface LinkOption {
  label: string
  href: string
  statsCount: string
}

interface LitSource {
  id: string
  title: string
  subtitle: string | null
  author: string
  publisher: string | null
  year: string | null
  stats_count: string | null
  pill_text: string | null
  description: string | null
  href: string
  chips: string[] | null
  icon_name: string | null
  sort_order: number
  is_visible: boolean
}

const EMPTY_FORM: Omit<LitSource, 'id'> = {
  title: '',
  subtitle: '',
  author: '',
  publisher: '',
  year: '',
  stats_count: '',
  pill_text: '',
  description: '',
  href: '',
  chips: [],
  icon_name: 'book-open',
  sort_order: 0,
  is_visible: true,
}

const ICON_OPTIONS = [
  { id: 'fish', label: 'Cá biển', icon: Fish },
  { id: 'compass', label: 'La bàn', icon: Compass },
  { id: 'leaf', label: 'Rong biển', icon: Leaf },
  { id: 'book-open', label: 'Sách mở', icon: BookOpen },
  { id: 'anchor', label: 'Mỏ neo', icon: Anchor },
  { id: 'shell', label: 'Vỏ sò', icon: Shell },
  { id: 'waves', label: 'Sóng biển', icon: Waves },
]

const THEME_PALETTE = [
  { accentColor: '#0ea5e9', accentGrad: 'linear-gradient(90deg, #0284c7 0%, #38bdf8 100%)', iconBg: 'rgba(14, 165, 233, 0.1)' },
  { accentColor: '#14b8a6', accentGrad: 'linear-gradient(90deg, #0d9488 0%, #2dd4bf 100%)', iconBg: 'rgba(20, 184, 166, 0.1)' },
  { accentColor: '#10b981', accentGrad: 'linear-gradient(90deg, #059669 0%, #34d399 100%)', iconBg: 'rgba(16, 185, 129, 0.1)' },
  { accentColor: '#8b5cf6', accentGrad: 'linear-gradient(90deg, #7c3aed 0%, #a78bfa 100%)', iconBg: 'rgba(139, 92, 246, 0.1)' },
  { accentColor: '#f59e0b', accentGrad: 'linear-gradient(90deg, #d97706 0%, #fbbf24 100%)', iconBg: 'rgba(245, 158, 11, 0.1)' },
  { accentColor: '#ec4899', accentGrad: 'linear-gradient(90deg, #db2777 0%, #f472b6 100%)', iconBg: 'rgba(236, 72, 153, 0.1)' },
]

function renderSourceIcon(name: string | null, size = 20) {
  switch (name) {
    case 'fish': return <Fish size={size} strokeWidth={1.75} />
    case 'compass': return <Compass size={size} strokeWidth={1.75} />
    case 'leaf': return <Leaf size={size} strokeWidth={1.75} />
    case 'anchor': return <Anchor size={size} strokeWidth={1.75} />
    case 'shell': return <Shell size={size} strokeWidth={1.75} />
    case 'waves': return <Waves size={size} strokeWidth={1.75} />
    default: return <BookOpen size={size} strokeWidth={1.75} />
  }
}

type ModalTab = 'metadata' | 'link' | 'visual' | 'preview'

export default function AdminLiteraturePage() {
  const [sources, setSources] = useState<LitSource[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<LitSource | null>(null)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [chipsList, setChipsList] = useState<string[]>([])
  const [newChipInput, setNewChipInput] = useState('')
  const [linkOptions, setLinkOptions] = useState<LinkOption[]>([])
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards')
  const [searchQuery, setSearchQuery] = useState('')
  const [modalTab, setModalTab] = useState<ModalTab>('metadata')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(6)

  const loadData = useCallback(async () => {
    setLoading(true)
    const { data } = await db
      .from('literature_sources')
      .select('*')
      .order('sort_order')
    setSources((data || []) as LitSource[])
    setLoading(false)
  }, [])

  // Fetch collection/volume stats for smart dropdowns
  const loadLinkOptions = useCallback(async () => {
    const { data } = await db
      .from('species')
      .select('collection_id, volume')
      .is('deleted_at', null)

    if (!data) return

    const collMap = new Map<string, number>()
    const volMap = new Map<string, number>()
    for (const row of data) {
      const cKey = row.collection_id
      const vKey = `${row.collection_id}|${row.volume}`
      collMap.set(cKey, (collMap.get(cKey) || 0) + 1)
      volMap.set(vKey, (volMap.get(vKey) || 0) + 1)
    }

    const nameMap: Record<string, string> = {}
    STATIC_COLLECTIONS.forEach(c => { nameMap[c.id] = c.nameVn })

    const options: LinkOption[] = []

    for (const [cid, count] of collMap) {
      const name = nameMap[cid] || cid
      options.push({
        label: `${name} (toàn bộ — ${count.toLocaleString()} loài)`,
        href: `/${cid}`,
        statsCount: `${count.toLocaleString()} loài`,
      })
    }

    for (const [vKey, count] of volMap) {
      const [cid, vol] = vKey.split('|')
      const name = nameMap[cid] || cid
      options.push({
        label: `${name} — Tập ${vol} (${count.toLocaleString()} loài)`,
        href: `/${cid}?vol=${vol}`,
        statsCount: `${count.toLocaleString()} loài`,
      })
    }

    options.sort((a, b) => {
      const aIsCol = !a.href.includes('?')
      const bIsCol = !b.href.includes('?')
      if (aIsCol !== bIsCol) return aIsCol ? -1 : 1
      return a.href.localeCompare(b.href)
    })

    setLinkOptions(options)
  }, [])

  useEffect(() => {
    loadData()
    loadLinkOptions()
  }, [loadData, loadLinkOptions])

  const handleLinkSelect = (href: string) => {
    setField('href', href)
    const match = linkOptions.find(o => o.href === href)
    if (match) setField('stats_count', match.statsCount)
  }

  const openCreate = () => {
    setEditing(null)
    setForm({ ...EMPTY_FORM, sort_order: sources.length + 1 })
    setChipsList([])
    setNewChipInput('')
    setModalTab('metadata')
    setCreating(true)
  }

  const openEdit = (item: LitSource) => {
    setCreating(false)
    setEditing(item)
    setForm({
      title: item.title,
      subtitle: item.subtitle || '',
      author: item.author,
      publisher: item.publisher || '',
      year: item.year || '',
      stats_count: item.stats_count || '',
      pill_text: item.pill_text || '',
      description: item.description || '',
      href: item.href,
      chips: item.chips || [],
      icon_name: item.icon_name || 'book-open',
      sort_order: item.sort_order,
      is_visible: item.is_visible,
    })
    setChipsList(item.chips || [])
    setNewChipInput('')
    setModalTab('metadata')
  }

  const closeModal = () => {
    setEditing(null)
    setCreating(false)
  }

  const flushHomeCache = () => fetch('/api/revalidate-home', { method: 'POST' }).catch(() => {})

  const handleAddChip = () => {
    const trimmed = newChipInput.trim()
    if (!trimmed) return
    if (!chipsList.includes(trimmed)) {
      setChipsList(prev => [...prev, trimmed])
    }
    setNewChipInput('')
  }

  const handleRemoveChip = (chipToRemove: string) => {
    setChipsList(prev => prev.filter(c => c !== chipToRemove))
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    const payload = {
      ...form,
      chips: chipsList.length > 0 ? chipsList : null,
      updated_at: new Date().toISOString(),
    }

    if (creating) {
      await db.from('literature_sources').insert(payload)
    } else if (editing) {
      await db.from('literature_sources').update(payload).eq('id', editing.id)
    }

    flushHomeCache()
    setSaving(false)
    closeModal()
    loadData()
  }

  const handleDelete = async (id: string, title: string) => {
    if (!confirm(`Xác nhận xóa tài liệu "${title}" khỏi hệ thống?`)) return
    await db.from('literature_sources').delete().eq('id', id)
    flushHomeCache()
    loadData()
  }

  const toggleVisible = async (item: LitSource) => {
    await db.from('literature_sources')
      .update({ is_visible: !item.is_visible, updated_at: new Date().toISOString() })
      .eq('id', item.id)
    flushHomeCache()
    loadData()
  }

  const setField = (key: string, value: string | number | boolean) => {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  // Filter sources
  const filteredSources = useMemo(() => {
    if (!searchQuery.trim()) return sources
    const q = searchQuery.toLowerCase()
    return sources.filter(s => 
      s.title.toLowerCase().includes(q) ||
      (s.subtitle && s.subtitle.toLowerCase().includes(q)) ||
      s.author.toLowerCase().includes(q) ||
      (s.publisher && s.publisher.toLowerCase().includes(q)) ||
      (s.year && s.year.toLowerCase().includes(q))
    )
  }, [sources, searchQuery])

  // Reset to page 1 on search or page size change
  useEffect(() => {
    setPage(1)
  }, [searchQuery, pageSize])

  // Pagination calculation
  const totalItems = filteredSources.length
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize))
  const paginatedSources = useMemo(() => {
    if (pageSize >= 9999) return filteredSources
    const start = (page - 1) * pageSize
    return filteredSources.slice(start, start + pageSize)
  }, [filteredSources, page, pageSize])

  // Stats calculation
  const totalCount = sources.length
  const visibleCount = sources.filter(s => s.is_visible).length

  const isFormOpen = creating || editing !== null

  return (
    <div className="admin-page">
      {/* ─── Hero Section ─── */}
      <div className="lit-admin-hero">
        <div className="lit-admin-badge">
          <BookMarked size={13} strokeWidth={2} />
          <span>Hệ thống Chuyên khảo Nguồn</span>
        </div>
        <div className="lit-admin-header">
          <div>
            <h1 className="lit-admin-title">Quản lý Tài liệu gốc</h1>
            <p className="lit-admin-subtitle">
              Danh mục sách chuyên khảo, atlas phân loại và tài liệu tham chiếu nền tảng hiển thị trên trang chủ và đối soát hệ thống.
            </p>
          </div>
          <button 
            className="btn btn-primary" 
            data-class="btn"
            onClick={openCreate} 
            type="button"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.45rem' }}
          >
            <Plus size={16} strokeWidth={2} /> 
            <span>Thêm tài liệu mới</span>
          </button>
        </div>
      </div>

      {/* ─── Telemetry KPI Strip ─── */}
      <div className="lit-telemetry-grid">
        <div className="lit-kpi-card">
          <div className="lit-kpi-card__icon" style={{ background: 'rgba(14, 165, 233, 0.1)', color: '#0284c7' }}>
            <Library size={22} strokeWidth={1.75} />
          </div>
          <div className="lit-kpi-card__meta">
            <span className="lit-kpi-card__label">Tổng chuyên khảo</span>
            <span className="lit-kpi-card__val">{totalCount} tài liệu</span>
          </div>
        </div>

        <div className="lit-kpi-card">
          <div className="lit-kpi-card__icon" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#059669' }}>
            <Sparkles size={22} strokeWidth={1.75} />
          </div>
          <div className="lit-kpi-card__meta">
            <span className="lit-kpi-card__label">Đang xuất bản (Trang chủ)</span>
            <span className="lit-kpi-card__val">{visibleCount} xuất bản</span>
          </div>
        </div>

        <div className="lit-kpi-card">
          <div className="lit-kpi-card__icon" style={{ background: 'rgba(20, 184, 166, 0.1)', color: '#0d9488' }}>
            <Layers size={22} strokeWidth={1.75} />
          </div>
          <div className="lit-kpi-card__meta">
            <span className="lit-kpi-card__label">Dữ liệu liên kết</span>
            <span className="lit-kpi-card__val">1,965+ loài</span>
          </div>
        </div>
      </div>

      {/* ─── Toolbar: Search + View Switcher ─── */}
      <div className="lit-admin-toolbar">
        <div className="lit-toolbar-search">
          <Search size={16} className="lit-toolbar-search-icon" />
          <input 
            type="text"
            placeholder="Tìm kiếm tài liệu theo tên, tác giả, năm..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="lit-toolbar-actions">
          <span className="lit-counter-badge">
            Hiển thị <strong>{filteredSources.length}</strong> / {totalCount} tài liệu
          </span>

          <div className="lit-view-switcher">
            <button
              type="button"
              data-class="btn"
              className={`lit-view-btn${viewMode === 'cards' ? ' active' : ''}`}
              onClick={() => setViewMode('cards')}
              title="Chế độ Thẻ Bento KPI"
            >
              <LayoutGrid size={15} />
              <span>Thẻ KPI</span>
            </button>
            <button
              type="button"
              data-class="btn"
              className={`lit-view-btn${viewMode === 'table' ? ' active' : ''}`}
              onClick={() => setViewMode('table')}
              title="Chế độ Bảng danh sách"
            >
              <TableIcon size={15} />
              <span>Bảng</span>
            </button>
          </div>
        </div>
      </div>

      {/* ─── Content Area ─── */}
      {loading ? (
        <div className="list-status-message">
          <div className="spinner" />
          <span>Đang tải danh mục tài liệu...</span>
        </div>
      ) : filteredSources.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: '#ffffff', border: '1px dashed #cbd5e1', borderRadius: '12px' }}>
          <BookOpen size={32} style={{ color: '#94a3b8', margin: '0 auto 0.75rem' }} />
          <p style={{ margin: 0, color: '#64748b', fontSize: '0.95rem', fontWeight: 500 }}>
            {searchQuery ? `Không tìm thấy tài liệu phù hợp với "${searchQuery}"` : 'Chưa có tài liệu nguồn nào.'}
          </p>
        </div>
      ) : viewMode === 'cards' ? (
        /* ── Bento KPI Cards Grid View ── */
        <div className="lit-cards-grid">
          {paginatedSources.map((item, idx) => {
            const theme = THEME_PALETTE[idx % THEME_PALETTE.length]
            return (
              <div 
                key={item.id} 
                className={`lit-admin-card${!item.is_visible ? ' is-hidden' : ''}`}
                style={{
                  ['--card-accent-color' as string]: theme.accentColor,
                  ['--card-accent-grad' as string]: theme.accentGrad,
                  ['--card-icon-bg' as string]: theme.iconBg,
                }}
              >
                <div className="lit-admin-card__top-bar" />
                <div className="lit-admin-card__body">
                  <div className="lit-admin-card__header-row">
                    <div className="lit-admin-card__icon-box">
                      {renderSourceIcon(item.icon_name, 22)}
                    </div>

                    <div className="lit-admin-card__status-wrap">
                      <button
                        type="button"
                        data-class="pill-btn"
                        className={`lit-status-pill ${item.is_visible ? 'online' : 'offline'}`}
                        onClick={() => toggleVisible(item)}
                        title={item.is_visible ? 'Click để ẩn khỏi trang chủ' : 'Click để xuất bản lên trang chủ'}
                      >
                        {item.is_visible ? <Eye size={12} strokeWidth={2} /> : <EyeOff size={12} strokeWidth={2} />}
                        <span>{item.is_visible ? 'ĐANG HIỆN' : 'ĐANG ẨN'}</span>
                      </button>
                    </div>
                  </div>

                  <h3 className="lit-admin-card__title">{item.title}</h3>
                  {item.subtitle && (
                    <div className="lit-admin-card__subtitle">{item.subtitle}</div>
                  )}

                  <div className="lit-admin-card__meta-row">
                    <div className="lit-admin-card__meta-item">
                      <span style={{ color: '#94a3b8', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>Tác giả:</span>
                      <strong style={{ color: '#0b1329' }}>{item.author}</strong>
                    </div>
                    {(item.publisher || item.year) && (
                      <div className="lit-admin-card__meta-item">
                        <span style={{ color: '#94a3b8', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>Xuất bản:</span>
                        <span>{[item.publisher, item.year].filter(Boolean).join(' • ')}</span>
                      </div>
                    )}
                  </div>

                  <div className="lit-admin-card__kpi-row">
                    <span className="lit-kpi-badge-text">{item.pill_text || 'Số lượng loài'}</span>
                    <span className="lit-kpi-badge-val">{item.stats_count || 'Chưa định lượng'}</span>
                  </div>

                  {item.chips && item.chips.length > 0 && (
                    <div className="lit-admin-card__chips">
                      {item.chips.map(c => (
                        <span key={c} className="lit-chip-badge">{c}</span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="lit-admin-card__footer">
                  <span className="lit-sort-pill">Thứ tự #{item.sort_order}</span>

                  <div className="lit-card-action-btns">
                    {item.href && (
                      <Link
                        href={item.href}
                        target="_blank"
                        className="btn btn-outline btn-sm"
                        data-class="btn"
                        style={{ padding: '0.3rem 0.5rem', display: 'inline-flex', alignItems: 'center' }}
                        title={`Tra cứu: ${item.href}`}
                      >
                        <ExternalLink size={13} />
                      </Link>
                    )}
                    <button
                      type="button"
                      className="btn btn-outline btn-sm"
                      data-class="btn"
                      onClick={() => openEdit(item)}
                      style={{ padding: '0.3rem 0.65rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                    >
                      <Pencil size={13} />
                      <span>Sửa</span>
                    </button>
                    <button
                      type="button"
                      className="btn btn-outline btn-sm"
                      data-class="btn"
                      onClick={() => handleDelete(item.id, item.title)}
                      style={{ padding: '0.3rem 0.5rem', color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.3)' }}
                      title="Xóa tài liệu"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        /* ── Classic Table View Fallback ── */
        <div className="admin-table-scroll" style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 2px 5px rgba(0,0,0,0.02)' }}>
          <table className="admin-table">
            <thead>
              <tr>
                <th style={{ width: 60, textAlign: 'center' }}>TT</th>
                <th>Tài liệu chuyên khảo</th>
                <th>Tác giả &amp; NXB</th>
                <th>Phân loại / Số loài</th>
                <th style={{ width: 120, textAlign: 'center' }}>Trang chủ</th>
                <th style={{ width: 140, textAlign: 'right' }}>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {paginatedSources.map(item => (
                <tr key={item.id}>
                  <td style={{ textAlign: 'center', fontWeight: 700, fontFamily: 'var(--font-outlier)' }}>
                    #{item.sort_order}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ width: 32, height: 32, borderRadius: 8, background: '#f1f5f9', display: 'grid', placeItems: 'center', color: '#0284c7' }}>
                        {renderSourceIcon(item.icon_name, 16)}
                      </div>
                      <div>
                        <div style={{ fontWeight: 700, color: '#0b1329', fontSize: '0.92rem' }}>{item.title}</div>
                        {item.subtitle && <div style={{ fontSize: '0.78rem', color: '#64748b' }}>{item.subtitle}</div>}
                      </div>
                    </div>
                  </td>
                  <td>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#1e293b' }}>{item.author}</div>
                    <div style={{ fontSize: '0.78rem', color: '#64748b' }}>{[item.publisher, item.year].filter(Boolean).join(', ')}</div>
                  </td>
                  <td>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      {item.pill_text && <span className="lit-chip-badge">{item.pill_text}</span>}
                      <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0284c7', fontFamily: 'var(--font-outlier)' }}>{item.stats_count}</span>
                    </div>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      type="button"
                      data-class="pill-btn"
                      className={`lit-status-pill ${item.is_visible ? 'online' : 'offline'}`}
                      onClick={() => toggleVisible(item)}
                    >
                      {item.is_visible ? 'ĐANG HIỆN' : 'ĐANG ẨN'}
                    </button>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: '0.4rem' }}>
                      <button
                        type="button"
                        className="btn btn-outline btn-sm"
                        data-class="btn"
                        onClick={() => openEdit(item)}
                        style={{ padding: '0.3rem 0.6rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                      >
                        <Pencil size={13} />
                        <span>Sửa</span>
                      </button>
                      <button
                        type="button"
                        className="btn btn-outline btn-sm"
                        data-class="btn"
                        onClick={() => handleDelete(item.id, item.title)}
                        style={{ padding: '0.3rem 0.5rem', color: '#ef4444', borderColor: 'rgba(239,68,68,0.3)' }}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ─── Pagination Footer ─── */}
      {filteredSources.length > 0 && (
        <div className="admin-pagination" style={{ marginTop: '1.5rem', borderRadius: '12px', border: '1px solid #e2e8f0', background: '#ffffff', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <span className="admin-pagination__info">
              Trang <strong>{page}</strong> / {totalPages} &nbsp;·&nbsp; Hiển thị <strong>{totalItems > 0 ? (page - 1) * pageSize + 1 : 0} – {Math.min(totalItems, page * pageSize)}</strong> trên tổng số <strong>{totalItems}</strong> tài liệu
            </span>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: '#64748b' }}>
              <span>Số lượng:</span>
              <select
                value={pageSize}
                onChange={e => setPageSize(Number(e.target.value))}
                className="form-input admin-select"
                style={{ padding: '0.25rem 1.75rem 0.25rem 0.6rem', fontSize: '0.78rem', width: 'auto', backgroundPosition: 'right 0.5rem center' }}
              >
                <option value={6}>6 tài liệu/trang</option>
                <option value={9}>9 tài liệu/trang</option>
                <option value={12}>12 tài liệu/trang</option>
                <option value={9999}>Tất cả</option>
              </select>
            </div>
          </div>

          {totalPages > 1 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <button
                className="btn btn-outline btn-sm"
                data-class="btn"
                disabled={page <= 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
                type="button"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.2rem', padding: '0.35rem 0.6rem' }}
              >
                <ChevronLeft size={14} />
                <span>Trước</span>
              </button>

              {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                <button
                  key={p}
                  type="button"
                  data-class="btn"
                  onClick={() => setPage(p)}
                  className={`btn btn-sm ${p === page ? 'btn-primary' : 'btn-outline'}`}
                  style={{ minWidth: 32, padding: '0 0.45rem', height: 30, fontSize: '0.8rem' }}
                >
                  {p}
                </button>
              ))}

              <button
                className="btn btn-outline btn-sm"
                data-class="btn"
                disabled={page >= totalPages}
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                type="button"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.2rem', padding: '0.35rem 0.6rem' }}
              >
                <span>Sau</span>
                <ChevronRight size={14} />
              </button>
            </div>
          )}
        </div>
      )}

      {/* ─── Studio 2-Column Modal ─── */}
      {isFormOpen && (
        <div className="admin-modal-overlay" onClick={closeModal}>
          <div className="admin-modal admin-modal--studio" onClick={e => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="admin-modal__header">
              <div className="admin-modal__title-group">
                <div className="admin-modal__badge-line">
                  <span className="admin-modal__collection-tag">TÀI LIỆU GỐC</span>
                  <span className="admin-modal__id-tag">#{form.sort_order || 1}</span>
                  <span 
                    className="admin-modal__vol-tag"
                    style={{ 
                      background: form.is_visible ? '#dcfce7' : '#f1f5f9',
                      color: form.is_visible ? '#15803d' : '#64748b',
                      borderColor: form.is_visible ? '#bbf7d0' : '#e2e8f0'
                    }}
                  >
                    {form.is_visible ? 'XUẤT BẢN TRANG CHỦ' : 'ẨN TRANG CHỦ'}
                  </span>
                </div>
                <h3 className="admin-modal__title">
                  {creating ? 'Thêm tài liệu chuyên khảo mới' : `Sửa: ${editing?.title}`}
                </h3>
              </div>
              <button 
                className="admin-modal__close" 
                data-class="close-btn"
                onClick={closeModal} 
                type="button" 
                aria-label="Đóng"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal 2-Column Workspace */}
            <form onSubmit={handleSave} className="admin-modal__workspace">
              {/* Left Sidebar */}
              <aside className="admin-modal__sidebar">
                <div className="modal-nav">
                  <button
                    type="button"
                    data-class="nav-btn"
                    className={`modal-nav-btn ${modalTab === 'metadata' ? 'active' : ''}`}
                    onClick={() => setModalTab('metadata')}
                  >
                    <span className="modal-nav-icon"><BookMarked size={16} /></span>
                    <div className="modal-nav-meta">
                      <span className="modal-nav-label">Thư mục</span>
                      <span className="modal-nav-desc">Tên, tác giả, NXB, năm</span>
                    </div>
                  </button>

                  <button
                    type="button"
                    data-class="nav-btn"
                    className={`modal-nav-btn ${modalTab === 'link' ? 'active' : ''}`}
                    onClick={() => setModalTab('link')}
                  >
                    <span className="modal-nav-icon"><ExternalLink size={16} /></span>
                    <div className="modal-nav-meta">
                      <span className="modal-nav-label">Liên kết &amp; Số loài</span>
                      <span className="modal-nav-desc">Bộ sưu tập, số lượng loài</span>
                    </div>
                  </button>

                  <button
                    type="button"
                    data-class="nav-btn"
                    className={`modal-nav-btn ${modalTab === 'visual' ? 'active' : ''}`}
                    onClick={() => setModalTab('visual')}
                  >
                    <span className="modal-nav-icon"><Bookmark size={16} /></span>
                    <div className="modal-nav-meta">
                      <span className="modal-nav-label">Icon &amp; Phân nhóm</span>
                      <span className="modal-nav-desc">Biểu tượng, chips phân tập</span>
                    </div>
                  </button>

                  <button
                    type="button"
                    data-class="nav-btn"
                    className={`modal-nav-btn ${modalTab === 'preview' ? 'active' : ''}`}
                    onClick={() => setModalTab('preview')}
                  >
                    <span className="modal-nav-icon"><Eye size={16} /></span>
                    <div className="modal-nav-meta">
                      <span className="modal-nav-label">Xem trước</span>
                      <span className="modal-nav-desc">Thẻ sách trên trang chủ</span>
                    </div>
                  </button>
                </div>

                <div className="modal-sidebar-footer">
                  <div className="modal-sidebar-kpi">
                    <span>Trạng thái:</span>
                    <span className="kpi-val">{creating ? 'Đang tạo mới' : 'Chỉnh sửa'}</span>
                  </div>
                  <div className="modal-sidebar-kpi">
                    <span>Thứ tự:</span>
                    <span className="kpi-val">Vị trí #{form.sort_order}</span>
                  </div>
                </div>
              </aside>

              {/* Right Content Panel */}
              <section className="admin-modal__content-area">
                <div className="admin-modal__scroll-body">
                  {/* Tab 1: Thư mục học thuật */}
                  {modalTab === 'metadata' && (
                    <div className="form-grid">
                      <div className="form-field" style={{ gridColumn: '1 / -1' }}>
                        <label className="form-label">Tên tài liệu chuyên khảo <span style={{ color: '#ef4444' }}>*</span></label>
                        <input 
                          className="form-input" 
                          value={form.title} 
                          onChange={e => setField('title', e.target.value)} 
                          placeholder="Ví dụ: Danh mục Cá biển Việt Nam"
                          required 
                        />
                      </div>

                      <div className="form-field" style={{ gridColumn: '1 / -1' }}>
                        <label className="form-label">Phụ đề (Khung năm hoặc phạm vi tập)</label>
                        <input 
                          className="form-input" 
                          value={form.subtitle || ''} 
                          onChange={e => setField('subtitle', e.target.value)} 
                          placeholder="Ví dụ: Tập I – V (1992 – 2007)" 
                        />
                      </div>

                      <div className="form-field">
                        <label className="form-label">Tác giả / Chủ biên <span style={{ color: '#ef4444' }}>*</span></label>
                        <input 
                          className="form-input" 
                          value={form.author} 
                          onChange={e => setField('author', e.target.value)} 
                          placeholder="Ví dụ: Nguyễn Khắc Hường, Mai Đàm..."
                          required 
                        />
                      </div>

                      <div className="form-field">
                        <label className="form-label">Nhà xuất bản</label>
                        <input 
                          className="form-input" 
                          value={form.publisher || ''} 
                          onChange={e => setField('publisher', e.target.value)} 
                          placeholder="Ví dụ: NXB Khoa học và Kỹ thuật" 
                        />
                      </div>

                      <div className="form-field">
                        <label className="form-label">Năm xuất bản</label>
                        <input 
                          className="form-input" 
                          value={form.year || ''} 
                          onChange={e => setField('year', e.target.value)} 
                          placeholder="Ví dụ: 1992 – 2007" 
                        />
                      </div>

                      <div className="form-field">
                        <label className="form-label">Thứ tự hiển thị (sort_order)</label>
                        <input 
                          className="form-input" 
                          type="number" 
                          value={form.sort_order} 
                          onChange={e => setField('sort_order', parseInt(e.target.value) || 0)} 
                        />
                      </div>

                      <div className="form-field" style={{ gridColumn: '1 / -1' }}>
                        <label className="form-label">Mô tả học thuật</label>
                        <textarea 
                          className="form-input" 
                          rows={3} 
                          value={form.description || ''} 
                          onChange={e => setField('description', e.target.value)} 
                          placeholder="Mô tả tóm lược về công trình chuyên khảo này..."
                        />
                      </div>
                    </div>
                  )}

                  {/* Tab 2: Liên kết & Số loài */}
                  {modalTab === 'link' && (
                    <div className="form-grid">
                      <div className="form-field" style={{ gridColumn: '1 / -1' }}>
                        <label className="form-label">Link tra cứu tương ứng <span style={{ color: '#ef4444' }}>*</span></label>
                        <select 
                          className="form-input admin-select" 
                          value={form.href} 
                          onChange={e => handleLinkSelect(e.target.value)}
                          required
                        >
                          <option value="">— Chọn bộ sưu tập / tập tra cứu —</option>
                          {linkOptions.map(opt => (
                            <option key={opt.href} value={opt.href}>{opt.label}</option>
                          ))}
                        </select>
                      </div>

                      <div className="form-field">
                        <label className="form-label">Số loài (hiển thị KPI)</label>
                        <input 
                          className="form-input" 
                          value={form.stats_count || ''} 
                          onChange={e => setField('stats_count', e.target.value)} 
                          placeholder="Tự điền khi chọn link — hoặc gõ tay (vd: 1,965 loài)" 
                        />
                      </div>

                      <div className="form-field">
                        <label className="form-label">Badge Pill (Nhãn nổi bật)</label>
                        <input 
                          className="form-input" 
                          value={form.pill_text || ''} 
                          onChange={e => setField('pill_text', e.target.value)} 
                          placeholder="Ví dụ: 5 Tập Chuyên Khảo" 
                        />
                      </div>

                      <div className="form-field" style={{ gridColumn: '1 / -1', marginTop: '1rem', background: '#f8fafc', padding: '1rem', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', cursor: 'pointer', margin: 0 }}>
                          <input 
                            type="checkbox" 
                            checked={form.is_visible} 
                            onChange={e => setField('is_visible', e.target.checked)} 
                            style={{ width: 18, height: 18, accentColor: '#00d4b8' }}
                          />
                          <div>
                            <div style={{ fontWeight: 600, color: '#0b1329', fontSize: '0.9rem' }}>Xuất bản trên trang chủ</div>
                            <div style={{ color: '#64748b', fontSize: '0.78rem' }}>Tài liệu này sẽ xuất hiện trong mục "Tài liệu khoa học nguồn" trên trang chủ public.</div>
                          </div>
                        </label>
                      </div>
                    </div>
                  )}

                  {/* Tab 3: Icon & Chips phân nhóm */}
                  {modalTab === 'visual' && (
                    <div className="form-grid form-grid--single">
                      <div className="form-field">
                        <label className="form-label">Chọn Biểu tượng đại dương (Icon)</label>
                        <div className="lit-icon-picker-grid">
                          {ICON_OPTIONS.map(opt => {
                            const IconComponent = opt.icon
                            const isSelected = form.icon_name === opt.id
                            return (
                              <button
                                key={opt.id}
                                type="button"
                                data-class="icon-btn"
                                className={`lit-icon-option-btn ${isSelected ? 'selected' : ''}`}
                                onClick={() => setField('icon_name', opt.id)}
                              >
                                <IconComponent size={24} strokeWidth={isSelected ? 2 : 1.75} />
                                <span className="lit-icon-option-label">{opt.label}</span>
                              </button>
                            )
                          })}
                        </div>
                      </div>

                      <div className="form-field synonyms-chip-editor" style={{ marginTop: '1rem' }}>
                        <label className="form-label">Phân tập &amp; Nhóm chuyên khảo (Chips)</label>
                        <div className="synonyms-chips">
                          {chipsList.length === 0 ? (
                            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Chưa có thẻ phân tập nào</span>
                          ) : (
                            chipsList.map(chip => (
                              <span key={chip} className="synonyms-chip">
                                {chip}
                                <button
                                  type="button"
                                  data-class="chip-btn"
                                  className="synonyms-chip-remove"
                                  onClick={() => handleRemoveChip(chip)}
                                  title={`Xóa ${chip}`}
                                >
                                  <X size={13} />
                                </button>
                              </span>
                            ))
                          )}
                        </div>

                        <div className="synonyms-input-row">
                          <input
                            type="text"
                            className="form-input"
                            placeholder="Nhập tên tập (ví dụ: T.I: Cá nhám, cá đuối)..."
                            value={newChipInput}
                            onChange={e => setNewChipInput(e.target.value)}
                            onKeyDown={e => {
                              if (e.key === 'Enter') {
                                e.preventDefault()
                                handleAddChip()
                              }
                            }}
                          />
                          <button
                            type="button"
                            data-class="btn"
                            className="btn btn-outline"
                            style={{ padding: '0 0.85rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            onClick={handleAddChip}
                          >
                            <Plus size={14} /> Thêm
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Tab 4: Live Preview Thẻ Trang Chủ */}
                  {modalTab === 'preview' && (
                    <div className="lit-preview-container">
                      <div className="lit-preview-watermark">
                        <Sparkles size={14} /> Bản xem trước trực quan trên Trang Chủ
                      </div>

                      <div 
                        className="lit-admin-card"
                        style={{
                          maxWidth: 420,
                          width: '100%',
                          ['--card-accent-color' as string]: '#0ea5e9',
                          ['--card-accent-grad' as string]: 'linear-gradient(90deg, #0284c7 0%, #38bdf8 100%)',
                          ['--card-icon-bg' as string]: 'rgba(14, 165, 233, 0.1)',
                          cursor: 'default',
                        }}
                      >
                        <div className="lit-admin-card__top-bar" />
                        <div className="lit-admin-card__body">
                          <div className="lit-admin-card__header-row">
                            <div className="lit-admin-card__icon-box">
                              {renderSourceIcon(form.icon_name, 22)}
                            </div>
                            {form.pill_text && (
                              <span className="lit-status-pill online">
                                {form.pill_text}
                              </span>
                            )}
                          </div>

                          <h3 className="lit-admin-card__title">{form.title || 'Tên tài liệu chuyên khảo'}</h3>
                          {form.subtitle && <div className="lit-admin-card__subtitle">{form.subtitle}</div>}

                          <div className="lit-admin-card__meta-row">
                            <div className="lit-admin-card__meta-item">
                              <span style={{ color: '#94a3b8', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>Tác giả:</span>
                              <strong style={{ color: '#0b1329' }}>{form.author || 'Chưa có tác giả'}</strong>
                            </div>
                            {(form.publisher || form.year) && (
                              <div className="lit-admin-card__meta-item">
                                <span style={{ color: '#94a3b8', fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600 }}>Xuất bản:</span>
                                <span>{[form.publisher, form.year].filter(Boolean).join(' • ')}</span>
                              </div>
                            )}
                          </div>

                          <div className="lit-admin-card__kpi-row">
                            <span className="lit-kpi-badge-text">Dữ liệu bảo chứng</span>
                            <span className="lit-kpi-badge-val">{form.stats_count || 'Chưa định lượng'}</span>
                          </div>

                          {chipsList.length > 0 && (
                            <div className="lit-admin-card__chips">
                              {chipsList.map(c => (
                                <span key={c} className="lit-chip-badge">{c}</span>
                              ))}
                            </div>
                          )}
                        </div>

                        <div className="lit-admin-card__footer">
                          <span style={{ fontSize: '0.78rem', color: '#0284c7', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                            Khám phá dữ liệu <ExternalLink size={12} />
                          </span>
                          <span className="lit-sort-pill">Link: {form.href || '/'}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Sticky Footer */}
                <div className="admin-modal__footer">
                  <button 
                    className="btn btn-outline" 
                    data-class="btn"
                    onClick={closeModal} 
                    type="button"
                  >
                    Hủy bỏ
                  </button>
                  <button 
                    className="btn btn-primary" 
                    data-class="btn"
                    type="submit" 
                    disabled={saving || !form.title || !form.author || !form.href}
                  >
                    {saving ? 'Đang lưu...' : (creating ? 'Thêm mới tài liệu' : 'Cập nhật tài liệu')}
                  </button>
                </div>
              </section>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

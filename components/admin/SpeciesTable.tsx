'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import '@/styles/admin.css'
import '@/styles/admin-command.css'
// ponytail: lazy load SpeciesForm (44KB) — only needed when user clicks Edit/Add
const SpeciesForm = dynamic(() => import('./SpeciesForm'), { ssr: false })
import ImportModal from './ImportModal'
import AuditLog from './AuditLog'
import {
  Search,
  Plus,
  Pencil,
  Trash2,
  RotateCcw,
  X,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Camera,
  ExternalLink,
  CheckCircle2,
  ShieldCheck,
  Image as ImageIcon,
} from 'lucide-react'
import { getCollectionBySlug } from '@/lib/collection-registry'

interface SpeciesRow {
  [key: string]: unknown
  id: string
  volume: number
  species_index: number | null
  vn_name: string
  scientific_name: string
  tax_family_latin: string | null
  collection_id: string
  deleted_at: string | null
  worms_status?: string | null
  worms_accepted_name?: string | null
  vn_status?: string | null
  biology?: {
    vnRedList?: {
      status?: string
      refCode?: string
      criteria?: string
      threats?: string
      actions?: string
    }
    [key: string]: unknown
  } | null
  photo_url?: string | null
}

interface Props {
  collection: string
  themeColor?: string
}

export default function SpeciesTable({ collection, themeColor = '#00f0d0' }: Props) {
  const colInfo = getCollectionBySlug(collection)
  const maxVols = colInfo?.volumeCount || 1
  const volOptions = maxVols > 1
    ? ['Tất cả', ...Array.from({ length: maxVols }, (_, i) => String(i + 1))]
    : []

  const [rows, setRows] = useState<SpeciesRow[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [vol, setVol] = useState('')
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [loading, setLoading] = useState(false)
  const [editTarget, setEditTarget] = useState<Record<string, unknown> | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [showDeleted, setShowDeleted] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)
  const [toast, setToast] = useState<{ msg: string; type: 'ok' | 'err' } | null>(null)
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const PAGE_SIZE = 20
  const totalPages = Math.ceil(total / PAGE_SIZE) || 1

  function showToast(msg: string, type: 'ok' | 'err' = 'ok') {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  const load = useCallback(
    async (p = page, v = vol, s = search, incDel = showDeleted, f = filterType) => {
      setLoading(true)
      const params = new URLSearchParams({ collection, page: String(p) })
      if (v) params.set('vol', v)
      if (s) params.set('search', s)
      if (incDel) params.set('include_deleted', 'true')
      if (f && f !== 'all') params.set('filter', f)
      params.set('t', String(Date.now()))
      const res = await fetch(`/api/species?${params}`)
      const json = await res.json()
      if (!res.ok) {
        showToast(json.error, 'err')
        setLoading(false)
        return
      }
      setRows(json.data || [])
      setTotal(json.total || 0)
      setLoading(false)
    },
    [collection, page, vol, search, showDeleted, filterType]
  )

  useEffect(() => {
    load(page, vol, search, showDeleted, filterType)
  }, [page, vol, showDeleted, filterType]) // eslint-disable-line

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value
    setSearch(v)
    if (searchTimer.current) clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => {
      setPage(1)
      load(1, vol, v, showDeleted, filterType)
    }, 450)
  }

  const clearSearch = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    if (searchTimer.current) clearTimeout(searchTimer.current)
    setSearch('')
    setPage(1)
    load(1, vol, '', showDeleted, filterType)
    document.getElementById('searchAdmin')?.focus()
  }

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape' && search) {
      e.preventDefault()
      clearSearch()
    }
  }

  const handleVolChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setVol(e.target.value)
    setPage(1)
  }

  const handleFilterChipClick = (type: string) => {
    setFilterType(type)
    setPage(1)
  }

  const fetchAndEdit = async (id: string) => {
    if (editingId) return
    setEditingId(id)
    try {
      const fullRes = await fetch(`/api/species/detail?id=${id}`)
      if (fullRes.ok) {
        const { data } = await fullRes.json()
        setEditTarget(data)
      } else {
        const row = rows.find((r) => r.id === id)
        setEditTarget(row || null)
      }
      setShowForm(true)
    } catch {
      showToast('Không thể tải chi tiết loài', 'err')
    } finally {
      setEditingId(null)
    }
  }

  const handleSave = async (data: Record<string, unknown>, id?: string) => {
    const isNew = !id
    const res = await fetch(isNew ? '/api/species' : `/api/species?id=${id}`, {
      method: isNew ? 'POST' : 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ ...data, collection_id: collection }),
    })
    const json = await res.json()
    if (!res.ok) {
      showToast(json.error, 'err')
      return false
    }
    showToast(isNew ? 'Đã thêm loài mới thành công ✓' : 'Đã cập nhật dữ liệu ✓')
    setShowForm(false)
    setEditTarget(null)
    load(page, vol, search, showDeleted, filterType)
    return true
  }

  const handleDelete = async (id: string) => {
    const res = await fetch(`/api/species?id=${id}`, { method: 'DELETE', credentials: 'include' })
    const json = await res.json()
    if (!res.ok) {
      showToast(json.error, 'err')
      return
    }
    showToast('Đã xóa mềm loài vào thùng rác ✓')
    setDeleteConfirm(null)
    load(page, vol, search, showDeleted, filterType)
  }

  const handleRestore = async (id: string) => {
    const res = await fetch(`/api/species?id=${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ deleted_at: null }),
    })
    const json = await res.json()
    if (!res.ok) {
      showToast(json.error, 'err')
      return
    }
    showToast('Đã khôi phục loài thành công ✓')
    load(page, vol, search, showDeleted, filterType)
  }

  const FILTER_CHIPS = [
    { id: 'all', label: 'Tất cả' },
    { id: 'has_photo', label: 'Có ảnh mẫu vật' },
    { id: 'no_photo', label: 'Thiếu ảnh' },
    { id: 'red_list', label: 'Sách Đỏ VAST' },
    { id: 'worms_valid', label: 'WoRMS Valid' },
  ]

  return (
    <div className="admin-species-container">
      {/* Toast Alert */}
      {toast && (
        <div className={`admin-toast${toast.type === 'err' ? ' admin-toast--err' : ''}`} role="status">
          {toast.msg}
        </div>
      )}

      {/* Main Table Card */}
      <div className="admin-table-wrapper">

        {/* Command Bar / Toolbar */}
        <div className="admin-toolbar">
          <div className="admin-toolbar__filters">
            {/* Search Box */}
            <div className="admin-search-box">
              <span className="admin-search-box__icon" aria-hidden="true">
                <Search size={15} />
              </span>
              <input
                type="text"
                id="searchAdmin"
                className="admin-search-input"
                placeholder="Tìm tên Việt, tên khoa học, họ Latinh..."
                value={search}
                onChange={handleSearch}
                onKeyDown={handleSearchKeyDown}
              />
              {search && (
                <button
                  type="button"
                  data-class="btn"
                  className="admin-search-clear-btn"
                  onClick={clearSearch}
                  title="Xóa từ khóa tìm kiếm (Esc)"
                  aria-label="Xóa từ khóa tìm kiếm"
                >
                  <X size={13} aria-hidden="true" />
                </button>
              )}
            </div>

            {/* Volume Filter Dropdown — Only shown if collection has > 1 volume */}
            {volOptions.length > 0 && (
              <select
                id="filterVol"
                className="admin-select"
                value={vol}
                onChange={handleVolChange}
                aria-label="Lọc theo tập"
              >
                {volOptions.map((v) => (
                  <option key={v} value={v === 'Tất cả' ? '' : v}>
                    {v === 'Tất cả'
                      ? 'Tất cả các tập'
                      : v === '6' && collection === 'ca-bien'
                      ? 'Atlas cá rạn san hô'
                      : `Tập ${v}`}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="admin-toolbar__actions">
            <label
              className="admin-deleted-toggle"
              style={{
                background: showDeleted ? '#fef2f2' : '#ffffff',
                borderColor: showDeleted ? '#fca5a5' : '#cbd5e1',
                color: showDeleted ? '#dc2626' : '#475569',
              }}
            >
              <input
                type="checkbox"
                checked={showDeleted}
                onChange={(e) => {
                  setShowDeleted(e.target.checked)
                  setPage(1)
                }}
              />
              <span>Thùng rác ({showDeleted ? 'Bật' : 'Tắt'})</span>
            </label>

            <ImportModal collection={collection} onImported={() => load(page, vol, search, showDeleted, filterType)} />

            <button
              className="btn btn-primary"
              data-class="btn"
              onClick={() => {
                setEditTarget(null)
                setShowForm(true)
              }}
              type="button"
              style={{
                background: `linear-gradient(135deg, ${themeColor}, #0f766e)`,
                color: '#ffffff',
                fontWeight: 700,
              }}
            >
              <Plus size={16} aria-hidden="true" />
              <span>Thêm loài mới</span>
            </button>
          </div>
        </div>

        {/* Smart Segmented Filter Chips */}
        <div className="admin-filter-chips-row" role="tablist" aria-label="Bộ lọc chuyên sâu">
          {FILTER_CHIPS.map((chip) => {
            const isActive = filterType === chip.id
            return (
              <button
                key={chip.id}
                type="button"
                data-class="btn"
                role="tab"
                aria-selected={isActive}
                onClick={() => handleFilterChipClick(chip.id)}
                className={`admin-filter-chip${isActive ? ' admin-filter-chip--active' : ''}`}
                style={isActive ? { borderColor: themeColor, color: themeColor, background: '#e0f7f4' } : undefined}
              >
                {chip.id === 'has_photo' && <ImageIcon size={12} aria-hidden="true" />}
                {chip.id === 'red_list' && <ShieldCheck size={12} aria-hidden="true" />}
                {chip.id === 'worms_valid' && <CheckCircle2 size={12} aria-hidden="true" />}
                <span>{chip.label}</span>
              </button>
            )
          })}
        </div>

        {/* Main Data Table */}
        <div className="admin-table-scroll">
          <table className="admin-table">
            <thead>
              <tr>
                <th style={{ width: 56, textAlign: 'center' }}>Mẫu vật</th>
                <th style={{ width: 115 }}>Tập / Mã ID</th>
                <th>Định danh &amp; Tên loài</th>
                <th style={{ width: 150 }}>Họ (Latinh)</th>
                <th style={{ width: 175 }}>Khoa học &amp; Bảo tồn</th>
                <th style={{ width: 140, textAlign: 'right' }}>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '3.5rem', color: 'var(--color-muted)' }}>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.6rem' }}>
                      <span className="admin-live-pulse" aria-hidden="true" />
                      <span>Đang tải danh sách loài sinh vật biển...</span>
                    </div>
                  </td>
                </tr>
              )}

              {!loading && rows.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '3.5rem', color: 'var(--color-muted)' }}>
                    Không tìm thấy loài nào khớp với bộ lọc hiện tại.
                  </td>
                </tr>
              )}

              {!loading &&
                rows.map((row) => {
                  const isDeleted = !!row.deleted_at
                  const redListStatus = row.biology?.vnRedList?.status || (row.vn_status && row.vn_status.length <= 4 ? row.vn_status : null)

                  return (
                    <tr key={row.id} className={isDeleted ? 'admin-row--deleted' : ''}>
                      {/* 1. Specimen Thumbnail */}
                      <td style={{ textAlign: 'center', padding: '0.6rem 0.4rem' }}>
                        {row.photo_url ? (
                          <div className="admin-specimen-thumb">
                            <img
                              src={row.photo_url}
                              alt={row.vn_name || row.scientific_name}
                              className="admin-specimen-thumb__img"
                              loading="lazy"
                            />
                          </div>
                        ) : (
                          <div className="admin-specimen-thumb admin-specimen-thumb--empty" title="Chưa có ảnh mẫu vật thực địa">
                            <Camera size={14} aria-hidden="true" />
                          </div>
                        )}
                      </td>

                      {/* 2. Volume & Species ID */}
                      <td>
                        <span
                          className="admin-vol-pill"
                          style={{ borderColor: `${themeColor}40`, color: themeColor }}
                        >
                          {collection === 'ca-bien' && row.volume === 6 ? 'Atlas rạn' : `Tập ${row.volume}`}
                        </span>
                        <div style={{ marginTop: '3px' }}>
                          <code className="admin-species-id">
                            {row.id}
                          </code>
                        </div>
                        {isDeleted && (
                          <span style={{ display: 'inline-block', fontSize: '0.68rem', color: '#ef4444', fontWeight: 600, marginTop: '2px' }}>
                            ✕ Đã xóa
                          </span>
                        )}
                      </td>

                      {/* 3. Species Identity: Vietnamese Name & Scientific Name */}
                      <td className="admin-species-cell">
                        <div className="admin-species-identity">
                          {isDeleted ? (
                            <span className="species-name-disabled">
                              {row.vn_name || '—'}
                            </span>
                          ) : (
                            <button
                              type="button"
                              data-class="btn"
                              className="species-name-btn"
                              onClick={() => fetchAndEdit(row.id)}
                              title="Bấm để mở form chỉnh sửa toàn bộ thông tin loài"
                              disabled={editingId === row.id}
                            >
                              <span className="species-name-btn__label">
                                {row.vn_name || '—'}
                              </span>
                              <Pencil size={11} className="species-name-btn__icon" aria-hidden="true" />
                              {editingId === row.id && (
                                <span className="species-name-btn__loading">...</span>
                              )}
                            </button>
                          )}

                          <div className="admin-species-sci-row">
                            <span className="admin-species-sci">
                              {row.scientific_name || '—'}
                            </span>
                            {row.species_index && (
                              <span className="admin-species-seq" title={`Số thứ tự trong chuyên khảo: #${row.species_index}`}>
                                {' '}#{row.species_index}
                              </span>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* 4. Family Latin */}
                      <td>
                        <span className="admin-family-latin">
                          {row.tax_family_latin || '—'}
                        </span>
                      </td>

                      {/* 5. Scientific & Conservation Badges */}
                      <td>
                        <div className="admin-badges-col">
                          {/* WoRMS Status Pill */}
                          {row.worms_status === 'valid' ? (
                            <span className="admin-badge-worms admin-badge-worms--valid" title={`WoRMS Aphia Valid: ${row.scientific_name}`}>
                              <span className="admin-badge-worms__dot" />
                              <span>WoRMS Valid</span>
                            </span>
                          ) : row.worms_status === 'synonym' ? (
                            <span className="admin-badge-worms admin-badge-worms--synonym" title={`Đồng danh WoRMS -> ${row.worms_accepted_name || ''}`}>
                              <span>Synonym</span>
                            </span>
                          ) : (
                            <span className="admin-badge-worms admin-badge-worms--none" title="Chưa đối soát WoRMS">
                              <span>Chưa kiểm định</span>
                            </span>
                          )}
                          {' '}
                          {/* Vietnam Red List VAST Badge */}
                          {redListStatus && (
                            <span
                              className={`admin-badge-redlist admin-badge-redlist--${redListStatus.toLowerCase()}`}
                              title={`Danh Lục Đỏ Việt Nam (VAST 2024): Phân hạng ${redListStatus}`}
                            >
                              SĐVN: {redListStatus}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* 6. Quick Actions */}
                      <td style={{ textAlign: 'right' }}>
                        <div className="admin-actions-row">
                          {isDeleted ? (
                            <button
                              className="btn btn-success-outline btn-sm"
                              data-class="btn"
                              onClick={() => handleRestore(row.id)}
                              type="button"
                              title="Khôi phục loài"
                            >
                              <RotateCcw size={12} aria-hidden="true" />
                              <span>Khôi phục</span>
                            </button>
                          ) : (
                            <>
                              <Link
                                href={`/${collection}/${row.id}`}
                                target="_blank"
                                className="admin-icon-btn"
                                title="Mở trang xem chi tiết công khai"
                              >
                                <ExternalLink size={13} aria-hidden="true" />
                              </Link>
                              <button
                                className="admin-icon-btn admin-icon-btn--edit"
                                data-class="btn"
                                onClick={() => fetchAndEdit(row.id)}
                                type="button"
                                title="Sửa chi tiết 5 tab"
                              >
                                <Pencil size={13} aria-hidden="true" />
                              </button>
                              <button
                                className="admin-icon-btn admin-icon-btn--delete"
                                data-class="btn"
                                onClick={() => setDeleteConfirm(row.id)}
                                type="button"
                                title="Xóa vào thùng rác"
                              >
                                <Trash2 size={13} aria-hidden="true" />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="admin-pagination">
          <span className="admin-pagination__info">
            Trang <strong>{page}</strong> / {totalPages} &nbsp;·&nbsp; Tổng cộng <strong>{total.toLocaleString('vi-VN')}</strong> loài
          </span>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="btn btn-outline btn-sm"
              data-class="btn"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              type="button"
            >
              <ChevronLeft size={14} aria-hidden="true" />
              <span>Trước</span>
            </button>
            <button
              className="btn btn-outline btn-sm"
              data-class="btn"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              type="button"
            >
              <span>Sau</span>
              <ChevronRight size={14} aria-hidden="true" />
            </button>
          </div>
        </div>
        {/* End admin-table-wrapper */}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="admin-modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', color: '#dc2626', marginBottom: '1rem' }}>
              <AlertTriangle size={24} />
              <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--color-ink)' }}>Xác nhận xóa loài</h3>
            </div>
            <p style={{ color: 'var(--color-muted)', margin: '0.75rem 0 1.5rem', lineHeight: 1.5 }}>
              Bạn có chắc chắn muốn xóa loài có mã <code>{deleteConfirm}</code>? Dữ liệu sẽ được chuyển vào thùng rác và có thể khôi phục lại khi bật tùy chọn &ldquo;Thùng rác&rdquo;.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button className="btn btn-outline" data-class="btn" onClick={() => setDeleteConfirm(null)} type="button">
                Hủy bỏ
              </button>
              <button
                className="btn btn-primary"
                data-class="btn"
                style={{ background: '#dc2626', color: '#ffffff' }}
                onClick={() => handleDelete(deleteConfirm)}
                type="button"
              >
                Xác nhận xóa
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Species 5-Tab Form Modal */}
      {showForm && (
        <SpeciesForm
          initial={editTarget}
          collection={collection}
          onSave={handleSave}
          onClose={() => {
            setShowForm(false)
            setEditTarget(null)
          }}
        />
      )}

      {/* Audit Log Stream */}
      <AuditLog collection={collection} />
    </div>
  )
}

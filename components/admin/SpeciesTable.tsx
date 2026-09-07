'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import SpeciesForm from './SpeciesForm'
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
} from 'lucide-react'

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
}

interface Props {
  collection: string
}

const VOLS = ['Tất cả', '1', '2', '3', '4', '5', '6']

export default function SpeciesTable({ collection }: Props) {
  const [rows, setRows] = useState<SpeciesRow[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [vol, setVol] = useState('')
  const [search, setSearch] = useState('')
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
    async (p = page, v = vol, s = search, incDel = showDeleted) => {
      setLoading(true)
      const params = new URLSearchParams({ collection, page: String(p) })
      if (v) params.set('vol', v)
      if (s) params.set('search', s)
      if (incDel) params.set('include_deleted', 'true')
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
    [collection, page, vol, search, showDeleted]
  )

  useEffect(() => {
    load(page, vol, search, showDeleted)
  }, [page, vol, showDeleted]) // eslint-disable-line

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value
    setSearch(v)
    if (searchTimer.current) clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => {
      setPage(1)
      load(1, vol, v)
    }, 450)
  }

  const clearSearch = () => {
    setSearch('')
    setPage(1)
    load(1, vol, '')
  }

  const handleVolChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setVol(e.target.value)
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
    load(page, vol, search)
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
    load(page, vol, search)
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
    load(page, vol, search, showDeleted)
  }

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
          <div className="admin-search-box">
            <Search size={16} aria-hidden="true" />
            <input
              type="text"
              id="searchAdmin"
              className="admin-search-input"
              placeholder="Tìm theo tên Việt, tên Latinh..."
              value={search}
              onChange={handleSearch}
            />
            {search && (
              <button
                type="button"
                onClick={clearSearch}
                style={{
                  position: 'absolute',
                  right: '0.6rem',
                  background: 'none',
                  border: 'none',
                  color: 'var(--color-muted)',
                  cursor: 'pointer',
                  padding: '2px',
                }}
                title="Xóa tìm kiếm"
              >
                <X size={14} />
              </button>
            )}
          </div>

          <select
            id="filterVol"
            className="admin-select"
            value={vol}
            onChange={handleVolChange}
            aria-label="Lọc theo tập"
          >
            {VOLS.map((v) => (
              <option key={v} value={v === 'Tất cả' ? '' : v}>
                {v === 'Tất cả'
                  ? 'Tất cả các tập'
                  : v === '6' && collection === 'ca-bien'
                  ? 'Atlas cá rạn san hô'
                  : `Tập ${v}`}
              </option>
            ))}
          </select>
        </div>

        <div className="admin-toolbar__actions">
          <label
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.45rem',
              fontSize: '0.82rem',
              color: 'var(--color-ink-3)',
              cursor: 'pointer',
              userSelect: 'none',
              padding: '0.35rem 0.65rem',
              borderRadius: '6px',
              background: showDeleted ? 'rgba(239, 68, 68, 0.08)' : 'transparent',
              border: showDeleted ? '1px solid rgba(239, 68, 68, 0.25)' : '1px solid transparent',
              transition: 'all 0.15s ease',
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
            <span>Hiện đã xóa</span>
          </label>

          <ImportModal collection={collection} onImported={() => load(page, vol, search)} />

          <button
            className="btn btn-primary"
            onClick={() => {
              setEditTarget(null)
              setShowForm(true)
            }}
            type="button"
          >
            <Plus size={16} aria-hidden="true" />
            <span>Thêm loài mới</span>
          </button>
        </div>
      </div>

      {/* Main Data Table */}
      <div className="admin-table-scroll">
        <table className="admin-table">
          <thead>
            <tr>
              <th style={{ width: 110 }}>Tập / Mã ID</th>
              <th>Tên tiếng Việt</th>
              <th>Tên khoa học (Danh pháp)</th>
              <th>Họ (Latinh)</th>
              <th style={{ width: 170, textAlign: 'right' }}>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-muted)' }}>
                  Đang tải danh sách loài...
                </td>
              </tr>
            )}

            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-muted)' }}>
                  Không tìm thấy loài nào khớp với bộ lọc.
                </td>
              </tr>
            )}

            {!loading &&
              rows.map((row) => {
                const isDeleted = !!row.deleted_at
                return (
                  <tr key={row.id} className={isDeleted ? 'admin-row--deleted' : ''}>
                    <td>
                      <span className={`vol-badge v${row.volume}`}>Tập {row.volume}</span>
                      <div style={{ marginTop: '3px' }}>
                        <code style={{ fontSize: '0.74rem', color: 'var(--color-muted)', fontFamily: 'var(--font-outlier)' }}>
                          {row.id}
                        </code>
                      </div>
                      {isDeleted && (
                        <span style={{ display: 'inline-block', fontSize: '0.7rem', color: '#ef4444', fontWeight: 600, marginTop: '2px' }}>
                          ✕ Đã xóa
                        </span>
                      )}
                    </td>

                    {/* Species Vietnamese Name - Click to Edit */}
                    <td className="admin-species-cell">
                      {isDeleted ? (
                        <span className="species-name-disabled" title="Loài đã xóa - hãy khôi phục để sửa">
                          {row.vn_name || '—'}
                        </span>
                      ) : (
                        <button
                          type="button"
                          className="species-name-btn"
                          onClick={() => fetchAndEdit(row.id)}
                          title="Bấm để mở form chỉnh sửa toàn bộ thông tin loài"
                          disabled={editingId === row.id}
                        >
                          <span className="species-name-btn__label">
                            {row.vn_name || '—'}
                          </span>
                          <Pencil size={12} className="species-name-btn__icon" aria-hidden="true" />
                          {editingId === row.id && (
                            <span className="species-name-btn__loading">...</span>
                          )}
                        </button>
                      )}
                    </td>

                    {/* Species Scientific Name - Click to Edit */}
                    <td className="admin-species-cell">
                      {isDeleted ? (
                        <span className="species-scientific-disabled" title="Loài đã xóa - hãy khôi phục để sửa">
                          {row.scientific_name || '—'}
                        </span>
                      ) : (
                        <button
                          type="button"
                          className="species-name-btn species-name-btn--scientific"
                          onClick={() => fetchAndEdit(row.id)}
                          title="Bấm để mở form chỉnh sửa toàn bộ thông tin loài"
                          disabled={editingId === row.id}
                        >
                          <span className="species-name-btn__label">
                            {row.scientific_name || '—'}
                          </span>
                          <Pencil size={12} className="species-name-btn__icon" aria-hidden="true" />
                        </button>
                      )}
                    </td>

                    {/* Family Latin */}
                    <td>
                      <span style={{ color: 'var(--color-ink-3)', fontSize: '0.88rem' }}>
                        {row.tax_family_latin || '—'}
                      </span>
                    </td>

                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'flex-end' }}>
                        {isDeleted ? (
                          <button
                            className="btn btn-success-outline btn-sm"
                            onClick={() => handleRestore(row.id)}
                            type="button"
                            title="Khôi phục loài"
                          >
                            <RotateCcw size={13} aria-hidden="true" />
                            <span>Khôi phục</span>
                          </button>
                        ) : (
                          <>
                            <button
                              className="btn btn-outline btn-sm"
                              onClick={() => fetchAndEdit(row.id)}
                              type="button"
                              title="Sửa chi tiết 5 tab"
                            >
                              <Pencil size={13} aria-hidden="true" />
                              <span>Sửa</span>
                            </button>
                            <button
                              className="btn btn-danger-outline btn-sm"
                              onClick={() => setDeleteConfirm(row.id)}
                              type="button"
                              title="Xóa vào thùng rác"
                            >
                              <Trash2 size={13} aria-hidden="true" />
                              <span>Xóa</span>
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
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            type="button"
          >
            <ChevronLeft size={14} aria-hidden="true" />
            <span>Trước</span>
          </button>
          <button
            className="btn btn-outline btn-sm"
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
              Bạn có chắc chắn muốn xóa loài có mã <code>{deleteConfirm}</code>? Dữ liệu sẽ được chuyển vào thùng rác và có thể khôi phục lại khi bật tùy chọn &ldquo;Hiện đã xóa&rdquo;.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button className="btn btn-outline" onClick={() => setDeleteConfirm(null)} type="button">
                Hủy bỏ
              </button>
              <button
                className="btn btn-primary"
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

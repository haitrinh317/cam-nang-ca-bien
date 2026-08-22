'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import SpeciesForm from './SpeciesForm'
import ImportModal from './ImportModal'
import AuditLog from './AuditLog'

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

interface Props { collection: string }

const VOLS = ['Tất cả', '1', '2', '3', '4', '5']

export default function SpeciesTable({ collection }: Props) {
  const [rows, setRows] = useState<SpeciesRow[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [vol, setVol] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [editTarget, setEditTarget] = useState<Record<string, unknown> | null>(null)
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

  const load = useCallback(async (p = page, v = vol, s = search, incDel = showDeleted) => {
    setLoading(true)
    const params = new URLSearchParams({ collection, page: String(p) })
    if (v) params.set('vol', v)
    if (s) params.set('search', s)
    if (incDel) params.set('include_deleted', 'true')
    const res = await fetch(`/api/species?${params}`)
    const json = await res.json()
    if (!res.ok) { showToast(json.error, 'err'); setLoading(false); return }
    setRows(json.data || [])
    setTotal(json.total || 0)
    setLoading(false)
  }, [collection, page, vol, search, showDeleted])

  useEffect(() => { load(page, vol, search, showDeleted) }, [page, vol, showDeleted]) // eslint-disable-line

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value
    setSearch(v)
    if (searchTimer.current) clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => { setPage(1); load(1, vol, v) }, 450)
  }

  const handleVolChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setVol(e.target.value)
    setPage(1)
  }

  const fetchAndEdit = async (id: string) => {
    const fullRes = await fetch(`/api/species/detail?id=${id}`)
    if (fullRes.ok) {
      const { data } = await fullRes.json()
      setEditTarget(data)
    } else {
      // Fallback: use the row we already have
      const row = rows.find(r => r.id === id)
      setEditTarget(row || null)
    }
    setShowForm(true)
  }

  const handleSave = async (data: Record<string, unknown>, id?: string) => {
    const isNew = !id
    const res = await fetch(isNew ? '/api/species' : `/api/species?id=${id}`, {
      method: isNew ? 'POST' : 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, collection_id: collection }),
    })
    const json = await res.json()
    if (!res.ok) { showToast(json.error, 'err'); return false }
    showToast(isNew ? 'Đã thêm loài mới ✓' : 'Đã cập nhật ✓')
    setShowForm(false)
    setEditTarget(null)
    load(page, vol, search)
    return true
  }

  const handleDelete = async (id: string) => {
    // Soft-delete by default (sets deleted_at)
    const res = await fetch(`/api/species?id=${id}`, { method: 'DELETE' })
    const json = await res.json()
    if (!res.ok) { showToast(json.error, 'err'); return }
    showToast('Đã xóa mềm ✓ (có thể khôi phục)')
    setDeleteConfirm(null)
    load(page, vol, search)
  }

  const handleRestore = async (id: string) => {
    const res = await fetch(`/api/species?id=${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deleted_at: null }),
    })
    const json = await res.json()
    if (!res.ok) { showToast(json.error, 'err'); return }
    showToast('Đã khôi phục ✓')
    load(page, vol, search, showDeleted)
  }

  return (
    <div className="admin-table-wrapper">
      {/* Toast */}
      {toast && (
        <div className={`admin-toast${toast.type === 'err' ? ' admin-toast--err' : ''}`}>
          {toast.msg}
        </div>
      )}

      {/* Toolbar */}
      <div className="admin-toolbar">
        <div className="admin-toolbar__filters">
          <div className="search-input-container" style={{ flex: 1, maxWidth: '380px' }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="text"
              id="searchAdmin"
              className="search-input"
              placeholder="Tìm tên Việt, tên khoa học..."
              value={search}
              onChange={handleSearch}
            />
          </div>
          <select
            id="filterVol"
            className="admin-select"
            value={vol}
            onChange={handleVolChange}
          >
            {VOLS.map(v => (
              <option key={v} value={v === 'Tất cả' ? '' : v}>
                {v === 'Tất cả' ? 'Tất cả các tập' : `Tập ${v}`}
              </option>
            ))}
          </select>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem', color: 'var(--color-ink-3)', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showDeleted}
              onChange={e => { setShowDeleted(e.target.checked); setPage(1) }}
            />
            Hiện đã xóa
          </label>
          <ImportModal collection={collection} onImported={() => load(page, vol, search)} />
          <button
            className="btn btn-primary"
            onClick={() => { setEditTarget(null); setShowForm(true) }}
            type="button"
          >
            + Thêm loài mới
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="admin-table-scroll">
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID / Tập</th>
              <th>Tên tiếng Việt</th>
              <th>Tên khoa học</th>
              <th>Họ (Latin)</th>
              <th style={{ width: '120px' }}>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-muted)' }}>Đang tải...</td></tr>
            )}
            {!loading && rows.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-muted)' }}>Không tìm thấy kết quả.</td></tr>
            )}
            {!loading && rows.map(row => {
              const isDeleted = !!row.deleted_at
              return (
                <tr key={row.id} style={isDeleted ? { opacity: 0.5, background: 'rgba(239,68,68,0.05)' } : {}}>
                  <td>
                    <span className={`vol-badge v${row.volume}`}>Tập {row.volume}</span><br />
                    <code style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>{row.id}</code>
                    {isDeleted && <span style={{ display: 'block', fontSize: '0.7rem', color: '#ef4444', marginTop: '2px' }}>✕ Đã xóa</span>}
                  </td>
                  <td style={{ fontWeight: 500 }}>{row.vn_name || '—'}</td>
                  <td style={{ fontStyle: 'italic', color: 'var(--color-ink-2)' }}>{row.scientific_name || '—'}</td>
                  <td style={{ color: 'var(--color-ink-3)' }}>{row.tax_family_latin || '—'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      {isDeleted ? (
                        <button
                          className="btn btn-outline"
                          style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem', borderColor: '#10b981', color: '#10b981' }}
                          onClick={() => handleRestore(row.id)}
                          type="button"
                        >
                          Khôi phục
                        </button>
                      ) : (
                        <>
                          <button
                            className="btn btn-outline"
                            style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem' }}
                            onClick={() => fetchAndEdit(row.id)}
                            type="button"
                          >
                            Sửa
                          </button>
                          <button
                            className="btn btn-outline"
                            style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem', borderColor: '#ef4444', color: '#ef4444' }}
                            onClick={() => setDeleteConfirm(row.id)}
                            type="button"
                          >
                            Xóa
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

      {/* Pagination */}
      <div className="admin-pagination">
        <button className="btn btn-outline" disabled={page <= 1} onClick={() => setPage(p => p - 1)} type="button">← Trước</button>
        <span style={{ color: 'var(--color-muted)', fontSize: '0.9rem' }}>
          Trang {page} / {totalPages} &nbsp;·&nbsp; Tổng {total} loài
        </span>
        <button className="btn btn-outline" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)} type="button">Sau →</button>
      </div>

      {/* Delete confirm modal */}
      {deleteConfirm && (
        <div className="admin-modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="admin-modal" onClick={e => e.stopPropagation()}>
            <h3>Xác nhận xóa</h3>
            <p style={{ color: 'var(--color-muted)', margin: '1rem 0' }}>
              Bạn chắc chắn muốn xóa loài <code>{deleteConfirm}</code>? Hành động này không thể hoàn tác.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button className="btn btn-outline" onClick={() => setDeleteConfirm(null)} type="button">Hủy</button>
              <button
                className="btn btn-primary"
                style={{ background: '#ef4444' }}
                onClick={() => handleDelete(deleteConfirm)}
                type="button"
              >
                Xóa
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Species Form Modal */}
      {showForm && (
        <SpeciesForm
          initial={editTarget}
          collection={collection}
          onSave={handleSave}
          onClose={() => { setShowForm(false); setEditTarget(null) }}
        />
      )}

      {/* Audit Log */}
      <AuditLog collection={collection} />
    </div>
  )
}

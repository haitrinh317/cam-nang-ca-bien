'use client'

import { useEffect, useState, useCallback } from 'react'
import { Edit2, Trash2, ClipboardList, PlusCircle, Database, Settings, RotateCw } from 'lucide-react'

interface LogEntry {
  id: number
  created_at: string
  user_email: string | null
  action: string
  collection_id: string | null
  species_id: string | null
  details: string | null
}

interface Props { collection?: string }

const ACTION_LABELS: Record<string, { icon: React.ReactNode; label: string }> = {
  create: { icon: <PlusCircle size={14} />, label: 'Thêm mới' },
  update: { icon: <Edit2 size={14} />, label: 'Cập nhật' },
  delete: { icon: <Trash2 size={14} />, label: 'Xóa' },
  bulk_import: { icon: <Database size={14} />, label: 'Import hàng loạt' },
  table_test: { icon: <Settings size={14} />, label: 'Test hệ thống' },
}

export default function AuditLog({ collection }: Props) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (collection) params.set('collection', collection)
    const res = await fetch(`/api/audit-log?${params}`)
    if (res.ok) {
      const { data } = await res.json()
      setLogs(data || [])
    } else {
      setLogs([])
    }
    setLoading(false)
  }, [collection])

  useEffect(() => { load() }, [load])

  const formatTime = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <section className="admin-audit-card" aria-labelledby="audit-log-heading">
      <div className="admin-audit-card__header">
        <div className="admin-audit-card__brand">
          <div className="admin-audit-card__icon-wrap" aria-hidden="true">
            <ClipboardList size={18} />
          </div>
          <div>
            <h3 id="audit-log-heading" className="admin-audit-card__title">
              Nhật ký thay đổi
            </h3>
            <p className="admin-audit-card__subtitle">
              Lịch sử ghi nhận thao tác dữ liệu tự động (Audit Trail)
            </p>
          </div>
        </div>

        <button
          className="admin-refresh-btn"
          onClick={load}
          disabled={loading}
          type="button"
          title="Tải lại nhật ký kiểm toán mới nhất"
        >
          <RotateCw size={14} className={loading ? 'admin-spin' : ''} aria-hidden="true" />
          <span>{loading ? 'Đang tải...' : 'Làm mới'}</span>
        </button>
      </div>

      {loading && <p style={{ color: 'var(--color-muted)' }}>Đang tải...</p>}

      {!loading && logs.length === 0 && (
        <p style={{ color: 'var(--color-muted)', textAlign: 'center', padding: '2rem' }}>
          Chưa có thao tác nào được ghi lại.
        </p>
      )}

      {!loading && logs.length > 0 && (
        <div className="admin-table-scroll" style={{ maxHeight: '400px' }}>
          <table className="admin-table" style={{ fontSize: '0.85rem' }}>
            <thead>
              <tr>
                <th style={{ width: '140px' }}>Thời gian</th>
                <th style={{ width: '120px' }}>Thao tác</th>
                <th>Người thực hiện</th>
                <th>Chi tiết</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => {
                const act = ACTION_LABELS[log.action] || { icon: '❓', label: log.action }
                return (
                  <tr key={log.id}>
                    <td style={{ color: 'var(--color-muted)', whiteSpace: 'nowrap' }}>
                      {formatTime(log.created_at)}
                    </td>
                    <td>
                      <span className={`audit-badge audit-badge--${log.action}`}>
                        {act.icon} {act.label}
                      </span>
                    </td>
                    <td>{log.user_email?.split('@')[0] || 'system'}</td>
                    <td style={{ color: 'var(--color-body)' }}>
                      {log.details || '—'}
                      {log.species_id && <code style={{ marginLeft: '0.5rem', fontSize: '0.75rem' }}>{log.species_id}</code>}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

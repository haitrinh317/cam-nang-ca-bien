'use client'

import { useEffect, useState, useCallback } from 'react'
import { db } from '@/lib/supabase-browser'

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

const ACTION_LABELS: Record<string, { icon: string; label: string }> = {
  create: { icon: '➕', label: 'Thêm mới' },
  update: { icon: '✏️', label: 'Cập nhật' },
  delete: { icon: '🗑️', label: 'Xóa' },
  bulk_import: { icon: '📥', label: 'Import hàng loạt' },
  table_test: { icon: '🔧', label: 'Test hệ thống' },
}

export default function AuditLog({ collection }: Props) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    let query = db
      .from('audit_log')
      .select('id, created_at, user_email, action, collection_id, species_id, details')
      .order('created_at', { ascending: false })
      .limit(50)

    if (collection) query = query.eq('collection_id', collection)

    const { data } = await query
    setLogs(data || [])
    setLoading(false)
  }, [collection])

  useEffect(() => { load() }, [load])

  const formatTime = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="audit-log-section">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <h3 style={{ margin: 0 }}>📋 Nhật ký thay đổi</h3>
        <button className="btn btn-outline" onClick={load} type="button" style={{ fontSize: '0.8rem', padding: '0.3rem 0.8rem' }}>
          Làm mới
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
    </div>
  )
}

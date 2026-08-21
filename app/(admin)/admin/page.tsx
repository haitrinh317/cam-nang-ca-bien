import { createServerClient } from '@/lib/supabase-server'
import Link from 'next/link'
import '@/styles/admin-dashboard.css'

const ACTION_MAP: Record<string, { label: string; cls: string }> = {
  create:      { label: 'Thêm mới',  cls: 'audit-badge--create' },
  update:      { label: 'Cập nhật',  cls: 'audit-badge--update' },
  delete:      { label: 'Xóa',       cls: 'audit-badge--delete' },
  bulk_import: { label: 'Import',    cls: 'audit-badge--bulk_import' },
  bulk_delete: { label: 'Xóa hàng loạt', cls: 'audit-badge--delete' },
}

export default async function AdminDashboard() {
  const db = createServerClient()

  const [
    { count: caBienCount },
    { count: thucVatCount },
    { data: recentAudit },
  ] = await Promise.all([
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'ca-bien'),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'thuc-vat-bien'),
    db.from('audit_log')
      .select('id, created_at, user_email, action, details')
      .order('created_at', { ascending: false })
      .limit(8),
  ])

  const total = (caBienCount || 0) + (thucVatCount || 0)

  // Volume breakdown (Cá biển)
  const volPromises = [1, 2, 3, 4, 5].map(v => 
    db.from('species').select('*', { count: 'exact', head: true })
      .eq('collection_id', 'ca-bien').eq('volume', v)
  )
  const volResults = await Promise.all(volPromises)
  const volCounts = volResults.map(r => r.count ?? 0)
  const maxVol = Math.max(...volCounts, 1)

  return (
    <div className="admin-page">
      <div className="admin-page__header">
        <div>
          <h1 className="admin-page__title">Tổng quan Cơ sở dữ liệu</h1>
          <p style={{ color: 'var(--color-muted)', marginTop: '0.5rem' }}>Theo dõi các số liệu thống kê và hoạt động gần đây của hệ thống</p>
        </div>
      </div>

      <div className="admin-kpi-grid">
        <div className="admin-kpi-card">
          <h3 className="admin-kpi-card__title">Tổng số loài</h3>
          <p className="admin-kpi-card__value">{total}</p>
        </div>
        <div className="admin-kpi-card">
          <h3 className="admin-kpi-card__title">Cá biển</h3>
          <p className="admin-kpi-card__value">{caBienCount || 0}</p>
        </div>
        <div className="admin-kpi-card">
          <h3 className="admin-kpi-card__title">Thực vật biển</h3>
          <p className="admin-kpi-card__value">{thucVatCount || 0}</p>
        </div>
      </div>

      <div className="admin-chart-card">
        <h2>Phân bố cá biển theo Tập</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {volCounts.map((count, index) => {
            const pct = Math.max((count / maxVol) * 100, 2)
            return (
              <div key={index} className="admin-vol-bar-row">
                <div className="admin-vol-bar-label">Tập {['I', 'II', 'III', 'IV', 'V'][index]}</div>
                <div className="admin-vol-bar-track">
                  <div className="admin-vol-bar-fill" style={{ width: `${pct}%` }}>
                    {pct > 10 ? count : ''}
                  </div>
                </div>
                <div className="admin-vol-bar-value">{count}</div>
              </div>
            )
          })}
        </div>
      </div>

      <div style={{ marginTop: 'var(--space-3xl)' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: 'var(--space-xl)', fontWeight: 600 }}>Hoạt động gần đây</h2>
        <div className="admin-table-scroll">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Hành động</th>
                <th>Người thực hiện</th>
                <th>Chi tiết</th>
                <th>Thời gian</th>
              </tr>
            </thead>
            <tbody>
              {recentAudit?.length === 0 && (
                <tr><td colSpan={4} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-muted)' }}>Chưa có hoạt động nào.</td></tr>
              )}
              {recentAudit?.map(log => {
                const act = ACTION_MAP[log.action] || { label: log.action, cls: 'audit-badge--update' }
                return (
                  <tr key={log.id}>
                    <td><span className={`audit-badge ${act.cls}`}>{act.label}</span></td>
                    <td style={{ fontWeight: 500 }}>{log.user_email || 'System'}</td>
                    <td style={{ color: 'var(--color-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
                      {typeof log.details === 'object' ? JSON.stringify(log.details) : String(log.details)}
                    </td>
                    <td style={{ color: 'var(--color-muted)', fontSize: '0.85rem' }}>
                      {new Date(log.created_at).toLocaleString('vi-VN')}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

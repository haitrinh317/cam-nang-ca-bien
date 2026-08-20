import { createServerClient } from '@/lib/supabase-server'

export default async function AdminDashboard() {
  const db = createServerClient()

  // Quick stats
  const [{ count: totalSpecies }, { data: byColl }] = await Promise.all([
    db.from('species').select('*', { count: 'exact', head: true }),
    db.from('species').select('collection_id').then(r =>
      // Group by collection_id client-side
      ({ data: r.data })),
  ])

  const byVol = await db
    .from('species')
    .select('volume')
    .eq('collection_id', 'ca-bien')

  const volCounts: Record<number, number> = {}
  byVol.data?.forEach(row => {
    volCounts[row.volume] = (volCounts[row.volume] || 0) + 1
  })

  return (
    <div className="admin-page">
      <h1 className="admin-page__title">📊 Tổng quan</h1>

      <div className="admin-stats-grid">
        <div className="admin-stat-card">
          <div className="admin-stat-card__number">{totalSpecies?.toLocaleString() || '—'}</div>
          <div className="admin-stat-card__label">Tổng số loài</div>
        </div>
        {Object.entries(volCounts).sort(([a], [b]) => Number(a) - Number(b)).map(([vol, count]) => (
          <div className="admin-stat-card" key={vol}>
            <div className="admin-stat-card__number">{count}</div>
            <div className="admin-stat-card__label">Tập {vol} — Cá biển</div>
          </div>
        ))}
      </div>

      <div className="admin-quick-links">
        <h2>Truy cập nhanh</h2>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '1rem' }}>
          <a href="/admin/ca-bien" className="btn btn-outline">🐟 Quản lý Cá biển</a>
          <a href="/admin/thuc-vat-bien" className="btn btn-outline">🌿 Quản lý Thực vật biển</a>
          <a href="/ca-bien" className="btn btn-outline" target="_blank">↗ Xem trang public</a>
        </div>
      </div>
    </div>
  )
}

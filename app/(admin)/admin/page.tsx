import { createServerClient } from '@/lib/supabase-server'

export default async function AdminDashboard() {
  const db = createServerClient()

  const [{ count: totalSpecies }, byVolRes] = await Promise.all([
    db.from('species').select('*', { count: 'exact', head: true }),
    db.from('species').select('volume,collection_id').eq('collection_id', 'ca-bien'),
  ])

  const volCounts: Record<number, number> = {}
  byVolRes.data?.forEach(row => {
    volCounts[row.volume] = (volCounts[row.volume] || 0) + 1
  })

  return (
    <div className="admin-page">
      <div className="admin-page__header">
        <div>
          <h1 className="admin-page__title">Tổng quan</h1>
          <p className="admin-page__subtitle">Cơ sở dữ liệu Sinh vật biển Việt Nam</p>
        </div>
      </div>

      <div className="admin-stats-grid">
        <div className="admin-stat-card">
          <div className="admin-stat-card__number">{totalSpecies?.toLocaleString() ?? '—'}</div>
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
        <div className="admin-action-grid">
          <a href="/admin/ca-bien" className="admin-action-card">
            <span className="admin-action-card__icon">🐟</span>
            <span className="admin-action-card__label">Quản lý Cá biển</span>
            <span className="admin-action-card__desc">Xem, tìm kiếm và chỉnh sửa loài cá</span>
          </a>
          <a href="/admin/thuc-vat-bien" className="admin-action-card">
            <span className="admin-action-card__icon">🌿</span>
            <span className="admin-action-card__label">Quản lý Thực vật biển</span>
            <span className="admin-action-card__desc">Rong biển, cỏ biển, tảo biển</span>
          </a>
          <a href="/ca-bien" target="_blank" className="admin-action-card">
            <span className="admin-action-card__icon">↗</span>
            <span className="admin-action-card__label">Xem trang public</span>
            <span className="admin-action-card__desc">Mở website trong tab mới</span>
          </a>
        </div>
      </div>
    </div>
  )
}


import { createServerClient } from '@/lib/supabase-server'
import Link from 'next/link'
import '@/styles/admin.css'
import { Database, Fish, Leaf, Shrimp, BookOpen, Clock, ArrowRight, BookCheck } from 'lucide-react'

const ACTION_MAP: Record<string, { label: string; cls: string }> = {
  create:      { label: 'Thêm mới',       cls: 'audit-badge--create' },
  update:      { label: 'Cập nhật',       cls: 'audit-badge--update' },
  delete:      { label: 'Xóa',            cls: 'audit-badge--delete' },
  bulk_import: { label: 'Import dữ liệu', cls: 'audit-badge--bulk_import' },
  bulk_delete: { label: 'Xóa hàng loạt',  cls: 'audit-badge--delete' },
}

const MONOGRAPHS = [
  {
    roman: 'I',
    title: 'Cá nhám & Cá đuối',
    latin: 'Chondrichthyes (Cá sụn)',
  },
  {
    roman: 'II',
    title: 'Cá trích, Cá chình & Cá mòi',
    latin: 'Clupeiformes, Anguilliformes',
  },
  {
    roman: 'III',
    title: 'Cá mú, Cá hồng & Cá đù',
    latin: 'Perciformes (Lutjanidae, Serranidae)',
  },
  {
    roman: 'IV',
    title: 'Bộ Cá vược (Phần 1)',
    latin: 'Perciformes (Serranidae, Carangidae)',
  },
  {
    roman: 'V',
    title: 'Bộ Cá vược (Phần 2)',
    latin: 'Perciformes (Labridae, Gobiidae)',
  },
]

function formatLogDetails(details: unknown): string {
  if (!details) return '—'
  if (typeof details === 'string') {
    try {
      const parsed = JSON.parse(details)
      return formatLogDetails(parsed)
    } catch {
      return details
    }
  }
  if (typeof details === 'object') {
    const obj = details as Record<string, unknown>
    const parts: string[] = []
    if (obj.vn_name) parts.push(`Tên VN: "${obj.vn_name}"`)
    if (obj.scientific_name) parts.push(`Tên KH: ${obj.scientific_name}`)
    if (obj.volume) parts.push(`Tập ${obj.volume}`)
    if (obj.count) parts.push(`Số lượng: ${obj.count}`)
    if (parts.length > 0) return parts.join(' · ')
    return JSON.stringify(obj).replace(/["{}]/g, '').slice(0, 80)
  }
  return String(details)
}

export default async function AdminDashboard() {
  const db = createServerClient()

  const [
    { count: totalCount },
    { count: caBienCount },
    { count: thucVatCount },
    { count: giapXacCount },
    { count: ranBienCount },
    { count: litCount },
    { data: recentAudit },
  ] = await Promise.all([
    db.from('species').select('*', { count: 'exact', head: true }).is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'ca-bien').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'thuc-vat-bien').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'giap-xac').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'ran-bien').is('deleted_at', null),
    db.from('literature_sources').select('*', { count: 'exact', head: true }),
    db.from('audit_log')
      .select('id, created_at, user_email, action, details')
      .order('created_at', { ascending: false })
      .limit(8),
  ])

  const total = totalCount || (caBienCount || 0) + (thucVatCount || 0) + (giapXacCount || 0) + (ranBienCount || 0)

  // Volume breakdown (Cá biển tập 1-5)
  const volPromises = [1, 2, 3, 4, 5].map((v) =>
    db
      .from('species')
      .select('*', { count: 'exact', head: true })
      .eq('collection_id', 'ca-bien')
      .eq('volume', v)
      .is('deleted_at', null)
  )
  const volResults = await Promise.all(volPromises)
  const volCounts = volResults.map((r) => r.count ?? 0)
  const totalVolSpecies = volCounts.reduce((acc, c) => acc + c, 0) || 1

  return (
    <div className="admin-page">
      <header className="admin-page__header">
        <div>
          <h1 className="admin-page__title">Tổng Quan Hệ Thống</h1>
          <p className="admin-page__subtitle">
            Cơ sở dữ liệu Đa dạng Sinh học Biển Việt Nam — Một dự án được phát triển bởi haitrinh
          </p>
        </div>
      </header>

      {/* KPI Bento Grid */}
      <section className="admin-kpi-grid" aria-label="Chỉ số chính">
        <div className="admin-kpi-card">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Tổng số loài</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Database size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{total.toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Toàn bộ kho dữ liệu số hóa</p>
        </div>

        <div className="admin-kpi-card">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Cá biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Fish size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(caBienCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Tập I – V &amp; Atlas cá rạn</p>
        </div>

        <div className="admin-kpi-card admin-kpi-card--thucvat">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Thực vật biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Leaf size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(thucVatCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Rong biển &amp; cỏ biển</p>
        </div>

        <div className="admin-kpi-card admin-kpi-card--giapxac">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Giáp xác biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Shrimp size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(giapXacCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Tôm biển &amp; tôm tít</p>
        </div>

        <div className="admin-kpi-card admin-kpi-card--ranbien">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Rắn biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><span style={{ fontSize: '16px', lineHeight: 1 }}>🐍</span></div>
          </div>
          <p className="admin-kpi-card__value">{(ranBienCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Rắn biển &amp; đẻn biển</p>
        </div>

        <div className="admin-kpi-card admin-kpi-card--lit">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Tài liệu gốc</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><BookOpen size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(litCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Chuyên khảo &amp; sách nguồn</p>
        </div>
      </section>

      {/* Volume Distribution Bento Dossier Section */}
      <section className="admin-volumes-section" aria-labelledby="volumes-heading">
        <div className="admin-volumes-header">
          <div>
            <h2 id="volumes-heading" className="admin-volumes-title">
              Cấu Trúc Bộ Danh Mục Cá Biển Việt Nam
            </h2>
            <p className="admin-volumes-subtitle">
              Phân bố số lượng loài theo 5 tập chuyên khảo tài liệu phân loại học gốc
            </p>
          </div>
          <div className="admin-volumes-badge">
            <BookCheck size={14} aria-hidden="true" />
            <span>5 TẬP CHUYÊN KHẢO</span>
          </div>
        </div>

        {/* Proportional Spectrum Ribbon */}
        <div className="admin-spectrum-bar" role="meter" aria-label="Tỷ lệ phân bố 5 tập">
          {volCounts.map((count, index) => {
            const volNum = index + 1
            const pct = ((count / totalVolSpecies) * 100).toFixed(1)
            return (
              <div
                key={index}
                className={`admin-spectrum-segment admin-spectrum-segment--${volNum}`}
                style={{ width: `${pct}%` }}
                title={`Tập ${MONOGRAPHS[index].roman}: ${count} loài (${pct}%)`}
              />
            )
          })}
        </div>

        {/* Bento Volume Tiles */}
        <div className="admin-vol-grid">
          {volCounts.map((count, index) => {
            const volNum = index + 1
            const m = MONOGRAPHS[index]
            const sharePct = ((count / totalVolSpecies) * 100).toFixed(1)

            return (
              <Link
                key={index}
                href={`/admin/ca-bien?vol=${volNum}`}
                className={`admin-vol-tile admin-vol-tile--${volNum}`}
                title={`Nhấn để quản lý dữ liệu Tập ${m.roman}`}
              >
                <div>
                  <div className="admin-vol-tile__head">
                    <span className={`admin-vol-tile__badge admin-vol-tile__badge--${volNum}`}>
                      TẬP {m.roman}
                    </span>
                    <span className="admin-vol-tile__pct">{sharePct}%</span>
                  </div>
                  <h3 className="admin-vol-tile__title">{m.title}</h3>
                  <span className="admin-vol-tile__latin">{m.latin}</span>
                </div>

                <div className="admin-vol-tile__foot">
                  <div className="admin-vol-tile__count">
                    <span className="admin-vol-tile__num">{count.toLocaleString('vi-VN')}</span>
                    <span className="admin-vol-tile__unit">loài</span>
                  </div>
                  <span className="admin-vol-tile__arrow" aria-hidden="true">
                    <ArrowRight size={14} />
                  </span>
                </div>
              </Link>
            )
          })}
        </div>
      </section>

      {/* Activity Log Stream */}
      <section className="admin-activity-card" aria-labelledby="activity-heading">
        <div className="admin-activity-card__header">
          <div>
            <h2 id="activity-heading">Nhật Ký Hoạt Động Gần Đây</h2>
            <p className="admin-page__subtitle" style={{ margin: 0 }}>
              Ghi nhận theo thời gian thực từ cơ chế kiểm toán bảo mật (Audit Log)
            </p>
          </div>
          <Link href="/admin/ca-bien" className="btn btn-outline btn-sm">
            <span>Quản lý dữ liệu</span>
            <ArrowRight size={13} aria-hidden="true" />
          </Link>
        </div>

        <div className="admin-table-scroll">
          <table className="admin-table">
            <thead>
              <tr>
                <th style={{ width: 140 }}>Hành động</th>
                <th style={{ width: 220 }}>Tài khoản</th>
                <th>Chi tiết thay đổi</th>
                <th style={{ width: 180, textAlign: 'right' }}>Thời gian</th>
              </tr>
            </thead>
            <tbody>
              {(!recentAudit || recentAudit.length === 0) && (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--color-muted)' }}>
                    Chưa có nhật ký hoạt động nào được ghi nhận.
                  </td>
                </tr>
              )}
              {recentAudit?.map((log) => {
                const act = ACTION_MAP[log.action] || {
                  label: log.action,
                  cls: 'audit-badge--update',
                }
                const formattedDetails = formatLogDetails(log.details)
                const dateStr = new Date(log.created_at).toLocaleString('vi-VN', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })

                return (
                  <tr key={log.id}>
                    <td>
                      <span className={`audit-badge ${act.cls}`}>{act.label}</span>
                    </td>
                    <td style={{ fontWeight: 600, color: 'var(--color-ink-2)' }}>
                      {log.user_email || 'System'}
                    </td>
                    <td>
                      <span className="admin-details-pill" title={formattedDetails}>
                        {formattedDetails}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', color: 'var(--color-muted)', fontSize: '0.82rem', fontFamily: 'var(--font-outlier)' }}>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                        <Clock size={12} aria-hidden="true" />
                        {dateStr}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

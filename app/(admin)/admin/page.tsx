import type { Metadata } from 'next'
import { createServerClient } from '@/lib/supabase-server'
import Link from 'next/link'
import '@/styles/admin.css'
import '@/styles/admin-command.css'
import AuditLogStream from '@/components/admin/AuditLogStream'
import {
  Database,
  Fish,
  Leaf,
  Shrimp,
  Turtle,
  Biohazard,
  Shell,
  Sparkles,
  Waves,
  BookOpen,
  Clock,
  ArrowRight,
  BookCheck,
  Activity,
  CheckCircle2,
  Image,
  ShieldCheck,
  ExternalLink,
  Microscope,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Trung Tâm Chỉ Huy Quản Trị — Cẩm Nang Sinh Vật Biển',
  description: 'Trung tâm giám sát và quản trị số hóa đa dạng sinh học biển Việt Nam — Dự án cá nhân phát triển bởi haitrinh.',
}

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
    { count: boSatCount },
    { count: sinhVatDocCount },
    { count: thanMemCount },
    { count: sanHoCount },
    { count: thuBienCount },
    { count: dvpdCount },
    { count: litCount },
    { count: photosCount },
    { count: wormsVerifiedCount },
    { count: vnRedListCount },
    { data: recentAudit, count: auditTotalCount },
    // Volume breakdown (Cá biển tập 1-5) — gộp vào 1 Promise.all, tránh waterfall
    ...volResults
  ] = await Promise.all([
    db.from('species').select('*', { count: 'exact', head: true }).is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'ca-bien').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'thuc-vat-bien').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'giap-xac').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'bo-sat-bien').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'sinh-vat-doc').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'than-mem').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'san-ho').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'thu-bien').is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', 'dong-vat-phu-du').is('deleted_at', null),
    db.from('literature_sources').select('*', { count: 'exact', head: true }),
    db.from('species_photos').select('*', { count: 'exact', head: true }),
    db.from('species').select('*', { count: 'exact', head: true }).not('worms_id', 'is', null).is('deleted_at', null),
    db.from('species').select('*', { count: 'exact', head: true }).not('vn_status', 'is', null).is('deleted_at', null),
    db.from('audit_log')
      .select('id, created_at, user_email, action, collection_id, species_id, details', { count: 'exact' })
      .order('created_at', { ascending: false })
      .range(0, 9),
    ...[1, 2, 3, 4, 5].map((v) =>
      db.from('species').select('*', { count: 'exact', head: true })
        .eq('collection_id', 'ca-bien').eq('volume', v).is('deleted_at', null)
    ),
  ])

  const total = totalCount || (
    (caBienCount || 0) +
    (thucVatCount || 0) +
    (giapXacCount || 0) +
    (boSatCount || 0) +
    (sinhVatDocCount || 0) +
    (thanMemCount || 0) +
    (sanHoCount || 0) +
    (thuBienCount || 0) +
    (dvpdCount || 0)
  )

  const volCounts = volResults.map((r) => r.count ?? 0)
  const totalVolSpecies = volCounts.reduce((acc, c) => acc + c, 0) || 1

  // Telemetry ratios
  const wormsPct = Math.min(100, Math.round(((wormsVerifiedCount || 0) / (total || 1)) * 100))
  const redListPct = Math.min(100, Math.round(((vnRedListCount || 0) / (total || 1)) * 100))
  const totalPhotos = photosCount || 4906

  // Grand spectrum distribution
  const GRAND_SPECTRUM = [
    { name: 'Cá biển', count: caBienCount || 0, color: '#00f0d0', slug: 'ca-bien' },
    { name: 'Thực vật biển', count: thucVatCount || 0, color: '#10b981', slug: 'thuc-vat-bien' },
    { name: 'Giáp xác', count: giapXacCount || 0, color: '#f87171', slug: 'giap-xac' },
    { name: 'Thân mềm', count: thanMemCount || 0, color: '#c084fc', slug: 'than-mem' },
    { name: 'Sinh vật độc', count: sinhVatDocCount || 0, color: '#fb7185', slug: 'sinh-vat-doc' },
    { name: 'San hô', count: sanHoCount || 0, color: '#f472b6', slug: 'san-ho' },
    { name: 'Thú biển', count: thuBienCount || 0, color: '#38bdf8', slug: 'thu-bien' },
    { name: 'Bò sát biển', count: boSatCount || 0, color: '#f59e0b', slug: 'bo-sat-bien' },
    { name: 'Động vật phù du', count: dvpdCount || 0, color: '#06b6d4', slug: 'dong-vat-phu-du' },
  ]

  return (
    <div className="admin-page">
      {/* Marine Command Header */}
      <header className="admin-page__header">
        <div>
          <h1 className="admin-page__title">Trung Tâm Chỉ Huy Dữ Liệu</h1>
          <p className="admin-page__subtitle">
            Hệ thống giám sát &amp; quản trị CSDL Đa dạng Sinh học Biển Việt Nam — 9 Phân hệ sinh thái
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <Link href="/admin/literature" className="btn btn-outline btn-sm" title="Quản lý Chuyên khảo & Tài liệu nguồn">
            <BookOpen size={14} aria-hidden="true" />
            <span>Tài liệu nguồn ({litCount || 0})</span>
          </Link>
          <Link href="/" className="btn btn-primary btn-sm" target="_blank" title="Mở trang tra cứu người dùng">
            <span>Mở tra cứu</span>
            <ExternalLink size={14} aria-hidden="true" />
          </Link>
        </div>
      </header>

      {/* ── BENTO COMMAND HERO & TELEMETRY HEALTH MATRIX ── */}
      <section className="admin-command-hero" aria-label="Chỉ số tổng quan và sức khỏe dữ liệu">
        {/* Spotlight Hero Card */}
        <div className="admin-hero-card">
          <div>
            <div className="admin-hero-card__head">
              <span className="admin-live-badge">
                <span className="admin-live-pulse" aria-hidden="true" />
                <span>CSDL TRỰC TUYẾN · 9 PHÂN HỆ</span>
              </span>
              <span style={{ fontSize: '0.74rem', color: 'rgba(240, 253, 249, 0.5)', fontFamily: 'var(--font-outlier)' }}>
                Supabase RLS Protected
              </span>
            </div>

            <p className="admin-hero-card__label">Tổng số loài sinh vật biển đã số hóa</p>
            <div className="admin-hero-card__stat">
              <span className="admin-hero-card__num">{total.toLocaleString('vi-VN')}</span>
              <span className="admin-hero-card__unit"> loài bảo tồn</span>
            </div>

            {/* Proportional Grand Diversity Spectrum Bar */}
            <div className="admin-grand-spectrum" role="meter" aria-label="Tỷ lệ phân bố 8 phân hệ">
              {GRAND_SPECTRUM.map((col) => {
                const pct = ((col.count / total) * 100).toFixed(1)
                return (
                  <div
                    key={col.slug}
                    className="admin-spectrum-seg"
                    style={{ width: `${pct}%`, background: col.color }}
                    title={`${col.name}: ${col.count.toLocaleString('vi-VN')} loài (${pct}%)`}
                  />
                )
              })}
            </div>
          </div>

          {/* Quick Collection Chips */}
          <div className="admin-collection-chips">
            {GRAND_SPECTRUM.map((col) => (
              <Link
                key={col.slug}
                href={`/admin/${col.slug}`}
                className="admin-collection-chip"
                title={`Mở quản trị ${col.name}`}
              >
                <span className="admin-collection-chip__dot" style={{ background: col.color }} />
                <span>{col.name}</span>
                <span style={{ opacity: 0.6, fontFamily: 'var(--font-outlier)' }}> ({col.count})</span>
              </Link>
            ))}
          </div>
        </div>

        {/* Data Health Telemetry Card */}
        <div className="admin-health-card">
          <div>
            <div className="admin-health-card__title">
              <span>Chỉ Số Hoàn Thiện Số Hóa</span>
              <Activity size={15} style={{ color: '#00f0d0' }} aria-hidden="true" />
            </div>

            <div className="admin-health-meters">
              {/* WoRMS Meter */}
              <div className="admin-health-meter">
                <div className="admin-health-meter__meta">
                  <span className="admin-health-meter__label">
                    <CheckCircle2 size={13} style={{ color: '#00f0d0' }} aria-hidden="true" />
                    <span>Định danh WoRMS Valid</span>
                  </span>
                  <span className="admin-health-meter__val">
                    {(wormsVerifiedCount || 0).toLocaleString('vi-VN')} <span style={{ color: 'rgba(255,255,255,0.4)' }}>({wormsPct}%)</span>
                  </span>
                </div>
                <div className="admin-health-meter__track">
                  <div className="admin-health-meter__bar" style={{ width: `${wormsPct}%`, background: '#00f0d0' }} />
                </div>
              </div>

              {/* Red List VAST Meter */}
              <div className="admin-health-meter">
                <div className="admin-health-meter__meta">
                  <span className="admin-health-meter__label">
                    <ShieldCheck size={13} style={{ color: '#f59e0b' }} aria-hidden="true" />
                    <span>Hồ sơ Sách Đỏ VAST 2024</span>
                  </span>
                  <span className="admin-health-meter__val">
                    {(vnRedListCount || 0).toLocaleString('vi-VN')} <span style={{ color: 'rgba(255,255,255,0.4)' }}>({redListPct}%)</span>
                  </span>
                </div>
                <div className="admin-health-meter__track">
                  <div className="admin-health-meter__bar" style={{ width: `${redListPct}%`, background: '#f59e0b' }} />
                </div>
              </div>

              {/* Photos Meter */}
              <div className="admin-health-meter">
                <div className="admin-health-meter__meta">
                  <span className="admin-health-meter__label">
                    <Image size={13} style={{ color: '#38bdf8' }} aria-hidden="true" />
                    <span>Thư viện ảnh mẫu vật</span>
                  </span>
                  <span className="admin-health-meter__val">
                    {totalPhotos.toLocaleString('vi-VN')} <span style={{ color: 'rgba(255,255,255,0.4)' }}>ảnh</span>
                  </span>
                </div>
                <div className="admin-health-meter__track">
                  <div className="admin-health-meter__bar" style={{ width: '100%', background: '#38bdf8' }} />
                </div>
              </div>
            </div>
          </div>

          <div style={{ marginTop: '1.25rem', paddingTop: '0.85rem', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', color: 'rgba(240,253,249,0.5)' }}>
            <span>Độ phủ: ~{((totalPhotos / total)).toFixed(1)} ảnh/loài</span>
            <span>Chuẩn dữ liệu: WoRMS Aphia</span>
          </div>
        </div>
      </section>

      {/* ── BENTO GROUP 1: TÀI NGUYÊN NGƯ HỌC & QUẦN XÃ THỰC VẬT ── */}
      <div className="admin-group-header">
        <span className="admin-group-title">
          <Fish size={15} style={{ color: '#00f0d0' }} aria-hidden="true" />
          <span>Tài Nguyên Ngư Học &amp; Quần Xã Thực Vật</span>
        </span>
        <span className="admin-group-count">4 Phân hệ</span>
      </div>

      <section className="admin-kpi-grid" aria-label="Tài nguyên ngư học và thực vật biển">
        <Link href="/admin/ca-bien" className="admin-kpi-card admin-kpi-card--cabien" title="Quản lý Cá biển Việt Nam">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Cá biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Fish size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(caBienCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Tập I – V &amp; Atlas cá rạn san hô</p>
        </Link>

        <Link href="/admin/thuc-vat-bien" className="admin-kpi-card admin-kpi-card--thucvat" title="Quản lý Thực vật biển">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Thực vật biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Leaf size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(thucVatCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Rong biển, cỏ biển &amp; TV ngập mặn</p>
        </Link>

        <Link href="/admin/giap-xac" className="admin-kpi-card admin-kpi-card--giapxac" title="Quản lý Giáp xác biển">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Giáp xác biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Shrimp size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(giapXacCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Tôm biển, tôm tít, cua &amp; ghẹ</p>
        </Link>

        <Link href="/admin/than-mem" className="admin-kpi-card admin-kpi-card--thanmem" title="Quản lý Động vật thân mềm">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Thân mềm biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Shell size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(thanMemCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Ốc, sò, nghêu, mực &amp; bạch tuộc</p>
        </Link>
      </section>

      {/* ── BENTO GROUP 2: ĐỘNG VẬT ĐẶC THÙ & BẢO TỒN CẤP THIẾT ── */}
      <div className="admin-group-header">
        <span className="admin-group-title">
          <Turtle size={15} style={{ color: '#f59e0b' }} aria-hidden="true" />
          <span>Động Vật Đặc Thù &amp; Bảo Tồn Cấp Thiết</span>
        </span>
        <span className="admin-group-count">5 Phân hệ</span>
      </div>

      <section className="admin-kpi-grid" aria-label="Động vật đặc thù và bảo tồn">
        <Link href="/admin/bo-sat-bien" className="admin-kpi-card admin-kpi-card--bosat" title="Quản lý Bò sát biển">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Bò sát biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Turtle size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(boSatCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Rùa biển, rắn biển &amp; cá sấu hoa cà</p>
        </Link>

        <Link href="/admin/thu-bien" className="admin-kpi-card admin-kpi-card--thubien" title="Quản lý Thú biển Việt Nam">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Thú biển</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Waves size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(thuBienCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Cá voi, cá heo &amp; bò biển Dugong</p>
        </Link>

        <Link href="/admin/san-ho" className="admin-kpi-card admin-kpi-card--sanho" title="Quản lý San hô Việt Nam">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">San hô</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Sparkles size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(sanHoCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">San hô tám ngăn vùng Nam &amp; quần thể</p>
        </Link>

        <Link href="/admin/sinh-vat-doc" className="admin-kpi-card admin-kpi-card--doc" title="Quản lý Động vật độc biển">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Động vật độc</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Biohazard size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(sinhVatDocCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Nọc độc, ngộ độc &amp; gai độc biển</p>
        </Link>

        <Link href="/admin/dong-vat-phu-du" className="admin-kpi-card admin-kpi-card--dongvatphudu" title="Quản lý Động vật phù du">
          <div className="admin-kpi-card__header">
            <h3 className="admin-kpi-card__title">Động vật phù du</h3>
            <div className="admin-kpi-card__icon" aria-hidden="true"><Microscope size={18} /></div>
          </div>
          <p className="admin-kpi-card__value">{(dvpdCount || 0).toLocaleString('vi-VN')}</p>
          <p className="admin-kpi-card__sub">Copepoda &amp; Phù du chân mái chèo</p>
        </Link>
      </section>

      {/* ── BENTO VOLUME DOSSIER (Cá biển 5 tập chuyên khảo) ── */}
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

      {/* ── ACTIVITY LOG STREAM ── */}
      <AuditLogStream initialLogs={(recentAudit || []) as import('@/components/admin/AuditLogStream').LogEntry[]} initialTotal={auditTotalCount || 0} />
    </div>
  )
}

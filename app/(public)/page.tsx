import { getCollections } from '@/lib/collections'
import { createServerClient } from '@/lib/supabase-server'
import GlobalSearch from '@/components/search/GlobalSearch'
import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Bảo tàng Hải dương học — Tra cứu Sinh vật biển Việt Nam',
  description: 'Cơ sở dữ liệu số hóa sinh vật biển Việt Nam — Viện Hải dương học, Nha Trang.',
}

export default async function HomePage() {
  const collections = await getCollections()
  const db = createServerClient()

  // Realtime stats
  const { count: totalSpecies } = await db
    .from('species')
    .select('*', { count: 'exact', head: true })

  const { data: familyRows } = await db
    .from('species')
    .select('tax_family_latin')
    .not('tax_family_latin', 'is', null)

  const familyCount = familyRows
    ? new Set(familyRows.map(r => r.tax_family_latin)).size
    : '—'

  return (
    <>
      <section className="hero" aria-label="Giới thiệu">
        <div className="hero__bg" aria-hidden="true" />
        <div className="hero__content">
          <h1>Danh mục Sinh vật biển <span className="hero__accent">Việt Nam</span></h1>
          <p>Cơ sở dữ liệu số hóa phục vụ nghiên cứu khoa học — Viện Hải dương học, Nha Trang.</p>
          <GlobalSearch />

          {/* Live stats */}
          <div className="hero__stats">
            <div className="hero__stat">
              <span className="hero__stat-num">{totalSpecies?.toLocaleString() || '—'}</span>
              <span className="hero__stat-label">Loài</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">{familyCount}</span>
              <span className="hero__stat-label">Họ</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">{collections.filter(c => c.status === 'active').length}</span>
              <span className="hero__stat-label">Bộ sưu tập</span>
            </div>
          </div>
        </div>
      </section>

      <section className="section-browse" aria-label="Duyệt theo tập">
        <div className="section-browse-header">
          <h2 className="section-browse-title">Bộ sưu tập Sinh vật biển</h2>
        </div>
        <div className="vol-grid">
          {collections.map(col => (
            <Link
              key={col.slug}
              href={col.status === 'draft' ? '#' : `/${col.slug}`}
              className={`vol-card${col.status === 'draft' ? ' vol-card--draft' : ''}`}
              aria-disabled={col.status === 'draft'}
              style={{
                opacity: col.status === 'draft' ? 0.55 : 1,
                pointerEvents: col.status === 'draft' ? 'none' : undefined,
              }}
            >
              <span className="vol-card-num" style={{ fontSize: '2.2rem' }}>{col.icon}</span>
              <span className="vol-card-title">{col.nameVn}</span>
              <span className="vol-card-count">
                {col.status === 'draft'
                  ? '⏳ Sắp ra mắt'
                  : `${col.volumeCount} tập`}
              </span>
            </Link>
          ))}
        </div>
      </section>
    </>
  )
}

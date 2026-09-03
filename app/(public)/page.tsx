import { createServerClient } from '@/lib/supabase-server'
import GlobalSearch from '@/components/search/GlobalSearch'
import LiteratureSection from '@/components/home/LiteratureSection'
import type { Metadata } from 'next'

// ponytail: ISR 1h — stats data changes rarely, no need for force-dynamic
export const revalidate = 3600

export const metadata: Metadata = {
  title: 'Bảo tàng Hải dương học — Tra cứu Sinh vật biển Việt Nam',
  description: 'Cơ sở dữ liệu số hóa sinh vật biển Việt Nam — Viện Hải dương học, Nha Trang.',
}

export default async function HomePage() {
  const db = createServerClient()

  // Realtime stats
  const { count: totalSpecies } = await db
    .from('species')
    .select('*', { count: 'exact', head: true })
    .is('deleted_at', null)

  const { data: familyRows } = await db
    .from('taxonomy_tree')
    .select('tax_family_latin')
    .not('tax_family_latin', 'is', null)
    .not('tax_family_latin', 'eq', '')

  const familyCount = familyRows
    ? new Set(familyRows.map(r => r.tax_family_latin).filter(Boolean)).size
    : 210

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
              <span className="hero__stat-num">{totalSpecies?.toLocaleString() || '1,965'}</span>
              <span className="hero__stat-label">Loài</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">{familyCount}</span>
              <span className="hero__stat-label">Họ</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">3</span>
              <span className="hero__stat-label">Tài liệu gốc</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">7</span>
              <span className="hero__stat-label">Tập sách</span>
            </div>
          </div>
        </div>
      </section>

      {/* Danh sách các tài liệu gốc dùng để tra cứu — Thiết kế chuẩn Hallmark & UI-UX-PRO-MAX */}
      <LiteratureSection />
    </>
  )
}

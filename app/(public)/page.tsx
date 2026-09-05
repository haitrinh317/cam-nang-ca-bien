import { createServerClient } from '@/lib/supabase-server'
import GlobalSearch from '@/components/search/GlobalSearch'
import SpecialGroupsSection from '@/components/home/SpecialGroupsSection'
import LiteratureSection from '@/components/home/LiteratureSection'
import type { LiteratureSourceRow } from '@/components/home/LiteratureSection'
import type { Metadata } from 'next'

// ponytail: ISR 1h — stats data changes rarely, no need for force-dynamic
export const revalidate = 3600

export const metadata: Metadata = {
  title: 'Cẩm Nang Sinh Vật Biển Việt Nam — Bảo tàng Hải dương học',
  description: 'Cơ sở dữ liệu số hóa 2.436+ loài cá biển và rong biển Việt Nam từ các công trình phân loại học nguyên bản — Viện Hải dương học Nha Trang.',
  alternates: {
    canonical: 'https://cam-nang-ca-bien.vercel.app',
  },
  openGraph: {
    type: 'website',
    locale: 'vi_VN',
    url: 'https://cam-nang-ca-bien.vercel.app',
    title: 'Cẩm Nang Sinh Vật Biển Việt Nam — Bảo tàng Hải dương học',
    description: 'Cơ sở dữ liệu số hóa 2.436+ loài cá biển và rong biển Việt Nam từ các công trình phân loại học nguyên bản — Viện Hải dương học Nha Trang.',
    images: [
      {
        url: '/og-default.png',
        width: 1200,
        height: 630,
        alt: 'Cẩm Nang Sinh Vật Biển Việt Nam',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Cẩm Nang Sinh Vật Biển Việt Nam — Bảo tàng Hải dương học',
    description: 'Cơ sở dữ liệu số hóa 2.436+ loài sinh vật biển Việt Nam.',
    images: ['/og-default.png'],
  },
}

export default async function HomePage() {
  const db = createServerClient()

  // Parallel fetch: species stats + literature sources
  const [
    { count: totalSpecies },
    { data: familyRows },
    { data: litSources, count: litCount },
  ] = await Promise.all([
    db.from('species')
      .select('*', { count: 'exact', head: true })
      .is('deleted_at', null),
    db.from('taxonomy_tree')
      .select('tax_family_latin')
      .not('tax_family_latin', 'is', null)
      .not('tax_family_latin', 'eq', ''),
    db.from('literature_sources')
      .select('*', { count: 'exact' })
      .eq('is_visible', true)
      .order('sort_order'),
  ])

  const familyCount = familyRows
    ? new Set(familyRows.map(r => r.tax_family_latin).filter(Boolean)).size
    : 210

  const sources = (litSources || []) as LiteratureSourceRow[]

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
              <span className="hero__stat-num">{litCount || sources.length}</span>
              <span className="hero__stat-label">Tài liệu gốc</span>
            </div>
          </div>
        </div>
      </section>

      {/* Khám phá 4 nhóm chuyên đề sinh thái & bảo tồn */}
      <SpecialGroupsSection />

      {/* Danh sách các tài liệu gốc dùng để tra cứu — data từ Supabase */}
      <LiteratureSection sources={sources} />
    </>
  )
}

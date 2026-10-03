import '@/styles/hero.css'
import '@/styles/browse.css'
import { createServerClient } from '@/lib/supabase-server'
import GlobalSearch from '@/components/search/GlobalSearch'
import SpecialGroupsSection from '@/components/home/SpecialGroupsSection'
import LiteratureSection from '@/components/home/LiteratureSection'
import type { LiteratureSourceRow } from '@/components/home/LiteratureSection'
import type { Metadata } from 'next'

// ponytail: ISR 1h — stats/literature hiếm khi thay đổi. Admin flush thủ công qua /api/revalidate-home.
export const revalidate = 3600

export const metadata: Metadata = {
  title: {
    absolute: 'Tra cứu thông tin Sinh Vật Biển Việt Nam',
  },
  description: 'Cơ sở dữ liệu số hóa 2.671+ loài sinh vật biển Việt Nam từ các công trình phân loại học nguyên bản — Một dự án được phát triển bởi haitrinh.',
  alternates: {
    canonical: 'https://www.tracuusinhvatbien.app',
  },
  openGraph: {
    type: 'website',
    locale: 'vi_VN',
    url: 'https://www.tracuusinhvatbien.app',
    siteName: 'Tra cứu thông tin Sinh Vật Biển Việt Nam',
    title: 'Tra cứu thông tin Sinh Vật Biển Việt Nam — haitrinh',
    description: 'Cơ sở dữ liệu số hóa 2.671+ loài sinh vật biển Việt Nam từ các công trình phân loại học nguyên bản — Một dự án được phát triển bởi haitrinh.',
    images: [
      {
        url: '/og-default.png',
        width: 1200,
        height: 630,
        alt: 'Tra cứu thông tin Sinh Vật Biển Việt Nam',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Tra cứu thông tin Sinh Vật Biển Việt Nam — haitrinh',
    description: 'Cơ sở dữ liệu số hóa 2.671+ loài sinh vật biển Việt Nam — Một dự án được phát triển bởi haitrinh.',
    images: ['/og-default.png'],
  },
}

export default async function HomePage() {
  const db = createServerClient()

  const hsOr = 'vn_distribution.ilike.%Hoàng Sa%,vn_distribution.ilike.%Trường Sa%,vn_distribution.ilike.%Hoàng-sa%,vn_distribution.ilike.%Trường-sa%,vn_distribution.ilike.%Nam Yết%,vn_specimen.ilike.%Hoàng-sa%,vn_specimen.ilike.%Trường-sa%,vn_name.ilike.%Trường Sa%'
  const coralFamilies = [
    'Pomacentridae', 'Chaetodontidae', 'Labridae', 'Serranidae', 'Scaridae',
    'Acanthuridae', 'Lutjanidae', 'Holocentridae', 'Mullidae', 'Apogonidae'
  ]

  // Parallel fetch: species stats + literature sources + live special group counts
  // ponytail: familyCount hardcoded — con số ~210 họ gần như cố định, loại bỏ query tải 2,828 rows.
  const familyCount = 210

  const [
    { count: totalSpecies },
    { data: litSources, count: litCount },
    { count: coralCount },
    { count: nguyCapCount },
    { count: hsCount },
    { count: seaweedCount },
    { count: toxicCount },
  ] = await Promise.all([
    db.from('species')
      .select('*', { count: 'exact', head: true })
      .is('deleted_at', null),
    db.from('literature_sources')
      .select('*', { count: 'exact' })
      .eq('is_visible', true)
      .order('sort_order'),
    db.from('species')
      .select('*', { count: 'exact', head: true })
      .is('deleted_at', null)
      .eq('collection_id', 'ca-bien')
      .in('tax_family_latin', coralFamilies),
    db.from('species')
      .select('*', { count: 'exact', head: true })
      .is('deleted_at', null)
      .or('biology->>iucnStatus.in.(CR,EN,VU,NT),biology->vnRedList.not.is.null'),
    db.from('species')
      .select('*', { count: 'exact', head: true })
      .is('deleted_at', null)
      .or(hsOr),
    db.from('species')
      .select('*', { count: 'exact', head: true })
      .is('deleted_at', null)
      .eq('collection_id', 'thuc-vat-bien'),
    db.from('species')
      .select('*', { count: 'exact', head: true })
      .is('deleted_at', null)
      .eq('collection_id', 'sinh-vat-doc'),
  ])

  const sources = (litSources || []) as LiteratureSourceRow[]

  const specialGroupCounts: Record<string, number> = {
    'san-ho': coralCount || 195,
    'nguy-cap': nguyCapCount || 152,
    'hoang-sa-truong-sa': hsCount || 160,
    'thuc-vat-bien': seaweedCount || 672,
    'sinh-vat-doc': toxicCount || 76,
  }

  return (
    <>
      <section className="hero" aria-label="Giới thiệu">
        <div className="hero__bg" aria-hidden="true" />
        <div className="hero__content">
          <h1>Danh mục Sinh vật biển <span className="hero__accent">Việt Nam</span></h1>
          <p>Cơ sở dữ liệu số hóa phục vụ nghiên cứu khoa học — Một dự án được phát triển bởi haitrinh.</p>
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

      {/* Khám phá 5 nhóm chuyên đề sinh thái & bảo tồn */}
      <SpecialGroupsSection counts={specialGroupCounts} />

      {/* Danh sách các tài liệu gốc dùng để tra cứu — data từ Supabase */}
      <LiteratureSection sources={sources} />
    </>
  )
}

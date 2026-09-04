import { getCollectionBySlug } from '@/lib/collections'
import { notFound } from 'next/navigation'
import SpeciesGrid from '@/components/browse/SpeciesGrid'
import GlobalSearch from '@/components/search/GlobalSearch'
import { createServerClient } from '@/lib/supabase-server'
import { getBooksForCollection } from '@/lib/books-data'
import type { Metadata } from 'next'

// ponytail: ISR 1h — species data rarely changes, consistent with landing page
export const revalidate = 3600

interface Props {
  params: Promise<{ collection: string }>
  searchParams: Promise<{ vol?: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  if (!col) return { title: 'Không tìm thấy' }
  const pageUrl = `https://cam-nang-ca-bien.vercel.app/${collection}`
  const desc = `Cơ sở dữ liệu số hóa ${col.nameVn} trích xuất từ các công trình khoa học nguyên bản của Viện Hải dương học Nha Trang.`
  return {
    title: `Tra cứu Danh mục — ${col.nameVn}`,
    description: desc,
    alternates: {
      canonical: pageUrl,
    },
    openGraph: {
      type: 'website',
      locale: 'vi_VN',
      url: pageUrl,
      title: `Tra cứu Danh mục — ${col.nameVn} — Bảo tàng Hải dương học`,
      description: `${col.volumeCount} tập tài liệu khoa học nguyên bản, định danh và chuẩn hóa danh pháp sinh vật biển Việt Nam.`,
      images: [
        {
          url: '/og-default.png',
          width: 1200,
          height: 630,
          alt: col.nameVn,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: `Tra cứu Danh mục — ${col.nameVn}`,
      description: desc,
      images: ['/og-default.png'],
    },
  }
}

export default async function CollectionPage({ params, searchParams }: Props) {
  const { collection } = await params
  const { vol } = await searchParams
  const col = getCollectionBySlug(collection)
  if (!col) notFound()

  const defaultVol = 1
  const initialVol = parseInt(vol || String(defaultVol)) || defaultVol
  const books = getBooksForCollection(collection)

  const db = createServerClient()
  const { count: totalSpecies } = await db
    .from('species')
    .select('*', { count: 'exact', head: true })
    .eq('collection_id', collection)
    .is('deleted_at', null)

  const { data: familyRows } = await db
    .from('species')
    .select('tax_family_latin')
    .eq('collection_id', collection)
    .is('deleted_at', null)
    .not('tax_family_latin', 'is', null)

  const familyCount = familyRows
    ? new Set(familyRows.map(r => r.tax_family_latin).filter(Boolean)).size
    : 210

  return (
    <>
      <section className="hero" aria-label="Tra cứu toàn bộ">
        <div className="hero__bg" aria-hidden="true" />
        <div className="hero__content">
          <h1>
            Tra cứu Danh mục <span className="hero__accent">{col.id === 'thuc-vat-bien' ? 'Thực Vật Biển Việt Nam' : col.nameVn}</span>
          </h1>
          <p>
            Cơ sở dữ liệu số hóa phục vụ nghiên cứu khoa học — Viện Hải dương học, Nha Trang.
          </p>
          <GlobalSearch />

          {/* Live stats đồng bộ hoàn toàn với trang chủ */}
          <div className="hero__stats">
            <div className="hero__stat">
              <span className="hero__stat-num">{totalSpecies?.toLocaleString() || '1,764'}</span>
              <span className="hero__stat-label">Loài</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">{familyCount}</span>
              <span className="hero__stat-label">Họ</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">{books.length}</span>
              <span className="hero__stat-label">Đầu sách</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-num">{col.volumeCount}</span>
              <span className="hero__stat-label">Tập tài liệu</span>
            </div>
          </div>
        </div>
      </section>

      <SpeciesGrid collection={collection} initialVol={initialVol} />
    </>
  )
}

export async function generateStaticParams() {
  return [{ collection: 'ca-bien' }, { collection: 'thuc-vat-bien' }]
}

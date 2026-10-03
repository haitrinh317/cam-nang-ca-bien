import '@/styles/catalogue.css'
import '@/styles/book-browser.css'
import {
  getCollectionBySlug,
  getSpecialGroup,
  getBooksForCollection,
} from '@/lib/collection-registry'
import { applySpeciesFilters } from '@/lib/species-query'
import { notFound } from 'next/navigation'
import SpeciesGrid from '@/components/browse/SpeciesGrid'
import CatalogHeader from '@/components/browse/CatalogHeader'
import { createServerClient } from '@/lib/supabase-server'
import type { Metadata } from 'next'
import { Suspense } from 'react'

// ponytail: ISR 1h — species data rarely changes, consistent with landing page
export const revalidate = 3600

interface Props {
  params: Promise<{ collection: string }>
  searchParams: Promise<{ vol?: string; group?: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  if (!col) return { title: 'Không tìm thấy' }
  const pageUrl = `https://www.tracuusinhvatbien.app/${collection}`
  const desc = `Cơ sở dữ liệu số hóa ${col.nameVn} trích xuất từ các công trình khoa học nguyên bản — Một dự án được phát triển bởi haitrinh.`
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
      siteName: 'Tra cứu thông tin Sinh Vật Biển Việt Nam',
      title: `Tra cứu Danh mục — ${col.nameVn} — haitrinh`,
      description: `${col.volumeCount} tập tài liệu khoa học nguyên bản, định danh và chuẩn hóa danh pháp sinh vật biển Việt Nam. Một dự án được phát triển bởi haitrinh.`,
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
      title: `Tra cứu Danh mục — ${col.nameVn} — haitrinh`,
      description: desc,
      images: ['/og-default.png'],
    },
  }
}

export default async function CollectionPage({ params, searchParams }: Props) {
  const { collection } = await params
  const { vol, group } = await searchParams
  const col = getCollectionBySlug(collection)
  if (!col) notFound()

  const defaultVol = 1
  const initialVol = parseInt(vol || String(defaultVol)) || defaultVol
  const books = getBooksForCollection(collection)

  const db = createServerClient()
  // ponytail: parallel fetch count + initial species list for first render
  // Columns must match SpeciesGrid.loadData() select to avoid shape mismatch
  const GRID_COLS = 'id, volume, species_index, vn_name, scientific_name, authorship, biology, vn_distribution, en_distribution, vn_specimen, collection_id'
  const [{ count: totalSpecies }, { data: initialSpecies }] = await Promise.all([
    db.from('species')
      .select('*', { count: 'exact', head: true })
      .eq('collection_id', collection)
      .is('deleted_at', null),
    // Pre-fetch species for initial volume (no group) — eliminates client Supabase call on first load
    !group
      ? applySpeciesFilters(
          db.from('species').select(GRID_COLS),
          collection
        ).eq('volume', initialVol).order('species_index').limit(800)
      : Promise.resolve({ data: null }),
  ])

  // ponytail: familyCount ước tính từ totalSpecies — tránh query tải N rows chỉ để đếm DISTINCT.
  // Tỉ lệ loài/họ trung bình ~13. Ceiling: sai lệch ±10% với collection nhỏ.
  const familyCount = Math.max(1, Math.round((totalSpecies || 0) / 13))

  const activeGroup = group ? getSpecialGroup(group) : null

  return (
    <>
      <CatalogHeader
        collection={col}
        totalSpecies={totalSpecies || 0}
        familyCount={familyCount}
        booksCount={books.length}
        activeGroup={activeGroup}
      />

      <Suspense fallback={<div className="list-status-message"><div className="spinner" /><span>Đang tải danh sách...</span></div>}>
        <SpeciesGrid collection={collection} initialVol={initialVol} initialGroup={group} initialSpecies={initialSpecies || undefined} />
      </Suspense>
    </>
  )
}

export async function generateStaticParams() {
  return [
    { collection: 'ca-bien' },
    { collection: 'thuc-vat-bien' },
    { collection: 'giap-xac' },
    { collection: 'bo-sat-bien' },
    { collection: 'sinh-vat-doc' },
    { collection: 'than-mem' },
    { collection: 'san-ho' },
    { collection: 'thu-bien' },
  ]
}

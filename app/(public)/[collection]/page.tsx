import { getCollectionBySlug } from '@/lib/collections'
import { notFound } from 'next/navigation'
import SpeciesGrid from '@/components/browse/SpeciesGrid'
import CatalogHeader from '@/components/browse/CatalogHeader'
import { getSpecialGroup } from '@/lib/special-groups'
import { createServerClient } from '@/lib/supabase-server'
import { getBooksForCollection } from '@/lib/books-data'
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
  const { vol, group } = await searchParams
  const col = getCollectionBySlug(collection)
  if (!col) notFound()

  const defaultVol = 1
  const initialVol = parseInt(vol || String(defaultVol)) || defaultVol
  const books = getBooksForCollection(collection)

  const db = createServerClient()
  const [{ count: totalSpecies }, { data: familyRows }] = await Promise.all([
    db.from('species')
      .select('*', { count: 'exact', head: true })
      .eq('collection_id', collection)
      .is('deleted_at', null),
    db.from('species')
      .select('tax_family_latin')
      .eq('collection_id', collection)
      .is('deleted_at', null)
      .not('tax_family_latin', 'is', null),
  ])

  const familyCount = familyRows
    ? new Set(familyRows.map(r => r.tax_family_latin).filter(Boolean)).size
    : 210

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
        <SpeciesGrid collection={collection} initialVol={initialVol} initialGroup={group} />
      </Suspense>
    </>
  )
}

export async function generateStaticParams() {
  return [{ collection: 'ca-bien' }, { collection: 'thuc-vat-bien' }]
}

import { getCollectionBySlug } from '@/lib/collections'
import { notFound } from 'next/navigation'
import SpeciesGrid from '@/components/browse/SpeciesGrid'
import type { Metadata } from 'next'

export const dynamic = 'force-dynamic'
export const revalidate = 0

interface Props {
  params: Promise<{ collection: string }>
  searchParams: Promise<{ vol?: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  if (!col) return { title: 'Không tìm thấy' }
  return {
    title: `Duyệt theo Tập — ${col.nameVn}`,
    description: `Danh sách ${col.nameVn} trích xuất từ ${col.volumeCount} tập tài liệu khoa học — Viện Hải dương học.`,
    openGraph: {
      title: `Duyệt theo Tập — ${col.nameVn}`,
      description: `${col.volumeCount} tập, hơn 1500 loài sinh vật biển Việt Nam.`,
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

  return (
    <>
      <section className="page-header" aria-label="Tiêu đề tập">
        <h1>Duyệt Theo Tập Sách Gốc</h1>
        <p>Trích xuất {col.volumeCount} tập tài liệu khoa học {col.nameVn} — Viện Hải dương học.</p>
      </section>
      <SpeciesGrid collection={collection} initialVol={initialVol} />
    </>
  )
}

export async function generateStaticParams() {
  return [{ collection: 'ca-bien' }]
}

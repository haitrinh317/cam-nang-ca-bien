import { getCollectionBySlug } from '@/lib/collections'
import { notFound } from 'next/navigation'
import TaxonomyTree from '@/components/browse/TaxonomyTree'
import type { Metadata } from 'next'

// ponytail: ISR cache 24h (86400s) — Cây phân loại chỉ cập nhật khi có xuất bản hoặc OCR batch mới
export const revalidate = 86400

interface Props {
  params: Promise<{ collection: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  return {
    title: `Cây Phân Loại — ${col?.nameVn || collection}`,
    description: `Cây phân loại học sinh học biển từ Lớp, Bộ, Họ, Giống đến từng Loài — ${col?.nameVn || ''}.`,
  }
}

export default async function TaxonomyPage({ params }: Props) {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  if (!col) notFound()

  return (
    <>
      <section className="page-header" aria-label="Tiêu đề phân loại">
        <h1>Hệ thống Phân loại Học</h1>
        <p>Cây phân loại học sinh học biển từ Lớp, Bộ, Họ, Giống đến từng Loài.</p>
      </section>
      <TaxonomyTree collection={collection} />
    </>
  )
}

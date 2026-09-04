import { getCollectionBySlug } from '@/lib/collections'
import { createServerClient } from '@/lib/supabase-server'
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
  const name = col?.nameVn || collection
  const pageUrl = `https://cam-nang-ca-bien.vercel.app/${collection}/taxonomy`
  const desc = `Cây phân loại học sinh học biển từ Lớp, Bộ, Họ, Giống đến từng Loài — ${name}.`
  return {
    title: `Cây Phân Loại — ${name}`,
    description: desc,
    alternates: {
      canonical: pageUrl,
    },
    openGraph: {
      type: 'website',
      locale: 'vi_VN',
      url: pageUrl,
      title: `Cây Phân Loại Sinh Học — ${name}`,
      description: desc,
      images: [
        {
          url: '/og-default.png',
          width: 1200,
          height: 630,
          alt: `Cây phân loại ${name}`,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: `Cây Phân Loại — ${name}`,
      description: desc,
      images: ['/og-default.png'],
    },
  }
}

const COLS = 'id, vn_name, scientific_name, tax_class_vn, tax_class_latin, tax_order_vn, tax_order_latin, tax_family_vn, tax_family_latin, tax_genus_vn, tax_genus_latin, species_index'

export default async function TaxonomyPage({ params }: Props) {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  if (!col) notFound()

  const db = createServerClient()
  const [r1, r2] = await Promise.all([
    db.from('species').select(COLS).eq('collection_id', collection).is('deleted_at', null).range(0, 999),
    db.from('species').select(COLS).eq('collection_id', collection).is('deleted_at', null).range(1000, 1999),
  ])

  const species = [...(r1.data || []), ...(r2.data || [])]
  species.sort((a: any, b: any) => {
    const cl = (a.tax_class_latin || '').localeCompare(b.tax_class_latin || '')
    if (cl !== 0) return cl
    const or = (a.tax_order_latin || '').localeCompare(b.tax_order_latin || '')
    if (or !== 0) return or
    const fa = (a.tax_family_latin || '').localeCompare(b.tax_family_latin || '')
    if (fa !== 0) return fa
    return (a.species_index || 0) - (b.species_index || 0)
  })

  return (
    <>
      <section className="page-header" aria-label="Tiêu đề phân loại">
        <h1>Hệ thống Phân loại Học</h1>
        <p>Cây phân loại học sinh học biển từ Lớp, Bộ, Họ, Giống đến từng Loài.</p>
      </section>
      <TaxonomyTree collection={collection} initialSpecies={species} />
    </>
  )
}

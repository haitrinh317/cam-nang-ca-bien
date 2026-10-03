import '@/styles/catalogue.css'
import { getCollectionBySlug } from '@/lib/collection-registry'
import { createServerClient } from '@/lib/supabase-server'
import { TAXONOMY_COLS, sortTaxonomyRows, type SpeciesRow } from '@/lib/taxonomy'
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

export default async function TaxonomyPage({ params }: Props) {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  if (!col) notFound()

  const db = createServerClient()
  // ponytail: single query with explicit limit — replaces 3 range queries (0-999, 1000-1999, 2000-2999).
  // Supabase JS .limit() overrides PostgREST default max_rows. Ceiling: if collection exceeds 3000 species.
  const { data: rawSpecies } = await db
    .from('species')
    .select(TAXONOMY_COLS)
    .eq('collection_id', collection)
    .is('deleted_at', null)
    .limit(3000)

  const species = sortTaxonomyRows((rawSpecies || []) as SpeciesRow[], 'modern')

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

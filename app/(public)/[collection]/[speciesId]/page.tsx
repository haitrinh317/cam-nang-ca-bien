import { cache } from 'react'
import { createServerClient } from '@/lib/supabase-server'
import { resolvePhotoUrl } from '@/lib/species-photos'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import SpecimenCard from '@/components/species/SpecimenCard'
import type { Metadata } from 'next'

// ponytail: ISR cache 24h (86400s). Dữ liệu loài cố định theo xuất bản khoa học, chỉ cập nhật khi admin sửa hoặc nạp batch mới.
export const revalidate = 86400

interface Props {
  params: Promise<{ collection: string; speciesId: string }>
}

// React cache() tự động de-duplicate query giữa generateMetadata và Page body trong cùng 1 request
const getSpecies = cache(async (speciesId: string) => {
  const db = createServerClient()
  const { data, error } = await db
    .from('species')
    .select('*')
    .eq('id', speciesId)
    .single()
  return (error || !data) ? null : data
})

const getSpeciesPhotos = cache(async (speciesId: string) => {
  const db = createServerClient()
  const { data } = await db
    .from('species_photos')
    .select('id, storage_path, source, photographer, license, source_url, is_primary, sort_order')
    .eq('species_id', speciesId)
    .order('is_primary', { ascending: false })
    .order('sort_order')
  return data || []
})

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { collection, speciesId } = await params
  const [data, photos] = await Promise.all([
    getSpecies(speciesId),
    getSpeciesPhotos(speciesId)
  ])
  if (!data) return { title: 'Loài không tìm thấy' }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
  const primaryPhoto = photos?.[0]
  const photoUrl = resolvePhotoUrl(primaryPhoto)

  const title = `${data.vn_name} (${data.scientific_name})`
  const rawDesc = data.biology_summary_vn || data.ecology || data.morphology || ''
  const description = rawDesc
    ? `${data.vn_name} — ${rawDesc.slice(0, 155).trim()}...`
    : `Thông tin phân loại học và sinh thái của ${data.vn_name} (${data.scientific_name}) — Viện Hải dương học Nha Trang.`

  const pageUrl = `https://cam-nang-ca-bien.vercel.app/${collection}/${speciesId}`

  return {
    title,
    description,
    alternates: {
      canonical: pageUrl,
    },
    openGraph: {
      type: 'article',
      locale: 'vi_VN',
      url: pageUrl,
      title: `${title} — Cẩm nang Sinh vật biển VN`,
      description,
      siteName: 'Bảo tàng Hải dương học',
      images: [
        {
          url: photoUrl,
          width: 1200,
          height: 630,
          alt: `${data.vn_name} — ${data.scientific_name}`,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: `${title} — Cẩm nang Sinh vật biển VN`,
      description,
      images: [photoUrl],
    },
  }
}

export default async function SpeciesDetailPage({ params }: Props) {
  const { collection, speciesId } = await params
  const [data, photos] = await Promise.all([
    getSpecies(speciesId),
    getSpeciesPhotos(speciesId)
  ])

  if (!data) notFound()

  const primaryPhoto = photos?.[0]
  const photoUrl = resolvePhotoUrl(primaryPhoto, undefined)

  // Schema.org Taxon (BiologicalEntity) Structured Data
  const taxonSchema = {
    '@context': 'https://schema.org',
    '@type': 'Taxon',
    name: data.vn_name,
    scientificName: data.scientific_name,
    taxonRank: 'Species',
    parentTaxon: data.tax_genus_latin ? {
      '@type': 'Taxon',
      name: data.tax_genus_latin,
      taxonRank: 'Genus',
    } : undefined,
    description: data.biology_summary_vn || data.morphology || data.ecology || undefined,
    image: photoUrl,
    sameAs: data.worms_aphia_id
      ? `https://www.marinespecies.org/aphia.php?p=taxdetails&id=${data.worms_aphia_id}`
      : undefined,
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(taxonSchema) }}
      />
      <div className="main-container">
        <Link href={`/${collection}?vol=${data.volume}`} className="back-link" aria-label="Quay lại danh sách">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          <span>Quay lại danh sách</span>
        </Link>
        <SpecimenCard sp={data} initialPhotos={photos} />
      </div>
    </>
  )
}


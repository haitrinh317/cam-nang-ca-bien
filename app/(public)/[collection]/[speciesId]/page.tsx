import { cache } from 'react'
import { createServerClient } from '@/lib/supabase-server'
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

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { speciesId } = await params
  const data = await getSpecies(speciesId)
  if (!data) return { title: 'Loài không tìm thấy' }
  return {
    title: `${data.vn_name} — ${data.scientific_name}`,
    description: `Thông tin phân loại học và sinh học của ${data.vn_name} (${data.scientific_name}) — Danh mục sinh vật biển Việt Nam.`,
  }
}

export default async function SpeciesDetailPage({ params }: Props) {
  const { collection, speciesId } = await params
  const data = await getSpecies(speciesId)

  if (!data) notFound()

  return (
    <div className="main-container">
      <Link href={`/${collection}?vol=${data.volume}`} className="back-link" aria-label="Quay lại danh sách">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <line x1="19" y1="12" x2="5" y2="12" />
          <polyline points="12 19 5 12 12 5" />
        </svg>
        <span>Quay lại danh sách</span>
      </Link>
      <SpecimenCard sp={data} />
    </div>
  )
}

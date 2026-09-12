import type { Metadata } from 'next'
import { getCollectionBySlug } from '@/lib/collection-registry'
import { notFound } from 'next/navigation'
import SpeciesTable from '@/components/admin/SpeciesTable'

interface Props {
  params: Promise<{ collection: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  return {
    title: `Quản lý ${col?.nameVn || collection} — Admin haitrinh`,
    description: `Quản lý dữ liệu phân loại học ${col?.nameVn} — Dự án cá nhân phát triển bởi haitrinh.`,
    robots: {
      index: false,
      follow: false,
    },
  }
}

export default async function AdminCollectionPage({ params }: Props) {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  if (!col) notFound()

  return (
    <div className="admin-page">
      <h1 className="admin-page__title">
        {col.icon} {col.nameVn}
      </h1>
      <p style={{ color: 'var(--color-muted)', marginBottom: 'var(--space-2xl)' }}>
        Quản lý toàn bộ loài trong collection <strong>{col.nameVn}</strong>.
        Thêm, sửa, xóa từng loài hoặc dùng script Python để import hàng loạt.
      </p>
      <SpeciesTable collection={collection} />
    </div>
  )
}

import { getCollectionBySlug } from '@/lib/collections'
import { notFound } from 'next/navigation'
import SpeciesTable from '@/components/admin/SpeciesTable'

interface Props {
  params: Promise<{ collection: string }>
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

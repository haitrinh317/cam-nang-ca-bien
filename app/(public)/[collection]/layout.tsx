import { getCollectionBySlug } from '@/lib/collection-registry'
import { notFound } from 'next/navigation'

interface Props {
  children: React.ReactNode
  params: Promise<{ collection: string }>
}

export default async function CollectionLayout({ children, params }: Props) {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  if (!col) notFound()

  return (
    <div
      className={`collection-wrapper collection-${collection}`}
      style={{ '--collection-accent': col.accentColor } as React.CSSProperties}
    >
      {children}
    </div>
  )
}

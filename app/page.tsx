import { getCollections } from '@/lib/collections'
import GlobalSearch from '@/components/search/GlobalSearch'
import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Bảo tàng Hải dương học — Tra cứu Sinh vật biển Việt Nam',
  description: 'Cơ sở dữ liệu số hóa sinh vật biển Việt Nam — Viện Hải dương học, Nha Trang.',
}

export default async function HomePage() {
  const collections = await getCollections()

  return (
    <>
      <section className="hero" aria-label="Giới thiệu">
        <h1>Danh mục Cá biển Việt Nam</h1>
        <p>Cơ sở dữ liệu số hóa phục vụ công tác nghiên cứu khoa học — Viện Hải dương học, Nha Trang.</p>
        <GlobalSearch />
      </section>

      <section className="section-browse" aria-label="Duyệt theo tập">
        <div className="section-browse-header">
          <h2 className="section-browse-title">Bộ sưu tập Sinh vật biển</h2>
        </div>
        <div className="vol-grid">
          {collections.map(col => (
            <Link
              key={col.slug}
              href={col.status === 'draft' ? '#' : `/${col.slug}`}
              className={`vol-card${col.status === 'draft' ? ' vol-card--draft' : ''}`}
              aria-disabled={col.status === 'draft'}
              style={{
                opacity: col.status === 'draft' ? 0.55 : 1,
                pointerEvents: col.status === 'draft' ? 'none' : undefined,
              }}
            >
              <span className="vol-card-num" style={{ fontSize: '2.2rem' }}>{col.icon}</span>
              <span className="vol-card-title">{col.nameVn}</span>
              <span className="vol-card-count">
                {col.status === 'draft'
                  ? '⏳ Sắp ra mắt'
                  : `${col.volumeCount} tập`}
              </span>
            </Link>
          ))}
        </div>
      </section>
    </>
  )
}

import type { Metadata } from 'next'
import { getCollectionBySlug } from '@/lib/collection-registry'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import '@/styles/admin.css'
import '@/styles/admin-command.css'
import SpeciesTable from '@/components/admin/SpeciesTable'
import { createServerClient } from '@/lib/supabase-server'
import {
  Fish,
  Leaf,
  Shrimp,
  Turtle,
  Biohazard,
  Shell,
  Sparkles,
  Waves,
  ChevronLeft,
  ExternalLink,
  CheckCircle2,
  ShieldCheck,
  Image as ImageIcon,
  Database,
  Microscope,
} from 'lucide-react'

interface Props {
  params: Promise<{ collection: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  return {
    title: `Quản lý ${col?.nameVn || collection} — Trung Tâm Chỉ Huy haitrinh`,
    description: `Quản lý và kiểm định dữ liệu phân loại học ${col?.nameVn} — Dự án cá nhân phát triển bởi haitrinh.`,
    robots: {
      index: false,
      follow: false,
    },
  }
}

const COLLECTION_ICONS: Record<string, { icon: React.ElementType; color: string; bg: string }> = {
  'ca-bien':        { icon: Fish,       color: '#0f766e', bg: '#e0f7f4' },
  'thuc-vat-bien':  { icon: Leaf,       color: '#059669', bg: '#ecfdf5' },
  'giap-xac':       { icon: Shrimp,     color: '#dc2626', bg: '#fef2f2' },
  'bo-sat-bien':    { icon: Turtle,     color: '#d97706', bg: '#fffbeb' },
  'sinh-vat-doc':   { icon: Biohazard,  color: '#e11d48', bg: '#fff1f2' },
  'than-mem':       { icon: Shell,      color: '#7c3aed', bg: '#f5f3ff' },
  'san-ho':         { icon: Sparkles,   color: '#db2777', bg: '#fdf2f8' },
  'thu-bien':       { icon: Waves,      color: '#0284c7', bg: '#f0f9ff' },
  'dong-vat-phu-du':{ icon: Microscope, color: '#0891b2', bg: '#ecfeff' },
}

export default async function AdminCollectionPage({ params }: Props) {
  const { collection } = await params
  const col = getCollectionBySlug(collection)
  if (!col) notFound()

  const iconMeta = COLLECTION_ICONS[collection] || { icon: Database, color: '#0f766e', bg: '#e0f7f4' }
  const IconComponent = iconMeta.icon

  // Fetch micro-telemetry counts in parallel via head queries (<50ms)
  const supabase = createServerClient()
  const [
    { count: totalCount },
    { count: wormsCount },
    { count: redListCount },
    { count: photosCount },
  ] = await Promise.all([
    supabase.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', collection).is('deleted_at', null),
    supabase.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', collection).eq('worms_status', 'valid').is('deleted_at', null),
    supabase.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', collection).not('biology->vnRedList', 'is', null).is('deleted_at', null),
    supabase.from('species').select('*', { count: 'exact', head: true }).eq('collection_id', collection).not('photo_url', 'is', null).neq('photo_url', '').is('deleted_at', null),
  ])

  const total = totalCount || 0
  const wormsValid = wormsCount || 0
  const wormsPct = total > 0 ? Math.round((wormsValid / total) * 100) : 0
  const redList = redListCount || 0
  const photos = photosCount || 0
  const photosPct = total > 0 ? Math.round((photos / total) * 100) : 0

  return (
    <div className="admin-page">
      {/* Breadcrumb Navigation */}
      <nav className="admin-col-breadcrumb" aria-label="Điều hướng phân hệ">
        <Link href="/admin" className="admin-col-breadcrumb__link">
          <ChevronLeft size={14} aria-hidden="true" />
          <span>Trung tâm chỉ huy</span>
        </Link>
        <span className="admin-col-breadcrumb__sep">/</span>
        <span className="admin-col-breadcrumb__curr">{col.nameVn}</span>
      </nav>

      {/* Spotlight Header Banner */}
      <header className="admin-col-hero">
        <div className="admin-col-hero__main">
          <div
            className="admin-col-hero__icon-box"
            style={{ color: iconMeta.color, background: iconMeta.bg, borderColor: `${iconMeta.color}35` }}
          >
            <IconComponent size={30} aria-hidden="true" />
          </div>
          <div>
            <div className="admin-col-hero__meta-row">
              <span
                className="admin-col-hero__pill"
                style={{ color: iconMeta.color, borderColor: `${iconMeta.color}45`, background: iconMeta.bg }}
              >
                Phân hệ CSDL
              </span>
              <span className="admin-col-hero__vol-badge">
                {' · '}{col.volumeCount > 1 ? `${col.volumeCount} tập chuyên khảo` : '1 chuyên khảo'}
              </span>
            </div>
            <h1 className="admin-col-hero__title">{col.nameVn}</h1>
            <p className="admin-col-hero__desc">
              Hệ thống giám sát, biên tập và kiểm định danh pháp đa dạng sinh học {col.nameVn.replace(/Việt Nam/i, '').trim().toLowerCase()} Việt Nam.
            </p>
          </div>
        </div>

        <div className="admin-col-hero__actions">
          <Link
            href={`/${collection}`}
            target="_blank"
            className="btn btn-outline btn-sm"
            title="Mở trang tra cứu công khai cho người dùng"
          >
            <span>Mở tra cứu</span>
            <ExternalLink size={13} aria-hidden="true" />
          </Link>
        </div>
      </header>

      {/* Telemetry Quick Ribbon */}
      <section className="admin-col-telemetry" aria-label="Chỉ số hoàn thiện phân hệ">
        <div className="admin-col-telemetry__card">
          <div className="admin-col-telemetry__label">Tổng số loài</div>
          <div className="admin-col-telemetry__val">
            <span className="num">{total.toLocaleString('vi-VN')}</span>
            <span className="unit"> loài bảo tồn</span>
          </div>
        </div>

        <div className="admin-col-telemetry__divider" aria-hidden="true" />

        <div className="admin-col-telemetry__card">
          <div className="admin-col-telemetry__label">
            <CheckCircle2 size={13} style={{ color: '#059669' }} aria-hidden="true" />
            <span>Định danh WoRMS Valid</span>
          </div>
          <div className="admin-col-telemetry__val" style={{ color: '#0f766e' }}>
            <span className="num">{wormsValid.toLocaleString('vi-VN')}</span>
            <span className="unit" style={{ color: '#64748b' }}> ({wormsPct}%)</span>
          </div>
        </div>

        <div className="admin-col-telemetry__divider" aria-hidden="true" />

        <div className="admin-col-telemetry__card">
          <div className="admin-col-telemetry__label">
            <ShieldCheck size={13} style={{ color: '#d97706' }} aria-hidden="true" />
            <span>Sách Đỏ VAST 2024</span>
          </div>
          <div className="admin-col-telemetry__val" style={{ color: '#b45309' }}>
            <span className="num">{redList.toLocaleString('vi-VN')}</span>
            <span className="unit"> loài nguy cấp</span>
          </div>
        </div>

        <div className="admin-col-telemetry__divider" aria-hidden="true" />

        <div className="admin-col-telemetry__card">
          <div className="admin-col-telemetry__label">
            <ImageIcon size={13} style={{ color: '#0284c7' }} aria-hidden="true" />
            <span>Ảnh mẫu vật số hóa</span>
          </div>
          <div className="admin-col-telemetry__val" style={{ color: '#0284c7' }}>
            <span className="num">{photos.toLocaleString('vi-VN')}</span>
            <span className="unit" style={{ color: '#64748b' }}> ({photosPct}%)</span>
          </div>
        </div>
      </section>

      {/* Main Species Table */}
      <SpeciesTable collection={collection} themeColor={iconMeta.color} />
    </div>
  )
}

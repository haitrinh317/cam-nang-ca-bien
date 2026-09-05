import Link from 'next/link'
import { Home, BookOpen, Layers, Sparkles } from 'lucide-react'
import type { SpecialGroupConfig } from '@/lib/special-groups'
import './CatalogHeader.css'

interface Props {
  collection: {
    id: string
    slug: string
    nameVn: string
    nameEn: string
    volumeCount: number
  }
  totalSpecies: number
  familyCount: number
  booksCount: number
  activeGroup?: SpecialGroupConfig | null
}

export default function CatalogHeader({
  collection,
  totalSpecies,
  familyCount,
  booksCount,
  activeGroup,
}: Props) {
  const isSpecialGroup = Boolean(activeGroup)

  return (
    <header className="catalog-header" aria-label="Đầu trang danh mục tra cứu">
      {/* 1. Breadcrumb phân cấp chuẩn ui-ux-pro-max */}
      <nav className="catalog-breadcrumb" aria-label="Điều hướng phân cấp">
        <Link href="/">
          <Home size={13} aria-hidden="true" />
          <span>Trang chủ</span>
        </Link>
        <span className="catalog-breadcrumb-sep" aria-hidden="true">/</span>

        {isSpecialGroup ? (
          <>
            <Link href={`/${collection.slug}`}>
              <span>{collection.nameVn}</span>
            </Link>
            <span className="catalog-breadcrumb-sep" aria-hidden="true">/</span>
            <span className="catalog-breadcrumb-current">{activeGroup?.title}</span>
          </>
        ) : (
          <span className="catalog-breadcrumb-current">{collection.nameVn}</span>
        )}
      </nav>

      {/* 2. Tiêu đề & mô tả học thuật súc tích */}
      <div className="catalog-header__body">
        <h1 className="catalog-header__title">
          {isSpecialGroup ? (
            activeGroup?.title
          ) : (
            <>
              Danh mục <span className="catalog-header__title-accent">{collection.id === 'thuc-vat-bien' ? 'Thực Vật Biển Việt Nam' : collection.nameVn}</span>
            </>
          )}
        </h1>

        <p className="catalog-header__desc">
          {isSpecialGroup ? (
            activeGroup?.subTitle
          ) : (
            'Cơ sở dữ liệu số hóa tiêu bản mẫu vật và phân loại học sinh vật biển nguyên bản — Viện Hải dương học Nha Trang.'
          )}
        </p>

        {/* 3. Dải Pills trạng thái nhanh gọn */}
        <div className="catalog-header__pills">
          {isSpecialGroup ? (
            <>
              <span className={`catalog-header__pill catalog-header__pill--group catalog-header__pill--group-${activeGroup?.badgeColor || 'amber'}`}>
                <Sparkles size={12} aria-hidden="true" />
                <span>{activeGroup?.badge}</span>
              </span>
              <span className="catalog-header__pill catalog-header__pill--highlight">
                <span>{activeGroup?.approxCount || totalSpecies} loài ghi nhận</span>
              </span>
              <span className="catalog-header__pill">
                <span>Viện Hải dương học</span>
              </span>
            </>
          ) : (
            <>
              <span className="catalog-header__pill catalog-header__pill--highlight">
                <span>{totalSpecies.toLocaleString()} loài sinh vật</span>
              </span>
              <span className="catalog-header__pill">
                <Layers size={12} aria-hidden="true" />
                <span>{familyCount} họ phân loại</span>
              </span>
              <span className="catalog-header__pill">
                <BookOpen size={12} aria-hidden="true" />
                <span>{booksCount} công trình tài liệu gốc</span>
              </span>
              <span className="catalog-header__pill">
                <span>{collection.volumeCount} tập tài liệu</span>
              </span>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

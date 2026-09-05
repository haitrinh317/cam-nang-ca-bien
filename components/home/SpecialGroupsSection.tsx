import React from 'react'
import Link from 'next/link'
import { SPECIAL_GROUPS_LIST } from '@/lib/special-groups'
import { Sparkles, ArrowRight, ShieldAlert, Waves, Leaf, Compass } from 'lucide-react'
import './SpecialGroupsSection.css'

interface Props {
  // Có thể truyền count thực tế từ server nếu muốn đồng bộ động
  counts?: Record<string, number>
}

export default function SpecialGroupsSection({ counts }: Props) {
  const getIcon = (id: string) => {
    switch (id) {
      case 'san-ho':
        return <Waves size={24} className="sgh-icon" />
      case 'nguy-cap':
        return <ShieldAlert size={24} className="sgh-icon" />
      case 'hoang-sa-truong-sa':
        return <Compass size={24} className="sgh-icon" />
      case 'thuc-vat-bien':
        return <Leaf size={24} className="sgh-icon" />
      default:
        return <Sparkles size={24} className="sgh-icon" />
    }
  }

  return (
    <section className="special-groups-section" aria-label="Khám phá theo chuyên đề sinh thái">
      <div className="sgs-header">
        <div className="sgs-badge-wrapper">
          <Sparkles size={14} className="sgs-badge-icon" />
          <span className="sgs-badge-text">BẢO TỒN & HỆ SINH THÁI ĐẶC SẮC</span>
        </div>
        <h2 className="sgs-title">Khám Phá Theo Chuyên Đề Sinh Thái Biển</h2>
        <p className="sgs-subtitle">
          Truy cập nhanh các nhóm sinh vật biển trọng điểm được phân loại theo hệ sinh thái rạn san hô,
          mức độ bảo tồn quốc tế (IUCN) và tài nguyên sinh vật biển Việt Nam.
        </p>
      </div>

      <div className="sgs-grid">
        {SPECIAL_GROUPS_LIST.map(group => {
          const speciesCount = counts?.[group.id] || group.approxCount
          return (
            <Link
              key={group.id}
              href={group.targetUrl}
              className={`sgs-card sgs-card--${group.badgeColor}`}
            >
              <div className="sgs-card__accent-bar" />
              <div className="sgs-card__body">
                <div className="sgs-card__top">
                  <div className="sgs-card__icon-box">
                    {getIcon(group.id)}
                  </div>
                  <span className="sgs-card__badge">{group.badge}</span>
                </div>

                <h3 className="sgs-card__title">{group.title}</h3>
                <p className="sgs-card__desc">{group.subTitle}</p>

                <div className="sgs-card__footer">
                  <div className="sgs-card__count">
                    <span className="sgs-card__count-num">{speciesCount.toLocaleString()}</span>
                    <span className="sgs-card__count-unit">loài trong CSDL</span>
                  </div>
                  <span className="sgs-card__cta">
                    Khám phá
                    <ArrowRight size={16} className="sgs-card__cta-arrow" />
                  </span>
                </div>
              </div>
            </Link>
          )
        })}
      </div>
    </section>
  )
}

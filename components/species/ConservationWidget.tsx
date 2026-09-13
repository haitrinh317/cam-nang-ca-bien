'use client'

import React from 'react'
import {
  ShieldAlert,
  AlertTriangle,
  Activity,
  Globe,
  BookOpen,
  BookmarkCheck,
  ExternalLink
} from 'lucide-react'
import type { VnRedListInfo } from './VnRedListBadge'
import { VN_REDLIST_LABEL } from './VnRedListBadge'
import './ConservationWidget.css'

export interface ConservationWidgetProps {
  vnRedList?: VnRedListInfo | null
  iucnStatus?: string | null
  speciesName?: string
  scientificName?: string
}

// Bảng cấu hình giao diện & màu sắc chủ đạo theo phân hạng bảo tồn
const STATUS_CONFIG: Record<string, {
  color: string
  themeClass: string
  defaultVn: string
}> = {
  CR: {
    color: '#dc2626',
    themeClass: 'theme-cr',
    defaultVn: 'Cực kỳ nguy cấp',
  },
  EN: {
    color: '#ea580c',
    themeClass: 'theme-en',
    defaultVn: 'Nguy cấp',
  },
  VU: {
    color: '#d97706',
    themeClass: 'theme-vu',
    defaultVn: 'Sắp nguy cấp',
  },
  NT: {
    color: '#65a30d',
    themeClass: 'theme-nt',
    defaultVn: 'Gần bị đe dọa',
  },
  LC: {
    color: '#16a34a',
    themeClass: 'theme-lc',
    defaultVn: 'Ít quan tâm',
  },
  EW: {
    color: '#7c3aed',
    themeClass: 'theme-ew',
    defaultVn: 'Tuyệt chủng ngoài tự nhiên',
  },
  EX: {
    color: '#475569',
    themeClass: 'theme-ex',
    defaultVn: 'Tuyệt chủng',
  },
  DD: {
    color: '#64748b',
    themeClass: 'theme-dd',
    defaultVn: 'Thiếu dữ liệu',
  },
}

export default function ConservationWidget({
  vnRedList,
  iucnStatus,
  speciesName,
  scientificName,
}: ConservationWidgetProps) {
  if (!vnRedList) return null

  const statusCode = (vnRedList.status || '').toUpperCase().trim()
  const config = STATUS_CONFIG[statusCode] || {
    color: '#d97706',
    themeClass: 'theme-vu',
    defaultVn: 'Bảo tồn cấp thiết',
  }

  const statusVn = vnRedList.statusVn || VN_REDLIST_LABEL[statusCode] || config.defaultVn
  const refCode = vnRedList.refCode
  const threats = vnRedList.threats
  const population = vnRedList.population
  const conservation = vnRedList.conservation
  const vastUrl = vnRedList.url || 'http://vnredlist.vast.vn/'

  // Nếu không có bất kỳ nội dung chi tiết nào, không hiển thị card lớn
  if (!threats && !conservation && !population && !statusCode) {
    return null
  }

  return (
    <section 
      className={`conservation-widget ${config.themeClass}`} 
      aria-label="Hồ sơ Bảo tồn và Sách Đỏ Việt Nam"
      style={{ '--status-accent': config.color } as React.CSSProperties}
    >
      {/* ─── Widget Header ─── */}
      <div className="conservation-widget__header">
        <div className="conservation-widget__title-group">
          <div className="conservation-widget__icon-box">
            <ShieldAlert size={24} />
          </div>
          <div className="conservation-widget__title-wrap">
            <h3 className="conservation-widget__title">
              Hồ Sơ Bảo Tồn &amp; Sách Đỏ Việt Nam
            </h3>
            <p className="conservation-widget__subtitle">
              Danh lục Đỏ Việt Nam — Viện Hàn lâm Khoa học và Công nghệ (VAST 2024)
            </p>
          </div>
        </div>

        {/* Badges Phân Hạng Song Hành */}
        <div className="conservation-widget__badges">
          {statusCode && (
            <span className="conservation-badge conservation-badge--status">
              <span className="conservation-badge__dot" />
              <span>SĐVN: {statusCode} — {statusVn}</span>
            </span>
          )}

          {iucnStatus && (
            <span className="conservation-badge conservation-badge--iucn">
              <Globe size={12} />
              <span>IUCN: {iucnStatus}</span>
            </span>
          )}

          {refCode && (
            <span className="conservation-badge conservation-badge--code">
              <BookmarkCheck size={12} />
              <span>Mã VAST: {refCode}</span>
            </span>
          )}
        </div>
      </div>

      {/* ─── Bento Grid Chi Tiết Bảo Tồn ─── */}
      <div className="conservation-widget__grid">
        {/* 1. Mối đe dọa tại vùng biển Việt Nam */}
        {threats && (
          <div className="conservation-card">
            <div className="conservation-card__header">
              <span className="conservation-card__icon conservation-card__icon--warning">
                <AlertTriangle size={15} />
              </span>
              <span>Mối đe dọa tại vùng biển Việt Nam</span>
            </div>
            <p className="conservation-card__body">{threats}</p>
          </div>
        )}

        {/* 2. Hiện trạng & Xu hướng quần thể tại Việt Nam */}
        {population && (
          <div className="conservation-card">
            <div className="conservation-card__header">
              <span className="conservation-card__icon">
                <Activity size={15} />
              </span>
              <span>Hiện trạng &amp; Xu hướng quần thể tại VN</span>
            </div>
            <p className="conservation-card__body">{population}</p>
          </div>
        )}

        {/* 3. Biện pháp bảo tồn hiện hành & Đề xuất cấp thiết (Hero Action Card) */}
        {conservation && (
          <div className="conservation-card conservation-card--hero">
            <div className="conservation-card__header">
              <span className="conservation-card__icon conservation-card__icon--hero">
                <ShieldAlert size={17} />
              </span>
              <span>BIỆN PHÁP BẢO TỒN HIỆN HÀNH &amp; ĐỀ XUẤT CẤP THIẾT</span>
            </div>
            <p className="conservation-card__body">{conservation}</p>
          </div>
        )}
      </div>

      {/* ─── Footer: Nguồn tham khảo từ vnredlist.vast.vn ─── */}
      <div className="conservation-widget__footer">
        <div className="conservation-credit">
          <BookOpen size={14} />
          <span>
            Nguồn tham khảo:{' '}
            <a 
              href={vastUrl} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="conservation-link"
              title="Mở hồ sơ gốc trên Cổng Danh Lục Đỏ Việt Nam (VAST)"
            >
              vnredlist.vast.vn
              <ExternalLink size={12} style={{ marginLeft: 4, verticalAlign: 'middle' }} />
            </a>
          </span>
        </div>
      </div>
    </section>
  )
}

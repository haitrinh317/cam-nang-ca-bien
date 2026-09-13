import React from 'react'

export const VN_REDLIST_COLOR: Record<string, string> = {
  LC: '#22c55e', // Ít quan tâm
  NT: '#84cc16', // Gần bị đe dọa
  VU: '#f59e0b', // Sắp nguy cấp
  EN: '#ea580c', // Nguy cấp
  CR: '#dc2626', // Cực kỳ nguy cấp
  EW: '#7c3aed', // Tuyệt chủng ngoài tự nhiên
  EX: '#475569', // Tuyệt chủng
  DD: '#64748b', // Thiếu dữ liệu
}

export const VN_REDLIST_LABEL: Record<string, string> = {
  LC: 'Ít quan tâm',
  NT: 'Gần bị đe dọa',
  VU: 'Sắp nguy cấp',
  EN: 'Nguy cấp',
  CR: 'Cực kỳ nguy cấp',
  EW: 'Tuyệt chủng ngoài tự nhiên',
  EX: 'Tuyệt chủng',
  DD: 'Thiếu dữ liệu',
}

export interface VnRedListInfo {
  status?: string | null
  statusVn?: string | null
  year?: string | null
  version?: string | null
  assessor?: string | null
  contributor?: string | null
  refCode?: string | null
  citation?: string | null
  criteria?: string | null
  threats?: string | null
  conservation?: string | null
  population?: string | null
  url?: string | null
}

interface VnRedListBadgeProps {
  status?: string | null
  refCode?: string | null
  showTooltip?: boolean
  compact?: boolean
  className?: string
  style?: React.CSSProperties
}

/**
 * Huy hiệu Danh Lục Đỏ Việt Nam (VAST 2024)
 * Thiết kế cao cấp đồng bộ cùng IucnBadge tạo nên hệ thống Dual-Conservation Badges
 */
export default function VnRedListBadge({
  status,
  refCode,
  showTooltip = true,
  compact = false,
  className = '',
  style = {},
}: VnRedListBadgeProps) {
  if (!status) return null

  const code = status.toUpperCase().trim()
  const label = VN_REDLIST_LABEL[code] || code
  const statusThemeClass = `vn-redlist-badge--${code.toLowerCase()}`
  const compactClass = compact ? 'vn-redlist-badge--compact' : ''

  const tooltipText = showTooltip
    ? `Danh Lục Đỏ Việt Nam (VAST 2024): ${code} — ${label}${refCode ? ` (Mã: ${refCode})` : ''}`
    : undefined

  return (
    <span
      className={`vn-redlist-badge ${statusThemeClass} ${compactClass} ${className}`}
      title={tooltipText}
      style={style}
    >
      <span className="vn-redlist-badge__dot" aria-hidden="true" />
      <span style={{ fontSize: '0.7rem', opacity: 0.85, fontWeight: 600 }}>SĐVN:</span>
      <span>{code}</span>
      {refCode && !compact && (
        <span
          style={{
            fontSize: '0.68rem',
            opacity: 0.75,
            fontWeight: 500,
            marginLeft: 1,
          }}
        >
          ({refCode})
        </span>
      )}
    </span>
  )
}

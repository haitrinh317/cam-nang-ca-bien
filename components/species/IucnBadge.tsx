import React from 'react'

export const IUCN_COLOR: Record<string, string> = {
  LC: '#22c55e', // Least Concern - Ít quan tâm
  NT: '#84cc16', // Near Threatened - Gần bị đe dọa
  VU: '#f59e0b', // Vulnerable - Sắp nguy cấp
  EN: '#f97316', // Endangered - Nguy cấp
  CR: '#ef4444', // Critically Endangered - Cực kỳ nguy cấp
  EX: '#7c3aed', // Extinct - Tuyệt chủng
  EW: '#7c3aed', // Extinct in the wild
  DD: '#94a3b8', // Data Deficient - Thiếu dữ liệu
}

export const IUCN_LABEL_VN: Record<string, string> = {
  LC: 'Ít quan tâm',
  NT: 'Gần bị đe dọa',
  VU: 'Sắp nguy cấp',
  EN: 'Nguy cấp',
  CR: 'Cực kỳ nguy cấp',
  EX: 'Tuyệt chủng',
  EW: 'Tuyệt chủng ngoài tự nhiên',
  DD: 'Thiếu dữ liệu',
}

interface IucnBadgeProps {
  status?: string | null
  showTooltip?: boolean
  className?: string
  style?: React.CSSProperties
}

/**
 * IUCN Badge component chuẩn hóa từ tab Sinh học (SpecimenCard)
 * Tái sử dụng đồng bộ cho toàn bộ hệ thống: Chi tiết loài, Danh mục, Nhóm nguy cấp
 */
export default function IucnBadge({ status, showTooltip = true, className = '', style = {} }: IucnBadgeProps) {
  if (!status) return null
  const code = status.toUpperCase().trim()
  const iucnColor = IUCN_COLOR[code] || '#94a3b8'
  const labelVn = IUCN_LABEL_VN[code] || code

  return (
    <span
      className={`iucn-badge-tag ${className}`}
      title={showTooltip ? `Sách Đỏ IUCN: ${code} — ${labelVn}` : undefined}
      style={{
        display: 'inline-block',
        padding: '0.15rem 0.5rem',
        borderRadius: '4px',
        background: `${iucnColor}22`,
        border: `1px solid ${iucnColor}55`,
        color: iucnColor,
        fontWeight: 700,
        fontSize: '0.82rem',
        letterSpacing: '.05em',
        lineHeight: 1.2,
        verticalAlign: 'middle',
        ...style,
      }}
    >
      {code}
    </span>
  )
}

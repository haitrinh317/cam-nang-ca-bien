'use client'

import React from 'react'
import { ExternalLink, CheckCircle, AlertTriangle } from 'lucide-react'

interface WormsBadgeProps {
  worms_status: string | null
  worms_id: number | null
  worms_accepted_name: string | null
  worms_synced_at: string | null
}

export default function WormsBadge({ worms_status, worms_id, worms_accepted_name, worms_synced_at }: WormsBadgeProps) {
  if (!worms_status && !worms_id) return null

  const statusRaw = (worms_status || '').toLowerCase().trim()
  const isValid = statusRaw === 'valid' || statusRaw === 'accepted'
  const isSynonym = statusRaw === 'synonym' || statusRaw === 'unaccepted' ||
                    statusRaw.includes('synonym') || statusRaw.includes('misspelling') ||
                    statusRaw.includes('superseded')
  const isUncertain = statusRaw === 'uncertain' || statusRaw === 'doubtful' || statusRaw === 'nomen dubium'

  let badgeType: 'valid' | 'synonym' | 'uncertain' | 'unknown' = 'unknown'
  let label = 'Chưa có trên WoRMS'
  let tooltip = 'Chưa tìm thấy bản ghi tương ứng trong CSDL WoRMS'
  let icon = <AlertTriangle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
  let inlineTheme = {
    bg: 'rgba(148, 163, 184, 0.12)',
    color: '#64748b',
    border: '1px solid rgba(148, 163, 184, 0.28)'
  }

  if (isValid || (worms_id && !isSynonym && !isUncertain && statusRaw !== 'not_found' && statusRaw !== 'parse_error')) {
    badgeType = 'valid'
    label = 'WoRMS: Tên hợp lệ'
    tooltip = `Tên được xác nhận trên WoRMS (AphiaID: ${worms_id || '—'})${worms_synced_at ? ` · Cập nhật: ${worms_synced_at.substring(0, 10)}` : ''}`
    icon = <CheckCircle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
    inlineTheme = {
      bg: 'rgba(16, 185, 129, 0.08)',
      color: '#047857',
      border: '1px solid rgba(16, 185, 129, 0.3)'
    }
  } else if (isSynonym) {
    badgeType = 'synonym'
    label = 'WoRMS: Danh pháp cũ'
    tooltip = `Danh pháp đồng nghĩa (Synonym). Tên hiện hành: ${worms_accepted_name || '?'}`
    icon = <AlertTriangle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
    inlineTheme = {
      bg: 'rgba(245, 158, 11, 0.08)',
      color: '#b45309',
      border: '1px solid rgba(245, 158, 11, 0.35)'
    }
  } else if (isUncertain) {
    badgeType = 'uncertain'
    label = 'WoRMS: Chưa rõ phân loại'
    tooltip = worms_accepted_name ? `Ghi nhận: ${worms_accepted_name}` : 'Trạng thái phân loại học chưa được xác định chắc chắn'
    icon = <AlertTriangle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
  } else if (statusRaw === 'parse_error') {
    badgeType = 'unknown'
    label = 'WoRMS: Lỗi cú pháp'
    tooltip = 'Lỗi cú pháp định dạng danh pháp khoa học'
    icon = <AlertTriangle size={12} aria-hidden="true" style={{ flexShrink: 0 }} />
  }

  const wormsUrl = worms_id
    ? `https://www.marinespecies.org/aphia.php?p=taxdetails&id=${worms_id}` : null

  const pillStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    height: '24px',
    padding: '0 10px',
    borderRadius: '9999px',
    fontSize: '0.72rem',
    fontWeight: 600,
    lineHeight: 1,
    textDecoration: 'none',
    whiteSpace: 'nowrap',
    backgroundColor: inlineTheme.bg,
    color: inlineTheme.color,
    border: inlineTheme.border,
    boxSizing: 'border-box'
  }

  return (
    <div className="worms-badge-wrap" style={{ display: 'inline-flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
      {wormsUrl ? (
        <a
          href={wormsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className={`worms-pill worms-pill--${badgeType}`}
          style={pillStyle}
          title={`${tooltip} — Bấm để mở hồ sơ CSDL WoRMS`}
        >
          <span className="worms-pill__icon" style={{ display: 'inline-flex', alignItems: 'center', marginRight: '2px' }}>{icon}</span>
          <span className="worms-pill__label">{label}</span>
          <ExternalLink size={11} className="worms-pill__ext" style={{ marginLeft: '4px', opacity: 0.7 }} aria-hidden="true" />
        </a>
      ) : (
        <span className={`worms-pill worms-pill--${badgeType}`} style={pillStyle} title={tooltip}>
          <span className="worms-pill__icon" style={{ display: 'inline-flex', alignItems: 'center', marginRight: '2px' }}>{icon}</span>
          <span className="worms-pill__label">{label}</span>
        </span>
      )}

      {isSynonym && worms_accepted_name && (
        <span className="worms-pill__synonym-note" style={{ fontSize: '0.76rem', color: 'var(--color-ink-3, #64748b)', marginLeft: '4px' }}>
          Tên hiện hành: <em className="worms-pill__accepted-name" style={{ fontStyle: 'italic', fontWeight: 600 }}>{worms_accepted_name}</em>
        </span>
      )}
    </div>
  )
}

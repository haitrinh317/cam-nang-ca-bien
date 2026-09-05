'use client'

import React from 'react'
import { Ruler, Waves, MapPin, Globe, CheckCircle2 } from 'lucide-react'
import './SpecimenVisualWidgets.css'

interface VisualWidgetsProps {
  sizeStr?: string | null
  vnSizeStr?: string | null
  enSizeStr?: string | null
  maxLengthStr?: string | null
  depthStr?: string | null
  depthVnStr?: string | null
  distributionStr?: string | null
}

/**
 * Trích xuất kích thước chiều dài tiêu chuẩn (cm) từ chuỗi mô tả
 * Hỗ trợ mm, cm, m và các định dạng tiếng Việt & FishBase
 */
function parseBodySize(raw: string): number | null {
  if (!raw || typeof raw !== 'string') return null
  const text = raw.trim().toLowerCase()

  // 1. Ưu tiên số có từ khóa lớn nhất / tối đa / maximum / max / up to
  const maxKeywords = /(?:lớn nhất|tối đa|maximum|max|up to|đạt tới|chiều dài tới)\s*(?:khoảng|chừng)?\s*:?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm|m\b)/i
  const maxMatch = text.match(maxKeywords)
  if (maxMatch) {
    const val = parseFloat(maxMatch[1].replace(',', '.'))
    const unit = maxMatch[2].toLowerCase()
    if (unit === 'mm') return Math.round((val / 10) * 10) / 10
    if (unit === 'm') return Math.round(val * 100 * 10) / 10
    return Math.round(val * 10) / 10
  }

  // 2. Tìm tất cả các cặp số kèm đơn vị đo mm, cm, m
  const unitRegex = /(\d+(?:[.,]\d+)?)\s*(mm|cm|m\b)/gi
  let match: RegExpExecArray | null
  const valuesInCm: number[] = []

  while ((match = unitRegex.exec(text)) !== null) {
    const val = parseFloat(match[1].replace(',', '.'))
    const unit = match[2].toLowerCase()
    let cm = val
    if (unit === 'mm') cm = val / 10
    else if (unit === 'm') cm = val * 100
    if (cm >= 0.5 && cm <= 3500) {
      valuesInCm.push(cm)
    }
  }

  if (valuesInCm.length > 0) {
    return Math.round(Math.max(...valuesInCm) * 10) / 10
  }

  // 3. Bắt khoảng số có đơn vị ở cuối (VD: 55 - 106 mm)
  const rangeMatch = text.match(/\d+(?:[.,]\d+)?\s*[\-\u2013\u2014]\s*(\d+(?:[.,]\d+)?)\s*(mm|cm|m\b)/i)
  if (rangeMatch) {
    const val = parseFloat(rangeMatch[1].replace(',', '.'))
    const unit = rangeMatch[2].toLowerCase()
    if (unit === 'mm') return Math.round((val / 10) * 10) / 10
    if (unit === 'm') return Math.round(val * 100 * 10) / 10
    return Math.round(val * 10) / 10
  }

  // 4. Fallback FishBase format (VD: "35.0 cm TL male/unsexed")
  const fbMatch = text.match(/(\d+(?:[.,]\d+)?)\s*(?:cm|m\b)/i)
  if (fbMatch) {
    const val = parseFloat(fbMatch[1].replace(',', '.'))
    return text.includes('m') && !text.includes('cm') && !text.includes('mm') ? val * 100 : val
  }

  return null
}

/**
 * Phân tích chuỗi phân bố địa lý thành 2 nhóm thẻ: Việt Nam & Thế giới
 */
function parseDistribution(raw?: string | null): { vn: string[]; world: string[]; fallback: string | null } {
  if (!raw || typeof raw !== 'string') return { vn: [], world: [], fallback: null }
  const text = raw.trim().replace(/\s+/g, ' ')

  let worldRaw = ''
  let vnRaw = ''

  // 1. Nhận diện cấu trúc: '..., Việt Nam. Vùng...' hoặc '... Việt Nam: ...' hoặc '...; Việt Nam: ...'
  const vnMatch = text.match(/(.*?)(?:Việt Nam\s*[:\.]\s*)(.*)/i)
  if (vnMatch) {
    worldRaw = vnMatch[1].replace(/Việt Nam\s*,?/gi, '').trim()
    vnRaw = vnMatch[2].trim()
  } else {
    // 2. Không có chữ 'Việt Nam.', nhưng có dấu chấm phân cách: 'Thái Bình Dương. Trung Bộ và Nam Bộ'
    const dotParts = text.split(/\.\s+/)
    if (dotParts.length >= 2) {
      worldRaw = dotParts[0].replace(/Việt Nam\s*,?/gi, '').trim()
      vnRaw = dotParts.slice(1).join('. ').trim()
    } else {
      worldRaw = text.replace(/Việt Nam\s*,?/gi, '').trim()
    }
  }

  // Parse Thế giới thành các mục riêng biệt
  const worldItems = worldRaw
    .split(/[,;:–—\/\.]|\bvà\b|\band\b/i)
    .map(s => s.trim().replace(/^[\-–—,\.;:\s]+|[\-–—,\.;:\s]+$/g, ''))
    .filter(s => s.length > 1 && !/^(nhiệt đới|á nhiệt đới|ven bờ|ven biển|vùng biển|khu vực|từ|đến|to|from)\b/i.test(s) && !/việt nam/i.test(s))

  // Loại bỏ trùng lặp trong danh sách thế giới
  const world = Array.from(new Set(worldItems))

  // Parse các vùng biển Việt Nam chuẩn
  const REGION_MAP = [
    { key: 'bac-bo', name: 'Vịnh Bắc Bộ', regex: /vịnh bắc bộ|bắc bộ|hải phòng|quảng ninh/i },
    { key: 'trung-bo', name: 'Vùng Biển Miền Trung', regex: /trung bộ|miền trung|đà nẵng|huế|quảng trị|quảng nam|quảng ngãi|bình định|phú yên|khánh hòa|nha trang|ninh thuận|bình thuận/i },
    { key: 'nam-bo', name: 'Vùng Biển Nam Bộ', regex: /nam bộ|đông nam bộ|vũng tàu|bà rịa|côn đảo/i },
    { key: 'tay-nam-bo', name: 'Vùng Biển Tây Nam (Phú Quốc)', regex: /tây nam|phú quốc|kiên giang|vịnh thái lan/i },
    { key: 'hoang-sa', name: 'Quần đảo Hoàng Sa', regex: /hoàng sa/i },
    { key: 'truong-sa', name: 'Quần đảo Trường Sa', regex: /trường sa/i },
  ]

  const vn: string[] = []
  REGION_MAP.forEach(r => {
    if (r.regex.test(vnRaw) || r.regex.test(text)) {
      vn.push(r.name)
    }
  })

  // Nếu có đề cập đến Việt Nam nhưng không rõ vùng cụ thể
  if (vn.length === 0 && (vnRaw.length > 2 || /việt nam/i.test(text))) {
    vn.push('Vùng biển Việt Nam')
  }

  // Fallback nếu không bóc tách được mục nào
  const fallback = (world.length === 0 && vn.length === 0) ? text : null

  return { world, vn, fallback }
}

export default function SpecimenVisualWidgets({
  sizeStr,
  vnSizeStr,
  enSizeStr,
  maxLengthStr,
  depthStr,
  depthVnStr,
  distributionStr,
}: VisualWidgetsProps) {
  // ── 1. Kích thước (cm) — Hỗ trợ song ngữ VN/EN ──
  const effectiveVnSize = vnSizeStr || sizeStr || ''
  const effectiveEnSize = enSizeStr || ''
  const rawSize = effectiveVnSize || effectiveEnSize || maxLengthStr || ''
  const sizeCm = parseBodySize(effectiveVnSize) || parseBodySize(effectiveEnSize) || (maxLengthStr ? parseBodySize(maxLengthStr) : null)

  let maxScaleCm = 200
  let scaleLabels = {
    start: '0 cm',
    mid1: '15 cm (Bàn tay)',
    mid2: '100 cm (1m)',
    end: '200+ cm',
  }

  if (sizeCm != null) {
    if (sizeCm <= 40) {
      maxScaleCm = 40
      scaleLabels = {
        start: '0 cm',
        mid1: '15 cm (Bàn tay)',
        mid2: '25 cm',
        end: '40 cm',
      }
    } else if (sizeCm <= 100) {
      maxScaleCm = 100
      scaleLabels = {
        start: '0 cm',
        mid1: '15 cm (Bàn tay)',
        mid2: '50 cm (Nửa mét)',
        end: '100 cm (1m)',
      }
    } else if (sizeCm > 250) {
      maxScaleCm = Math.max(500, Math.ceil(sizeCm / 100) * 100)
      scaleLabels = {
        start: '0 m',
        mid1: '1 m',
        mid2: '2 m (Người lớn)',
        end: `${maxScaleCm / 100}m+`,
      }
    }
  }

  const fillPercent = sizeCm != null ? Math.min(100, Math.max(6, (sizeCm / maxScaleCm) * 100)) : 0

  // ── 2. Độ sâu (m) ──
  const rawDepth = depthVnStr || depthStr || ''
  const depthMatches = rawDepth.match(/\b(\d+)\b/g)
  let minDepth = 0
  let maxDepth: number | null = null
  if (depthMatches && depthMatches.length >= 2) {
    minDepth = parseInt(depthMatches[0], 10)
    maxDepth = parseInt(depthMatches[1], 10)
  } else if (depthMatches && depthMatches.length === 1) {
    maxDepth = parseInt(depthMatches[0], 10)
  }

  const isEpipelagic = minDepth <= 200 // 0 - 200m
  const isMesopelagic = (maxDepth != null && maxDepth > 200) || (minDepth > 200 && minDepth <= 1000) // 200 - 1000m
  const isBathypelagic = (maxDepth != null && maxDepth > 1000) || minDepth > 1000 // > 1000m

  // ── 3. Phân bố địa lý: Tách thành Việt Nam & Thế giới ──
  const { vn: vnLocations, world: worldLocations, fallback: distFallback } = parseDistribution(distributionStr)
  const hasDistribution = vnLocations.length > 0 || worldLocations.length > 0 || distFallback != null

  const hasAnyVisualData = sizeCm != null || maxDepth != null || hasDistribution

  if (!hasAnyVisualData) return null

  return (
    <div
      className="specimen-visual-widgets"
      style={{
        marginTop: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem',
        width: '100%',
        fontFamily: "var(--font-body, 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif)",
      }}
    >
      {/* ── Khối 1: Thước đo kích thước chiều dài (Song ngữ VN/EN) ── */}
      {sizeCm != null && (
        <div
          className="visual-widget-card visual-widget-card--size"
          style={{
            background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.05) 0%, rgba(6, 182, 212, 0.02) 100%)',
            border: '1px solid rgba(14, 165, 233, 0.2)',
            borderRadius: '12px',
            padding: '16px 20px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.02)',
          }}
        >
          <div
            className="vwc-header"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Ruler size={16} className="vwc-icon vwc-icon--cyan" style={{ color: '#0284c7' }} />
              <span
                className="vwc-title"
                style={{
                  fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  letterSpacing: '0.03em',
                  textTransform: 'uppercase',
                  color: 'var(--color-ink-2, #1e293b)',
                }}
              >
                Kích thước chiều dài
              </span>
            </div>
            <span
              className="vwc-badge vwc-badge--cyan"
              style={{
                fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                fontSize: '0.85rem',
                fontWeight: 700,
                padding: '3px 11px',
                borderRadius: '9999px',
                color: '#0284c7',
                background: 'rgba(14, 165, 233, 0.12)',
                border: '1px solid rgba(14, 165, 233, 0.28)',
                fontFeatureSettings: '"tnum" 1',
              }}
            >
              {sizeCm >= 100 ? `${(sizeCm / 100).toFixed(1)} m` : `${sizeCm} cm`}
            </span>
          </div>

          <div className="size-scale-container" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div
              className="size-scale-track"
              style={{
                width: '100%',
                height: '9px',
                background: 'var(--color-paper-3, #e2e8f0)',
                borderRadius: '9999px',
                overflow: 'hidden',
                position: 'relative',
              }}
            >
              <div
                className="size-scale-fill"
                style={{
                  width: `${fillPercent}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, #0284c7 0%, #06b6d4 100%)',
                  borderRadius: '9999px',
                  transition: 'width 0.3s ease-out',
                  boxShadow: '0 0 8px rgba(6, 182, 212, 0.4)',
                }}
              />
            </div>
            <div
              className="size-scale-labels"
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                fontSize: '0.76rem',
                fontWeight: 500,
                color: 'var(--color-ink-3, #64748b)',
                marginTop: '2px',
                fontFeatureSettings: '"tnum" 1',
              }}
            >
              <span>{scaleLabels.start}</span>
              <span className="scale-ref">{scaleLabels.mid1}</span>
              <span className="scale-ref">{scaleLabels.mid2}</span>
              <span>{scaleLabels.end}</span>
            </div>
          </div>

          {/* Ghi nhận mẫu vật song ngữ (VN & EN) */}
          <div
            className="vwc-size-notes"
            style={{
              marginTop: '10px',
              paddingTop: '8px',
              borderTop: '1px dashed rgba(14, 165, 233, 0.15)',
              display: 'flex',
              flexDirection: 'column',
              gap: '3px',
            }}
          >
            {effectiveVnSize && (
              <p
                className="vwc-note"
                style={{
                  fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                  fontSize: '0.85rem',
                  color: 'var(--color-ink-2, #334155)',
                  margin: 0,
                  lineHeight: 1.45,
                  maxWidth: 'none',
                  width: '100%',
                }}
              >
                Ghi nhận mẫu vật: <strong style={{ color: 'var(--color-ink, #0f172a)' }}>{effectiveVnSize}</strong>
              </p>
            )}

            {effectiveEnSize && effectiveEnSize.toLowerCase() !== effectiveVnSize.toLowerCase() && (
              <p
                className="vwc-note-en"
                style={{
                  fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                  fontSize: '0.8rem',
                  color: 'var(--color-neutral, #64748b)',
                  margin: 0,
                  lineHeight: 1.4,
                  fontStyle: 'italic',
                  maxWidth: 'none',
                  width: '100%',
                }}
              >
                Size: {effectiveEnSize}
              </p>
            )}

            {!effectiveVnSize && !effectiveEnSize && rawSize && (
              <p
                className="vwc-note"
                style={{
                  fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                  fontSize: '0.85rem',
                  color: 'var(--color-ink-2, #334155)',
                  margin: 0,
                  lineHeight: 1.45,
                }}
              >
                Ghi nhận: <strong style={{ color: 'var(--color-ink, #0f172a)' }}>{rawSize}</strong>
              </p>
            )}
          </div>
        </div>
      )}

      {/* ── Khối 2: Dải độ sâu sinh thái đại dương ── */}
      {maxDepth != null && (
        <div className="visual-widget-card visual-widget-card--depth">
          <div className="vwc-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Waves size={16} className="vwc-icon vwc-icon--blue" />
              <span className="vwc-title">
                Dải độ sâu sinh thái
              </span>
            </div>
            <span className="vwc-badge vwc-badge--blue">
              {minDepth}m – {maxDepth}m
            </span>
          </div>

          <div className="depth-zones-container">
            {/* Tầng 1: Tầng chiếu sáng */}
            <div className={`depth-zone-item ${isEpipelagic ? 'is-active' : ''}`}>
              <span className="dzi-depth">0 – 200m</span>
              <span className="dzi-label">Tầng chiếu sáng (Epipelagic)</span>
            </div>

            {/* Tầng 2: Tầng chạng vạng */}
            <div className={`depth-zone-item ${isMesopelagic ? 'is-active' : ''}`}>
              <span className="dzi-depth">200 – 1.000m</span>
              <span className="dzi-label">Tầng chạng vạng (Mesopelagic)</span>
            </div>

            {/* Tầng 3: Tầng biển sâu */}
            <div className={`depth-zone-item ${isBathypelagic ? 'is-active' : ''}`}>
              <span className="dzi-depth">&gt; 1.000m</span>
              <span className="dzi-label">Tầng biển sâu (Bathypelagic)</span>
            </div>
          </div>
          <p className="vwc-note">
            Độ sâu ghi nhận: <strong>{rawDepth}</strong>
          </p>
        </div>
      )}

      {/* ── Khối 3: Thẻ địa bàn phân bố (Việt Nam & Thế giới) ── */}
      {hasDistribution && (
        <div
          className="visual-widget-card visual-widget-card--distribution"
          style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.04) 0%, rgba(14, 165, 233, 0.02) 100%)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            borderRadius: '12px',
            padding: '16px 20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          {/* Nhóm 1: Việt Nam */}
          {vnLocations.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MapPin size={15} style={{ color: '#059669', flexShrink: 0 }} />
                <span
                  style={{
                    fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                    fontSize: '0.76rem',
                    fontWeight: 700,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                    color: '#059669',
                  }}
                >
                  Việt Nam
                </span>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {vnLocations.map((loc, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '5px 12px',
                      borderRadius: '9999px',
                      fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      background: 'rgba(5, 150, 105, 0.1)',
                      border: '1px solid rgba(5, 150, 105, 0.3)',
                      color: '#059669',
                    }}
                  >
                    <CheckCircle2 size={13} style={{ color: '#059669' }} />
                    <span>{loc}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Nhóm 2: Thế giới */}
          {worldLocations.length > 0 && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                paddingTop: vnLocations.length > 0 ? '8px' : 0,
                borderTop: vnLocations.length > 0 ? '1px dashed rgba(0, 0, 0, 0.08)' : 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Globe size={15} style={{ color: '#0284c7', flexShrink: 0 }} />
                <span
                  style={{
                    fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                    fontSize: '0.76rem',
                    fontWeight: 700,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                    color: '#0284c7',
                  }}
                >
                  Thế giới
                </span>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {worldLocations.map((loc, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '5px 12px',
                      borderRadius: '9999px',
                      fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                      fontSize: '0.82rem',
                      fontWeight: 500,
                      background: 'rgba(2, 132, 199, 0.07)',
                      border: '1px solid rgba(2, 132, 199, 0.22)',
                      color: '#0369a1',
                    }}
                  >
                    <span>{loc}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Fallback nếu chuỗi không thể tách thành tag */}
          {distFallback && (
            <p
              style={{
                fontFamily: "var(--font-body, 'Be Vietnam Pro', sans-serif)",
                fontSize: '0.85rem',
                color: 'var(--color-ink-3, #475569)',
                margin: 0,
                lineHeight: 1.5,
              }}
            >
              {distFallback}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

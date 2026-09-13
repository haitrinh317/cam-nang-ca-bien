'use client'

import React from 'react'
import {
  ShieldAlert,
  AlertTriangle,
  Activity,
  Globe,
  BookOpen,
  BookmarkCheck,
  ExternalLink,
  CheckCircle2,
  Lightbulb,
  TrendingDown,
  TrendingUp,
  Minus
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

/**
 * Phân tích cú pháp an toàn các thẻ HTML định dạng: <i>, <em>, <b>, <strong>, <u>
 * Trả về React Elements (Zero XSS, không dùng dangerouslySetInnerHTML)
 */
function renderFormattedInline(rawText: string): React.ReactNode[] {
  if (!rawText) return []
  const tokens = rawText.split(/(<\/?(?:i|b|em|strong|u)>)/gi)
  const nodes: React.ReactNode[] = []

  let isItalic = false
  let isBold = false
  let isUnderline = false

  tokens.forEach((token, idx) => {
    const lower = token.toLowerCase()
    if (lower === '<i>' || lower === '<em>') {
      isItalic = true
    } else if (lower === '</i>' || lower === '</em>') {
      isItalic = false
    } else if (lower === '<b>' || lower === '<strong>') {
      isBold = true
    } else if (lower === '</b>' || lower === '</strong>') {
      isBold = false
    } else if (lower === '<u>') {
      isUnderline = true
    } else if (lower === '</u>') {
      isUnderline = false
    } else if (token) {
      if (isItalic && isBold) {
        nodes.push(<strong key={idx}><em style={{ fontStyle: 'italic' }}>{token}</em></strong>)
      } else if (isItalic) {
        nodes.push(<em key={idx} style={{ fontStyle: 'italic', fontWeight: 'inherit' }}>{token}</em>)
      } else if (isBold) {
        nodes.push(<strong key={idx} style={{ fontWeight: 700 }}>{token}</strong>)
      } else if (isUnderline) {
        nodes.push(<u key={idx}>{token}</u>)
      } else {
        nodes.push(token)
      }
    }
  })

  return nodes
}

/**
 * Tự động ngắt đoạn văn thông minh cho nội dung bảo tồn:
 * - Ưu tiên dấu ngắt dòng có sẵn (\n)
 * - Tách câu tại dấu chấm/chấm than/hỏi, bảo vệ các từ viết tắt học thuật (NĐ-CP, Ref., sp., et al., GS., TS.)
 * - Nhóm 2-3 câu thành từng đoạn văn thoáng đãng, dễ đọc
 */
function splitIntoParagraphs(text: string): string[] {
  if (!text) return []
  const trimmed = text.trim()
  if (!trimmed) return []

  // 1. Nếu văn bản đã có ngắt dòng
  if (trimmed.includes('\n')) {
    return trimmed
      .split(/\n+/)
      .map(p => p.trim())
      .filter(Boolean)
  }

  // 2. Nếu văn bản ngắn (dưới 180 ký tự), giữ nguyên 1 đoạn
  if (trimmed.length <= 180) {
    return [trimmed]
  }

  // 3. Tách câu thông minh có bảo vệ từ viết tắt
  const protectedText = trimmed.replace(
    /\b(Refs?|sp|spp|et al|e\.g|i\.e|NĐ-CP|GS|TS|ThS)\.\s*/gi,
    (m, word) => `${word}_DOT_ `
  )

  const sentences = protectedText
    .split(/(?<=[.!?])\s+(?=[\p{Lu}0-9])/u)
    .map(s => s.replace(/_DOT_/g, '.').trim())
    .filter(Boolean)

  if (sentences.length <= 2) {
    return [trimmed]
  }

  const paragraphs: string[] = []
  let currentChunk: string[] = []
  let currentLen = 0

  for (const s of sentences) {
    currentChunk.push(s)
    currentLen += s.length

    // Khi đã có từ 2 câu và dài trên 180 ký tự, hoặc đủ 3 câu -> tạo đoạn mới
    if ((currentChunk.length >= 2 && currentLen >= 180) || currentChunk.length >= 3) {
      paragraphs.push(currentChunk.join(' '))
      currentChunk = []
      currentLen = 0
    }
  }

  if (currentChunk.length > 0) {
    if (paragraphs.length > 0 && currentChunk.length === 1 && currentLen < 120) {
      paragraphs[paragraphs.length - 1] += ' ' + currentChunk.join(' ')
    } else {
      paragraphs.push(currentChunk.join(' '))
    }
  }

  return paragraphs
}

/**
 * Xử lý & làm sạch trường Mối đe dọa (threats):
 * - Loại bỏ tiền tố nhãn lặp 'Mối đe dọa'
 * - Chuẩn hóa dấu chấm liền từ viết hoa
 * - Tách đoạn văn bản rõ ràng
 */
function cleanThreats(raw?: string | null): string[] {
  if (!raw) return []
  let cleaned = raw.replace(/^Mối\s+đe\s+d[ọo]a\s*:?\s*/i, '').trim()
  cleaned = cleaned.replace(/\.([\p{Lu}])/gu, '. $1')
  return splitIntoParagraphs(cleaned)
}

/**
 * Xử lý & làm sạch trường Hiện trạng & Xu hướng quần thể (population):
 * - Loại bỏ tiền tố lặp 'Hiện trạng quần thể Hiện trạng quần thể'
 * - Tách riêng chỉ số 'Xu hướng quần thể' (Suy giảm, Ổn định, Không rõ...) thành pill độc lập
 * - Phân đoạn thân bài khảo sát
 */
function cleanPopulation(raw?: string | null): { paragraphs: string[]; trend: string } {
  if (!raw) return { paragraphs: [], trend: '' }
  let cleaned = raw.replace(/^(Hiện\s+trạng\s+quần\s+thể\s*:?\s*)+/i, '').trim()
  cleaned = cleaned.replace(/\.([\p{Lu}])/gu, '. $1')

  const trendMatch = cleaned.match(/(?:[\.\s]|^)Xu\s+hướng\s+quần\s+thể\s*:?\s*([^\.\n]+(?:\.|$))/i)
  let trend = ''
  if (trendMatch) {
    trend = trendMatch[1].replace(/\.$/, '').trim()
    cleaned = cleaned.replace(trendMatch[0], '').trim()
  }

  return {
    paragraphs: splitIntoParagraphs(cleaned),
    trend
  }
}

/**
 * Xử lý & cấu trúc trường Biện pháp bảo tồn (conservation):
 * - Tách 2 phân khu độc lập: Biện pháp đã ban hành (Đã có) & Đề xuất cấp thiết (Đề xuất)
 * - Không để xảy ra tình trạng dính chữ 'Đã có Đề xuất' khi chưa có biện pháp hiện hành
 * - Phân đoạn từng khuyến nghị
 */
function cleanConservation(raw?: string | null): { existing: string[]; proposed: string[] } {
  if (!raw) return { existing: [], proposed: [] }
  let cleaned = raw.replace(/^Biện\s+pháp\s+bảo\s+tồn\s*:?\s*/i, '').trim()
  cleaned = cleaned.replace(/\.([\p{Lu}])/gu, '. $1')

  const deXuatIndex = cleaned.search(/(?:^|\s)Đề\s+xuất\s*:?\s*/i)
  let existingStr = ''
  let proposedStr = ''

  if (deXuatIndex !== -1) {
    existingStr = cleaned.slice(0, deXuatIndex).replace(/^(?:Đã\s+có\s*:?\s*)+/i, '').trim()
    proposedStr = cleaned.slice(deXuatIndex).replace(/^(?:[\s\.]|^)Đề\s+xuất\s*:?\s*/i, '').trim()
  } else {
    existingStr = cleaned.replace(/^(?:Đã\s+có\s*:?\s*)+/i, '').trim()
  }

  return {
    existing: splitIntoParagraphs(existingStr),
    proposed: splitIntoParagraphs(proposedStr)
  }
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

  // Xử lý làm sạch và phân đoạn văn bản
  const threatParagraphs = React.useMemo(() => cleanThreats(threats), [threats])
  const populationData = React.useMemo(() => cleanPopulation(population), [population])
  const conservationData = React.useMemo(() => cleanConservation(conservation), [conservation])

  // Nếu không có bất kỳ nội dung chi tiết nào, không hiển thị card lớn
  const hasDetails = threatParagraphs.length > 0 ||
    populationData.paragraphs.length > 0 ||
    conservationData.existing.length > 0 ||
    conservationData.proposed.length > 0 ||
    Boolean(statusCode)

  if (!hasDetails) {
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
        {threatParagraphs.length > 0 && (
          <div className="conservation-card">
            <div className="conservation-card__header">
              <span className="conservation-card__icon conservation-card__icon--warning">
                <AlertTriangle size={15} />
              </span>
              <span>Mối đe dọa tại vùng biển Việt Nam</span>
            </div>
            <div className="conservation-card__body">
              {threatParagraphs.map((p, idx) => (
                <p key={idx} className="conservation-card__text">
                  {renderFormattedInline(p)}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* 2. Hiện trạng & Xu hướng quần thể tại Việt Nam */}
        {(populationData.paragraphs.length > 0 || populationData.trend) && (
          <div className="conservation-card">
            <div className="conservation-card__header">
              <span className="conservation-card__icon">
                <Activity size={15} />
              </span>
              <span>Hiện trạng &amp; Xu hướng quần thể tại VN</span>
            </div>
            <div className="conservation-card__body">
              {populationData.paragraphs.map((p, idx) => (
                <p key={idx} className="conservation-card__text">
                  {renderFormattedInline(p)}
                </p>
              ))}

              {populationData.trend && (
                <div className="conservation-trend-pill">
                  {populationData.trend.toLowerCase().includes('giảm') ? (
                    <TrendingDown size={14} className="conservation-trend-pill__icon" />
                  ) : populationData.trend.toLowerCase().includes('tăng') ? (
                    <TrendingUp size={14} className="conservation-trend-pill__icon" />
                  ) : (
                    <Minus size={14} className="conservation-trend-pill__icon" />
                  )}
                  <span className="conservation-trend-pill__label">Xu hướng quần thể tại tự nhiên:</span>
                  <strong className="conservation-trend-pill__val">{populationData.trend}</strong>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 3. Biện pháp bảo tồn hiện hành & Đề xuất cấp thiết (Hero Action Card) */}
        {(conservationData.existing.length > 0 || conservationData.proposed.length > 0) && (
          <div className="conservation-card conservation-card--hero">
            <div className="conservation-card__header">
              <span className="conservation-card__icon conservation-card__icon--hero">
                <ShieldAlert size={17} />
              </span>
              <span>BIỆN PHÁP BẢO TỒN HIỆN HÀNH &amp; ĐỀ XUẤT CẤP THIẾT</span>
            </div>

            <div className="conservation-card__body conservation-card__body--hero">
              {/* Phân nhóm 1: Biện pháp đã có (Hiện hành) */}
              {conservationData.existing.length > 0 && (
                <div className="conservation-subgroup conservation-subgroup--existing">
                  <div className="conservation-subgroup__header">
                    <CheckCircle2 size={15} className="conservation-subgroup__icon" />
                    <span className="conservation-subgroup__title">Biện pháp đã ban hành (Hiện hành)</span>
                  </div>
                  <div className="conservation-subgroup__content">
                    {conservationData.existing.map((p, idx) => (
                      <p key={idx} className="conservation-card__text">
                        {renderFormattedInline(p)}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {/* Phân nhóm 2: Biện pháp đề xuất cấp thiết */}
              {conservationData.proposed.length > 0 && (
                <div className="conservation-subgroup conservation-subgroup--proposed">
                  <div className="conservation-subgroup__header">
                    <Lightbulb size={15} className="conservation-subgroup__icon" />
                    <span className="conservation-subgroup__title">Đề xuất cấp thiết</span>
                  </div>
                  <div className="conservation-subgroup__content">
                    {conservationData.proposed.map((p, idx) => (
                      <p key={idx} className="conservation-card__text">
                        {renderFormattedInline(p)}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
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

'use client'

import React, { useEffect, useState } from 'react'
import { 
  Sparkles, 
  Compass, 
  Egg, 
  Ruler, 
  BookOpen, 
  Globe, 
  ChevronDown, 
  AlertTriangle 
} from 'lucide-react'

interface Props {
  labelEn: string
  labelVn: string
  text: string
  cacheKey: string
  textVn?: string | null
}

async function translateToVi(text: string): Promise<string> {
  if (text.length > 2000) {
    const chunks: string[] = []
    for (let i = 0; i < text.length; i += 1800) chunks.push(text.slice(i, i + 1800))
    const results = await Promise.all(chunks.map(c => translateToVi(c)))
    return results.join(' ')
  }
  const res = await fetch('/api/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
  if (!res.ok) throw new Error('translate fail')
  const json = await res.json()
  return json.text
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
 * Tự động ngắt đoạn thông minh:
 * - Ưu tiên dấu ngắt dòng có sẵn (\n\n hoặc \n)
 * - Nếu là khối văn bản liền đặc (> 250 ký tự), phân tách câu hợp lý tránh ngắt nhầm (Ref. xxxx)
 * - Gom mỗi 2-3 câu thành một đoạn văn thoáng đãng
 */
function splitIntoParagraphs(text: string): string[] {
  if (!text) return []
  const trimmed = text.trim()

  // 1. Nếu văn bản đã có dấu ngắt dòng
  if (trimmed.includes('\n')) {
    return trimmed
      .split(/\n+/)
      .map(p => p.trim())
      .filter(Boolean)
  }

  // 2. Nếu văn bản ngắn (<= 250 ký tự), giữ nguyên 1 đoạn
  if (trimmed.length <= 250) {
    return [trimmed]
  }

  // 3. Tách câu thông minh: bảo vệ các từ viết tắt có dấu chấm như Ref., Refs., sp., spp., et al.
  const protectedText = trimmed.replace(
    /\b(Refs?|sp|spp|et al|e\.g|i\.e)\.\s*/gi,
    (m, word) => `${word}_DOT_ `
  )

  // Ngắt câu tại dấu chấm/chấm than/chấm hỏi theo sau bởi khoảng trắng và ký tự viết hoa
  const rawSentences = protectedText
    .split(/(?<=[.!?])\s+(?=[A-ZÀ-Ỹ0-9])/)
    .map(s => s.replace(/_DOT_/g, '.').trim())
    .filter(Boolean)

  if (rawSentences.length <= 3) {
    return [trimmed]
  }

  const paragraphs: string[] = []
  let currentChunk: string[] = []
  let currentLen = 0

  for (const sentence of rawSentences) {
    currentChunk.push(sentence)
    currentLen += sentence.length

    // Khi đã có từ 2 câu và dài trên 220 ký tự, hoặc đã đủ 3 câu -> tạo đoạn mới
    if ((currentChunk.length >= 2 && currentLen >= 220) || currentChunk.length >= 3) {
      paragraphs.push(currentChunk.join(' '))
      currentChunk = []
      currentLen = 0
    }
  }

  if (currentChunk.length > 0) {
    if (paragraphs.length > 0 && currentChunk.length === 1 && currentLen < 150) {
      paragraphs[paragraphs.length - 1] += ' ' + currentChunk.join(' ')
    } else {
      paragraphs.push(currentChunk.join(' '))
    }
  }

  return paragraphs.length > 0 ? paragraphs : [trimmed]
}

/**
 * Component hiển thị đoạn văn bản có format thẻ in nghiêng và ngắt đoạn
 */
function FormattedParagraphs({ content, isEn = false }: { content: string; isEn?: boolean }) {
  const paras = splitIntoParagraphs(content)

  return (
    <div className={`bio-note-card__paragraphs ${isEn ? 'bio-note-card__paragraphs--en' : ''}`}>
      {paras.map((p, idx) => (
        <p
          key={idx}
          className={`bio-note-card__text ${isEn ? 'bio-note-card__text--en' : ''}`}
        >
          {renderFormattedInline(p)}
        </p>
      ))}
    </div>
  )
}

/**
 * Tách tiêu đề sạch và phát hiện nguồn dữ liệu
 */
function extractTitleAndSource(rawVn: string, rawEn: string): {
  titleVn: string
  titleEn: string
  source: string
  iconType: 'summary' | 'ecology' | 'reproduction' | 'morphology' | 'default'
} {
  // Trích xuất nguồn (nếu có trong ngoặc đơn)
  const sourceMatch = rawEn.match(/\((FishBase.*?|AlgaeBase|GBIF|SeaLifeBase.*?)\)/i) ||
                      rawVn.match(/\((FishBase.*?|AlgaeBase|GBIF|SeaLifeBase.*?)\)/i)
  const source = sourceMatch ? sourceMatch[1].trim() : 'FishBase / GBIF'

  // Làm sạch tiêu đề tiếng Việt và tiếng Anh (loại bỏ tên nguồn trong ngoặc)
  const titleVn = rawVn.replace(/\s*\((FishBase.*?|AlgaeBase|GBIF|SeaLifeBase.*?)\)/i, '').trim()
  const titleEn = rawEn.replace(/\s*\((FishBase.*?|AlgaeBase|GBIF|SeaLifeBase.*?)\)/i, '').trim()

  // Phân loại Icon & Theme màu sắc
  const lower = (rawEn + ' ' + rawVn).toLowerCase()
  let iconType: 'summary' | 'ecology' | 'reproduction' | 'morphology' | 'default' = 'default'

  if (lower.includes('summary') || lower.includes('tóm tắt')) {
    iconType = 'summary'
  } else if (lower.includes('ecology') || lower.includes('sinh thái')) {
    iconType = 'ecology'
  } else if (lower.includes('repro') || lower.includes('sinh sản')) {
    iconType = 'reproduction'
  } else if (lower.includes('morph') || lower.includes('hình thái')) {
    iconType = 'morphology'
  }

  return { titleVn, titleEn, source, iconType }
}

export default function BilingualNoteBlock({ labelEn, labelVn, text, cacheKey, textVn }: Props) {
  const [runtimeVnText, setRuntimeVnText] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)

  // Phân tích tiêu đề & nguồn
  const { titleVn, titleEn, source, iconType } = extractTitleAndSource(labelVn, labelEn)

  // Icon và Style theo loại chuyên đề
  let IconComponent = BookOpen
  let iconClass = 'bio-note-card__icon--default'

  if (iconType === 'summary') {
    IconComponent = Sparkles
    iconClass = 'bio-note-card__icon--cyan'
  } else if (iconType === 'ecology') {
    IconComponent = Compass
    iconClass = 'bio-note-card__icon--blue'
  } else if (iconType === 'reproduction') {
    IconComponent = Egg
    iconClass = 'bio-note-card__icon--amber'
  } else if (iconType === 'morphology') {
    IconComponent = Ruler
    iconClass = 'bio-note-card__icon--purple'
  }

  // Nếu đã có sẵn bản dịch chuẩn từ CSDL
  const hasPrecomputedVn = Boolean(textVn && textVn.trim())

  useEffect(() => {
    if (hasPrecomputedVn) return
    const cached = sessionStorage.getItem(cacheKey)
    if (cached) { setRuntimeVnText(cached); return }
    setLoading(true)
    translateToVi(text)
      .then(vn => { sessionStorage.setItem(cacheKey, vn); setRuntimeVnText(vn) })
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [text, cacheKey, hasPrecomputedVn])

  return (
    <article className="bio-note-card" aria-label={titleVn}>
      {/* ─── Card Header ─── */}
      <header className="bio-note-card__header">
        <div className="bio-note-card__title-group">
          <span className={`bio-note-card__icon ${iconClass}`}>
            <IconComponent size={16} aria-hidden="true" />
          </span>
          <div className="bio-note-card__heading">
            <h5 className="bio-note-card__title">{titleVn}</h5>
            <span className="bio-note-card__en-label">({titleEn})</span>
          </div>
        </div>

        <span className="bio-note-card__source-pill">
          {source}
        </span>
      </header>

      {/* ─── Card Body: Bản dịch tiếng Việt ─── */}
      <div className="bio-note-card__body">
        {hasPrecomputedVn ? (
          <FormattedParagraphs content={textVn!} />
        ) : (
          <div className="bio-note-card__runtime">
            {loading && <span className="bio-notes-loading">Đang tải bản dịch đối chiếu...</span>}
            {error && <span className="bio-notes-error">Không thể tải bản dịch tự động.</span>}
            {runtimeVnText && (
              <>
                <FormattedParagraphs content={runtimeVnText} />
                <p className="bio-notes-disclaimer">
                  <AlertTriangle size={13} /> Bản dịch từ AI, chỉ có tính chất tham khảo học thuật.
                </p>
              </>
            )}
          </div>
        )}
      </div>

      {/* ─── Collapsible Panel: Văn bản gốc Tiếng Anh đối chiếu ─── */}
      <details className="bio-note-card__en-details">
        <summary className="bio-note-card__en-summary">
          <Globe size={13} className="bio-note-card__globe-icon" />
          <span>Xem văn bản gốc tiếng Anh ({source})</span>
          <ChevronDown size={14} className="bio-note-card__chevron" />
        </summary>
        <div className="bio-note-card__en-content">
          <FormattedParagraphs content={text} isEn />
        </div>
      </details>
    </article>
  )
}

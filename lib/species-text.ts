/**
 * lib/species-text.ts
 * Quản lý dữ liệu văn bản tab Thông số (Thông tin chung).
 *
 * NGUYÊN TẮC BẢO TỒN DI SẢN SÁCH GỐC OCR:
 * 1. Tab Thông số là không gian tôn vinh tư liệu nghiên cứu từ sách gốc OCR Việt Nam.
 * 2. Đặc điểm hình thái: Ưu tiên tuyệt đối OCR tiếng Việt (sp.morphology_vn).
 *    Nếu OCR chưa có thì dùng bio.morphDescriptionVn để bổ trợ nhận dạng.
 * 3. Sinh thái & Dinh dưỡng: CHỈ lấy từ sách gốc OCR (sp.ecology_vn).
 *    KHÔNG đưa bản dịch/thông số FishBase/GBIF vào đây vì đã có tab Sinh học đảm nhiệm.
 * 4. Giá trị sử dụng & Kinh tế: CHỈ lấy từ sách gốc OCR (sp.economic_value_vn).
 *    Nếu sách gốc không ghi nhận thì để trống, không nhồi nhét thông số FishBase.
 */

import { BiologyData } from '@/components/species/BiologyDashboard'

export interface SpeciesTextSource {
  morphology_vn?: string | null
  morphology_en?: string | null
  ecology_vn?: string | null
  ecology_en?: string | null
  economic_value_vn?: string | null
  economic_value_en?: string | null
  biology?: BiologyData | string | null
  collection_id?: string | null
}

/**
 * 1. Lấy mô tả hình thái học:
 * Ưu tiên trích xuất từ sách gốc OCR (sp.morphology_vn).
 * Nếu chưa có, sử dụng mô tả hình thái tiếng Việt bio.morphDescriptionVn.
 */
export function getResolvedMorphologyVn(sp: SpeciesTextSource, bio?: BiologyData | null): string {
  if (sp.morphology_vn && sp.morphology_vn.trim()) {
    return sp.morphology_vn.trim()
  }

  if (bio?.morphDescriptionVn && bio.morphDescriptionVn.trim()) {
    return bio.morphDescriptionVn.trim()
  }

  return ''
}

/**
 * 2. Lấy sinh thái & dinh dưỡng:
 * CHỈ lấy dữ liệu trích xuất từ sách gốc OCR (sp.ecology_vn).
 * Không lấy bản dịch FishBase/GBIF để bảo toàn giá trị tư liệu gốc.
 */
export function getResolvedEcologyVn(sp: SpeciesTextSource): string {
  if (sp.ecology_vn && sp.ecology_vn.trim()) {
    return sp.ecology_vn.trim()
  }

  return ''
}

/**
 * 3. Lấy giá trị sử dụng & kinh tế:
 * CHỈ lấy dữ liệu trích xuất từ sách gốc OCR (sp.economic_value_vn).
 * Nếu sách gốc không ghi nhận thì để trống, không nhồi nhét thông số FishBase.
 */
export function getResolvedEconomicValueVn(sp: SpeciesTextSource): string {
  if (sp.economic_value_vn && sp.economic_value_vn.trim()) {
    return sp.economic_value_vn.trim()
  }

  return ''
}

/**
 * Viết hoa chữ cái đầu tiên của chuỗi
 */
export function capitalizeFirst(str: string): string {
  if (!str) return str
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * Tự động ngắt đoạn văn thông minh cho nội dung khoa học, hình thái, sinh thái & bảo tồn:
 * - Ưu tiên dấu ngắt dòng có sẵn (\n)
 * - Tách câu tại dấu chấm/chấm than/hỏi, bảo vệ các từ viết tắt học thuật (NĐ-CP, Ref., sp., et al., GS., TS.)
 * - Tách các câu dài (> 200 ký tự) có dấu chấm phẩy (; ) thành các câu riêng biệt
 * - Nhóm các câu thành các đoạn văn ngắn 1-2 câu (140 - 200 ký tự) thoáng đãng, dễ đọc
 */
export function splitIntoParagraphs(text: string): string[] {
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

  // 2. Nếu văn bản ngắn (dưới 150 ký tự), giữ nguyên 1 đoạn
  if (trimmed.length <= 150) {
    return [trimmed]
  }

  // 3. Tách câu thông minh có bảo vệ từ viết tắt
  const protectedText = trimmed.replace(
    /\b(Refs?|sp|spp|et al|e\.g|i\.e|NĐ-CP|GS|TS|ThS)\.\s*/gi,
    (m, word) => `${word}_DOT_ `
  )

  const rawSentences = protectedText
    .split(/(?<=[.!?])\s+(?=[\p{Lu}0-9])/u)
    .map(s => s.replace(/_DOT_/g, '.').trim())
    .filter(Boolean)

  // 4. Xử lý các câu quá dài (> 200 ký tự) có dấu chấm phẩy (; ) để ngắt ý
  const sentences: string[] = []
  for (const s of rawSentences) {
    if (s.length > 200 && s.includes('; ')) {
      const parts = s.split(/;\s+/)
      for (let idx = 0; idx < parts.length; idx++) {
        let p = parts[idx].trim()
        if (!p) continue
        if (idx === parts.length - 1) {
          if (!p.endsWith('.')) p += '.'
        } else {
          p = p.replace(/;$/, '') + '.'
        }
        sentences.push(capitalizeFirst(p))
      }
    } else {
      sentences.push(s)
    }
  }

  if (sentences.length <= 1) {
    return [trimmed]
  }

  const paragraphs: string[] = []
  let currentChunk: string[] = []
  let currentLen = 0

  for (const s of sentences) {
    // Nếu trong chunk chỉ có 1 câu dẫn rất ngắn (< 60 ký tự), gom câu tiếp theo vào cùng đoạn
    if (currentChunk.length === 1 && currentLen < 60) {
      currentChunk.push(s)
      currentLen += s.length
      paragraphs.push(currentChunk.join(' '))
      currentChunk = []
      currentLen = 0
      continue
    }

    // Nếu bản thân câu đã dài (>= 170 ký tự), tách thành đoạn độc lập
    if (s.length >= 170) {
      if (currentChunk.length > 0) {
        paragraphs.push(currentChunk.join(' '))
        currentChunk = []
        currentLen = 0
      }
      paragraphs.push(s)
      continue
    }

    currentChunk.push(s)
    currentLen += s.length

    // Khi gom đủ 2 câu hoặc tổng độ dài >= 140 ký tự -> ngắt đoạn mới
    if (currentChunk.length >= 2 || currentLen >= 140) {
      paragraphs.push(currentChunk.join(' '))
      currentChunk = []
      currentLen = 0
    }
  }

  if (currentChunk.length > 0) {
    if (paragraphs.length > 0 && paragraphs[paragraphs.length - 1].length < 100 && (paragraphs[paragraphs.length - 1].length + currentLen <= 220)) {
      paragraphs[paragraphs.length - 1] += ' ' + currentChunk.join(' ')
    } else {
      paragraphs.push(currentChunk.join(' '))
    }
  }

  return paragraphs
}

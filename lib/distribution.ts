/**
 * lib/distribution.ts
 * Utility module for parsing, splitting, and formatting species geographical distribution strings.
 * Ensures 100% data compatibility with Supabase column vn_distribution / en_distribution (text <= 2000 chars)
 * and strictly adheres to lib/schemas.ts (Zod speciesUpdateSchema & speciesCreateSchema).
 */

export interface DistributionParts {
  world: string
  vn: string
}

export interface ParsedDistribution {
  world: string[]
  vn: string[]
  fallback: string | null
}

const WORLD_KEYWORDS = /(thái[\s\-]bình[\s\-]dương|ấn[\s\-]độ[\s\-]dương|đại[\s\-]tây[\s\-]dương|biển[\s\-]đỏ|hồng[\s\-]hải|indonesia|philippines|nhật[\s\-]bản|trung[\s\-]quốc|australia|triều[\s\-]tiên|đông[\s\-]phi|madagascar|srilanca|sri[\s\-]lanka|malaysia|polynesia|melanesia|fiji|new[\s\-]guinea|hawaii|đài[\s\-]loan|thế[\s\-]giới|quốc[\s\-]tế)/i

const VN_KEYWORDS = /(việt[\s\-]nam|vịnh[\s\-]bắc[\s\-]bộ|bắc[\s\-]bộ|trung[\s\-]bộ|nam[\s\-]bộ|đông[\s\-]nam[\s\-]bộ|tây[\s\-]nam|phú[\s\-]quốc|hoàng[\s\-]sa|trường[\s\-]sa|nha[\s\-]trang|khánh[\s\-]hòa|bình[\s\-]thuận|ninh[\s\-]thuận|quảng[\s\-]ninh|hải[\s\-]phòng|đà[\s\-]nẵng|côn[\s\-]đảo|vũng[\s\-]tàu|rạn[\s\-]san[\s\-]hô|ven[\s\-]bờ|duyên[\s\-]hải|vùng[\s\-]biển)/i

export const REGION_MAP = [
  { key: 'bac-bo', name: 'Vịnh Bắc Bộ', regex: /vịnh bắc bộ|bắc bộ|hải phòng|quảng ninh/i },
  { key: 'trung-bo', name: 'Vùng Biển Miền Trung', regex: /trung bộ|miền trung|đà nẵng|huế|quảng trị|quảng nam|quảng ngãi|bình định|phú yên|khánh hòa|nha trang|ninh thuận|bình thuận/i },
  { key: 'nam-bo', name: 'Vùng Biển Nam Bộ', regex: /nam bộ|đông nam bộ|vũng tàu|bà rịa|côn đảo/i },
  { key: 'tay-nam-bo', name: 'Vùng Biển Tây Nam (Phú Quốc)', regex: /tây nam|phú quốc|kiên giang|vịnh thái lan/i },
  { key: 'hoang-sa', name: 'Quần đảo Hoàng Sa', regex: /hoàng sa/i },
  { key: 'truong-sa', name: 'Quần đảo Trường Sa', regex: /trường sa/i },
]

/**
 * Tách chuỗi phân bố gộp trong CSDL thành 2 phần: Thế giới và Việt Nam
 */
export function splitDistribution(raw?: string | null): DistributionParts {
  if (!raw || typeof raw !== 'string') return { world: '', vn: '' }
  const text = raw.trim()
  if (!text) return { world: '', vn: '' }

  // 1. Nhận diện nhãn rõ ràng: 'Thế giới:' và 'Việt Nam:'
  const hasTgLabel = /thế giới\s*[:\.]/i.test(text)
  const hasVnLabel = /việt nam\s*[:\.]/i.test(text)

  if (hasTgLabel && hasVnLabel) {
    if (text.search(/thế giới\s*[:\.]/i) < text.search(/việt nam\s*[:\.]/i)) {
      const match = text.match(/thế giới\s*[:\.]\s*(.*?)(?:[\.;\n]\s*việt nam\s*[:\.]\s*|\bviệt nam\s*[:\.]\s*)(.+)/i)
      if (match) return { world: match[1].trim(), vn: match[2].trim() }
    } else {
      const match = text.match(/việt nam\s*[:\.]\s*(.*?)(?:[\.;\n]\s*thế giới\s*[:\.]\s*|\bthế giới\s*[:\.]\s*)(.+)/i)
      if (match) return { vn: match[1].trim(), world: match[2].trim() }
    }
  }

  if (hasTgLabel && !hasVnLabel) {
    const match = text.match(/thế giới\s*[:\.]\s*(.*)/i)
    return { world: match ? match[1].trim() : text, vn: '' }
  }

  if (hasVnLabel && !hasTgLabel) {
    const matchWithPreWorld = text.match(/^(.*?)(?:,\s*việt nam|\bviệt nam)\s*[:\.]\s*(.+)/i)
    if (matchWithPreWorld && matchWithPreWorld[1].trim().length > 0) {
      return { world: matchWithPreWorld[1].trim().replace(/,\s*$/, ''), vn: matchWithPreWorld[2].trim() }
    }
    const matchOnlyVn = text.match(/việt nam\s*[:\.]\s*(.*)/i)
    return { world: '', vn: matchOnlyVn ? matchOnlyVn[1].trim() : text }
  }

  // 2. Định dạng sách kinh điển: 'Triều Tiên, Nhật Bản, Trung Quốc, Việt Nam. Vịnh Bắc Bộ, Trung Bộ.'
  const vnMatch = text.match(/^(.*?)(?:,\s*Việt Nam|\bViệt Nam)\s*\.\s*(.{2,})/i)
  if (vnMatch && vnMatch[1].trim().length > 0) {
    return { world: vnMatch[1].trim().replace(/,\s*$/, ''), vn: vnMatch[2].trim() }
  }

  // 3. Phân tách bằng dấu chấm có chứa từ khóa
  const dotParts = text.split(/\.\s+/)
  if (dotParts.length >= 2) {
    const p1 = dotParts[0].trim()
    const p2 = dotParts.slice(1).join('. ').trim()

    if (WORLD_KEYWORDS.test(p1) && VN_KEYWORDS.test(p2)) {
      return { world: p1, vn: p2 }
    }
    if (VN_KEYWORDS.test(p1) && WORLD_KEYWORDS.test(p2)) {
      return { vn: p1, world: p2 }
    }
  }

  // 4. Nếu chỉ thuần Việt Nam hoặc thuần Thế giới
  if (!WORLD_KEYWORDS.test(text) && VN_KEYWORDS.test(text)) {
    return { world: '', vn: text }
  }

  if (WORLD_KEYWORDS.test(text) && !VN_KEYWORDS.test(text)) {
    return { world: text, vn: '' }
  }

  return { world: '', vn: text }
}

/**
 * Tổng hợp 2 phần (Thế giới & Việt Nam) thành chuỗi chuẩn hóa lưu vào CSDL (max 2000 ký tự)
 */
export function formatDistribution(world?: string | null, vn?: string | null): string {
  const w = (world || '').trim()
  const v = (vn || '').trim()

  if (w && v) {
    const wClean = w.replace(/^thế\s*giới\s*[:\.]\s*/i, '').trim()
    const vClean = v.replace(/^việt\s*nam\s*[:\.]\s*/i, '').trim()
    return `Thế giới: ${wClean}. Việt Nam: ${vClean}`
  }

  if (w) {
    const wClean = w.replace(/^thế\s*giới\s*[:\.]\s*/i, '').trim()
    return `Thế giới: ${wClean}`
  }

  if (v) {
    return v
  }

  return ''
}

/**
 * Phân tích chuỗi phân bố thành danh sách thẻ hiển thị cho giao diện SpeciesCard & Live Preview
 */
export function parseDistribution(raw?: string | null): ParsedDistribution {
  if (!raw || typeof raw !== 'string') return { vn: [], world: [], fallback: null }
  const text = raw.trim().replace(/\s+/g, ' ')
  if (!text) return { vn: [], world: [], fallback: null }

  const { world: worldRaw, vn: vnRaw } = splitDistribution(text)

  // 1. Phân tích các địa danh thế giới thành tags
  const worldItems = worldRaw
    ? worldRaw
        .split(/[,;:–—\/\.]|\bvà\b|\band\b/i)
        .map(s => s.trim().replace(/^[\-–—,\.;:\s]+|[\-–—,\.;:\s]+$/g, ''))
        .filter(s => s.length > 1 && !/^(nhiệt đới|á nhiệt đới|cận nhiệt đới|ven bờ|ven biển|vùng biển|khu vực|từ|đến|to|from)\b/i.test(s) && !/việt nam/i.test(s))
    : []

  const world = Array.from(new Set(worldItems))

  // 2. Phân tích các vùng biển Việt Nam
  const vn: string[] = []
  REGION_MAP.forEach(r => {
    if (r.regex.test(vnRaw) || (vnRaw.length === 0 && r.regex.test(text))) {
      vn.push(r.name)
    }
  })

  // Nếu có đề cập đến Việt Nam nhưng không rõ vùng biển cụ thể theo REGION_MAP
  if (vn.length === 0 && (vnRaw.length > 2 || /việt nam/i.test(text))) {
    vn.push('Vùng biển Việt Nam')
  }

  // Fallback nếu không bóc tách được tag nào
  const fallback = (world.length === 0 && vn.length === 0) ? text : null

  return { world, vn, fallback }
}

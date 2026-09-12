/**
 * lib/species-parsers.ts
 * Pure parsing functions for species text data.
 * Extracted from SpecimenCard.tsx to enable reuse and independent testing.
 */

/** Parse literature references from raw OCR text */
export function parseLiterature(lit?: string | null): string[] {
  if (!lit) return []
  const trimmed = lit.trim()

  // 1. Phân tách theo dấu chấm phẩy (;): Chuẩn trích dẫn học thuật quốc tế (Rắn biển, Giáp xác, Rong biển)
  // Gộp các ký tự ngắt dòng ngang (\n) do scan cột sách thành khoảng trắng trước khi split
  if (trimmed.includes(';')) {
    const singleLine = trimmed.replace(/\r?\n+/g, ' ').replace(/\s{2,}/g, ' ')
    return singleLine.split(/;\s*/).map(s => s.trim().replace(/\.$/, '')).filter(Boolean)
  }

  // 2. Phân tách theo số thứ tự (chỉ số thứ tự 1-2 chữ số "1. ... 2. ...", tránh nhầm năm 19xx.)
  const numSplit = trimmed.split(/(?=^\s*\d{1,2}\.\s+|\s+\d{1,2}\.\s+)/)
  if (numSplit.length > 1) {
    return numSplit.map(s => s.replace(/^\s*\d{1,2}\.\s*/, '').trim()).filter(Boolean)
  }

  // 3. Nếu có ký tự xuống dòng rõ ràng (không chứa ;)
  const lineSplit = trimmed.split(/\r?\n/).map(s => s.trim()).filter(Boolean)
  if (lineSplit.length > 1) return lineSplit

  // 4. Phân tách bằng dấu chấm sau năm 4 chữ số: "Tác giả A, 1962. Tác giả B, 1992." (Sách Cá biển cổ)
  // Chỉ phân tách nếu có từ 2 mốc năm 4 chữ số trở lên (đại diện cho nhiều trích dẫn khác nhau)
  const yearMatches = trimmed.match(/\b(?:18|19|20)\d{2}[a-z]?\b/g)
  if (yearMatches && yearMatches.length > 1) {
    const yearDotSplit = trimmed.split(/(?<=\b(?:18|19|20)\d{2}[a-z]?)\s*\.\s*(?=[A-ZÀ-ỸĐ])/i)
    if (yearDotSplit.length > 1) {
      return yearDotSplit.map(s => s.trim().replace(/\.$/, '')).filter(Boolean)
    }
  }

  return [trimmed]
}

/** Parse specimen locations from raw text */
export function parseLocations(str?: string | null): string[] {
  if (!str) return []
  const clean = str.trim()
  // Chỉ tách dòng nếu văn bản có ký tự xuống dòng rõ ràng
  if (clean.includes('\n')) {
    return clean.split(/\r?\n/).map(s => s.replace(/^[•\-\*]\s*/, '').trim()).filter(Boolean)
  }
  // Hoặc tách nếu dùng chấm phẩy ngăn cách danh sách các viện (không phải câu văn có dấu chấm kết thúc)
  if (clean.includes(';') && !clean.includes('. ') && clean.length < 120) {
    return clean.split(/;\s*/).map(s => s.trim()).filter(Boolean)
  }
  return [clean]
}

export interface StatusItem {
  label?: string
  text: string
}

/** Parse status text (field status, conservation, danger level) */
export function parseStatus(stat?: string | null): StatusItem[] {
  if (!stat) return []
  const clean = stat.trim()

  // Bóc tách nếu có cả "Tình trạng thực địa:" và/hoặc "Hiện trạng bảo tồn:"
  const fieldMatch = clean.match(/Tình trạng thực địa:\s*([^]*?)(?=\s*Hiện trạng bảo tồn:|$)/i)
  const consMatch = clean.match(/Hiện trạng bảo tồn:\s*([^]*)$/i)

  if (fieldMatch || consMatch) {
    const items: StatusItem[] = []
    if (fieldMatch && fieldMatch[1].trim()) {
      items.push({
        label: 'Tình trạng thực địa',
        text: fieldMatch[1].trim(),
      })
    }
    if (consMatch && consMatch[1].trim()) {
      items.push({
        label: 'Hiện trạng bảo tồn',
        text: consMatch[1].trim(),
      })
    }
    if (items.length > 0) return items
  }

  // Bóc tách nếu có "Mức độ nguy hiểm:"
  const dangerMatch = clean.match(/^Mức độ nguy hiểm:\s*([^]*)$/i)
  if (dangerMatch && dangerMatch[1].trim()) {
    return [{
      label: 'Mức độ nguy hiểm',
      text: dangerMatch[1].trim(),
    }]
  }

  // Nếu dữ liệu có xuống dòng sẵn
  if (clean.includes('\n')) {
    return clean
      .split(/\r?\n/)
      .map(s => s.trim())
      .filter(Boolean)
      .map(s => ({ text: s }))
  }

  return [{ text: clean }]
}

/** Format alternate names (handle JSON arrays and unicode escapes) */
export function formatAlternateNames(val?: string | null): string {
  if (!val) return ''
  const trimmed = val.trim()
  if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
    try {
      const arr = JSON.parse(trimmed)
      if (Array.isArray(arr)) {
        return arr.filter(Boolean).join(', ')
      }
    } catch {
      // ignore
    }
  }
  return trimmed.replace(/\\u([0-9a-fA-F]{4})/g, (_, c) => String.fromCharCode(parseInt(c, 16)))
}

/** Clean taxon hierarchy names — remove rank prefixes, normalize Latin case, strip OCR artifacts */
export function cleanTaxonHierarchy(rank: string, vnRaw?: string | null, latRaw?: string | null): { vn: string; lat: string } {
  let vn = (vnRaw || '').trim()
  let lat = (latRaw || '').trim()

  // 1. Bỏ tiền tố rank: Lớp, Bộ, Họ, Giống, Chi
  vn = vn.replace(new RegExp(`^(Lớp|Bộ|Họ|Giống|Chi)\\s*`, 'i'), '')
  // Bỏ số thứ tự (ví dụ "11: ", "12. ")
  vn = vn.replace(/^\d+[\s:\.\-]+/, '')

  // 2. Làm sạch Latin: bỏ tiền tố "Family ", "Order ", "Class "
  lat = lat.replace(/^(Class|Order|Family|Genus)\s+/i, '')

  // 3. Chuẩn hóa Latin cho Chi/Giống: nếu quá dài hoặc chứa trích dẫn sách, chỉ lấy danh pháp chi chính
  if (rank === 'Giống' || rank === 'Chi') {
    const genusWord = lat.split(/\s+/)[0]
    if (lat.length > 35 || lat.includes('Ann.') || lat.includes('Vol.') || lat.includes('pp.') || lat.includes('Type:')) {
      lat = genusWord
    }
  }

  // 4. Chuẩn hóa TitleCase cho Latin nếu bị ALL CAPS (CALLIONYMIDAE -> Callionymidae)
  if (/^[A-Z]{4,}$/.test(lat)) {
    lat = lat.charAt(0) + lat.slice(1).toLowerCase()
  }

  // 5. Tách tên Latin nếu bị dính đuôi vào tên tiếng Việt (ví dụ "Cá Nhám Râu Orectolobidae" -> "Cá Nhám Râu")
  if (lat) {
    const mainLatWord = lat.split(/\s+/)[0]
    if (mainLatWord && mainLatWord.length > 2) {
      const regex = new RegExp(`\\s*\\b${mainLatWord}\\b.*$`, 'i')
      if (regex.test(vn)) {
        const stripped = vn.replace(regex, '').trim()
        if (stripped) vn = stripped
      }
    }
  }

  // 6. Bỏ ngoặc đơn thừa
  vn = vn.replace(/^\((.*)\)$/, '$1').trim()
  lat = lat.replace(/^\((.*)\)$/, '$1').trim()

  return { vn: vn || lat, lat }
}

/** Format synonym text — italicize binomial names */
export function formatSynonym(text: string): string {
  if (text.includes('<span class="syn-name">')) return text.replace('<span class="syn-name">', '<i>').replace('</span>', '</i>')
  return text.replace(/^([A-Z][a-z\-]+(?: \([A-Z][a-z\-]+\))? [a-z\-]+)(.*)/, '<i>$1</i>$2')
}

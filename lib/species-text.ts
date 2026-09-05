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
 * Không lấy thông số FishBase/GBIF để bảo toàn giá trị tư liệu gốc.
 */
export function getResolvedEconomicValueVn(sp: SpeciesTextSource): string {
  if (sp.economic_value_vn && sp.economic_value_vn.trim()) {
    return sp.economic_value_vn.trim()
  }

  return ''
}

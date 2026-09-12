/**
 * Shared species query utilities.
 * Centralises business rules that every species list query must obey:
 *   - collection_id filter
 *   - soft-delete exclusion (deleted_at IS NULL)
 *   - search input sanitisation
 *
 * Previously split between:
 *   - app/api/species/route.ts  (sanitizeSearch, PAGE_SIZE)
 *   - components/browse/SpeciesGrid.tsx  (inline .eq/.is calls)
 */

export const SPECIES_PAGE_SIZE = 20

/**
 * Các cột SELECT chuẩn — thêm/xóa cột ở 1 chỗ duy nhất.
 * SPECIES_LIST_COLS: Dùng cho danh sách phân trang, bảng admin.
 * SPECIES_DETAIL_COLS: Toàn bộ thông tin chi tiết loài.
 *
 * ponytail: Full repository pattern (getById, getByCollection, etc.)
 * là over-engineering cho các câu query ngắn, mỗi nơi cần projection khác nhau.
 * Ceiling: Khi có >20 điểm query hoặc migration schema phức tạp mới cần Repository class.
 */
export const SPECIES_LIST_COLS =
  'id, volume, species_index, vn_name, scientific_name, tax_family_latin, collection_id'

export const SPECIES_DETAIL_COLS = '*'

/** Strip chars that could break PostgREST text filters */
export function sanitizeSearch(raw: string): string {
  return raw.replace(/[%_(),.]/g, '').trim().slice(0, 100)
}

/**
 * Apply standard base filters to a Supabase species query builder.
 * Always enforces: collection_id + soft-delete exclusion (unless opted out).
 *
 * Usage:
 *   const q = applySpeciesFilters(
 *     db.from('species').select('...'),
 *     'ca-bien'
 *   )
 *   // then chain vol/search/pagination on q
 */
// ponytail: `any` is intentional — both browser and server Supabase clients
// share the same filter chain API but differ in generic type params.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function applySpeciesFilters(query: any, collection: string, includeDeleted = false) {
  let q = query.eq('collection_id', collection)
  if (!includeDeleted) q = q.is('deleted_at', null)
  return q
}

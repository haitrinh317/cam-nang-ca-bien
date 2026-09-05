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

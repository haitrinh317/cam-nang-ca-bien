/**
 * search.ts — typed wrapper over RPC search_species / search_species_counts (migration 012).
 * Client-safe: takes the Supabase client as an argument (browser or server).
 */
import type { SupabaseClient } from '@supabase/supabase-js'

export type SearchMatch = 'vn' | 'alt' | 'en' | 'sci' | 'mix'

export interface SearchHit {
  id: string
  volume: number
  vn_name: string
  scientific_name: string
  authorship: string | null
  collection_id: string
  vn_alternate_names: string | null
  en_common_name: string | null
  matched: SearchMatch
  score: number
  total: number
}

export interface SearchCount {
  collection_id: string
  total: number
}

export const MATCH_HINT: Partial<Record<SearchMatch, string>> = {
  alt: 'khớp tên gọi khác',
  en: 'khớp tên tiếng Anh',
  sci: 'khớp tên khoa học',
}

export async function searchSpecies(
  client: SupabaseClient,
  q: string,
  opts: { collection?: string | null; limit?: number; offset?: number } = {},
): Promise<SearchHit[]> {
  const { data, error } = await client.rpc('search_species', {
    p_query: q,
    p_collection: opts.collection || null,
    p_limit: opts.limit ?? 12,
    p_offset: opts.offset ?? 0,
  })
  if (error) throw error
  return (data ?? []) as SearchHit[]
}

export async function searchCounts(client: SupabaseClient, q: string): Promise<SearchCount[]> {
  const { data, error } = await client.rpc('search_species_counts', { p_query: q })
  if (error) throw error
  return (data ?? []) as SearchCount[]
}

export function speciesHref(hit: Pick<SearchHit, 'collection_id' | 'id'>) {
  return `/${hit.collection_id || 'ca-bien'}/${hit.id}`
}

export function resultsHref(q: string, collection?: string | null) {
  const p = new URLSearchParams({ q })
  if (collection) p.set('c', collection)
  return `/tim-kiem?${p.toString()}`
}

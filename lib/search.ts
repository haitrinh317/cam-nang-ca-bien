/**
 * search.ts — typed wrapper over RPC search_species / search_species_counts (migration 012).
 * Client-safe: takes the Supabase client as an argument (browser or server).
 */
import type { SupabaseClient } from '@supabase/supabase-js'

export type SearchMatch = 'vn' | 'alt' | 'en' | 'sci' | 'mix' | 'none'

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

export interface SearchFilters {
  iucn: string[]
  habitat: string[]
  region: string[]
  dmin?: number
  dmax?: number
  lmin?: number
  lmax?: number
}

export const IUCN_ORDER = ['CR', 'EN', 'VU', 'NT', 'LC', 'DD', 'EW', 'EX', 'NE'] as const
export const IUCN_LABEL: Record<string, string> = {
  CR: 'Cực kỳ nguy cấp (CR)', EN: 'Nguy cấp (EN)', VU: 'Sắp nguy cấp (VU)', NT: 'Gần bị đe dọa (NT)',
  LC: 'Ít quan tâm (LC)', DD: 'Thiếu dữ liệu (DD)', EW: 'Tuyệt chủng ngoài tự nhiên (EW)',
  EX: 'Tuyệt chủng (EX)', NE: 'Chưa đánh giá (NE)',
}

export const HABITAT_LABEL: Record<string, string> = {
  'ran-san-ho': 'Rạn san hô',
  'day-cat-bun': 'Đáy cát / bùn',
  'day-da': 'Đáy đá',
  'tham-co-bien': 'Thảm cỏ biển / rong',
  'ngap-man-cua-song': 'Rừng ngập mặn / cửa sông',
  'bien-khoi': 'Biển khơi / tầng nước mặt',
  'bien-sau': 'Biển sâu',
}
export const REGION_LABEL: Record<string, string> = {
  'bac-bo': 'Bắc Bộ',
  'trung-bo': 'Trung Bộ',
  'nam-bo': 'Nam Bộ',
  'hoang-sa': 'Hoàng Sa',
  'truong-sa': 'Trường Sa',
}

const toNum = (v?: string) => {
  const n = v === undefined || v.trim() === '' ? NaN : Number(v.replace(',', '.'))
  return Number.isFinite(n) && n >= 0 ? n : undefined
}

/** Parse bộ lọc từ searchParams (iucn=CR,EN&dmin=0&dmax=30&lmin=&lmax=). Giá trị lạ bị bỏ, không lỗi. */
export function parseFilters(sp: Record<string, string | string[] | undefined>): SearchFilters {
  const one = (v?: string | string[]) => (Array.isArray(v) ? v[0] : v)
  // checkbox form gửi iucn lặp (mảng); link dùng dạng CR,EN — nhận cả hai
  const list = (v: string | string[] | undefined, ok: (x: string) => boolean, up = false) =>
    [v].flat().join(',').split(',').map(x => (up ? x.trim().toUpperCase() : x.trim())).filter(ok)
  const iucn = list(sp.iucn, x => (IUCN_ORDER as readonly string[]).includes(x), true)
  const habitat = list(sp.habitat, x => x in HABITAT_LABEL)
  const region = list(sp.region, x => x in REGION_LABEL)
  return { iucn, habitat, region, dmin: toNum(one(sp.dmin)), dmax: toNum(one(sp.dmax)), lmin: toNum(one(sp.lmin)), lmax: toNum(one(sp.lmax)) }
}

export const NO_FILTERS: SearchFilters = { iucn: [], habitat: [], region: [] }

export const hasFilters = (f: SearchFilters) =>
  f.iucn.length > 0 || f.habitat.length > 0 || f.region.length > 0 || [f.dmin, f.dmax, f.lmin, f.lmax].some(v => v !== undefined)

const rpcFilters = (f: SearchFilters) => ({
  p_iucn: f.iucn.length ? f.iucn : null,
  p_habitat: f.habitat.length ? f.habitat : null,
  p_region: f.region.length ? f.region : null,
  p_depth_min: f.dmin ?? null, p_depth_max: f.dmax ?? null,
  p_len_min: f.lmin ?? null, p_len_max: f.lmax ?? null,
})

export async function searchSpecies(
  client: SupabaseClient,
  q: string,
  opts: { collection?: string | null; filters?: SearchFilters; limit?: number; offset?: number } = {},
): Promise<SearchHit[]> {
  const { data, error } = await client.rpc('search_species', {
    p_query: q || null,
    p_collection: opts.collection || null,
    ...rpcFilters(opts.filters ?? NO_FILTERS),
    p_limit: opts.limit ?? 12,
    p_offset: opts.offset ?? 0,
  })
  if (error) throw error
  return (data ?? []) as SearchHit[]
}

/** Đếm theo phân hệ — áp mọi bộ lọc trừ phân hệ. */
export async function searchCounts(client: SupabaseClient, q: string, filters: SearchFilters = NO_FILTERS): Promise<SearchCount[]> {
  const { data, error } = await client.rpc('search_species_counts', { p_query: q || null, ...rpcFilters(filters) })
  if (error) throw error
  return (data ?? []) as SearchCount[]
}

export interface Facets {
  iucn: Map<string, number>
  habitat: Map<string, number>
  region: Map<string, number>
  /** Số loài chưa có mã IUCN (value NULL) trong tập đang xét */
  iucnMissing: number
}

/** Đếm cho 3 nhóm lọc (mỗi nhóm áp mọi bộ lọc KHÁC, trừ chính nó) trong một lần gọi RPC. */
export async function searchFacets(
  client: SupabaseClient, q: string, collection: string | null, filters: SearchFilters = NO_FILTERS,
): Promise<Facets> {
  const { data, error } = await client.rpc('search_species_facets', { p_query: q || null, p_collection: collection || null, ...rpcFilters(filters) })
  if (error) throw error
  const out: Facets = { iucn: new Map(), habitat: new Map(), region: new Map(), iucnMissing: 0 }
  for (const r of (data ?? []) as { facet: 'iucn' | 'habitat' | 'region'; value: string | null; total: number }[]) {
    if (r.value === null) out.iucnMissing += Number(r.total)
    else out[r.facet].set(r.value, Number(r.total))
  }
  return out
}

export function speciesHref(hit: Pick<SearchHit, 'collection_id' | 'id'>) {
  return `/${hit.collection_id || 'ca-bien'}/${hit.id}`
}

export function resultsHref(q: string, collection?: string | null, filters?: SearchFilters, page = 1) {
  const p = new URLSearchParams()
  if (q) p.set('q', q)
  if (collection) p.set('c', collection)
  if (filters?.iucn.length) p.set('iucn', filters.iucn.join(','))
  if (filters?.habitat.length) p.set('habitat', filters.habitat.join(','))
  if (filters?.region.length) p.set('region', filters.region.join(','))
  for (const k of ['dmin', 'dmax', 'lmin', 'lmax'] as const) if (filters?.[k] !== undefined) p.set(k, String(filters[k]))
  if (page > 1) p.set('page', String(page))
  const qs = p.toString()
  return qs ? `/tim-kiem?${qs}` : '/tim-kiem'
}

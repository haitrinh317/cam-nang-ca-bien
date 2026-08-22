/**
 * collections.ts — Collection registry (server-side)
 * Re-exports static data + adds Supabase fetcher for server components.
 */
import { createServerClient } from '@/lib/supabase-server'
import type { Collection } from '@/lib/collections-static'

// Re-export everything from static module
export type { Collection }
export { STATIC_COLLECTIONS, getCollectionBySlug, getAllCollections, getActiveCollections } from '@/lib/collections-static'

function mapRow(row: Record<string, unknown>): Collection {
  return {
    id: row.id as string,
    slug: row.slug as string,
    nameVn: row.name_vn as string,
    nameEn: row.name_en as string,
    icon: (row.icon as string) || '🌊',
    accentColor: (row.accent_color as string) || '#6fffe8',
    volumeCount: (row.volume_count as number) || 0,
    status: (row.status as 'active' | 'draft' | 'archived') || 'active',
    sortOrder: (row.sort_order as number) || 0,
  }
}

/** Server-side: fetch from DB with static fallback */
export async function getCollections(): Promise<Collection[]> {
  const { STATIC_COLLECTIONS } = await import('@/lib/collections-static')
  try {
    const db = createServerClient()
    const { data, error } = await db
      .from('collections')
      .select('*')
      .order('sort_order')
    if (error || !data?.length) return STATIC_COLLECTIONS
    return data.map(mapRow)
  } catch {
    return STATIC_COLLECTIONS
  }
}

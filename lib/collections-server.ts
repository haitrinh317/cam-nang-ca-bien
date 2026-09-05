/**
 * collections-server.ts — Server-only collection fetcher.
 * Imports supabase-server (uses next/headers) — DO NOT import in 'use client' files.
 *
 * For static collection data in client components, use lib/collections.ts.
 */
import { createServerClient } from '@/lib/supabase-server'
import { STATIC_COLLECTIONS, Collection } from '@/lib/collections'

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

/** Server-side: fetch live from DB with static fallback */
export async function getCollections(): Promise<Collection[]> {
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

/**
 * collections.ts — Collection registry
 * Phase M2: Fetches from Supabase `collections` table with static fallback.
 */
import { createServerClient } from '@/lib/supabase-server'

export interface Collection {
  id: string
  slug: string
  nameVn: string
  nameEn: string
  icon: string
  accentColor: string
  volumeCount: number
  status: 'active' | 'draft' | 'archived'
  sortOrder: number
}

// Static fallback — used if DB isn't set up yet (Phase M0-M1)
const STATIC_COLLECTIONS: Collection[] = [
  {
    id: 'ca-bien', slug: 'ca-bien',
    nameVn: 'Cá biển Việt Nam', nameEn: 'Vietnamese Marine Fish',
    icon: '🐟', accentColor: '#6fffe8', volumeCount: 5,
    status: 'active', sortOrder: 1,
  },
  {
    id: 'thuc-vat-bien', slug: 'thuc-vat-bien',
    nameVn: 'Thực vật biển Việt Nam', nameEn: 'Vietnamese Marine Plants',
    icon: '🌿', accentColor: '#a7f3d0', volumeCount: 0,
    status: 'draft', sortOrder: 2,
  },
]

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

/** Sync helper for server components that can't await at module level */
export function getCollectionBySlug(slug: string): Collection | undefined {
  return STATIC_COLLECTIONS.find(c => c.slug === slug)
}

export function getAllCollections(): Collection[] {
  return STATIC_COLLECTIONS
}

export function getActiveCollections(): Collection[] {
  return STATIC_COLLECTIONS.filter(c => c.status === 'active')
}

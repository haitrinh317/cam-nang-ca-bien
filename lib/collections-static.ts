/**
 * collections-static.ts — Static collection registry (client-safe)
 * No Supabase import — safe for 'use client' components.
 */

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

export const STATIC_COLLECTIONS: Collection[] = [
  {
    id: 'ca-bien', slug: 'ca-bien',
    nameVn: 'Cá biển Việt Nam', nameEn: 'Vietnamese Marine Fish',
    icon: '🐟', accentColor: '#6fffe8', volumeCount: 5,
    status: 'active', sortOrder: 1,
  },
  {
    id: 'thuc-vat-bien', slug: 'thuc-vat-bien',
    nameVn: 'Rong biển thường gặp ở Việt Nam', nameEn: 'Common Seaweeds of Vietnam',
    icon: '🌿', accentColor: '#a7f3d0', volumeCount: 1,
    status: 'active', sortOrder: 2,
  },
]

export function getCollectionBySlug(slug: string): Collection | undefined {
  return STATIC_COLLECTIONS.find(c => c.slug === slug)
}

export function getAllCollections(): Collection[] {
  return STATIC_COLLECTIONS
}

export function getActiveCollections(): Collection[] {
  return STATIC_COLLECTIONS.filter(c => c.status === 'active')
}

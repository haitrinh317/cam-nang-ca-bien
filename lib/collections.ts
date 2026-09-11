/**
 * collections.ts — Client-safe collection registry.
 * No Supabase imports. Safe for 'use client' components.
 *
 * For server-side DB fetching with fallback, use lib/collections-server.ts.
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
    icon: '🐟', accentColor: '#6fffe8', volumeCount: 6,
    status: 'active', sortOrder: 1,
  },
  {
    id: 'thuc-vat-bien', slug: 'thuc-vat-bien',
    nameVn: 'Thực vật biển', nameEn: 'Marine Plants & Algae of Vietnam',
    icon: '🌿', accentColor: '#a7f3d0', volumeCount: 2,
    status: 'active', sortOrder: 2,
  },
  {
    id: 'giap-xac', slug: 'giap-xac',
    nameVn: 'Giáp xác biển', nameEn: 'Marine Crustaceans of Vietnam',
    icon: '🦐', accentColor: '#fca5a5', volumeCount: 1,
    status: 'active', sortOrder: 3,
  },
  {
    id: 'ran-bien', slug: 'ran-bien',
    nameVn: 'Rắn biển Việt Nam', nameEn: 'Sea Snakes of Vietnam',
    icon: '🐍', accentColor: '#f59e0b', volumeCount: 1,
    status: 'active', sortOrder: 4,
  },
  {
    id: 'sinh-vat-doc', slug: 'sinh-vat-doc',
    nameVn: 'Động vật độc biển', nameEn: 'Venomous & Poisonous Marine Animals',
    icon: '☣️', accentColor: '#fb7185', volumeCount: 1,
    status: 'active', sortOrder: 5,
  },
  {
    id: 'than-mem', slug: 'than-mem',
    nameVn: 'Động vật thân mềm', nameEn: 'Marine Molluscs of Vietnam',
    icon: '🐚', accentColor: '#e8c4ff', volumeCount: 1,
    status: 'active', sortOrder: 6,
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

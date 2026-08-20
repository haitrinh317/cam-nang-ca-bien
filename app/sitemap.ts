/**
 * sitemap.ts — Generates dynamic XML sitemap for Google indexing
 * Static: /, /ca-bien, /ca-bien/taxonomy
 * Dynamic: /ca-bien/[speciesId] × 1574 species
 */
import { MetadataRoute } from 'next'
import { createServerClient } from '@/lib/supabase-server'

const BASE = 'https://cam-nang-ca-bien.vercel.app'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const db = createServerClient()

  // Fetch all species IDs for dynamic routes
  const [r1, r2] = await Promise.all([
    db.from('species').select('id, collection_id').range(0, 999),
    db.from('species').select('id, collection_id').range(1000, 1999),
  ])

  const species = [...(r1.data || []), ...(r2.data || [])]

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: BASE, lastModified: new Date(), changeFrequency: 'weekly', priority: 1 },
    { url: `${BASE}/ca-bien`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${BASE}/ca-bien/taxonomy`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
  ]

  const speciesRoutes: MetadataRoute.Sitemap = species.map(sp => ({
    url: `${BASE}/${sp.collection_id || 'ca-bien'}/${sp.id}`,
    changeFrequency: 'monthly' as const,
    priority: 0.6,
  }))

  return [...staticRoutes, ...speciesRoutes]
}

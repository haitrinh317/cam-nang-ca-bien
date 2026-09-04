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

  // Fetch all species IDs for dynamic routes (2,436+ rows — 3 pages of 1000)
  const q = (from: number, to: number) =>
    db.from('species').select('id, collection_id').is('deleted_at', null).range(from, to)
  const [r1, r2, r3] = await Promise.all([q(0, 999), q(1000, 1999), q(2000, 2999)])

  const species = [...(r1.data || []), ...(r2.data || []), ...(r3.data || [])]

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

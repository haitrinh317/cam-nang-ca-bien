/**
 * sitemap.ts — Generates dynamic XML sitemap for Google indexing
 * Covers all collections, taxonomy, static pages, and 2,436+ species
 */
import { MetadataRoute } from 'next'
import { createServerClient } from '@/lib/supabase-server'
import { getCollections } from '@/lib/collections-server'

const BASE = 'https://cam-nang-ca-bien.vercel.app'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const db = createServerClient()
  const collections = await getCollections()

  // 1. Static informational pages
  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE, lastModified: new Date(), changeFrequency: 'weekly', priority: 1.0 },
    { url: `${BASE}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${BASE}/faq`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
  ]

  // 2. Collection listing & taxonomy pages
  const collectionRoutes: MetadataRoute.Sitemap = collections.flatMap(col => [
    {
      url: `${BASE}/${col.slug || col.id}`,
      lastModified: new Date(),
      changeFrequency: 'weekly' as const,
      priority: 0.9,
    },
    {
      url: `${BASE}/${col.slug || col.id}/taxonomy`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 0.7,
    },
  ])

  // 3. Fetch all active species (chunked by 1000 rows to bypass Supabase default limits)
  const q = (from: number, to: number) =>
    db
      .from('species')
      .select('id, collection_id')
      .is('deleted_at', null)
      .range(from, to)

  const [r1, r2, r3, r4] = await Promise.all([
    q(0, 999),
    q(1000, 1999),
    q(2000, 2999),
    q(3000, 3999),
  ])

  const species = [
    ...(r1.data || []),
    ...(r2.data || []),
    ...(r3.data || []),
    ...(r4.data || []),
  ]

  const speciesRoutes: MetadataRoute.Sitemap = species.map(sp => ({
    url: `${BASE}/${sp.collection_id || 'ca-bien'}/${sp.id}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: 0.6,
  }))

  return [...staticPages, ...collectionRoutes, ...speciesRoutes]
}

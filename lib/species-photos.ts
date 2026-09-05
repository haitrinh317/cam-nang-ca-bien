/**
 * Species photo URL resolver — single source of truth for Supabase Storage paths.
 *
 * Previously duplicated across:
 *   - app/(public)/[collection]/[speciesId]/page.tsx  (×2: generateMetadata + page)
 *   - components/species/PhotoGallery.tsx             (inline publicUrl fn)
 *   - components/admin/PhotoManager.tsx               (const BUCKET)
 *   - app/api/species/photo/route.ts                  (const BUCKET)
 */

export const SPECIES_PHOTOS_BUCKET = 'species-photos'

const FALLBACK_OG = 'https://cam-nang-ca-bien.vercel.app/og-default.png'

/**
 * Build the full public CDN URL for a species photo stored in Supabase Storage.
 *
 * @param storagePath  The `storage_path` column value from `species_photos` table.
 * @returns Full URL, e.g. https://xxx.supabase.co/storage/v1/object/public/species-photos/abc.jpg
 */
export function getSpeciesPhotoUrl(storagePath: string): string {
  const base = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
  return `${base}/storage/v1/object/public/${SPECIES_PHOTOS_BUCKET}/${storagePath}`
}

/**
 * Resolve the best available photo URL for a species, with fallback chain:
 *   storage_path → source_url → fallback
 *
 * @param photo         A row from `species_photos` (may be undefined if no photo)
 * @param fallback      URL to use when no photo is available (defaults to OG image)
 */
export function resolvePhotoUrl(
  photo: { storage_path?: string | null; source_url?: string | null } | null | undefined,
  fallback = FALLBACK_OG
): string {
  if (photo?.storage_path) return getSpeciesPhotoUrl(photo.storage_path)
  if (photo?.source_url)   return photo.source_url
  return fallback
}

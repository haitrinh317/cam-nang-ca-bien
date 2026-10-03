/**
 * supabase-server.ts — Server-side Supabase clients
 *
 * createServerClient()  → for API Routes & Server Actions (no cookies needed)
 * createSSRClient()     → for Server Components that need auth session from cookies
 */
import { createClient } from '@supabase/supabase-js'
import { createServerClient as createSSRServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

const url = process.env.NEXT_PUBLIC_SUPABASE_URL!

/** Plain server client — for API Routes, no cookie session needed */
export function createServerClient() {
  // ponytail: fail-fast — service_role key is mandatory for server operations.
  // Silent fallback to anon_key would cause RLS-blocked writes that are hard to debug.
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!serviceKey) throw new Error('SUPABASE_SERVICE_ROLE_KEY is required for server client')
  return createClient(url, serviceKey)
}

/** SSR-aware client — reads session cookies for Server Components */
export async function createSSRClient() {
  const cookieStore = await cookies()
  return createSSRServerClient(
    url,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return cookieStore.getAll() },
        setAll() { /* read-only in Server Components */ },
      },
    }
  )
}

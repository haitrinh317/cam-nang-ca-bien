/**
 * Supabase browser client — for client components ('use client')
 * Uses anon key, safe to expose in browser.
 */
import { createBrowserClient } from '@supabase/ssr'

export const db = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

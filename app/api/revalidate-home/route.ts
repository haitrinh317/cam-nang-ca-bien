/**
 * API: POST /api/revalidate-home
 * Flush ISR cache cho trang chủ `/` sau khi Admin thay đổi literature_sources.
 * Chỉ cho phép admin đã đăng nhập gọi.
 * ponytail: 1 route nhỏ thay vì on-demand revalidation phức tạp.
 */
import { NextResponse } from 'next/server'
import { revalidatePath } from 'next/cache'
import { createSSRClient, createServerClient } from '@/lib/supabase-server'

export const dynamic = 'force-dynamic'

async function isAdmin(): Promise<boolean> {
  try {
    const ssrDb = await createSSRClient()
    const { data: { user } } = await ssrDb.auth.getUser()
    if (!user?.email) return false

    const serviceDb = createServerClient()
    const { data } = await serviceDb
      .from('user_roles')
      .select('role')
      .eq('email', user.email)
      .single()
    return data?.role === 'admin'
  } catch {
    return false
  }
}

export async function POST() {
  const ok = await isAdmin()
  if (!ok) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  revalidatePath('/')
  return NextResponse.json({ revalidated: true })
}

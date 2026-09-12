import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase-server'
import { SPECIES_DETAIL_COLS } from '@/lib/species-query'

export async function GET(req: NextRequest) {
  const db = createServerClient()
  const id = req.nextUrl.searchParams.get('id')

  if (!id) return NextResponse.json({ error: 'Missing id' }, { status: 400 })

  const { data, error } = await db.from('species').select(SPECIES_DETAIL_COLS).eq('id', id).single()

  if (error) return NextResponse.json({ error: error.message }, { status: 404 })

  return NextResponse.json({ data })
}

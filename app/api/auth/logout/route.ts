import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const url = request.nextUrl.clone()
  url.pathname = '/login'
  return NextResponse.redirect(url)
}

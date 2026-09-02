import { NextResponse } from 'next/server'

// MyMemory free API - no key needed, 500 chars/request limit
async function translateChunk(text: string): Promise<string> {
  const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=en|vi`
  const res = await fetch(url, { next: { revalidate: 86400 } }) // cache 24h
  if (!res.ok) throw new Error(`MyMemory API error: ${res.status}`)
  const json = await res.json()
  if (json.responseStatus !== 200) throw new Error('Translation failed')
  return json.responseData.translatedText as string
}

export async function POST(request: Request) {
  try {
    const { text } = await request.json()
    if (!text) return NextResponse.json({ error: 'Missing text' }, { status: 400 })

    // Chunk at 450 chars (MyMemory limit is 500)
    const CHUNK = 450
    if (text.length <= CHUNK) {
      const translated = await translateChunk(text)
      return NextResponse.json({ text: translated })
    }

    // Split on sentence boundaries near the chunk limit
    const chunks: string[] = []
    let remaining = text as string
    while (remaining.length > CHUNK) {
      let cut = remaining.lastIndexOf('. ', CHUNK)
      if (cut < 200) cut = remaining.lastIndexOf(' ', CHUNK)
      if (cut < 1) cut = CHUNK
      chunks.push(remaining.slice(0, cut + 1))
      remaining = remaining.slice(cut + 1)
    }
    if (remaining) chunks.push(remaining)

    const parts = await Promise.all(chunks.map(translateChunk))
    return NextResponse.json({ text: parts.join(' ') })
  } catch (error) {
    console.error('Translation error:', error)
    return NextResponse.json({ error: 'Failed to translate' }, { status: 500 })
  }
}

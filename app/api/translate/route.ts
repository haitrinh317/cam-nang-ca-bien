import { NextResponse } from 'next/server'

const GEMINI_API_KEY = process.env.GEMINI_API_KEY

async function translateWithGemini(text: string): Promise<string> {
  if (!GEMINI_API_KEY) throw new Error('No GEMINI_API_KEY')
  const prompt = `Bạn là chuyên gia Ngư loại học và Sinh học biển tại Việt Nam.
Hãy dịch đoạn văn bản mô tả sinh học/sinh thái sau đây sang tiếng Việt với văn phong khoa học chuẩn mực, trang trọng, gãy gọn, thuật ngữ chính xác (ví dụ: continental shelf: thềm lục địa, reef-associated: sống quanh rạn san hô, demersal: tầng đáy, pelagic: tầng nổi, oviparous: đẻ trứng, ovoviviparous: noãn thai sinh...).
Tuyệt đối không dịch máy thô từng từ. Giữ nguyên tên khoa học La-tinh.
Chỉ trả về duy nhất đoạn văn bản tiếng Việt đã dịch, không thêm lời chào, không đặt trong markdown.

Văn bản cần dịch:
${text}`

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=${GEMINI_API_KEY}`
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.2 }
    })
  })
  if (!res.ok) throw new Error(`Gemini API error ${res.status}`)
  const data = await res.json()
  const translated = data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim()
  if (!translated) throw new Error('Empty Gemini translation')
  return translated
}

// MyMemory free API fallback
async function translateChunk(text: string): Promise<string> {
  const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=en|vi`
  const res = await fetch(url, { next: { revalidate: 86400 } })
  if (!res.ok) throw new Error(`MyMemory API error: ${res.status}`)
  const json = await res.json()
  if (json.responseStatus !== 200) throw new Error('Translation failed')
  return json.responseData.translatedText as string
}

export async function POST(request: Request) {
  try {
    const { text } = await request.json()
    if (!text) return NextResponse.json({ error: 'Missing text' }, { status: 400 })

    // Ưu tiên sử dụng Gemini
    if (GEMINI_API_KEY) {
      try {
        const translated = await translateWithGemini(text)
        return NextResponse.json({ text: translated })
      } catch (geminiError) {
        console.warn('Gemini translate failed, falling back to MyMemory:', geminiError)
      }
    }

    // Fallback sang MyMemory
    const CHUNK = 450
    if (text.length <= CHUNK) {
      const translated = await translateChunk(text)
      return NextResponse.json({ text: translated })
    }

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

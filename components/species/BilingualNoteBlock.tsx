'use client'

import { useEffect, useState } from 'react'
import { AlertTriangle } from 'lucide-react'

interface Props {
  labelEn: string
  labelVn: string
  text: string
  cacheKey: string
}

async function translateToVi(text: string): Promise<string> {
  if (text.length > 2000) {
    const chunks: string[] = []
    for (let i = 0; i < text.length; i += 1800) chunks.push(text.slice(i, i + 1800))
    const results = await Promise.all(chunks.map(c => translateToVi(c)))
    return results.join(' ')
  }
  const res = await fetch('/api/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
  if (!res.ok) throw new Error('translate fail')
  const json = await res.json()
  return json.text
}

export default function BilingualNoteBlock({ labelEn, labelVn, text, cacheKey }: Props) {
  const [vnText, setVnText] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)

  useEffect(() => {
    const cached = sessionStorage.getItem(cacheKey)
    if (cached) { setVnText(cached); return }
    setLoading(true)
    translateToVi(text)
      .then(vn => { sessionStorage.setItem(cacheKey, vn); setVnText(vn) })
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [text, cacheKey])

  return (
    <div className="bio-notes-block">
      <div className="bio-notes-header">
        <span className="bio-notes-label-vn">{labelEn}</span>
        <span className="bio-notes-label-en">({labelVn})</span>
      </div>
      <div className="bio-notes-en" style={{ marginBottom: '0.5rem' }}>
        <p className="bio-notes-text bio-notes-text--en">{text}</p>
      </div>
      <details className="bio-notes-en-details">
        <summary className="bio-notes-en-toggle">Xem bản dịch tiếng Việt (tham khảo)</summary>
        <div className="bio-notes-vn" style={{ marginTop: '0.5rem' }}>
          {loading && <span className="bio-notes-loading">Đang dịch...</span>}
          {error && <span className="bio-notes-error">Không thể tải bản dịch.</span>}
          {vnText && (
            <>
              <p className="bio-notes-text">{vnText}</p>
              <p className="bio-notes-disclaimer" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <AlertTriangle size={14} /> Bản dịch từ AI, chỉ có tính chất tham khảo.
              </p>
            </>
          )}
        </div>
      </details>
    </div>
  )
}

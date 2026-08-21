'use client'

import { useState, useRef } from 'react'

interface Props {
  collection: string
  onImported: () => void
}

export default function ImportModal({ collection, onImported }: Props) {
  const [open, setOpen] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<Record<string, unknown>[] | null>(null)
  const [status, setStatus] = useState<'idle' | 'loading' | 'done' | 'error'>('idle')
  const [result, setResult] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    setFile(f)
    setStatus('idle')
    setResult('')

    try {
      const text = await f.text()
      const json = JSON.parse(text)
      const arr = Array.isArray(json) ? json : [json]
      setPreview(arr.slice(0, 5))
    } catch {
      setPreview(null)
      setResult('File không phải JSON hợp lệ.')
      setStatus('error')
    }
  }

  const handleImport = async () => {
    if (!file || !preview) return
    setStatus('loading')

    try {
      const text = await file.text()
      const json = JSON.parse(text)
      const arr = Array.isArray(json) ? json : [json]

      const res = await fetch('/api/species/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ species: arr, collection_id: collection }),
      })
      const data = await res.json()
      if (!res.ok) {
        setResult(data.error || 'Lỗi không xác định')
        setStatus('error')
        return
      }
      setResult(data.message || `Đã import ${data.imported} loài.`)
      setStatus('done')
      onImported()
    } catch (err) {
      setResult(`Lỗi: ${err}`)
      setStatus('error')
    }
  }

  const reset = () => {
    setFile(null)
    setPreview(null)
    setStatus('idle')
    setResult('')
    if (inputRef.current) inputRef.current.value = ''
  }

  if (!open) {
    return (
      <button className="btn btn-outline" onClick={() => setOpen(true)} type="button">
        📥 Import JSON
      </button>
    )
  }

  return (
    <div className="admin-modal-overlay" onClick={() => { setOpen(false); reset() }}>
      <div className="admin-modal admin-modal--wide" onClick={e => e.stopPropagation()}>
        <div className="admin-modal__header">
          <h3>📥 Import loài từ file JSON</h3>
          <button className="admin-modal__close" onClick={() => { setOpen(false); reset() }} type="button" aria-label="Đóng">✕</button>
        </div>

        <div className="admin-modal__body">
          {/* File picker */}
          <div className="import-drop-zone">
            <input
              ref={inputRef}
              type="file"
              accept=".json"
              onChange={handleFile}
              id="import-file"
              style={{ display: 'none' }}
            />
            <label htmlFor="import-file" className="import-drop-label">
              {file ? (
                <>
                  <span className="import-icon">📄</span>
                  <span className="import-filename">{file.name}</span>
                  <span className="import-filesize">{(file.size / 1024).toFixed(1)} KB</span>
                </>
              ) : (
                <>
                  <span className="import-icon">📂</span>
                  <span>Chọn file JSON hoặc kéo thả vào đây</span>
                  <span className="import-hint">Hỗ trợ file JSON chứa mảng loài (tối đa 200 loài/lần)</span>
                </>
              )}
            </label>
          </div>

          {/* Preview */}
          {preview && preview.length > 0 && (
            <div className="import-preview">
              <h4>Xem trước ({preview.length <= 5 ? preview.length : `5/${preview.length}`} loài đầu tiên)</h4>
              <div className="admin-table-scroll" style={{ maxHeight: '200px' }}>
                <table className="admin-table" style={{ fontSize: '0.8rem' }}>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Tên VN</th>
                      <th>Tên khoa học</th>
                      <th>Tập</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.map((sp, i) => (
                      <tr key={i}>
                        <td><code>{String(sp.id || '—')}</code></td>
                        <td>{String(sp.vn_name || sp.vnName || '—')}</td>
                        <td style={{ fontStyle: 'italic' }}>{String(sp.scientific_name || sp.scientificName || '—')}</td>
                        <td>{String(sp.volume || '—')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Result message */}
          {result && (
            <div className={`import-result ${status === 'error' ? 'import-result--error' : status === 'done' ? 'import-result--success' : ''}`}>
              {result}
            </div>
          )}
        </div>

        <div className="admin-modal__footer">
          <button className="btn btn-outline" onClick={() => { setOpen(false); reset() }} type="button">Đóng</button>
          <button
            className="btn btn-primary"
            onClick={handleImport}
            disabled={!preview || status === 'loading' || status === 'done'}
            type="button"
          >
            {status === 'loading' ? 'Đang import...' : status === 'done' ? '✓ Hoàn tất' : 'Import vào CSDL'}
          </button>
        </div>
      </div>
    </div>
  )
}

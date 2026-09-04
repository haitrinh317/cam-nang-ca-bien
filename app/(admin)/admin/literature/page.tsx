'use client'

import { useEffect, useState, useCallback } from 'react'
import { db } from '@/lib/supabase-browser'
import { BookOpen, Plus, Pencil, Trash2, Eye, EyeOff } from 'lucide-react'
import { STATIC_COLLECTIONS } from '@/lib/collections-static'

interface LinkOption {
  label: string
  href: string
  statsCount: string
}

interface LitSource {
  id: string
  title: string
  subtitle: string | null
  author: string
  publisher: string | null
  year: string | null
  stats_count: string | null
  pill_text: string | null
  description: string | null
  href: string
  chips: string[] | null
  icon_name: string | null
  sort_order: number
  is_visible: boolean
}

const EMPTY_FORM: Omit<LitSource, 'id'> = {
  title: '', subtitle: '', author: '', publisher: '', year: '',
  stats_count: '', pill_text: '', description: '', href: '',
  chips: [], icon_name: 'book-open', sort_order: 0, is_visible: true,
}

const ICON_OPTIONS = ['fish', 'compass', 'leaf', 'book-open', 'anchor', 'shell', 'waves']

export default function AdminLiteraturePage() {
  const [sources, setSources] = useState<LitSource[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<LitSource | null>(null)
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [chipsText, setChipsText] = useState('')
  const [linkOptions, setLinkOptions] = useState<LinkOption[]>([])

  const loadData = useCallback(async () => {
    setLoading(true)
    const { data } = await db
      .from('literature_sources')
      .select('*')
      .order('sort_order')
    setSources((data || []) as LitSource[])
    setLoading(false)
  }, [])

  // Fetch collection/volume stats for smart dropdowns
  const loadLinkOptions = useCallback(async () => {
    const { data } = await db
      .from('species')
      .select('collection_id, volume')
      .is('deleted_at', null)

    if (!data) return

    // Group by collection and volume
    const collMap = new Map<string, number>()
    const volMap = new Map<string, number>()
    for (const row of data) {
      const cKey = row.collection_id
      const vKey = `${row.collection_id}|${row.volume}`
      collMap.set(cKey, (collMap.get(cKey) || 0) + 1)
      volMap.set(vKey, (volMap.get(vKey) || 0) + 1)
    }

    const nameMap: Record<string, string> = {}
    STATIC_COLLECTIONS.forEach(c => { nameMap[c.id] = c.nameVn })

    const options: LinkOption[] = []

    // Collection-level options
    for (const [cid, count] of collMap) {
      const name = nameMap[cid] || cid
      options.push({
        label: `${name} (toàn bộ — ${count.toLocaleString()} loài)`,
        href: `/${cid}`,
        statsCount: `${count.toLocaleString()} loài`,
      })
    }

    // Volume-level options
    for (const [vKey, count] of volMap) {
      const [cid, vol] = vKey.split('|')
      const name = nameMap[cid] || cid
      options.push({
        label: `${name} — Tập ${vol} (${count.toLocaleString()} loài)`,
        href: `/${cid}?vol=${vol}`,
        statsCount: `${count.toLocaleString()} loài`,
      })
    }

    // Sort: collection-level first, then by href
    options.sort((a, b) => {
      const aIsCol = !a.href.includes('?')
      const bIsCol = !b.href.includes('?')
      if (aIsCol !== bIsCol) return aIsCol ? -1 : 1
      return a.href.localeCompare(b.href)
    })

    setLinkOptions(options)
  }, [])

  useEffect(() => { loadData(); loadLinkOptions() }, [loadData, loadLinkOptions])

  const handleLinkSelect = (href: string) => {
    setField('href', href)
    const match = linkOptions.find(o => o.href === href)
    if (match) setField('stats_count', match.statsCount)
  }

  const openCreate = () => {
    setEditing(null)
    setForm({ ...EMPTY_FORM, sort_order: sources.length + 1 })
    setChipsText('')
    setCreating(true)
  }

  const openEdit = (item: LitSource) => {
    setCreating(false)
    setEditing(item)
    setForm({
      title: item.title,
      subtitle: item.subtitle || '',
      author: item.author,
      publisher: item.publisher || '',
      year: item.year || '',
      stats_count: item.stats_count || '',
      pill_text: item.pill_text || '',
      description: item.description || '',
      href: item.href,
      chips: item.chips || [],
      icon_name: item.icon_name || 'book-open',
      sort_order: item.sort_order,
      is_visible: item.is_visible,
    })
    setChipsText((item.chips || []).join('\n'))
  }

  const closeModal = () => {
    setEditing(null)
    setCreating(false)
  }

  const handleSave = async () => {
    setSaving(true)
    const payload = {
      ...form,
      chips: chipsText.split('\n').map(s => s.trim()).filter(Boolean),
      updated_at: new Date().toISOString(),
    }

    if (creating) {
      await db.from('literature_sources').insert(payload)
    } else if (editing) {
      await db.from('literature_sources').update(payload).eq('id', editing.id)
    }

    setSaving(false)
    closeModal()
    loadData()
  }

  const handleDelete = async (id: string, title: string) => {
    if (!confirm(`Xác nhận xóa "${title}"?`)) return
    await db.from('literature_sources').delete().eq('id', id)
    loadData()
  }

  const toggleVisible = async (item: LitSource) => {
    await db.from('literature_sources')
      .update({ is_visible: !item.is_visible, updated_at: new Date().toISOString() })
      .eq('id', item.id)
    loadData()
  }

  const setField = (key: string, value: string | number | boolean) => {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  const isFormOpen = creating || editing !== null

  return (
    <div className="admin-page">
      <div className="admin-page__header">
        <div>
          <h1 className="admin-page__title">Quản lý Tài liệu gốc</h1>
          <p style={{ color: 'var(--color-muted)', marginTop: '0.5rem' }}>
            Các tài liệu khoa học hiển thị trên trang chủ. Thêm, sửa, xóa hoặc ẩn/hiện.
          </p>
        </div>
        <button className="btn btn-primary" onClick={openCreate} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Plus size={16} /> Thêm tài liệu
        </button>
      </div>

      {loading ? (
        <div className="list-status-message"><div className="spinner" /><span>Đang tải...</span></div>
      ) : (
        <div className="admin-table-scroll">
          <table className="admin-table">
            <thead>
              <tr>
                <th style={{ width: 50 }}>TT</th>
                <th>Tên tài liệu</th>
                <th>Tác giả</th>
                <th>Số loài</th>
                <th style={{ width: 80 }}>Hiển thị</th>
                <th style={{ width: 120 }}>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {sources.length === 0 && (
                <tr><td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-muted)' }}>Chưa có tài liệu nào.</td></tr>
              )}
              {sources.map(item => (
                <tr key={item.id}>
                  <td style={{ textAlign: 'center', fontWeight: 600 }}>{item.sort_order}</td>
                  <td>
                    <div style={{ fontWeight: 600 }}>{item.title}</div>
                    {item.subtitle && <div style={{ fontSize: '0.8rem', color: 'var(--color-muted)' }}>{item.subtitle}</div>}
                  </td>
                  <td style={{ fontSize: '0.85rem' }}>{item.author}</td>
                  <td style={{ fontSize: '0.85rem', fontWeight: 500 }}>{item.stats_count}</td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      className="btn-icon"
                      onClick={() => toggleVisible(item)}
                      title={item.is_visible ? 'Đang hiện — click để ẩn' : 'Đang ẩn — click để hiện'}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: item.is_visible ? 'var(--brand-primary)' : 'var(--color-muted)' }}
                    >
                      {item.is_visible ? <Eye size={18} /> : <EyeOff size={18} />}
                    </button>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        className="btn btn-outline btn-sm"
                        onClick={() => openEdit(item)}
                        title="Sửa"
                        style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                      >
                        <Pencil size={14} /> Sửa
                      </button>
                      <button
                        className="btn btn-outline btn-sm"
                        onClick={() => handleDelete(item.id, item.title)}
                        title="Xóa"
                        style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#ef4444', borderColor: 'rgba(239,68,68,0.3)' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ─── Modal Form ─── */}
      {isFormOpen && (
        <div className="admin-modal-overlay" onClick={closeModal}>
          <div className="admin-modal admin-modal--wide" onClick={e => e.stopPropagation()}>
            <div className="admin-modal__header">
              <h3>{creating ? 'Thêm tài liệu mới' : `Sửa: ${editing?.title}`}</h3>
              <button className="admin-modal__close" onClick={closeModal}>&times;</button>
            </div>

            <div className="admin-modal__body">
              <div className="form-grid">
                <div className="form-field">
                  <label className="form-label">Tên tài liệu *</label>
                  <input className="form-input" value={form.title} onChange={e => setField('title', e.target.value)} placeholder="Danh mục Cá biển Việt Nam" />
                </div>
                <div className="form-field">
                  <label className="form-label">Phụ đề</label>
                  <input className="form-input" value={form.subtitle || ''} onChange={e => setField('subtitle', e.target.value)} placeholder="Tập I – V (1992 – 2007)" />
                </div>
                <div className="form-field">
                  <label className="form-label">Tác giả *</label>
                  <input className="form-input" value={form.author} onChange={e => setField('author', e.target.value)} />
                </div>
                <div className="form-field">
                  <label className="form-label">Nhà xuất bản</label>
                  <input className="form-input" value={form.publisher || ''} onChange={e => setField('publisher', e.target.value)} />
                </div>
                <div className="form-field">
                  <label className="form-label">Năm</label>
                  <input className="form-input" value={form.year || ''} onChange={e => setField('year', e.target.value)} placeholder="1992 – 2007" />
                </div>
                <div className="form-field">
                  <label className="form-label">Link tra cứu *</label>
                  <select className="form-input" value={form.href} onChange={e => handleLinkSelect(e.target.value)}>
                    <option value="">— Chọn bộ sưu tập —</option>
                    {linkOptions.map(opt => (
                      <option key={opt.href} value={opt.href}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label className="form-label">Số loài (hiển thị)</label>
                  <input className="form-input" value={form.stats_count || ''} onChange={e => setField('stats_count', e.target.value)} placeholder="Tự điền khi chọn link — hoặc nhập tay" />
                </div>
                <div className="form-field">
                  <label className="form-label">Badge pill</label>
                  <input className="form-input" value={form.pill_text || ''} onChange={e => setField('pill_text', e.target.value)} placeholder="5 Tập Chuyên Khảo" />
                </div>
                <div className="form-field">
                  <label className="form-label">Icon</label>
                  <select className="form-input" value={form.icon_name || 'book-open'} onChange={e => setField('icon_name', e.target.value)}>
                    {ICON_OPTIONS.map(ico => <option key={ico} value={ico}>{ico}</option>)}
                  </select>
                </div>
                <div className="form-field">
                  <label className="form-label">Thứ tự</label>
                  <input className="form-input" type="number" value={form.sort_order} onChange={e => setField('sort_order', parseInt(e.target.value) || 0)} />
                </div>
              </div>

              <div className="form-grid form-grid--single" style={{ marginTop: 'var(--space-lg)' }}>
                <div className="form-field">
                  <label className="form-label">Mô tả</label>
                  <textarea className="form-input" rows={3} value={form.description || ''} onChange={e => setField('description', e.target.value)} />
                </div>
                <div className="form-field">
                  <label className="form-label">Chips (mỗi dòng 1 chip)</label>
                  <textarea className="form-input" rows={4} value={chipsText} onChange={e => setChipsText(e.target.value)} placeholder="T.I: Cá nhám, cá đuối&#10;T.II: Cá trích, cá chình" />
                </div>
              </div>

              <div style={{ marginTop: 'var(--space-lg)' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input type="checkbox" checked={form.is_visible} onChange={e => setField('is_visible', e.target.checked)} />
                  <span style={{ fontSize: '0.9rem' }}>Hiển thị trên trang chủ</span>
                </label>
              </div>
            </div>

            <div className="admin-modal__footer">
              <button className="btn btn-outline" onClick={closeModal}>Hủy</button>
              <button className="btn btn-primary" onClick={handleSave} disabled={saving || !form.title || !form.author || !form.href}>
                {saving ? 'Đang lưu...' : creating ? 'Thêm mới' : 'Cập nhật'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

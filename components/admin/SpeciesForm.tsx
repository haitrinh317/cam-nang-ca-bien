'use client'

import { useState } from 'react'
import { ClipboardList, Leaf, Globe, BookOpen, Camera, X } from 'lucide-react'
import PhotoManager from './PhotoManager'

interface SpeciesRow {
  id?: string
  volume?: number
  species_index?: number | null
  vn_name?: string
  scientific_name?: string
  authorship?: string | null
  tax_class_vn?: string | null
  tax_class_latin?: string | null
  tax_order_vn?: string | null
  tax_order_latin?: string | null
  tax_family_vn?: string | null
  tax_family_latin?: string | null
  tax_genus_vn?: string | null
  tax_genus_latin?: string | null
  vn_alternate_names?: string | null
  vn_size?: string | null
  vn_distribution?: string | null
  vn_specimen?: string | null
  vn_status?: string | null
  vn_literature?: string | null
  en_common_name?: string | null
  en_size?: string | null
  en_distribution?: string | null
  en_specimen?: string | null
  en_status?: string | null
  en_literature?: string | null
  photo_url?: string | null
  morphology_vn?: string | null
  morphology_en?: string | null
  ecology_vn?: string | null
  ecology_en?: string | null
  economic_value_vn?: string | null
  economic_value_en?: string | null
}

interface Props {
  initial: SpeciesRow | null
  collection: string
  onSave: (data: Record<string, unknown>, id?: string) => Promise<boolean>
  onClose: () => void
}

type Tab = 'basic' | 'taxonomy' | 'vn' | 'en' | 'photo'

function Field({ label, name, value, onChange, required, textarea }: {
  label: string; name: string; value: string; onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void
  required?: boolean; textarea?: boolean
}) {
  return (
    <div className="form-field">
      <label className="form-label" htmlFor={`field-${name}`}>
        {label}{required && <span style={{ color: '#ef4444' }}> *</span>}
      </label>
      {textarea
        ? <textarea id={`field-${name}`} className="form-input" name={name} value={value} onChange={onChange} rows={3} />
        : <input id={`field-${name}`} className="form-input" type="text" name={name} value={value} onChange={onChange} required={required} />
      }
    </div>
  )
}

export default function SpeciesForm({ initial, collection, onSave, onClose }: Props) {
  const [tab, setTab] = useState<Tab>('basic')
  const [saving, setSaving] = useState(false)
  const genusLabel = collection === 'thuc-vat-bien' ? 'Chi' : 'Giống'
  const [form, setForm] = useState<Record<string, string>>({
    id:               initial?.id || '',
    volume:           String(initial?.volume || 1),
    species_index:    String(initial?.species_index || ''),
    vn_name:          initial?.vn_name || '',
    scientific_name:  initial?.scientific_name || '',
    authorship:       initial?.authorship || '',
    tax_class_vn:     initial?.tax_class_vn || '',
    tax_class_latin:  initial?.tax_class_latin || '',
    tax_order_vn:     initial?.tax_order_vn || '',
    tax_order_latin:  initial?.tax_order_latin || '',
    tax_family_vn:    initial?.tax_family_vn || '',
    tax_family_latin: initial?.tax_family_latin || '',
    tax_genus_vn:     initial?.tax_genus_vn || '',
    tax_genus_latin:  initial?.tax_genus_latin || '',
    vn_alternate_names: initial?.vn_alternate_names || '',
    vn_size:          initial?.vn_size || '',
    vn_distribution:  initial?.vn_distribution || '',
    vn_specimen:      initial?.vn_specimen || '',
    vn_status:        initial?.vn_status || '',
    vn_literature:    initial?.vn_literature || '',
    en_common_name:   initial?.en_common_name || '',
    en_size:          initial?.en_size || '',
    en_distribution:  initial?.en_distribution || '',
    en_specimen:      initial?.en_specimen || '',
    en_status:        initial?.en_status || '',
    en_literature:    initial?.en_literature || '',
    morphology_vn:    (initial as any)?.morphology_vn || '',
    morphology_en:    (initial as any)?.morphology_en || '',
    ecology_vn:       (initial as any)?.ecology_vn || '',
    ecology_en:       (initial as any)?.ecology_en || '',
    economic_value_vn: (initial as any)?.economic_value_vn || '',
    economic_value_en: (initial as any)?.economic_value_en || '',
  })

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    // Cast numeric fields
    const payload: Record<string, unknown> = {
      ...form,
      volume: parseInt(form.volume) || 1,
      species_index: form.species_index ? parseInt(form.species_index) : null,
      collection_id: collection,
    }
    // Remove id from payload (it's in the URL for PATCH)
    const id = initial?.id
    if (!id) delete payload.id // new record: let DB generate
    const ok = await onSave(payload, id)
    if (!ok) setSaving(false)
  }

  const TABS: { key: Tab; label: React.ReactNode }[] = [
    { key: 'basic', label: <><ClipboardList size={16} /> Cơ bản</> },
    { key: 'taxonomy', label: <><Leaf size={16} /> Phân loại</> },
    { key: 'vn', label: <><Globe size={16} /> Tiếng Việt</> },
    { key: 'en', label: <><BookOpen size={16} /> English</> },
    ...(initial?.id ? [{ key: 'photo' as Tab, label: <><Camera size={16} /> Ảnh</> }] : []),
  ]

  return (
    <div className="admin-modal-overlay" onClick={onClose}>
      <div className="admin-modal admin-modal--wide" onClick={e => e.stopPropagation()}>
        <div className="admin-modal__header">
          <h3>{initial ? `Sửa: ${initial.vn_name}` : 'Thêm Loài Mới'}</h3>
          <button className="admin-modal__close" onClick={onClose} type="button" aria-label="Đóng"><X size={20} /></button>
        </div>

        {/* Tabs */}
        <div className="form-tabs">
          {TABS.map(t => (
            <button
              key={t.key}
              className={`form-tab${tab === t.key ? ' active' : ''}`}
              onClick={() => setTab(t.key)}
              type="button"
            >
              {t.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit}>
          <div className="admin-modal__body">
            {/* Tab: Cơ bản */}
            {tab === 'basic' && (
              <div className="form-grid">
                <Field label="ID loài" name="id" value={form.id} onChange={onChange} required={!initial} />
                <div className="form-field">
                  <label className="form-label" htmlFor="field-volume">Tập số <span style={{ color: '#ef4444' }}>*</span></label>
                  <select id="field-volume" className="form-input admin-select" name="volume" value={form.volume} onChange={onChange}>
                    {[1,2,3,4,5].map(v => <option key={v} value={v}>Tập {v}</option>)}
                    <option value={6}>Atlas cá rạn san hô VN</option>
                  </select>
                </div>
                <Field label="STT trong tập" name="species_index" value={form.species_index} onChange={onChange} />
                <Field label="Tên tiếng Việt" name="vn_name" value={form.vn_name} onChange={onChange} required />
                <Field label="Tên khoa học" name="scientific_name" value={form.scientific_name} onChange={onChange} required />
                <Field label="Tác giả (Authorship)" name="authorship" value={form.authorship} onChange={onChange} />
              </div>
            )}

            {/* Tab: Phân loại */}
            {tab === 'taxonomy' && (
              <div className="form-grid">
                <Field label="Lớp (Tiếng Việt)" name="tax_class_vn" value={form.tax_class_vn} onChange={onChange} />
                <Field label="Lớp (Latin)" name="tax_class_latin" value={form.tax_class_latin} onChange={onChange} />
                <Field label="Bộ (Tiếng Việt)" name="tax_order_vn" value={form.tax_order_vn} onChange={onChange} />
                <Field label="Bộ (Latin)" name="tax_order_latin" value={form.tax_order_latin} onChange={onChange} />
                <Field label="Họ (Tiếng Việt)" name="tax_family_vn" value={form.tax_family_vn} onChange={onChange} />
                <Field label="Họ (Latin)" name="tax_family_latin" value={form.tax_family_latin} onChange={onChange} />
                <Field label={`${genusLabel} (Tiếng Việt)`} name="tax_genus_vn" value={form.tax_genus_vn} onChange={onChange} />
                <Field label={`${genusLabel} (Latin)`} name="tax_genus_latin" value={form.tax_genus_latin} onChange={onChange} />
              </div>
            )}

            {/* Tab: Tiếng Việt */}
            {tab === 'vn' && (
              <div className="form-grid form-grid--single">
                <Field label="Tên gọi khác" name="vn_alternate_names" value={form.vn_alternate_names} onChange={onChange} />
                <Field label="Mô tả hình thái" name="morphology_vn" value={form.morphology_vn} onChange={onChange} textarea />
                <Field label="Kích thước" name="vn_size" value={form.vn_size} onChange={onChange} textarea />
                <Field label="Sinh thái &amp; Dinh dưỡng" name="ecology_vn" value={form.ecology_vn} onChange={onChange} textarea />
                <Field label="Phân bố" name="vn_distribution" value={form.vn_distribution} onChange={onChange} textarea />
                <Field label="Giá trị kinh tế" name="economic_value_vn" value={form.economic_value_vn} onChange={onChange} textarea />
                <Field label="Nơi lưu trữ mẫu" name="vn_specimen" value={form.vn_specimen} onChange={onChange} textarea />
                <Field label="Tình trạng" name="vn_status" value={form.vn_status} onChange={onChange} textarea />
                <Field label="Tài liệu dẫn" name="vn_literature" value={form.vn_literature} onChange={onChange} textarea />
              </div>
            )}

            {/* Tab: English */}
            {tab === 'en' && (
              <div className="form-grid form-grid--single">
                <Field label="Common Name" name="en_common_name" value={form.en_common_name} onChange={onChange} />
                <Field label="Morphology (EN)" name="morphology_en" value={form.morphology_en} onChange={onChange} textarea />
                <Field label="Size" name="en_size" value={form.en_size} onChange={onChange} textarea />
                <Field label="Ecology & Diet (EN)" name="ecology_en" value={form.ecology_en} onChange={onChange} textarea />
                <Field label="Distribution" name="en_distribution" value={form.en_distribution} onChange={onChange} textarea />
                <Field label="Economic Value (EN)" name="economic_value_en" value={form.economic_value_en} onChange={onChange} textarea />
                <Field label="Specimen" name="en_specimen" value={form.en_specimen} onChange={onChange} textarea />
                <Field label="Status" name="en_status" value={form.en_status} onChange={onChange} textarea />
                <Field label="Literature" name="en_literature" value={form.en_literature} onChange={onChange} textarea />
              </div>
            )}

            {/* Tab: Ảnh */}
            {tab === 'photo' && initial?.id && (
              <div className="form-grid form-grid--single">
                <PhotoManager
                  speciesId={initial.id}
                  currentUrl={form.photo_url || initial?.photo_url || null}
                  onUpdated={(url) => setForm(f => ({ ...f, photo_url: url }))}
                />
              </div>
            )}
          </div>

          <div className="admin-modal__footer">
            <button className="btn btn-outline" onClick={onClose} type="button">Hủy</button>
            <button className="btn btn-primary" type="submit" disabled={saving}>
              {saving ? 'Đang lưu...' : (initial ? 'Cập nhật' : 'Thêm loài')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

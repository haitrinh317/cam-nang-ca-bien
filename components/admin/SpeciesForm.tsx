'use client'

import { useState } from 'react'
import { ClipboardList, Leaf, Globe, BookOpen, Camera, Database, X, Plus } from 'lucide-react'
import PhotoManager from './PhotoManager'
import DistributionEditor from './DistributionEditor'
import { speciesUpdateSchema, speciesCreateSchema } from '@/lib/schemas'

interface BiologyData {
  iucnStatus?: string | null
  maxLength?: string | null
  maxWeight?: string | null
  dangerous?: string | null
  habitat?: string | null
  habitatVn?: string | null
  source?: string | null
  fbSpecCode?: number | string | null
  fbName?: string | null
  algaebaseId?: number | string | null
  algaebaseUrl?: string | null
  feedingType?: string | null
  trophicLevel?: number | string | null
  depth?: string | null
  depthVn?: string | null
  longevity?: string | null
  reproduction?: string | null
  spawning?: string | null
  spawnAggregation?: string | null
  parentalCare?: string | null
  importance?: string | null
  importanceVn?: string | null
  aquaculture?: string | null
  priceCategory?: string | null
  vulnerability?: number | string | null
  biologySummary?: string | null
  biologySummaryVn?: string | null
  ecologyNotes?: string | null
  ecologyNotesVn?: string | null
  reproductionNotes?: string | null
  reproductionNotesVn?: string | null
  morphDescription?: string | null
  morphDescriptionVn?: string | null
  toxicology?: {
    toxinType?: string | null
    mechanism?: string | null
    firstAidProtocol?: string | null
    [key: string]: unknown
  } | null
  vnRedList?: {
    status?: string | null
    statusVn?: string | null
    year?: string | null
    version?: string | null
    assessor?: string | null
    contributor?: string | null
    refCode?: string | null
    citation?: string | null
    criteria?: string | null
    threats?: string | null
    conservation?: string | null
    population?: string | null
    url?: string | null
  } | null
  [key: string]: unknown
}

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
  worms_status?: string | null
  worms_accepted_name?: string | null
  worms_id?: number | null
  worms_synced_at?: string | null
  worms_lsid?: string | null
  synonyms?: string | string[] | null
  biology?: BiologyData | string | null
}

interface Props {
  initial: SpeciesRow | null
  collection: string
  onSave: (data: Record<string, unknown>, id?: string) => Promise<boolean>
  onClose: () => void
}

type Tab = 'basic' | 'taxonomy' | 'vn' | 'en' | 'sync' | 'photo'

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

function parseSynonyms(val: unknown): string[] {
  if (!val) return []
  if (Array.isArray(val)) return val.map(item => String(item).trim()).filter(Boolean)
  if (typeof val === 'string') {
    try {
      const parsed = JSON.parse(val)
      if (Array.isArray(parsed)) return parsed.map(item => String(item).trim()).filter(Boolean)
    } catch {
      if (val.trim()) return val.split(',').map(s => s.trim()).filter(Boolean)
    }
  }
  return []
}

export default function SpeciesForm({ initial, collection, onSave, onClose }: Props) {
  const [tab, setTab] = useState<Tab>('basic')
  const [saving, setSaving] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const genusLabel = collection === 'thuc-vat-bien' ? 'Chi' : 'Giống'

  const rawBio = initial?.biology
  const bio: BiologyData = (typeof rawBio === 'string' ? (() => {
    try { return JSON.parse(rawBio) } catch { return {} }
  })() : rawBio) || {}

  const [synonymsList, setSynonymsList] = useState<string[]>(() => parseSynonyms(initial?.synonyms))
  const [newSynonym, setNewSynonym] = useState('')

  const [form, setForm] = useState<Record<string, string>>({
    id:                 initial?.id || '',
    volume:             String(initial?.volume || 1),
    species_index:      String(initial?.species_index || ''),
    vn_name:            initial?.vn_name || '',
    scientific_name:    initial?.scientific_name || '',
    authorship:         initial?.authorship || '',
    tax_class_vn:       initial?.tax_class_vn || '',
    tax_class_latin:    initial?.tax_class_latin || '',
    tax_order_vn:       initial?.tax_order_vn || '',
    tax_order_latin:    initial?.tax_order_latin || '',
    tax_family_vn:      initial?.tax_family_vn || '',
    tax_family_latin:   initial?.tax_family_latin || '',
    tax_genus_vn:       initial?.tax_genus_vn || '',
    tax_genus_latin:    initial?.tax_genus_latin || '',
    vn_alternate_names: initial?.vn_alternate_names || '',
    vn_size:            initial?.vn_size || '',
    vn_distribution:    initial?.vn_distribution || '',
    vn_specimen:        initial?.vn_specimen || '',
    vn_status:          initial?.vn_status || '',
    vn_literature:      initial?.vn_literature || '',
    en_common_name:     initial?.en_common_name || '',
    en_size:            initial?.en_size || '',
    en_distribution:    initial?.en_distribution || '',
    en_specimen:        initial?.en_specimen || '',
    en_status:          initial?.en_status || '',
    en_literature:      initial?.en_literature || '',
    morphology_vn:      (initial as unknown as Record<string, string>)?.morphology_vn || '',
    morphology_en:      (initial as unknown as Record<string, string>)?.morphology_en || '',
    ecology_vn:         (initial as unknown as Record<string, string>)?.ecology_vn || '',
    ecology_en:         (initial as unknown as Record<string, string>)?.ecology_en || '',
    economic_value_vn:  (initial as unknown as Record<string, string>)?.economic_value_vn || '',
    economic_value_en:  (initial as unknown as Record<string, string>)?.economic_value_en || '',
    // WoRMS & Biology editable fields
    worms_status:        initial?.worms_status || '',
    worms_accepted_name: initial?.worms_accepted_name || '',
    worms_id:            initial?.worms_id ? String(initial.worms_id) : '',
    bio_iucnStatus:      bio.iucnStatus || '',
    bio_vnRedListStatus: bio.vnRedList?.status || '',
    bio_vnRedListRefCode: bio.vnRedList?.refCode || '',
    bio_maxLength:       bio.maxLength || '',
    bio_maxWeight:       bio.maxWeight || '',
    bio_dangerous:       bio.dangerous || '',
    bio_habitat:         bio.habitat || '',
    bio_habitatVn:       bio.habitatVn || '',
  })

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  const handleAddSynonym = () => {
    const trimmed = newSynonym.trim()
    if (!trimmed) return
    if (!synonymsList.includes(trimmed)) {
      setSynonymsList(list => [...list, trimmed])
    }
    setNewSynonym('')
  }

  const handleRemoveSynonym = (synToRemove: string) => {
    setSynonymsList(list => list.filter(s => s !== synToRemove))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMsg(null)
    setSaving(true)

    const payload: Record<string, unknown> = {
      ...form,
      volume: parseInt(form.volume) || 1,
      species_index: form.species_index ? parseInt(form.species_index) : null,
      collection_id: collection,
    }

    const id = initial?.id
    if (id) {
      delete payload.id
      payload.worms_status = form.worms_status || null
      payload.worms_accepted_name = form.worms_accepted_name || null
      payload.worms_id = form.worms_id ? parseInt(form.worms_id) : null
      payload.synonyms = synonymsList.length > 0 ? synonymsList : null

      const bioEdits: Record<string, unknown> = {
        iucnStatus: form.bio_iucnStatus || null,
        vnRedListStatus: form.bio_vnRedListStatus || null,
        vnRedListRefCode: form.bio_vnRedListRefCode || null,
        maxLength: form.bio_maxLength || null,
        maxWeight: form.bio_maxWeight || null,
        dangerous: form.bio_dangerous || null,
        habitat: form.bio_habitat || null,
        habitatVn: form.bio_habitatVn || null,
      }
      payload._biology_edits = bioEdits
    }

    // Clean form-internal helper keys
    delete payload.bio_iucnStatus
    delete payload.bio_vnRedListStatus
    delete payload.bio_vnRedListRefCode
    delete payload.bio_maxLength
    delete payload.bio_maxWeight
    delete payload.bio_dangerous
    delete payload.bio_habitat
    delete payload.bio_habitatVn

    // Client-side Zod Schema Verification
    const validator = id ? speciesUpdateSchema : speciesCreateSchema
    const check = validator.safeParse(payload)
    if (!check.success) {
      const fieldErrors = check.error.flatten().fieldErrors as Record<string, string[] | undefined>
      const firstField = Object.keys(fieldErrors)[0]
      const firstMsg = fieldErrors[firstField]?.[0] || 'Dữ liệu không hợp lệ theo Zod schema'
      setErrorMsg(`Lỗi Zod schema [${firstField}]: ${firstMsg}`)
      setSaving(false)
      return
    }

    const ok = await onSave(payload, id)
    if (!ok) setSaving(false)
  }

  const TABS: { key: Tab; label: React.ReactNode }[] = [
    { key: 'basic', label: <><ClipboardList size={16} /> Cơ bản</> },
    { key: 'taxonomy', label: <><Leaf size={16} /> Phân loại</> },
    { key: 'vn', label: <><Globe size={16} /> Tiếng Việt</> },
    { key: 'en', label: <><BookOpen size={16} /> English</> },
    ...(initial?.id ? [
      { key: 'sync' as Tab, label: <><Database size={16} /> Đồng bộ</> },
      { key: 'photo' as Tab, label: <><Camera size={16} /> Ảnh</> },
    ] : []),
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
          {errorMsg && (
            <div style={{ margin: '0.5rem 1.5rem 0.5rem', padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#dc2626', fontSize: '0.85rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>⚠️</span>
              <span>{errorMsg}</span>
            </div>
          )}

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
                <DistributionEditor
                  label="Phân bố địa lý (Việt Nam & Thế giới)"
                  value={form.vn_distribution || ''}
                  onChange={(val) => setForm(f => ({ ...f, vn_distribution: val }))}
                  lang="vn"
                />
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

            {/* Tab: Đồng bộ (Frontend-Backend Parity) */}
            {tab === 'sync' && initial?.id && (
              <div className="sync-tab-container">
                {/* Vùng 1: Chỉnh sửa được */}
                <div className="sync-section">
                  <div className="sync-section-header">
                    <span className="sync-section-title">
                      ⚙️ Dữ liệu danh pháp &amp; Sinh học có thể hiệu chỉnh
                    </span>
                    <span className="sync-badge sync-badge--editable">Sửa được</span>
                  </div>

                  <div className="form-grid">
                    <div className="form-field">
                      <label className="form-label" htmlFor="field-worms_status">Trạng thái WoRMS</label>
                      <select
                        id="field-worms_status"
                        className="form-input admin-select"
                        name="worms_status"
                        value={form.worms_status}
                        onChange={onChange}
                      >
                        <option value="">-- Chưa đối soát / Trống --</option>
                        <option value="accepted">accepted (Hợp lệ)</option>
                        <option value="synonym">synonym (Đồng danh)</option>
                        <option value="unresolved">unresolved (Chưa giải quyết)</option>
                        <option value="not_found">not_found (Không tìm thấy)</option>
                      </select>
                    </div>

                    <Field
                      label="Tên hợp lệ theo WoRMS (worms_accepted_name)"
                      name="worms_accepted_name"
                      value={form.worms_accepted_name}
                      onChange={onChange}
                    />

                    <Field
                      label="WoRMS AphiaID (worms_id)"
                      name="worms_id"
                      value={form.worms_id}
                      onChange={onChange}
                    />

                    <div className="form-field">
                      <label className="form-label" htmlFor="field-bio_iucnStatus">Tình trạng bảo tồn (IUCN Red List)</label>
                      <select
                        id="field-bio_iucnStatus"
                        className="form-input admin-select"
                        name="bio_iucnStatus"
                        value={form.bio_iucnStatus}
                        onChange={onChange}
                      >
                        <option value="">-- Chưa đánh giá / Trống --</option>
                        <option value="EX">EX — Tuyệt chủng (Extinct)</option>
                        <option value="EW">EW — Tuyệt chủng ngoài tự nhiên (Extinct in the Wild)</option>
                        <option value="CR">CR — Cực kỳ nguy cấp (Critically Endangered)</option>
                        <option value="EN">EN — Nguy cấp (Endangered)</option>
                        <option value="VU">VU — Sắp nguy cấp (Vulnerable)</option>
                        <option value="NT">NT — Sắp bị đe dọa (Near Threatened)</option>
                        <option value="LC">LC — Ít quan tâm (Least Concern)</option>
                        <option value="DD">DD — Thiếu dữ liệu (Data Deficient)</option>
                        <option value="NE">NE — Chưa đánh giá (Not Evaluated)</option>
                      </select>
                    </div>

                    <div className="form-field">
                      <label className="form-label" htmlFor="field-bio_vnRedListStatus">Danh Lục Đỏ Việt Nam (VAST 2024)</label>
                      <select
                        id="field-bio_vnRedListStatus"
                        className="form-input admin-select"
                        name="bio_vnRedListStatus"
                        value={form.bio_vnRedListStatus}
                        onChange={onChange}
                      >
                        <option value="">-- Chưa có trong SĐVN / Trống --</option>
                        <option value="CR">CR — Cực kỳ nguy cấp</option>
                        <option value="EN">EN — Nguy cấp</option>
                        <option value="VU">VU — Sắp nguy cấp</option>
                        <option value="NT">NT — Gần bị đe dọa</option>
                        <option value="LC">LC — Ít quan tâm</option>
                        <option value="DD">DD — Thiếu dữ liệu</option>
                      </select>
                    </div>

                    <Field
                      label="Mã hồ sơ Danh Lục Đỏ VN (refCode, VD: FS45)"
                      name="bio_vnRedListRefCode"
                      value={form.bio_vnRedListRefCode}
                      onChange={onChange}
                    />

                    <Field
                      label="Kích thước tối đa (maxLength)"
                      name="bio_maxLength"
                      value={form.bio_maxLength}
                      onChange={onChange}
                    />

                    <Field
                      label="Trọng lượng tối đa (maxWeight)"
                      name="bio_maxWeight"
                      value={form.bio_maxWeight}
                      onChange={onChange}
                    />

                    <div className="form-field">
                      <label className="form-label" htmlFor="field-bio_dangerous">Mức độ nguy hiểm / Độc tính (dangerous)</label>
                      <select
                        id="field-bio_dangerous"
                        className="form-input admin-select"
                        name="bio_dangerous"
                        value={form.bio_dangerous}
                        onChange={onChange}
                      >
                        <option value="">-- Không rõ / Trống --</option>
                        <option value="harmless">harmless (Vô hại)</option>
                        <option value="traumatogenic">traumatogenic (Gây tổn thương / cắn / húc)</option>
                        <option value="venomous">venomous (Tiết nọc độc / gai độc)</option>
                        <option value="poisonous">poisonous (Nội tạng / thịt có độc tố)</option>
                        <option value="other">other (Khác)</option>
                      </select>
                    </div>
                  </div>

                  {/* Synonyms Chip Editor */}
                  <div className="form-field synonyms-chip-editor">
                    <label className="form-label">Tên đồng danh (Synonyms)</label>
                    <div className="synonyms-chips">
                      {synonymsList.length === 0 ? (
                        <span style={{ fontSize: '0.8rem', color: 'var(--color-muted)' }}>Chưa có tên đồng danh</span>
                      ) : (
                        synonymsList.map(s => (
                          <span key={s} className="synonyms-chip">
                            {s}
                            <button
                              type="button"
                              className="synonyms-chip-remove"
                              onClick={() => handleRemoveSynonym(s)}
                              title={`Xóa ${s}`}
                            >
                              <X size={13} />
                            </button>
                          </span>
                        ))
                      )}
                    </div>
                    <div className="synonyms-input-row">
                      <input
                        type="text"
                        className="form-input"
                        placeholder="Nhập tên đồng danh (VD: Pterois miles)..."
                        value={newSynonym}
                        onChange={e => setNewSynonym(e.target.value)}
                        onKeyDown={e => {
                          if (e.key === 'Enter') {
                            e.preventDefault()
                            handleAddSynonym()
                          }
                        }}
                      />
                      <button
                        type="button"
                        className="btn btn-outline"
                        style={{ padding: '0 0.85rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                        onClick={handleAddSynonym}
                      >
                        <Plus size={14} /> Thêm
                      </button>
                    </div>
                  </div>

                  {/* Sinh cảnh VN / EN */}
                  <div className="form-grid">
                    <Field
                      label="Sinh cảnh (Tiếng Việt - habitatVn)"
                      name="bio_habitatVn"
                      value={form.bio_habitatVn}
                      onChange={onChange}
                      textarea
                    />
                    <Field
                      label="Sinh cảnh (English - habitat)"
                      name="bio_habitat"
                      value={form.bio_habitat}
                      onChange={onChange}
                      textarea
                    />
                  </div>
                </div>

                {/* Vùng 2: Dữ liệu nguồn đọc được (Read-only) */}
                <div className="sync-section">
                  <div className="sync-section-header">
                    <span className="sync-section-title">
                      📖 Dữ liệu tham chiếu &amp; Tri thức mở rộng
                    </span>
                    <span className="sync-badge sync-badge--readonly">Chỉ đọc (Read-only)</span>
                  </div>

                  <div className="sync-readonly-grid">
                    {/* Card 1: Nguồn dữ liệu & Metadata */}
                    <div className="sync-readonly-card">
                      <div className="sync-readonly-card__title">📡 Nguồn &amp; Danh pháp mở rộng</div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Nguồn dữ liệu:</span>
                        <span className="sync-readonly-val">{bio.source || <span className="sync-readonly-val--empty">Không có</span>}</span>
                      </div>
                      {bio.fbSpecCode && (
                        <div className="sync-readonly-field">
                          <span className="sync-readonly-label">FishBase ID / Tên:</span>
                          <span className="sync-readonly-val">#{bio.fbSpecCode} — {bio.fbName || ''}</span>
                        </div>
                      )}
                      {bio.algaebaseId && (
                        <div className="sync-readonly-field">
                          <span className="sync-readonly-label">AlgaeBase ID:</span>
                          <span className="sync-readonly-val">#{bio.algaebaseId}</span>
                        </div>
                      )}
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">WoRMS LSID:</span>
                        <span className="sync-readonly-val">{initial.worms_lsid || <span className="sync-readonly-val--empty">Chưa có LSID</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Thời điểm sync WoRMS:</span>
                        <span className="sync-readonly-val">{initial.worms_synced_at ? new Date(initial.worms_synced_at).toLocaleString('vi-VN') : <span className="sync-readonly-val--empty">Chưa đồng bộ</span>}</span>
                      </div>
                    </div>

                    {/* Card 2: Sinh thái & Dinh dưỡng */}
                    <div className="sync-readonly-card">
                      <div className="sync-readonly-card__title">🌿 Sinh thái &amp; Dinh dưỡng</div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Kiểu dinh dưỡng:</span>
                        <span className="sync-readonly-val">{bio.feedingType || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Bậc dinh dưỡng (Trophic Level):</span>
                        <span className="sync-readonly-val">{bio.trophicLevel ? String(bio.trophicLevel) : <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Độ sâu sinh sống:</span>
                        <span className="sync-readonly-val">{bio.depthVn || bio.depth || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Tuổi thọ:</span>
                        <span className="sync-readonly-val">{bio.longevity || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                    </div>

                    {/* Card 3: Sinh sản & Tập tính */}
                    <div className="sync-readonly-card">
                      <div className="sync-readonly-card__title">🐣 Sinh sản &amp; Tập tính</div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Hình thức sinh sản:</span>
                        <span className="sync-readonly-val">{bio.reproduction || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Tập tính đẻ trứng:</span>
                        <span className="sync-readonly-val">{bio.spawning || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Gom đàn đẻ trứng:</span>
                        <span className="sync-readonly-val">{bio.spawnAggregation || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Chăm sóc con non:</span>
                        <span className="sync-readonly-val">{bio.parentalCare || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                    </div>

                    {/* Card 4: Kinh tế & Mức độ tổn thương */}
                    <div className="sync-readonly-card">
                      <div className="sync-readonly-card__title">💎 Giá trị kinh tế &amp; Tổn thương</div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Tầm quan trọng thương mại:</span>
                        <span className="sync-readonly-val">{bio.importanceVn || bio.importance || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Nuôi trồng thủy sản:</span>
                        <span className="sync-readonly-val">{bio.aquaculture || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Mức giá thị trường:</span>
                        <span className="sync-readonly-val">{bio.priceCategory || <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                      <div className="sync-readonly-field">
                        <span className="sync-readonly-label">Độ tổn thương (Vulnerability):</span>
                        <span className="sync-readonly-val">{bio.vulnerability ? String(bio.vulnerability) : <span className="sync-readonly-val--empty">Chưa có</span>}</span>
                      </div>
                    </div>

                    {/* Card: Danh Lục Đỏ Việt Nam (VAST 2024) */}
                    {bio.vnRedList && (
                      <div className="sync-readonly-card">
                        <div className="sync-readonly-card__title">🇻🇳 Danh Lục Đỏ Việt Nam (VAST 2024)</div>
                        <div className="sync-readonly-field">
                          <span className="sync-readonly-label">Phân hạng bảo tồn:</span>
                          <span className="sync-readonly-val">
                            {bio.vnRedList.status ? `${bio.vnRedList.status} — ${bio.vnRedList.statusVn || ''}` : <span className="sync-readonly-val--empty">Chưa có</span>}
                          </span>
                        </div>
                        {bio.vnRedList.refCode && (
                          <div className="sync-readonly-field">
                            <span className="sync-readonly-label">Mã hồ sơ:</span>
                            <span className="sync-readonly-val">{bio.vnRedList.refCode}</span>
                          </div>
                        )}
                        {bio.vnRedList.assessor && (
                          <div className="sync-readonly-field">
                            <span className="sync-readonly-label">Người đánh giá:</span>
                            <span className="sync-readonly-val">{bio.vnRedList.assessor}</span>
                          </div>
                        )}
                        {bio.vnRedList.threats && (
                          <div className="sync-readonly-field">
                            <span className="sync-readonly-label">Mối đe dọa:</span>
                            <span className="sync-readonly-val" style={{ fontSize: '0.8rem', lineHeight: 1.4 }}>{bio.vnRedList.threats}</span>
                          </div>
                        )}
                        {bio.vnRedList.conservation && (
                          <div className="sync-readonly-field">
                            <span className="sync-readonly-label">Biện pháp bảo tồn:</span>
                            <span className="sync-readonly-val" style={{ fontSize: '0.8rem', lineHeight: 1.4 }}>{bio.vnRedList.conservation}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Card 5: Ghi chú & Tóm tắt sinh học */}
                  {(bio.biologySummaryVn || bio.biologySummary || bio.ecologyNotesVn || bio.ecologyNotes || bio.morphDescriptionVn || bio.morphDescription) && (
                    <div className="sync-readonly-card">
                      <div className="sync-readonly-card__title">📝 Tóm tắt &amp; Ghi chú học thuật</div>
                      {(bio.biologySummaryVn || bio.biologySummary) && (
                        <div className="sync-readonly-field">
                          <span className="sync-readonly-label">Tóm tắt sinh học:</span>
                          <span className="sync-readonly-val">{bio.biologySummaryVn || bio.biologySummary}</span>
                        </div>
                      )}
                      {(bio.ecologyNotesVn || bio.ecologyNotes) && (
                        <div className="sync-readonly-field">
                          <span className="sync-readonly-label">Ghi chú sinh thái:</span>
                          <span className="sync-readonly-val">{bio.ecologyNotesVn || bio.ecologyNotes}</span>
                        </div>
                      )}
                      {(bio.morphDescriptionVn || bio.morphDescription) && (
                        <div className="sync-readonly-field">
                          <span className="sync-readonly-label">Mô tả hình thái chuyên sâu:</span>
                          <span className="sync-readonly-val">{bio.morphDescriptionVn || bio.morphDescription}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Card 6: Độc học lâm sàng (nếu có dữ liệu từ sinh-vat-doc) */}
                  {bio.toxicology && (
                    <div className="sync-readonly-card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}>
                      <div className="sync-readonly-card__title" style={{ color: '#ef4444' }}>⚠️ Độc học lâm sàng &amp; Cấp cứu</div>
                      {bio.toxicology.toxinType && (
                        <div className="sync-readonly-field">
                          <span className="sync-readonly-label">Loại độc tố:</span>
                          <span className="sync-readonly-val">{String(bio.toxicology.toxinType)}</span>
                        </div>
                      )}
                      {bio.toxicology.mechanism && (
                        <div className="sync-readonly-field">
                          <span className="sync-readonly-label">Cơ chế tác động:</span>
                          <span className="sync-readonly-val">{String(bio.toxicology.mechanism)}</span>
                        </div>
                      )}
                      {bio.toxicology.firstAidProtocol && (
                        <div className="sync-readonly-field">
                          <span className="sync-readonly-label">Phác đồ sơ cứu:</span>
                          <span className="sync-readonly-val">{String(bio.toxicology.firstAidProtocol)}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
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

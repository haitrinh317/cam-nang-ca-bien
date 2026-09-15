'use client'

import { useState } from 'react'
import {
  Network,
  ShieldCheck,
  BookOpen,
  CornerDownRight,
  Dna,
  Layers,
} from 'lucide-react'
import WormsBadge from '../WormsBadge'
import { formatSynonym, cleanTaxonHierarchy } from '@/lib/species-parsers'
import { stripRankPrefix } from '@/lib/taxonomy'
import type { Species } from '../SpecimenCard'

export interface TaxCrumb {
  rank: string
  rankKey: 'class' | 'order' | 'family' | 'genus'
  vn: string
  lat: string | null
}

interface PhanloaiTabProps {
  sp: Species
  syns: string[]
  crumbs: TaxCrumb[]
  cleanAuthor: string
}

export default function PhanloaiTab({ sp, syns, crumbs, cleanAuthor }: PhanloaiTabProps) {
  const wt = sp.biology?.wormsTaxonomy
  const hasModernTax = Boolean(wt && wt.order && wt.family)
  const [taxMode, setTaxMode] = useState<'modern' | 'classic'>(hasModernTax ? 'modern' : 'classic')

  // Clean WoRMS modern taxonomy ranks to avoid "Lớp Lớp...", "Bộ Bộ..."
  const modernClass = cleanTaxonHierarchy('Lớp', wt?.classVn, wt?.class)
  const modernOrder = cleanTaxonHierarchy('Bộ', wt?.orderVn, wt?.order)
  const modernFamily = cleanTaxonHierarchy('Họ', wt?.familyVn, wt?.family)
  const modernGenus = cleanTaxonHierarchy('Chi', wt?.genusVn, wt?.genus)

  // Book taxonomy crumbs
  const bookClassRaw = crumbs.find(c => c.rankKey === 'class')
  const bookOrderRaw = crumbs.find(c => c.rankKey === 'order')
  const bookFamilyRaw = crumbs.find(c => c.rankKey === 'family')
  const bookGenusRaw = crumbs.find(c => c.rankKey === 'genus')

  const bookClass = cleanTaxonHierarchy('Lớp', bookClassRaw?.vn || sp.tax_class_vn, bookClassRaw?.lat || sp.tax_class_latin)
  const bookOrder = cleanTaxonHierarchy('Bộ', bookOrderRaw?.vn || sp.tax_order_vn, bookOrderRaw?.lat || sp.tax_order_latin)
  const bookFamily = cleanTaxonHierarchy('Họ', bookFamilyRaw?.vn || sp.tax_family_vn, bookFamilyRaw?.lat || sp.tax_family_latin)
  const bookGenus = cleanTaxonHierarchy(sp.collection_id === 'thuc-vat-bien' ? 'Chi' : 'Giống', bookGenusRaw?.vn || sp.tax_genus_vn, bookGenusRaw?.lat || sp.tax_genus_latin)

  // Build active stepped crumbs according to taxMode
  const activeCrumbs: TaxCrumb[] = (taxMode === 'modern' && wt) ? [
    { rank: 'Lớp', rankKey: 'class' as const, vn: modernClass.vn, lat: modernClass.lat },
    { rank: 'Bộ', rankKey: 'order' as const, vn: modernOrder.vn, lat: modernOrder.lat },
    { rank: 'Họ', rankKey: 'family' as const, vn: modernFamily.vn, lat: modernFamily.lat },
    { rank: 'Chi', rankKey: 'genus' as const, vn: modernGenus.vn, lat: modernGenus.lat },
  ] : [
    { rank: 'Lớp', rankKey: 'class' as const, vn: bookClass.vn, lat: bookClass.lat },
    { rank: 'Bộ', rankKey: 'order' as const, vn: bookOrder.vn, lat: bookOrder.lat },
    { rank: 'Họ', rankKey: 'family' as const, vn: bookFamily.vn, lat: bookFamily.lat },
    { rank: sp.collection_id === 'thuc-vat-bien' ? 'Chi' : 'Giống', rankKey: 'genus' as const, vn: bookGenus.vn, lat: bookGenus.lat },
  ].filter(c => c.vn || c.lat)

  return (
    <div
      id="tab-panel-phanloai"
      role="tabpanel"
      aria-labelledby="tab-phanloai"
      className="detail-tab-panel active"
    >
      <div className="specimen-phanloai-container">
        {/* 1. Hệ thống Phân loại học (Taxonomic Stepped Tree) */}
        <div className="specimen-bento-card specimen-tax-lineage-card">
          <div className="specimen-bento-card__header">
            <div className="specimen-bento-card__title-group">
              <span className="specimen-bento-card__icon specimen-bento-card__icon--blue">
                <Network size={16} />
              </span>
              <div>
                <h3 className="specimen-bento-card__title">Cây Phân loại học</h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-muted)', display: 'block', marginTop: '2px' }}>
                  {taxMode === 'modern' ? 'Theo Chuẩn Phát sinh Chủng loài WoRMS 2026' : 'Theo Sách Chuyên khảo Viện Hải dương học'}
                </span>
              </div>
            </div>
            <span className="specimen-bento-card__badge">
              {activeCrumbs.length + 1} bậc phân loại
            </span>
          </div>

          {/* Dual Taxonomy Switcher (nếu có dữ liệu WoRMS) */}
          {hasModernTax && (
            <div className="dual-tax-controls">
              <div className="dual-tax-switcher" role="tablist" aria-label="Hệ thống phân loại">
                <button
                  type="button"
                  className={`dual-tax-btn ${taxMode === 'modern' ? 'active' : ''}`}
                  onClick={() => setTaxMode('modern')}
                  title="Hệ thống phát sinh chủng loài phân tử cập nhật mới nhất"
                >
                  <Dna size={14} />
                  <span>WoRMS Hiện Đại</span>
                </button>
                <button
                  type="button"
                  className={`dual-tax-btn ${taxMode === 'classic' ? 'active--classic' : ''}`}
                  onClick={() => setTaxMode('classic')}
                  title="Trật tự phân loại gốc theo bộ sách Danh mục Cá biển VN"
                >
                  <BookOpen size={14} />
                  <span>Sách Chuyên Khảo</span>
                </button>
              </div>

              <span style={{ fontSize: '0.78rem', color: 'var(--color-muted)' }}>
                {taxMode === 'modern' ? 'Phân loại học phân tử' : 'Hình thái học truyền thống'}
              </span>
            </div>
          )}

          {/* Stepped Tree Lineage */}
          <div className="tax-tree-container">
            {activeCrumbs.map((c, idx) => (
              <div
                key={c.rankKey}
                className={`tax-tree-node tax-tree-node--${c.rankKey}`}
                data-level={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '4px 8px',
                  marginLeft: `calc(${idx} * var(--tax-indent, 24px))`
                }}
              >
                {idx > 0 && (
                  <span className="tax-tree-branch" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                    <CornerDownRight size={14} />
                  </span>
                )}
                <span className={`rank-badge rank-${c.rankKey}`}>
                  {c.rank}
                </span>
                <span
                  className="tax-tree-vn"
                  style={{
                    fontSize: '0.95rem',
                    fontWeight: 600,
                    fontStyle: c.lat && c.lat.toLowerCase() === c.vn.toLowerCase() ? 'italic' : 'normal'
                  }}
                >
                  {c.vn}
                </span>
                {c.lat && c.lat.toLowerCase() !== c.vn.toLowerCase() && (
                  <em
                    className="tax-tree-lat"
                    style={{
                      fontSize: '0.88rem',
                      fontStyle: 'italic'
                    }}
                  >
                    ({c.lat})
                  </em>
                )}
              </div>
            ))}

            {/* Bậc Loài cuối cùng (Current Target Specimen) */}
            <div
              className="tax-tree-node tax-tree-node--species tax-tree-node--current"
              data-level={activeCrumbs.length}
              style={{
                display: 'flex',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '4px 8px',
                marginLeft: `calc(${activeCrumbs.length} * var(--tax-indent, 24px))`
              }}
            >
              <span className="tax-tree-branch tax-tree-branch--current" aria-hidden="true" style={{ display: 'inline-flex', alignItems: 'center' }}>
                <CornerDownRight size={16} />
              </span>
              <span className="rank-badge rank-species">
                Loài
              </span>
              <span
                className="tax-tree-vn tax-tree-vn--current"
                style={{
                  fontSize: '0.98rem',
                  fontWeight: 600
                }}
              >
                {stripRankPrefix(sp.vn_name)}
              </span>
              <em
                className="tax-tree-lat tax-tree-lat--current"
                style={{
                  fontSize: '0.92rem',
                  fontStyle: 'italic',
                  fontWeight: 600
                }}
              >
                {sp.scientific_name}
              </em>
              {cleanAuthor && (
                <span
                  className="tax-tree-author"
                  style={{
                    fontSize: '0.82rem'
                  }}
                >
                  {' '}{cleanAuthor}
                </span>
              )}
            </div>
          </div>

          {/* Bảng Đối Chiếu Cây Phân Loại Kép (Dual Taxonomy Comparison Table) */}
          {hasModernTax && wt && (
            <div className="dual-tax-comparison-grid">
              <div className="dual-tax-card dual-tax-card--modern">
                <div className="dual-tax-card__title">
                  <Dna size={14} /> Chuẩn Hiện Đại (WoRMS 2026)
                </div>
                <div className="dual-tax-row">
                  <span className="dual-tax-label">Lớp:</span>
                  <span className="dual-tax-val">
                    {modernClass.vn}
                    {modernClass.lat && modernClass.lat.toLowerCase() !== modernClass.vn.toLowerCase() && (
                      <em> ({modernClass.lat})</em>
                    )}
                  </span>
                </div>
                <div className="dual-tax-row">
                  <span className="dual-tax-label">Bộ:</span>
                  <span className="dual-tax-val">
                    {modernOrder.vn}
                    {modernOrder.lat && modernOrder.lat.toLowerCase() !== modernOrder.vn.toLowerCase() && (
                      <em> ({modernOrder.lat})</em>
                    )}
                  </span>
                </div>
                <div className="dual-tax-row">
                  <span className="dual-tax-label">Họ:</span>
                  <span className="dual-tax-val">
                    {modernFamily.vn}
                    {modernFamily.lat && modernFamily.lat.toLowerCase() !== modernFamily.vn.toLowerCase() && (
                      <em> ({modernFamily.lat})</em>
                    )}
                  </span>
                </div>
                <div className="dual-tax-row">
                  <span className="dual-tax-label">Chi:</span>
                  <span className="dual-tax-val">
                    <span style={{ fontStyle: modernGenus.lat && modernGenus.lat.toLowerCase() === modernGenus.vn.toLowerCase() ? 'italic' : 'normal' }}>
                      {modernGenus.vn}
                    </span>
                    {modernGenus.lat && modernGenus.lat.toLowerCase() !== modernGenus.vn.toLowerCase() && (
                      <em> ({modernGenus.lat})</em>
                    )}
                  </span>
                </div>
              </div>

              <div className="dual-tax-card dual-tax-card--classic">
                <div className="dual-tax-card__title">
                  <BookOpen size={14} /> Sách Gốc (Viện Hải dương học)
                </div>
                <div className="dual-tax-row">
                  <span className="dual-tax-label">Lớp:</span>
                  <span className="dual-tax-val">
                    {bookClass.vn || bookClass.lat || '—'}
                    {bookClass.lat && bookClass.lat.toLowerCase() !== (bookClass.vn || '').toLowerCase() && (
                      <em> ({bookClass.lat})</em>
                    )}
                  </span>
                </div>
                <div className="dual-tax-row">
                  <span className="dual-tax-label">Bộ:</span>
                  <span className="dual-tax-val">
                    {bookOrder.vn || bookOrder.lat || '—'}
                    {bookOrder.lat && bookOrder.lat.toLowerCase() !== (bookOrder.vn || '').toLowerCase() && (
                      <em> ({bookOrder.lat})</em>
                    )}
                  </span>
                </div>
                <div className="dual-tax-row">
                  <span className="dual-tax-label">Họ:</span>
                  <span className="dual-tax-val">
                    {bookFamily.vn || bookFamily.lat || '—'}
                    {bookFamily.lat && bookFamily.lat.toLowerCase() !== (bookFamily.vn || '').toLowerCase() && (
                      <em> ({bookFamily.lat})</em>
                    )}
                  </span>
                </div>
                <div className="dual-tax-row">
                  <span className="dual-tax-label">{sp.collection_id === 'thuc-vat-bien' ? 'Chi:' : 'Giống:'}</span>
                  <span className="dual-tax-val">
                    <span style={{ fontStyle: bookGenus.lat && bookGenus.lat.toLowerCase() === (bookGenus.vn || '').toLowerCase() ? 'italic' : 'normal' }}>
                      {bookGenus.vn || bookGenus.lat || '—'}
                    </span>
                    {bookGenus.lat && bookGenus.lat.toLowerCase() !== (bookGenus.vn || '').toLowerCase() && (
                      <em> ({bookGenus.lat})</em>
                    )}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 2. Thẩm Định Danh Pháp Quốc Tế (WoRMS Curatorial Dossier) */}
        {(sp.worms_id || sp.worms_status) && (
          <div className="specimen-bento-card specimen-worms-dossier-card">
            <div className="specimen-bento-card__header">
              <div className="specimen-bento-card__title-group">
                <span className="specimen-bento-card__icon specimen-bento-card__icon--emerald">
                  <ShieldCheck size={16} />
                </span>
                <div>
                  <h3 className="specimen-bento-card__title" style={{ fontSize: 'var(--text-lg, 1.15rem)' }}>
                    Hồ sơ Thẩm định Danh pháp Quốc tế
                  </h3>
                  <span style={{ fontSize: 'var(--text-xs, 0.85rem)', color: 'var(--color-ink-3, #64748b)', fontWeight: 500, display: 'block', marginTop: '2px' }}>
                    World Register of Marine Species (WoRMS)
                  </span>
                </div>
              </div>
            </div>

            <div className="worms-dossier-grid" style={{ marginTop: '6px' }}>
              {/* Tile 1: Trạng thái danh pháp */}
              <div className="worms-tile">
                <span className="worms-tile__label">
                  Trạng thái danh pháp
                </span>
                <div style={{ display: 'flex', alignItems: 'center', minHeight: '26px' }}>
                  <WormsBadge
                    worms_status={sp.worms_status}
                    worms_id={sp.worms_id}
                    worms_accepted_name={sp.worms_accepted_name}
                    worms_synced_at={sp.worms_synced_at}
                  />
                </div>
                <span className="worms-tile__sub">
                  {(sp.worms_status?.toLowerCase() === 'accepted' || sp.worms_status?.toLowerCase() === 'valid')
                    ? 'Tên hợp lệ được công nhận toàn cầu trong CSDL sinh vật biển'
                    : (sp.worms_status?.toLowerCase().includes('synonym')
                      ? 'Danh pháp đồng nghĩa (tên phân loại cũ trong lịch sử)'
                      : 'Dữ liệu đối soát phân loại học')}
                </span>
              </div>

              {/* Tile 2: Mã số AphiaID */}
              {sp.worms_id && (
                <div className="worms-tile">
                  <span className="worms-tile__label">
                    Mã định danh Quốc tế (AphiaID)
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', minHeight: '26px' }}>
                    <code
                      style={{
                        fontFamily: 'var(--font-outlier, monospace)',
                        fontSize: 'var(--text-base, 1.05rem)',
                        fontWeight: 700,
                        color: 'var(--color-ink, #0b1329)',
                        background: 'rgba(11, 19, 41, 0.05)',
                        padding: '2px 8px',
                        borderRadius: '4px'
                      }}
                    >
                      #{sp.worms_id}
                    </code>
                  </div>
                  <span className="worms-tile__sub">
                    Mã số tra cứu định danh duy nhất trong CSDL WoRMS
                  </span>
                </div>
              )}

              {/* Tile 3: Danh pháp khoa học hiện hành */}
              <div className="worms-tile">
                <span className="worms-tile__label">
                  Danh pháp khoa học hiện hành được WoRMS công nhận
                </span>
                <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px', minHeight: '26px' }}>
                  <em
                    style={{
                      fontStyle: 'italic',
                      fontWeight: 600,
                      fontSize: '0.98rem',
                      color: 'var(--color-accent, #00d4b8)'
                    }}
                  >
                    {sp.worms_accepted_name || sp.scientific_name}
                  </em>
                  {cleanAuthor && (
                    <span style={{ fontSize: '0.82rem', color: 'var(--color-ink-3, #64748b)' }}>
                      {cleanAuthor}
                    </span>
                  )}
                </div>
                <span className="worms-tile__sub">
                  {sp.worms_accepted_name
                    ? (sp.worms_status?.toLowerCase().includes('synonym')
                      ? 'Tên khoa học chính thức hiện nay (thay thế cho danh pháp cũ)'
                      : 'Danh pháp mô tả ban đầu được bảo lưu hợp lệ')
                    : 'Danh pháp hiện hành bảo toàn theo công bố phân loại'}
                </span>
              </div>

              {/* Tile 4: Thời điểm đồng bộ xác thực */}
              {sp.worms_synced_at && (
                <div className="worms-tile">
                  <span className="worms-tile__label">
                    Thời điểm đồng bộ xác thực
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', minHeight: '26px' }}>
                    <span style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--color-ink, #0b1329)' }}>
                      {sp.worms_synced_at.substring(0, 10)}
                    </span>
                  </div>
                  <span className="worms-tile__sub">
                    Tự động cập nhật qua WoRMS REST API
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 3. Danh pháp đồng nghĩa & Lịch sử mô tả gốc */}
        <div className="specimen-bento-card specimen-synonyms-card">
          <div className="specimen-bento-card__header">
            <div className="specimen-bento-card__title-group">
              <span className="specimen-bento-card__icon specimen-bento-card__icon--purple">
                <BookOpen size={16} />
              </span>
              <h3 className="specimen-bento-card__title" style={{ fontSize: 'var(--text-lg, 1.15rem)' }}>
                Danh pháp đồng nghĩa &amp; Phân loại gốc
              </h3>
            </div>
            {syns.length > 0 && (
              <span className="specimen-bento-card__badge" style={{ fontSize: 'var(--text-xs, 0.85rem)' }}>
                {syns.length} danh pháp ghi nhận
              </span>
            )}
          </div>

          {syns.length > 0 ? (
            <div className="specimen-synonyms-list">
              {syns.map((syn, idx) => {
                const html = formatSynonym(syn)
                if (!html) return null
                return (
                  <div
                    key={idx}
                    className="specimen-synonym-item"
                    style={{
                      display: 'flex',
                      alignItems: 'baseline',
                      gap: '10px',
                      padding: '8px 12px'
                    }}
                  >
                    <span
                      className="specimen-synonym-idx"
                      style={{
                        flexShrink: 0,
                        fontSize: '0.78rem',
                        fontFamily: 'var(--font-outlier, monospace)',
                        fontWeight: 700
                      }}
                    >
                      [{idx + 1}]
                    </span>
                    <div 
                      className="specimen-synonym-text"
                      style={{
                        flex: 1,
                        minWidth: 0,
                        fontSize: '0.82rem',
                        lineHeight: 1.5
                      }}
                      dangerouslySetInnerHTML={{ __html: html }} 
                    />
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="specimen-tax-empty">
              <p className="specimen-tax-empty-text" style={{ fontSize: 'var(--text-sm, 0.95rem)' }}>
                Chưa ghi nhận danh pháp đồng nghĩa. Danh pháp khoa học hiện hành được công nhận trực tiếp từ công bố mô tả gốc ban đầu.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

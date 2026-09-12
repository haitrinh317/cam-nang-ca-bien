'use client'

import React, { useState } from 'react'
import PhotoGallery from './PhotoGallery'
import WormsBadge from './WormsBadge'
import { BiologyData } from './BiologyDashboard'
import { cleanTaxonHierarchy } from '@/lib/species-parsers'
import ThongsoTab from './tabs/ThongsoTab'
import SinhhocTab from './tabs/SinhhocTab'
import PhanloaiTab from './tabs/PhanloaiTab'
import type { TaxCrumb } from './tabs/PhanloaiTab'
import './SpecimenCard.css'

export interface Species {
  id: string
  volume: number
  species_index: number | null
  vn_name: string
  scientific_name: string
  authorship: string | null
  worms_status: string | null
  worms_id: number | null
  worms_accepted_name: string | null
  worms_synced_at: string | null
  tax_class_vn: string | null
  tax_class_latin: string | null
  tax_order_vn: string | null
  tax_order_latin: string | null
  tax_family_vn: string | null
  tax_family_latin: string | null
  tax_genus_vn: string | null
  tax_genus_latin: string | null
  vn_alternate_names: string | null
  vn_size: string | null
  vn_distribution: string | null
  vn_specimen: string | null
  vn_status: string | null
  vn_literature: string | null
  en_common_name: string | null
  en_size: string | null
  en_distribution: string | null
  en_specimen: string | null
  en_status: string | null
  en_literature: string | null
  synonyms: string | string[] | null
  biology: BiologyData | null
  morphology_vn: string | null
  morphology_en: string | null
  ecology_vn: string | null
  ecology_en: string | null
  economic_value_vn: string | null
  economic_value_en: string | null
  photo_place: string | null
  photo_depth: string | null
  photo_date: string | null
  photo_url: string | null
  collection_id: string | null
}

type TabId = 'thongso' | 'sinhhoc' | 'phanloai'

export default function SpecimenCard({ sp, initialPhotos }: { sp: Species; initialPhotos?: unknown[] }) {
  const [active, setActive] = useState<TabId>('thongso')

  // Parse synonyms
  let syns: string[] = []
  try { syns = typeof sp.synonyms === 'string' ? JSON.parse(sp.synonyms) : (sp.synonyms || []) } catch { syns = [] }

  // Parse biology
  let bio: BiologyData | null = null
  try { bio = typeof sp.biology === 'string' ? JSON.parse(sp.biology) : sp.biology } catch { bio = null }

  const cleanAuthor = (sp.authorship || '').replace(/"/g, '').trim()

  // Taxonomy breadcrumb — normalized
  const rawCrumbs = [
    (sp.tax_class_vn || sp.tax_class_latin)   ? { rank: 'Lớp',   rankKey: 'class'  as const, vn: sp.tax_class_vn || sp.tax_class_latin || '',  lat: sp.tax_class_latin }  : null,
    (sp.tax_order_vn || sp.tax_order_latin)   ? { rank: 'Bộ',    rankKey: 'order'  as const, vn: sp.tax_order_vn || sp.tax_order_latin || '',  lat: sp.tax_order_latin }  : null,
    (sp.tax_family_vn || sp.tax_family_latin) ? { rank: 'Họ',    rankKey: 'family' as const, vn: sp.tax_family_vn || (sp.tax_family_latin ? `Họ ${sp.tax_family_latin}` : ''), lat: sp.tax_family_latin } : null,
    (sp.tax_genus_vn || sp.tax_genus_latin)   ? { rank: sp.collection_id === 'thuc-vat-bien' ? 'Chi' : 'Giống', rankKey: 'genus' as const, vn: sp.tax_genus_vn || (sp.tax_genus_latin ? `${sp.collection_id === 'thuc-vat-bien' ? 'Chi' : 'Giống'} ${sp.tax_genus_latin}` : ''),  lat: sp.tax_genus_latin }  : null,
  ].filter(Boolean) as { rank: string; rankKey: 'class' | 'order' | 'family' | 'genus'; vn: string; lat: string | null }[]

  const crumbs: TaxCrumb[] = rawCrumbs.map(c => {
    const cleaned = cleanTaxonHierarchy(c.rank, c.vn, c.lat)
    return { rank: c.rank, rankKey: c.rankKey, vn: cleaned.vn, lat: cleaned.lat }
  })

  const familyCrumb = crumbs.find(c => c.rankKey === 'family')

  const TABS: { id: TabId; label: string }[] = [
    { id: 'thongso',  label: 'Thông số' },
    { id: 'sinhhoc',  label: 'Sinh học' },
    { id: 'phanloai', label: 'Phân loại' },
  ]

  return (
    <div className={`specimen vol-${sp.volume}`}>
      {/* Hero */}
      <header className="specimen__hero">
        <div className="specimen__meta">
          <span className="specimen__index">#{sp.species_index || ''}</span>
          <span className="specimen__vol">
            {sp.collection_id === 'thuc-vat-bien' 
              ? (sp.volume === 2 ? 'Tập II · Rong biển VN (1969)' : 'Tập I · Thực vật phía Nam') 
              : sp.collection_id === 'sinh-vat-doc'
              ? 'Động vật độc biển VN (2018)'
              : `Tập ${sp.volume || ''}`}
          </span>
        </div>
        <h1 className="specimen__name">{sp.vn_name}</h1>
        <div className="specimen__sci-row" style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px 14px', marginTop: '4px', marginBottom: '8px' }}>
          <p className="specimen__sci" style={{ margin: 0, lineHeight: 1.35 }}>
            <em className="specimen__sci-name" style={{ fontStyle: 'italic' }}>{sp.scientific_name}</em>
            {cleanAuthor && <span className="specimen__author" style={{ fontStyle: 'normal', color: 'var(--color-ink-3, #64748b)', marginLeft: '4px' }}> {cleanAuthor}</span>}
          </p>
          <WormsBadge
            worms_status={sp.worms_status}
            worms_id={sp.worms_id}
            worms_accepted_name={sp.worms_accepted_name}
            worms_synced_at={sp.worms_synced_at}
          />
          {bio?.toxicology && (
            <span 
              className="specimen__tox-pill"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                height: '24px',
                padding: '0 10px',
                borderRadius: '9999px',
                fontSize: '0.72rem',
                fontWeight: 700,
                lineHeight: 1,
                backgroundColor: bio.toxicology.danger_level === 'lethal' ? 'rgba(239, 68, 68, 0.12)' : 'rgba(245, 158, 11, 0.12)',
                color: bio.toxicology.danger_level === 'lethal' ? '#dc2626' : '#d97706',
                border: bio.toxicology.danger_level === 'lethal' ? '1px solid rgba(239, 68, 68, 0.35)' : '1px solid rgba(245, 158, 11, 0.35)',
              }}
              title={bio.toxicology.danger_level_vn || 'Sinh vật biển có độc tính'}
            >
              <span style={{ fontSize: '0.82rem' }}>☣️</span>
              <span>{bio.toxicology.danger_level === 'lethal' ? 'Cực độc' : 'Sinh vật độc'}</span>
            </span>
          )}
          {familyCrumb && (
            <span className="specimen__family-pill" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.74rem', color: 'var(--color-ink-3, #64748b)', padding: '2px 8px', borderRadius: '4px', background: 'var(--color-paper-2, #f8fafc)', border: '1px solid var(--color-rule-2, rgba(0,0,0,0.06))' }}>
              <span style={{ fontWeight: 600 }}>Họ {familyCrumb.vn}</span>
              {familyCrumb.lat && <em style={{ fontStyle: 'italic', opacity: 0.85 }}>({familyCrumb.lat})</em>}
            </span>
          )}
        </div>
      </header>

      {/* Photo Gallery */}
      <PhotoGallery
        speciesId={sp.id}
        fallbackUrl={sp.photo_url}
        initialPhotos={initialPhotos as any}
        fallbackCredit={
          (bio as any)?.inaturalist ? {
            photographer: (bio as any).inaturalist.attribution || 'iNaturalist',
            license: (bio as any).inaturalist.license_code,
            sourceUrl: (bio as any).inaturalist.photo_url,
            source: 'iNaturalist'
          } : null
        }
      />

      {/* Tab navigation */}
      <div className="detail-tabs" role="tablist">
        {TABS.map(tab => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={active === tab.id}
            aria-controls={`tab-panel-${tab.id}`}
            id={`tab-${tab.id}`}
            className={`detail-tab${active === tab.id ? ' active' : ''}`}
            onClick={() => setActive(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab panels — deep modules */}
      {active === 'thongso' && <ThongsoTab sp={sp} bio={bio} />}
      {active === 'sinhhoc' && <SinhhocTab bio={bio} speciesId={sp.id} collectionId={sp.collection_id} />}
      {active === 'phanloai' && <PhanloaiTab sp={sp} syns={syns} crumbs={crumbs} cleanAuthor={cleanAuthor} />}
    </div>
  )
}

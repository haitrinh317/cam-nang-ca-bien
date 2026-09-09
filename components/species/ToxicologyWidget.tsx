'use client'

import React from 'react'
import { 
  AlertOctagon, 
  ShieldAlert, 
  Activity, 
  HeartPulse, 
  Sparkles, 
  Camera, 
  BookOpen, 
  CheckCircle2, 
  AlertTriangle,
  Zap
} from 'lucide-react'
import './ToxicologyWidget.css'

export interface ToxicologyData {
  poison_type?: 'contact' | 'ingestion' | 'both' | string
  poison_type_vn?: string
  danger_level?: 'lethal' | 'severe' | 'moderate' | 'mild' | string
  danger_level_vn?: string
  toxin_names?: string[]
  mechanism?: string
  symptoms?: string
  first_aid?: string
  photographer?: string
}

interface ToxicologyWidgetProps {
  toxicology: ToxicologyData
  speciesName?: string
  scientificName?: string
}

export default function ToxicologyWidget({
  toxicology,
  speciesName,
  scientificName
}: ToxicologyWidgetProps) {
  if (!toxicology) return null

  const isLethal = toxicology.danger_level === 'lethal'
  const isSevere = toxicology.danger_level === 'severe'
  
  // Format danger badge
  let badgeClass = 'tox-badge--moderate'
  let defaultLevelLabel = 'Nguy hiểm'
  if (isLethal) {
    badgeClass = 'tox-badge--lethal'
    defaultLevelLabel = 'Cực độc (Nguy cơ tử vong)'
  } else if (isSevere) {
    badgeClass = 'tox-badge--severe'
    defaultLevelLabel = 'Độc mạnh'
  }

  const dangerLabel = toxicology.danger_level_vn || defaultLevelLabel

  // Format poison type badge
  const poisonTypeLabel = toxicology.poison_type_vn || (
    toxicology.poison_type === 'both' 
      ? 'Độc cả Cắn & Ăn phải' 
      : toxicology.poison_type === 'ingestion' 
      ? 'Ngộ độc đường tiêu hóa (Thịt/Nội tạng độc)' 
      : 'Nọc độc châm chích / Tiếp xúc'
  )

  const toxinNames = toxicology.toxin_names || []

  return (
    <section className="tox-widget" aria-label="Hồ sơ độc học và phác đồ cấp cứu">
      {/* ─── Widget Header ─── */}
      <div className="tox-widget__header">
        <div className="tox-widget__title-group">
          <div className="tox-widget__icon-box">
            <AlertOctagon size={24} />
          </div>
          <div className="tox-widget__title-wrap">
            <h3 className="tox-widget__title">
              Hồ Sơ Độc Học &amp; Phác Đồ Cấp Cứu
            </h3>
            <p className="tox-widget__subtitle">
              Chuyên khảo &ldquo;Động vật độc biển Việt Nam&rdquo; — Viện Hải dương học
            </p>
          </div>
        </div>

        <div className="tox-widget__badges">
          <span className={`tox-badge ${badgeClass}`}>
            <AlertTriangle size={13} />
            <span>{dangerLabel}</span>
          </span>
          <span className="tox-badge tox-badge--type">
            <ShieldAlert size={13} />
            <span>{poisonTypeLabel}</span>
          </span>
        </div>
      </div>

      {/* ─── Danh sách Độc tố chính (Toxin Tags) ─── */}
      {toxinNames.length > 0 && (
        <div className="tox-widget__toxins">
          <span className="tox-widget__toxins-label">
            <Sparkles size={14} />
            Độc tố chính nhận diện:
          </span>
          {toxinNames.map((toxin, idx) => (
            <span key={idx} className="tox-pill">
              <Zap size={11} />
              {toxin}
            </span>
          ))}
        </div>
      )}

      {/* ─── Bento Grid Chi Tiết Độc Tính ─── */}
      <div className="tox-widget__grid">
        {/* 1. Cơ chế tác động dược lý / sinh học */}
        {toxicology.mechanism && (
          <div className="tox-card">
            <div className="tox-card__header">
              <span className="tox-card__icon">
                <Activity size={15} />
              </span>
              <span>Cơ chế tác động dược lý &amp; Sinh học</span>
            </div>
            <p className="tox-card__body">{toxicology.mechanism}</p>
          </div>
        )}

        {/* 2. Triệu chứng lâm sàng */}
        {toxicology.symptoms && (
          <div className="tox-card">
            <div className="tox-card__header">
              <span className="tox-card__icon tox-card__icon--danger">
                <HeartPulse size={15} />
              </span>
              <span>Triệu chứng lâm sàng &amp; Diễn biến</span>
            </div>
            <p className="tox-card__body">{toxicology.symptoms}</p>
          </div>
        )}

        {/* 3. Phác đồ xử trí & Sơ cứu khẩn cấp (Hero Card) */}
        {toxicology.first_aid && (
          <div className="tox-card tox-card--emergency">
            <div className="tox-card__header">
              <span className="tox-card__icon tox-card__icon--danger">
                <ShieldAlert size={17} />
              </span>
              <span>PHÁC ĐỒ XỬ TRÍ &amp; SƠ CỨU KHẨN CẤP BAN ĐẦU</span>
            </div>
            <p className="tox-card__body">{toxicology.first_aid}</p>
          </div>
        )}
      </div>

      {/* ─── Footer: Nguồn tham khảo & Tác giả ảnh ─── */}
      <div className="tox-widget__footer">
        <div className="tox-credit">
          <BookOpen size={14} />
          <span>
            Chủ biên chuyên khảo: <strong>PGS.TS. Đào Việt Hà</strong>
          </span>
        </div>

        {toxicology.photographer && (
          <div className="tox-credit tox-credit--photo">
            <Camera size={13} />
            <span>
              Ảnh mẫu vật / Thực địa: <strong>{toxicology.photographer}</strong>
            </span>
          </div>
        )}
      </div>
    </section>
  )
}

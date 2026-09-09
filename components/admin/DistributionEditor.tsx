'use client'

import React, { useState, useEffect, useRef } from 'react'
import { MapPin, Globe, CheckCircle2, Eye, SlidersHorizontal, Sparkles, AlertCircle } from 'lucide-react'
import { splitDistribution, formatDistribution, parseDistribution } from '@/lib/distribution'

interface DistributionEditorProps {
  value: string
  onChange: (val: string) => void
  label?: string
  lang?: 'vn' | 'en'
}

const COMMON_VN_REGIONS = [
  'Vịnh Bắc Bộ',
  'Miền Trung',
  'Nam Bộ',
  'Quần đảo Hoàng Sa',
  'Quần đảo Trường Sa',
  'Vùng biển Tây Nam (Phú Quốc)',
  'Rạn san hô ven biển',
]

export default function DistributionEditor({
  value = '',
  onChange,
  label = 'Phân bố địa lý (Địa bàn & Vùng biển)',
  lang = 'vn',
}: DistributionEditorProps) {
  const [worldText, setWorldText] = useState('')
  const [vnText, setVnText] = useState('')
  const [rawMode, setRawMode] = useState(false)
  const lastSyncedRef = useRef(value)

  // Đồng bộ khi value từ ngoài truyền vào (vd mở modal loài khác)
  useEffect(() => {
    if (value !== lastSyncedRef.current) {
      const { world, vn } = splitDistribution(value)
      setWorldText(world)
      setVnText(vn)
      lastSyncedRef.current = value
    }
  }, [value])

  const handleVnChange = (val: string) => {
    setVnText(val)
    const combined = formatDistribution(worldText, val)
    lastSyncedRef.current = combined
    onChange(combined)
  }

  const handleWorldChange = (val: string) => {
    setWorldText(val)
    const combined = formatDistribution(val, vnText)
    lastSyncedRef.current = combined
    onChange(combined)
  }

  const handleRawChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value
    lastSyncedRef.current = val
    onChange(val)
    const { world, vn } = splitDistribution(val)
    setWorldText(world)
    setVnText(vn)
  }

  const handleAddVnRegion = (regionName: string) => {
    const trimmed = vnText.trim()
    if (!trimmed) {
      handleVnChange(regionName)
      return
    }
    // Tránh thêm trùng
    if (trimmed.toLowerCase().includes(regionName.toLowerCase())) {
      return
    }
    const endsWithPunctuation = /[,;\.]$/.test(trimmed)
    const newText = endsWithPunctuation ? `${trimmed} ${regionName}` : `${trimmed}, ${regionName}`
    handleVnChange(newText)
  }

  // Phân tích thẻ Live Preview theo thời gian thực
  const parsed = parseDistribution(value)
  const length = value ? value.length : 0
  const isOverLimit = length > 2000

  return (
    <div
      className="form-field distribution-editor-card"
      style={{
        background: 'var(--color-paper-2, #ffffff)',
        border: '1px solid var(--color-rule, rgba(0, 0, 0, 0.1))',
        borderRadius: '12px',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
      }}
    >
      {/* Header & Toggle */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="form-label" style={{ margin: 0, fontWeight: 700 }}>
            {label}
          </span>
          <span
            style={{
              fontSize: '0.72rem',
              padding: '2px 8px',
              borderRadius: '9999px',
              background: 'rgba(0, 212, 184, 0.12)',
              color: '#059669',
              fontWeight: 600,
            }}
          >
            Đồng bộ Zod Schema
          </span>
        </div>

        <button
          type="button"
          onClick={() => setRawMode(!rawMode)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.78rem',
            padding: '4px 10px',
            borderRadius: '6px',
            border: '1px solid var(--color-rule, rgba(0,0,0,0.15))',
            background: rawMode ? 'rgba(0, 212, 184, 0.15)' : 'transparent',
            color: rawMode ? '#0f766e' : 'var(--color-muted, #64748b)',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <SlidersHorizontal size={13} />
          <span>{rawMode ? 'Đang bật: Văn bản gộp' : 'Văn bản gộp (Nâng cao)'}</span>
        </button>
      </div>

      {!rawMode ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* 1. Ô nhập Phân bố Việt Nam */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#059669',
              }}
            >
              <MapPin size={15} style={{ color: '#059669' }} />
              <span>Phân bố tại Việt Nam</span>
            </label>
            <textarea
              className="form-input"
              rows={2}
              placeholder="Ví dụ: Vùng biển ven bờ, Vịnh Bắc Bộ, Miền Trung, Hoàng Sa, các rạn san hô..."
              value={vnText}
              onChange={e => handleVnChange(e.target.value)}
              style={{ fontSize: '0.88rem', lineHeight: 1.4 }}
            />

            {/* Gợi ý nhanh vùng biển */}
            <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px', marginTop: '2px' }}>
              <span style={{ fontSize: '0.73rem', color: 'var(--color-muted, #64748b)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <Sparkles size={11} /> Gợi ý nhanh:
              </span>
              {COMMON_VN_REGIONS.map(reg => (
                <button
                  key={reg}
                  type="button"
                  onClick={() => handleAddVnRegion(reg)}
                  style={{
                    background: 'rgba(5, 150, 105, 0.08)',
                    border: '1px solid rgba(5, 150, 105, 0.25)',
                    color: '#047857',
                    borderRadius: '9999px',
                    padding: '2px 8px',
                    fontSize: '0.73rem',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(5, 150, 105, 0.18)')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'rgba(5, 150, 105, 0.08)')}
                >
                  + {reg}
                </button>
              ))}
            </div>
          </div>

          {/* 2. Ô nhập Phân bố Thế giới */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#0284c7',
              }}
            >
              <Globe size={15} style={{ color: '#0284c7' }} />
              <span>Phân bố trên Thế giới</span>
            </label>
            <textarea
              className="form-input"
              rows={2}
              placeholder="Ví dụ: Ấn Độ Dương, Thái Bình Dương, Biển Đỏ, Philippines, Nhật Bản..."
              value={worldText}
              onChange={e => handleWorldChange(e.target.value)}
              style={{ fontSize: '0.88rem', lineHeight: 1.4 }}
            />
          </div>
        </div>
      ) : (
        /* Chế độ nhập văn bản gộp (Nâng cao) */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <label style={{ fontSize: '0.78rem', color: 'var(--color-muted, #64748b)' }}>
            Văn bản gộp chuỗi phân bố trong CSDL (cột <code>{lang === 'vn' ? 'vn_distribution' : 'en_distribution'}</code>):
          </label>
          <textarea
            className="form-input"
            rows={4}
            value={value}
            onChange={handleRawChange}
            placeholder="Nhập chuỗi phân bố đầy đủ..."
            style={{ fontFamily: 'monospace', fontSize: '0.84rem' }}
          />
        </div>
      )}

      {/* ── Khối 3: Bản Xem Trước Trực Quan (Live Preview trên Thẻ Loài) ── */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.04) 0%, rgba(14, 165, 233, 0.03) 100%)',
          border: '1px dashed rgba(16, 185, 129, 0.3)',
          borderRadius: '10px',
          padding: '12px 14px',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              color: 'var(--color-ink, #0b1329)',
            }}
          >
            <Eye size={13} style={{ color: '#059669' }} />
            <span>Xem trước ngoài SpeciesCard (Live Preview)</span>
          </span>

          <span
            style={{
              fontSize: '0.72rem',
              color: isOverLimit ? '#ef4444' : length > 1800 ? '#f59e0b' : 'var(--color-muted, #64748b)',
              fontWeight: 600,
            }}
          >
            {length} / 2000 ký tự
          </span>
        </div>

        {isOverLimit && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 10px',
              borderRadius: '6px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#dc2626',
              fontSize: '0.75rem',
              fontWeight: 600,
            }}
          >
            <AlertCircle size={14} />
            <span>Đã vượt quá 2000 ký tự tối đa của Zod Schema! Vui lòng rút gọn lại.</span>
          </div>
        )}

        {/* Thẻ Việt Nam */}
        {parsed.vn.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#059669', textTransform: 'uppercase' }}>
              📍 Việt Nam:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {parsed.vn.map((loc, idx) => (
                <span
                  key={idx}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '3px 10px',
                    borderRadius: '9999px',
                    fontSize: '0.78rem',
                    fontWeight: 600,
                    background: 'rgba(5, 150, 105, 0.1)',
                    border: '1px solid rgba(5, 150, 105, 0.3)',
                    color: '#059669',
                  }}
                >
                  <CheckCircle2 size={12} />
                  {loc}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Thẻ Thế Giới */}
        {parsed.world.length > 0 && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
              paddingTop: parsed.vn.length > 0 ? '6px' : 0,
              borderTop: parsed.vn.length > 0 ? '1px dashed rgba(0,0,0,0.08)' : 'none',
            }}
          >
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#0284c7', textTransform: 'uppercase' }}>
              🌐 Thế giới:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {parsed.world.map((loc, idx) => (
                <span
                  key={idx}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: '3px 10px',
                    borderRadius: '9999px',
                    fontSize: '0.78rem',
                    fontWeight: 500,
                    background: 'rgba(2, 132, 199, 0.08)',
                    border: '1px solid rgba(2, 132, 199, 0.25)',
                    color: '#0369a1',
                  }}
                >
                  {loc}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Nếu không có thẻ nào */}
        {parsed.vn.length === 0 && parsed.world.length === 0 && (
          <div style={{ fontSize: '0.78rem', color: 'var(--color-muted, #94a3b8)', fontStyle: 'italic' }}>
            {value.trim() ? (
              <span>Nội dung hiện tại: {value}</span>
            ) : (
              <span>(Chưa có dữ liệu phân bố. Hãy nhập thông tin phía trên)</span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

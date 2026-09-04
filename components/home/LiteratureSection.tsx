import React from 'react'
import Link from 'next/link'
import { BookOpen, Fish, Compass, Leaf, ArrowRight, BookMarked, Anchor, Shell, Waves } from 'lucide-react'
import './LiteratureSection.css'

// ponytail: auto-assign theme colors by index — no admin color picking needed
const THEME_PALETTE = [
  { accentColor: '#0ea5e9', accentGrad: 'linear-gradient(90deg, #0284c7 0%, #38bdf8 100%)', accentShadow: 'rgba(14, 165, 233, 0.22)', iconBg: 'rgba(14, 165, 233, 0.12)', pillBg: 'rgba(14, 165, 233, 0.1)', pillBorder: 'rgba(14, 165, 233, 0.25)' },
  { accentColor: '#14b8a6', accentGrad: 'linear-gradient(90deg, #0d9488 0%, #2dd4bf 100%)', accentShadow: 'rgba(20, 184, 166, 0.22)', iconBg: 'rgba(20, 184, 166, 0.12)', pillBg: 'rgba(20, 184, 166, 0.1)', pillBorder: 'rgba(20, 184, 166, 0.25)' },
  { accentColor: '#10b981', accentGrad: 'linear-gradient(90deg, #059669 0%, #34d399 100%)', accentShadow: 'rgba(16, 185, 129, 0.22)', iconBg: 'rgba(16, 185, 129, 0.12)', pillBg: 'rgba(16, 185, 129, 0.1)', pillBorder: 'rgba(16, 185, 129, 0.25)' },
  { accentColor: '#8b5cf6', accentGrad: 'linear-gradient(90deg, #7c3aed 0%, #a78bfa 100%)', accentShadow: 'rgba(139, 92, 246, 0.22)', iconBg: 'rgba(139, 92, 246, 0.12)', pillBg: 'rgba(139, 92, 246, 0.1)', pillBorder: 'rgba(139, 92, 246, 0.25)' },
  { accentColor: '#f59e0b', accentGrad: 'linear-gradient(90deg, #d97706 0%, #fbbf24 100%)', accentShadow: 'rgba(245, 158, 11, 0.22)', iconBg: 'rgba(245, 158, 11, 0.12)', pillBg: 'rgba(245, 158, 11, 0.1)', pillBorder: 'rgba(245, 158, 11, 0.25)' },
  { accentColor: '#ec4899', accentGrad: 'linear-gradient(90deg, #db2777 0%, #f472b6 100%)', accentShadow: 'rgba(236, 72, 153, 0.22)', iconBg: 'rgba(236, 72, 153, 0.12)', pillBg: 'rgba(236, 72, 153, 0.1)', pillBorder: 'rgba(236, 72, 153, 0.25)' },
]

const ICON_MAP: Record<string, React.ReactNode> = {
  'fish': <Fish size={24} strokeWidth={1.75} />,
  'compass': <Compass size={24} strokeWidth={1.75} />,
  'leaf': <Leaf size={24} strokeWidth={1.75} />,
  'book-open': <BookOpen size={24} strokeWidth={1.75} />,
  'anchor': <Anchor size={24} strokeWidth={1.75} />,
  'shell': <Shell size={24} strokeWidth={1.75} />,
  'waves': <Waves size={24} strokeWidth={1.75} />,
}

export interface LiteratureSourceRow {
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
}

interface Props {
  sources: LiteratureSourceRow[]
}

export default function LiteratureSection({ sources }: Props) {
  if (!sources.length) return null

  return (
    <section className="lit-section" aria-label="Tài liệu khoa học gốc tra cứu">
      <div className="lit-header">
        <div className="lit-badge-wrapper">
          <BookOpen size={15} color="var(--color-cyan-raw)" />
          <span className="lit-badge-text">TÀI LIỆU KHOA HỌC GỐC TRA CỨU</span>
        </div>
        <h2 className="lit-title">Nguồn tài liệu tham khảo</h2>
        <p className="lit-subtitle">
          Cơ sở dữ liệu được tham khảo chính từ các nguồn tài liệu sau:
        </p>
      </div>

      <div className="lit-grid">
        {sources.map((item, index) => {
          const theme = THEME_PALETTE[index % THEME_PALETTE.length]
          const icon = ICON_MAP[item.icon_name || 'book-open'] || ICON_MAP['book-open']

          return (
            <Link
              key={item.id}
              href={item.href}
              className="lit-card"
              style={
                {
                  '--card-accent-color': theme.accentColor,
                  '--card-accent-grad': theme.accentGrad,
                  '--card-accent-shadow': theme.accentShadow,
                  '--card-icon-bg': theme.iconBg,
                  '--card-pill-bg': theme.pillBg,
                  '--card-pill-border': theme.pillBorder,
                } as React.CSSProperties
              }
            >
              <div className="lit-card__accent-bar" />
              <div className="lit-card__body">
                <div className="lit-card__top-meta">
                  <div className="lit-card__icon-box">{icon}</div>
                  {item.pill_text && <span className="lit-card__pill">{item.pill_text}</span>}
                </div>

                <h3 className="lit-card__title">{item.title}</h3>
                <div className="lit-card__author">
                  <BookMarked size={14} />
                  <span>{item.author}</span>
                </div>
                <div className="lit-card__pub">{item.publisher} • {item.year}</div>

                {item.description && <p className="lit-card__desc">{item.description}</p>}

                {item.chips && item.chips.length > 0 && (
                  <div className="lit-card__chips">
                    {item.chips.map((chip, idx) => (
                      <span key={idx} className="lit-chip">
                        {chip}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="lit-card__footer">
                <span className="lit-card__stat-count">{item.stats_count}</span>
                <span className="lit-card__cta-btn">
                  Tra cứu công trình <ArrowRight size={15} />
                </span>
              </div>
            </Link>
          )
        })}
      </div>
    </section>
  )
}

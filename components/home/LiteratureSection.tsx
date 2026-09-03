import React from 'react'
import Link from 'next/link'
import { BookOpen, Fish, Compass, Leaf, ArrowRight, BookMarked, Award, Layers } from 'lucide-react'
import './LiteratureSection.css'

interface LiteratureSource {
  id: string
  title: string
  subtitle: string
  author: string
  publisher: string
  year: string
  statsCount: string
  pillText: string
  description: string
  icon: React.ReactNode
  href: string
  chips: string[]
  theme: {
    accentColor: string
    accentGrad: string
    accentShadow: string
    iconBg: string
    pillBg: string
    pillBorder: string
  }
}

const LITERATURE_SOURCES: LiteratureSource[] = [
  {
    id: 'ca-bien-5-tap',
    title: 'Danh mục Cá biển Việt Nam',
    subtitle: 'Tập I – V (1992 – 2007)',
    author: 'GS. Nguyễn Khắc Hường, TS. Nguyễn Nhật Thi và CS',
    publisher: 'Nhà xuất bản Nông nghiệp',
    year: '1992 – 2007',
    statsCount: '1,501 loài cá biển',
    pillText: '5 Tập Chuyên Khảo',
    description:
      'Công trình điều tra định loại học nền tảng toàn diện nhất về thành phần loài cá tại các vùng biển Việt Nam, phân định chi tiết từ cá sụn đến cá xương.',
    icon: <Fish size={24} strokeWidth={1.75} />,
    href: '/ca-bien?vol=1',
    chips: ['T.I: Cá nhám, cá đuối', 'T.II: Cá trích, cá chình', 'T.III: Cá bơn, cá chai', 'T.IV: Cá mú, cá thia', 'T.V: Cá đù, cá khế'],
    theme: {
      accentColor: '#0ea5e9',
      accentGrad: 'linear-gradient(90deg, #0284c7 0%, #38bdf8 100%)',
      accentShadow: 'rgba(14, 165, 233, 0.22)',
      iconBg: 'rgba(14, 165, 233, 0.12)',
      pillBg: 'rgba(14, 165, 233, 0.1)',
      pillBorder: 'rgba(14, 165, 233, 0.25)',
    },
  },
  {
    id: 'atlas-ca-ran',
    title: 'Atlas Cá rạn san hô Việt Nam',
    subtitle: 'Tập VI (2020)',
    author: 'TS. Đỗ Thị Cát Tường',
    publisher: 'NXB Khoa học Tự nhiên và Công nghệ',
    year: '2020',
    statsCount: '263 loài cá rạn',
    pillText: 'Tập VI • Atlas Màu',
    description:
      'Bộ tư liệu hình thái và mẫu ảnh thực địa chuyên sâu về các loài cá đặc trưng thuộc hệ sinh thái rạn san hô, gắn liền dữ liệu quan trắc sinh thái học.',
    icon: <Compass size={24} strokeWidth={1.75} />,
    href: '/ca-bien?vol=6',
    chips: ['263 loài cá rạn san hô', '1,069 ảnh Research-grade', 'Độ phủ ảnh 98.5%', '100% dịch tóm tắt sinh học'],
    theme: {
      accentColor: '#14b8a6',
      accentGrad: 'linear-gradient(90deg, #0d9488 0%, #2dd4bf 100%)',
      accentShadow: 'rgba(20, 184, 166, 0.22)',
      iconBg: 'rgba(20, 184, 166, 0.12)',
      pillBg: 'rgba(20, 184, 166, 0.1)',
      pillBorder: 'rgba(20, 184, 166, 0.25)',
    },
  },
  {
    id: 'thuc-vat-bien',
    title: 'Thực Vật Biển Thường Thấy ở Phía Nam Việt Nam',
    subtitle: 'The Common Marine Plants of Southern Vietnam',
    author: 'TSUTSUI Isao, HUỲNH Quang Năng, NGUYỄN Hữu Dinh, ARAI Shogo and YOSHIDA Tadao',
    publisher: 'Japan Seaweed Association',
    year: 'Chuyên khảo chuẩn',
    statsCount: '201 loài thực vật',
    pillText: '1 Tập Chuyên Khảo',
    description:
      'Tài liệu định loại hệ Thực vật biển Việt Nam: khóa phân loại, đặc điểm hiển vi, giá trị kinh tế và sinh thái của các loài rong ven bờ và hải đảo.',
    icon: <Leaf size={24} strokeWidth={1.75} />,
    href: '/thuc-vat-bien',
    chips: ['Rhodophyta (Rong đỏ): 111 loài', 'Phaeophyceae (Rong nâu): 46', 'Chlorophyta (Rong lục): 38', 'Cyanobacteria: 6'],
    theme: {
      accentColor: '#10b981',
      accentGrad: 'linear-gradient(90deg, #059669 0%, #34d399 100%)',
      accentShadow: 'rgba(16, 185, 129, 0.22)',
      iconBg: 'rgba(16, 185, 129, 0.12)',
      pillBg: 'rgba(16, 185, 129, 0.1)',
      pillBorder: 'rgba(16, 185, 129, 0.25)',
    },
  },
]

export default function LiteratureSection() {
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
        {LITERATURE_SOURCES.map((item) => (
          <Link
            key={item.id}
            href={item.href}
            className="lit-card"
            style={
              {
                '--card-accent-color': item.theme.accentColor,
                '--card-accent-grad': item.theme.accentGrad,
                '--card-accent-shadow': item.theme.accentShadow,
                '--card-icon-bg': item.theme.iconBg,
                '--card-pill-bg': item.theme.pillBg,
                '--card-pill-border': item.theme.pillBorder,
              } as React.CSSProperties
            }
          >
            <div className="lit-card__accent-bar" />
            <div className="lit-card__body">
              <div className="lit-card__top-meta">
                <div className="lit-card__icon-box">{item.icon}</div>
                <span className="lit-card__pill">{item.pillText}</span>
              </div>

              <h3 className="lit-card__title">{item.title}</h3>
              <div className="lit-card__author">
                <BookMarked size={14} />
                <span>{item.author}</span>
              </div>
              <div className="lit-card__pub">{item.publisher} • {item.year}</div>

              <p className="lit-card__desc">{item.description}</p>

              <div className="lit-card__chips">
                {item.chips.map((chip, idx) => (
                  <span key={idx} className="lit-chip">
                    {chip}
                  </span>
                ))}
              </div>
            </div>

            <div className="lit-card__footer">
              <span className="lit-card__stat-count">{item.statsCount}</span>
              <span className="lit-card__cta-btn">
                Tra cứu công trình <ArrowRight size={15} />
              </span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  )
}

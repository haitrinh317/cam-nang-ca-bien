import '@/styles/about.css'
import type { Metadata } from 'next'
import Link from 'next/link'
import { ArrowLeft, BookOpen, ShieldCheck, Sparkles, Globe, HeartHandshake, Compass, Library, CheckCircle2 } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Giới thiệu',
  description: 'Dự án số hóa di sản và dữ liệu sinh vật biển phi lợi nhuận phục vụ học tập, nghiên cứu và cộng đồng — Một dự án được phát triển bởi haitrinh.',
  alternates: {
    canonical: 'https://www.tracuusinhvatbien.app/about',
  },
  openGraph: {
    type: 'website',
    locale: 'vi_VN',
    url: 'https://www.tracuusinhvatbien.app/about',
    siteName: 'Tra cứu thông tin Sinh Vật Biển Việt Nam',
    title: 'Giới thiệu — Tra cứu thông tin Sinh Vật Biển Việt Nam',
    description: 'Sứ mệnh bảo tồn tri thức phân loại học biển, ứng dụng AI/OCR và kết nối CSDL sinh vật biển toàn cầu — Một dự án được phát triển bởi haitrinh.',
    images: [{ url: '/og-default.png', width: 1200, height: 630, alt: 'Giới thiệu Tra cứu thông tin Sinh Vật Biển Việt Nam' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Giới thiệu — Tra cứu thông tin Sinh Vật Biển Việt Nam',
    description: 'Sứ mệnh bảo tồn tri thức phân loại học biển và kết nối CSDL sinh vật biển toàn cầu — Một dự án được phát triển bởi haitrinh.',
    images: ['/og-default.png'],
  },
}

const STATS = [
  { value: '1.765+', label: 'Loài cá biển', sub: 'Đã số hóa cấu trúc' },
  { value: '6 Tập', label: 'Ấn phẩm kinh điển', sub: '1992 – nay' },
  { value: '100%', label: 'Xác thực WoRMS', sub: 'Mã AphiaID quốc tế' },
  { value: '2026', label: 'Khởi xướng', sub: 'Phát triển bởi haitrinh' },
]

const PILLARS = [
  {
    icon: <BookOpen size={24} />,
    title: 'Bảo tồn Di sản Khoa học',
    desc: 'Số hóa và cứu vãn những trang sách giấy ố vàng từ những năm 1990 trước nguy cơ thất truyền vật lý, phục dựng nguyên vẹn mô tả hình thái và bản vẽ nét độc bản của các chuyên gia đầu ngành.',
  },
  {
    icon: <Sparkles size={24} />,
    title: 'Công nghệ AI & OCR Đa tầng',
    desc: 'Ứng dụng mô hình thị giác máy tính và Vision LLMs để nhận diện chính xác cấu trúc văn bản học thuật song ngữ, công thức vây, kích thước mẫu vật và địa điểm phân bố.',
  },
  {
    icon: <Globe size={24} />,
    title: 'Chuẩn hóa Quốc tế (WoRMS & FishBase)',
    desc: 'Đối chiếu 100% danh pháp khoa học cổ với Cơ sở dữ liệu Danh lục Sinh vật biển Thế giới (WoRMS) và làm giàu dữ liệu sinh thái, tuổi thọ, mức độ đe dọa từ FishBase & Sách Đỏ IUCN.',
  },
  {
    icon: <HeartHandshake size={24} />,
    title: 'Khoa học Mở vì Cộng đồng',
    desc: 'Nền tảng mở phi thương mại, phục vụ trực tiếp công tác học tập, nghiên cứu sinh học biển, giáo dục học đường và nâng cao nhận thức bảo tồn đại dương.',
  },
]

const VOLUMES = [
  { vol: 'Tập I', year: '1992', name: 'Cá Nhám, Cá Đuối, Cá Trích, Cá Chình', author: 'GS. Nguyễn Khắc Hường' },
  { vol: 'Tập II', year: '1994', name: 'Cá Mối, Cá Suốt, Cá Chích, Cá Chai', author: 'GS. Nguyễn Khắc Hường, TS. Nguyễn Nhật Thi' },
  { vol: 'Tập III', year: '2000', name: 'Cá Hồng, Cá Mú, Cá Đù, Cá Mối', author: 'GS. Nguyễn Khắc Hường' },
  { vol: 'Tập IV', year: '2004', name: 'Cá Bướm, Cá Thiên nga, Cá Tai tượng', author: 'TS. Nguyễn Nhật Thi' },
  { vol: 'Tập V', year: '2007', name: 'Cá Bống, Cá Bơn, Cá Nóc, Cá Cóc biển', author: 'TS. Nguyễn Nhật Thi' },
  { vol: 'Tập VI', year: '2020s', name: 'Atlas Cá rạn san hô Việt Nam', author: 'TS. Đỗ Thị Cát Tường' },
  { vol: 'Thực vật biển', year: 'Chuyên khảo', name: 'Thực Vật Biển Thường Thấy ở Phía Nam Việt Nam', author: 'TSUTSUI Isao, HUỲNH Quang Năng, NGUYỄN Hữu Dinh, ARAI Shogo and YOSHIDA Tadao' },
]

export default function AboutPage() {
  return (
    <div className="about-wrapper">
      <div className="about-container">
        {/* Back Link */}
        <Link href="/" className="back-link" aria-label="Quay lại trang chủ">
          <ArrowLeft size={16} />
          <span>Quay lại trang chủ</span>
        </Link>

        {/* Hero Section */}
        <header className="about-hero">
          <div className="about-hero__badge">
            <Compass size={14} />
            <span>SỨ MỆNH DI SẢN & KHOA HỌC MỞ</span>
          </div>
          <h1 className="about-hero__title">
            Lăng kính Đại dương.<br />
            <span className="about-hero__title-accent">Bảo tồn Tri thức Biển Việt Nam.</span>
          </h1>
          <p className="about-hero__lead">
            Tra cứu thông tin Sinh Vật Biển Việt Nam là công trình chuyển đổi số toàn diện, kết nối kho tàng nghiên cứu ngư loại học đồ sộ của các nhà khoa học Việt Nam từ thế kỷ 20 với công nghệ trí tuệ nhân tạo và chuẩn mực phân loại học toàn cầu.
          </p>

          <div className="about-hero__meta-card">
            <div className="about-meta-col">
              <span className="about-meta-label">Dự án</span>
              <span className="about-meta-value">Tra cứu thông tin Sinh Vật Biển Việt Nam</span>
            </div>
            <div className="about-meta-col">
              <span className="about-meta-label">Nhà phát triển</span>
              <span className="about-meta-value">Một dự án được phát triển bởi haitrinh</span>
            </div>
            <div className="about-meta-col">
              <span className="about-meta-label">Định hướng</span>
              <span className="about-meta-value">Số hóa tri thức di sản phân loại học & bảo tồn đại dương</span>
            </div>
          </div>
        </header>

        {/* Impact Numbers */}
        <section className="about-stats-grid" aria-label="Các con số nổi bật của dự án">
          {STATS.map((st, i) => (
            <div key={i} className="about-stat-card">
              <span className="about-stat-num">{st.value}</span>
              <span className="about-stat-label">{st.label}</span>
              <span className="about-stat-sub">{st.sub}</span>
            </div>
          ))}
        </section>

        {/* Story Section */}
        <section className="about-story-section">
          <div className="about-section-header">
            <h2 className="about-section-title">Khởi nguồn & Ý nghĩa Dự án</h2>
            <div className="about-section-bar" />
          </div>

          <div className="about-story-content">
            <p>
              Việt Nam sở hữu bờ biển dài hơn 3.260 km với hệ sinh thái biển vô cùng phong phú và đa dạng. Trong suốt hơn một thế kỷ qua, nhiều thế hệ nhà khoa học sinh vật biển đã thực hiện hàng trăm chuyến hải trình thám hiểm, khảo sát, đo vẽ và định loại hàng nghìn loài sinh vật biển tại vùng biển từ Vịnh Bắc Bộ, dải bờ miền Trung, quần đảo Hoàng Sa – Trường Sa cho đến Vịnh Thái Lan.
            </p>
            <p>
              Thành quả của những thập kỷ lao động kiên trì đó đã kết tinh trong các bộ sách kinh điển, đặc biệt là bộ <strong>&ldquo;Danh mục Cá biển Việt Nam&rdquo;</strong> (Tập I đến Tập V do GS. Nguyễn Khắc Hường và TS. Nguyễn Nhật Thi chủ biên) cùng <strong>&ldquo;Atlas cá rạn san hô Việt Nam&rdquo;</strong> (Tập VI của TS. Đỗ Thị Cát Tường). Tuy nhiên, sau nhiều thập kỷ, các bản in giấy đang dần bị lão hóa, phai mờ và ngày càng khó tìm.
            </p>
            <blockquote className="about-quote">
              &ldquo;Một di sản khoa học chỉ thực sự sống mãi khi nó được lan tỏa, tiếp cận dễ dàng và trở thành nguồn cảm hứng cho thế hệ tiếp nối bảo vệ biển mẹ.&rdquo;
            </blockquote>
            <p>
              Chính vì lý do đó, dự án <strong>Tra cứu thông tin Sinh Vật Biển Việt Nam</strong> được tác giả <strong>haitrinh</strong> khởi xướng và triển khai như một cầu nối số hóa độc lập: kết hợp công nghệ xử lý ảnh số, trí tuệ nhân tạo (Vision OCR) và cơ sở dữ liệu hiện đại để số hóa từng trang tư liệu, hiệu đính danh pháp theo chuẩn quốc tế và trao tặng cho cộng đồng một kho tri thức biển sống động, minh bạch và hoàn toàn miễn phí.
            </p>
          </div>
        </section>

        {/* 4 Pillars Grid */}
        <section className="about-pillars-section">
          <div className="about-section-header">
            <h2 className="about-section-title">4 Trụ Cột Phát Triển</h2>
            <div className="about-section-bar" />
          </div>

          <div className="about-pillars-grid">
            {PILLARS.map((p, idx) => (
              <div key={idx} className="about-pillar-card">
                <div className="about-pillar-icon">{p.icon}</div>
                <h3 className="about-pillar-title">{p.title}</h3>
                <p className="about-pillar-desc">{p.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Archival Literature Timeline */}
        <section className="about-timeline-section">
          <div className="about-section-header">
            <div className="about-badge-small">
              <Library size={13} />
              <span>NGUỒN TÀI LIỆU KHOA HỌC</span>
            </div>
            <h2 className="about-section-title">Ấn Bản Kinh Điển Được Số Hóa</h2>
            <div className="about-section-bar" />
          </div>

          <div className="about-timeline-list">
            {VOLUMES.map((vol, idx) => (
              <div key={idx} className="about-timeline-item">
                <div className="about-timeline-marker">
                  <CheckCircle2 size={16} />
                </div>
                <div className="about-timeline-content">
                  <div className="about-vol-header">
                    <span className="about-vol-badge">{vol.vol}</span>
                    <span className="about-vol-year">Năm {vol.year}</span>
                  </div>
                  <h4 className="about-vol-name">{vol.name}</h4>
                  <p className="about-vol-author">Tác giả / Ban biên soạn: {vol.author}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Call to Action Footer Box */}
        <section className="about-cta-box">
          <div className="about-cta-content">
            <h3 className="about-cta-title">Bắt đầu khám phá CSDL Sinh vật biển</h3>
            <p className="about-cta-desc">
              Tra cứu hình ảnh, công thức vây, kích thước mẫu vật, tên khoa học WoRMS và dữ liệu sinh thái của hơn 1.765 loài cá biển và rong biển Việt Nam.
            </p>
            <div className="about-cta-actions">
              <Link href="/ca-bien" className="about-btn-primary">
                Tra cứu Cá biển Việt Nam
              </Link>
              <Link href="/faq" className="about-btn-secondary">
                Xem Câu hỏi thường gặp (FAQ)
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Giới thiệu — Cẩm nang Sinh vật biển Việt Nam',
  description: 'Dự án số hóa dữ liệu sinh vật biển phi lợi nhuận của Viện Hải dương học.',
}

export default function AboutPage() {
  return (
    <div className="about-page">
      <header className="about__header">
        <h1 className="about__title">Lăng kính<br />đại dương.</h1>
        <div className="about__meta">
          <span className="about__meta-label">DỰ ÁN SỐ HÓA</span>
          <span className="about__meta-value">Phi lợi nhuận</span>
          <span className="about__meta-label">ĐƠN VỊ PHÁT TRIỂN</span>
          <span className="about__meta-value">Phòng Thông tin – Truyền thông<br/>Viện Hải dương học</span>
        </div>
      </header>
      
      <main className="about__content">
        <article className="about__reading-column">
          <p className="about__lead">
            Cẩm nang Sinh vật biển Việt Nam là một dự án kế thừa và hệ thống hóa kho tàng tri thức khổng lồ từ các công trình nghiên cứu và ấn phẩm khoa học đã được công bố về các nhóm sinh vật biển tại Việt Nam.
          </p>
          
          <p>
            Chúng tôi xây dựng nền tảng này với mục tiêu cốt lõi: tạo ra một công cụ tra cứu thông tin nhanh chóng, chính xác và trực quan nhất, phục vụ trực tiếp cho công tác chuyên môn của viên chức và người lao động tại Bảo tàng Hải dương học.
          </p>
          
          <p>
            Dự án được khởi xướng và phát triển bởi Phòng Thông tin – Truyền thông, Viện Hải dương học (Viện Hàn lâm Khoa học và Công nghệ Việt Nam), như một nỗ lực chuyển đổi số và bảo tồn các giá trị khoa học biển nước nhà.
          </p>
        </article>
      </main>
    </div>
  )
}

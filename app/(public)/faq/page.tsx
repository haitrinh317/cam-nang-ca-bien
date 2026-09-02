import type { Metadata } from 'next'
import Link from 'next/link'
import FaqAccordion from '@/components/faq/FaqAccordion'
import { FAQ_DATA } from '@/lib/faq-data'
import { ArrowLeft, HelpCircle } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Câu hỏi thường gặp (FAQ) — Cẩm nang Sinh vật biển Việt Nam',
  description: 'Giải đáp thắc mắc về nguồn dữ liệu khoa học, lý do số hóa di sản, công nghệ OCR AI, quy chuẩn danh pháp WoRMS và điều khoản bản quyền của Cẩm nang Sinh vật biển Việt Nam.',
  openGraph: {
    title: 'Câu hỏi thường gặp (FAQ) — Cẩm nang Sinh vật biển Việt Nam',
    description: 'Nguồn gốc tài liệu, công nghệ OCR số hóa và tính xác thực khoa học của Cẩm nang Sinh vật biển Việt Nam.',
    type: 'website',
  },
}

export default function FaqPage() {
  // Generate JSON-LD for Google FAQPage Schema
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: FAQ_DATA.map(item => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer.replace(/\n\n/g, ' '),
      },
    })),
  }

  return (
    <>
      {/* Schema.org FAQPage Structured Data for SEO Rich Snippets */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="faq-page-wrapper">
        <div className="faq-page-container">
          {/* Back link */}
          <Link href="/" className="back-link" aria-label="Quay lại trang chủ">
            <ArrowLeft size={16} />
            <span>Quay lại trang chủ</span>
          </Link>

          {/* Hero Header */}
          <header className="faq-hero">
            <div className="faq-hero__pill">
              <HelpCircle size={14} />
              <span>Hỏi đáp & Tra cứu tri thức</span>
            </div>
            <h1 className="faq-hero__title">
              Câu hỏi thường gặp
            </h1>
            <p className="faq-hero__subtitle">
              Mọi điều bạn cần biết về nguồn tài liệu nghiên cứu gốc, lý do thực hiện dự án số hóa, công nghệ nhận dạng OCR AI và tính xác thực khoa học chuẩn quốc tế (WoRMS & FishBase).
            </p>
          </header>

          {/* Interactive Accordion & Search */}
          <main>
            <FaqAccordion />
          </main>
        </div>
      </div>
    </>
  )
}

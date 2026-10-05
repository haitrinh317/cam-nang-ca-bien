import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import BackToTop from '@/components/ui/BackToTop'
import { BottomNav } from '@/components/layout/BottomNav'

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <a href="#main-content" className="skip-link">Bỏ qua đến nội dung chính</a>
      <Nav />
      <main id="main-content" tabIndex={-1} className="main-container">
        {children}
      </main>
      <Footer />
      <BackToTop />
      <BottomNav />
    </>
  )
}

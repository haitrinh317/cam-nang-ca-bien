import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import BackToTop from '@/components/ui/BackToTop'
import { BottomNav } from '@/components/layout/BottomNav'
import { PwaInstallPrompt } from '@/components/layout/PwaInstallPrompt'

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <Nav />
      <main className="main-container">
        {children}
      </main>
      <Footer />
      <BackToTop />
      <BottomNav />
      <PwaInstallPrompt />
    </>
  )
}

import type { Metadata } from 'next'
import '@/styles/tokens.css'
import '@/styles/globals.css'
import { ThemeScript } from '@/components/layout/ThemeScript'
import { BottomNav } from '@/components/layout/BottomNav'

const SITE_URL = 'https://cam-nang-ca-bien.vercel.app'

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: 'Bảo tàng Hải dương học — Tra cứu Sinh vật biển Việt Nam',
    template: '%s — Bảo tàng Hải dương học',
  },
  description: 'Cơ sở dữ liệu số hóa sinh vật biển Việt Nam phục vụ nghiên cứu khoa học — Viện Hải dương học, Nha Trang.',
  keywords: ['cá biển', 'sinh vật biển', 'hải dương học', 'Việt Nam', 'danh mục', 'phân loại học', 'marine fish', 'Vietnam'],
  authors: [{ name: 'Viện Hải dương học, Nha Trang' }],
  creator: 'Bảo tàng Hải dương học',
  openGraph: {
    type: 'website',
    locale: 'vi_VN',
    alternateLocale: 'en_US',
    url: SITE_URL,
    siteName: 'Bảo tàng Hải dương học',
    title: 'Bảo tàng Hải dương học — Tra cứu Sinh vật biển Việt Nam',
    description: 'Cơ sở dữ liệu số hóa sinh vật biển Việt Nam — Viện Hải dương học, Nha Trang.',
    images: [{ url: '/og-default.png', width: 1200, height: 630, alt: 'Bảo tàng Hải dương học' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Bảo tàng Hải dương học — Tra cứu Sinh vật biển Việt Nam',
    description: 'Cơ sở dữ liệu số hóa sinh vật biển Việt Nam.',
    images: ['/og-default.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, 'max-image-preview': 'large' },
  },
  manifest: '/site.webmanifest',
}


export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        <meta name="theme-color" content="#0c142a" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="Cá biển VN" />
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
        <ThemeScript />
      </head>
      <body>
        {children}
        <BottomNav />
      </body>
    </html>
  )
}

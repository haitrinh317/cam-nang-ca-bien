import type { Metadata, Viewport } from 'next'
import { Lora, Be_Vietnam_Pro, JetBrains_Mono } from 'next/font/google'
import '@/styles/tokens.css'
import '@/styles/globals.css'
import '@/styles/responsive.css'
import '@/styles/buttons.css'
import '@/styles/mobile.css'
import '@/styles/dark-mode.css'
import { BottomNav } from '@/components/layout/BottomNav'
import { PwaInstallPrompt } from '@/components/layout/PwaInstallPrompt'

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
}

const lora = Lora({
  subsets: ['vietnamese', 'latin'],
  weight: ['400', '500', '600', '700'],
  style: ['normal', 'italic'],
  variable: '--font-lora',
  display: 'swap',
})

const beVietnamPro = Be_Vietnam_Pro({
  subsets: ['vietnamese', 'latin'],
  weight: ['400', '500', '600', '700'],
  style: ['normal', 'italic'],
  variable: '--font-be-vietnam',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

const SITE_URL = 'https://www.tracuusinhvatbien.app'

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: 'Tra cứu thông tin Sinh Vật Biển Việt Nam',
    template: '%s — Tra cứu thông tin Sinh Vật Biển Việt Nam',
  },
  description: 'Cơ sở dữ liệu số hóa sinh vật biển Việt Nam phục vụ học tập, nghiên cứu và cộng đồng — Một dự án được phát triển bởi haitrinh.',
  keywords: ['tra cứu sinh vật biển', 'cá biển', 'rong biển', 'giáp xác', 'rắn biển', 'phân loại học', 'sinh thái biển', 'marine species', 'Vietnam'],
  authors: [{ name: 'haitrinh', url: SITE_URL }],
  creator: 'haitrinh',
  publisher: 'haitrinh',
  openGraph: {
    type: 'website',
    locale: 'vi_VN',
    alternateLocale: 'en_US',
    url: SITE_URL,
    siteName: 'Tra cứu thông tin Sinh Vật Biển Việt Nam',
    title: 'Tra cứu thông tin Sinh Vật Biển Việt Nam — haitrinh',
    description: 'Cơ sở dữ liệu số hóa 2.671+ loài sinh vật biển Việt Nam — Hệ thống tra cứu danh pháp, hình thái học & sinh thái. Một dự án được phát triển bởi haitrinh.',
    images: [{ url: '/og-default.png', width: 1200, height: 630, alt: 'Tra cứu thông tin Sinh Vật Biển Việt Nam' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Tra cứu thông tin Sinh Vật Biển Việt Nam — haitrinh',
    description: 'Cơ sở dữ liệu số hóa 2.671+ loài sinh vật biển Việt Nam — Một dự án được phát triển bởi haitrinh.',
    creator: '@haitrinh',
    images: ['/og-default.png'],
  },
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/icons/icon-192x192.png', sizes: '192x192', type: 'image/png' },
    ],
    apple: [
      { url: '/icons/icon-192x192.png', sizes: '192x192', type: 'image/png' },
    ],
    shortcut: '/favicon.ico',
  },
  alternates: {
    canonical: SITE_URL,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, 'max-image-preview': 'large' },
  },
  manifest: '/site.webmanifest',
}

const websiteSchema = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'Tra cứu thông tin Sinh Vật Biển Việt Nam',
  alternateName: ['Cẩm Nang Sinh Vật Biển Việt Nam', 'Tra cứu Sinh vật biển Việt Nam', 'Cá Biển Việt Nam'],
  url: SITE_URL,
  description: 'Cơ sở dữ liệu số hóa 2.671+ loài sinh vật biển Việt Nam phục vụ học tập, nghiên cứu và cộng đồng — Một dự án được phát triển bởi haitrinh.',
  author: {
    '@type': 'Person',
    name: 'haitrinh',
    url: SITE_URL,
  },
  creator: {
    '@type': 'Person',
    name: 'haitrinh',
    url: SITE_URL,
  },
  publisher: {
    '@type': 'Person',
    name: 'haitrinh',
    url: SITE_URL,
    jobTitle: 'Nhà phát triển độc lập',
  },
  potentialAction: {
    '@type': 'SearchAction',
    target: {
      '@type': 'EntryPoint',
      urlTemplate: `${SITE_URL}/ca-bien?q={search_term_string}`,
    },
    'query-input': 'required name=search_term_string',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="vi"
      className={`${lora.variable} ${beVietnamPro.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <head>
        <meta name="theme-color" content="#0c142a" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="SVBVN" />
        <meta name="application-name" content="SVBVN" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteSchema) }}
        />
        {/* ponytail: inline theme script — React 19 warns when <script> is wrapped in a component */}
        <script
          dangerouslySetInnerHTML={{ __html: `(function(){var t=localStorage.getItem('cabien-theme')||'light';document.documentElement.setAttribute('data-theme',t);})()` }}
        />
      </head>
      <body>
        {children}
        <BottomNav />
        <PwaInstallPrompt />
      </body>
    </html>
  )
}

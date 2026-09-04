import type { Metadata } from 'next'
import { Lora, Be_Vietnam_Pro, JetBrains_Mono } from 'next/font/google'
import '@/styles/tokens.css'
import '@/styles/globals.css'
import { ThemeScript } from '@/components/layout/ThemeScript'
import { BottomNav } from '@/components/layout/BottomNav'
import { PwaInstallPrompt } from '@/components/layout/PwaInstallPrompt'

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
    siteName: 'Cẩm Nang Sinh Vật Biển Việt Nam',
    title: 'Cẩm Nang Sinh Vật Biển Việt Nam — Tra cứu & Phân loại học',
    description: 'Cơ sở dữ liệu số hóa 2.436+ loài sinh vật biển Việt Nam — Hệ thống tra cứu danh pháp, hình thái học & sinh học biển.',
    images: [{ url: '/og-default.png', width: 1200, height: 630, alt: 'Cẩm Nang Sinh Vật Biển Việt Nam' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Cẩm Nang Sinh Vật Biển Việt Nam — Tra cứu & Phân loại học',
    description: 'Cơ sở dữ liệu số hóa 2.436+ loài sinh vật biển Việt Nam.',
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
  name: 'Cẩm Nang Sinh Vật Biển Việt Nam',
  alternateName: ['Bảo tàng Hải dương học — Tra cứu Sinh vật biển Việt Nam', 'Cá Biển Việt Nam'],
  url: SITE_URL,
  description: 'Cơ sở dữ liệu số hóa 2.436+ loài sinh vật biển Việt Nam phục vụ nghiên cứu khoa học — Viện Hải dương học, Nha Trang.',
  publisher: {
    '@type': 'Organization',
    name: 'Viện Hải dương học',
    alternateName: 'Institute of Oceanography, VAST',
    url: 'https://vnio.org.vn',
    logo: `${SITE_URL}/logo.png`,
    address: {
      '@type': 'PostalAddress',
      streetAddress: '01 Cầu Đá',
      addressLocality: 'Nha Trang',
      addressRegion: 'Khánh Hòa',
      addressCountry: 'VN',
    },
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
        <ThemeScript />
      </head>
      <body>
        {children}
        <BottomNav />
        <PwaInstallPrompt />
      </body>
    </html>
  )
}

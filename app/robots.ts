import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/admin', '/admin/*', '/api/*'],
      },
    ],
    sitemap: 'https://cam-nang-ca-bien.vercel.app/sitemap.xml',
    host: 'https://cam-nang-ca-bien.vercel.app',
  }
}

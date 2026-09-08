import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/admin', '/admin/*', '/login', '/api/*'],
      },
    ],
    sitemap: 'https://www.tracuusinhvatbien.app/sitemap.xml',
    host: 'https://www.tracuusinhvatbien.app',
  }
}

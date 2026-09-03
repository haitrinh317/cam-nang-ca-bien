import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: '.', // Silence the lockfile warning
  },

  // Redirect old Vite MPA URLs → new Next.js routes
  async redirects() {
    return [
      // index.html → /
      { source: '/index.html', destination: '/', permanent: true },
      // tap.html → /ca-bien (browse by volume)
      { source: '/tap.html', destination: '/ca-bien', permanent: true },
      // browse.html → /ca-bien/taxonomy
      { source: '/browse.html', destination: '/ca-bien/taxonomy', permanent: true },
      // species.html?id=XXX → /ca-bien/XXX
      // Next.js redirects don't support query params → handled by /species route below
      { source: '/species.html', destination: '/ca-bien', permanent: false },
      // admin.html → /admin
      { source: '/admin.html', destination: '/admin', permanent: true },
    ]
  },

  // Optional: headers for security + caching
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
      {
        // Edge Cache cho trang chi tiết loài và cây phân loại (24h)
        source: '/:collection(ca-bien|thuc-vat-bien)/:path*',
        headers: [
          { key: 'Cache-Control', value: 'public, s-maxage=86400, stale-while-revalidate=86400' },
        ],
      },
      {
        // Cache static assets aggressively
        source: '/_next/static/(.*)',
        headers: [{ key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }],
      },
    ]
  },
};

export default nextConfig;


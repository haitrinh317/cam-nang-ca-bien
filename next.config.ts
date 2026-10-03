import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: process.cwd(), // Silence the lockfile warning (must be absolute)
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
      // ran-bien → /bo-sat-bien (Collection upgrade redirect)
      { source: '/ran-bien', destination: '/bo-sat-bien', permanent: true },
      { source: '/ran-bien/:path*', destination: '/bo-sat-bien/:path*', permanent: true },
      { source: '/admin/ran-bien', destination: '/admin/bo-sat-bien', permanent: true },
      { source: '/admin/ran-bien/:path*', destination: '/admin/bo-sat-bien/:path*', permanent: true },
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
          { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains; preload' },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=(), browsing-topics=()' },
        ],
      },
      // Service worker: không để trình duyệt cache file sw.js để cập nhật phiên bản ngay
      {
        source: '/sw.js',
        headers: [
          { key: 'Content-Type', value: 'application/javascript; charset=utf-8' },
          { key: 'Cache-Control', value: 'no-cache, no-store, must-revalidate' },
        ],
      },
      // Edge cache for species/taxonomy pages comes from ISR (dynamic='force-static' + revalidate in each page),
      // not from a custom Cache-Control header (Next overrides it to no-store on dynamic routes).
      // /_next/static: Next.js already serves immutable cache headers — no custom rule needed
    ]
  },
};

export default nextConfig;


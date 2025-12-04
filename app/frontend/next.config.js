/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  
  // Image optimization for production
  images: {
    domains: ['localhost'],
    unoptimized: process.env.NODE_ENV === 'development',
  },
  
  // Disable x-powered-by header
  poweredByHeader: false,
  
  // Production source maps (optional, can disable for smaller bundle)
  productionBrowserSourceMaps: false,
}

module.exports = nextConfig


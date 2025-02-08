/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; connect-src 'self' http://localhost:8000; style-src 'self' 'unsafe-inline';"
          }
        ],
      },
    ]
  },
  reactStrictMode: true,
}

module.exports = nextConfig 
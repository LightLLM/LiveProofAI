/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@liveproof/shared'],
  output: 'standalone',
};

module.exports = nextConfig;

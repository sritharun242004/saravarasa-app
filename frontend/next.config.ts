import type { NextConfig } from "next";

// Derived from the actual configured backend URL at build time — never a
// wildcard hostname, which would turn next/image's optimizer into an
// SSRF-capable open image proxy (it fetches whatever URL matches server-side).
const apiUrl = new URL(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

const csp = [
  "default-src 'self'",
  // Next.js needs 'unsafe-inline'/'unsafe-eval' for its own dev/runtime scripts.
  "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
  "style-src 'self' 'unsafe-inline'",
  `img-src 'self' data: blob: ${apiUrl.origin}`,
  `connect-src 'self' ${apiUrl.origin} https://cognito-idp.*.amazonaws.com https://*.amazoncognito.com`,
  "font-src 'self' data:",
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self'",
].join("; ");

const nextConfig: NextConfig = {
  poweredByHeader: false,
  images: {
    remotePatterns: [
      {
        protocol: apiUrl.protocol.replace(":", "") as "http" | "https",
        hostname: apiUrl.hostname,
        port: apiUrl.port,
        pathname: "/uploads/**",
      },
    ],
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(self), geolocation=(), microphone=()" },
          { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
          { key: "Content-Security-Policy", value: csp },
        ],
      },
    ];
  },
};

export default nextConfig;

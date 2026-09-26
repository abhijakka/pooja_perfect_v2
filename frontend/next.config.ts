import type { NextConfig } from "next";

// Hosts allowed to load the dev server cross-origin. These must stay in step
// with the backend's CORS_ALLOW_ORIGINS, or a device on the LAN can render the
// page but every API call is blocked. Override with NEXT_PUBLIC_ALLOWED_DEV_ORIGINS
// (comma-separated) when your IP changes; "*.local" covers mDNS hostnames.
const DEFAULT_ALLOWED_DEV_ORIGINS = ["192.168.1.34", "127.0.0.1", "*.local"];

const allowedDevOrigins = (process.env.NEXT_PUBLIC_ALLOWED_DEV_ORIGINS ?? "")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

const nextConfig: NextConfig = {
  allowedDevOrigins: allowedDevOrigins.length > 0 ? allowedDevOrigins : DEFAULT_ALLOWED_DEV_ORIGINS,
};

export default nextConfig;

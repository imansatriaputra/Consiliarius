import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",   // Static HTML/CSS/JS — no server needed
  trailingSlash: true, // Netlify prefers /index.html over /
};

export default nextConfig;

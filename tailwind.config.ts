import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "bg-deep": "#0a0f1e",
        "bg-surface": "#0d1117",
        "bg-card": "#111827",
        "bg-card-hover": "#141d2e",
        "accent-blue": "#3b82f6",
        "accent-cyan": "#06b6d4",
        "text-primary": "#f1f5f9",
        "text-secondary": "#64748b",
        "text-muted": "#334155",
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.16, 1, 0.3, 1)",
      },
      boxShadow: {
        "glow-blue": "0 0 24px rgba(59, 130, 246, 0.15)",
        "glow-cyan": "0 0 32px rgba(6, 182, 212, 0.12)",
        "glow-blue-strong": "0 0 40px rgba(59, 130, 246, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;

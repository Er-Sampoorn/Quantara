/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        surface: "#0f172a",
        surfaceBorder: "#1e293b",
        surfaceHover: "#1e293b80",
        primary: {
          DEFAULT: "#06b6d4", // cyan
          foreground: "#ffffff",
          glow: "rgba(6, 182, 212, 0.15)",
        },
        success: {
          DEFAULT: "#10b981", // emerald
          glow: "rgba(16, 185, 129, 0.15)",
        },
        danger: {
          DEFAULT: "#f43f5e", // rose
          glow: "rgba(244, 63, 94, 0.15)",
        },
        warning: {
          DEFAULT: "#f59e0b", // amber
          glow: "rgba(245, 158, 11, 0.15)",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
      },
    },
  },
  plugins: [],
};

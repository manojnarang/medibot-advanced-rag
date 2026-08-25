import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef7f6",
          100: "#d3ebe8",
          200: "#a7d7d1",
          300: "#78bfb6",
          400: "#4fa79b",
          500: "#2f8c7f",
          600: "#237166",
          700: "#1c5a52",
          800: "#164541",
          900: "#0f302d",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;

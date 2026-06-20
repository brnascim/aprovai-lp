import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0A0D12", surface: "#13171E", surface2: "#1A1F29",
        line: "rgba(255,255,255,0.08)", ink: "#EEF1F6", muted: "#98A2B2",
        accent: "#FF7A1A", accent2: "#FFB02E", trust: "#34D399", danger: "#F87171",
      },
      fontFamily: {
        display: ['"Space Grotesk"', "sans-serif"],
        body: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;

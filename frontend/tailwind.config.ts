import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}", "./features/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: { colors: { brand: { 50: "#eff8ff", 100: "#dcefff", 500: "#2886d8", 600: "#1672c4", 700: "#105c9f" } } } },
  plugins: [],
};
export default config;

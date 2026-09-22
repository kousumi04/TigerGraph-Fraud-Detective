/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0d1117",
        surface: "#161b22",
        "surface-border": "#30363d",
        accent: "#1f6feb",
        danger: "#f85149",
        warning: "#d29922",
        success: "#238636",
        muted: "#8b949e",
        text: "#c9d1d9",
        heading: "#f0f6fc"
      },
      fontFamily: {
        mono: ["Consolas", "Courier New", "monospace"],
      }
    },
  },
  plugins: [],
};
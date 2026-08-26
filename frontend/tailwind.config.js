/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        tv: {
          bg: '#131722',
          card: '#1e222d',
          border: '#2a2e39',
          hover: '#2a2e39',
          text: '#d1d4dc',
          muted: '#787b86',
          green: '#22c55e',
          red: '#ef4444',
          gold: '#f59e0b',
          blue: '#3b82f6',
          purple: '#a855f7'
        }
      }
    },
  },
  plugins: [],
}

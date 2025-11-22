/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'devtrack-bg': '#0b1020',
        'devtrack-card': '#151a2b',
        'devtrack-accent': '#4f46e5',
        'devtrack-text': '#f9fafb',
        'devtrack-muted': '#9ca3af',
        'devtrack-danger': '#f97373',
        'devtrack-success': '#4ade80',
        'devtrack-border': '#1f2937',
      },
    },
  },
  plugins: [],
}


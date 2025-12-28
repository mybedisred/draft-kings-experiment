/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme colors
        'dk-bg': '#0f0d1a',
        'dk-bg-light': '#1a1625',
        'dk-card': '#1e1a2e',
        'dk-card-hover': '#252136',
        'dk-border': '#2d2640',
        'dk-accent': '#8b5cf6',
        'dk-accent-hover': '#7c3aed',
        'dk-live': '#ef4444',
        'dk-positive': '#22c55e',
        'dk-negative': '#ef4444',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': {
            boxShadow: '0 0 5px #ef4444, 0 0 10px #ef4444',
            opacity: '1'
          },
          '50%': {
            boxShadow: '0 0 10px #ef4444, 0 0 20px #ef4444',
            opacity: '0.8'
          },
        }
      }
    },
  },
  plugins: [],
}

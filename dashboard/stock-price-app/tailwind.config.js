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
        // Trading Theme Colors
        trading: {
          dark: '#0a0a0f',
          darker: '#050508',
          card: '#12121a',
          cardHover: '#1a1a24',
          border: '#1e1e2d',
          accent: '#6366f1',
          accentHover: '#818cf8',
        },
        // Signal Colors
        signal: {
          buy: '#10b981',
          strongBuy: '#059669',
          ultraBuy: '#047857',
          sell: '#ef4444',
          strongSell: '#dc2626',
          hold: '#6b7280',
          watch: '#f59e0b',
          ready: '#3b82f6',
          execute: '#10b981',
        },
        // Trend Colors
        trend: {
          up: '#10b981',
          down: '#ef4444',
          neutral: '#6b7280',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          'primary': '#3B82F6',
          'primary-dark': '#2563EB',
          'secondary': '#10B981',
          'accent': '#8B5CF6',
          'background': '#F9FAFB',
          'surface': '#FFFFFF',
          'text-primary': '#111827',
          'text-secondary': '#6B7280',
          'border': '#E5E7EB',
        },
        animation: {
          'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
          'slide-up': 'slideUp 0.3s ease-out',
        },
        keyframes: {
          slideUp: {
            '0%': { transform: 'translateY(10px)', opacity: '0' },
            '100%': { transform: 'translateY(0)', opacity: '1' },
          },
        },
      },
    },
    plugins: [],
  }
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1E3A5F',
          mid: '#2D5F8A',
          soft: '#5B8CB8',
        },
        accent: {
          DEFAULT: '#D98E4A',
        },
        danger: {
          DEFAULT: '#C0392B',
        },
        warning: {
          DEFAULT: '#E8A33D',
        },
        success: {
          DEFAULT: '#2E8B57',
        },
        base: {
          bg: '#F4F1EC',
          surface: '#FFFFFF',
          text: '#1C2733',
          muted: '#8A97A5',
          border: '#DDE3E8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

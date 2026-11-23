/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          50: '#f0f5fa',
          100: '#e1ecf5',
          200: '#c3d9eb',
          300: '#94bcdd',
          400: '#5f9bcc',
          500: '#3b7eb8',
          600: '#2b6499',
          700: '#23507d',
          800: '#1b3f63',
          900: '#0f243a',
          950: '#091523',
        },
        assam: {
          green: '#1e6b37',
          gold: '#c2921e',
        }
      },
    },
  },
  plugins: [],
}

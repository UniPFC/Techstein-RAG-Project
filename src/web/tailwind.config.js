/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a73e8',
        'primary-hover': '#1557b0',
        secondary: '#34a853',
        success: '#34a853',
        error: '#ea4335',
        warning: '#fbbc04',
        'text-primary': '#202124',
        'text-secondary': '#5f6368',
        'border': '#dadce0',
        'surface-1': '#ffffff',
        'surface-2': '#f1f3f4',
        'surface-3': '#e8eaed',
      },
    },
  },
  plugins: [],
}

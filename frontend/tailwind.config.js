/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: '#5eead4',
          500: '#34d399',
        },
      },
      borderRadius: {
        xl: '14px',
      },
      boxShadow: {
        'card-lg': '0 18px 40px rgba(2,6,23,0.65)',
        'soft-lg': '0 8px 30px rgba(2,6,23,0.35)'
      },
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
      },
      keyframes: {
        pop: {
          '0%': { transform: 'scale(.98)', opacity: '0' },
          '60%': { transform: 'scale(1.02)', opacity: '1' },
          '100%': { transform: 'scale(1)', opacity: '1' }
        },
        float: {
          '0%': { transform: 'translateY(6px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        },
        subtlefade: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        }
      },
      animation: {
        pop: 'pop .28s cubic-bezier(.2,.9,.25,1) both',
        float: 'float .32s cubic-bezier(.2,.9,.25,1) both',
        subtlefade: 'subtlefade .22s ease both'
      },
      transitionDuration: {
        250: '250ms',
        350: '350ms'
      }
    }
  },
  plugins: []
}

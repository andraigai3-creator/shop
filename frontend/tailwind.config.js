/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Цвета бренда: зелёный + золотой — традиционные исламские цвета
      colors: {
        brand: {
          green:      '#1a7a4a',  // основной зелёный
          'green-light': '#2da06a',
          'green-dark':  '#0f5232',
          gold:       '#c9a227',  // золотой акцент
          'gold-light':  '#e8c547',
          cream:      '#fdf6e3',  // фон-крем
        },
        // Переменные Telegram тем — используем CSS-переменные
        tg: {
          bg:        'var(--tg-theme-bg-color, #ffffff)',
          text:      'var(--tg-theme-text-color, #222222)',
          hint:      'var(--tg-theme-hint-color, #999999)',
          link:      'var(--tg-theme-link-color, #2678b6)',
          button:    'var(--tg-theme-button-color, #1a7a4a)',
          'btn-text':'var(--tg-theme-button-text-color, #ffffff)',
          'sec-bg':  'var(--tg-theme-secondary-bg-color, #f5f5f5)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'slide-up':   'slideUp 0.3s ease-out',
        'fade-in':    'fadeIn 0.2s ease-in',
        'bounce-in':  'bounceIn 0.4s ease-out',
      },
      keyframes: {
        slideUp: {
          '0%':   { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        bounceIn: {
          '0%':   { transform: 'scale(0.8)', opacity: '0' },
          '70%':  { transform: 'scale(1.05)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

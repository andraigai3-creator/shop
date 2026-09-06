/**
 * useTelegram — хук для работы с Telegram WebApp API.
 * Источник паттерна: telegram-web-app-shop/src/hooks/useTelegram.ts
 *
 * Возвращает объект Telegram.WebApp или null (если открыто в браузере для теста).
 */

const useTelegram = () => {
  // window.Telegram появляется после загрузки telegram-web-app.js
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp
  }
  // Заглушка для разработки в обычном браузере
  return null
}

export default useTelegram

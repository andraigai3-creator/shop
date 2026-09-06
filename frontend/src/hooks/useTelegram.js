/**
 * useTelegram — хук для работы с Telegram WebApp API.
 * Источник паттерна: telegram-web-app-shop/src/hooks/useTelegram.ts
 *
 * Возвращает объект Telegram.WebApp или null (если открыто в браузере для теста).
 * Использует прямое обращение к window.Telegram для надёжности.
 */
import { useState, useEffect } from 'react'

const useTelegram = () => {
  const [tg, setTg] = useState(() => {
    // Инициализация при первом рендере
    return (typeof window !== 'undefined' && window.Telegram?.WebApp) || null
  })

  useEffect(() => {
    // Повторная проверка после монтирования (на случай async загрузки SDK)
    if (!tg && window.Telegram?.WebApp) {
      setTg(window.Telegram.WebApp)
    }
  }, [tg])

  return tg
}

export default useTelegram

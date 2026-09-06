/**
 * Cart — боковая шторка (drawer) корзины.
 * Источник паттерна: telegram-web-app-shop/src/pages/user/cart/index.tsx
 *
 * Логика оформления заказа:
 *   - Вызывает Telegram.WebApp.sendData(JSON.stringify(cartData))
 *   - Это отправляет данные в бот через web_app_data (см. telegram-web-app-bot-example)
 *   - После sendData WebApp закрывается автоматически
 *
 * Props:
 *   isOpen        — bool
 *   onClose       — () => void
 *   items         — [{ id, name, price, qty }]
 *   totalPrice    — number
 *   onChangeQty   — (id, delta) => void
 *   onRemove      — (id) => void
 *   onClear       — () => void
 *   tg            — объект Telegram.WebApp или null
 */

import React, { useEffect } from 'react'

const Cart = ({ isOpen, onClose, items, totalPrice, onChangeQty, onRemove, onClear, tg }) => {

  // Блокируем скролл фона когда корзина открыта
  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  /**
   * Оформить заказ:
   * 1. Формируем JSON с товарами
   * 2. Отправляем в бот через sendData
   * 3. WebApp закроется автоматически
   */
  const handleCheckout = () => {
    if (items.length === 0) return

    // Данные которые получит бот
    const orderData = {
      items: items.map(i => ({
        id:    i.id,
        name:  i.name,
        price: i.price,
        qty:   i.qty,
        total: i.price * i.qty,
      })),
      totalPrice,
      currency: 'RUB',
      timestamp: new Date().toISOString(),
    }

    // Пробуем получить Telegram WebApp напрямую (надёжнее чем через props)
    const telegram = tg || (typeof window !== 'undefined' && window.Telegram?.WebApp) || null

    if (telegram && telegram.sendData) {
      // Реальная отправка в Telegram-бот
      telegram.sendData(JSON.stringify(orderData))
      // WebApp закроется автоматически после sendData
    } else {
      // Режим разработки (открыто в браузере)
      console.log('📦 Данные заказа (dev-режим):', orderData)
      alert(`✅ Заказ сформирован!\n\nТоваров: ${items.length}\nСумма: ${totalPrice.toLocaleString('ru-RU')} ₽\n\nОткройте магазин через бота Telegram для оформления.`)
    }
  }

  return (
    <>
      {/* Затемнённый фон */}
      <div
        className={`fixed inset-0 z-50 bg-black/50 backdrop-blur-sm transition-opacity duration-300
                    ${isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
      />

      {/* Шторка */}
      <div
        className={`fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-3xl shadow-2xl
                    transition-transform duration-300 ease-out max-h-[90vh] flex flex-col
                    ${isOpen ? 'translate-y-0' : 'translate-y-full'}`}
      >
        {/* Ручка */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 bg-gray-300 rounded-full" />
        </div>

        {/* Заголовок */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-800">
            🛒 Корзина
            {items.length > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({items.length} позиц.)
              </span>
            )}
          </h2>
          <div className="flex items-center gap-2">
            {items.length > 0 && (
              <button
                onClick={onClear}
                className="text-xs text-red-400 hover:text-red-600 active:scale-95 transition-all
                           bg-red-50 hover:bg-red-100 px-2 py-1 rounded-lg"
              >
                Очистить
              </button>
            )}
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100
                         hover:bg-gray-200 text-gray-500 text-xl transition-colors"
            >
              ×
            </button>
          </div>
        </div>

        {/* Список товаров */}
        <div className="flex-1 overflow-y-auto px-5 py-3">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <span className="text-6xl mb-4">🛍️</span>
              <p className="text-gray-500 font-medium">Корзина пуста</p>
              <p className="text-gray-400 text-sm mt-1">
                Добавьте товары из каталога
              </p>
            </div>
          ) : (
            <ul className="space-y-3">
              {items.map(item => (
                <li
                  key={item.id}
                  className="flex items-center gap-3 bg-gray-50 rounded-xl p-3"
                >
                  {/* Название и цена */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 line-clamp-2 leading-snug">
                      {item.name}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {item.price.toLocaleString('ru-RU')} ₽ × {item.qty}
                    </p>
                    <p className="text-sm font-bold text-brand-green mt-0.5">
                      {(item.price * item.qty).toLocaleString('ru-RU')} ₽
                    </p>
                  </div>

                  {/* Счётчик */}
                  <div className="flex items-center gap-1.5 bg-white border border-gray-200 rounded-xl">
                    <button
                      onClick={() => onChangeQty(item.id, -1)}
                      className="w-8 h-8 flex items-center justify-center text-brand-green
                                 font-bold text-lg hover:bg-gray-100 rounded-l-xl transition-colors"
                    >
                      −
                    </button>
                    <span className="text-sm font-bold text-gray-800 min-w-[20px] text-center">
                      {item.qty}
                    </span>
                    <button
                      onClick={() => onChangeQty(item.id, +1)}
                      className="w-8 h-8 flex items-center justify-center text-brand-green
                                 font-bold text-lg hover:bg-gray-100 rounded-r-xl transition-colors"
                    >
                      +
                    </button>
                  </div>

                  {/* Удалить */}
                  <button
                    onClick={() => onRemove(item.id)}
                    className="text-gray-400 hover:text-red-500 active:scale-95
                               transition-all ml-1 text-xl leading-none"
                    aria-label="Удалить"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Итог и кнопка оформления */}
        {items.length > 0 && (
          <div className="px-5 py-4 border-t border-gray-100 bg-white">
            <div className="flex items-center justify-between mb-3">
              <span className="text-gray-600 font-medium">Итого:</span>
              <span className="text-xl font-bold text-brand-green">
                {totalPrice.toLocaleString('ru-RU')} ₽
              </span>
            </div>
            <button
              onClick={handleCheckout}
              className="w-full bg-brand-green hover:bg-brand-green-light active:scale-[0.98]
                         text-white font-bold py-4 rounded-2xl text-base transition-all duration-150
                         shadow-lg shadow-green-200 flex items-center justify-center gap-2"
            >
              <span>✅</span>
              <span>Оформить заказ</span>
            </button>
            <p className="text-center text-xs text-gray-400 mt-2">
              После нажатия мы свяжемся с вами в Telegram
            </p>
          </div>
        )}
      </div>
    </>
  )
}

export default Cart

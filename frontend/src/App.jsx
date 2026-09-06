/**
 * App — корневой компонент Telegram Mini App «Исламский магазин».
 *
 * Порядок инициализации (из telegram-web-app-bot-example):
 *   1. Telegram.WebApp.ready()  — сигнализируем TG что WebApp загружен
 *   2. Telegram.WebApp.expand() — раскрываем на всю высоту экрана
 *
 * Поток заказа:
 *   Каталог → Корзина → «Оформить заказ» → sendData(JSON) → бот получает web_app_data
 */

import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import CategoryFilter from './components/CategoryFilter'
import ProductCard from './components/ProductCard'
import Cart from './components/Cart'
import useCart from './hooks/useCart'
import useTelegram from './hooks/useTelegram'
import { PRODUCTS } from './data/products'

const App = () => {
  const tg = useTelegram()

  // Активная категория фильтра
  const [activeCategory, setActiveCategory] = useState('all')

  // Открытие/закрытие корзины
  const [isCartOpen, setIsCartOpen] = useState(false)

  // Всё управление корзиной
  const {
    items, addToCart, removeFromCart, changeQty, clearCart, getQty,
    totalPrice, totalItems,
  } = useCart()

  // ── Инициализация Telegram WebApp ─────────────────────────────────────────
  useEffect(() => {
    if (tg) {
      // Сообщаем Telegram что WebApp готов (скрывает лоадер)
      tg.ready()
      // Разворачиваем на полный экран
      tg.expand()
      // Устанавливаем цвет хедера под наш бренд
      tg.setHeaderColor('#1a7a4a')
    }
  }, [tg])

  // ── Фильтрация товаров ───────────────────────────────────────────────────
  const filteredProducts = activeCategory === 'all'
    ? PRODUCTS
    : PRODUCTS.filter(p => p.category === activeCategory)

  // ── Рендер ──────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50 pb-6">
      {/* Шапка */}
      <Header
        totalItems={totalItems}
        onCartClick={() => setIsCartOpen(true)}
      />

      {/* Фильтр категорий */}
      <CategoryFilter
        activeCategory={activeCategory}
        onSelect={setActiveCategory}
      />

      {/* Сетка товаров */}
      <main className="px-3 pt-4">
        {filteredProducts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <span className="text-5xl mb-3">📦</span>
            <p className="text-gray-500">В этой категории пока нет товаров</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {filteredProducts.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                qty={getQty(product.id)}
                onAdd={() => addToCart(product)}
                onRemove={() => changeQty(product.id, -1)}
              />
            ))}
          </div>
        )}
      </main>

      {/* Плавающая кнопка «Корзина» (появляется когда есть товары) */}
      {totalItems > 0 && !isCartOpen && (
        <button
          onClick={() => setIsCartOpen(true)}
          className="fixed bottom-5 left-1/2 -translate-x-1/2 z-40
                     bg-brand-green text-white font-bold
                     px-6 py-3.5 rounded-full shadow-xl shadow-green-200
                     flex items-center gap-2 animate-slide-up
                     hover:bg-brand-green-light active:scale-95 transition-all"
        >
          <span>🛒</span>
          <span>Корзина</span>
          <span className="bg-white text-brand-green text-xs font-bold px-2 py-0.5 rounded-full">
            {totalItems}
          </span>
          <span className="text-sm font-normal opacity-90">
            · {totalPrice.toLocaleString('ru-RU')} ₽
          </span>
        </button>
      )}

      {/* Корзина-шторка */}
      <Cart
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        items={items}
        totalPrice={totalPrice}
        onChangeQty={changeQty}
        onRemove={removeFromCart}
        onClear={clearCart}
        tg={tg}
      />
    </div>
  )
}

export default App

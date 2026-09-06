/**
 * useCart — хук управления корзиной.
 * Хранит состояние в localStorage, чтобы корзина не сбрасывалась при перезагрузке.
 *
 * Методы:
 *   addToCart(product)       — добавить товар или увеличить количество
 *   removeFromCart(id)       — удалить позицию полностью
 *   changeQty(id, delta)     — изменить количество (+1 / -1), удалит если станет 0
 *   clearCart()              — очистить всю корзину
 *   totalPrice               — итоговая сумма
 *   totalItems               — общее количество единиц товара
 */

import { useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'islamic_shop_cart'

const useCart = () => {
  // Загружаем корзину из localStorage при первом рендере
  const [items, setItems] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })

  // Сохраняем корзину в localStorage при каждом изменении
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }, [items])

  /** Добавить товар. Если уже есть — увеличить qty на 1. */
  const addToCart = useCallback((product) => {
    setItems(prev => {
      const existing = prev.find(i => i.id === product.id)
      if (existing) {
        return prev.map(i =>
          i.id === product.id ? { ...i, qty: i.qty + 1 } : i
        )
      }
      // Добавляем только нужные поля (без тяжёлых данных)
      return [...prev, { id: product.id, name: product.name, price: product.price, qty: 1 }]
    })
  }, [])

  /** Убрать весь товар по id из корзины. */
  const removeFromCart = useCallback((id) => {
    setItems(prev => prev.filter(i => i.id !== id))
  }, [])

  /** Изменить количество: delta = +1 или -1. При qty = 0 — удалить позицию. */
  const changeQty = useCallback((id, delta) => {
    setItems(prev =>
      prev
        .map(i => i.id === id ? { ...i, qty: i.qty + delta } : i)
        .filter(i => i.qty > 0)
    )
  }, [])

  /** Очистить корзину. */
  const clearCart = useCallback(() => {
    setItems([])
  }, [])

  /** Получить количество единиц конкретного товара в корзине. */
  const getQty = useCallback((id) => {
    return items.find(i => i.id === id)?.qty ?? 0
  }, [items])

  // Итоговая сумма
  const totalPrice = items.reduce((sum, i) => sum + i.price * i.qty, 0)

  // Общее количество позиций (единиц)
  const totalItems = items.reduce((sum, i) => sum + i.qty, 0)

  return {
    items,
    addToCart,
    removeFromCart,
    changeQty,
    clearCart,
    getQty,
    totalPrice,
    totalItems,
  }
}

export default useCart

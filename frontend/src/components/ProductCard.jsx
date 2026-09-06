/**
 * ProductCard — карточка товара в каталоге.
 * Источник паттерна: telegram-web-app-shop/src/components/product/card.tsx
 *
 * Props:
 *   product       — объект товара из products.js
 *   qty           — текущее количество в корзине (0 = не добавлен)
 *   onAdd         — () => void  — добавить/увеличить
 *   onRemove      — () => void  — уменьшить/убрать
 */

import React from 'react'

const ProductCard = ({ product, qty, onAdd, onRemove }) => {
  const { name, description, price, image, badge } = product

  return (
    <div className="bg-white rounded-2xl shadow-sm overflow-hidden transition-all duration-200 hover:shadow-md active:scale-[0.99]">
      {/* Фото товара */}
      <div className="relative">
        <img
          src={image}
          alt={name}
          loading="lazy"
          className="w-full h-44 object-cover"
          onError={(e) => {
            // Заглушка если изображение не загрузилось
            e.target.src = `https://placehold.co/400x280/1a7a4a/white?text=${encodeURIComponent(name.slice(0, 10))}`
          }}
        />
        {badge && (
          <span className="absolute top-2 left-2 bg-brand-gold text-white text-xs font-bold
                           px-2 py-0.5 rounded-full shadow">
            {badge}
          </span>
        )}
      </div>

      {/* Информация */}
      <div className="p-3">
        <h3 className="font-semibold text-gray-800 text-sm leading-snug line-clamp-2 mb-1">
          {name}
        </h3>
        <p className="text-gray-500 text-xs leading-relaxed line-clamp-2 mb-3">
          {description}
        </p>

        {/* Цена + кнопки */}
        <div className="flex items-center justify-between gap-2">
          <span className="text-brand-green font-bold text-base">
            {price.toLocaleString('ru-RU')} ₽
          </span>

          {qty === 0 ? (
            /* Кнопка «В корзину» */
            <button
              onClick={onAdd}
              className="flex items-center gap-1 bg-brand-green hover:bg-brand-green-light
                         active:scale-95 text-white text-sm font-medium px-3 py-1.5
                         rounded-xl transition-all duration-150 shadow-sm"
            >
              <span>+</span>
              <span>В корзину</span>
            </button>
          ) : (
            /* Счётчик количества */
            <div className="flex items-center gap-2 bg-gray-100 rounded-xl overflow-hidden">
              <button
                onClick={onRemove}
                className="w-8 h-8 flex items-center justify-center text-brand-green
                           font-bold text-lg hover:bg-gray-200 active:bg-gray-300 transition-colors"
              >
                −
              </button>
              <span className="text-sm font-bold text-gray-800 min-w-[20px] text-center">
                {qty}
              </span>
              <button
                onClick={onAdd}
                className="w-8 h-8 flex items-center justify-center text-brand-green
                           font-bold text-lg hover:bg-gray-200 active:bg-gray-300 transition-colors"
              >
                +
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProductCard

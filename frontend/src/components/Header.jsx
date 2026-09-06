/**
 * Header — верхняя панель магазина.
 * Показывает логотип, название и иконку корзины с количеством товаров.
 */

import React from 'react'

const Header = ({ totalItems, onCartClick }) => {
  return (
    <header className="sticky top-0 z-40 bg-brand-green shadow-md">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Логотип и название */}
        <div className="flex items-center gap-2">
          <span className="text-2xl">🕌</span>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">
              Tazakkur
            </h1>
            <p className="text-green-200 text-xs leading-tight">
              Исламский магазин
            </p>
          </div>
        </div>

        {/* Кнопка корзины */}
        <button
          onClick={onCartClick}
          className="relative flex items-center gap-1 bg-white/20 hover:bg-white/30 active:bg-white/40 
                     text-white rounded-xl px-3 py-2 transition-all duration-150"
          aria-label="Открыть корзину"
        >
          <span className="text-xl">🛒</span>
          {totalItems > 0 && (
            <span className="absolute -top-1.5 -right-1.5 bg-brand-gold text-white text-xs font-bold
                             rounded-full min-w-[20px] h-5 flex items-center justify-center px-1
                             animate-bounce-in">
              {totalItems > 99 ? '99+' : totalItems}
            </span>
          )}
        </button>
      </div>
    </header>
  )
}

export default Header

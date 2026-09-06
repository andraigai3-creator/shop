/**
 * CategoryFilter — горизонтальный скролл с фильтрами по категориям.
 * Источник паттерна: telegram-web-app-shop/src/pages/user/categories/list.tsx
 */

import React from 'react'
import { CATEGORIES } from '../data/products'

const CategoryFilter = ({ activeCategory, onSelect }) => {
  return (
    <div className="sticky top-[57px] z-30 bg-white/95 backdrop-blur border-b border-gray-100 shadow-sm">
      <div className="flex gap-2 overflow-x-auto px-4 py-2.5 scrollbar-hide">
        {CATEGORIES.map(cat => {
          const isActive = activeCategory === cat.id
          return (
            <button
              key={cat.id}
              onClick={() => onSelect(cat.id)}
              className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full
                         text-sm font-medium transition-all duration-200 whitespace-nowrap
                         ${isActive
                           ? 'bg-brand-green text-white shadow-md scale-105'
                           : 'bg-gray-100 text-gray-600 hover:bg-gray-200 active:scale-95'
                         }`}
            >
              <span className="text-base">{cat.emoji}</span>
              <span>{cat.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default CategoryFilter

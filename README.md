# 🕌 Tazakkur — Исламский магазин1

Telegram Mini App интернет-магазина исламских товаров.  
Фронтенд: **React + Vite + TailwindCSS**  
Бэкенд: **Python + aiogram 3**

---

## Структура проекта

```
islamic-shop/
├── frontend/          # React WebApp (Telegram Mini App)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx          # Шапка с кнопкой корзины
│   │   │   ├── CategoryFilter.jsx  # Горизонтальный фильтр категорий
│   │   │   ├── ProductCard.jsx     # Карточка товара
│   │   │   └── Cart.jsx            # Корзина-шторка + кнопка оформления
│   │   ├── hooks/
│   │   │   ├── useTelegram.js      # Хук для Telegram.WebApp API
│   │   │   └── useCart.js          # Хук управления корзиной
│   │   ├── data/
│   │   │   └── products.js         # Каталог товаров (17 позиций)
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── backend/
│   ├── bot.py          # Telegram-бот на aiogram 3
│   ├── catalog.json    # Копия каталога для бота
│   ├── requirements.txt
│   ├── .env            # Твои токены (не коммитить!)
│   └── .env.example    # Шаблон .env
└── README.md
```

---

## Шаг 1 — Настройка через BotFather

1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. Создай нового бота: `/newbot`
3. Скопируй **токен бота**
4. Настрой кнопку меню с WebApp:
   ```
   /setmenubutton
   ```
   - Выбери своего бота
   - Введи URL твоего задеплоенного фронтенда (см. Шаг 2)
   - Введи текст кнопки, например: `🛍️ Магазин`
5. Узнай свой `chat_id` — напиши боту [@userinfobot](https://t.me/userinfobot), он покажет твой ID

---

## Шаг 2 — Деплой фронтенда на Vercel

### Вариант A: через Vercel CLI (рекомендуется)

```bash
cd frontend

# Установить зависимости
npm install

# Собрать проект
npm run build

# Установить Vercel CLI
npm i -g vercel

# Задеплоить
vercel deploy --prod
```

Vercel выдаст URL вида `https://islamic-shop-xxx.vercel.app` — это и есть `WEBAPP_URL`.

### Вариант B: через GitHub

1. Загрузи проект на GitHub
2. Зайди на [vercel.com](https://vercel.com) → «New Project»
3. Подключи репозиторий, выбери папку `frontend` как Root Directory
4. Нажми Deploy

### Вариант B2: GitHub Pages

```bash
cd frontend
npm install
npm install --save-dev gh-pages

# В package.json добавь:
# "homepage": "https://USERNAME.github.io/islamic-shop",
# "scripts": { "deploy": "gh-pages -d dist" }

npm run build
npm run deploy
```

> **Важно:** Telegram WebApp требует **HTTPS**. Vercel и GitHub Pages дают HTTPS автоматически.

---

## Шаг 3 — Настройка и запуск бота

```bash
cd backend

# Создай .env файл
cp .env.example .env
```

Заполни `.env`:
```env
BOT_TOKEN=123456789:AAxxxxxx      # Токен от BotFather
SELLER_CHAT_ID=123456789           # Твой chat_id (получи у @userinfobot)
WEBAPP_URL=https://your-app.vercel.app  # URL из Шага 2
SELLER_USERNAME=tazakkur_support   # Твой Telegram-юзернейм без @
```

```bash
# Установить зависимости Python
pip install -r requirements.txt

# Запустить бота
python bot.py
```

---

## Шаг 4 — Настройка кнопки WebApp в BotFather

После деплоя фронтенда введи в BotFather:

```
/setmenubutton
```

Выбери бота → введи URL → введи название кнопки.

Или через `/mybots` → выбери бота → `Bot Settings` → `Menu Button` → `Configure menu button`.

---

## Как работает поток заказа

```
Пользователь в Telegram
       │
       ▼
Нажимает /start → бот отправляет кнопку с WebApp URL
       │
       ▼
Открывается WebApp (фронтенд на React)
       │
       ▼
Пользователь выбирает товары → добавляет в корзину
       │
       ▼
Нажимает «Оформить заказ»
       │
       ▼
Фронтенд вызывает: Telegram.WebApp.sendData(JSON.stringify(cart))
       │
       ▼
WebApp закрывается автоматически
       │
       ▼
Бот получает событие web_app_data
       │
       ├──► Пересылает заказ продавцу (SELLER_CHAT_ID)
       │    с кнопкой «Написать покупателю»
       │
       └──► Отправляет покупателю подтверждение
            с кнопкой «Связаться с продавцом»
```

---

## Тестирование фронтенда локально

```bash
cd frontend
npm install
npm run dev
```

Открой `http://localhost:5173` в браузере.

> В обычном браузере объект `window.Telegram` недоступен, поэтому кнопка «Оформить заказ» выведет данные в `console.log` и `alert` (DEV-режим).

Для полноценного тестирования используй [Telegram Dev Tools](https://core.telegram.org/bots/webapps#testing-mini-apps).

---

## Добавление/изменение товаров

Отредактируй файл `frontend/src/data/products.js` — добавь объект в массив `PRODUCTS`:

```js
{
  id: 18,
  name: 'Название товара',
  description: 'Описание товара',
  price: 1500,           // в рублях
  category: 'prayer',   // clothing | books | prayer | perfume | accessories
  image: 'https://...',  // URL изображения
  badge: 'Новинка',      // необязательно: Хит / Новинка / Премиум
},
```

Обнови также `backend/catalog.json` для синхронности.

---

## Стек

| Часть      | Технология                             |
|------------|----------------------------------------|
| Фронтенд   | React 18, Vite 5, TailwindCSS 3        |
| Бэкенд     | Python 3.10+, aiogram 3.13             |
| Деплой     | Vercel (фронтенд), VPS/Railway (бот)   |
| Конфиг     | python-dotenv (.env файл)              |

---

## Шаблоны-источники

- [telegram-web-app-bot-example](https://github.com/revenkroz/telegram-web-app-bot-example) — логика sendData
- [telegram-web-app-shop](https://github.com/mojtaba1180/telegram-web-app-shop) — UI структура
- [Shop-bot](https://github.com/DaniilDonskoy/Shop-bot) — структура бота
- [Telegram-shop](https://github.com/interlumpen/Telegram-shop) — продвинутый бот

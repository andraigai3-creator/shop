# Islamic Shop — Telegram Mini App

A full-stack Islamic e-commerce shop delivered as a **Telegram Mini App** (WebApp).

## Structure

```
islamic-shop/
├── frontend/        # Vite + React + TypeScript + Tailwind CSS (Telegram Mini App UI)
├── backend/         # Python aiogram Telegram bot (shop logic, admin, orders)
└── _templates/      # Reference repos (excluded from git — see .gitignore)
```

## Frontend (`frontend/`)

- **Framework:** Vite + React 18 + TypeScript
- **Styling:** Tailwind CSS + SCSS
- **Telegram SDK:** `@twa-dev/sdk` via `window.Telegram.WebApp`
- Key pages: home, categories, product list/detail, cart, checkout, payment, profile, orders, admin

## Backend (`backend/`)

- **Framework:** Python + aiogram (async Telegram Bot API)
- **Features:** catalog browsing, cart management, order flow, admin panel, delivery status
- **Storage:** configurable via `utils/db/`

## Getting Started

### Frontend

```bash
cd frontend
yarn install
yarn dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # set BOT_TOKEN and other vars
python loader.py
```

## Reference

The `_templates/` directory contains raw upstream repos used for reference during development — they are **not** part of the deployable project and are excluded from version control.

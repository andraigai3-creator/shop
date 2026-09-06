"""
Telegram-бот для исламского магазина «Tazakkur».
Написан на aiogram 3.x (современный async Python).

Источники логики:
  - Структура обработчиков: Shop-bot/handlers/user/
  - web_app_data: telegram-web-app-bot-example + aiogram docs
  - Паттерн .env: Telegram-shop/bot/misc/env.py

Установка:
    pip install -r requirements.txt

Запуск:
    python bot.py
"""

import asyncio
import json
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from dotenv import load_dotenv

# ── Загрузка конфигурации из .env ────────────────────────────────────────────
load_dotenv()

BOT_TOKEN      = os.getenv("BOT_TOKEN")          # Токен от BotFather
SELLER_CHAT_ID = int(os.getenv("SELLER_CHAT_ID"))  # Твой chat_id (продавца)
WEBAPP_URL     = os.getenv("WEBAPP_URL")          # URL задеплоенного фронтенда
SELLER_USERNAME = os.getenv("SELLER_USERNAME", "tazakkur_support")  # @юзернейм продавца

if not BOT_TOKEN or not WEBAPP_URL or not SELLER_CHAT_ID:
    raise RuntimeError(
        "Заполни .env файл: BOT_TOKEN, SELLER_CHAT_ID, WEBAPP_URL обязательны!"
    )

# ── Инициализация бота ───────────────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()

# ── Логирование ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# /start — приветствие и кнопка для открытия WebApp
# Источник: Shop-bot/app.py → cmd_start
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Приветственное сообщение с кнопкой открытия WebApp-магазина."""

    user_name = message.from_user.first_name or "дорогой покупатель"

    # Клавиатура с кнопкой WebApp
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍️ Открыть магазин",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Связаться с продавцом",
                    url=f"https://t.me/{SELLER_USERNAME}",
                )
            ],
        ]
    )

    await message.answer(
        text=(
            f"Ассаляму алейкум, {user_name}! 🌙\n\n"
            "Добро пожаловать в <b>Tazakkur</b> — ваш исламский магазин.\n\n"
            "У нас вы найдёте:\n"
            "👘 Одежду (джуббы, абайи, хиджабы)\n"
            "📚 Исламскую литературу\n"
            "🕌 Атрибуты для намаза\n"
            "🌹 Халяльную парфюмерию\n"
            "📿 Аксессуары и подарки\n\n"
            "Нажмите кнопку ниже, чтобы перейти в каталог 👇"
        ),
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    logger.info("Пользователь %s открыл бота", message.from_user.id)


# ════════════════════════════════════════════════════════════════════════════════
# Обработчик web_app_data — получаем корзину из WebApp
# Источник логики: telegram-web-app-bot-example + Shop-bot/handlers/user/cart.py
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message) -> None:
    """
    Обрабатывает данные корзины, отправленные через Telegram.WebApp.sendData().

    Формат JSON от фронтенда:
    {
      "items": [{"id": 1, "name": "...", "price": 100, "qty": 2, "total": 200}],
      "totalPrice": 200,
      "currency": "RUB",
      "timestamp": "2026-09-06T12:00:00Z"
    }
    """
    user = message.from_user
    logger.info("Получен заказ от пользователя %s (%s)", user.id, user.username)

    # ── Парсим JSON ──────────────────────────────────────────────────────────
    try:
        order_data = json.loads(message.web_app_data.data)
        items: list = order_data.get("items", [])
        total_price: int = order_data.get("totalPrice", 0)
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error("Ошибка парсинга JSON: %s", e)
        await message.answer("❌ Ошибка обработки заказа. Попробуйте ещё раз.")
        return

    if not items:
        await message.answer("❌ Корзина пуста. Пожалуйста, добавьте товары и повторите.")
        return

    # ── Формируем читаемый текст заказа ──────────────────────────────────────
    order_time = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Данные покупателя
    buyer_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    buyer_name = user.full_name or "Без имени"

    # Строки позиций
    items_text = "\n".join(
        f"  {i+1}. {item['name']}\n"
        f"     {item['price']:,} ₽ × {item['qty']} = {item['total']:,} ₽"
        for i, item in enumerate(items)
    )

    # Полный текст для продавца
    seller_text = (
        f"🛒 <b>НОВЫЙ ЗАКАЗ #{order_time.replace('.', '').replace(' ', '').replace(':', '')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Покупатель:</b> {buyer_name} ({buyer_info})\n"
        f"📅 <b>Время:</b> {order_time}\n\n"
        f"📦 <b>Состав заказа:</b>\n"
        f"{items_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>ИТОГО: {total_price:,} ₽</b>\n\n"
        f"Свяжитесь с покупателем для уточнения доставки и оплаты."
    )

    # ── Пересылаем заказ продавцу ─────────────────────────────────────────────
    # Кнопка-ссылка на чат с покупателем (если есть username)
    seller_keyboard = None
    if user.username:
        seller_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=f"💬 Написать {buyer_name}",
                    url=f"https://t.me/{user.username}",
                )
            ]]
        )

    try:
        await bot.send_message(
            chat_id=SELLER_CHAT_ID,
            text=seller_text,
            parse_mode="HTML",
            reply_markup=seller_keyboard,
        )
        logger.info("Заказ переслан продавцу (chat_id=%s)", SELLER_CHAT_ID)
    except Exception as e:
        logger.error("Не удалось отправить заказ продавцу: %s", e)

    # ── Подтверждение покупателю ──────────────────────────────────────────────
    # Краткий итог для покупателя
    buyer_items_text = "\n".join(
        f"• {item['name']} — {item['qty']} шт. × {item['price']:,} ₽"
        for item in items
    )

    buyer_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="💬 Связаться с продавцом",
                url=f"https://t.me/{SELLER_USERNAME}",
            )
        ]]
    )

    await message.answer(
        text=(
            "✅ <b>Заказ принят!</b>\n\n"
            f"<b>Ваш заказ:</b>\n{buyer_items_text}\n\n"
            f"💰 <b>Итого: {total_price:,} ₽</b>\n\n"
            "Продавец скоро свяжется с вами для уточнения деталей доставки и оплаты. "
            "Вы также можете написать ему напрямую 👇"
        ),
        reply_markup=buyer_keyboard,
        parse_mode="HTML",
    )
    logger.info(
        "Заказ подтверждён покупателю %s. Товаров: %d, сумма: %d ₽",
        user.id, len(items), total_price,
    )


# ════════════════════════════════════════════════════════════════════════════════
# Запуск бота
# ════════════════════════════════════════════════════════════════════════════════

async def main() -> None:
    logger.info("🤖 Бот Tazakkur запускается...")
    # Удаляем старые вебхуки (на случай если были)
    await bot.delete_webhook(drop_pending_updates=True)
    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

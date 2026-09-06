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
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from dotenv import load_dotenv

# ── Загрузка конфигурации из .env ────────────────────────────────────────────
load_dotenv()

BOT_TOKEN       = os.getenv("BOT_TOKEN")           # Токен от BotFather
SELLER_CHAT_ID  = int(os.getenv("SELLER_CHAT_ID"))  # Твой chat_id (продавца)
WEBAPP_URL      = os.getenv("WEBAPP_URL")           # URL задеплоенного фронтенда
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

# ── Relay: словарь для отслеживания обращений пользователей ─────────────────
# Ключ: message_id сообщения, отправленного продавцу → значение: user_id покупателя
# Используется чтобы знать, кому пересылать ответ продавца
order_message_map: dict[int, int] = {}

# Множество всех user_id, которые написали боту (для команды /users)
contacted_users: set[int] = set()


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

    # Фиксируем пользователя в глобальном множестве
    contacted_users.add(user.id)

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
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"📅 <b>Время:</b> {order_time}\n\n"
        f"📦 <b>Состав заказа:</b>\n"
        f"{items_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>ИТОГО: {total_price:,} ₽</b>\n\n"
        f"💡 Ответьте на это сообщение, чтобы написать покупателю напрямую."
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
        sent_msg = await bot.send_message(
            chat_id=SELLER_CHAT_ID,
            text=seller_text,
            parse_mode="HTML",
            reply_markup=seller_keyboard,
        )
        # ── Сохраняем привязку: message_id → user_id для relay-ответов ───────
        order_message_map[sent_msg.message_id] = user.id
        logger.info(
            "Заказ переслан продавцу (chat_id=%s), message_id=%s → user_id=%s",
            SELLER_CHAT_ID, sent_msg.message_id, user.id,
        )
    except Exception as e:
        logger.error("Не удалось отправить заказ продавцу: %s", e)

    # ── Подтверждение покупателю ──────────────────────────────────────────────
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
# /users — команда для продавца: статистика обратившихся пользователей
# Доступно только продавцу (SELLER_CHAT_ID)
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(Command("users"), F.chat.id == SELLER_CHAT_ID)
async def cmd_users(message: Message) -> None:
    """Показывает количество уникальных пользователей, обратившихся к боту."""
    total_users   = len(contacted_users)
    tracked_orders = len(order_message_map)

    await message.answer(
        f"📊 <b>Статистика бота:</b>\n\n"
        f"👥 Уникальных пользователей: <b>{total_users}</b>\n"
        f"🛒 Заказов в памяти (relay): <b>{tracked_orders}</b>\n\n"
        f"💡 Чтобы написать покупателю — ответьте на сообщение с его заказом.",
        parse_mode="HTML",
    )


# ════════════════════════════════════════════════════════════════════════════════
# RELAY: Продавец отвечает на сообщение бота → пересылаем покупателю
# Срабатывает, когда продавец делает reply на любое сообщение в чате с ботом
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(F.reply_to_message, F.chat.id == SELLER_CHAT_ID)
async def relay_admin_reply_to_user(message: Message) -> None:
    """
    Когда продавец отвечает (reply) на сообщение бота в своём чате:
    1. Ищем user_id через order_message_map по message_id оригинального сообщения.
    2. Если нашли — пересылаем ответ продавца покупателю.
    """
    replied_msg_id = message.reply_to_message.message_id

    # Пробуем найти user_id через наш словарь
    target_user_id = order_message_map.get(replied_msg_id)

    # Запасной вариант: если в оригинале есть forward_from (forwarded message)
    if target_user_id is None and message.reply_to_message.forward_from:
        target_user_id = message.reply_to_message.forward_from.id

    if target_user_id is None:
        # Ответ на сообщение, не связанное с заказом — игнорируем
        logger.debug(
            "Продавец ответил на message_id=%s, но user_id не найден в order_message_map",
            replied_msg_id,
        )
        await message.reply(
            "⚠️ Не могу определить получателя. "
            "Убедитесь, что отвечаете на сообщение с заказом покупателя."
        )
        return

    # ── Пересылаем ответ продавца покупателю ─────────────────────────────────
    try:
        seller_name = message.from_user.full_name or "Продавец"
        header = f"💬 <b>Ответ от продавца ({seller_name}):</b>\n\n"

        if message.text:
            await bot.send_message(
                chat_id=target_user_id,
                text=header + message.text,
                parse_mode="HTML",
            )
        elif message.photo:
            # Пересылаем фото с подписью
            caption = (header + message.caption) if message.caption else header.strip()
            await bot.send_photo(
                chat_id=target_user_id,
                photo=message.photo[-1].file_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif message.document:
            caption = (header + message.caption) if message.caption else header.strip()
            await bot.send_document(
                chat_id=target_user_id,
                document=message.document.file_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif message.voice:
            await bot.send_voice(
                chat_id=target_user_id,
                voice=message.voice.file_id,
                caption=header.strip(),
                parse_mode="HTML",
            )
        elif message.sticker:
            # Стикеры шлём без заголовка, потом текстом
            await bot.send_message(chat_id=target_user_id, text=header.strip(), parse_mode="HTML")
            await bot.send_sticker(chat_id=target_user_id, sticker=message.sticker.file_id)
        else:
            # Для остальных типов — просто пересылаем
            await bot.forward_message(
                chat_id=target_user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )

        await message.reply(f"✅ Ответ доставлен покупателю (ID: <code>{target_user_id}</code>).", parse_mode="HTML")
        logger.info("Relay: ответ продавца доставлен пользователю %s", target_user_id)

    except Exception as e:
        logger.error("Relay: не удалось доставить ответ пользователю %s: %s", target_user_id, e)
        await message.reply(f"❌ Не удалось доставить сообщение пользователю (ID: {target_user_id}).\nОшибка: {e}")


# ════════════════════════════════════════════════════════════════════════════════
# RELAY: Пользователь пишет в бот → пересылаем продавцу
# Срабатывает на любое сообщение НЕ от продавца, НЕ команду, НЕ web_app_data
# ════════════════════════════════════════════════════════════════════════════════

@dp.message(~F.chat.id.in_({SELLER_CHAT_ID}), ~F.web_app_data, ~F.text.startswith("/"))
async def relay_user_message_to_admin(message: Message) -> None:
    """
    Когда обычный пользователь пишет что-либо в бот (не команду, не web_app_data):
    1. Пересылаем его сообщение продавцу с информацией об отправителе.
    2. Сохраняем reply-привязку, чтобы продавец мог ответить.
    """
    user = message.from_user
    contacted_users.add(user.id)

    buyer_info = f"@{user.username}" if user.username else f"ID: <code>{user.id}</code>"
    buyer_name = user.full_name or "Без имени"

    header = (
        f"📩 <b>Сообщение от покупателя</b>\n"
        f"👤 {buyer_name} ({buyer_info})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
    )

    try:
        if message.text:
            sent_msg = await bot.send_message(
                chat_id=SELLER_CHAT_ID,
                text=header + message.text,
                parse_mode="HTML",
            )
        elif message.photo:
            caption = (header + message.caption) if message.caption else header.strip()
            sent_msg = await bot.send_photo(
                chat_id=SELLER_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif message.document:
            caption = (header + message.caption) if message.caption else header.strip()
            sent_msg = await bot.send_document(
                chat_id=SELLER_CHAT_ID,
                document=message.document.file_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif message.voice:
            sent_msg = await bot.send_voice(
                chat_id=SELLER_CHAT_ID,
                voice=message.voice.file_id,
                caption=header.strip(),
                parse_mode="HTML",
            )
        elif message.sticker:
            await bot.send_message(chat_id=SELLER_CHAT_ID, text=header.strip(), parse_mode="HTML")
            sent_msg = await bot.send_sticker(chat_id=SELLER_CHAT_ID, sticker=message.sticker.file_id)
        else:
            # Пересылаем оригинал + добавляем заголовок отдельным сообщением
            await bot.send_message(chat_id=SELLER_CHAT_ID, text=header.strip(), parse_mode="HTML")
            sent_msg = await bot.forward_message(
                chat_id=SELLER_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )

        # Сохраняем привязку: message_id у продавца → user_id покупателя
        order_message_map[sent_msg.message_id] = user.id
        logger.info(
            "Relay: сообщение от пользователя %s переслано продавцу (message_id=%s)",
            user.id, sent_msg.message_id,
        )

        # Уведомляем пользователя, что сообщение доставлено
        await message.reply(
            "📨 Ваше сообщение передано продавцу. Ожидайте ответа.",
        )

    except Exception as e:
        logger.error("Relay: не удалось переслать сообщение от %s продавцу: %s", user.id, e)


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

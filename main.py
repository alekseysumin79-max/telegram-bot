import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", " ")

# Ссылка на курс на твоём сайте (файл больше не отправляем из Telegram)
PDF_LINK = "https://nakerosine.ru/crypto/kurs-7-siblings-print.html"

# Список каналов для проверки (ID и юзернейм)
CHANNELS = [
    {"id": -1002035579299, "username": "@crypto_beetle", "name": "Crypto Beetle"},
    {"id": -1004436853996, "username": "@flamehub_visuals", "name": "FlameHub | Visuals"},
    {"id": -1003236230594, "username": "@filosofskiy_sous", "name": "Философский соус"},
    {"id": -1004411687846, "username": "@got_news_ru", "name": "Игра престолов | Вестерос"},
]
# ================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


def file_kb() -> InlineKeyboardMarkup:
    """Кнопка со ссылкой на курс на сайте."""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📥 Получить курс", url=PDF_LINK))
    return kb


def subs_kb(missing: list) -> InlineKeyboardMarkup:
    """Кнопки только на НЕ подписанные каналы + кнопка проверки."""
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in missing:
        kb.add(InlineKeyboardButton(
            f"📢 Подписаться: {ch['name']}",
            url=f"https://t.me/{ch['username'].strip('@')}"
        ))
    kb.add(InlineKeyboardButton("✅ Я подписался — проверить", callback_data="check"))
    return kb


async def missing_channels(user_id: int) -> list:
    """Возвращает список каналов, на которых пользователя НЕТ."""
    missing = []
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if member.status in ("left", "kicked"):
                missing.append(ch)
        except Exception as e:
            logging.error(f"Ошибка проверки канала {ch['username']}: {e}")
            missing.append(ch)  # недоступен для проверки — считаем неподписанным
    return missing


@dp.chat_join_request_handler()
async def on_join_request(update: types.ChatJoinRequest):
    """Человек подал заявку на закрытый канал — бот сам пишет ему в личку."""
    try:
        missing = await missing_channels(update.from_user.id)
        if not missing:
            await bot.send_message(
                update.from_user.id,
                "🎉 Спасибо за подписку на все каналы! Вот ваш курс:",
                reply_markup=file_kb(),
            )
        else:
            await bot.send_message(
                update.from_user.id,
                "👋 Заявка принята! Чтобы получить PDF «Стратегия 7 Siblings»,\n"
                "осталось подписаться на эти каналы:",
                reply_markup=subs_kb(missing),
            )
    except Exception as e:
        logging.error(f"Не удалось написать {update.from_user.id}: {e}")


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    missing = await missing_channels(user_id)

    if not missing:
        await message.answer(
            "📥 Спасибо за подписку на все каналы!\n\nЗабирайте курс:",
            reply_markup=file_kb()
        )
    else:
        await message.answer(
            "❌ Чтобы получить PDF «Стратегия 7 Siblings», подпишитесь на каналы:\n\n"
            + "\n".join([f"• {ch['name']}" for ch in missing]) +
            "\n\nПосле подписки нажмите «Я подписался — проверить».",
            reply_markup=subs_kb(missing)
        )


@dp.callback_query_handler(text="check")
async def check_subs_cb(call: types.CallbackQuery):
    missing = await missing_channels(call.from_user.id)
    if not missing:
        await call.message.answer("🎁 Всё готово! Забирайте курс:", reply_markup=file_kb())
        await call.answer("Всё верно! 🎉")
    else:
        await call.answer("Осталось: " + ", ".join(ch["name"] for ch in missing), show_alert=True)


if __name__ == "__main__":
    print("🚀 Бот запущен. Жду сообщения...")
    executor.start_polling(
        dp,
        skip_updates=True,
        allowed_updates=["message", "callback_query", "chat_join_request", "chat_member"],
    )
﻿

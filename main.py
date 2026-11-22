import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "сюда_впиши_токен_только_для_локального_теста")
PDF_PATH = "kurs-7-siblings.pdf"

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


async def check_sub(user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на ВСЕ каналы из списка."""
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception as e:
            logging.error(f"Ошибка проверки канала {ch['username']}: {e}")
            return False
    return True


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    if await check_sub(user_id):
        try:
            with open(PDF_PATH, "rb") as pdf:
                await message.answer_document(
                    pdf,
                    caption="📥 Ваш PDF: «Стратегия 7 Siblings»\n\nСпасибо за подписку на все каналы!"
                )
        except Exception as e:
            await message.answer(f"❌ Ошибка при отправке файла: {e}\n\nПроверь, что файл {PDF_PATH} лежит рядом с ботом.")
    else:
        kb = InlineKeyboardMarkup(row_width=1)
        for ch in CHANNELS:
            kb.add(InlineKeyboardButton(
                f"📢 {ch['name']}",
                url=f"https://t.me/{ch['username'].strip('@')}"
            ))
        await message.answer(
            "❌ Чтобы получить PDF, подпишитесь на все каналы:\n\n"
            + "\n".join([f"• {ch['name']}" for ch in CHANNELS]) +
            "\n\nПосле подписки нажмите /start снова.",
            reply_markup=kb
        )


if __name__ == "__main__":
    print("🚀 Бот запущен. Жду сообщения...")
    executor.start_polling(dp, skip_updates=True)

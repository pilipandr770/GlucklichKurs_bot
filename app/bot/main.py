# file: app/bot/main.py
import asyncio, os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from .handlers import start, text, voice
from .utils.reminders import schedule

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def send_reminder_factory(bot: Bot):
    async def _send(uid: int):
        await bot.send_message(uid, "Нагадування ✨\nВступний урок уже дав тобі відчуття користі? Повна програма допоможе закріпити результат. Натисни /pay, щоб отримати доступ до всіх уроків.")
    return _send

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(text.router)
    dp.include_router(voice.router)

    # планувальник нагадувань
    await schedule(await send_reminder_factory(bot))

    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

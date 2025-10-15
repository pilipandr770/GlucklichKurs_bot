# file: app/bot/main.py
import asyncio, os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from .handlers import start, text, voice, buy, legal
from .utils.reminders import start_reminders

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def send_reminder(bot: Bot, uid: int):
    """Відправляє нагадування користувачу"""
    try:
        await bot.send_message(
            uid, 
            "✨ <b>Нагадування</b>\n\n"
            "Вступний урок уже дав тобі відчуття користі? "
            "Повна програма «10 кроків до щастя» допоможе закріпити результат.\n\n"
            "Натисни /pay, щоб отримати доступ до всіх уроків."
        )
    except Exception as e:
        print(f"Failed to send reminder to {uid}: {e}")

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Реєструємо роутери
    dp.include_router(start.router)
    dp.include_router(buy.router)
    dp.include_router(legal.router)
    dp.include_router(text.router)
    dp.include_router(voice.router)

    # Запускаємо планувальник нагадувань
    await start_reminders(lambda uid: send_reminder(bot, uid))

    print("✅ Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

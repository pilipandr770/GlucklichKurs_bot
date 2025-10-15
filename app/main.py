# file: app/main.py
"""
Об'єднаний запуск FastAPI (webhooks) + Telegram Bot в одному процесі
"""
import asyncio
import os
import threading
from dotenv import load_dotenv

load_dotenv()

def run_fastapi():
    """Запускає FastAPI сервер в окремому потоці"""
    import uvicorn
    from app.web.server import app
    
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting FastAPI on port {port}...")
    
    # Запускаємо uvicorn без asyncio (в окремому потоці)
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )

async def run_bot():
    """Запускає Telegram бота"""
    from aiogram import Bot, Dispatcher
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from app.bot.handlers import start, text, voice, buy, legal
    from app.bot.utils.reminders import start_reminders
    
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
    
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Видаляємо webhook, якщо він був встановлений раніше
    await bot.delete_webhook(drop_pending_updates=True)
    
    dp = Dispatcher()
    
    # Реєструємо роутери
    dp.include_router(start.router)
    dp.include_router(buy.router)
    dp.include_router(legal.router)
    dp.include_router(text.router)
    dp.include_router(voice.router)
    
    # Запускаємо планувальник нагадувань
    await start_reminders(lambda uid: send_reminder(bot, uid))
    
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

def main():
    """Головна функція - запускає FastAPI і Bot"""
    print("🚀 Starting GlückenKurs Bot + Web Server...")
    
    # Запускаємо FastAPI в окремому потоці
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Невелика затримка, щоб FastAPI встиг запуститися
    import time
    time.sleep(2)
    
    # Запускаємо бота в головному потоці
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()

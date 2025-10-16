# file: app/web/stripe_webhook.py
import os
import json
import aiohttp
from ..storage.db import mark_paid

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PAID_CHANNEL_LINK = os.getenv("PAID_CHANNEL_LINK", "")  # t.me/+xxxx або @channel

async def _notify_user(tg_id: str, text: str):
    """Надсилає повідомлення користувачу через Telegram Bot API"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️  TELEGRAM_BOT_TOKEN not set, skipping notification")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": tg_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.text()
                if response.status == 200:
                    print(f"✅ Notification sent to user {tg_id}")
                else:
                    print(f"❌ Failed to send notification: {result}")
    except Exception as e:
        print(f"❌ Error sending notification: {e}")

async def handle_stripe_event(event: dict):
    """
    Приймає Stripe події.
    На success: дістаємо tg_id з metadata і шлемо лінк у приватні повідомлення.
    За бажання — тут же можна позначати оплату в БД.
    """
    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        tg_id = ""
        try:
            tg_id = str(data.get("metadata", {}).get("tg_id", "")).strip()
        except Exception:
            tg_id = ""
        
        if tg_id:
            # Позначаємо оплату в БД
            try:
                user_id = int(tg_id)
                session_id = data.get("id", "")
                mark_paid(user_id, session_id)
                print(f"✅ Payment successful for user {user_id}, session {session_id}")
            except Exception as e:
                print(f"❌ Failed to mark payment in DB: {e}")
            
            # Надсилаємо інвайт-лінк
            text = (
                "🎉 <b>Оплату підтверджено!</b>\n\n"
                "Вітаємо у закритому курсі «10 кроків до щастя». "
                "Приєднуйтесь до приватного каналу з уроками:\n\n"
                f"🔗 {PAID_CHANNEL_LINK}\n\n"
                "Якщо посилання не відкривається — напишіть /help у бот.\n\n"
                "💬 <b>Coach Agent</b> готовий відповісти на твої питання про уроки!"
            )
            await _notify_user(tg_id, text)

    # Для відлагодження (опційно)
    if os.getenv("DEBUG", "").lower() == "true":
        print("Stripe event:", json.dumps(event, ensure_ascii=False, indent=2))

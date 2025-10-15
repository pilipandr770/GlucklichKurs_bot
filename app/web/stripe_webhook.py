# file: app/web/stripe_webhook.py
import os, json
from ..storage.db import mark_paid, get_user_by_stripe_session

async def handle_stripe_event(event):
    """Обробка подій від Stripe"""
    event_type = event["type"]
    
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id")
        
        # Отримуємо user_id з метаданих
        telegram_user_id = session.get("metadata", {}).get("telegram_user_id")
        
        if telegram_user_id:
            user_id = int(telegram_user_id)
            mark_paid(user_id, session_id)
            print(f"✅ Payment successful for user {user_id}, session {session_id}")
            
            # TODO: Тут можна відправити повідомлення користувачу через бота
            # або надати інвайт-лінк до приватного каналу
        else:
            # Пробуємо знайти через session_id
            user_id = get_user_by_stripe_session(session_id)
            if user_id:
                mark_paid(user_id, session_id)
                print(f"✅ Payment successful for user {user_id} (found by session)")
    
    # Дебаг для інших подій
    if os.getenv("DEBUG","").lower()=="true":
        print(f"Stripe event [{event_type}]:", json.dumps(event, indent=2))

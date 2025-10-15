# file: app/web/stripe_webhook.py
import os, json, asyncio

async def handle_stripe_event(event):
    t = event["type"]
    if t == "checkout.session.completed":
        # TODO: тут можна видати доступ користувачу, якщо ти зв'язуєш user_id з session metadata
        pass
    # для дебага
    if os.getenv("DEBUG","").lower()=="true":
        print("Stripe event:", json.dumps(event, indent=2))

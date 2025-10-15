# file: app/web/server.py
import os, stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, PlainTextResponse
from dotenv import load_dotenv
from .stripe_webhook import handle_stripe_event
from ..storage.db import save_stripe_metadata

load_dotenv()

app = FastAPI(title="GlückenKurs Billing")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/pay")
async def pay(user_id: int = None):
    """Створює Stripe Checkout Session з прив'язкою до Telegram user_id"""
    domain = os.getenv("BASE_URL","http://localhost:8000")
    paid_channel = os.getenv("PAID_CHANNEL_ID","")
    
    # Метадані для прив'язки користувача
    metadata = {}
    if user_id:
        metadata["telegram_user_id"] = str(user_id)
    
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data":{
                "currency":"eur",
                "product_data":{"name":"Курс «10 кроків до щастя»"},
                "unit_amount":999
            },
            "quantity":1
        }],
        success_url=f"{domain}/paid?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{domain}/cancel",
        metadata=metadata
    )
    
    # Зберігаємо session_id для користувача
    if user_id:
        save_stripe_metadata(user_id, session.id)
    
    return RedirectResponse(session.url, status_code=303)

@app.get("/paid")
async def paid(session_id: str = ""):
    """Показує сторінку успішної оплати"""
    paid_channel = os.getenv("PAID_CHANNEL_ID", "@your_private_paid_channel")
    return PlainTextResponse(
        f"✅ Дякуємо за оплату!\n\n"
        f"За кілька хвилин ви отримаєте повідомлення в Telegram з інструкціями для доступу.\n\n"
        f"Приватний канал з уроками: {paid_channel}\n\n"
        f"Session ID: {session_id}"
    )

@app.get("/cancel")
async def cancel():
    """Сторінка скасування оплати"""
    return PlainTextResponse("❌ Оплату скасовано. Ви можете спробувати знову у боті командою /pay")

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Обробка вебхуків від Stripe"""
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig, endpoint_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    await handle_stripe_event(event)
    return {"received": True}

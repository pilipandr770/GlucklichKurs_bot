# file: app/web/server.py
import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, PlainTextResponse, JSONResponse
from dotenv import load_dotenv
from .stripe_webhook import handle_stripe_event

load_dotenv()

app = FastAPI(title="GlückenKurs Billing")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/pay")
async def pay(tg_id: str = ""):
    """
    Стартова точка оплати. Бот повинен викликати /pay?tg_id=123456789
    tg_id передаємо в Stripe metadata → заберемо у вебхуку.
    """
    if not tg_id:
        # можна показати сторінку помилки або редірект на лендінг
        return JSONResponse({"error": "tg_id is required"}, status_code=400)

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": "Курс «10 кроків до щастя»"},
                "unit_amount": 999  # 9.99 EUR → копійки
            },
            "quantity": 1
        }],
        metadata={"tg_id": tg_id},
        success_url=f"{BASE_URL}/paid",
        cancel_url=f"{BASE_URL}/cancel"
    )
    return RedirectResponse(session.url, status_code=303)

@app.get("/paid")
async def paid():
    """Показує сторінку успішної оплати"""
    return PlainTextResponse(
        "✅ Дякуємо за оплату!\n\n"
        "Перевірте приватні повідомлення у Telegram — надіслали інструкцію доступу."
    )

@app.get("/cancel")
async def cancel():
    """Сторінка скасування оплати"""
    return PlainTextResponse(
        "❌ Оплату скасовано.\n\n"
        "За потреби поверніться до бота і спробуйте ще раз: /pay"
    )

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

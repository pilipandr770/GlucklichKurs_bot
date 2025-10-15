# file: app/web/server.py
import os, stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, PlainTextResponse
from dotenv import load_dotenv
from .stripe_webhook import handle_stripe_event
load_dotenv()

app = FastAPI(title="GlückenKurs Billing")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/pay")
async def pay():
    # Створюємо Checkout Session; після успіху — редірект у приватний канал
    domain = os.getenv("BASE_URL","http://localhost:8000")
    paid_channel = os.getenv("PAID_CHANNEL_ID","")
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price_data":{"currency":"eur","product_data":{"name":"Курс «10 кроків до щастя»"},"unit_amount":999},"quantity":1}],
        success_url=f"{domain}/paid?c={paid_channel}",
        cancel_url=f"{domain}/cancel",
    )
    return RedirectResponse(session.url, status_code=303)

@app.get("/paid")
async def paid(c: str=""):
    # показати інструкцію доступу до каналу
    return PlainTextResponse(f"Дякуємо за оплату! Приєднуйтесь до приватного каналу: {c}")

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(payload, sig, endpoint_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    await handle_stripe_event(event)
    return {"received": True}

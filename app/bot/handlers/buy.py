# app/bot/handlers/buy.py
import os
from aiogram import Router, types, F
from ..keyboards.legal import legal_menu
from ...storage.db import upsert_user, save_stripe_metadata

router = Router()

@router.message(F.text == "/pay")
async def pay_cmd(m: types.Message):
    upsert_user(m.from_user.id, m.from_user.username)
    base = os.getenv("BASE_URL","http://localhost:8000")
    # Передаємо user_id як параметр для прив'язки до Stripe
    await m.answer(
        f"💳 Щоб оформити оплату, перейдіть за посиланням:\n{base}/pay?user_id={m.from_user.id}\n\n"
        f"Після успішної оплати ви отримаєте доступ до приватного каналу з усіма уроками.",
        reply_markup=legal_menu()
    )
    
@router.callback_query(F.data=="buy")
async def buy_cb(cb: types.CallbackQuery):
    upsert_user(cb.from_user.id, cb.from_user.username)
    base = os.getenv("BASE_URL","http://localhost:8000")
    await cb.message.answer(
        f"💳 Для оплати перейдіть за посиланням:\n{base}/pay?user_id={cb.from_user.id}\n\n"
        f"⚠️ Перед оплатою обов'язково перегляньте юридичні умови нижче:",
        reply_markup=legal_menu()
    )
    await cb.answer()

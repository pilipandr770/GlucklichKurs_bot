# app/bot/handlers/legal.py
import os
from aiogram import Router, types, F
from ..keyboards.legal import legal_menu
from ..keyboards.main_menu import main_menu

router = Router()

LEGAL_DIR = os.path.join("data","legal")
FILES = {
    "legal_datenschutz": "datenschutz.md",
    "legal_agb": "agb.md",
    "legal_impressum": "impressum.md",
    "legal_disclaimer": "disclaimer.md",
}

def _read_md(name: str) -> str:
    path = os.path.join(LEGAL_DIR, name)
    if not os.path.exists(path):
        return "Текст буде додано найближчим часом."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@router.message(F.text.in_(["/legal", "/terms", "/datenschutz", "/agb", "/impressum", "/disclaimer"]))
async def cmd_legal(m: types.Message):
    await m.answer("Юридична інформація:", reply_markup=legal_menu())

@router.callback_query(F.data=="legal_open")
async def open_legal_menu(cb: types.CallbackQuery):
    await cb.message.edit_text("Юридична інформація:", reply_markup=legal_menu())
    await cb.answer()

@router.callback_query(F.data.in_(FILES.keys()))
async def show_legal(cb: types.CallbackQuery):
    text = _read_md(FILES[cb.data])
    if len(text) > 3900: 
        text = text[:3900] + "\n…"
    await cb.message.answer(text, reply_markup=legal_menu())
    await cb.answer()

@router.callback_query(F.data=="legal_refund_ack")
async def refund_ack(cb: types.CallbackQuery):
    refund_text = _read_md("refund.md")
    await cb.message.answer(f"{refund_text}\n\n✅ Ви підтверджуєте відсутність повернення коштів.", reply_markup=legal_menu())
    await cb.answer()

@router.callback_query(F.data=="back_to_main")
async def back_to_main(cb: types.CallbackQuery):
    await cb.message.edit_text("Головне меню:", reply_markup=main_menu())
    await cb.answer()

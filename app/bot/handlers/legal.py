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

def split_long_message(text: str, max_length: int = 4000):
    """Розбиває довге повідомлення на частини"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current = ""
    for line in text.split('\n'):
        if len(current) + len(line) + 1 > max_length:
            parts.append(current)
            current = line
        else:
            current += '\n' + line if current else line
    if current:
        parts.append(current)
    return parts

# Обробка кнопок постійного меню
@router.message(F.text == "📜 Datenschutz")
async def persistent_datenschutz(m: types.Message):
    text = _read_md("datenschutz.md")
    parts = split_long_message(text)
    for part in parts:
        await m.answer(part)

@router.message(F.text == "📜 AGB")
async def persistent_agb(m: types.Message):
    text = _read_md("agb.md")
    parts = split_long_message(text)
    for part in parts:
        await m.answer(part)

@router.message(F.text == "📜 Impressum")
async def persistent_impressum(m: types.Message):
    text = _read_md("impressum.md")
    parts = split_long_message(text)
    for part in parts:
        await m.answer(part)

@router.message(F.text == "🏠 Головне меню")
async def show_main_menu_button(m: types.Message):
    await m.answer("Головне меню:", reply_markup=main_menu())

# Команди
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
    parts = split_long_message(text)
    for i, part in enumerate(parts):
        if i == len(parts) - 1:
            # Останнє повідомлення з кнопками
            await cb.message.answer(part, reply_markup=legal_menu())
        else:
            await cb.message.answer(part)
    await cb.answer()

@router.callback_query(F.data=="legal_refund_ack")
async def refund_ack(cb: types.CallbackQuery):
    refund_text = _read_md("refund.md")
    parts = split_long_message(refund_text)
    for i, part in enumerate(parts):
        if i == len(parts) - 1:
            await cb.message.answer(f"{part}\n\n✅ Ви підтверджуєте відсутність повернення коштів.", reply_markup=legal_menu())
        else:
            await cb.message.answer(part)
    await cb.answer()

@router.callback_query(F.data=="back_to_main")
async def back_to_main(cb: types.CallbackQuery):
    await cb.message.edit_text("Головне меню:", reply_markup=main_menu())
    await cb.answer()

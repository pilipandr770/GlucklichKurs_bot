# app/bot/keyboards/legal.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def legal_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Datenschutz", callback_data="legal_datenschutz")],
        [InlineKeyboardButton(text="📜 AGB", callback_data="legal_agb")],
        [InlineKeyboardButton(text="📜 Impressum", callback_data="legal_impressum")],
        [InlineKeyboardButton(text="📜 Disclaimer", callback_data="legal_disclaimer")],
        [InlineKeyboardButton(text="✅ Підтверджую без повернення коштів", callback_data="legal_refund_ack")],
        [InlineKeyboardButton(text="🔙 Назад до меню", callback_data="back_to_main")]
    ])

# file: app/bot/keyboards/main_menu.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Вступний урок", callback_data="intro")],
        [InlineKeyboardButton(text=" Придбати курс", callback_data="buy")],
        [InlineKeyboardButton(text="ℹ️ Про курс", callback_data="about")],
        [InlineKeyboardButton(text="📜 Datenschutz", callback_data="legal_datenschutz")],
        [InlineKeyboardButton(text="📜 AGB", callback_data="legal_agb")],
        [InlineKeyboardButton(text=" Impressum", callback_data="legal_impressum")],
        [InlineKeyboardButton(text=" Disclaimer", callback_data="legal_disclaimer")],
        [InlineKeyboardButton(text="✅ Підтверджую без повернення коштів", callback_data="legal_refund")]
    ])

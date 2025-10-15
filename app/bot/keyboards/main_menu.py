# file: app/bot/keyboards/main_menu.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Вступний урок", callback_data="intro")],
        [InlineKeyboardButton(text="💳 Придбати курс", callback_data="buy")],
        [InlineKeyboardButton(text="ℹ️ Про курс", callback_data="about")],
        [InlineKeyboardButton(text="⚖️ Юридична інформація", callback_data="legal_open")]
    ])

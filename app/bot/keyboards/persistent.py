# app/bot/keyboards/persistent.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def persistent_menu():
    """Постійне меню з юридичними кнопками внизу"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📜 Datenschutz"),
                KeyboardButton(text="📜 AGB"),
                KeyboardButton(text="📜 Impressum")
            ],
            [
                KeyboardButton(text="🏠 Головне меню")
            ]
        ],
        resize_keyboard=True,
        persistent=True,  # Залишається видимою завжди
        input_field_placeholder="Напишіть повідомлення або оберіть дію..."
    )

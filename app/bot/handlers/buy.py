# app/bot/handlers/buy.py
import os
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ...storage.db import upsert_user, get_user_by_id

router = Router()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def confirmation_keyboard():
    """Клавіатура для підтвердження перед оплатою"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Прочитати умови повернення", callback_data="show_refund")],
        [InlineKeyboardButton(text="✅ Я прочитав(ла) та погоджуюсь", callback_data="confirm_purchase")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_purchase")]
    ])

def payment_keyboard(user_id: int):
    """Клавіатура з посиланням на оплату (передаємо tg_id)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Перейти до оплати", url=f"{BASE_URL}/pay?tg_id={user_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])

@router.message(F.text == "/pay")
async def pay_cmd(m: types.Message):
    """Команда /pay — швидкий доступ до оплати"""
    upsert_user(m.from_user.id, m.from_user.username)
    url = f"{BASE_URL}/pay?tg_id={m.from_user.id}"
    await m.answer(
        "💳 <b>Оплата курсу «10 кроків до щастя»</b>\n\n"
        "🔗 Перейдіть за посиланням для оплати через Stripe:\n"
        f"{url}\n\n"
        "Після успішної оплати ви отримаєте повідомлення з інвайт-лінком до приватного каналу.\n\n"
        "⚠️ Перед оплатою ознайомтесь з умовами: /legal"
    )

@router.callback_query(F.data=="buy")
async def buy_cb(cb: types.CallbackQuery):
    upsert_user(cb.from_user.id, cb.from_user.username)
    await cb.message.answer(
        "💳 <b>Придбати курс «10 кроків до щастя»</b>\n\n"
        "📦 <b>Що ви отримаєте:</b>\n"
        "✅ 10 структурованих уроків\n"
        "✅ Практичні завдання та квізи\n"
        "✅ Доступ до приватного каналу\n"
        "✅ Пожиттєвий доступ\n\n"
        "💰 <b>Ціна:</b> 9,99 EUR (одноразово)\n\n"
        "⚠️ <b>ВАЖЛИВО:</b> Перед оплатою ви повинні прочитати та підтвердити умови.",
        reply_markup=confirmation_keyboard()
    )
    await cb.answer()

async def show_purchase_warning(message: types.Message):
    """Показує попередження перед покупкою"""
    await message.answer(
        "💳 <b>Придбати курс «10 кроків до щастя»</b>\n\n"
        "📦 <b>Що ви отримаєте:</b>\n"
        "✅ 10 структурованих уроків\n"
        "✅ Практичні завдання та квізи\n"
        "✅ Доступ до приватного каналу\n"
        "✅ Пожиттєвий доступ\n\n"
        "💰 <b>Ціна:</b> 9,99 EUR (одноразово)\n\n"
        "⚠️ <b>ВАЖЛИВО:</b> Перед оплатою ви повинні прочитати та підтвердити умови.",
        reply_markup=confirmation_keyboard()
    )

@router.callback_query(F.data=="show_refund")
async def show_refund_policy(cb: types.CallbackQuery):
    """Показує політику повернення коштів"""
    refund_text = """
⛔ <b>ПОЛІТИКА ПОВЕРНЕННЯ КОШТІВ</b>

<b>ВАЖЛИВО! Прочитайте уважно:</b>

❌ Повернення коштів НЕМОЖЛИВЕ після покупки
❌ Відсутнє право на відмову
❌ Це цифровий продукт з миттєвим доступом

<b>Чому немає повернення?</b>
• Ви отримуєте НЕГАЙНИЙ доступ до всіх 10 уроків
• Цифровий контент неможливо "повернути"
• Це передбачено законодавством ЄС (§ 356 BGB)

<b>Перед покупкою:</b>
✅ Перегляньте безкоштовний вступний урок
✅ Переконайтеся, що вам підходить формат
✅ Прочитайте всі юридичні документи

<b>Натискаючи "Я погоджуюсь", ви підтверджуєте:</b>
☑️ Я розумію, що повернення коштів неможливе
☑️ Я відмовляюся від права на відмову
☑️ Я погоджуюсь отримати негайний доступ
☑️ Я прочитав(ла) AGB та Datenschutz
    """
    await cb.message.answer(refund_text, reply_markup=confirmation_keyboard())
    await cb.answer()

@router.callback_query(F.data=="confirm_purchase")
async def confirm_purchase(cb: types.CallbackQuery):
    """Підтвердження покупки - показує посилання на оплату"""
    user_id = cb.from_user.id
    upsert_user(user_id, cb.from_user.username)
    
    await cb.message.answer(
        "✅ <b>Дякуємо за підтвердження!</b>\n\n"
        "Тепер ви можете перейти до безпечної оплати через Stripe.\n\n"
        "🔒 Ваші платіжні дані захищені\n"
        "💳 Приймаються картки Visa, Mastercard та інші\n"
        "🌍 Підтримка різних валют\n\n"
        "Після успішної оплати ви негайно отримаєте доступ до приватного каналу.",
        reply_markup=payment_keyboard(user_id)
    )
    await cb.answer("✅ Умови прийняті")

@router.callback_query(F.data=="cancel_purchase")
async def cancel_purchase(cb: types.CallbackQuery):
    """Скасування покупки"""
    from ..keyboards.main_menu import main_menu
    await cb.message.edit_text(
        "❌ Покупку скасовано.\n\n"
        "Ви можете повернутися до покупки в будь-який час через кнопку «💳 Придбати курс».\n\n"
        "Якщо у вас є питання, напишіть нам або перегляньте безкоштовний вступний урок.",
        reply_markup=main_menu()
    )
    await cb.answer("Скасовано")

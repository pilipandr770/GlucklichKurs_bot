# file: app/bot/handlers/start.py
import os, json
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from ..keyboards.main_menu import main_menu
from ..utils.openai_client import chat_completion
from ..utils.reminders import add_user
router = Router()

WELCOME_SALES_PROMPT = [
    {"role":"system","content":"Ти — привітний сейлз-агент курсу '10 кроків до щастя'. Коротко, тепло, по суті. Запрошуй подивитись вступний урок і пояснюй користь курсу. Уникай довгих текстів."}
]

def load_intro_lesson():
    path = os.path.join("data","lessons","lesson_1.json")
    if not os.path.exists(path): return None
    with open(path,"r",encoding="utf-8") as f: return json.load(f)

@router.message(CommandStart())
async def on_start(msg: types.Message):
    add_user(msg.from_user.id, int(os.getenv("REMINDER_DAYS", "3")))
    await msg.answer("Вітаю! Це курс 10 кроків до щастя \nОбери дію з меню нижче:", reply_markup=main_menu())

@router.callback_query(F.data=="about")
async def on_about(cb: types.CallbackQuery):
    user = cb.from_user
    resp = chat_completion(WELCOME_SALES_PROMPT + [{"role":"user","content":f"Користувач @{user.username} питає: розкажи коротко про курс і як він працює."}])
    text = resp.choices[0].message.content
    await cb.message.edit_text(text, reply_markup=main_menu())
    await cb.answer()

@router.callback_query(F.data=="intro")
async def on_intro(cb: types.CallbackQuery):
    lesson = load_intro_lesson()
    if not lesson:
        await cb.message.answer("Вступний урок ще готується. Спробуй пізніше ", reply_markup=main_menu())
    else:
        await cb.message.answer(f"🎓 {lesson['title']}\n\n{lesson['hook']}\n\n{lesson['core']}")
    await cb.answer()

@router.callback_query(F.data=="buy")
async def on_buy(cb: types.CallbackQuery):
    await cb.message.answer("Щоб оформити оплату, перейдіть за посиланням: /pay\nПісля оплати ви отримаєте доступ до приватного каналу з усіма уроками.")
    await cb.answer()

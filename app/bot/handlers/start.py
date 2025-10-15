# file: app/bot/handlers/start.py
import os, json
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from ..keyboards.main_menu import main_menu
from ..utils.openai_client import chat_completion
from ...storage.db import upsert_user, mark_intro_seen

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
    from ..keyboards.persistent import persistent_menu
    upsert_user(msg.from_user.id, msg.from_user.username)
    await msg.answer(
        "Вітаю! Це курс «10 кроків до щастя» 😊\n\n"
        "Оберіть дію з меню нижче або використовуйте кнопки внизу для швидкого доступу до юридичних документів.",
        reply_markup=persistent_menu()
    )
    await msg.answer("Головне меню:", reply_markup=main_menu())

@router.callback_query(F.data=="about")
async def on_about(cb: types.CallbackQuery):
    user = cb.from_user
    upsert_user(user.id, user.username)
    resp = chat_completion(WELCOME_SALES_PROMPT + [{"role":"user","content":f"Користувач @{user.username} питає: розкажи коротко про курс і як він працює."}])
    text = resp.choices[0].message.content
    await cb.message.edit_text(text, reply_markup=main_menu())
    await cb.answer()

@router.callback_query(F.data=="intro")
async def on_intro(cb: types.CallbackQuery):
    upsert_user(cb.from_user.id, cb.from_user.username)
    lesson = load_intro_lesson()
    if not lesson:
        await cb.message.answer("Вступний урок ще готується. Спробуй пізніше 🙏", reply_markup=main_menu())
    else:
        text = f"🎓 <b>{lesson['title']}</b>\n\n{lesson['hook']}\n\n{lesson['core']}"
        if len(text) > 4000:
            text = text[:4000] + "..."
        await cb.message.answer(text, reply_markup=main_menu())
        mark_intro_seen(cb.from_user.id)
    await cb.answer()



# file: app/bot/handlers/start.py
import os
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from ..keyboards.main_menu import main_menu
from ..utils.openai_client import chat_completion
from ..utils.agent_loader import get_agent_prompt
from ...storage.db import upsert_user, mark_intro_seen

router = Router()

def load_intro_text():
    """Завантажує вступний текст про курс з data/intro.txt"""
    path = os.path.join("data", "intro.txt")
    if not os.path.exists(path):
        return "Вступний урок готується. Спробуйте пізніше 🙏"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

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
    
    # Використовуємо sales_agent з YAML
    sales_prompt = get_agent_prompt("sales_agent")
    resp = chat_completion([
        {"role": "system", "content": sales_prompt},
        {"role": "user", "content": f"Користувач @{user.username} питає: розкажи коротко про курс і як він працює."}
    ])
    text = resp.choices[0].message.content
    await cb.message.edit_text(text, reply_markup=main_menu())
    await cb.answer()

@router.callback_query(F.data=="intro")
async def on_intro(cb: types.CallbackQuery):
    upsert_user(cb.from_user.id, cb.from_user.username)
    
    # Завантажуємо повний вступний текст
    intro_text = load_intro_text()
    
    # Розділяємо на частини, якщо текст довгий
    if len(intro_text) > 4000:
        parts = []
        current = ""
        for line in intro_text.split("\n"):
            if len(current) + len(line) + 1 < 4000:
                current += line + "\n"
            else:
                parts.append(current)
                current = line + "\n"
        if current:
            parts.append(current)
        
        for idx, part in enumerate(parts):
            if idx == 0:
                await cb.message.answer(part)
            else:
                await cb.message.answer(part)
        
        await cb.message.answer("Головне меню:", reply_markup=main_menu())
    else:
        await cb.message.answer(intro_text, reply_markup=main_menu())
    
    mark_intro_seen(cb.from_user.id)
    await cb.answer()



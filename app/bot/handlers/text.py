# file: app/bot/handlers/text.py
from aiogram import Router, types, F
from ..utils.openai_client import chat_completion
from ..utils.agent_loader import get_agent_prompt
from ..utils.lesson_loader import get_full_lessons_context
from ..utils.safety_guards import apply_guard
from ...storage.db import upsert_user, get_user_by_id

router = Router()

@router.message(F.text)
async def on_text(msg: types.Message):
    if not msg.text or msg.text.strip() == "":
        return
    
    # Оновлюємо користувача в БД
    upsert_user(msg.from_user.id, msg.from_user.username)
    
    # Перевіряємо, чи користувач оплатив курс
    user = get_user_by_id(msg.from_user.id)
    is_paid = user and user.get("is_paid") == 1
    is_paid = user and user.get("is_paid") == 1
    
    # Застосовуємо Safety Guard
    agent_type = "coach" if is_paid else "sales"
    is_allowed, rejection_message = await apply_guard(msg.text, agent_type)
    
    if not is_allowed:
        await msg.answer(rejection_message)
        return
    
    if is_paid:
        # Використовуємо coach_agent з повним контекстом уроків
        coach_prompt = get_agent_prompt("coach_agent")
        lessons_context = get_full_lessons_context()
        
        messages = [
            {"role": "system", "content": coach_prompt},
            {"role": "system", "content": lessons_context},
            {"role": "user", "content": msg.text}
        ]
        
        resp = chat_completion(messages)
        answer = resp.choices[0].message.content
        
        # Якщо відповідь дуже довга, розділяємо
        if len(answer) > 4000:
            parts = []
            current = ""
            for line in answer.split("\n"):
                if len(current) + len(line) + 1 < 4000:
                    current += line + "\n"
                else:
                    parts.append(current)
                    current = line + "\n"
            if current:
                parts.append(current)
            
            for part in parts:
                await msg.answer(part)
        else:
            await msg.answer(answer)
    
    else:
        # Використовуємо sales_agent для безплатних користувачів
        sales_prompt = get_agent_prompt("sales_agent")
        
        messages = [
            {"role": "system", "content": sales_prompt},
            {"role": "user", "content": msg.text}
        ]
        
        resp = chat_completion(messages)
        await msg.answer(resp.choices[0].message.content)

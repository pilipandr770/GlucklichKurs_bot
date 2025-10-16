"""
Handler для повідомлень у приватному каналі/чаті з уроками
Coach agent відповідає на питання користувачів після оплати
"""
from aiogram import Router, types, F
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from ..utils.openai_client import chat_completion
from ..utils.agent_loader import get_agent_prompt
from ..utils.lesson_loader import get_full_lessons_context
from ..utils.safety_guards import apply_guard
import os

router = Router()

# ID приватного каналу з уроками (з .env)
PAID_CHANNEL_ID = int(os.getenv("PAID_CHANNEL_ID", "0"))

@router.message(F.chat.id == PAID_CHANNEL_ID)
async def channel_message(msg: types.Message):
    """
    Обробляє повідомлення у приватному каналі/чаті з уроками.
    Coach agent відповідає на питання з повним контекстом курсу.
    """
    # Ігноруємо пусті повідомлення або повідомлення від ботів
    if not msg.text or msg.from_user.is_bot:
        return
    
    # Ігноруємо service messages (pinned, joined, etc.)
    if msg.text.startswith("/"):
        return
    
    print(f"📝 Channel message from {msg.from_user.id}: {msg.text[:50]}...")
    print(f"🔵 [DEBUG] chat_id={msg.chat.id}, PAID_CHANNEL_ID={PAID_CHANNEL_ID}")
    
    # Застосовуємо Safety Guard (coach type)
    is_allowed, rejection_message = await apply_guard(msg.text, "coach")
    
    if not is_allowed:
        await msg.reply(rejection_message)
        return
    
    # Використовуємо coach_agent з повним контекстом уроків
    coach_prompt = get_agent_prompt("coach_agent")
    lessons_context = get_full_lessons_context()
    
    print(f"🔵 [DEBUG] coach_prompt length: {len(coach_prompt)} chars")
    print(f"🔵 [DEBUG] lessons_context length: {len(lessons_context)} chars")
    print(f"🔵 [DEBUG] First 200 chars of coach_prompt: {coach_prompt[:200]}")
    
    messages = [
        {"role": "system", "content": coach_prompt},
        {"role": "system", "content": lessons_context},
        {"role": "user", "content": msg.text}
    ]
    
    try:
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
                await msg.reply(part)
        else:
            # Відповідаємо reply (прив'язуємо до питання)
            await msg.reply(answer)
    
    except Exception as e:
        print(f"❌ Error in channel handler: {e}")
        await msg.reply("❌ Вибач, сталася помилка. Спробуй ще раз або напиши мені в приватні повідомлення.")

@router.my_chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER)
)
async def bot_added_to_channel(event: types.ChatMemberUpdated):
    """Бот доданий до каналу/чату"""
    print(f"✅ Bot added to chat {event.chat.id} ({event.chat.title})")

@router.my_chat_member(
    ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER)
)
async def bot_removed_from_channel(event: types.ChatMemberUpdated):
    """Бот видалений з каналу/чату"""
    print(f"❌ Bot removed from chat {event.chat.id} ({event.chat.title})")

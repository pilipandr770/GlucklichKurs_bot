# file: app/bot/handlers/text.py
from aiogram import Router, types, F
from ..utils.openai_client import chat_completion
router = Router()

COACH_PROMPT = [
    {"role":"system","content":"Ти — коуч-агент курсу. Відповідай коротко, підтримувально, практично. Якщо є питання про оплату чи доступ — перенаправ на /pay."}
]

@router.message(F.text)
async def on_text(msg: types.Message):
    if not msg.text or msg.text.strip() == "":
        return
    resp = chat_completion(COACH_PROMPT + [{"role":"user","content":msg.text}])
    await msg.answer(resp.choices[0].message.content)

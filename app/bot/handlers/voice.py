# file: app/bot/handlers/voice.py
import aiohttp
from aiogram import Router, types, F
from ..utils.openai_client import speech_to_text, text_to_speech, chat_completion
router = Router()

@router.message(F.voice)
async def on_voice(msg: types.Message):
    file_id = msg.voice.file_id
    f = await msg.bot.get_file(file_id)
    url = f"https://api.telegram.org/file/bot{msg.bot.token}/{f.file_path}"
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            ogg_bytes = await r.read()

    text = speech_to_text(ogg_bytes)
    resp = chat_completion([{"role":"system","content":"Ти — турботливий коуч, відповідай стисло і корисно."},
                            {"role":"user","content":text}])
    answer = resp.choices[0].message.content
    try:
        mp3 = text_to_speech(answer)
        await msg.answer_voice(voice=mp3, caption=" Відповідь голосом")
    except Exception:
        await msg.answer(answer)

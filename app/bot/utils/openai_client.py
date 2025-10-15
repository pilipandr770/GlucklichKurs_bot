# file: app/bot/utils/openai_client.py
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GPT = os.getenv("OPENAI_MODEL_GPT", "gpt-4o-mini")
TTS = os.getenv("OPENAI_MODEL_TTS", "gpt-4o-mini-tts")
STT = os.getenv("OPENAI_MODEL_STT", "whisper-1")

def chat_completion(messages, model: str = GPT):
    return _client.chat.completions.create(model=model, messages=messages)

def speech_to_text(audio_bytes: bytes, filename="voice.ogg", model: str = STT) -> str:
    from io import BytesIO
    bio = BytesIO(audio_bytes)
    return _client.audio.transcriptions.create(model=model, file=("audio.ogg", bio)).text

def text_to_speech(text: str, voice="alloy", model: str = TTS) -> bytes:
    # Повертаємо MP3 байти
    audio = _client.audio.speech.create(model=model, voice=voice, input=text, format="mp3")
    return audio.read()

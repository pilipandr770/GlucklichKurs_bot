# file: README.md
GlückenKurs — Telegram SaaS бот: багатoагентна система (OpenAI Agents SDK), продаж курсу через Stripe, STT/TTS, нагадування, юридичні кнопки.
## Швидкий старт
1) python -m venv .venv && .\.venv\Scripts\Activate.ps1
2) pip install -r requirements.txt
3) копіюй .env.example -> .env і заповни значення
4) uvicorn app.web.server:app --reload
5) python -m app.bot.main

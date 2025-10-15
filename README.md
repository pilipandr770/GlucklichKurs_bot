# file: README.md
# GlückenKurs — Telegram SaaS Bot

Telegram SaaS бот для продажу онлайн-курсу «10 кроків до щастя» з інтеграцією OpenAI (GPT, STT, TTS), Stripe платежами, системою нагадувань та базою даних.

## 🎯 Основні можливості

- 🤖 **Telegram бот** на aiogram 3.x
- 💬 **OpenAI Integration**: GPT-4, Whisper (STT), TTS
- 💳 **Stripe платежі** з автоматичним відстеженням
- 📊 **SQLite база даних** для користувачів та транзакцій
- ⏰ **Система нагадувань** (APScheduler)
- 📚 **10 структурованих уроків** з квізами та практиками
- ⚖️ **Юридичні документи** (GDPR-ready)
- 🎙️ **Голосові повідомлення** з розпізнаванням та озвучуванням

## 🚀 Швидкий старт

### 1. Встановлення залежностей

```powershell
# Створіть віртуальне середовище
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Встановіть залежності
pip install -r requirements.txt
```

### 2. Налаштування змінних оточення

```powershell
# Скопіюйте шаблон
Copy-Item .env.example .env

# Відредагуйте .env файл та додайте ваші ключі:
# - TELEGRAM_BOT_TOKEN
# - OPENAI_API_KEY
# - STRIPE_SECRET_KEY
# - STRIPE_WEBHOOK_SECRET
# - BASE_URL
```

### 3. Запуск

**Термінал 1 — Веб-сервер (FastAPI для Stripe):**
```powershell
uvicorn app.web.server:app --reload --port 8000
```

**Термінал 2 — Telegram бот:**
```powershell
python -m app.bot.main
```

## 📁 Структура проекту

```
GlückenKurs/
├── app/
│   ├── bot/                    # Telegram бот
│   │   ├── handlers/          # Обробники (start, buy, legal, text, voice)
│   │   ├── keyboards/         # Клавіатури (main_menu, legal)
│   │   └── utils/             # OpenAI клієнт, аудіо, нагадування
│   ├── web/                   # FastAPI сервер
│   │   ├── server.py          # Stripe Checkout endpoints
│   │   └── stripe_webhook.py  # Webhook обробник
│   └── storage/               # База даних
│       └── db.py              # SQLite операції
├── data/
│   ├── lessons/               # 10 уроків у JSON форматі
│   └── legal/                 # Юридичні документи (MD)
├── .env.example               # Шаблон змінних оточення
├── requirements.txt           # Python залежності
└── README.md
```

## 🗄️ База даних

SQLite таблиця `users`:
- `user_id` — Telegram user ID (PRIMARY KEY)
- `username` — Telegram username
- `seen_intro_at` — Час перегляду вступного уроку
- `reminder_sent` — Чи було надіслано нагадування
- `is_paid` — Статус оплати
- `stripe_session_id` — ID Stripe сесії
- `created_at` — Час реєстрації

## 🔧 Налаштування Stripe

1. Отримайте ключі на [dashboard.stripe.com](https://dashboard.stripe.com)
2. Налаштуйте webhook endpoint: `https://your-domain.tld/stripe/webhook`
3. Підпишіться на події: `checkout.session.completed`
4. Додайте `STRIPE_WEBHOOK_SECRET` у `.env`

## 📝 Команди бота

- `/start` — Головне меню
- `/pay` — Оформити оплату курсу
- `/legal` — Юридична інформація

## 🔐 Безпека

- `.env` файл додано до `.gitignore`
- Stripe webhook підпис перевіряється
- База даних локальна (не в Git)

## 📦 Залежності

- aiogram 3.6.0 — Telegram Bot framework
- openai 1.40.0 — OpenAI API
- fastapi 0.115.0 — Web framework
- stripe 7.10.0 — Payment processing
- apscheduler 3.10.4 — Task scheduling
- pydub 0.25.1 — Audio processing

## 🎓 Уроки курсу

1. Благодарність
2. Цілі та мрії
3. Фізична активність
4. Зв'язки та стосунки
5. Мислення зростання
6. Медитація та усвідомленість
7. Служіння іншим
8. Фінансова стабільність
9. Творчість
10. Самоприйняття

Кожен урок містить:
- Мотивуючу цитату (hook)
- Основний контент (core)
- Наукові докази (evidence)
- Практичні завдання (practices)
- Квіз з 3 питаннями

## 🛠️ Подальший розвиток

- [ ] Автоматична видача інвайт-лінків після оплати
- [ ] Dashboard для адміністратора
- [ ] Аналітика та статистика
- [ ] OpenAI Agents SDK повна інтеграція
- [ ] Система прогресу користувача
- [ ] Розсилка уроків за розкладом

## 📄 Ліцензія

Приватний проект

## 👤 Автор

@pilipandr770

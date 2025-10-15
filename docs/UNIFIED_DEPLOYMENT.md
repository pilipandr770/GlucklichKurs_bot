# 🎯 Один сервіс замість двох: FastAPI + Bot разом

## ✅ Що зроблено

Об'єднано FastAPI (webhooks) і Telegram Bot в **один процес**:
- FastAPI запускається в окремому **background thread**
- Telegram Bot працює в **головному потоці**
- **Один сервіс на Render** замість двох
- **Безкоштовно** - 750 годин/місяць

---

## 📋 Архітектура

```python
app/main.py:
├─ Thread 1: FastAPI (uvicorn)
│  ├─ /health
│  ├─ /pay?user_id=...
│  └─ /stripe/webhook
│
└─ Main Thread: Telegram Bot (aiogram)
   ├─ /start
   ├─ /pay
   └─ Reminders
```

**Переваги:**
- ✅ Один сервіс = економія
- ✅ Швидка комунікація (локальна пам'ять)
- ✅ Спільна база даних (PostgreSQL)
- ✅ Простіше деплоїти

---

## 🚀 Деплой на Render

### Варіант 1: Оновити існуючий сервіс

**Dashboard → glucklichkurs-bot → Settings:**

1. **Start Command:**
   ```bash
   python scripts/migrate_db.py && python -m app.main
   ```

2. **Environment Variables:**
   Оновіть `BASE_URL`:
   ```
   BASE_URL=https://glucklichkurs-bot.onrender.com
   ```

3. **Save Changes** → **Manual Deploy** → **Deploy latest commit**

---

### Варіант 2: Створити новий сервіс

**Dashboard → New + → Web Service:**

```
Name: gluckenkurs-bot
Repository: pilipandr770/GlucklichKurs_bot
Branch: main
Runtime: Python
Region: Frankfurt

Build Command:
pip install -r requirements.txt

Start Command:
python scripts/migrate_db.py && python -m app.main

Environment Variables (скопіюйте з вашого .env файлу):
# Використовуйте значення з вашого локального .env файлу
# Не публікуйте реальні токени в документації!

DATABASE_URL=postgresql://user:pass@host.render.com/db
DB_SCHEMA=gluckenkurs
TELEGRAM_BOT_TOKEN=xxxxxxxxx:xxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx
OPENAI_MODEL_GPT=gpt-4o-mini
OPENAI_MODEL_TTS=tts-1
OPENAI_MODEL_STT=whisper-1
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxx
STRIPE_PRODUCT_ID=prod_xxxxxxxxxxxxxx
BASE_URL=https://gluckenkurs-bot.onrender.com
INTRO_CHANNEL_ID=-100xxxxxxxxxx
PAID_CHANNEL_ID=-100xxxxxxxxxx
REMINDER_DAYS=3
PORT=10000
```

---

## 🔧 Налаштування Stripe Webhook

1. https://dashboard.stripe.com/webhooks
2. **Add endpoint:** `https://gluckenkurs-bot.onrender.com/stripe/webhook`
3. **Events:** `checkout.session.completed`
4. Скопіюйте **Signing secret** → Оновіть `STRIPE_WEBHOOK_SECRET`

---

## ✅ Перевірка

### 1. Health Check:
```bash
curl https://gluckenkurs-bot.onrender.com/health
# Має повернути: {"ok":true}
```

### 2. Логи (Dashboard → Service → Logs):
```
🌐 Starting FastAPI on port 10000...
INFO:     Started server process
🤖 Bot is running...
✅ Завантажено 10 уроків
```

### 3. Telegram Bot:
```
/start → Має відповісти з меню
💳 Купити курс → Stripe checkout
```

---

## 🧪 Локальне тестування

```bash
# Запуск
python -m app.main

# Очікується:
# 🚀 Starting GlückenKurs Bot + Web Server...
# 🌐 Starting FastAPI on port 8000...
# INFO:     Uvicorn running on http://0.0.0.0:8000
# 🤖 Bot is running...
# ✅ Завантажено 10 уроків
```

**Тест:**
1. http://localhost:8000/health → `{"ok":true}`
2. Telegram → /start → Відповідає

---

## 🐛 Troubleshooting

### Бот не відповідає:
```bash
# Перевірте логи
Dashboard → gluckenkurs-bot → Logs

# Має бути:
🤖 Bot is running...
```

### Webhook не працює:
```bash
# Перевірте BASE_URL
curl https://gluckenkurs-bot.onrender.com/stripe/webhook

# Має повернути: {"detail":"Method Not Allowed"}
# (це нормально - GET не дозволено, тільки POST від Stripe)
```

### FastAPI не запускається:
```bash
# Перевірте PORT
Dashboard → Service → Environment → PORT

# Має бути автоматично встановлено Render
```

---

## 💰 Економія

**Було:**
- Web Service: 750 год/міс
- Worker Service: 750 год/міс
- **Разом:** 2 сервіси

**Стало:**
- Web Service (unified): 750 год/міс
- **Разом:** 1 сервіс ✅

**Економія:** Один сервіс замість двох!

---

## 📊 Порівняння підходів

| Підхід | Сервіси | Вартість | Складність |
|--------|---------|----------|------------|
| **Два окремі** | 2 | $14/міс (Starter) | Висока |
| **Unified (поточний)** | 1 | $0 (Free) або $7/міс | Низька ✅ |
| **Docker Compose** | 1 | $7/міс (Docker) | Середня |

---

**Статус:** ✅ Готово до деплою  
**Час деплою:** ~5 хвилин  
**Версія:** v2.4.0 (Unified Deployment)

# Деплой на Render.com з PostgreSQL

## 📋 Передумови

- [x] Акаунт на Render.com
- [x] GitHub репозиторій: https://github.com/pilipandr770/GlucklichKurs_bot
- [x] Існуюча PostgreSQL БД на Render

---

## 🚀 Крок 1: Підготовка репозиторію

### Файли готові до деплою:
- ✅ `render.yaml` - конфігурація Render (web + worker)
- ✅ `requirements.txt` - додано `gunicorn`, `psycopg2-binary`
- ✅ `app/storage/db_postgres.py` - PostgreSQL з підтримкою схем
- ✅ `scripts/migrate_db.py` - міграція БД

### Закомітьте зміни:
```bash
git add .
git commit -m "Add Render deployment config with PostgreSQL support"
git push origin main
```

---

## 🗄️ Крок 2: Підключення існуючої PostgreSQL БД

### У Render Dashboard:

1. Перейдіть до вашої існуючої PostgreSQL БД
2. Скопіюйте **Internal Database URL**  
   Формат: `postgres://user:password@hostname/database`

3. **ВАЖЛИВО:** Ми створимо окрему схему `gluckenkurs` в цій БД

---

## 🔧 Крок 3: Створення сервісів

### Варіант А: Автоматичний деплой через render.yaml

1. Перейдіть на https://dashboard.render.com/
2. Натисніть **"New +"** → **"Blueprint"**
3. Підключіть репозиторій: `pilipandr770/GlucklichKurs_bot`
4. Render автоматично виявить `render.yaml`
5. Натисніть **"Apply"**

### Варіант Б: Ручне створення (якщо render.yaml не підходить)

#### Сервіс 1: Web Server

1. **New +** → **Web Service**
2. Підключіть GitHub репозиторій
3. **Name:** `gluckenkurs-web`
4. **Region:** Frankfurt (EU Central)
5. **Branch:** `main`
6. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
7. **Start Command:**
   ```bash
   gunicorn app.web.server:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```
8. **Plan:** Free

#### Сервіс 2: Telegram Bot (Worker)

1. **New +** → **Background Worker**
2. Підключіть той же репозиторій
3. **Name:** `gluckenkurs-bot`
4. **Region:** Frankfurt (EU Central)
5. **Branch:** `main`
6. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
7. **Start Command:**
   ```bash
   python scripts/migrate_db.py && python -m app.bot.main
   ```
8. **Plan:** Free

---

## 🔐 Крок 4: Налаштування змінних середовища

### Для ОБОХ сервісів (web + worker):

**Підключення до БД:**
```env
DATABASE_URL=<ваш_internal_database_url>
DB_SCHEMA=gluckenkurs
```

**Telegram Bot:**
```env
TELEGRAM_BOT_TOKEN=8414485386:AAF6deWBVSFNr5upKN3WpDnzb-ivPtUUMAE
```

**OpenAI:**
```env
OPENAI_API_KEY=sk-proj-ODT-JLgNtCscVfYD4nLi1...
OPENAI_MODEL_GPT=gpt-4o-mini
OPENAI_MODEL_TTS=tts-1
OPENAI_MODEL_STT=whisper-1
```

**Stripe:**
```env
STRIPE_SECRET_KEY=sk_test_51PhccQHpsuFkjt3pKveboY...
STRIPE_WEBHOOK_SECRET=whsec_KFoob2HFpkaQPRJ8VscYF...
STRIPE_PUBLISHABLE_KEY=pk_test_51PhccQHpsuFkjt3p9kZnz1...
STRIPE_PRODUCT_ID=prod_SmG0MRLT4aRKmf
```

**Канали:**
```env
INTRO_CHANNEL_ID=-1002911331449
PAID_CHANNEL_ID=-1003140324634
```

**Інше:**
```env
BASE_URL=https://gluckenkurs-web.onrender.com
REMINDER_DAYS=3
```

---

## 🛠️ Крок 5: Налаштування Stripe Webhook

### Після деплою веб-сервера:

1. Зайдіть на https://dashboard.stripe.com/webhooks
2. **Add endpoint**
3. **Endpoint URL:** `https://gluckenkurs-web.onrender.com/stripe/webhook`
4. **Events to send:**
   - ✅ `checkout.session.completed`
5. **Add endpoint**
6. Скопіюйте **Signing secret** (whsec_...)
7. Оновіть `STRIPE_WEBHOOK_SECRET` в Render

---

## ✅ Крок 6: Перевірка деплою

### Перевірте веб-сервер:
```bash
curl https://gluckenkurs-web.onrender.com/health
# Очікується: {"ok":true}
```

### Перевірте бота:
1. Відкрийте Telegram
2. Напишіть `/start` вашому боту
3. Має відповісти з меню

### Перевірте БД:
```bash
# Підключіться до PostgreSQL (через Render Shell або pgAdmin)
psql $DATABASE_URL

# Перевірте схему
\dn

# Має бути схема: gluckenkurs

# Перевірте таблиці
SET search_path TO gluckenkurs;
\dt

# Має бути таблиця: users
```

---

## 📊 Крок 7: Моніторинг

### Логи веб-сервера:
https://dashboard.render.com/web/[service-id]/logs

### Логи бота (worker):
https://dashboard.render.com/worker/[service-id]/logs

### Метрики:
- CPU usage
- Memory usage
- Request count

---

## 🐛 Troubleshooting

### Помилка: "relation does not exist"
**Причина:** Схема не створена  
**Рішення:**
```bash
# Підключіться до БД
psql $DATABASE_URL

# Створіть схему вручну
CREATE SCHEMA IF NOT EXISTS gluckenkurs;

# Перезапустіть bot worker
```

### Помилка: "column user_id does not exist"
**Причина:** Таблиця не створена  
**Рішення:**
```bash
# Запустіть міграцію вручну
python scripts/migrate_db.py
```

### Бот не відповідає
**Перевірте:**
1. Worker запущений (Render Dashboard → gluckenkurs-bot → Logs)
2. TELEGRAM_BOT_TOKEN правильний
3. Немає помилок в логах

### Webhook не працює
**Перевірте:**
1. STRIPE_WEBHOOK_SECRET правильний
2. Endpoint URL правильний: `https://gluckenkurs-web.onrender.com/stripe/webhook`
3. Події обрані: `checkout.session.completed`

---

## 📝 Структура БД на Render

```
PostgreSQL Database (існуюча)
├── schema: public (інші проекти)
├── schema: gluckenkurs (наш проект) ← нова схема
│   └── table: users
│       ├── user_id BIGINT PRIMARY KEY
│       ├── username TEXT
│       ├── seen_intro_at BIGINT
│       ├── reminder_sent INTEGER
│       ├── is_paid INTEGER
│       ├── stripe_session_id TEXT
│       └── created_at BIGINT
```

### Переваги окремої схеми:
- ✅ Ізоляція від інших проектів
- ✅ Немає конфліктів таблиць
- ✅ Легке управління через `SET search_path`
- ✅ Можливість backup окремо

---

## 🔄 Оновлення проекту

### Після push на GitHub:
1. Render автоматично виявить зміни
2. Запустить build
3. Перезапустить сервіси

### Ручний перезапуск:
1. Render Dashboard → Service → **Manual Deploy** → **Deploy latest commit**

---

## 💰 Ціни Render Free Plan

### Обмеження:
- Web Service: 750 годин/місяць (достатньо для одного сервісу)
- Worker: окрема квота 750 годин/місяць
- PostgreSQL: 1 GB (спільна з іншими проектами)
- Сервіси засинають після 15 хв неактивності
- Перший запит після сну: ~30 сек

### Рекомендації:
- Використовуйте cron-job для підтримки активності
- Або перейдіть на Starter Plan ($7/міс) для постійної роботи

---

## 🎯 Чеклист готовності

- [ ] Закоммічено render.yaml
- [ ] Закоммічено оновлений requirements.txt
- [ ] Закоммічено db_postgres.py та migrate_db.py
- [ ] Створено Web Service на Render
- [ ] Створено Worker Service на Render
- [ ] Налаштовано всі змінні середовища
- [ ] DATABASE_URL підключено
- [ ] DB_SCHEMA=gluckenkurs встановлено
- [ ] Міграція виконана успішно
- [ ] /health повертає {"ok":true}
- [ ] /start працює в Telegram
- [ ] Stripe webhook налаштовано
- [ ] Тестова оплата працює

---

**Автор:** Andrii Pylypchuk  
**Проект:** GlückenKurs Bot  
**Версія:** 2.3.0 (Render Deployment)  
**Дата:** 15.10.2025

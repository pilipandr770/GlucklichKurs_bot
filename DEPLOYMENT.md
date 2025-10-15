# DEPLOYMENT.md — Інструкція з розгортання

## 📋 Налаштування після клонування

### 1. Встановлення

```powershell
git clone https://github.com/pilipandr770/GlucklichKurs_bot.git
cd GlucklichKurs_bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Налаштування .env

Скопіюйте `.env.example` у `.env` та заповніть:

```env
# Telegram
TELEGRAM_BOT_TOKEN=ваш_токен_від_@BotFather

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Stripe
STRIPE_SECRET_KEY=sk_test_... (або sk_live_...)
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_... (або pk_live_...)

# URL
BASE_URL=https://ваш-домен.tld (для продакшена)

# Канали
PAID_CHANNEL_ID=@ваш_приватний_канал
```

### 3. Налаштування Stripe Webhook

1. Перейдіть на https://dashboard.stripe.com/webhooks
2. Додайте новий endpoint: `https://ваш-домен.tld/stripe/webhook`
3. Виберіть події: `checkout.session.completed`
4. Скопіюйте Signing Secret у `STRIPE_WEBHOOK_SECRET`

### 4. Запуск локально

**Термінал 1 — FastAPI:**
```powershell
uvicorn app.web.server:app --reload --host 0.0.0.0 --port 8000
```

**Термінал 2 — Telegram Bot:**
```powershell
python -m app.bot.main
```

### 5. Тестування Stripe (локально)

Для тестування вебхуків локально використайте Stripe CLI:

```powershell
# Встановіть Stripe CLI
scoop install stripe

# Налаштуйте forwarding
stripe login
stripe listen --forward-to localhost:8000/stripe/webhook

# В іншому терміналі тригерте подію
stripe trigger checkout.session.completed
```

## 🚀 Розгортання на сервері

### Варіант 1: VPS (Ubuntu/Debian)

```bash
# Встановіть залежності
sudo apt update
sudo apt install python3.10 python3-pip python3-venv nginx

# Клонуйте проект
git clone https://github.com/pilipandr770/GlucklichKurs_bot.git
cd GlucklichKurs_bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Налаштуйте systemd сервіси
sudo nano /etc/systemd/system/gluckenkurs-bot.service
sudo nano /etc/systemd/system/gluckenkurs-web.service

# Запустіть
sudo systemctl enable gluckenkurs-bot gluckenkurs-web
sudo systemctl start gluckenkurs-bot gluckenkurs-web
```

### Варіант 2: Docker

```dockerfile
# Dockerfile (приклад)
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "app.bot.main"]
```

### Варіант 3: Heroku

```bash
# Додайте Procfile
web: uvicorn app.web.server:app --host 0.0.0.0 --port $PORT
bot: python -m app.bot.main
```

## 🔧 Налаштування приватного каналу

### 1. Створіть приватний канал
- Зробіть канал приватним
- Додайте бота як адміністратора з правом запрошувати

### 2. Отримайте ID каналу
```python
# У боті відправте повідомлення в канал та подивіться логи
print(message.chat.id)  # Має вигляд: -1001234567890
```

### 3. Автоматична видача доступу

Додайте в `app/web/stripe_webhook.py`:

```python
from aiogram import Bot

async def handle_stripe_event(event):
    if event["type"] == "checkout.session.completed":
        telegram_user_id = int(event["data"]["object"]["metadata"]["telegram_user_id"])
        
        # Створіть інвайт-лінк
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        invite_link = await bot.create_chat_invite_link(
            chat_id=os.getenv("PAID_CHANNEL_ID"),
            member_limit=1
        )
        
        # Відправте користувачу
        await bot.send_message(
            telegram_user_id,
            f"✅ Оплату підтверджено!\n\n"
            f"Ваш особистий доступ до курсу:\n{invite_link.invite_link}"
        )
```

## 📊 Моніторинг та логи

### Перегляд логів бота
```bash
journalctl -u gluckenkurs-bot -f
```

### Перегляд логів веб-сервера
```bash
journalctl -u gluckenkurs-web -f
```

### База даних
```bash
sqlite3 app.db
> SELECT * FROM users;
> SELECT COUNT(*) FROM users WHERE is_paid=1;
```

## 🔐 Безпека

1. ✅ Ніколи не комітьте `.env` файл
2. ✅ Використовуйте HTTPS для вебхуків
3. ✅ Перевіряйте Stripe webhook підписи
4. ✅ Обмежте доступ до бази даних
5. ✅ Регулярно оновлюйте залежності

## 🆘 Troubleshooting

### Бот не отримує повідомлення
- Перевірте токен в `.env`
- Перевірте інтернет-з'єднання
- Подивіться логи: `python -m app.bot.main`

### Stripe вебхуки не працюють
- Перевірте `STRIPE_WEBHOOK_SECRET`
- Перевірте HTTPS та доступність URL
- Тестуйте з Stripe CLI

### База даних помилки
- Видаліть `app.db` та перезапустіть
- Перевірте права доступу до файлу

## 📞 Підтримка

GitHub Issues: https://github.com/pilipandr770/GlucklichKurs_bot/issues

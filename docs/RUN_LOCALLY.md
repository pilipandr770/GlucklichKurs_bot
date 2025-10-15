# Запуск проекту GlückenKurs Bot

## 🚀 Швидкий запуск (для тестування локально)

### 1. Запустити веб-сервер (FastAPI)
```powershell
# В одному терміналі
uvicorn app.web.server:app --host 0.0.0.0 --port 8000 --reload
```

**Перевірка:** Відкрийте http://localhost:8000/health — має показати `{"ok": true}`

---

### 2. Запустити Telegram бота (в іншому терміналі)
```powershell
# В другому терміналі
python -m app.bot.main
```

**Перевірка:** Має показати:
```
✅ Reminder scheduler started
✅ Bot is running...
```

---

## 🔧 Альтернатива: Один термінал з tmux/screen

### Для Windows (PowerShell):
```powershell
# Запустити веб-сервер у фоні
Start-Job -ScriptBlock { uvicorn app.web.server:app --host 0.0.0.0 --port 8000 }

# Запустити бота
python -m app.bot.main
```

---

## 🧪 Тестування оплати

### 1. Відкрийте бота в Telegram
```
/start
```

### 2. Натисніть кнопку "💰 Купити курс"

### 3. Підтвердіть умови та натисніть "💳 Перейти до оплати"

**ЩО ВІДБУВАЄТЬСЯ:**
- Бот відкриє URL: `http://localhost:8000/pay?user_id=YOUR_ID`
- Сервер створить Stripe Checkout Session
- Вас перенаправить на сторінку оплати Stripe
- Використовуйте тестову картку: `4242 4242 4242 4242`

### 4. Тестові дані Stripe:
```
Номер картки: 4242 4242 4242 4242
MM/YY: 12/34 (будь-яка майбутня дата)
CVC: 123
Поштовий індекс: 12345
```

### 5. Після оплати:
- Ви побачите сторінку "✅ Дякуємо за оплату!"
- Webhook спрацює (якщо налаштований)
- Статус `is_paid=1` оновиться в БД

---

## ⚠️ Важливі налаштування

### BASE_URL у .env:
```env
# Для локального тестування:
BASE_URL=http://localhost:8000

# Для продакшну (коли матимете домен):
BASE_URL=https://your-domain.com
```

**ВАЖЛИВО:** `BASE_URL` має вказувати на ваш веб-сервер (FastAPI), а НЕ на Telegram!

---

## 🌐 Налаштування для продакшну

### 1. Отримайте публічний домен або IP
```
Варіанти:
- VPS (DigitalOcean, Hetzner)
- ngrok для тестування (https://ngrok.com)
- Railway / Render для безкоштовного хостингу
```

### 2. Налаштуйте Stripe Webhook
```
1. Зайдіть на https://dashboard.stripe.com/webhooks
2. Створіть endpoint: https://your-domain.com/stripe/webhook
3. Оберіть події: checkout.session.completed
4. Скопіюйте Signing Secret → STRIPE_WEBHOOK_SECRET у .env
```

### 3. Оновіть .env:
```env
BASE_URL=https://your-domain.com
```

---

## 📊 Перевірка статусу

### Перевірити веб-сервер:
```powershell
curl http://localhost:8000/health
# Або відкрийте в браузері
```

### Перевірити бота:
```
/start в Telegram
```

### Перевірити базу даних:
```powershell
python -c "from app.storage.db import get_user_by_id; print(get_user_by_id(YOUR_USER_ID))"
```

---

## 🐛 Troubleshooting

### Помилка: "Connection refused" при /pay
**Причина:** Веб-сервер не запущений  
**Рішення:** 
```powershell
uvicorn app.web.server:app --port 8000
```

### Помилка: "TelegramBadRequest: query is too old"
**Причина:** Бот був вимкнений, старі callback запити  
**Рішення:** Це нормально, просто ігноруйте або натисніть /start знову

### Оплата перенаправляє в Telegram замість Stripe
**Причина:** BASE_URL вказує на Telegram  
**Рішення:** Змініть на `http://localhost:8000` у .env

### Webhook не спрацьовує
**Причина:** Stripe не може достукатись до localhost  
**Рішення:** 
- Використайте ngrok: `ngrok http 8000`
- Або розгорніть на публічному сервері

---

## 📝 Корисні команди

```powershell
# Перевірити порт 8000
netstat -an | findstr :8000

# Вбити процес на порту 8000 (якщо зайнятий)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Переглянути логи бота (якщо запущений як фоновий процес)
Get-Job | Receive-Job
```

---

## 🎯 Чеклист готовності

- [ ] Встановлено всі залежності: `pip install -r requirements.txt`
- [ ] Файл `.env` створений та заповнений
- [ ] `BASE_URL=http://localhost:8000` у .env
- [ ] Веб-сервер запущений на порту 8000
- [ ] Telegram бот запущений
- [ ] http://localhost:8000/health повертає {"ok": true}
- [ ] /start працює в Telegram
- [ ] Кнопка "Купити курс" відкриває Stripe сторінку

---

**Версія:** 2.2.0  
**Автор:** Andrii Pylypchuk  
**Документація:** docs/DEPLOYMENT.md

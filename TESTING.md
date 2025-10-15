# TESTING.md — Керівництво з тестування

## 🧪 Локальне тестування

### 1. Тестування Telegram бота

#### Основні команди:
```
/start          → Має показати головне меню
🎓 Вступний урок → Має показати урок 1 з базою даних
💳 Придбати курс → Має показати посилання /pay
ℹ️ Про курс     → Має відповісти через OpenAI
⚖️ Юридична інф → Має показати меню юридичних документів
```

#### Перевірка бази даних:
```powershell
# Відкрийте базу даних
sqlite3 app.db

# Перевірте користувачів
SELECT * FROM users;

# Перевірте чи збережено user_id після /start
SELECT user_id, username, seen_intro_at FROM users;

# Вийдіть
.quit
```

### 2. Тестування текстових повідомлень

Надішліть будь-який текст боту:
- ✅ Має відповісти через OpenAI GPT
- ✅ Не має викидати помилки "null content"

### 3. Тестування голосових повідомлень

Надішліть голосове повідомлення:
- ✅ Має розпізнати через Whisper (STT)
- ✅ Має відповісти текстом через GPT
- ✅ Опціонально: має озвучити через TTS

### 4. Тестування юридичних документів

Натисніть "⚖️ Юридична інформація":
- ✅ Має показати меню з 5 кнопками
- ✅ Кожна кнопка має показати відповідний документ з `data/legal/`
- ✅ Кнопка "🔙 Назад" має повернути до головного меню

### 5. Тестування системи нагадувань

```python
# У Python консолі
from app.storage.db import users_due_for_reminder
import os

# Перевірте користувачів для нагадування
os.environ["REMINDER_DAYS"] = "0"  # Для тесту
users = users_due_for_reminder(0)
print(f"Users to remind: {users}")
```

## 💳 Тестування Stripe

### Локальне тестування з Stripe CLI

#### 1. Встановіть Stripe CLI
```powershell
# Windows (з Scoop)
scoop install stripe

# Або завантажте з https://stripe.com/docs/stripe-cli
```

#### 2. Авторизуйтеся
```powershell
stripe login
```

#### 3. Запустіть webhook forwarding
```powershell
# У терміналі 1: запустіть веб-сервер
uvicorn app.web.server:app --reload

# У терміналі 2: запустіть forwarding
stripe listen --forward-to localhost:8000/stripe/webhook

# Скопіюйте webhook secret і додайте до .env
```

#### 4. Тестові платежі

Використовуйте тестові картки Stripe:
- **Успішна оплата**: `4242 4242 4242 4242`
- **Відхилена**: `4000 0000 0000 0002`
- CVV: будь-які 3 цифри
- Дата: будь-яка майбутня

### Тестування через бота

```
1. Натисніть "💳 Придбати курс"
2. Скопіюйте посилання (має містити user_id)
3. Відкрийте в браузері
4. Заповніть форму Stripe тестовою карткою
5. Перевірте:
   - ✅ Редірект на /paid
   - ✅ Webhook отримано
   - ✅ is_paid=1 в базі даних
```

### Перевірка в базі даних
```sql
-- Перевірте статус оплати
SELECT user_id, username, is_paid, stripe_session_id FROM users WHERE user_id = ВАШ_USER_ID;

-- Має показати is_paid = 1
```

## 🔍 Перевірка логів

### Логи бота
```powershell
# Під час роботи бота шукайте:
✅ Reminder scheduler started
✅ Bot is running...
✅ Payment successful for user XXX
```

### Логи Stripe webhook
```powershell
# У Stripe CLI
stripe listen --print-json

# Або в коді (встановіть DEBUG=true в .env)
```

## 🐛 Типові помилки та рішення

### Помилка: "ModuleNotFoundError: No module named 'app.storage'"
```powershell
# Переконайтесь що запускаєте з кореня проекту
python -m app.bot.main  # ✅ Правильно
cd app && python bot/main.py  # ❌ Неправильно
```

### Помилка: "BadRequestError: Invalid value for 'content'"
```
Вже виправлено: додано фільтр F.text в handlers/text.py
```

### Помилка: "sqlite3.OperationalError: no such table: users"
```powershell
# База створюється автоматично при першому запуску
# Якщо проблема залишається - видаліть app.db та перезапустіть
rm app.db
python -m app.bot.main
```

### Stripe webhook не спрацьовує
```
1. Перевірте STRIPE_WEBHOOK_SECRET в .env
2. Перевірте що веб-сервер запущено
3. Використайте Stripe CLI для локального тестування
4. Перевірте URL в Stripe Dashboard (має бути HTTPS для продакшена)
```

## ✅ Чеклист перед деплоєм

- [ ] `.env` налаштовано з правильними ключами
- [ ] База даних створюється автоматично
- [ ] Бот відповідає на `/start`
- [ ] OpenAI API працює (текстові та голосові повідомлення)
- [ ] Stripe тест пройдено успішно
- [ ] Webhook отримує події
- [ ] Юридичні документи показуються коректно
- [ ] Система нагадувань запущена
- [ ] Логи чисті без критичних помилок

## 📊 Моніторинг після запуску

### Перевірка кожні 24 години:
```sql
-- Скільки користувачів зареєструвалось
SELECT COUNT(*) FROM users;

-- Скільки оплатили
SELECT COUNT(*) FROM users WHERE is_paid=1;

-- Конверсія
SELECT 
  ROUND(100.0 * SUM(CASE WHEN is_paid=1 THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate
FROM users 
WHERE seen_intro_at IS NOT NULL;
```

### Логи помилок
```bash
# Шукайте в логах
grep -i "error\|exception\|failed" bot.log
```

## 🎯 Метрики успіху

- **Конверсія**: >10% користувачів після intro купують курс
- **Час до покупки**: <3 дні після вступного уроку
- **Помилки**: <1% від загальної кількості запитів
- **Час відповіді бота**: <2 секунди

---

**Підтримка**: Якщо виникли проблеми, створіть Issue на GitHub.

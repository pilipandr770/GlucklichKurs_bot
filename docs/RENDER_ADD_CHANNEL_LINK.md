# ⚠️ ВАЖЛИВО: Додати PAID_CHANNEL_LINK на Render

## Проблема
Після deploy код працює, але **webhook не надішле лінк**, якщо `PAID_CHANNEL_LINK` не встановлено в Render.

---

## ✅ Рішення: Додати env var на Render

### Крок 1: Відкрий Render Dashboard
https://dashboard.render.com/

### Крок 2: Вибери сервіс
**glucklichkurs-bot** → **Environment**

### Крок 3: Додай нову змінну
Натисни **Add Environment Variable**

- **Key:** `PAID_CHANNEL_LINK`
- **Value:** `https://t.me/+BVlgP_AqpcowYTcy`

### Крок 4: Збережи
Натисни **Save Changes**

### Крок 5: Перезапусти (опційно)
Render автоматично перезапустить сервіс, або можеш натиснути **Manual Deploy**

---

## 🧪 Перевірка

1. Після deploy зайди в **Logs**
2. Натисни `/pay` в боті
3. Оплата (тестова картка Stripe)
4. Перевір логи:
   ```
   ✅ Payment successful for user 123456789
   ✅ Notification sent to user 123456789
   ```

5. Перевір Telegram — має прийти повідомлення:
   ```
   🎉 Оплату підтверджено!
   
   Вітаємо у закритому курсі «10 кроків до щастя».
   Приєднуйтесь до приватного каналу з уроками:
   
   🔗 https://t.me/+BVlgP_AqpcowYTcy
   ```

---

## ❌ Troubleshooting

**Повідомлення не приходить:**
- ✅ Перевір: `PAID_CHANNEL_LINK` встановлено на Render
- ✅ Перевір: `TELEGRAM_BOT_TOKEN` правильний
- ✅ Перевір логи: чи є помилки в `_notify_user()`

**Лінк не працює:**
- ✅ Перевір: лінк починається з `https://t.me/+`
- ✅ Перевір: інвайт-лінк не застарів (створи новий в настройках каналу)

---

**Статус:** Критично важливо додати перед тестуванням!

# 🚀 Швидкий чеклист: Production Payment Flow

## ✅ Що вже зроблено (в коді):

- [x] `/pay?tg_id=123` — передача Telegram ID в Stripe
- [x] Webhook автоматично надсилає інвайт-лінк
- [x] Команда `/pay` формує правильний URL
- [x] Кнопка "Купити курс" оновлена
- [x] Документація створена

---

## ⏳ Що треба зробити ТОБІ (3 хвилини):

### 1️⃣ Додати PAID_CHANNEL_LINK на Render

**Де:** https://dashboard.render.com/ → glucklichkurs-bot → Environment

**Що додати:**
```
Key: PAID_CHANNEL_LINK
Value: https://t.me/+BVlgP_AqpcowYTcy
```

**Як:**
1. Відкрий Render Dashboard
2. glucklichkurs-bot → Environment tab
3. "Add Environment Variable"
4. Введи Key + Value
5. Save Changes
6. Чекай 2-3 хв (auto-redeploy)

---

### 2️⃣ Перевірити Stripe Webhook URL

**Де:** https://dashboard.stripe.com/webhooks

**Має бути:**
```
URL: https://glucklichkurs-bot.onrender.com/stripe/webhook
Events: checkout.session.completed
```

**Якщо немає:**
1. Create webhook endpoint
2. URL: `https://glucklichkurs-bot.onrender.com/stripe/webhook`
3. Events to send: `checkout.session.completed`
4. Копіюй Signing secret → Render env `STRIPE_WEBHOOK_SECRET`

---

### 3️⃣ Протестувати потік

**Тест 1: Команда /pay**
1. Напиши боту `/pay`
2. Має показати лінк: `https://glucklichkurs-bot.onrender.com/pay?tg_id=твій_id`

**Тест 2: Кнопка "Купити"**
1. Натисни кнопку в меню
2. Має показати той самий лінк

**Тест 3: Оплата (тестова картка)**
```
Картка: 4242 4242 4242 4242
Термін: будь-який майбутній
CVC: будь-який 3-значний
```

**Тест 4: Отримання лінку**
- Через 2-5 сек після оплати має прийти повідомлення:
  ```
  🎉 Оплату підтверджено!
  
  Вітаємо у закритому курсі...
  🔗 https://t.me/+BVlgP_AqpcowYTcy
  ```

---

## 📊 Перевірка логів Render

Після тестової оплати перевір:

```
✅ Payment successful for user 123456789, session cs_xxx
✅ Notification sent to user 123456789
```

Якщо бачиш:
```
⚠️ TELEGRAM_BOT_TOKEN not set, skipping notification
```
→ Перевір env vars на Render

---

## 🎯 Результат

Після виконання чеклисту:

✅ Користувач натискає `/pay`
✅ Переходить на Stripe Checkout
✅ Оплачує картою
✅ **Автоматично** отримує інвайт-лінк в Telegram
✅ Переходить за лінком → доступ до каналу
✅ Coach Agent відповідає на питання

**Час від оплати до доступу: 2-5 секунд** ⚡

---

## 📝 Наступні кроки (опційно):

1. **Guard rules для Sales Agent** — заборона на медичні поради
2. **Guard rules для Coach Agent** — заборона на збір приватних даних
3. **Публікація уроків в канал** — автопостинг 10 уроків
4. **Нагадування** — через 2-3 дні після вступного уроку
5. **Analytics** — скільки користувачів оплатило

---

**Статус:** Готово до production! 🎉
**Версія:** v3.0.0
**Пріоритет:** Додати PAID_CHANNEL_LINK на Render (критично!)

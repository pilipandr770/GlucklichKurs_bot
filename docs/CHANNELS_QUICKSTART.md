# Швидкий старт: Налаштування каналів

## ⚠️ ВАЖЛИВО: Виправте ID каналів у .env

### Поточна конфігурація (НЕПРАВИЛЬНА):
```env
INTRO_CHANNEL_ID=https://web.telegram.org/k/#-2911331449
PAID_CHANNEL_ID=https://web.telegram.org/k/#-3140324634
```

### Правильна конфігурація:
```env
INTRO_CHANNEL_ID=-1002911331449       # Опціонально
PAID_CHANNEL_ID=-1003140324634        # Обов'язково
```

---

## 🔧 Як отримати правильний ID каналу

### Метод 1: Через @getmyid_bot
1. Додайте бота `@getmyid_bot` до вашого каналу як адміна
2. Напишіть щось у канал
3. Бот покаже ID каналу (формат: `-100...`)
4. Видаліть `@getmyid_bot` після отримання ID

### Метод 2: Через @userinfobot
1. Перешліть повідомлення з каналу до `@userinfobot`
2. Бот покаже ID каналу

### Метод 3: Вручну з URL
Ваш URL: `https://web.telegram.org/k/#-2911331449`
Правильний ID: `-1002911331449` (додайте `-100` на початок)

---

## 🤖 Додайте бота адміном до платного каналу

### Налаштування:
1. Відкрийте ваш платний канал у Telegram
2. **Налаштування → Адміністратори → Додати адміністратора**
3. Знайдіть вашого бота (наприклад, `@GlucklichKurs_bot`)
4. **Встановіть галочку: "Invite users via link"** ✅
5. Опціонально: "Post messages" (якщо бот публікуватиме контент)
6. Збережіть зміни

---

## ✅ Перевірка правильності налаштування

### Тест 1: Запустіть скрипт перевірки
```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('INTRO_CHANNEL_ID:', os.getenv('INTRO_CHANNEL_ID')); print('PAID_CHANNEL_ID:', os.getenv('PAID_CHANNEL_ID'))"
```

**Очікуваний результат:**
```
INTRO_CHANNEL_ID: -1002911331449
PAID_CHANNEL_ID: -1003140324634
```

### Тест 2: Перевірка доступу бота
```python
# Створіть файл test_channels.py
import os
import asyncio
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

async def test_channels():
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    
    paid_channel_id = int(os.getenv("PAID_CHANNEL_ID"))
    
    try:
        # Перевірка, чи бот є адміном
        chat = await bot.get_chat(paid_channel_id)
        print(f"✅ Канал знайдено: {chat.title}")
        
        # Перевірка прав
        bot_member = await bot.get_chat_member(paid_channel_id, bot.id)
        print(f"✅ Статус бота: {bot_member.status}")
        
        if bot_member.can_invite_users:
            print("✅ Бот може запрошувати користувачів")
        else:
            print("❌ Бот НЕ МОЖЕ запрошувати користувачів! Додайте право 'Invite users via link'")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        print("Переконайтесь, що:")
        print("1. Бот доданий адміном до каналу")
        print("2. ID каналу правильний (формат -100...)")
        print("3. Бот має право 'Invite users via link'")
    
    await bot.session.close()

asyncio.run(test_channels())
```

**Запустіть:**
```powershell
python test_channels.py
```

---

## 🔗 Автоматична відправка інвайт-лінків (TODO)

### Зараз: Користувач отримує лише підтвердження оплати

### Потрібно: Додати код у `app/web/stripe_webhook.py`

**Знайдіть:**
```python
if user_id:
    user_id = int(user_id)
    mark_paid(user_id, session.id)
```

**Додайте після:**
```python
    # ✅ Відправка інвайт-лінку
    try:
        from aiogram import Bot
        
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        paid_channel_id = int(os.getenv("PAID_CHANNEL_ID"))
        
        # Створення одноразового лінку
        invite_link = await bot.create_chat_invite_link(
            chat_id=paid_channel_id,
            member_limit=1,  # Тільки для цього користувача
            name=f"User {user_id}"
        )
        
        # Відправка користувачу
        await bot.send_message(
            chat_id=user_id,
            text=f"🎉 Вітаємо! Ваша оплата підтверджена.\n\n"
                 f"✅ Доступ до всіх 10 уроків відкрито\n"
                 f"✅ Коуч-агент готовий відповідати на питання\n\n"
                 f"🔗 Приєднуйтесь до закритого каналу:\n"
                 f"{invite_link.invite_link}\n\n"
                 f"Бажаємо успіхів! 🌟"
        )
        
        await bot.session.close()
    except Exception as e:
        print(f"❌ Помилка відправки інвайт-лінку: {e}")
```

**Детальна інструкція:** `docs/CHANNELS_SETUP.md`

---

## 📝 Оновіть .env файл

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=ваш_токен

# Канали (ВИПРАВТЕ ID!)
INTRO_CHANNEL_ID=-1002911331449          # Вступний канал (опціонально)
PAID_CHANNEL_ID=-1003140324634           # Платний канал (ОБОВ'ЯЗКОВО)

# OpenAI
OPENAI_API_KEY=ваш_ключ

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Інші налаштування
REMINDER_DAYS=3
```

---

## 🎯 Чеклист

- [ ] Виправлено INTRO_CHANNEL_ID у .env (формат `-100...`)
- [ ] Виправлено PAID_CHANNEL_ID у .env (формат `-100...`)
- [ ] Бот доданий адміном до платного каналу
- [ ] Встановлено право "Invite users via link"
- [ ] Запущено `test_channels.py` — всі перевірки пройшли ✅
- [ ] Додано код автоматичної відправки інвайт-лінків (опціонально)
- [ ] Протестовано повний цикл: покупка → отримання лінку

---

## ❓ Проблеми та рішення

### Помилка: "Chat not found"
**Причина:** Неправильний ID або бот не доданий до каналу  
**Рішення:** 
1. Перевірте формат ID: `-100...`
2. Додайте бота адміном до каналу

### Помилка: "Not enough rights to invite users"
**Причина:** Бот не має права запрошувати  
**Рішення:** У налаштуваннях каналу встановіть галочку "Invite users via link"

### Інвайт-лінк не відправляється
**Причина:** Код ще не додано в `stripe_webhook.py`  
**Рішення:** Додайте код згідно інструкції вище

---

**Детальна документація:** `docs/CHANNELS_SETUP.md` (повний гайд 200+ рядків)

**Версія:** 2.2.0  
**Автор:** Andrii Pylypchuk

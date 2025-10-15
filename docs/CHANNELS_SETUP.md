# Система Telegram-каналів

## Огляд

Проект використовує **два Telegram-канали** для організації контенту:

### 1️⃣ Вступний канал (INTRO_CHANNEL_ID)
**Призначення:** Публічний або напівпублічний контент для ознайомлення  
**Статус:** Опціональний  
**Налаштування:** `.env` → `INTRO_CHANNEL_ID`

**Можливий контент:**
- Анонси нових уроків
- Мотиваційні цитати з курсу
- Безплатні міні-поради
- Відгуки користувачів

---

### 2️⃣ Платний канал (PAID_CHANNEL_ID)
**Призначення:** Закритий канал для оплачених користувачів  
**Статус:** Обов'язковий  
**Налаштування:** `.env` → `PAID_CHANNEL_ID`

**Контент:**
- Повні тексти всіх 10 уроків
- Додаткові матеріали та вправи
- Приватна підтримка та обговорення
- Бонусний контент

---

## Поточна конфігурація

### З файлу `.env`:
```env
INTRO_CHANNEL_ID=https://web.telegram.org/k/#-2911331449
PAID_CHANNEL_ID=https://web.telegram.org/k/#-3140324634
```

⚠️ **Важливо:** Формат ID у файлі має бути виправлений. Telegram Channel ID повинен бути числом, а не URL.

### Правильний формат:
```env
INTRO_CHANNEL_ID=-1001234567890    # Опціонально
PAID_CHANNEL_ID=-1009876543210     # Обов'язково
```

**Як отримати правильний ID каналу:**
1. Додайте бота `@getmyid_bot` до вашого каналу як адміна
2. Напишіть щось в канал
3. Бот покаже ID каналу (формат: `-100...`)
4. Видаліть бота `@getmyid_bot` після отримання ID

---

## Налаштування бота в каналах

### Необхідні дозволи для бота:

#### У платному каналі (PAID_CHANNEL_ID):
1. ✅ **Адміністратор каналу**
2. ✅ **Може запрошувати користувачів через посилання** (Invite users via link)
3. ✅ **Може публікувати повідомлення** (Post messages) - опціонально
4. ✅ **Може редагувати повідомлення** (Edit messages) - опціонально

#### Як додати бота адміном:
1. Відкрийте канал в Telegram
2. Налаштування → Адміністратори → Додати адміністратора
3. Знайдіть вашого бота за username (наприклад, `@GlucklichKurs_bot`)
4. Встановіть галочку "Invite users via link"
5. Збережіть

---

## Автоматична відправка інвайт-лінків (TODO)

### Поточний стан:
❌ **НЕ реалізовано** — користувач отримує підтвердження оплати, але інвайт-лінк не надсилається автоматично.

### План реалізації:

#### 1. Створення інвайт-лінку після оплати
**Файл:** `app/web/stripe_webhook.py`

```python
async def handle_stripe_event(event):
    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = session.metadata.get("telegram_user_id")
        
        if user_id:
            user_id = int(user_id)
            mark_paid(user_id, session.id)
            
            # ✅ ДОДАТИ: Створення інвайт-лінку
            try:
                from aiogram import Bot
                import os
                
                bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
                paid_channel_id = int(os.getenv("PAID_CHANNEL_ID"))
                
                # Створення одноразового інвайт-лінку
                invite_link = await bot.create_chat_invite_link(
                    chat_id=paid_channel_id,
                    member_limit=1,  # Лише для цього користувача
                    name=f"Invite for user {user_id}"
                )
                
                # Відправка лінку користувачу
                await bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 Вітаємо! Ваша оплата підтверджена.\n\n"
                         f"✅ Тепер у вас є доступ до всіх 10 уроків курсу.\n"
                         f"✅ Ви можете ставити питання коуч-агенту в будь-який час.\n\n"
                         f"🔗 Приєднуйтесь до закритого каналу за посиланням:\n"
                         f"{invite_link.invite_link}\n\n"
                         f"Бажаємо успіхів на шляху до щастя! 🌟"
                )
                
                await bot.session.close()
            except Exception as e:
                print(f"Error sending invite link: {e}")
```

#### 2. Оновлення handler оплати
**Файл:** `app/bot/handlers/buy.py`

Додати кнопку "Перевірити оплату":
```python
@router.callback_query(F.data=="check_payment")
async def check_payment(cb: types.CallbackQuery):
    user = get_user_by_id(cb.from_user.id)
    
    if user and user.get("is_paid"):
        # Якщо інвайт вже надіслано, нагадати
        await cb.message.answer(
            "✅ Ваша оплата підтверджена!\n"
            "Перевірте особисті повідомлення — там має бути посилання на закритий канал."
        )
    else:
        await cb.message.answer(
            "⏳ Оплата ще обробляється. Зачекайте 1-2 хвилини та спробуйте знову."
        )
    await cb.answer()
```

---

## Альтернативний підхід: Ручне додавання

### Якщо автоматизація не потрібна:

1. **Після оплати:** Бот надсилає адміну повідомлення
2. **Адмін вручну:** Додає користувача до каналу
3. **Користувач:** Отримує сповіщення про доступ

**Файл:** `app/web/stripe_webhook.py`
```python
ADMIN_ID = 123456789  # Ваш Telegram ID

await bot.send_message(
    chat_id=ADMIN_ID,
    text=f"💰 Нова оплата!\n"
         f"User ID: {user_id}\n"
         f"Username: @{username}\n"
         f"Додайте до каналу вручну."
)
```

---

## Типи інвайт-лінків

### 1. Одноразовий лінк (рекомендовано)
```python
invite_link = await bot.create_chat_invite_link(
    chat_id=channel_id,
    member_limit=1,          # Тільки 1 користувач
    expire_date=None,        # Без терміну дії
    name=f"User {user_id}"
)
```

**Переваги:**
- Безпечніше (лінк не можна передати)
- Можна відстежити, хто використав
- Автоматично деактивується після використання

---

### 2. Тимчасовий лінк
```python
from datetime import datetime, timedelta

expire_time = datetime.now() + timedelta(days=7)

invite_link = await bot.create_chat_invite_link(
    chat_id=channel_id,
    expire_date=expire_time,   # Дійсний 7 днів
    member_limit=1,
    name=f"User {user_id}"
)
```

---

### 3. Багаторазовий лінк (НЕ рекомендовано)
```python
invite_link = await bot.create_chat_invite_link(
    chat_id=channel_id,
    member_limit=None,    # Необмежено
    creates_join_request=False
)
```

⚠️ **Ризик:** Користувач може поділитись лінком з іншими.

---

## Моніторинг доступу

### Перевірка членства в каналі:
```python
from aiogram.types import ChatMemberStatus

async def check_channel_membership(bot, user_id, channel_id):
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
    except:
        return False
```

### Використання:
```python
is_member = await check_channel_membership(bot, user_id, PAID_CHANNEL_ID)

if not is_member and user_is_paid:
    # Надіслати інвайт знову
    await resend_invite(user_id)
```

---

## Безпека

### ✅ Рекомендовані практики:
1. Використовуйте одноразові лінки (member_limit=1)
2. Регулярно перевіряйте список учасників каналу
3. Видаляйте користувачів після refund (якщо впроваджено)
4. Не публікуйте PAID_CHANNEL_ID у відкритих місцях
5. Ротація інвайт-лінків раз на місяць

### ⚠️ Що НЕ робити:
- ❌ Публічні посилання на платний канал
- ❌ Багаторазові лінки без обмежень
- ❌ Відсутність перевірки оплати перед відправкою лінку

---

## Чеклист налаштування

- [ ] Створено два Telegram-канали (intro + paid)
- [ ] Отримано правильні ID каналів (формат `-100...`)
- [ ] Бот доданий адміном до платного каналу
- [ ] Встановлено дозвіл "Invite users via link"
- [ ] Оновлено `.env` з правильними ID
- [ ] Протестовано створення інвайт-лінку через `@BotFather`
- [ ] Реалізовано автоматичну відправку лінків (або ручний процес)
- [ ] Додано кнопку "Перевірити оплату" в бота
- [ ] Налаштовано моніторинг членства в каналі

---

## FAQ

**Q: Чому інвайт-лінк не працює?**  
A: Переконайтесь, що бот має дозвіл "Invite users via link" як адмін каналу.

**Q: Як видалити користувача з каналу?**  
```python
await bot.ban_chat_member(channel_id, user_id)
await bot.unban_chat_member(channel_id, user_id)  # Розбанити, щоб міг приєднатись пізніше
```

**Q: Скільки коштує створення інвайт-лінків?**  
A: Безплатно. Telegram API не має обмежень на кількість лінків.

**Q: Чи можна використовувати групу замість каналу?**  
A: Так, але канали краще для односторонньої комунікації (курси, новини).

---

**Автор:** Andrii Pylypchuk  
**Проект:** GlückenKurs Bot  
**Версія:** 2.2.0

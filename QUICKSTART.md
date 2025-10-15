# ⚡ Швидкий старт

## Проблема: "Перекидає в Telegram при оплаті"

### ✅ Рішення:

1. **Виправлено `.env`:**
```env
BASE_URL=http://localhost:8000  # Змінено з Telegram URL
```

2. **Запустіть ДВА процеси:**

### Варіант 1: Автоматичний запуск (рекомендовано)
```powershell
.\start.ps1
```

### Варіант 2: Два термінали вручну

**Термінал 1 - Веб-сервер:**
```powershell
uvicorn app.web.server:app --host 0.0.0.0 --port 8000 --reload
```

**Термінал 2 - Telegram бот:**
```powershell
python -m app.bot.main
```

---

## 🧪 Як протестувати оплату:

1. Відкрийте бота в Telegram: `/start`
2. Натисніть "💰 Купити курс"
3. Підтвердіть умови
4. Натисніть "💳 Перейти до оплати"
5. **Зараз відкриється Stripe, а не Telegram!** ✅
6. Використайте тестову картку: `4242 4242 4242 4242`
7. Заповніть: MM/YY: `12/34`, CVC: `123`
8. Після оплати побачите: "✅ Дякуємо за оплату!"

---

## 📋 Чеклист перед тестом:

- [ ] `.env` файл створений
- [ ] `BASE_URL=http://localhost:8000` (НЕ Telegram URL!)
- [ ] Веб-сервер запущений (порт 8000)
- [ ] Telegram бот запущений
- [ ] http://localhost:8000/health працює

---

## 🐛 Якщо щось не працює:

### "Connection refused" при /pay
```powershell
# Перевірте, чи запущений веб-сервер
curl http://localhost:8000/health
```

### Порт 8000 зайнятий
```powershell
# Знайти процес
Get-NetTCPConnection -LocalPort 8000

# Вбити процес
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

---

**Детальна документація:** `docs/RUN_LOCALLY.md`

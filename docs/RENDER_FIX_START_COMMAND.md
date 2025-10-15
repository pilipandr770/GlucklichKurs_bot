# 🚨 Виправлення Start Command в Render

## Проблема
```
gunicorn.errors.AppImportError: Failed to find attribute 'app' in 'app'.
```

Render використовує дефолтну команду `gunicorn app:app` замість правильної з `render.yaml`.

---

## ✅ Рішення: Оновити Start Command в Dashboard

### Крок 1: Відкрити Settings
1. Перейдіть: https://dashboard.render.com/
2. Знайдіть сервіс **gluckenkurs-web**
3. Клацніть на сервіс → **Settings**

### Крок 2: Оновити Start Command
Знайдіть поле **Start Command** і введіть:

```bash
gunicorn app.web.server:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Крок 3: Зберегти та перезапустити
1. Натисніть **Save Changes**
2. Перейдіть на вкладку **Manual Deploy**
3. Натисніть **Deploy latest commit**

---

## 📋 Правильні команди для обох сервісів

### Web Service (gluckenkurs-web):
```bash
# Build Command:
pip install -r requirements.txt

# Start Command:
gunicorn app.web.server:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Worker Service (gluckenkurs-bot):
```bash
# Build Command:
pip install -r requirements.txt

# Start Command:
python scripts/migrate_db.py && python -m app.bot.main
```

---

## 🔍 Перевірка після деплою

```bash
# 1. Перевірте health endpoint
curl https://gluckenkurs-web.onrender.com/health
# Має повернути: {"ok":true}

# 2. Перевірте логи
Dashboard → gluckenkurs-web → Logs
# Має бути: "Uvicorn running on..."
```

---

## 🐛 Альтернатива: Procfile

Якщо Start Command не працює, створіть `Procfile`:

```bash
# У корені проекту
echo "web: gunicorn app.web.server:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:\$PORT" > Procfile
git add Procfile
git commit -m "Add Procfile for Render"
git push
```

Render автоматично виявить `Procfile` і використає команду звідти.

---

**Статус:** Python 3.11.9 ✅ | Dependencies ✅ | Start Command ❌ (треба виправити в Dashboard)

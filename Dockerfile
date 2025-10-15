# Dockerfile для GlückenKurs Bot на Render
FROM python:3.11-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо requirements
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код
COPY . .

# Порт для веб-сервера (Render встановить $PORT)
ENV PORT=8000

# За замовчуванням запускаємо бота (можна перевизначити в render.yaml)
CMD ["python", "-m", "app.bot.main"]

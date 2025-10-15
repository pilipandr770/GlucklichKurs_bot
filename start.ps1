# Скрипт для запуску GlückenKurs Bot (Windows PowerShell)
# Запускає веб-сервер та Telegram бота одночасно

Write-Host "🚀 Запуск GlückenKurs Bot..." -ForegroundColor Green
Write-Host ""

# Перевірка .env файлу
if (-Not (Test-Path ".env")) {
    Write-Host "❌ Файл .env не знайдено!" -ForegroundColor Red
    Write-Host "Скопіюйте .env.example в .env та заповніть ключі" -ForegroundColor Yellow
    exit 1
}

# Перевірка BASE_URL
$envContent = Get-Content .env -Raw
if ($envContent -match 'BASE_URL=https://web.telegram.org') {
    Write-Host "⚠️  УВАГА: BASE_URL вказує на Telegram!" -ForegroundColor Yellow
    Write-Host "   Оплата не працюватиме правильно." -ForegroundColor Yellow
    Write-Host "   Рекомендовано: BASE_URL=http://localhost:8000" -ForegroundColor Yellow
    Write-Host ""
}

# Перевірка порту 8000
$portCheck = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portCheck) {
    Write-Host "⚠️  Порт 8000 зайнятий! Звільняю..." -ForegroundColor Yellow
    $process = Get-Process -Id $portCheck.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $process.Id -Force
        Start-Sleep -Seconds 2
    }
}

Write-Host "1️⃣  Запуск веб-сервера (FastAPI) на порту 8000..." -ForegroundColor Cyan
Start-Job -Name "WebServer" -ScriptBlock {
    Set-Location $using:PWD
    uvicorn app.web.server:app --host 0.0.0.0 --port 8000 --reload
} | Out-Null

# Чекаємо, поки сервер запуститься
Write-Host "   Чекаємо запуску сервера..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Перевіряємо health endpoint
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Веб-сервер запущений: http://localhost:8000" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Веб-сервер запускається... (може зайняти ще 5-10 сек)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "2️⃣  Запуск Telegram бота..." -ForegroundColor Cyan
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

# Запускаємо бота в основному процесі
try {
    python -m app.bot.main
} catch {
    Write-Host ""
    Write-Host "❌ Помилка запуску бота!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "🛑 Зупинка сервісів..." -ForegroundColor Yellow
    
    # Зупиняємо веб-сервер
    Get-Job -Name "WebServer" -ErrorAction SilentlyContinue | Stop-Job
    Get-Job -Name "WebServer" -ErrorAction SilentlyContinue | Remove-Job
    
    Write-Host "✅ Всі сервіси зупинені" -ForegroundColor Green
}

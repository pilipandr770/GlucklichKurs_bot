"""
Скрипт для перевірки та видалення webhook з Telegram Bot
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def check_webhook():
    """Перевіряє поточний webhook"""
    response = requests.get(f"{BASE_URL}/getWebhookInfo")
    data = response.json()
    
    if data["ok"]:
        info = data["result"]
        print("📋 Webhook Info:")
        print(f"  URL: {info.get('url', 'NOT SET')}")
        print(f"  Pending updates: {info.get('pending_update_count', 0)}")
        print(f"  Last error: {info.get('last_error_message', 'None')}")
        return info.get('url', '')
    else:
        print("❌ Failed to get webhook info")
        return None

def delete_webhook():
    """Видаляє webhook і очищує pending updates"""
    print("\n🗑️  Deleting webhook...")
    response = requests.post(f"{BASE_URL}/deleteWebhook?drop_pending_updates=true")
    data = response.json()
    
    if data["ok"]:
        print("✅ Webhook successfully deleted!")
        return True
    else:
        print(f"❌ Failed to delete webhook: {data}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Telegram Bot webhook status...\n")
    
    webhook_url = check_webhook()
    
    if webhook_url:
        print(f"\n⚠️  WARNING: Webhook is SET to: {webhook_url}")
        print("This will conflict with polling mode on Render!")
        
        confirm = input("\nDelete webhook? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            delete_webhook()
            print("\n✅ Done! Now bot can use polling mode.")
        else:
            print("\n❌ Webhook not deleted. Bot will continue to conflict.")
    else:
        print("\n✅ No webhook set. Polling mode should work fine!")

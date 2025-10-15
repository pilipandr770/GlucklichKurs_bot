#!/usr/bin/env python3
"""
Міграція БД для GlückenKurs Bot
Створює схему та таблиці в PostgreSQL на Render
"""
import os
import sys

def migrate():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    DB_SCHEMA = os.environ.get("DB_SCHEMA", "gluckenkurs")
    
    if not DATABASE_URL:
        print("⚠️  DATABASE_URL не встановлено. Пропускаємо міграцію (використовується SQLite)")
        return
    
    print(f"🔄 Початок міграції БД...")
    print(f"   Схема: {DB_SCHEMA}")
    
    try:
        import psycopg2
        
        # Render надає postgres://, але psycopg2 потребує postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            # Створюємо схему
            print(f"📦 Створення схеми {DB_SCHEMA}...")
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}")
            
            # Створюємо таблицю users
            print(f"📊 Створення таблиці {DB_SCHEMA}.users...")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    seen_intro_at BIGINT,
                    reminder_sent INTEGER DEFAULT 0,
                    is_paid INTEGER DEFAULT 0,
                    stripe_session_id TEXT,
                    created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT
                )
            """)
            
            # Створюємо індекси для швидшого пошуку
            print(f"🔍 Створення індексів...")
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_users_stripe_session 
                ON {DB_SCHEMA}.users(stripe_session_id)
                WHERE stripe_session_id IS NOT NULL
            """)
            
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_users_reminders
                ON {DB_SCHEMA}.users(seen_intro_at, reminder_sent, is_paid)
                WHERE seen_intro_at IS NOT NULL
            """)
        
        conn.close()
        
        print("✅ Міграція успішно завершена!")
        return True
        
    except Exception as e:
        print(f"❌ Помилка міграції: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()

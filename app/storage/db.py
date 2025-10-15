# app/storage/db.py
"""
Автоматичний вибір БД:
- PostgreSQL (якщо DATABASE_URL встановлено) - для Render
- SQLite (локальна розробка)
"""
import os

# Перевіряємо, чи використовується PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    # Використовуємо PostgreSQL
    from .db_postgres import *
else:
    # Використовуємо SQLite (локальна розробка)
    import sqlite3, time
    
    DB_PATH = os.environ.get("DB_PATH", "app.db")
    
    def _conn():
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            seen_intro_at INTEGER,
            reminder_sent INTEGER DEFAULT 0,
            is_paid INTEGER DEFAULT 0,
            stripe_session_id TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now'))
        )""")
        conn.commit()
        return conn

    def upsert_user(user_id: int, username: str | None):
        with _conn() as c:
            c.execute("INSERT OR IGNORE INTO users(user_id,username) VALUES(?,?)", (user_id, username))
            if username:
                c.execute("UPDATE users SET username=? WHERE user_id=?", (username, user_id))
            c.commit()

    def mark_intro_seen(user_id: int):
        with _conn() as c:
            c.execute("UPDATE users SET seen_intro_at=?, reminder_sent=0 WHERE user_id=?", (int(time.time()), user_id))
            c.commit()

    def users_due_for_reminder(days: int):
        cutoff = int(time.time()) - days*24*3600
        with _conn() as c:
            cur = c.execute("""SELECT user_id FROM users
                WHERE seen_intro_at IS NOT NULL AND seen_intro_at<=?
                  AND COALESCE(reminder_sent,0)=0
                  AND COALESCE(is_paid,0)=0
            """, (cutoff,))
            return [r[0] for r in cur.fetchall()]

    def mark_reminded(user_id: int):
        with _conn() as c:
            c.execute("UPDATE users SET reminder_sent=1 WHERE user_id=?", (user_id,))
            c.commit()

    def mark_paid(user_id: int, stripe_session_id: str = None):
        with _conn() as c:
            c.execute("UPDATE users SET is_paid=1, stripe_session_id=? WHERE user_id=?", (stripe_session_id, user_id))
            c.commit()

    def get_user_by_id(user_id: int):
        with _conn() as c:
            cur = c.execute("SELECT user_id, username, is_paid FROM users WHERE user_id=?", (user_id,))
            row = cur.fetchone()
            if row:
                return {"user_id": row[0], "username": row[1], "is_paid": row[2]}
            return None

    def save_stripe_metadata(user_id: int, session_id: str):
        with _conn() as c:
            c.execute("UPDATE users SET stripe_session_id=? WHERE user_id=?", (session_id, user_id))
            c.commit()

    def get_user_by_stripe_session(session_id: str):
        with _conn() as c:
            cur = c.execute("SELECT user_id FROM users WHERE stripe_session_id=?", (session_id,))
            row = cur.fetchone()
            return row[0] if row else None

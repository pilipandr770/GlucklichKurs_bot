# app/storage/db_postgres.py
"""PostgreSQL database module with schema support for Render deployment"""
import os
import time
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL", "")
DB_SCHEMA = os.environ.get("DB_SCHEMA", "public")

# Render надає postgres://, але psycopg2 потребує postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def _conn():
    """PostgreSQL з'єднання з окремою схемою"""
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    
    with conn.cursor() as cur:
        # Створюємо схему, якщо не існує
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}")
        
        # Встановлюємо search_path для використання нашої схеми
        cur.execute(f"SET search_path TO {DB_SCHEMA}, public")
        
        # Створюємо таблицю users
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
    
    conn.commit()
    return conn

def upsert_user(user_id: int, username: Optional[str]):
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {DB_SCHEMA}, public")
            cur.execute(
                f"""
                INSERT INTO {DB_SCHEMA}.users(user_id, username)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username
                """,
                (user_id, username)
            )
        conn.commit()
    finally:
        conn.close()

def mark_intro_seen(user_id: int):
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {DB_SCHEMA}, public")
            cur.execute(
                f"""
                UPDATE {DB_SCHEMA}.users
                SET seen_intro_at = %s, reminder_sent = 0
                WHERE user_id = %s
                """,
                (int(time.time()), user_id)
            )
        conn.commit()
    finally:
        conn.close()

def users_due_for_reminder(days: int):
    cutoff = int(time.time()) - days * 24 * 3600
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {DB_SCHEMA}, public")
            cur.execute(
                f"""
                SELECT user_id FROM {DB_SCHEMA}.users
                WHERE seen_intro_at IS NOT NULL
                  AND seen_intro_at <= %s
                  AND COALESCE(reminder_sent, 0) = 0
                  AND COALESCE(is_paid, 0) = 0
                """,
                (cutoff,)
            )
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()

def mark_reminded(user_id: int):
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {DB_SCHEMA}, public")
            cur.execute(
                f"UPDATE {DB_SCHEMA}.users SET reminder_sent = 1 WHERE user_id = %s",
                (user_id,)
            )
        conn.commit()
    finally:
        conn.close()

def mark_paid(user_id: int, stripe_session_id: Optional[str] = None):
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {DB_SCHEMA}, public")
            cur.execute(
                f"""
                UPDATE {DB_SCHEMA}.users
                SET is_paid = 1, stripe_session_id = %s
                WHERE user_id = %s
                """,
                (stripe_session_id, user_id)
            )
        conn.commit()
    finally:
        conn.close()

def get_user_by_id(user_id: int):
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SET search_path TO {DB_SCHEMA}, public")
            cur.execute(
                f"""
                SELECT user_id, username, is_paid
                FROM {DB_SCHEMA}.users
                WHERE user_id = %s
                """,
                (user_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def save_stripe_metadata(user_id: int, session_id: str):
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {DB_SCHEMA}, public")
            cur.execute(
                f"""
                UPDATE {DB_SCHEMA}.users
                SET stripe_session_id = %s
                WHERE user_id = %s
                """,
                (session_id, user_id)
            )
        conn.commit()
    finally:
        conn.close()

def get_user_by_stripe_session(session_id: str):
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {DB_SCHEMA}, public")
            cur.execute(
                f"""
                SELECT user_id FROM {DB_SCHEMA}.users
                WHERE stripe_session_id = %s
                """,
                (session_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        conn.close()

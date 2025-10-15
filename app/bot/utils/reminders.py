# file: app/bot/utils/reminders.py
import json, asyncio, os, datetime as dt
from apscheduler.schedulers.asyncio import AsyncIOScheduler

STORE = ".reminders.json"

def add_user(user_id: int, days: int = 3):
    data = load()
    data[str(user_id)] = (dt.datetime.utcnow() + dt.timedelta(days=days)).isoformat()
    save(data)

def load():
    if not os.path.exists(STORE): return {}
    with open(STORE, "r", encoding="utf-8") as f: return json.load(f)

def save(data: dict):
    with open(STORE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

def due_users():
    now = dt.datetime.utcnow()
    for uid, when in load().items():
        try:
            if dt.datetime.fromisoformat(when) <= now:
                yield int(uid)
        except: continue

def remove_user(user_id: int):
    data = load()
    data.pop(str(user_id), None)
    save(data)

async def schedule(bot_send):
    sched = AsyncIOScheduler()
    async def job():
        for uid in list(due_users()):
            await bot_send(uid)
            remove_user(uid)
    sched.add_job(job, "interval", hours=1)
    sched.start()

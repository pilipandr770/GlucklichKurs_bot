# app/bot/utils/reminders.py
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ...storage.db import users_due_for_reminder, mark_reminded

REMINDER_DAYS = int(os.getenv("REMINDER_DAYS","3"))

async def start_reminders(send_func):
    sched = AsyncIOScheduler()
    
    async def job():
        for uid in users_due_for_reminder(REMINDER_DAYS):
            try:
                await send_func(uid)
                mark_reminded(uid)
            except Exception as e:
                print(f"Failed to send reminder to {uid}: {e}")
    
    sched.add_job(job, "interval", hours=1)
    sched.start()
    print(f"✅ Reminder scheduler started (checking every hour, {REMINDER_DAYS} days threshold)")

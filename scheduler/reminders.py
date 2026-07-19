"""
Background scheduler: periodically checks stored task/fact state and pushes
proactive reminders (e.g. via push notification, email, or next-chat-open banner).
This is the "reminds me of what to do" piece — it runs independent of the
user having a conversation open.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from memory.store import MemoryStore
from datetime import datetime, timezone

scheduler = BackgroundScheduler()


def check_reminders(tenant_id: str, notify_fn):
    """
    notify_fn: callable(str) -> None, wire this to push notifications,
    email, or a websocket event to the frontend.
    """
    memory = MemoryStore(tenant_id)
    due = memory.get_fact("next_reminder_due")
    if due and datetime.fromisoformat(due) <= datetime.now(timezone.utc):
        message = memory.get_fact("next_reminder_message") or "You have a pending task."
        notify_fn(message)
        memory.set_fact("next_reminder_due", "")  # clear until re-scheduled


def schedule_reminder(tenant_id: str, message: str, run_at: datetime):
    memory = MemoryStore(tenant_id)
    memory.set_fact("next_reminder_due", run_at.isoformat())
    memory.set_fact("next_reminder_message", message)


def start(tenant_id: str, notify_fn, interval_seconds: int = 60):
    scheduler.add_job(check_reminders, "interval", seconds=interval_seconds, args=[tenant_id, notify_fn])
    scheduler.start()

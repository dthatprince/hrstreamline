from celery import Celery
from celery.schedules import crontab  # <-- Import here
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery = Celery(
    "leave_app",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery.conf.beat_schedule = {
    "monthly-leave-accrual": {
        "task": "tasks.accrual.monthly_accrual",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),  # <-- Runs on 1st of every month at midnight
    },
    "check-leave-end-status-daily": {
        "task": "tasks.leave.end_leave_status_check",
        "schedule": crontab(hour=0, minute=30),  # Runs daily at 00:30 AM
    }
}

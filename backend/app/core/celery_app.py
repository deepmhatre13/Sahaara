"""Celery application + beat schedule.

Two processes run this module:

    celery -A app.core.celery_app.celery_app worker --loglevel=info
    celery -A app.core.celery_app.celery_app beat   --loglevel=info

Both need Redis reachable at ``CELERY_BROKER_URL`` / ``CELERY_RESULT_BACKEND``.
Celery is used only for genuinely periodic work (reminders); request-scoped
background work such as motion monitoring stays on the in-process monitor threads
so the API keeps working without a broker.
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "sahaara",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.reminders"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Reminders are idempotent-ish but should not pile up if a worker restarts.
    task_acks_late=True,
    worker_max_tasks_per_child=200,
)

celery_app.conf.beat_schedule = {
    "check-medication-reminders-every-minute": {
        "task": "app.tasks.reminders.check_medication_reminders",
        "schedule": crontab(minute="*"),
    },
    "check-appointment-reminders-every-5-minutes": {
        "task": "app.tasks.reminders.check_appointment_reminders",
        "schedule": crontab(minute="*/5"),
    },
}

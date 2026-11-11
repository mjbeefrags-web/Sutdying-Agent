from celery import Celery
from celery.schedules import schedule

from apps.api.app.core.config import get_settings

settings = get_settings()
celery_app = Celery(
    "study_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["apps.worker.app.tasks"],
)
celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_default_queue="default",
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "dispatch-database-outbox": {
            "task": "outbox.dispatch",
            "schedule": schedule(2.0),
        }
    },
)

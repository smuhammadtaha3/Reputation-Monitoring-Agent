from celery import Celery
from app.core.config import settings

celery = Celery(
    "reputation_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"]
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    beat_schedule={
        "poll-reviews-every-15-min": {
            "task": "app.workers.tasks.poll_reviews",
            "schedule": 900.0,  # seconds
        }
    }
)
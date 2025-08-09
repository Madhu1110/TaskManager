# app/celery_app.py
from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

celery_app = Celery("tms", broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app.conf.update(task_track_started=True, task_soft_time_limit=120)

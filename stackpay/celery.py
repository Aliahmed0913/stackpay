from celery import Celery
from celery.schedules import crontab
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stackpay.settings")

app = Celery("stackpay")

app.config_from_object("django.conf:settings", namespace="CELERY_")
app.conf.beat_schedule = {
    "remove-expiredcode-every-10m": {
        "task": "users.tasks.remove_expired_task",
        "schedule": crontab(minute="*/10"),
        "options": {"queue": "expired"},
    },
}
app.autodiscover_tasks()

app.conf.update(
    CELERY_ALWAYS_EAGER=True,
)

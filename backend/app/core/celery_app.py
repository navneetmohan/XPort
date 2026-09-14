from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery = Celery(
    "xport",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.core.tasks"],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# Configure Celery Beat schedule (Default: Monday-Friday post-market 12:00 UTC / 17:30 IST)
cron_parts = settings.MARKET_DATA_SYNC_CRON.split()
if len(cron_parts) == 5:
    minute_val, hour_val, dom_val, moy_val, dow_val = cron_parts
else:
    minute_val, hour_val, dom_val, moy_val, dow_val = "0", "12", "*", "*", "1-5"

celery.conf.beat_schedule = {
    "daily-market-data-sync": {
        "task": "app.core.tasks.sync_market_data_task",
        "schedule": crontab(
            minute=minute_val,
            hour=hour_val,
            day_of_month=dom_val,
            month_of_year=moy_val,
            day_of_week=dow_val,
        ),
        "kwargs": {
            "symbols": settings.MARKET_DATA_DEFAULT_SYMBOLS,
            "lookback_days": settings.MARKET_DATA_DEFAULT_LOOKBACK_DAYS,
        },
        "options": {"expires": 3600},
    },
}

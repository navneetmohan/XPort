from typing import Dict, Any
from app.core.celery_app import celery


@celery.task(name="app.core.tasks.health_check_task")
def health_check_task() -> Dict[str, Any]:
    """
    Foundation verification task.
    Verifies communication path: FastAPI -> Celery -> Redis.
    """
    return {
        "status": "ok",
        "task": "health_check_task",
        "message": "Celery worker is operational and communicating via Redis",
    }

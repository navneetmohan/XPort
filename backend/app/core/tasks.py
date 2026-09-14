import datetime
import logging
from typing import Any, Dict, List, Optional
from app.core.celery_app import celery
from app.db.session import SessionLocal
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)


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


@celery.task(name="app.core.tasks.sync_market_data_task", bind=True)
def sync_market_data_task(
    self,
    symbols: Optional[List[str]] = None,
    lookback_days: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Celery background task for Market Data synchronization.
    Safely creates its own DB session per execution.
    """
    logger.info(f"Executing sync_market_data_task with symbols: {symbols}")
    db = SessionLocal()
    try:
        parsed_start = datetime.date.fromisoformat(start_date) if start_date else None
        parsed_end = datetime.date.fromisoformat(end_date) if end_date else None

        service = MarketDataService(db)
        result = service.sync_market_data(
            symbols=symbols,
            lookback_days=lookback_days,
            start_date=parsed_start,
            end_date=parsed_end,
        )
        return result
    except Exception as exc:
        logger.error(f"Error executing sync_market_data_task: {exc}", exc_info=True)
        return {
            "status": "error",
            "error": str(exc),
            "symbols_requested": symbols or [],
        }
    finally:
        db.close()

import datetime
import logging
from typing import Any, Dict, List, Optional
from app.core.celery_app import celery
from app.db.session import SessionLocal
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.market_data_service import MarketDataService
try:
    from app.services.portfolio_optimizer import PortfolioOptimizer
except ImportError:
    PortfolioOptimizer = None

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


@celery.task(name="app.core.tasks.refresh_market_data_task", bind=True)
def refresh_market_data_task(
    self,
    symbols: Optional[List[str]] = None,
    lookback_days: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Coherent pipeline background task:
    Celery Beat / Manual Trigger -> refresh_market_data -> fetch -> preprocess -> features -> PostgreSQL.
    """
    logger.info(f"Executing refresh_market_data_task with symbols: {symbols}")
    db = SessionLocal()
    pipeline_start = datetime.datetime.now(datetime.timezone.utc)
    try:
        parsed_start = datetime.date.fromisoformat(start_date) if start_date else None
        parsed_end = datetime.date.fromisoformat(end_date) if end_date else None

        # 1 & 2. Fetch, preprocess, and persist raw market data
        md_service = MarketDataService(db)
        sync_result = md_service.sync_market_data(
            symbols=symbols,
            lookback_days=lookback_days,
            start_date=parsed_start,
            end_date=parsed_end,
        )

        # 3 & 4. Compute and persist engineered features
        fe_summary = {"status": "skipped", "total_upserted": 0, "symbols_processed": []}
        try:
            fe_service = FeatureEngineeringService(db)
            processed_symbols = sync_result.get("symbols_processed", [])
            target_fe_symbols = processed_symbols if processed_symbols else symbols
            fe_summary = fe_service.generate_features_for_all(symbols=target_fe_symbols)
        except Exception as fe_exc:
            logger.warning(f"Feature calculation notice during refresh pipeline: {fe_exc}")
            fe_summary = {"status": "notice", "error": str(fe_exc)}

        pipeline_duration = (datetime.datetime.now(datetime.timezone.utc) - pipeline_start).total_seconds()

        # Top-level keys include both market data sync summary and features
        sync_result["features"] = fe_summary
        sync_result["pipeline_duration_seconds"] = round(pipeline_duration, 2)
        sync_result["status"] = "success" if not sync_result.get("failures") else "completed_with_warnings"
        return sync_result
    except Exception as exc:
        logger.error(f"Fatal error executing refresh_market_data_task: {exc}", exc_info=True)
        return {
            "status": "error",
            "error": str(exc),
            "rows_fetched": 0,
            "rows_inserted_updated": 0,
            "failures": [{"symbol": "ALL", "reason": str(exc)}],
            "symbols_requested": symbols or [],
            "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    finally:
        try:
            db.close()
        except Exception:
            pass


# Backward-compatible Celery task alias
@celery.task(name="app.core.tasks.sync_market_data_task", bind=True)
def sync_market_data_task(
    self,
    symbols: Optional[List[str]] = None,
    lookback_days: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Alias for refresh_market_data_task for backward compatibility."""
    return refresh_market_data_task(
        symbols=symbols,
        lookback_days=lookback_days,
        start_date=start_date,
        end_date=end_date,
    )


# Function aliases for direct task dispatching
refresh_market_data = refresh_market_data_task
sync_market_data = sync_market_data_task


@celery.task(name="app.core.tasks.calculate_features_task")
def calculate_features_task(symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Celery task to compute technical indicators and feature engineering records.
    """
    logger.info(f"Executing calculate_features_task with symbols: {symbols}")
    db = SessionLocal()
    try:
        service = FeatureEngineeringService(db)
        return service.generate_features_for_all(symbols=symbols)
    except Exception as exc:
        logger.error(f"Error executing calculate_features_task: {exc}", exc_info=True)
        return {"status": "error", "error": str(exc)}
    finally:
        db.close()


@celery.task(name="app.core.tasks.run_portfolio_optimization_task", bind=True)
def run_portfolio_optimization_task(
    self,
    symbols: Optional[List[str]] = None,
    pop_size: int = 50,
    generations: int = 50,
    recommendation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Celery background task for NSGA-II Multi-Objective Portfolio Optimization.
    Executes optimization and persists Pareto portfolio results in PostgreSQL.
    """
    task_id = self.request.id if hasattr(self, "request") and self.request else None
    logger.info(f"Executing run_portfolio_optimization_task: symbols={symbols}, task_id={task_id}")
    db = SessionLocal()
    rec_repo = RecommendationRepository(db)

    # Ensure recommendation record exists
    if recommendation_id:
        existing = rec_repo.get_by_id_or_task_id(recommendation_id)
        if not existing:
            rec_repo.create_recommendation(
                symbols={"symbols": symbols or []},
                task_id=task_id,
                recommendation_id=recommendation_id,
            )
        rec_repo.update_recommendation(recommendation_id, status="RUNNING")

    try:
        # First ensure features are generated for symbols if needed
        fe_service = FeatureEngineeringService(db)
        fe_service.generate_features_for_all(symbols=symbols)

        # Run NSGA-II Optimization
        global PortfolioOptimizer
        if PortfolioOptimizer is None:
            from app.services.portfolio_optimizer import PortfolioOptimizer
        optimizer = PortfolioOptimizer(db)
        result = optimizer.optimize(
            symbols=symbols or ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"],
            pop_size=pop_size,
            generations=generations,
        )

        result["task_id"] = task_id
        result["recommendation_id"] = recommendation_id

        if recommendation_id:
            rec_repo.update_recommendation(recommendation_id, status="COMPLETED", result_data=result)

        return result
    except Exception as exc:
        logger.error(f"Error executing run_portfolio_optimization_task: {exc}", exc_info=True)
        err_res = {"status": "FAILED", "error": str(exc), "task_id": task_id}
        if recommendation_id:
            rec_repo.update_recommendation(recommendation_id, status="FAILED", result_data=err_res)
        return err_res
    finally:
        db.close()

import datetime
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.tasks import sync_market_data_task
from app.db.session import get_db
from app.repositories.market_data_repository import MarketDataRepository
from app.schemas.market_data import (
    MarketDataPaginatedResponse,
    MarketDataSyncRequest,
    MarketDataSyncResponse,
    SymbolCoverageListResponse,
    SymbolCoverageRead,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=MarketDataPaginatedResponse,
    summary="Query Historical Market Data",
    description="Retrieve paginated historical OHLCV records filtered by symbol and date range.",
)
def query_market_data(
    symbol: Optional[str] = Query(None, description="Filter by instrument symbol (e.g., RELIANCE.NS)"),
    start_date: Optional[datetime.date] = Query(None, description="Filter start date (inclusive, YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="Filter end date (inclusive, YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(100, ge=1, le=1000, description="Records per page"),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    repo = MarketDataRepository(db)
    records, total_count = repo.get_market_data(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=page_size,
    )

    return MarketDataPaginatedResponse(
        total=total_count,
        page=page,
        page_size=page_size,
        data=records,
    )


@router.get(
    "/symbols",
    response_model=SymbolCoverageListResponse,
    summary="List Instrument Symbol Coverage",
    description="Retrieve available instrument symbols along with date range coverage and record counts.",
)
def get_symbol_coverage(
    db: Session = Depends(get_db),
):
    repo = MarketDataRepository(db)
    coverage = repo.get_symbol_coverage()
    items = [SymbolCoverageRead(**c) for c in coverage]
    return SymbolCoverageListResponse(total_symbols=len(items), symbols=items)


@router.post(
    "/sync",
    response_model=MarketDataSyncResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Market Data Sync",
    description="Asynchronously trigger market data acquisition and persistence via Celery.",
)
def trigger_market_data_sync(
    request: Optional[MarketDataSyncRequest] = None,
):
    req = request or MarketDataSyncRequest()
    symbols = req.symbols or settings.MARKET_DATA_DEFAULT_SYMBOLS
    lookback = req.lookback_days or settings.MARKET_DATA_DEFAULT_LOOKBACK_DAYS

    start_str = req.start_date.isoformat() if req.start_date else None
    end_str = req.end_date.isoformat() if req.end_date else None

    try:
        task = sync_market_data_task.delay(
            symbols=symbols,
            lookback_days=lookback,
            start_date=start_str,
            end_date=end_str,
        )
        task_id = task.id
    except Exception as exc:
        logger.error(f"Failed to dispatch Celery sync task: {exc}", exc_info=True)
        # Fallback pseudo task ID if Celery broker is unavailable during sync request
        task_id = "task-sync-failed-dispatch"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch synchronization task: {str(exc)}",
        )

    return MarketDataSyncResponse(
        task_id=task_id,
        status="PENDING",
        message="Market data synchronization task successfully queued.",
        symbols_requested=symbols if isinstance(symbols, list) else [symbols],
    )

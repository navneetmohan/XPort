import datetime
import logging
from typing import Any, Dict, Optional
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.celery_app import celery
from app.core.config import settings
from app.core.instruments import get_all_asset_classes, get_all_instruments
from app.core.tasks import refresh_market_data_task, sync_market_data_task
from app.db.session import get_db
from app.repositories.market_data_repository import MarketDataRepository
from app.schemas.market_data import (
    MarketDataPaginatedResponse,
    MarketDataRead,
    MarketDataRefreshRequest,
    MarketDataRefreshResponse,
    MarketDataSyncRequest,
    MarketDataSyncResponse,
    PipelineStatusResponse,
    PipelineTaskStatusResponse,
    SymbolCoverageListResponse,
    SymbolCoverageRead,
)
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=MarketDataPaginatedResponse,
    summary="Query Historical Market Data",
    description="Retrieve paginated historical OHLCV records filtered by optional symbol and date range.",
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
    "/status",
    response_model=PipelineStatusResponse,
    summary="Get Pipeline & Market Data Status",
    description="Returns system-wide operational health, coverage, and feature status across all universe instruments.",
)
def get_pipeline_status(
    db: Session = Depends(get_db),
):
    service = MarketDataService(db)
    status_data = service.get_data_status()
    return PipelineStatusResponse(**status_data)


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


@router.get(
    "/instruments",
    summary="List Curated Instrument Universe",
    description="Returns the curated multi-asset instrument universe categorized by conceptual asset classes.",
)
def get_instruments():
    return {
        "asset_classes": get_all_asset_classes(),
        "instruments": get_all_instruments(),
    }


@router.post(
    "/refresh",
    response_model=MarketDataRefreshResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Market Data & Feature Pipeline Refresh",
    description="Asynchronously triggers the end-to-end data acquisition, preprocessing, and feature engineering pipeline via Celery.",
)
def trigger_market_data_refresh(
    request: Optional[MarketDataRefreshRequest] = None,
):
    req = request or MarketDataRefreshRequest()
    symbols = req.symbols or settings.MARKET_DATA_DEFAULT_SYMBOLS
    lookback = req.lookback_days or settings.MARKET_DATA_DEFAULT_LOOKBACK_DAYS

    start_str = req.start_date.isoformat() if req.start_date else None
    end_str = req.end_date.isoformat() if req.end_date else None

    try:
        task = refresh_market_data_task.delay(
            symbols=symbols,
            lookback_days=lookback,
            start_date=start_str,
            end_date=end_str,
        )
        task_id = task.id
    except Exception as exc:
        logger.error(f"Failed to dispatch Celery refresh task: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch refresh task: {str(exc)}",
        )

    return MarketDataRefreshResponse(
        task_id=task_id,
        status="PENDING",
        message="Market data and feature pipeline refresh task successfully queued.",
        symbols_requested=symbols if isinstance(symbols, list) else [symbols],
    )


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


@router.get(
    "/task/{task_id}",
    response_model=PipelineTaskStatusResponse,
    summary="Query Asynchronous Pipeline Task Status",
    description="Query Celery task execution status, completion, and returned pipeline summary.",
)
def get_task_status(task_id: str):
    try:
        async_result = AsyncResult(task_id, app=celery)
        task_status = async_result.status
        is_ready = async_result.ready()
        is_success = async_result.successful() if is_ready else None

        result_data = None
        error_msg = None

        if is_ready:
            if is_success:
                raw_res = async_result.result
                result_data = raw_res if isinstance(raw_res, dict) else {"result": str(raw_res)}
            else:
                error_msg = str(async_result.result)

        return PipelineTaskStatusResponse(
            task_id=task_id,
            status=task_status,
            ready=is_ready,
            successful=is_success,
            result=result_data,
            error=error_msg,
        )
    except Exception as exc:
        logger.error(f"Error checking task {task_id}: {exc}", exc_info=True)
        return PipelineTaskStatusResponse(
            task_id=task_id,
            status="UNKNOWN",
            ready=False,
            error=str(exc),
        )


@router.get(
    "/{symbol}",
    response_model=MarketDataPaginatedResponse,
    summary="Get Historical Market Data for a Specific Symbol",
    description="Retrieve recent historical OHLCV data for an instrument by symbol.",
)
def get_symbol_market_data(
    symbol: str,
    start_date: Optional[datetime.date] = Query(None, description="Filter start date (inclusive, YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="Filter end date (inclusive, YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(100, ge=1, le=1000, description="Records per page"),
    db: Session = Depends(get_db),
):
    clean_symbol = symbol.strip().upper()
    skip = (page - 1) * page_size
    repo = MarketDataRepository(db)

    records, total_count = repo.get_market_data(
        symbol=clean_symbol,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=page_size,
    )

    if total_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No market data records found for symbol '{clean_symbol}'.",
        )

    return MarketDataPaginatedResponse(
        total=total_count,
        page=page,
        page_size=page_size,
        data=records,
    )

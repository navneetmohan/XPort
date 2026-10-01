import datetime
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.engineered_features_repository import EngineeredFeaturesRepository
from app.schemas.market_data import (
    EngineeredFeaturesPaginatedResponse,
    EngineeredFeaturesRead,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{symbol}",
    response_model=EngineeredFeaturesPaginatedResponse,
    summary="Get Engineered Features for a Symbol",
    description="Retrieve calculated technical indicators (SMA, EMA, RSI, MACD, returns, volatility) for a financial instrument.",
)
def get_symbol_features(
    symbol: str,
    start_date: Optional[datetime.date] = Query(None, description="Filter start date (inclusive, YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="Filter end date (inclusive, YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(100, ge=1, le=1000, description="Records per page"),
    db: Session = Depends(get_db),
):
    clean_symbol = symbol.strip().upper()
    skip = (page - 1) * page_size
    repo = EngineeredFeaturesRepository(db)

    features = repo.get_features(
        symbol=clean_symbol,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=page_size,
    )
    total_count = repo.get_features_count(symbol=clean_symbol)

    if total_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No engineered features found for symbol '{clean_symbol}'. Please run market data sync/refresh first.",
        )

    return EngineeredFeaturesPaginatedResponse(
        symbol=clean_symbol,
        total=total_count,
        page=page,
        page_size=page_size,
        data=features,
    )


@router.get(
    "",
    summary="Query Engineered Features Across Universe",
    description="Retrieve calculated technical indicators with optional symbol and date filtering.",
)
def query_features(
    symbol: Optional[str] = Query(None, description="Filter by instrument symbol"),
    start_date: Optional[datetime.date] = Query(None, description="Filter start date"),
    end_date: Optional[datetime.date] = Query(None, description="Filter end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Records per page"),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    repo = EngineeredFeaturesRepository(db)

    features = repo.get_features(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=page_size,
    )
    total_count = repo.get_features_count(symbol=symbol)

    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "data": features,
    }

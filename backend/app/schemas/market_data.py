import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MarketDataRead(BaseModel):
    """Schema representing an individual historical OHLCV market data record."""

    id: int
    symbol: str
    date: datetime.date
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    adj_close: Optional[float] = None
    volume: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MarketDataPaginatedResponse(BaseModel):
    """Paginated response wrapper for market data records query."""

    total: int = Field(..., description="Total records matching filter criteria")
    page: int = Field(1, description="Current page number (1-indexed)")
    page_size: int = Field(100, description="Number of items per page")
    data: List[MarketDataRead] = Field(..., description="List of market data records")


class SymbolCoverageRead(BaseModel):
    """Coverage and dataset statistics for a financial instrument."""

    symbol: str
    earliest_date: Optional[datetime.date] = None
    latest_date: Optional[datetime.date] = None
    record_count: int = 0


class SymbolCoverageListResponse(BaseModel):
    """List response for available symbols and coverage metadata."""

    total_symbols: int
    symbols: List[SymbolCoverageRead]


class MarketDataSyncRequest(BaseModel):
    """Request payload for manual market data synchronization."""

    symbols: Optional[List[str]] = Field(
        default=None,
        description="List of ticker symbols to sync. Uses defaults if omitted.",
        json_schema_extra={"example": ["RELIANCE.NS", "TCS.NS"]},
    )
    lookback_days: Optional[int] = Field(
        default=None,
        description="Historical lookback window in days.",
        json_schema_extra={"example": 365},
    )
    start_date: Optional[datetime.date] = Field(
        default=None,
        description="Start date for sync range (YYYY-MM-DD).",
    )
    end_date: Optional[datetime.date] = Field(
        default=None,
        description="End date for sync range (YYYY-MM-DD).",
    )


class MarketDataSyncResponse(BaseModel):
    """Response returned upon dispatching an asynchronous synchronization task."""

    task_id: str = Field(..., description="Celery task identifier")
    status: str = Field("PENDING", description="Task dispatch status")
    message: str = Field(..., description="Description of the sync trigger")
    symbols_requested: List[str] = Field(..., description="List of symbols targeted for sync")


class MarketDataSyncSummary(BaseModel):
    """Detailed summary of synchronization execution result."""

    symbols_requested: List[str]
    symbols_processed: List[str]
    rows_fetched: int
    rows_inserted_updated: int
    rows_rejected: int
    failures: List[Dict[str, Any]]
    sync_timestamp: str

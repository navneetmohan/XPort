import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MarketDataRead(BaseModel):
    """Schema representing an individual historical OHLCV market data record."""

    id: int
    symbol: str
    asset_class: Optional[str] = None
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
    asset_class: Optional[str] = None
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


MarketDataRefreshRequest = MarketDataSyncRequest


class MarketDataSyncResponse(BaseModel):
    """Response returned upon dispatching an asynchronous synchronization task."""

    task_id: str = Field(..., description="Celery task identifier")
    status: str = Field("PENDING", description="Task dispatch status")
    message: str = Field(..., description="Description of the sync trigger")
    symbols_requested: List[str] = Field(..., description="List of symbols targeted for sync")


MarketDataRefreshResponse = MarketDataSyncResponse


class MarketDataSyncSummary(BaseModel):
    """Detailed summary of synchronization execution result."""

    symbols_requested: List[str]
    symbols_processed: List[str]
    rows_fetched: int
    rows_inserted_updated: int
    rows_rejected: int
    duplicates_detected: Optional[int] = 0
    missing_values_detected: Optional[int] = 0
    failures: List[Dict[str, Any]]
    sync_timestamp: str


class EngineeredFeaturesRead(BaseModel):
    """Schema representing persisted technical indicators and features."""

    id: int
    symbol: str
    date: datetime.date
    market_data_id: Optional[int] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    daily_return: Optional[float] = None
    rolling_volatility: Optional[float] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EngineeredFeaturesPaginatedResponse(BaseModel):
    """Paginated response wrapper for engineered features query."""

    symbol: str = Field(..., description="Instrument symbol")
    total: int = Field(..., description="Total records matching filter criteria")
    page: int = Field(1, description="Current page number (1-indexed)")
    page_size: int = Field(100, description="Number of items per page")
    data: List[EngineeredFeaturesRead] = Field(..., description="List of engineered features")


class PipelineInstrumentStatus(BaseModel):
    """Pipeline and feature availability status for a single instrument."""

    symbol: str
    name: str
    asset_class: str
    is_yahoo_supported: bool
    market_data_records: int = 0
    market_earliest_date: Optional[datetime.date] = None
    market_latest_date: Optional[datetime.date] = None
    features_records: int = 0
    features_earliest_date: Optional[datetime.date] = None
    features_latest_date: Optional[datetime.date] = None
    has_market_data: bool = False
    has_features: bool = False


class PipelineStatusResponse(BaseModel):
    """System-wide market data and feature pipeline status."""

    status: str = "operational"
    total_universe_instruments: int
    instruments_with_market_data: int
    instruments_with_features: int
    total_market_records: int
    total_feature_records: int
    instruments: List[PipelineInstrumentStatus]
    timestamp: str


class PipelineTaskStatusResponse(BaseModel):
    """Asynchronous background task status schema."""

    task_id: str
    status: str
    ready: bool
    successful: Optional[bool] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

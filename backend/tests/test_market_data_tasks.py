import datetime
from unittest.mock import MagicMock, patch
import pytest

from app.core.tasks import sync_market_data_task
from app.services.market_data_service import MarketDataService


@patch.object(MarketDataService, "sync_market_data")
def test_sync_market_data_task_success(mock_sync):
    mock_sync.return_value = {
        "symbols_requested": ["NIFTYBEES.NS"],
        "symbols_processed": ["NIFTYBEES.NS"],
        "rows_fetched": 10,
        "rows_inserted_updated": 10,
        "rows_rejected": 0,
        "failures": [],
        "sync_timestamp": "2026-09-14T20:00:00+00:00",
    }

    result = sync_market_data_task(symbols=["NIFTYBEES.NS"], lookback_days=10)

    assert result["rows_fetched"] == 10
    assert result["rows_inserted_updated"] == 10
    assert result["failures"] == []
    mock_sync.assert_called_once()


@patch.object(MarketDataService, "sync_market_data")
def test_sync_market_data_task_failure_handling(mock_sync):
    mock_sync.side_effect = RuntimeError("Database connection timeout")

    result = sync_market_data_task(symbols=["INFY.NS"])

    assert result["status"] == "error"
    assert "Database connection timeout" in result["error"]
    assert result["symbols_requested"] == ["INFY.NS"]

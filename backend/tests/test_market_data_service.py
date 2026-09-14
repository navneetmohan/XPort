import datetime
from unittest.mock import MagicMock
import pandas as pd
import pytest

from app.services.market_data_service import MarketDataService
from app.services.yahoo_finance_service import YahooFinanceService


def test_yahoo_finance_service_normalize_dataframe():
    service = YahooFinanceService()
    dates = pd.date_range("2026-01-01", periods=3)
    df = pd.DataFrame(
        {
            "Open": [100.0, 102.0, 104.0],
            "High": [105.0, 106.0, 108.0],
            "Low": [99.0, 101.0, 103.0],
            "Close": [104.0, 105.0, 107.0],
            "Adj Close": [104.0, 105.0, 107.0],
            "Volume": [10000, 12000, 15000],
        },
        index=dates,
    )

    records = service.normalize_dataframe(df, "RELIANCE.NS")
    assert len(records) == 3
    assert records[0]["symbol"] == "RELIANCE.NS"
    assert records[0]["date"] == datetime.date(2026, 1, 1)
    assert records[0]["open"] == 100.0
    assert records[0]["high"] == 105.0
    assert records[0]["low"] == 99.0
    assert records[0]["close"] == 104.0
    assert records[0]["volume"] == 10000


def test_yahoo_finance_service_empty_df():
    service = YahooFinanceService()
    empty_df = pd.DataFrame()
    records = service.normalize_dataframe(empty_df, "TCS.NS")
    assert records == []


def test_market_data_service_validation_rules(db_session):
    service = MarketDataService(db_session)

    # 1. Valid record
    valid_rec = {
        "symbol": "INFY.NS",
        "date": datetime.date(2026, 1, 15),
        "open": 1500.0,
        "high": 1550.0,
        "low": 1490.0,
        "close": 1530.0,
        "adj_close": 1530.0,
        "volume": 500000,
    }
    is_valid, reason = service.validate_record(valid_rec)
    assert is_valid is True
    assert reason == ""

    # 2. Negative price
    invalid_price = dict(valid_rec, open=-100.0)
    is_valid, reason = service.validate_record(invalid_price)
    assert is_valid is False
    assert "positive number" in reason

    # 3. High lower than Low
    invalid_hl = dict(valid_rec, high=1400.0, low=1500.0)
    is_valid, reason = service.validate_record(invalid_hl)
    assert is_valid is False
    assert "lower than Low" in reason

    # 4. Open outside High/Low
    invalid_open = dict(valid_rec, open=1600.0, high=1550.0)
    is_valid, reason = service.validate_record(invalid_open)
    assert is_valid is False
    assert "outside High" in reason

    # 5. Negative volume
    invalid_vol = dict(valid_rec, volume=-50)
    is_valid, reason = service.validate_record(invalid_vol)
    assert is_valid is False
    assert "non-negative integer" in reason


def test_market_data_service_sync_orchestration(db_session):
    mock_yf = MagicMock(spec=YahooFinanceService)
    mock_yf.fetch_historical_ohlcv.return_value = [
        {
            "symbol": "HDFCBANK.NS",
            "date": datetime.date(2026, 2, 1),
            "open": 1600.0,
            "high": 1620.0,
            "low": 1590.0,
            "close": 1610.0,
            "adj_close": 1610.0,
            "volume": 200000,
        },
        {
            # Invalid record
            "symbol": "HDFCBANK.NS",
            "date": datetime.date(2026, 2, 2),
            "open": -10.0,
            "high": 1620.0,
            "low": 1590.0,
            "close": 1610.0,
            "adj_close": 1610.0,
            "volume": 200000,
        },
    ]

    service = MarketDataService(db_session, yf_service=mock_yf)
    summary = service.sync_market_data(symbols=["HDFCBANK.NS"], lookback_days=10)

    assert summary["rows_fetched"] == 2
    assert summary["rows_inserted_updated"] == 1
    assert summary["rows_rejected"] == 1
    assert "HDFCBANK.NS" in summary["symbols_processed"]

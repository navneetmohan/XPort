import datetime
from unittest.mock import patch
import pytest
from app.models.engineered_features import EngineeredFeatures
from app.models.market_data import MarketData


def test_get_symbol_market_data_endpoint(client, db_session):
    """Verify GET /api/v1/market-data/{symbol} returns data and 404 for missing symbol."""
    # Seed single record
    rec = MarketData(
        symbol="TCS.NS",
        asset_class="stocks",
        date=datetime.date(2026, 3, 1),
        open=3500.0,
        high=3550.0,
        low=3480.0,
        close=3520.0,
        adj_close=3520.0,
        volume=120000,
    )
    db_session.add(rec)
    db_session.commit()

    # Existing symbol
    res_ok = client.get("/api/v1/market-data/TCS.NS")
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["total"] == 1
    assert data["data"][0]["symbol"] == "TCS.NS"
    assert data["data"][0]["close"] == 3520.0
    assert data["data"][0]["asset_class"] == "stocks"

    # Non-existing symbol
    res_missing = client.get("/api/v1/market-data/UNKNOWN.NS")
    assert res_missing.status_code == 404
    assert "No market data records found" in res_missing.json()["detail"]


def test_get_symbol_features_endpoint(client, db_session):
    """Verify GET /api/v1/features/{symbol} returns engineered indicators and 404 for missing."""
    rec = EngineeredFeatures(
        symbol="INFY.NS",
        date=datetime.date(2026, 3, 1),
        sma_20=1600.0,
        sma_50=1580.0,
        ema_20=1605.0,
        ema_50=1590.0,
        rsi_14=62.5,
        macd=5.2,
        macd_signal=4.8,
        macd_histogram=0.4,
        daily_return=0.008,
        rolling_volatility=0.014,
    )
    db_session.add(rec)
    db_session.commit()

    # Existing symbol features
    res_ok = client.get("/api/v1/features/INFY.NS")
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["symbol"] == "INFY.NS"
    assert data["total"] == 1
    assert data["data"][0]["rsi_14"] == 62.5
    assert data["data"][0]["ema_50"] == 1590.0

    # Non-existing symbol features
    res_missing = client.get("/api/v1/features/NOT_SYNCED.NS")
    assert res_missing.status_code == 404
    assert "No engineered features found" in res_missing.json()["detail"]


def test_get_pipeline_status_endpoint(client, db_session):
    """Verify GET /api/v1/market-data/status returns operational summary across universe."""
    res = client.get("/api/v1/market-data/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert "total_universe_instruments" in data
    assert "instruments" in data
    assert len(data["instruments"]) > 0
    # Spot-check asset classes in instruments
    asset_classes = {i["asset_class"] for i in data["instruments"]}
    assert "stocks" in asset_classes


def test_get_instruments_universe_endpoint(client):
    """Verify GET /api/v1/market-data/instruments returns categorized instrument universe."""
    res = client.get("/api/v1/market-data/instruments")
    assert res.status_code == 200
    data = res.json()
    assert "asset_classes" in data
    assert "instruments" in data
    symbols = [inst["symbol"] for inst in data["instruments"]]
    assert "RELIANCE.NS" in symbols
    assert "GOLDBEES.NS" in symbols


@patch("app.api.v1.endpoints.market_data.refresh_market_data_task.delay")
def test_post_market_data_refresh_endpoint(mock_task, client):
    """Verify POST /api/v1/market-data/refresh triggers background Celery pipeline."""
    mock_task.return_value.id = "refresh-task-uuid-456"

    payload = {"symbols": ["RELIANCE.NS"], "lookback_days": 60}
    res = client.post("/api/v1/market-data/refresh", json=payload)

    assert res.status_code == 202
    data = res.json()
    assert data["task_id"] == "refresh-task-uuid-456"
    assert data["status"] == "PENDING"
    mock_task.assert_called_once()


def test_get_task_status_endpoint(client):
    """Verify GET /api/v1/market-data/task/{task_id} returns task status schema."""
    res = client.get("/api/v1/market-data/task/mock-task-789")
    assert res.status_code == 200
    data = res.json()
    assert data["task_id"] == "mock-task-789"
    assert "status" in data
    assert "ready" in data

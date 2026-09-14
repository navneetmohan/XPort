import datetime
from unittest.mock import patch
import pytest

from app.models.market_data import MarketData


def test_get_market_data_empty(client):
    response = client.get("/api/v1/market-data")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total"] == 0
    assert json_data["page"] == 1
    assert json_data["data"] == []


def test_get_market_data_with_records(client, db_session):
    rec = MarketData(
        symbol="ICICIBANK.NS",
        date=datetime.date(2026, 1, 10),
        open=1000.0,
        high=1020.0,
        low=990.0,
        close=1015.0,
        adj_close=1015.0,
        volume=300000,
    )
    db_session.add(rec)
    db_session.commit()

    response = client.get("/api/v1/market-data?symbol=ICICIBANK.NS")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total"] == 1
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["symbol"] == "ICICIBANK.NS"
    assert json_data["data"][0]["close"] == 1015.0


def test_get_symbol_coverage_api(client, db_session):
    rec = MarketData(
        symbol="GOLDBEES.NS",
        date=datetime.date(2026, 1, 10),
        open=50.0,
        high=52.0,
        low=49.5,
        close=51.5,
        adj_close=51.5,
        volume=50000,
    )
    db_session.add(rec)
    db_session.commit()

    response = client.get("/api/v1/market-data/symbols")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total_symbols"] == 1
    assert json_data["symbols"][0]["symbol"] == "GOLDBEES.NS"
    assert json_data["symbols"][0]["record_count"] == 1


@patch("app.api.v1.endpoints.market_data.sync_market_data_task.delay")
def test_post_market_data_sync_api(mock_task, client):
    mock_task.return_value.id = "test-task-id-12345"

    payload = {
        "symbols": ["RELIANCE.NS", "TCS.NS"],
        "lookback_days": 30,
    }

    response = client.post("/api/v1/market-data/sync", json=payload)
    assert response.status_code == 202
    json_data = response.json()
    assert json_data["task_id"] == "test-task-id-12345"
    assert json_data["status"] == "PENDING"
    assert json_data["symbols_requested"] == ["RELIANCE.NS", "TCS.NS"]
    mock_task.assert_called_once()

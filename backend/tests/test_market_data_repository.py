import datetime
import pytest

from app.models.market_data import MarketData
from app.repositories.market_data_repository import MarketDataRepository


def test_repository_upsert_and_duplicates(db_session):
    repo = MarketDataRepository(db_session)

    records = [
        {
            "symbol": "TCS.NS",
            "date": datetime.date(2026, 1, 10),
            "open": 3800.0,
            "high": 3850.0,
            "low": 3780.0,
            "close": 3820.0,
            "adj_close": 3820.0,
            "volume": 150000,
        },
        {
            "symbol": "TCS.NS",
            "date": datetime.date(2026, 1, 11),
            "open": 3820.0,
            "high": 3880.0,
            "low": 3810.0,
            "close": 3870.0,
            "adj_close": 3870.0,
            "volume": 180000,
        },
    ]

    inserted, total = repo.upsert_records(records)
    assert inserted == 2
    assert total == 2

    # Verify query
    fetched, count = repo.get_market_data(symbol="TCS.NS")
    assert count == 2
    assert fetched[0].close == 3820.0

    # Upsert updated record for 2026-01-10
    updated_records = [
        {
            "symbol": "TCS.NS",
            "date": datetime.date(2026, 1, 10),
            "open": 3800.0,
            "high": 3850.0,
            "low": 3780.0,
            "close": 3830.0,  # Updated close price
            "adj_close": 3830.0,
            "volume": 160000,
        }
    ]

    repo.upsert_records(updated_records)

    # Total count should still be 2 (no duplicate row created)
    fetched_after, count_after = repo.get_market_data(symbol="TCS.NS")
    assert count_after == 2

    record_jan10 = [r for r in fetched_after if r.date == datetime.date(2026, 1, 10)][0]
    assert record_jan10.close == 3830.0


def test_repository_filtering_and_coverage(db_session):
    repo = MarketDataRepository(db_session)

    records = [
        {
            "symbol": "RELIANCE.NS",
            "date": datetime.date(2026, 1, 1),
            "open": 2400.0,
            "high": 2450.0,
            "low": 2390.0,
            "close": 2430.0,
            "adj_close": 2430.0,
            "volume": 100000,
        },
        {
            "symbol": "RELIANCE.NS",
            "date": datetime.date(2026, 1, 5),
            "open": 2430.0,
            "high": 2480.0,
            "low": 2420.0,
            "close": 2470.0,
            "adj_close": 2470.0,
            "volume": 120000,
        },
        {
            "symbol": "INFY.NS",
            "date": datetime.date(2026, 1, 2),
            "open": 1500.0,
            "high": 1520.0,
            "low": 1490.0,
            "close": 1510.0,
            "adj_close": 1510.0,
            "volume": 90000,
        },
    ]

    repo.upsert_records(records)

    # Test date filtering
    filtered, count = repo.get_market_data(
        symbol="RELIANCE.NS", start_date=datetime.date(2026, 1, 2)
    )
    assert count == 1
    assert filtered[0].date == datetime.date(2026, 1, 5)

    # Test coverage summary
    coverage = repo.get_symbol_coverage()
    assert len(coverage) == 2

    symbols_found = {c["symbol"]: c for c in coverage}
    assert "RELIANCE.NS" in symbols_found
    assert symbols_found["RELIANCE.NS"]["record_count"] == 2
    assert symbols_found["RELIANCE.NS"]["earliest_date"] == datetime.date(2026, 1, 1)
    assert symbols_found["RELIANCE.NS"]["latest_date"] == datetime.date(2026, 1, 5)

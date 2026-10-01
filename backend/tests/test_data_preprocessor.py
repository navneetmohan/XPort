import datetime
import pytest
from app.services.data_preprocessor import DataPreprocessor, DataQualityReport


def test_data_preprocessor_clean_and_sort():
    """Verify preprocessor sorts dates chronologically and normalizes OHLCV."""
    preprocessor = DataPreprocessor()
    raw = [
        {"date": "2026-01-05", "open": 100.0, "high": 105.0, "low": 99.0, "close": 104.0, "volume": 1000},
        {"date": "2026-01-02", "open": 98.0, "high": 101.0, "low": 97.0, "close": 100.0, "volume": 1200},
        {"date": "2026-01-01", "open": 95.0, "high": 99.0, "low": 94.0, "close": 98.0, "volume": 1500},
    ]

    clean_records, report = preprocessor.preprocess_symbol_data(raw, "RELIANCE.NS", "stocks")

    assert len(clean_records) == 3
    assert report.valid_records == 3
    assert report.records_fetched == 3
    assert report.duplicate_count == 0
    assert report.invalid_record_count == 0
    # Chronological sort order: 2026-01-01, 2026-01-02, 2026-01-05
    assert clean_records[0]["date"] == datetime.date(2026, 1, 1)
    assert clean_records[1]["date"] == datetime.date(2026, 1, 2)
    assert clean_records[2]["date"] == datetime.date(2026, 1, 5)
    assert clean_records[0]["asset_class"] == "stocks"


def test_data_preprocessor_duplicate_detection():
    """Verify duplicate date records are detected and deduplicated."""
    preprocessor = DataPreprocessor()
    raw = [
        {"date": "2026-01-02", "open": 98.0, "high": 101.0, "low": 97.0, "close": 100.0, "volume": 1000},
        {"date": "2026-01-02", "open": 99.0, "high": 102.0, "low": 98.0, "close": 101.0, "volume": 2000},
    ]

    clean_records, report = preprocessor.preprocess_symbol_data(raw, "TCS.NS")

    assert len(clean_records) == 1
    assert report.duplicate_count == 1
    assert clean_records[0]["close"] == 101.0  # Keeps the latest record
    assert clean_records[0]["volume"] == 2000


def test_data_preprocessor_missing_value_handling_and_rejection():
    """Verify missing price rules: reject missing/negative close, impute zero volume."""
    preprocessor = DataPreprocessor()
    raw = [
        # Valid record with missing volume -> imputed to 0
        {"date": "2026-01-01", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": None},
        # Missing close -> cannot be imputed, must be rejected
        {"date": "2026-01-02", "open": 100.0, "high": 105.0, "low": 95.0, "close": None, "volume": 1000},
        # Negative price -> invalid, must be rejected
        {"date": "2026-01-03", "open": 100.0, "high": 105.0, "low": -5.0, "close": 102.0, "volume": 1000},
        # Missing date -> must be rejected
        {"date": None, "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 1000},
    ]

    clean_records, report = preprocessor.preprocess_symbol_data(raw, "INFY.NS")

    assert len(clean_records) == 1
    assert clean_records[0]["date"] == datetime.date(2026, 1, 1)
    assert clean_records[0]["volume"] == 0
    assert report.valid_records == 1
    assert report.invalid_record_count == 3


def test_data_preprocessor_ohlc_consistency():
    """Verify OHLC relationship validation: High >= Low, Open/Close within [Low, High]."""
    preprocessor = DataPreprocessor()
    raw = [
        # Inverted High < Low
        {"date": "2026-01-01", "open": 100.0, "high": 90.0, "low": 95.0, "close": 92.0, "volume": 1000},
        # Close higher than High
        {"date": "2026-01-02", "open": 100.0, "high": 105.0, "low": 95.0, "close": 110.0, "volume": 1000},
        # Open lower than Low
        {"date": "2026-01-03", "open": 90.0, "high": 105.0, "low": 95.0, "close": 100.0, "volume": 1000},
        # Valid candle
        {"date": "2026-01-04", "open": 98.0, "high": 102.0, "low": 96.0, "close": 101.0, "volume": 1000},
    ]

    clean_records, report = preprocessor.preprocess_symbol_data(raw, "HDFCBANK.NS")

    assert len(clean_records) == 1
    assert clean_records[0]["date"] == datetime.date(2026, 1, 4)
    assert report.invalid_record_count == 3


def test_data_preprocessor_trading_gap_detection():
    """Verify extended calendar gaps are flagged in the data quality report."""
    preprocessor = DataPreprocessor()
    raw = [
        {"date": "2026-01-01", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 1000},
        # Gap of 15 days
        {"date": "2026-01-16", "open": 103.0, "high": 107.0, "low": 101.0, "close": 105.0, "volume": 1000},
    ]

    clean_records, report = preprocessor.preprocess_symbol_data(raw, "GOLDBEES.NS", "gold")

    assert len(clean_records) == 2
    assert len(report.gap_warnings) == 1
    assert "15 calendar days" in report.gap_warnings[0]

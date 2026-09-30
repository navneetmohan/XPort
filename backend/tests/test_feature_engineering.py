import datetime
import numpy as np
import pandas as pd
import pytest
from sqlalchemy.orm import Session
from app.models.engineered_features import EngineeredFeatures
from app.models.market_data import MarketData
from app.repositories.engineered_features_repository import EngineeredFeaturesRepository
from app.repositories.market_data_repository import MarketDataRepository
from app.services.feature_engineering_service import FeatureEngineeringService


def test_feature_engineering_indicator_calculations(db_session: Session):
    """Verify technical indicator mathematical calculations on synthetic data."""
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(60)]
    np.random.seed(42)
    base_price = 100.0
    prices = [base_price]
    for _ in range(59):
        prices.append(prices[-1] * (1.0 + np.random.normal(0.001, 0.015)))

    df_raw = pd.DataFrame({
        "symbol": "TEST.NS",
        "date": dates,
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": [10000] * 60,
    })

    service = FeatureEngineeringService(db_session)
    df_calc = service.calculate_indicators(df_raw)

    assert "sma_20" in df_calc.columns
    assert "sma_50" in df_calc.columns
    assert "ema_20" in df_calc.columns
    assert "rsi_14" in df_calc.columns
    assert "macd" in df_calc.columns
    assert "daily_return" in df_calc.columns
    assert "rolling_volatility" in df_calc.columns

    # Verify SMA 20 on line 20
    sma20_expected = np.mean(prices[0:20])
    assert abs(df_calc.loc[19, "sma_20"] - sma20_expected) < 1e-4

    # Verify valid records formatted
    valid_recs = service.validate_and_format_features(df_calc)
    assert len(valid_recs) > 0
    first_valid = valid_recs[0]
    assert first_valid["symbol"] == "TEST.NS"
    assert 0.0 <= first_valid["rsi_14"] <= 100.0
    assert np.isfinite(first_valid["daily_return"])
    assert np.isfinite(first_valid["rolling_volatility"])


def test_feature_engineering_validation_rules(db_session: Session):
    """Verify malformed indicator rows (NaNs, invalid RSI) are rejected."""
    service = FeatureEngineeringService(db_session)

    bad_df = pd.DataFrame([
        {
            "symbol": "BAD.NS",
            "date": datetime.date(2026, 1, 1),
            "close": -10.0, # Negative price
            "high": 5.0,
            "low": 10.0, # High < Low
            "sma_20": np.nan,
            "rsi_14": 150.0, # RSI out of bounds
            "daily_return": np.nan,
            "rolling_volatility": np.nan,
        }
    ])

    recs = service.validate_and_format_features(bad_df)
    assert len(recs) == 0


def test_engineered_features_repository_idempotent_upsert(db_session: Session):
    """Verify upsert operation avoids duplicate rows for same symbol & date."""
    repo = EngineeredFeaturesRepository(db_session)
    d = datetime.date(2026, 2, 1)

    recs = [
        {
            "symbol": "RELIANCE.NS",
            "date": d,
            "sma_20": 2500.0,
            "sma_50": 2450.0,
            "rsi_14": 55.5,
            "daily_return": 0.012,
            "rolling_volatility": 0.018,
        }
    ]

    upserted1, total1 = repo.upsert_records(recs)
    assert upserted1 == 1

    # Second run with updated RSI value
    recs_updated = [
        {
            "symbol": "RELIANCE.NS",
            "date": d,
            "sma_20": 2500.0,
            "sma_50": 2450.0,
            "rsi_14": 58.2,
            "daily_return": 0.012,
            "rolling_volatility": 0.018,
        }
    ]

    upserted2, total2 = repo.upsert_records(recs_updated)
    assert upserted2 == 1

    # Check database record count is 1
    features = repo.get_features(symbol="RELIANCE.NS")
    assert len(features) == 1
    assert float(features[0].rsi_14) == 58.2

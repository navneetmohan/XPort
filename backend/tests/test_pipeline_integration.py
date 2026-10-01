import datetime
from unittest.mock import patch
import pandas as pd
import pytest
from app.repositories.engineered_features_repository import EngineeredFeaturesRepository
from app.repositories.market_data_repository import MarketDataRepository
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.market_data_service import MarketDataService
from app.services.yahoo_finance_service import YahooFinanceService


def test_full_pipeline_integration(client, db_session):
    """
    End-to-end integration test:
    Mock external Yahoo Finance -> MarketDataService -> DataPreprocessor ->
    PostgreSQL/SQLite persistence -> FeatureEngineeringService ->
    EngineeredFeatures persistence -> Retrieval via API.
    """
    # 1. Prepare 60 days of synthetic trading bars
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(60)]
    prices = [2000.0 + (i * 5.0) for i in range(60)]

    mock_df = pd.DataFrame({
        "Date": dates,
        "Open": [p * 0.99 for p in prices],
        "High": [p * 1.01 for p in prices],
        "Low": [p * 0.98 for p in prices],
        "Close": prices,
        "Adj Close": prices,
        "Volume": [250000] * 60,
    })

    yf_service = YahooFinanceService()

    with patch.object(yf_service, "_fetch_single_symbol") as mock_fetch:
        mock_fetch.return_value = yf_service.normalize_dataframe(mock_df, "RELIANCE.NS")

        # 2. Execute MarketDataService sync
        md_service = MarketDataService(db_session, yf_service=yf_service)
        sync_result = md_service.sync_market_data(symbols=["RELIANCE.NS"], lookback_days=60)

        assert sync_result["rows_fetched"] == 60
        assert sync_result["rows_inserted_updated"] == 60
        assert sync_result["failures"] == []

        # 3. Verify MarketData persisted in DB
        md_repo = MarketDataRepository(db_session)
        records, total_md = md_repo.get_market_data(symbol="RELIANCE.NS")
        assert total_md == 60
        assert records[0].asset_class == "stocks"

        # 4. Execute FeatureEngineeringService
        fe_service = FeatureEngineeringService(db_session)
        fe_summary = fe_service.generate_features_for_all(symbols=["RELIANCE.NS"])
        assert fe_summary["total_upserted"] > 0

        # 5. Verify EngineeredFeatures persisted in DB
        fe_repo = EngineeredFeaturesRepository(db_session)
        features = fe_repo.get_features(symbol="RELIANCE.NS")
        assert len(features) > 0
        latest_fe = fe_repo.get_latest_features("RELIANCE.NS")
        assert latest_fe is not None
        assert latest_fe.sma_20 is not None
        assert latest_fe.ema_20 is not None
        assert latest_fe.rsi_14 is not None
        assert 0.0 <= float(latest_fe.rsi_14) <= 100.0

        # 6. Verify retrieval via REST API endpoints
        res_md = client.get("/api/v1/market-data/RELIANCE.NS")
        assert res_md.status_code == 200
        assert res_md.json()["total"] == 60

        res_fe = client.get("/api/v1/features/RELIANCE.NS")
        assert res_fe.status_code == 200
        assert res_fe.json()["total"] > 0
        first_feat = res_fe.json()["data"][0]
        assert "sma_20" in first_feat
        assert "rsi_14" in first_feat
        assert "macd" in first_feat

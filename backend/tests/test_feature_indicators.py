import datetime
import numpy as np
import pandas as pd
import pytest
from app.services.feature_engineering_service import FeatureEngineeringService


def test_sma_mathematical_correctness(db_session):
    """Verify SMA calculation against independent arithmetic mean."""
    service = FeatureEngineeringService(db_session)
    n = 60
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(n)]
    prices = [10.0 + (i * 0.5) for i in range(n)]

    df = pd.DataFrame({
        "symbol": "SYNTH.NS",
        "date": dates,
        "open": prices,
        "high": [p + 1.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [1000] * n,
    })

    df_res = service.calculate_indicators(df, sma_windows=[20, 50])

    # Check SMA 20 at day index 19 (first full window)
    expected_sma_20 = float(np.mean(prices[0:20]))
    actual_sma_20 = float(df_res.loc[19, "sma_20"])
    assert abs(actual_sma_20 - expected_sma_20) < 1e-4

    # Check SMA 50 at day index 49 (first full window)
    expected_sma_50 = float(np.mean(prices[0:50]))
    actual_sma_50 = float(df_res.loc[49, "sma_50"])
    assert abs(actual_sma_50 - expected_sma_50) < 1e-4


def test_ema_mathematical_correctness(db_session):
    """Verify EMA calculation against recursive EMA formula."""
    service = FeatureEngineeringService(db_session)
    n = 60
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(n)]
    np.random.seed(99)
    prices = [100.0]
    for _ in range(n - 1):
        prices.append(prices[-1] * (1.0 + np.random.normal(0.001, 0.01)))

    df = pd.DataFrame({
        "symbol": "SYNTH.NS",
        "date": dates,
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": [5000] * n,
    })

    df_res = service.calculate_indicators(df, ema_windows=[20, 50])

    # Check EMA column presence
    assert "ema_20" in df_res.columns
    assert "ema_50" in df_res.columns

    # Verify manual recursive calculation of EMA(20) with adjust=False
    # alpha = 2 / (20 + 1)
    alpha = 2.0 / 21.0
    manual_ema = [prices[0]]
    for p in prices[1:]:
        manual_ema.append(alpha * p + (1.0 - alpha) * manual_ema[-1])

    for i in range(n):
        actual = float(df_res.loc[i, "ema_20"])
        expected = manual_ema[i]
        assert abs(actual - expected) < 1e-4


def test_rsi_wilders_smoothing_and_bounds(db_session):
    """Verify RSI Wilder's smoothing, bounds [0, 100], and extreme market conditions."""
    service = FeatureEngineeringService(db_session)
    n = 60
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(n)]

    # 1. Monotonically increasing prices -> RSI should approach 100
    up_prices = [100.0 + (i * 2.0) for i in range(n)]
    df_up = pd.DataFrame({
        "symbol": "UP.NS",
        "date": dates,
        "open": up_prices,
        "high": [p + 1.0 for p in up_prices],
        "low": [p - 1.0 for p in up_prices],
        "close": up_prices,
        "volume": [1000] * n,
    })
    res_up = service.calculate_indicators(df_up, rsi_period=14)
    # After warmup period, RSI on strictly positive gains should equal 100
    valid_up_rsi = res_up["rsi_14"].dropna().iloc[-10:]
    for val in valid_up_rsi:
        assert val == 100.0

    # 2. Monotonically decreasing prices -> RSI should approach 0
    down_prices = [200.0 - (i * 2.0) for i in range(n)]
    df_down = pd.DataFrame({
        "symbol": "DOWN.NS",
        "date": dates,
        "open": down_prices,
        "high": [p + 1.0 for p in down_prices],
        "low": [p - 1.0 for p in down_prices],
        "close": down_prices,
        "volume": [1000] * n,
    })
    res_down = service.calculate_indicators(df_down, rsi_period=14)
    valid_down_rsi = res_down["rsi_14"].dropna().iloc[-10:]
    for val in valid_down_rsi:
        assert val == 0.0


def test_macd_calculation(db_session):
    """Verify MACD line, signal line, and histogram relationships."""
    service = FeatureEngineeringService(db_session)
    n = 60
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(n)]
    prices = [50.0 + (i * 0.8) for i in range(n)]

    df = pd.DataFrame({
        "symbol": "MACD.NS",
        "date": dates,
        "open": prices,
        "high": [p + 1.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [2000] * n,
    })

    df_res = service.calculate_indicators(df, macd_fast=12, macd_slow=26, macd_signal=9)

    assert "macd" in df_res.columns
    assert "macd_signal" in df_res.columns
    assert "macd_histogram" in df_res.columns

    # Verify histogram = macd - signal
    for i in range(n):
        macd_val = df_res.loc[i, "macd"]
        sig_val = df_res.loc[i, "macd_signal"]
        hist_val = df_res.loc[i, "macd_histogram"]
        if pd.notna(macd_val) and pd.notna(sig_val) and pd.notna(hist_val):
            assert abs((macd_val - sig_val) - hist_val) < 1e-4


def test_no_look_ahead_leakage(db_session):
    """Verify that indicators at time t are identical regardless of future data appended."""
    service = FeatureEngineeringService(db_session)
    n_base = 35
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(60)]
    prices = [100.0 + (i * 0.5) for i in range(60)]

    df_base = pd.DataFrame({
        "symbol": "LEAK_TEST.NS",
        "date": dates[:n_base],
        "open": prices[:n_base],
        "high": [p + 1.0 for p in prices[:n_base]],
        "low": [p - 1.0 for p in prices[:n_base]],
        "close": prices[:n_base],
        "volume": [1000] * n_base,
    })

    df_extended = pd.DataFrame({
        "symbol": "LEAK_TEST.NS",
        "date": dates,
        "open": prices,
        "high": [p + 1.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [1000] * 60,
    })

    res_base = service.calculate_indicators(df_base)
    res_extended = service.calculate_indicators(df_extended)

    # Indicator values at index 30 must be identical in both runs
    idx = 30
    for col in ["sma_20", "ema_20", "rsi_14", "macd", "daily_return", "rolling_volatility"]:
        val_base = res_base.loc[idx, col]
        val_ext = res_extended.loc[idx, col]
        if pd.notna(val_base):
            assert abs(val_base - val_ext) < 1e-4, f"Look-ahead leakage detected in column {col}"

import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.market_data import MarketData
from app.repositories.engineered_features_repository import EngineeredFeaturesRepository
from app.repositories.market_data_repository import MarketDataRepository

logger = logging.getLogger(__name__)


class FeatureEngineeringService:
    """
    Dedicated service for technical indicator computation, feature validation,
    leakage prevention, and persistence into PostgreSQL.
    """

    def __init__(self, db: Session):
        self.db = db
        self.market_repo = MarketDataRepository(db)
        self.features_repo = EngineeredFeaturesRepository(db)

    def calculate_indicators(
        self,
        df: pd.DataFrame,
        sma_windows: Optional[List[int]] = None,
        ema_windows: Optional[List[int]] = None,
        rsi_period: Optional[int] = None,
        macd_fast: Optional[int] = None,
        macd_slow: Optional[int] = None,
        macd_signal: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Calculates configurable technical indicators for a single instrument's OHLCV series.
        Chronologically sorted by date with no forward look-ahead leakage.
        """
        if df.empty or len(df) < 5:
            return pd.DataFrame()

        # Enforce chronological ordering to prevent look-ahead bias
        df = df.sort_values("date").reset_index(drop=True).copy()
        close = df["close"].astype(float)

        s_windows = sma_windows or (settings.FEATURE_SMA_WINDOWS if isinstance(settings.FEATURE_SMA_WINDOWS, list) else [20, 50])
        e_windows = ema_windows or (settings.FEATURE_EMA_WINDOWS if isinstance(settings.FEATURE_EMA_WINDOWS, list) else [20, 50])
        r_period = rsi_period or settings.RSI_PERIOD
        m_fast = macd_fast or settings.MACD_FAST_PERIOD
        m_slow = macd_slow or settings.MACD_SLOW_PERIOD
        m_sig = macd_signal or settings.MACD_SIGNAL_PERIOD

        # 1. Simple Moving Averages (SMA)
        for w in s_windows:
            df[f"sma_{w}"] = close.rolling(window=w).mean()
        if "sma_20" not in df.columns:
            df["sma_20"] = close.rolling(window=20).mean()
        if "sma_50" not in df.columns:
            df["sma_50"] = close.rolling(window=50).mean()

        # 2. Exponential Moving Averages (EMA)
        for span in e_windows:
            df[f"ema_{span}"] = close.ewm(span=span, adjust=False).mean()
        if "ema_20" not in df.columns:
            df["ema_20"] = close.ewm(span=20, adjust=False).mean()
        if "ema_50" not in df.columns:
            df["ema_50"] = close.ewm(span=50, adjust=False).mean()

        # 3. Relative Strength Index (RSI) using Wilder's Smoothing
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = -1.0 * delta.clip(upper=0.0)
        # Wilder's smoothing uses alpha = 1 / period
        avg_gain = gain.ewm(alpha=1.0 / r_period, min_periods=r_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / r_period, min_periods=r_period, adjust=False).mean()

        rs = np.where(avg_loss == 0, np.nan, avg_gain / avg_loss)
        rsi = np.where(
            avg_loss == 0,
            100.0,
            np.where(avg_gain == 0, 0.0, 100.0 - (100.0 / (1.0 + rs)))
        )
        df["rsi_14"] = rsi
        if r_period != 14:
            df[f"rsi_{r_period}"] = rsi

        # 4. Moving Average Convergence Divergence (MACD)
        ema_fast_s = close.ewm(span=m_fast, adjust=False).mean()
        ema_slow_s = close.ewm(span=m_slow, adjust=False).mean()
        df["macd"] = ema_fast_s - ema_slow_s
        df["macd_signal"] = df["macd"].ewm(span=m_sig, adjust=False).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]

        # 5. Daily Return
        df["daily_return"] = close.pct_change()

        # 6. Rolling Volatility (20-day sample standard deviation)
        df["rolling_volatility"] = df["daily_return"].rolling(window=20).std()

        return df

    def validate_and_format_features(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Validate calculated indicator rows and convert into formatted dicts for DB upsert.
        Rejects incomplete (warmup NaN), non-finite, or out-of-bounds indicator values.
        """
        if df.empty:
            return []

        valid_records: List[Dict[str, Any]] = []

        for _, row in df.iterrows():
            close_val = float(row["close"]) if pd.notna(row.get("close")) else None
            high_val = float(row["high"]) if pd.notna(row.get("high")) else None
            low_val = float(row["low"]) if pd.notna(row.get("low")) else None

            # Basic price validity check
            price_valid = (
                close_val is not None
                and close_val > 0
                and high_val is not None
                and low_val is not None
                and high_val >= low_val - 0.01
            )
            if not price_valid:
                continue

            # Core required indicators: rsi_14, daily_return, rolling_volatility, sma_20
            rsi_val = float(row["rsi_14"]) if pd.notna(row.get("rsi_14")) else np.nan
            ret_val = float(row["daily_return"]) if pd.notna(row.get("daily_return")) else np.nan
            vol_val = float(row["rolling_volatility"]) if pd.notna(row.get("rolling_volatility")) else np.nan
            sma20_val = float(row["sma_20"]) if pd.notna(row.get("sma_20")) else np.nan

            if (
                np.isnan(rsi_val)
                or np.isnan(ret_val)
                or np.isnan(vol_val)
                or np.isnan(sma20_val)
            ):
                continue

            # Validate numerical bounds and finite checks
            if not (np.isfinite(ret_val) and np.isfinite(vol_val) and np.isfinite(rsi_val)):
                continue

            if not (0.0 <= rsi_val <= 100.0):
                continue

            date_val = row["date"]
            if isinstance(date_val, pd.Timestamp):
                date_val = date_val.date()
            elif isinstance(date_val, str):
                date_val = datetime.date.fromisoformat(date_val)

            sma50_val = float(row["sma_50"]) if pd.notna(row.get("sma_50")) else None
            ema20_val = float(row["ema_20"]) if pd.notna(row.get("ema_20")) else None
            ema50_val = float(row["ema_50"]) if pd.notna(row.get("ema_50")) else None
            macd_val = float(row["macd"]) if pd.notna(row.get("macd")) else None
            macd_sig = float(row["macd_signal"]) if pd.notna(row.get("macd_signal")) else None
            macd_hist = float(row["macd_histogram"]) if pd.notna(row.get("macd_histogram")) else None
            m_id = int(row["market_data_id"]) if pd.notna(row.get("market_data_id")) else None

            rec = {
                "symbol": str(row["symbol"]).strip().upper(),
                "date": date_val,
                "market_data_id": m_id,
                "sma_20": float(round(sma20_val, 4)) if sma20_val is not None else None,
                "sma_50": float(round(sma50_val, 4)) if sma50_val is not None else None,
                "ema_20": float(round(ema20_val, 4)) if ema20_val is not None else None,
                "ema_50": float(round(ema50_val, 4)) if ema50_val is not None else None,
                "rsi_14": float(round(rsi_val, 4)),
                "macd": float(round(macd_val, 4)) if macd_val is not None else None,
                "macd_signal": float(round(macd_sig, 4)) if macd_sig is not None else None,
                "macd_histogram": float(round(macd_hist, 4)) if macd_hist is not None else None,
                "daily_return": float(round(ret_val, 6)),
                "rolling_volatility": float(round(vol_val, 6)),
            }
            valid_records.append(rec)

        return valid_records

    def generate_features_for_symbol(
        self,
        symbol: str,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> Tuple[int, int]:
        """
        Fetch market data for a symbol, compute indicators, validate, and upsert features.
        Returns (upserted_count, total_records_processed).
        """
        records, total = self.market_repo.get_market_data(
            symbol=symbol, start_date=start_date, end_date=end_date, limit=10000
        )
        if not records:
            logger.info(f"No market data found for {symbol} to compute features.")
            return 0, 0

        raw_data = [
            {
                "market_data_id": r.id,
                "symbol": r.symbol,
                "date": r.date,
                "open": float(r.open) if r.open is not None else None,
                "high": float(r.high) if r.high is not None else None,
                "low": float(r.low) if r.low is not None else None,
                "close": float(r.close) if r.close is not None else None,
                "volume": r.volume,
            }
            for r in records
        ]

        df = pd.DataFrame(raw_data)
        df_indicators = self.calculate_indicators(df)
        valid_records = self.validate_and_format_features(df_indicators)

        if not valid_records:
            return 0, len(records)

        upserted, total_valid = self.features_repo.upsert_records(valid_records)
        logger.info(f"Generated and upserted {upserted}/{total_valid} features for {symbol}")
        return upserted, total_valid

    def generate_features_for_all(
        self,
        symbols: Optional[List[str]] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate feature calculation and persistence across multiple symbols.
        """
        if not symbols:
            coverage = self.market_repo.get_symbol_coverage()
            symbols = [c["symbol"] for c in coverage]

        if not symbols:
            symbols = [
                "RELIANCE.NS",
                "TCS.NS",
                "HDFCBANK.NS",
                "INFY.NS",
                "ICICIBANK.NS",
                "NIFTYBEES.NS",
                "GOLDBEES.NS",
            ]

        summary: Dict[str, Any] = {
            "status": "success",
            "symbols_processed": [],
            "total_upserted": 0,
        }

        for sym in symbols:
            clean_sym = sym.strip().upper()
            try:
                upserted, processed = self.generate_features_for_symbol(
                    clean_sym, start_date=start_date, end_date=end_date
                )
                summary["symbols_processed"].append(
                    {"symbol": clean_sym, "upserted": upserted, "processed": processed, "status": "ok"}
                )
                summary["total_upserted"] += upserted
            except Exception as exc:
                logger.error(f"Error computing features for {clean_sym}: {exc}", exc_info=True)
                summary["symbols_processed"].append(
                    {"symbol": clean_sym, "upserted": 0, "processed": 0, "status": "failed", "error": str(exc)}
                )

        return summary

import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from app.models.market_data import MarketData
from app.repositories.engineered_features_repository import EngineeredFeaturesRepository
from app.repositories.market_data_repository import MarketDataRepository

logger = logging.getLogger(__name__)


class FeatureEngineeringService:
    """
    Service layer for technical indicator calculation, feature engineering,
    validation, and persistence.
    """

    def __init__(self, db: Session):
        self.db = db
        self.market_repo = MarketDataRepository(db)
        self.features_repo = EngineeredFeaturesRepository(db)

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for a DataFrame containing market data
        for a single symbol.
        DataFrame must contain columns: ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume'].
        Sorted chronologically by date.
        """
        if df.empty or len(df) < 5:
            return pd.DataFrame()

        df = df.sort_values("date").reset_index(drop=True).copy()
        close = df["close"].astype(float)

        # 1. Simple Moving Averages
        df["sma_20"] = close.rolling(window=20).mean()
        df["sma_50"] = close.rolling(window=50).mean()

        # 2. Exponential Moving Average
        df["ema_20"] = close.ewm(span=20, adjust=False).mean()

        # 3. RSI 14
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        # Avoid division by zero
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["rsi_14"] = 100 - (100 / (1 + rs))

        # 4. MACD (12, 26, 9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        df["macd"] = ema_12 - ema_26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]

        # 5. Daily Return
        df["daily_return"] = close.pct_change()

        # 6. Rolling Volatility (20-day standard deviation of daily return)
        df["rolling_volatility"] = df["daily_return"].rolling(window=20).std()

        return df

    def validate_and_format_features(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Validate calculated indicator rows and convert into dictionary list for storage.
        Rejects incomplete (NaN), non-finite, or invalid indicator rows.
        """
        if df.empty:
            return []

        valid_records: List[Dict[str, Any]] = []

        for idx, row in df.iterrows():
            close_val = float(row["close"]) if pd.notna(row.get("close")) else None
            high_val = float(row["high"]) if pd.notna(row.get("high")) else None
            low_val = float(row["low"]) if pd.notna(row.get("low")) else None

            # Check price/date sanity
            price_valid = (
                close_val is not None
                and close_val > 0
                and high_val is not None
                and low_val is not None
                and high_val >= low_val - 0.01
            )
            if not price_valid:
                continue

            # Core required indicators for AI model: daily_return, rolling_volatility, sma_20, rsi_14, macd
            # Drop rows with NaN in key indicators (usually early warmup period)
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
            macd_val = float(row["macd"]) if pd.notna(row.get("macd")) else None
            macd_sig = float(row["macd_signal"]) if pd.notna(row.get("macd_signal")) else None
            macd_hist = float(row["macd_histogram"]) if pd.notna(row.get("macd_histogram")) else None

            rec = {
                "symbol": str(row["symbol"]).strip().upper(),
                "date": date_val,
                "sma_20": float(round(sma20_val, 4)) if sma20_val is not None else None,
                "sma_50": float(round(sma50_val, 4)) if sma50_val is not None else None,
                "ema_20": float(round(ema20_val, 4)) if ema20_val is not None else None,
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
            symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]

        summary: Dict[str, Any] = {
            "status": "success",
            "symbols_processed": [],
            "total_upserted": 0,
        }

        for sym in symbols:
            clean_sym = sym.strip().upper()
            upserted, processed = self.generate_features_for_symbol(
                clean_sym, start_date=start_date, end_date=end_date
            )
            summary["symbols_processed"].append(
                {"symbol": clean_sym, "upserted": upserted, "processed": processed}
            )
            summary["total_upserted"] += upserted

        return summary

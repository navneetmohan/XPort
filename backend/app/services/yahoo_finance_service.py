import datetime
import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class YahooFinanceService:
    """
    Service responsible for fetching, parsing, and normalizing market data
    from Yahoo Finance. Does NOT interact with the database.
    """

    def fetch_historical_ohlcv(
        self,
        symbols: List[str],
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        lookback_days: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical OHLCV data for given list of symbols.
        Returns a list of standardized record dictionaries.
        """
        if not symbols:
            logger.warning("No symbols provided to fetch_historical_ohlcv")
            return []

        cleaned_symbols = [s.strip().upper() for s in symbols if s and s.strip()]
        if not cleaned_symbols:
            return []

        end = end_date or datetime.date.today()
        if start_date:
            start = start_date
        elif lookback_days:
            start = end - datetime.timedelta(days=lookback_days)
        else:
            start = end - datetime.timedelta(days=1825)

        logger.info(
            f"Fetching market data for {len(cleaned_symbols)} symbols ({cleaned_symbols}) "
            f"from {start} to {end}"
        )

        all_records: List[Dict[str, Any]] = []

        for symbol in cleaned_symbols:
            symbol_records = self._fetch_single_symbol(symbol, start, end)
            all_records.extend(symbol_records)

        logger.info(f"Successfully fetched and normalized {len(all_records)} market data records")
        return all_records

    def _fetch_single_symbol(
        self, symbol: str, start: datetime.date, end: datetime.date
    ) -> List[Dict[str, Any]]:
        """Fetch and normalize data for a single symbol."""
        try:
            df = yf.download(
                tickers=symbol,
                start=start.strftime("%Y-%m-%d"),
                end=(end + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=False,
            )

            if df is None or df.empty:
                logger.warning(f"No data returned from Yahoo Finance for symbol '{symbol}'")
                return []

            return self.normalize_dataframe(df, symbol)
        except Exception as exc:
            logger.error(f"Error fetching yfinance data for symbol '{symbol}': {exc}", exc_info=True)
            return []

    def normalize_dataframe(self, df: pd.DataFrame, default_symbol: str) -> List[Dict[str, Any]]:
        """
        Normalizes raw yfinance DataFrame into a list of MarketData dictionaries.
        """
        if df.empty:
            return []

        df = df.copy()

        # Handle MultiIndex columns if present (e.g. ('Close', 'RELIANCE.NS'))
        if isinstance(df.columns, pd.MultiIndex):
            level_0 = df.columns.get_level_values(0)
            df.columns = level_0

        # Reset index to bring Date/Datetime from index into a column
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()

        date_col = None
        for col in df.columns:
            if str(col).lower() in ("date", "index", "datetime", "timestamp"):
                date_col = col
                break

        if date_col is None and len(df.columns) > 0:
            date_col = df.columns[0]

        column_map = {}
        for col in df.columns:
            col_str = str(col).strip().lower().replace(" ", "_")
            if col_str == "open":
                column_map[col] = "open"
            elif col_str == "high":
                column_map[col] = "high"
            elif col_str == "low":
                column_map[col] = "low"
            elif col_str == "close":
                column_map[col] = "close"
            elif col_str in ("adj_close", "adjclose"):
                column_map[col] = "adj_close"
            elif col_str == "volume":
                column_map[col] = "volume"

        df = df.rename(columns=column_map)

        if "close" in df.columns and "adj_close" not in df.columns:
            df["adj_close"] = df["close"]

        records: List[Dict[str, Any]] = []

        for _, row in df.iterrows():
            raw_date = row[date_col] if date_col in row else None
            if pd.isna(raw_date):
                continue

            if isinstance(raw_date, (pd.Timestamp, datetime.datetime)):
                record_date = raw_date.date()
            elif isinstance(raw_date, datetime.date):
                record_date = raw_date
            else:
                try:
                    record_date = pd.to_datetime(raw_date).date()
                except Exception:
                    continue

            open_val = self._clean_float(row.get("open"))
            high_val = self._clean_float(row.get("high"))
            low_val = self._clean_float(row.get("low"))
            close_val = self._clean_float(row.get("close"))
            adj_close_val = self._clean_float(row.get("adj_close"))
            volume_val = self._clean_int(row.get("volume"))

            records.append({
                "symbol": default_symbol,
                "date": record_date,
                "open": open_val,
                "high": high_val,
                "low": low_val,
                "close": close_val,
                "adj_close": adj_close_val,
                "volume": volume_val,
            })

        return records

    @staticmethod
    def _clean_float(val: Any) -> Optional[float]:
        if val is None or pd.isna(val) or np.isinf(val):
            return None
        try:
            f_val = float(val)
            return f_val if not (np.isnan(f_val) or np.isinf(f_val)) else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _clean_int(val: Any) -> Optional[int]:
        if val is None or pd.isna(val) or np.isinf(val):
            return None
        try:
            i_val = int(float(val))
            return i_val if i_val >= 0 else None
        except (ValueError, TypeError):
            return None

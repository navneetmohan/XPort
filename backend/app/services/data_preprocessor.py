"""
Data Preprocessing Layer for XPort.
Provides systematic data cleaning, chronology enforcement, duplicate removal,
OHLCV sanity checks, gap diagnostics, and data-quality reporting.

Data Imputation Strategy Rationale:
- Price fields (Close, Open, High, Low) represent true market valuations.
  We DO NOT blindly forward-fill missing prices across missing trading sessions,
  as doing so falsifies volatility, zeroes returns artificially, and corrupts
  downstream risk-adjusted metrics (Sharpe ratio, rolling volatility, RSI).
  If core price values are missing or negative, the record is rejected.
- Volume: Missing volume is imputed to 0 (indicating zero recorded trades/liquidity).
- Adjusted Close: If adjusted close is missing from data feed, it is imputed as Close
  (assuming no corporate actions/dividends occurred on that session).
"""

import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from app.core.instruments import get_asset_class_for_symbol

logger = logging.getLogger(__name__)


class DataQualityReport:
    """Detailed data quality assessment for a symbol or universe batch."""

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.records_fetched: int = 0
        self.valid_records: int = 0
        self.missing_value_count: int = 0
        self.duplicate_count: int = 0
        self.invalid_record_count: int = 0
        self.earliest_date: Optional[datetime.date] = None
        self.latest_date: Optional[datetime.date] = None
        self.gap_warnings: List[str] = []
        self.rejection_reasons: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "records_fetched": self.records_fetched,
            "valid_records": self.valid_records,
            "missing_value_count": self.missing_value_count,
            "duplicate_count": self.duplicate_count,
            "invalid_record_count": self.invalid_record_count,
            "earliest_date": self.earliest_date.isoformat() if self.earliest_date else None,
            "latest_date": self.latest_date.isoformat() if self.latest_date else None,
            "gap_warnings_count": len(self.gap_warnings),
            "gap_warnings": self.gap_warnings[:10],
            "rejections": self.rejection_reasons[:20],
        }


class DataPreprocessor:
    """
    Dedicated preprocessor responsible for data hygiene, chronological sorting,
    validation, gap detection, and reporting.
    """

    PRICE_ROUNDING_TOLERANCE = 0.01  # Currency unit tolerance for precision artifacts
    MAX_TRADING_GAP_DAYS = 5        # Business days before a warning is logged

    def preprocess_symbol_data(
        self,
        raw_records: List[Dict[str, Any]],
        symbol: str,
        asset_class: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], DataQualityReport]:
        """
        Preprocesses a list of raw market data records for a single instrument.
        Returns (clean_records, quality_report).
        """
        clean_symbol = symbol.strip().upper()
        resolved_asset_class = asset_class or get_asset_class_for_symbol(clean_symbol)
        report = DataQualityReport(clean_symbol)
        report.records_fetched = len(raw_records)

        if not raw_records:
            return [], report

        # Step 1: Parse and validate individual records
        parsed_by_date: Dict[datetime.date, Dict[str, Any]] = {}
        for raw in raw_records:
            date_val = raw.get("date")
            if not date_val:
                report.missing_value_count += 1
                report.invalid_record_count += 1
                report.rejection_reasons.append({"reason": "Missing date field", "raw": str(raw)})
                continue

            if isinstance(date_val, str):
                try:
                    date_val = datetime.date.fromisoformat(date_val)
                except ValueError:
                    report.invalid_record_count += 1
                    report.rejection_reasons.append({"reason": f"Malformed date string: {date_val}"})
                    continue
            elif isinstance(date_val, datetime.datetime):
                date_val = date_val.date()

            # Detect duplicates
            if date_val in parsed_by_date:
                report.duplicate_count += 1
                logger.debug(f"Duplicate record detected for {clean_symbol} on {date_val}; keeping latest.")

            # Validate numerical values
            is_valid, reason, sanitized = self._validate_and_sanitize(raw, date_val, clean_symbol, resolved_asset_class)
            if not is_valid:
                report.invalid_record_count += 1
                report.rejection_reasons.append({"date": str(date_val), "reason": reason})
            else:
                parsed_by_date[date_val] = sanitized

        if not parsed_by_date:
            return [], report

        # Step 2: Chronological Sort
        sorted_dates = sorted(parsed_by_date.keys())
        clean_records = [parsed_by_date[d] for d in sorted_dates]

        report.valid_records = len(clean_records)
        report.earliest_date = sorted_dates[0]
        report.latest_date = sorted_dates[-1]

        # Step 3: Gap Analysis across consecutive business days
        self._detect_trading_gaps(sorted_dates, report)

        logger.info(
            f"Preprocessed {clean_symbol}: {report.valid_records}/{report.records_fetched} valid records "
            f"({report.duplicate_count} duplicates, {report.invalid_record_count} rejected, "
            f"range: {report.earliest_date} to {report.latest_date})"
        )

        return clean_records, report

    def _validate_and_sanitize(
        self,
        raw: Dict[str, Any],
        date_val: datetime.date,
        symbol: str,
        asset_class: str,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates OHLC relationships, applies documented imputation, and returns sanitized dict.
        """
        open_val = self._to_float(raw.get("open"))
        high_val = self._to_float(raw.get("high"))
        low_val = self._to_float(raw.get("low"))
        close_val = self._to_float(raw.get("close"))
        adj_close_val = self._to_float(raw.get("adj_close"))
        volume_val = self._to_int(raw.get("volume"))

        # Core Rule 1: Close price is non-negotiable
        if close_val is None or close_val <= 0:
            return False, f"Close price must be strictly positive, got: {close_val}", {}

        # Impute missing Open/High/Low if close is solitary valid bar (flat day)
        if open_val is None:
            open_val = close_val
        if high_val is None:
            high_val = max(open_val, close_val)
        if low_val is None:
            low_val = min(open_val, close_val)

        # Impute missing Adj Close with Close
        if adj_close_val is None:
            adj_close_val = close_val

        # Impute missing Volume with 0
        if volume_val is None or volume_val < 0:
            volume_val = 0

        # Core Rule 2: Strictly positive prices
        for name, val in [("open", open_val), ("high", high_val), ("low", low_val), ("adj_close", adj_close_val)]:
            if val is None or val <= 0 or not np.isfinite(val):
                return False, f"Price {name} must be finite and positive, got: {val}", {}

        # Core Rule 3: High cannot be lower than Low
        tol = self.PRICE_ROUNDING_TOLERANCE
        if high_val < low_val - tol:
            return False, f"Inconsistent OHLC: High ({high_val}) < Low ({low_val})", {}

        # Core Rule 4: Open and Close bounded within [Low, High]
        if open_val > high_val + tol or open_val < low_val - tol:
            return False, f"Inconsistent OHLC: Open ({open_val}) outside Low ({low_val}) - High ({high_val})", {}

        if close_val > high_val + tol or close_val < low_val - tol:
            return False, f"Inconsistent OHLC: Close ({close_val}) outside Low ({low_val}) - High ({high_val})", {}

        sanitized = {
            "symbol": symbol,
            "asset_class": asset_class,
            "date": date_val,
            "open": round(open_val, 4),
            "high": round(high_val, 4),
            "low": round(low_val, 4),
            "close": round(close_val, 4),
            "adj_close": round(adj_close_val, 4),
            "volume": volume_val,
        }
        return True, "", sanitized

    def _detect_trading_gaps(self, sorted_dates: List[datetime.date], report: DataQualityReport) -> None:
        """Identifies gaps longer than standard holiday windows between consecutive sessions."""
        for i in range(1, len(sorted_dates)):
            prev_d = sorted_dates[i - 1]
            curr_d = sorted_dates[i]
            calendar_gap = (curr_d - prev_d).days

            # Calculate approximate business days
            if calendar_gap > self.MAX_TRADING_GAP_DAYS:
                msg = (
                    f"Gap of {calendar_gap} calendar days between {prev_d} and {curr_d} "
                    f"exceeds standard weekend/holiday threshold."
                )
                report.gap_warnings.append(msg)
                logger.debug(f"{report.symbol}: {msg}")

    @staticmethod
    def _to_float(val: Any) -> Optional[float]:
        if val is None or pd.isna(val) or np.isinf(val):
            return None
        try:
            f = float(val)
            return f if np.isfinite(f) else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _to_int(val: Any) -> Optional[int]:
        if val is None or pd.isna(val) or np.isinf(val):
            return None
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None

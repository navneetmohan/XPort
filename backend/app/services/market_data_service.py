import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.market_data_repository import MarketDataRepository
from app.services.yahoo_finance_service import YahooFinanceService

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Orchestration service combining YahooFinanceService data acquisition,
    data validation rules, and MarketDataRepository persistence.
    Independent of FastAPI and safe for background Celery tasks.
    """

    def __init__(self, db: Session, yf_service: Optional[YahooFinanceService] = None):
        self.db = db
        self.repository = MarketDataRepository(db)
        self.yf_service = yf_service or YahooFinanceService()

    def sync_market_data(
        self,
        symbols: Optional[List[str]] = None,
        lookback_days: Optional[int] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> Dict[str, Any]:
        """
        Synchronizes historical OHLCV market data for requested symbols.
        Returns a detailed summary of synchronization results.
        """
        target_symbols = symbols or settings.MARKET_DATA_DEFAULT_SYMBOLS
        lookback = lookback_days or settings.MARKET_DATA_DEFAULT_LOOKBACK_DAYS

        if isinstance(target_symbols, str):
            target_symbols = [s.strip() for s in target_symbols.split(",") if s.strip()]

        cleaned_symbols = [s.strip().upper() for s in target_symbols if s and s.strip()]

        sync_start_time = datetime.datetime.now(datetime.timezone.utc)
        logger.info(f"Starting market data synchronization for symbols: {cleaned_symbols}")

        try:
            raw_records = self.yf_service.fetch_historical_ohlcv(
                symbols=cleaned_symbols,
                start_date=start_date,
                end_date=end_date,
                lookback_days=lookback if not start_date else None,
            )
        except Exception as exc:
            logger.error(f"Failed to fetch market data from yfinance: {exc}", exc_info=True)
            return {
                "symbols_requested": cleaned_symbols,
                "symbols_processed": [],
                "rows_fetched": 0,
                "rows_inserted_updated": 0,
                "rows_rejected": 0,
                "failures": [{"symbol": "ALL", "reason": str(exc)}],
                "sync_timestamp": sync_start_time.isoformat(),
            }

        valid_records: List[Dict[str, Any]] = []
        rejected_records: List[Dict[str, Any]] = []
        processed_symbols = set()

        for rec in raw_records:
            is_valid, reason = self.validate_record(rec)
            if is_valid:
                valid_records.append(rec)
                processed_symbols.add(rec["symbol"])
            else:
                rejected_records.append({"record": rec, "reason": reason})
                logger.warning(
                    f"Rejected market data record for {rec.get('symbol')} on {rec.get('date')}: {reason}"
                )

        upserted_count = 0
        if valid_records:
            upserted_count, _ = self.repository.upsert_records(valid_records)

        failures = []
        for s in cleaned_symbols:
            if s not in processed_symbols:
                failures.append({"symbol": s, "reason": "No valid records fetched or saved"})

        summary = {
            "symbols_requested": cleaned_symbols,
            "symbols_processed": sorted(list(processed_symbols)),
            "rows_fetched": len(raw_records),
            "rows_inserted_updated": upserted_count,
            "rows_rejected": len(rejected_records),
            "failures": failures,
            "sync_timestamp": sync_start_time.isoformat(),
        }

        logger.info(
            f"Market data synchronization complete. Fetched: {len(raw_records)}, "
            f"Persisted: {upserted_count}, Rejected: {len(rejected_records)}"
        )
        return summary

    def validate_record(self, rec: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates a single market data record according to Stage 2 validation rules.
        Returns (is_valid, failure_reason).
        """
        symbol = rec.get("symbol")
        if not symbol or not isinstance(symbol, str) or not symbol.strip():
            return False, "Symbol must be a non-empty string"

        date_val = rec.get("date")
        if not date_val or not isinstance(date_val, datetime.date):
            return False, f"Invalid date: {date_val}"

        open_val = rec.get("open")
        high_val = rec.get("high")
        low_val = rec.get("low")
        close_val = rec.get("close")
        volume_val = rec.get("volume")

        # Require price values to be positive numbers
        for name, val in [("open", open_val), ("high", high_val), ("low", low_val), ("close", close_val)]:
            if val is None:
                return False, f"Missing price field: {name}"
            if not isinstance(val, (int, float)) or val <= 0:
                return False, f"Price {name} must be a positive number, got: {val}"

        if volume_val is not None:
            if not isinstance(volume_val, int) or volume_val < 0:
                return False, f"Volume must be a non-negative integer, got: {volume_val}"

        # High should not be lower than Low (allowing 0.01 tolerance for precision rounding)
        if high_val < low_val - 0.01:
            return False, f"High price ({high_val}) cannot be lower than Low price ({low_val})"

        # Open/Close should be bounded within High/Low range with rounding tolerance
        tol = 0.01
        if open_val > high_val + tol or open_val < low_val - tol:
            return False, f"Open price ({open_val}) outside High ({high_val}) / Low ({low_val}) bound"

        if close_val > high_val + tol or close_val < low_val - tol:
            return False, f"Close price ({close_val}) outside High ({high_val}) / Low ({low_val}) bound"

        return True, ""

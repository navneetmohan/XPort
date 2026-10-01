import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.instruments import (
    get_all_instruments,
    get_asset_class_for_symbol,
    get_yahoo_supported_symbols,
)
from app.repositories.market_data_repository import MarketDataRepository
from app.repositories.engineered_features_repository import EngineeredFeaturesRepository
from app.services.data_preprocessor import DataPreprocessor, DataQualityReport
from app.services.yahoo_finance_service import YahooFinanceService

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Market Data Service responsible for coordinating:
    - Yahoo Finance data acquisition
    - Dedicated preprocessing and data hygiene (via DataPreprocessor)
    - Data persistence and querying (via MarketDataRepository)
    - Comprehensive data quality reporting
    """

    def __init__(
        self,
        db: Session,
        yf_service: Optional[YahooFinanceService] = None,
        preprocessor: Optional[DataPreprocessor] = None,
    ):
        self.db = db
        self.repository = MarketDataRepository(db)
        self.features_repo = EngineeredFeaturesRepository(db)
        self.yf_service = yf_service or YahooFinanceService()
        self.preprocessor = preprocessor or DataPreprocessor()

    def sync_market_data(
        self,
        symbols: Optional[List[str]] = None,
        lookback_days: Optional[int] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> Dict[str, Any]:
        """
        Synchronizes historical OHLCV market data for requested symbols.
        Applies preprocessing, validation, deduplication, and persists to database.
        Returns a detailed data quality and sync summary.
        """
        target_symbols = symbols or settings.MARKET_DATA_DEFAULT_SYMBOLS
        lookback = lookback_days or settings.MARKET_DATA_DEFAULT_LOOKBACK_DAYS

        if isinstance(target_symbols, str):
            target_symbols = [s.strip() for s in target_symbols.split(",") if s.strip()]

        cleaned_symbols = [s.strip().upper() for s in target_symbols if s and s.strip()]

        sync_start_time = datetime.datetime.now(datetime.timezone.utc)
        logger.info(f"Starting market data synchronization for symbols: {cleaned_symbols}")

        symbols_processed: List[str] = []
        failures: List[Dict[str, Any]] = []
        quality_reports: List[Dict[str, Any]] = []
        total_fetched = 0
        total_upserted = 0
        total_rejected = 0
        total_duplicates = 0
        total_missing = 0

        # Process instrument by instrument so failure in one does not crash the entire pipeline
        for symbol in cleaned_symbols:
            try:
                raw_records = self.yf_service.fetch_historical_ohlcv(
                    symbols=[symbol],
                    start_date=start_date,
                    end_date=end_date,
                    lookback_days=lookback if not start_date else None,
                )
                total_fetched += len(raw_records)

                if not raw_records:
                    failures.append({"symbol": symbol, "reason": "No data returned from upstream Yahoo Finance"})
                    continue

                # Run through dedicated preprocessing layer
                asset_class = get_asset_class_for_symbol(symbol)
                clean_records, report = self.preprocessor.preprocess_symbol_data(
                    raw_records=raw_records,
                    symbol=symbol,
                    asset_class=asset_class,
                )

                quality_reports.append(report.to_dict())
                total_rejected += report.invalid_record_count
                total_duplicates += report.duplicate_count
                total_missing += report.missing_value_count

                if clean_records:
                    upserted, _ = self.repository.upsert_records(clean_records)
                    total_upserted += upserted
                    symbols_processed.append(symbol)
                else:
                    failures.append({
                        "symbol": symbol,
                        "reason": f"All {len(raw_records)} records failed preprocessing validation",
                    })

            except Exception as exc:
                logger.error(f"Error processing market data for {symbol}: {exc}", exc_info=True)
                failures.append({"symbol": symbol, "reason": str(exc)})

        summary = {
            "symbols_requested": cleaned_symbols,
            "symbols_processed": sorted(symbols_processed),
            "rows_fetched": total_fetched,
            "rows_inserted_updated": total_upserted,
            "rows_rejected": total_rejected,
            "duplicates_detected": total_duplicates,
            "missing_values_detected": total_missing,
            "quality_reports": quality_reports,
            "failures": failures,
            "sync_timestamp": sync_start_time.isoformat(),
        }

        logger.info(
            f"Market data synchronization complete. Fetched: {total_fetched}, "
            f"Persisted: {total_upserted}, Rejected: {total_rejected}, Failures: {len(failures)}"
        )
        return summary

    def get_data_status(self) -> Dict[str, Any]:
        """
        Retrieves overall market data & features pipeline status across the universe.
        """
        all_instruments = get_all_instruments()
        market_coverage = self.repository.get_symbol_coverage()
        feature_coverage = self.features_repo.get_features_coverage()

        market_map = {c["symbol"]: c for c in market_coverage}
        feature_map = {f["symbol"]: f for f in feature_coverage}

        instruments_status = []
        for inst in all_instruments:
            sym = inst["symbol"]
            m_stat = market_map.get(sym, {})
            f_stat = feature_map.get(sym, {})

            instruments_status.append({
                "symbol": sym,
                "name": inst.get("name", sym),
                "asset_class": inst.get("asset_class", "stocks"),
                "is_yahoo_supported": inst.get("is_yahoo_supported", True),
                "market_data_records": m_stat.get("record_count", 0),
                "market_earliest_date": m_stat.get("earliest_date"),
                "market_latest_date": m_stat.get("latest_date"),
                "features_records": f_stat.get("record_count", 0),
                "features_earliest_date": f_stat.get("earliest_date"),
                "features_latest_date": f_stat.get("latest_date"),
                "has_market_data": m_stat.get("record_count", 0) > 0,
                "has_features": f_stat.get("record_count", 0) > 0,
            })

        total_market_records = sum(c.get("record_count", 0) for c in market_coverage)
        total_feature_records = self.features_repo.get_features_count()

        return {
            "status": "operational",
            "total_universe_instruments": len(all_instruments),
            "instruments_with_market_data": len(market_coverage),
            "instruments_with_features": len(feature_coverage),
            "total_market_records": total_market_records,
            "total_feature_records": total_feature_records,
            "instruments": instruments_status,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    def validate_record(self, rec: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Direct validation method maintained for backward compatibility.
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

import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.engineered_features import EngineeredFeatures

logger = logging.getLogger(__name__)


class EngineeredFeaturesRepository:
    """
    Data Access Layer for EngineeredFeatures records supporting high-performance
    PostgreSQL upserts and query operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def upsert_records(self, records: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Upsert engineered feature records into the database.
        Returns a tuple of (inserted_or_updated_count, total_processed_count).
        """
        if not records:
            return 0, 0

        dialect_name = self.db.bind.dialect.name if self.db.bind else "sqlite"

        if dialect_name == "postgresql":
            return self._upsert_postgresql(records)
        else:
            return self._upsert_generic(records)

    def _upsert_postgresql(self, records: List[Dict[str, Any]]) -> Tuple[int, int]:
        """PostgreSQL-specific ON CONFLICT DO UPDATE bulk upsert."""
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        batch_size = 1000
        total_upserted = 0

        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            stmt = pg_insert(EngineeredFeatures).values(batch)
            upsert_stmt = stmt.on_conflict_do_update(
                constraint="uq_engineered_features_symbol_date",
                set_={
                    "sma_20": stmt.excluded.sma_20,
                    "sma_50": stmt.excluded.sma_50,
                    "ema_20": stmt.excluded.ema_20,
                    "rsi_14": stmt.excluded.rsi_14,
                    "macd": stmt.excluded.macd,
                    "macd_signal": stmt.excluded.macd_signal,
                    "macd_histogram": stmt.excluded.macd_histogram,
                    "daily_return": stmt.excluded.daily_return,
                    "rolling_volatility": stmt.excluded.rolling_volatility,
                    "updated_at": func.now(),
                },
            )
            self.db.execute(upsert_stmt)
            total_upserted += len(batch)

        self.db.commit()
        return total_upserted, len(records)

    def _upsert_generic(self, records: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Generic dialect-agnostic upsert for SQLite and unit testing."""
        count = 0
        for rec in records:
            symbol = rec["symbol"]
            date_val = rec["date"]

            existing = self.db.scalar(
                select(EngineeredFeatures).where(
                    EngineeredFeatures.symbol == symbol, EngineeredFeatures.date == date_val
                )
            )

            if existing:
                existing.sma_20 = rec.get("sma_20")
                existing.sma_50 = rec.get("sma_50")
                existing.ema_20 = rec.get("ema_20")
                existing.rsi_14 = rec.get("rsi_14")
                existing.macd = rec.get("macd")
                existing.macd_signal = rec.get("macd_signal")
                existing.macd_histogram = rec.get("macd_histogram")
                existing.daily_return = rec.get("daily_return")
                existing.rolling_volatility = rec.get("rolling_volatility")
            else:
                new_item = EngineeredFeatures(
                    symbol=symbol,
                    date=date_val,
                    sma_20=rec.get("sma_20"),
                    sma_50=rec.get("sma_50"),
                    ema_20=rec.get("ema_20"),
                    rsi_14=rec.get("rsi_14"),
                    macd=rec.get("macd"),
                    macd_signal=rec.get("macd_signal"),
                    macd_histogram=rec.get("macd_histogram"),
                    daily_return=rec.get("daily_return"),
                    rolling_volatility=rec.get("rolling_volatility"),
                )
                self.db.add(new_item)
            count += 1

        self.db.commit()
        return count, len(records)

    def get_features(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        skip: int = 0,
        limit: int = 500,
    ) -> List[EngineeredFeatures]:
        """
        Query EngineeredFeatures records with optional filtering.
        """
        stmt = select(EngineeredFeatures)
        if symbol:
            clean_symbol = symbol.strip().upper()
            stmt = stmt.where(EngineeredFeatures.symbol == clean_symbol)
        if start_date:
            stmt = stmt.where(EngineeredFeatures.date >= start_date)
        if end_date:
            stmt = stmt.where(EngineeredFeatures.date <= end_date)

        stmt = stmt.order_by(EngineeredFeatures.symbol.asc(), EngineeredFeatures.date.asc())
        stmt = stmt.offset(skip).limit(limit)

        return list(self.db.scalars(stmt).all())

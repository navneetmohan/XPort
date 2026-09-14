import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.market_data import MarketData

logger = logging.getLogger(__name__)


class MarketDataRepository:
    """
    Data Access Layer for MarketData records supporting high-performance
    PostgreSQL upserts and query operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def upsert_records(self, records: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Upsert market data records into the database.
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

        # Process in batches of 1000 records
        batch_size = 1000
        total_upserted = 0

        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            stmt = pg_insert(MarketData).values(batch)
            upsert_stmt = stmt.on_conflict_do_update(
                constraint="uq_market_data_symbol_date",
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "adj_close": stmt.excluded.adj_close,
                    "volume": stmt.excluded.volume,
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
                select(MarketData).where(
                    MarketData.symbol == symbol, MarketData.date == date_val
                )
            )

            if existing:
                existing.open = rec.get("open")
                existing.high = rec.get("high")
                existing.low = rec.get("low")
                existing.close = rec.get("close")
                existing.adj_close = rec.get("adj_close")
                existing.volume = rec.get("volume")
            else:
                new_item = MarketData(
                    symbol=symbol,
                    date=date_val,
                    open=rec.get("open"),
                    high=rec.get("high"),
                    low=rec.get("low"),
                    close=rec.get("close"),
                    adj_close=rec.get("adj_close"),
                    volume=rec.get("volume"),
                )
                self.db.add(new_item)
            count += 1

        self.db.commit()
        return count, len(records)

    def get_market_data(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[MarketData], int]:
        """
        Query MarketData records with optional filtering by symbol and date range.
        Returns (list_of_records, total_matching_count).
        """
        stmt = select(MarketData)
        count_stmt = select(func.count()).select_from(MarketData)

        if symbol:
            clean_symbol = symbol.strip().upper()
            stmt = stmt.where(MarketData.symbol == clean_symbol)
            count_stmt = count_stmt.where(MarketData.symbol == clean_symbol)

        if start_date:
            stmt = stmt.where(MarketData.date >= start_date)
            count_stmt = count_stmt.where(MarketData.date >= start_date)

        if end_date:
            stmt = stmt.where(MarketData.date <= end_date)
            count_stmt = count_stmt.where(MarketData.date <= end_date)

        total_count = self.db.scalar(count_stmt) or 0

        stmt = stmt.order_by(MarketData.symbol.asc(), MarketData.date.asc())
        stmt = stmt.offset(skip).limit(limit)

        records = list(self.db.scalars(stmt).all())
        return records, total_count

    def get_symbol_coverage(self) -> List[Dict[str, Any]]:
        """
        Retrieves summary statistics for each available symbol in the database.
        """
        stmt = select(
            MarketData.symbol,
            func.min(MarketData.date).label("earliest_date"),
            func.max(MarketData.date).label("latest_date"),
            func.count(MarketData.id).label("record_count"),
        ).group_by(MarketData.symbol).order_by(MarketData.symbol.asc())

        results = self.db.execute(stmt).all()

        coverage: List[Dict[str, Any]] = []
        for row in results:
            coverage.append({
                "symbol": row.symbol,
                "earliest_date": row.earliest_date,
                "latest_date": row.latest_date,
                "record_count": row.record_count,
            })

        return coverage

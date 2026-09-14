import datetime
from sqlalchemy import BigInteger, Date, DateTime, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class MarketData(Base):
    """
    Historical OHLCV Market Data record for financial instruments.
    """
    __tablename__ = "market_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    open: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    high: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    low: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    close: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    adj_close: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_market_data_symbol_date"),
    )

    def __repr__(self) -> str:
        return f"<MarketData(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

import datetime
from sqlalchemy import BigInteger, Date, DateTime, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class EngineeredFeatures(Base):
    """
    Persisted technical indicators and engineered features for financial instruments.
    """
    __tablename__ = "engineered_features"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    
    sma_20: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    sma_50: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    ema_20: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    rsi_14: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    macd: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    macd_signal: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    macd_histogram: Mapped[float] = mapped_column(Numeric(14, 4), nullable=True)
    daily_return: Mapped[float] = mapped_column(Numeric(14, 6), nullable=True)
    rolling_volatility: Mapped[float] = mapped_column(Numeric(14, 6), nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_engineered_features_symbol_date"),
    )

    def __repr__(self) -> str:
        return f"<EngineeredFeatures(symbol='{self.symbol}', date='{self.date}', rsi_14={self.rsi_14})>"

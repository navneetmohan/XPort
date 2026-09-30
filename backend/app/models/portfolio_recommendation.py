import datetime
from typing import Any, Dict, Optional
from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class PortfolioRecommendation(Base):
    """
    Persistence model for storing NSGA-II multi-objective portfolio optimization results.
    """
    __tablename__ = "portfolio_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    symbols: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    result_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PortfolioRecommendation(id='{self.id}', status='{self.status}')>"

import logging
import uuid
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.portfolio_recommendation import PortfolioRecommendation

logger = logging.getLogger(__name__)


class RecommendationRepository:
    """
    Data Access Layer for PortfolioRecommendation records.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_recommendation(
        self,
        symbols: Dict[str, Any],
        task_id: Optional[str] = None,
        recommendation_id: Optional[str] = None,
    ) -> PortfolioRecommendation:
        """Create a new portfolio recommendation record in PENDING status."""
        rec_id = recommendation_id or str(uuid.uuid4())
        rec = PortfolioRecommendation(
            id=rec_id,
            task_id=task_id,
            status="PENDING",
            symbols=symbols,
            result_data=None,
        )
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def update_recommendation(
        self,
        recommendation_id: str,
        status: str,
        result_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[PortfolioRecommendation]:
        """Update status and result_data for a recommendation."""
        rec = self.db.scalar(
            select(PortfolioRecommendation).where(PortfolioRecommendation.id == recommendation_id)
        )
        if rec:
            rec.status = status
            if result_data is not None:
                rec.result_data = result_data
            self.db.commit()
            self.db.refresh(rec)
        return rec

    def get_by_id_or_task_id(self, identifier: str) -> Optional[PortfolioRecommendation]:
        """Query recommendation by recommendation ID or Celery task_id."""
        return self.db.scalar(
            select(PortfolioRecommendation).where(
                (PortfolioRecommendation.id == identifier)
                | (PortfolioRecommendation.task_id == identifier)
            )
        )

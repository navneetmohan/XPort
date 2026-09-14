"""Initial database migration baseline

Revision ID: 0001_initial_baseline
Revises: 
Create Date: 2026-09-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Initial baseline migration for XPort.
    Domain entities (User, InvestorProfile, MarketData, EngineeredFeature,
    PortfolioRecommendation, PortfolioAllocation, ExplainabilityResult)
    are scheduled for integration in Stage 4.
    """
    pass


def downgrade() -> None:
    """Revert baseline."""
    pass

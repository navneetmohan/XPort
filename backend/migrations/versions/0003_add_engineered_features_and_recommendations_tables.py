"""Add engineered_features and portfolio_recommendations tables

Revision ID: 0003_add_engineered_features_and_recommendations_tables
Revises: 0002_add_market_data_table
Create Date: 2026-09-30 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0003_add_engineered_features_and_recommendations_tables"
down_revision: Union[str, None] = "0002_add_market_data_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create engineered_features and portfolio_recommendations tables."""
    # Create engineered_features table
    op.create_table(
        "engineered_features",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("sma_20", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("sma_50", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("ema_20", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("rsi_14", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("macd", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("macd_signal", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("macd_histogram", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("daily_return", sa.Numeric(precision=14, scale=6), nullable=True),
        sa.Column("rolling_volatility", sa.Numeric(precision=14, scale=6), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol", "date", name="uq_engineered_features_symbol_date"),
    )
    op.create_index(op.f("ix_engineered_features_symbol"), "engineered_features", ["symbol"], unique=False)
    op.create_index(op.f("ix_engineered_features_date"), "engineered_features", ["date"], unique=False)

    # Create portfolio_recommendations table
    op.create_table(
        "portfolio_recommendations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("symbols", sa.JSON(), nullable=True),
        sa.Column("result_data", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_portfolio_recommendations_task_id"), "portfolio_recommendations", ["task_id"], unique=False)


def downgrade() -> None:
    """Drop engineered_features and portfolio_recommendations tables."""
    op.drop_index(op.f("ix_portfolio_recommendations_task_id"), table_name="portfolio_recommendations")
    op.drop_table("portfolio_recommendations")
    op.drop_index(op.f("ix_engineered_features_date"), table_name="engineered_features")
    op.drop_index(op.f("ix_engineered_features_symbol"), table_name="engineered_features")
    op.drop_table("engineered_features")

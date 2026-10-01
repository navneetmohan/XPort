"""Add asset_class to market_data and ema_50, market_data_id to engineered_features

Revision ID: 0004_add_asset_class_and_ema50
Revises: 0003_add_engineered_features_and_recommendations_tables
Create Date: 2026-10-01 07:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0004_add_asset_class_and_ema50"
down_revision: Union[str, None] = "0003_add_engineered_features_and_recommendations_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add asset_class and new indicator fields."""
    # 1. Add asset_class to market_data table
    op.add_column(
        "market_data",
        sa.Column("asset_class", sa.String(length=50), nullable=True),
    )
    op.create_index(
        op.f("ix_market_data_asset_class"),
        "market_data",
        ["asset_class"],
        unique=False,
    )

    # 2. Add ema_50 and market_data_id to engineered_features table
    op.add_column(
        "engineered_features",
        sa.Column("ema_50", sa.Numeric(precision=14, scale=4), nullable=True),
    )
    op.add_column(
        "engineered_features",
        sa.Column("market_data_id", sa.BigInteger(), nullable=True),
    )
    op.create_index(
        op.f("ix_engineered_features_market_data_id"),
        "engineered_features",
        ["market_data_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_engineered_features_market_data_id",
        "engineered_features",
        "market_data",
        ["market_data_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Revert asset_class and indicator fields."""
    op.drop_constraint(
        "fk_engineered_features_market_data_id",
        "engineered_features",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_engineered_features_market_data_id"),
        table_name="engineered_features",
    )
    op.drop_column("engineered_features", "market_data_id")
    op.drop_column("engineered_features", "ema_50")

    op.drop_index(op.f("ix_market_data_asset_class"), table_name="market_data")
    op.drop_column("market_data", "asset_class")

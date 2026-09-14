"""Add market_data table

Revision ID: 0002_add_market_data_table
Revises: 0001_initial_baseline
Create Date: 2026-09-14 20:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002_add_market_data_table"
down_revision: Union[str, None] = "0001_initial_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create market_data table, indexes, and constraints."""
    op.create_table(
        "market_data",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("high", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("low", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("close", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("adj_close", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("volume", sa.BigInteger(), nullable=True),
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
        sa.UniqueConstraint("symbol", "date", name="uq_market_data_symbol_date"),
    )
    op.create_index(op.f("ix_market_data_symbol"), "market_data", ["symbol"], unique=False)
    op.create_index(op.f("ix_market_data_date"), "market_data", ["date"], unique=False)


def downgrade() -> None:
    """Drop market_data table and indexes."""
    op.drop_index(op.f("ix_market_data_date"), table_name="market_data")
    op.drop_index(op.f("ix_market_data_symbol"), table_name="market_data")
    op.drop_table("market_data")

"""add serving state metadata

Revision ID: b7f1c2d9e4a6
Revises: 0811c4fb3a13
Create Date: 2026-09-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7f1c2d9e4a6"
down_revision: Union[str, Sequence[str], None] = "0811c4fb3a13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("serving_state", sa.JSON(), nullable=True))
    op.add_column("match_sets", sa.Column("serving_state", sa.JSON(), nullable=True))
    op.add_column("match_events", sa.Column("server", sa.String(length=10), nullable=True))


def downgrade() -> None:
    op.drop_column("match_events", "server")
    op.drop_column("match_sets", "serving_state")
    op.drop_column("matches", "serving_state")

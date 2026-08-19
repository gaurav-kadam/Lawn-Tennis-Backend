"""add doubles match support (match_type, player3/4, service_order)

Revision ID: 2a6b7718a2a6
Revises: 158e782f7c3c
Create Date: 2026-08-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a6b7718a2a6'
down_revision: Union[str, Sequence[str], None] = '158e782f7c3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # All new columns are nullable or carry a server_default, so every
    # existing Singles row is backfilled automatically and keeps working
    # exactly as before: match_type='SINGLES', service_order=[], player3/4=NULL.
    # batch_alter_table keeps this portable across MySQL and SQLite.
    with op.batch_alter_table('matches') as batch_op:
        batch_op.add_column(sa.Column('match_type', sa.String(length=10), nullable=False, server_default='SINGLES'))
        batch_op.add_column(sa.Column('player3_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('player4_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('player3_name', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('player4_name', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('service_order', sa.JSON(), nullable=False, server_default='[]'))
        batch_op.create_foreign_key('fk_matches_player3_id_players', 'players', ['player3_id'], ['id'])
        batch_op.create_foreign_key('fk_matches_player4_id_players', 'players', ['player4_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('matches') as batch_op:
        batch_op.drop_constraint('fk_matches_player4_id_players', type_='foreignkey')
        batch_op.drop_constraint('fk_matches_player3_id_players', type_='foreignkey')
        batch_op.drop_column('service_order')
        batch_op.drop_column('player4_name')
        batch_op.drop_column('player3_name')
        batch_op.drop_column('player4_id')
        batch_op.drop_column('player3_id')
        batch_op.drop_column('match_type')

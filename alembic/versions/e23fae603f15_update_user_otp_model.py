"""update_user_otp_model"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = 'e23fae603f15'
down_revision: Union[str, Sequence[str], None] = 'e52000dd3cd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_otp', sa.Column('otp', sa.String(4), nullable=True))
    op.drop_column('user_otp', 'otp_hash')
    op.drop_column('user_otp', 'attempt_count')
    op.alter_column('user_otp', 'otp', existing_type=sa.String(4), nullable=False)


def downgrade() -> None:
    op.add_column('user_otp', sa.Column('otp_hash', mysql.VARCHAR(64), nullable=True))
    op.add_column('user_otp', sa.Column('attempt_count', mysql.INTEGER(), nullable=False, server_default='0'))
    op.drop_column('user_otp', 'otp')
    op.alter_column('user_otp', 'otp_hash', existing_type=mysql.VARCHAR(64), nullable=False)
    op.alter_column('user_otp', 'attempt_count', existing_type=mysql.INTEGER(), server_default=None)
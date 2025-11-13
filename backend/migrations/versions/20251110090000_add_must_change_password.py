"""为用户添加首登改密标记字段

Revision ID: 20251110090000_add_must_change_password
Revises: dc971a6c7670
Create Date: 2025-11-10 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251110090000_add_must_change_password'
down_revision: Union[str, None] = 'dc971a6c7670'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 向 users 表添加 must_change_password 字段，默认 False，非空
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default=sa.false()))
    # 迁移后移除 server_default，仅保留模型层默认
    op.alter_column('users', 'must_change_password', server_default=None)


def downgrade() -> None:
    op.drop_column('users', 'must_change_password')






"""add avatar and bio to users

Revision ID: add_avatar_and_bio
Revises: 30b7fef8bade
Create Date: 2023-07-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_avatar_and_bio'
down_revision = '30b7fef8bade'
branch_labels = None
depends_on = None


def upgrade():
    # 添加avatar和bio字段到users表
    op.add_column('users', sa.Column('avatar', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))


def downgrade():
    # 删除avatar和bio字段
    op.drop_column('users', 'bio')
    op.drop_column('users', 'avatar') 
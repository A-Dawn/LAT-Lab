"""add email verification

Revision ID: 5a7b3e9c4d2f
Revises: add_avatar_and_bio
Create Date: 2023-06-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a7b3e9c4d2f'
down_revision = 'add_avatar_and_bio'
branch_labels = None
depends_on = None


def upgrade():
    # 添加邮箱验证相关字段
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('verification_token', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('token_created_at', sa.DateTime(), nullable=True))
    
    # 将现有用户设置为已验证状态
    op.execute("UPDATE users SET is_verified = 1")


def downgrade():
    # 移除邮箱验证相关字段
    op.drop_column('users', 'token_created_at')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'is_verified') 
"""add article likes table

Revision ID: add_article_likes
Revises: c12271f22ba5
Create Date: 2025-07-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_article_likes'
down_revision = 'plugin_marketplace'
branch_labels = None
depends_on = None


def upgrade():
    # 创建用户-文章点赞关联表
    op.create_table('article_likes',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'article_id')
    )
    
    # 创建索引
    op.create_index(op.f('ix_article_likes_article_id'), 'article_likes', ['article_id'], unique=False)
    op.create_index(op.f('ix_article_likes_user_id'), 'article_likes', ['user_id'], unique=False)


def downgrade():
    # 删除索引
    op.drop_index(op.f('ix_article_likes_user_id'), table_name='article_likes')
    op.drop_index(op.f('ix_article_likes_article_id'), table_name='article_likes')
    
    # 删除表
    op.drop_table('article_likes') 
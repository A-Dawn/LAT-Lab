"""Add plugin marketplace functionality

Revision ID: plugin_marketplace
Revises: c12271f22ba5
Create Date: 2023-11-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'plugin_marketplace'
down_revision: Union[str, None] = 'c12271f22ba5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()

    # 创建插件分类表
    if 'plugin_categories' not in tables:
        op.create_table(
            'plugin_categories',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_plugin_categories_id'), 'plugin_categories', ['id'], unique=False)
        op.create_index(op.f('ix_plugin_categories_name'), 'plugin_categories', ['name'], unique=True)
        
        # 添加预设分类
        op.bulk_insert(
            sa.table(
                'plugin_categories',
                sa.Column('name', sa.String(50)),
                sa.Column('description', sa.Text),
            ),
            [
                {'name': '工具', 'description': '实用工具类插件'},
                {'name': '增强', 'description': '增强博客功能的插件'},
                {'name': '数据分析', 'description': '数据处理和分析类插件'},
                {'name': 'AI 与机器学习', 'description': '人工智能和机器学习相关插件'},
                {'name': '外部集成', 'description': '与外部服务集成的插件'},
                {'name': 'SEO', 'description': '搜索引擎优化相关插件'},
                {'name': '安全', 'description': '安全增强类插件'},
                {'name': '内容展示', 'description': '改进内容展示的插件'},
                {'name': '其他', 'description': '其他类型的插件'},
            ]
        )
    
    # 创建插件标签定义表
    if 'plugin_tag_definitions' not in tables:
        op.create_table(
            'plugin_tag_definitions',
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint('name')
        )
        
        # 添加预设标签
        op.bulk_insert(
            sa.table(
                'plugin_tag_definitions',
                sa.Column('name', sa.String(50)),
            ),
            [
                {'name': 'ai'},
                {'name': 'seo'},
                {'name': '数据可视化'},
                {'name': '文件管理'},
                {'name': '社交媒体'},
                {'name': '安全'},
                {'name': '性能优化'},
                {'name': '内容处理'},
                {'name': 'UI增强'},
                {'name': '工具'},
            ]
        )
    
    # 创建插件与标签的多对多关系表
    if 'plugin_tags' not in tables:
        op.create_table(
            'plugin_tags',
            sa.Column('plugin_id', sa.Integer(), nullable=False),
            sa.Column('tag_name', sa.String(length=50), nullable=False),
            sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['tag_name'], ['plugin_tag_definitions.name'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('plugin_id', 'tag_name')
        )
    
    # 创建插件评论表
    if 'plugin_reviews' not in tables:
        op.create_table(
            'plugin_reviews',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('plugin_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('rating', sa.Integer(), nullable=False),
            sa.Column('comment', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_plugin_reviews_id'), 'plugin_reviews', ['id'], unique=False)
    
    # 为已有的插件表添加新字段
    with op.batch_alter_table('plugins') as batch_op:
        # 检查列是否已存在
        columns = [col['name'] for col in inspector.get_columns('plugins')]
        
        if 'version' not in columns:
            batch_op.add_column(sa.Column('version', sa.String(length=20), server_default='0.1.0', nullable=True))
        if 'category_id' not in columns:
            batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        if 'downloads' not in columns:
            batch_op.add_column(sa.Column('downloads', sa.Integer(), server_default='0', nullable=True))
        if 'rating' not in columns:
            batch_op.add_column(sa.Column('rating', sa.Float(), server_default='0.0', nullable=True))
        if 'ratings_count' not in columns:
            batch_op.add_column(sa.Column('ratings_count', sa.Integer(), server_default='0', nullable=True))
        if 'config_schema' not in columns:
            batch_op.add_column(sa.Column('config_schema', sa.Text(), nullable=True))
        if 'is_public' not in columns:
            batch_op.add_column(sa.Column('is_public', sa.Boolean(), server_default='true', nullable=True))
        if 'featured' not in columns:
            batch_op.add_column(sa.Column('featured', sa.Boolean(), server_default='false', nullable=True))
        if 'icon' not in columns:
            batch_op.add_column(sa.Column('icon', sa.Text(), nullable=True))
        if 'repository_url' not in columns:
            batch_op.add_column(sa.Column('repository_url', sa.String(length=255), nullable=True))
        if 'dependency_info' not in columns:
            batch_op.add_column(sa.Column('dependency_info', sa.Text(), nullable=True))
        
        # 添加外键，如果不存在
        foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('plugins')]
        if 'fk_plugins_category_id' not in foreign_keys:
            batch_op.create_foreign_key('fk_plugins_category_id', 'plugin_categories', ['category_id'], ['id'])


def downgrade():
    # 移除插件表的新字段
    with op.batch_alter_table('plugins') as batch_op:
        batch_op.drop_constraint('fk_plugins_category_id', type_='foreignkey')
        batch_op.drop_column('dependency_info')
        batch_op.drop_column('repository_url')
        batch_op.drop_column('icon')
        batch_op.drop_column('featured')
        batch_op.drop_column('is_public')
        batch_op.drop_column('config_schema')
        batch_op.drop_column('ratings_count')
        batch_op.drop_column('rating')
        batch_op.drop_column('downloads')
        batch_op.drop_column('category_id')
        batch_op.drop_column('version')
    
    # 删除插件评论表
    op.drop_index(op.f('ix_plugin_reviews_id'), table_name='plugin_reviews')
    op.drop_table('plugin_reviews')
    
    # 删除插件标签关系表
    op.drop_table('plugin_tags')
    
    # 删除标签定义表
    op.drop_table('plugin_tag_definitions')
    
    # 删除分类表
    op.drop_index(op.f('ix_plugin_categories_name'), table_name='plugin_categories')
    op.drop_index(op.f('ix_plugin_categories_id'), table_name='plugin_categories')
    op.drop_table('plugin_categories') 
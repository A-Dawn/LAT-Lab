#!/usr/bin/env python3
"""
LAT-LAB 数据库初始化脚本
用于初始化数据库和创建示例数据
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from src.lat_lab.core.database import SessionLocal, engine, Base
from src.lat_lab.core.security import get_password_hash
from src.lat_lab.models import user, article, category, comment, tag, plugin

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """创建所有数据库表"""
    logger.info("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")


def create_admin_user():
    """创建管理员用户"""
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin = db.query(user.User).filter(user.User.username == "admin").first()
        if admin:
            logger.info("管理员用户已存在")
            return
        
        # 创建管理员用户
        admin_user = user.User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_verified=True,
            bio="系统管理员",
        )
        
        db.add(admin_user)
        db.commit()
        logger.info("管理员用户创建成功")
    
    except Exception as e:
        logger.error(f"创建管理员失败: {e}")
        db.rollback()
    finally:
        db.close()


def create_example_categories():
    """创建示例分类"""
    db = SessionLocal()
    try:
        # 检查是否已有分类
        cats = db.query(category.Category).count()
        if cats > 0:
            logger.info(f"已存在 {cats} 个分类")
            return
        
        # 创建示例分类
        categories = [
            category.Category(name="技术", description="技术相关文章"),
            category.Category(name="生活", description="生活随笔"),
            category.Category(name="旅行", description="旅行见闻"),
            category.Category(name="阅读", description="读书笔记"),
        ]
        
        db.add_all(categories)
        db.commit()
        logger.info("示例分类创建成功")
    
    except Exception as e:
        logger.error(f"创建示例分类失败: {e}")
        db.rollback()
    finally:
        db.close()


def create_example_tags():
    """创建示例标签"""
    db = SessionLocal()
    try:
        # 检查是否已有标签
        tags_count = db.query(tag.Tag).count()
        if tags_count > 0:
            logger.info(f"已存在 {tags_count} 个标签")
            return
        
        # 创建示例标签
        tags = [
            tag.Tag(name="Python"),
            tag.Tag(name="FastAPI"),
            tag.Tag(name="SQLite"),
            tag.Tag(name="前端"),
            tag.Tag(name="后端"),
            tag.Tag(name="Vue"),
            tag.Tag(name="旅行"),
            tag.Tag(name="读书"),
        ]
        
        db.add_all(tags)
        db.commit()
        logger.info("示例标签创建成功")
    
    except Exception as e:
        logger.error(f"创建示例标签失败: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """主函数"""
    logger.info("开始初始化数据库...")
    
    # 创建数据库表
    create_tables()
    
    # 创建管理员用户
    create_admin_user()
    
    # 创建示例数据
    create_example_categories()
    create_example_tags()
    
    logger.info("数据库初始化完成")


if __name__ == "__main__":
    main() 
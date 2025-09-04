#!/usr/bin/env python3
"""
LAT-LAB MySQL数据库初始化脚本
用于Docker部署方式，专门处理MySQL数据库
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.lat_lab.core.database import engine, Base, SessionLocal
from src.lat_lab.core.security import get_password_hash

# 导入所有模型以确保它们被注册到Base.metadata
from src.lat_lab.models import user, article, category, comment, tag, plugin, system

# 确保所有模型都被导入
logger.info("已导入的模型:")
logger.info(f"  - user: {user}")
logger.info(f"  - article: {article}")
logger.info(f"  - category: {category}")
logger.info(f"  - comment: {comment}")
logger.info(f"  - tag: {tag}")
logger.info(f"  - plugin: {plugin}")
logger.info(f"  - system: {system}")


def create_mysql_tables():
    """创建MySQL数据库表"""
    logger.info("创建MySQL数据库表...")
    try:
        # 检查数据库连接
        logger.info(f"数据库引擎: {engine}")
        logger.info(f"数据库URL: {engine.url}")
        
        # 检查Base.metadata中的表
        logger.info(f"Base.metadata中的表: {list(Base.metadata.tables.keys())}")
        
        # 使用engine直接创建表
        Base.metadata.create_all(bind=engine)
        logger.info("MySQL数据库表创建完成")
        
        # 验证表是否真的创建成功
        with engine.connect() as conn:
            # 检查关键表是否存在
            result = conn.execute("SHOW TABLES")
            tables = [row[0] for row in result]
            logger.info(f"已创建的表: {tables}")
            
            if 'users' in tables and 'categories' in tables:
                logger.info("关键表创建成功")
                return True
            else:
                logger.error("关键表创建失败")
                return False
                
    except Exception as e:
        logger.error(f"创建MySQL数据库表失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return False


def wait_for_mysql_tables():
    """等待MySQL表创建完成"""
    logger.info("等待MySQL表创建完成...")
    import time
    max_attempts = 15
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            with engine.connect() as conn:
                # 尝试查询一个简单的表
                result = conn.execute("SELECT COUNT(*) FROM users")
                count = result.scalar()
                logger.info(f"表创建完成，users表中有 {count} 条记录")
                return True
        except Exception as e:
            if attempt == max_attempts:
                logger.error(f"等待表创建超时: {e}")
                return False
            logger.info(f"表尚未就绪，等待 2 秒后重试... (第 {attempt} 次)")
            time.sleep(2)
            attempt += 1
    
    return False


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
            role=user.RoleEnum.admin,
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
            tag.Tag(name="MySQL"),
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
    logger.info("开始MySQL数据库初始化...")
    
    # 创建表
    if not create_mysql_tables():
        logger.error("创建MySQL数据库表失败")
        sys.exit(1)
    
    # 等待表创建完成
    if not wait_for_mysql_tables():
        logger.error("等待表创建超时")
        sys.exit(1)
    
    # 初始化数据
    create_admin_user()
    create_example_categories()
    create_example_tags()
    
    logger.info("MySQL数据库初始化完成")


if __name__ == "__main__":
    main() 
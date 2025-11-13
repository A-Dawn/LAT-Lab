#!/usr/bin/env python3
"""
LAT-LAB 数据库初始化脚本
用于初始化数据库和创建示例数据
"""
import os
import sys
import logging
from pathlib import Path
from sqlalchemy import text

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from src.lat_lab.core.database import SessionLocal, engine, Base
from src.lat_lab.core.security import get_password_hash

# 导入所有模型以确保它们被注册到Base.metadata
from src.lat_lab.models import user, article, category, comment, tag, plugin, system

# 避免在日志中输出敏感或冗余内容，仅记录必要信息
logger.info("模型模块已加载")


def create_tables():
    """创建所有数据库表"""
    logger.info("创建数据库表...")
    try:
        # 使用engine直接创建表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建完成")
        
        # 验证表是否真的创建成功
        with engine.connect() as conn:
            # 检查关键表是否存在
            try:
                result = conn.execute(text("SELECT 1 FROM users LIMIT 1"))
                logger.info("关键表创建成功")
                return True
            except Exception:
                logger.error("关键表创建失败")
                return False
                
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return False


def wait_for_tables():
    """等待表创建完成"""
    logger.info("等待表创建完成...")
    import time
    max_attempts = 15
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            with engine.connect() as conn:
                # 尝试查询一个简单的表
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
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
    """基于环境变量创建管理员用户（受控、幂等、无敏感日志）
    
    环境变量：
      - ADMIN_ENABLED: 'true'/'false'（默认 false）
      - ADMIN_USERNAME: 管理员用户名（默认 'admin'）
      - ADMIN_EMAIL: 管理员邮箱（默认 'admin@example.com'）
      - ADMIN_PASSWORD: 管理员密码（必须在启用创建时提供）
    仅当 ADMIN_ENABLED=true 且数据库中不存在任何管理员时才创建。
    """
    admin_enabled = os.getenv("ADMIN_ENABLED", "false").lower() == "true"
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_enabled:
        logger.info("默认管理员创建已禁用（ADMIN_ENABLED=false）")
        return

    if not admin_password:
        logger.error("已启用默认管理员创建，但未提供 ADMIN_PASSWORD，操作中止")
        return

    db = SessionLocal()
    try:
        # 检查是否已存在任何管理员
        existing_admin = db.query(user.User).filter(user.User.role == user.RoleEnum.admin).first()
        if existing_admin:
            logger.info("检测到管理员用户，跳过默认管理员创建")
            return
        
        # 创建管理员用户
        admin_user = user.User(
            username=admin_username,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            role=user.RoleEnum.admin,
            is_verified=True,
            must_change_password=True,
            bio="系统管理员",
        )
        
        db.add(admin_user)
        db.commit()
        logger.info("管理员用户创建成功（已设置首登改密标记）")
    
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
    logger.info("开始数据库初始化...")
    
    # 创建表
    if not create_tables():
        logger.error("创建数据库表失败")
        sys.exit(1)
    
    # 等待表创建完成
    if not wait_for_tables():
        logger.error("等待表创建超时")
        sys.exit(1)
    
    # 初始化数据
    create_admin_user()
    create_example_categories()
    create_example_tags()
    # create_example_articles()  # 暂时注释掉，避免错误
    # create_example_comments()  # 暂时注释掉，避免错误
    # create_example_plugins()   # 暂时注释掉，避免错误
    
    logger.info("数据库初始化完成")


if __name__ == "__main__":
    main() 
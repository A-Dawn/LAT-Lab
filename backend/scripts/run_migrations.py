#!/usr/bin/env python3
"""
LAT-LAB 数据库迁移脚本
用于运行数据库迁移
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from src.lat_lab.core.database import engine, Base
from src.lat_lab.models import user, article, category, comment, tag, plugin, system

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """创建所有数据库表"""
    logger.info("创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建完成")
        return True
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("开始数据库迁移...")
    
    if create_tables():
        logger.info("数据库迁移成功完成")
    else:
        logger.error("数据库迁移失败")
        sys.exit(1)


if __name__ == "__main__":
    main() 
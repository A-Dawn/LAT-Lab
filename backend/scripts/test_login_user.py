#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录用户脚本
尝试使用与应用相同的验证方式进行登录测试
"""

import os
import sys
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import logging

# 添加项目根目录到路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.lat_lab.core.config import settings
from src.lat_lab.models.user import User

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 密码哈希器 - 与应用使用相同配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配哈希"""
    return pwd_context.verify(plain_password, hashed_password)

def create_db_session():
    """创建数据库连接和会话"""
    db_uri = settings.SQLALCHEMY_DATABASE_URI
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    return Session()

def test_login(username, password):
    """测试用户登录"""
    try:
        # 创建数据库会话
        session = create_db_session()
        
        # 通过用户名获取用户
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            logger.error(f"用户 '{username}' 不存在")
            return False
            
        # 验证密码
        if not verify_password(password, user.hashed_password):
            logger.error(f"密码验证失败")
            logger.debug(f"存储的密码哈希: {user.hashed_password}")
            return False
            
        # 检查用户是否已验证邮箱
        if not user.is_verified:
            logger.warning(f"用户存在但邮箱未验证")
            return False
            
        logger.info(f"登录成功！用户ID: {user.id}, 角色: {user.role}")
        return True
        
    except Exception as e:
        logger.error(f"登录测试失败: {str(e)}")
        return False
    finally:
        # 关闭会话
        if 'session' in locals():
            session.close()

def main():
    parser = argparse.ArgumentParser(description="测试用户登录")
    parser.add_argument("-u", "--username", help="用户名")
    parser.add_argument("-p", "--password", help="密码")
    args = parser.parse_args()
    
    # 获取用户名和密码
    username = args.username
    if not username:
        username = input("请输入用户名: ")
    
    password = args.password
    if not password:
        import getpass
        password = getpass.getpass("请输入密码: ")
    
    # 测试登录
    success = test_login(username, password)
    
    if success:
        logger.info("登录测试成功")
        sys.exit(0)
    else:
        logger.error("登录测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 
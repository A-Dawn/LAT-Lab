#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建用户脚本
支持创建管理员或普通用户，直接写入数据库
"""

import os
import sys
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import secrets
import string
from datetime import datetime, timedelta
import logging
import getpass

# 添加项目根目录到路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.lat_lab.models.user import User, RoleEnum
from src.lat_lab.core.config import settings
from src.lat_lab.core.database import Base

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 密码哈希器
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    使用与应用相同的算法生成密码哈希
    """
    return pwd_context.hash(password)

def generate_verification_token(length=64):
    """生成随机验证令牌"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_user(session, username, email, password, is_admin=False, is_verified=True):
    """
    创建用户
    :param session: 数据库会话
    :param username: 用户名
    :param email: 邮箱
    :param password: 密码
    :param is_admin: 是否为管理员，默认为False
    :param is_verified: 是否已验证邮箱，默认为True
    :return: 创建的用户对象
    """
    # 检查用户名是否已存在
    existing_user = session.query(User).filter(User.username == username).first()
    if existing_user:
        logger.error(f"用户名 '{username}' 已存在")
        sys.exit(1)
    
    # 检查邮箱是否已存在
    existing_email = session.query(User).filter(User.email == email).first()
    if existing_email:
        logger.error(f"邮箱 '{email}' 已被注册")
        sys.exit(1)
    
    # 生成哈希密码
    hashed_password = get_password_hash(password)
    
    # 确定角色
    role = RoleEnum.admin if is_admin else RoleEnum.user
    
    # 生成验证令牌
    verification_token = generate_verification_token() if not is_verified else None
    
    # 创建用户对象
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role,
        is_verified=is_verified,
        verification_token=verification_token,
        token_created_at=datetime.now() if not is_verified else None
    )
    
    # 保存到数据库
    session.add(user)
    session.commit()
    logger.info(f"用户 '{username}' 创建成功，用户ID: {user.id}")
    return user

def create_db_session():
    """创建数据库连接和会话"""
    db_uri = settings.SQLALCHEMY_DATABASE_URI
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    return Session()

def check_user_count(session):
    """检查数据库中的用户数量"""
    count = session.query(User).count()
    logger.info(f"当前数据库中有 {count} 个用户")
    return count

def validate_input(username, email, password):
    """验证输入参数"""
    # 检查用户名
    if len(username) < 3:
        logger.error("用户名至少需要3个字符")
        sys.exit(1)
        
    # 检查邮箱
    if '@' not in email or '.' not in email:
        logger.error("请输入有效的邮箱地址")
        sys.exit(1)
        
    # 检查密码
    if len(password) < 6:
        logger.error("密码至少需要6个字符")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="创建用户脚本")
    parser.add_argument("-u", "--username", help="用户名")
    parser.add_argument("-e", "--email", help="邮箱")
    parser.add_argument("-p", "--password", help="密码（不推荐通过命令行传递，留空将提示输入）")
    parser.add_argument("-a", "--admin", action="store_true", help="创建管理员用户")
    parser.add_argument("--not-verified", action="store_true", help="标记用户为未验证状态（默认已验证）")
    args = parser.parse_args()
    
    logger.info("开始创建用户...")
    
    # 交互式获取缺少的参数
    username = args.username
    email = args.email
    password = args.password
    is_admin = args.admin
    is_verified = not args.not_verified
    
    if not username:
        username = input("请输入用户名: ")
    
    if not email:
        email = input("请输入邮箱: ")
    
    if not password:
        password = getpass.getpass("请输入密码: ")
        confirm_password = getpass.getpass("请再次输入密码: ")
        if password != confirm_password:
            logger.error("两次密码输入不一致")
            sys.exit(1)
    
    # 验证输入参数
    validate_input(username, email, password)
    
    # 角色显示
    role_text = "管理员" if is_admin else "普通用户"
    verification_status = "已验证" if is_verified else "未验证"
    
    # 确认信息
    print(f"\n即将创建以下用户:")
    print(f"用户名: {username}")
    print(f"邮箱: {email}")
    print(f"角色: {role_text}")
    print(f"验证状态: {verification_status}")
    
    # 二次确认
    confirm = input("\n确认创建? (y/n): ")
    if confirm.lower() != 'y':
        logger.info("操作已取消")
        sys.exit(0)
    
    try:
        # 创建数据库会话
        session = create_db_session()
        
        # 检查用户数量
        user_count = check_user_count(session)
        
        # 如果没有用户，且未指定创建管理员，提醒用户
        if user_count == 0 and not is_admin:
            logger.warning("数据库中没有用户，建议创建管理员账户")
            create_admin = input("是否创建为管理员账户? (y/n): ")
            if create_admin.lower() == 'y':
                is_admin = True
        
        # 创建用户
        user = create_user(session, username, email, password, is_admin, is_verified)
        
        # 成功信息
        role_text = "管理员" if user.role == RoleEnum.admin else "普通用户"
        logger.info(f"成功创建{role_text} {username} (ID: {user.id})")
        
    except Exception as e:
        logger.error(f"创建用户失败: {str(e)}")
        sys.exit(1)
    finally:
        # 关闭会话
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main() 
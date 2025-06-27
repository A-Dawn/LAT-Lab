#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建管理员用户脚本

此脚本用于为LAT-Lab系统创建管理员用户
使用方法: python setup_tools/create_admin_user.py [username] [email] [password]
"""

import os
import sys
import sqlite3
import datetime
from passlib.context import CryptContext
import pathlib

# 密码哈希配置，必须与app/core/security.py中保持一致
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_admin_user(username, email, password):
    """创建管理员用户"""
    # 获取脚本所在目录
    script_dir = pathlib.Path(__file__).parent.resolve()
    # 数据库路径 (相对于后端根目录)
    db_path = os.path.join(script_dir, "..", "blog.db")
    
    # 检查数据库是否存在
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件 {db_path} 不存在")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查用户是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"错误: 用户名 '{username}' 或邮箱 '{email}' 已存在")
            conn.close()
            return False
        
        # 生成密码哈希
        hashed_password = get_password_hash(password)
        
        # 查看users表的结构
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 准备插入数据的字段和值
        fields = ["username", "email", "hashed_password", "role", "is_verified"]
        values = [username, email, hashed_password, "admin", 1]
        
        # 如果表中有created_at和updated_at字段，添加当前时间
        if "created_at" in columns:
            fields.append("created_at")
            values.append(datetime.datetime.now().isoformat())
            
        if "updated_at" in columns:
            fields.append("updated_at")
            values.append(datetime.datetime.now().isoformat())
        
        # 构建SQL插入语句
        placeholders = ", ".join(["?" for _ in fields])
        fields_str = ", ".join(fields)
        
        # 执行插入操作
        cursor.execute(
            f"INSERT INTO users ({fields_str}) VALUES ({placeholders})",
            values
        )
        
        # 提交事务
        conn.commit()
        
        # 获取用户ID
        user_id = cursor.lastrowid
        print(f"成功创建管理员用户! ID: {user_id}, 用户名: {username}, 电子邮箱: {email}")
        print("现在您可以使用这个管理员账户登录LAT-Lab博客系统了。")
        
        # 关闭连接
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False

def main():
    """主函数"""
    print("="*50)
    print("LAT-Lab 博客系统 - 创建管理员用户")
    print("="*50)
    print()
    
    # 处理命令行参数
    if len(sys.argv) == 4:
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
    else:
        # 交互模式
        username = input("请输入管理员用户名: ")
        email = input("请输入管理员电子邮箱: ")
        password = input("请输入管理员密码: ")
    
    # 验证输入
    if not username or not email or not password:
        print("错误: 用户名、电子邮箱和密码不能为空")
        return
    
    # 创建管理员用户
    create_admin_user(username, email, password)

if __name__ == "__main__":
    main() 
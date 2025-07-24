#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试安全修复验证脚本
用于验证敏感数据安全存储和密码安全传输的修复是否有效
"""

import os
import sys
import requests
import json
import hashlib
import base64
from urllib.parse import urljoin
import argparse

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# 默认配置
DEFAULT_API_BASE = "http://localhost:8000"

def setup_args():
    """设置命令行参数"""
    parser = argparse.ArgumentParser(description='测试安全修复')
    parser.add_argument('--api', default=DEFAULT_API_BASE, help='API基础URL')
    parser.add_argument('--username', default='admin', help='用于测试的用户名')
    parser.add_argument('--password', default='admin123', help='用于测试的密码')
    parser.add_argument('--article-id', type=int, help='要测试的密码保护文章ID')
    parser.add_argument('--article-password', help='文章的访问密码')
    
    return parser.parse_args()

def get_token(api_base, username, password):
    """获取认证令牌"""
    auth_url = urljoin(api_base, "/api/auth/login")
    
    # 使用x-www-form-urlencoded格式，模拟表单提交
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(
            auth_url, 
            data=data,
            headers=headers
        )
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"登录失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"登录请求异常: {str(e)}")
        return None

def test_password_hash_auth(api_base, token, article_id, article_password):
    """测试密码哈希认证"""
    if not article_id or not article_password:
        print("跳过密码哈希认证测试：未提供文章ID或密码")
        return False
        
    print(f"\n测试密码保护文章访问 (ID: {article_id})")
    
    article_url = urljoin(api_base, f"/api/articles/{article_id}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试1: 不提供密码 - 应该失败
    print("\n测试1: 不提供密码...")
    response = requests.get(article_url, headers=headers)
    if response.status_code == 403:
        print("✅ 测试1通过: 无密码访问被正确拒绝")
    else:
        print(f"❌ 测试1失败: 应返回403，实际返回{response.status_code}")
        print(f"响应内容: {response.text}")
        return False
    
    # 测试2: 使用明文密码 - 应该成功
    print("\n测试2: 使用明文密码...")
    params = {"password": article_password}
    response = requests.get(article_url, headers=headers, params=params)
    if response.status_code == 200:
        print("✅ 测试2通过: 明文密码访问成功")
    else:
        print(f"❌ 测试2失败: 应返回200，实际返回{response.status_code}")
        print(f"响应内容: {response.text}")
        return False
        
    # 测试3: 使用客户端哈希 - 应该成功
    print("\n测试3: 使用客户端哈希...")
    # 计算密码的SHA-256哈希
    password_hash = hashlib.sha256(article_password.encode()).digest()
    password_hash_b64 = base64.b64encode(password_hash).decode()
    
    params = {
        "password_hash": password_hash_b64,
        "client_hash": "true"  # 注意：查询参数中布尔值需要是字符串
    }
    
    response = requests.get(article_url, headers=headers, params=params)
    if response.status_code == 200:
        print("✅ 测试3通过: 客户端哈希验证成功")
        article_data = response.json()
        print(f"文章标题: {article_data.get('title')}")
        return True
    else:
        print(f"❌ 测试3失败: 应返回200，实际返回{response.status_code}")
        print(f"响应内容: {response.text}")
        return False

def main():
    """主函数"""
    args = setup_args()
    
    print("LAT-Lab 安全修复验证脚本")
    print(f"API基础URL: {args.api}")
    
    # 获取认证令牌
    print("\n获取认证令牌...")
    token = get_token(args.api, args.username, args.password)
    
    if not token:
        print("❌ 获取令牌失败，无法继续测试")
        sys.exit(1)
    
    print("✅ 认证成功")
    
    # 测试密码哈希认证
    test_password_hash_auth(args.api, token, args.article_id, args.article_password)
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 
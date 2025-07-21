#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用requests库测试API
"""

import requests
import json
import sys

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api"

def print_response(response):
    """打印响应信息"""
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    try:
        data = response.json()
        print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"响应内容: {response.text}")

def test_marketplace_info():
    """测试市场信息API"""
    print("\n" + "="*50)
    print("测试市场信息API")
    print("="*50)
    
    url = f"{BASE_URL}/plugins/marketplace/info"
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response)
    except Exception as e:
        print(f"请求失败: {str(e)}")

def test_marketplace_plugins(featured=None):
    """测试插件列表API"""
    print("\n" + "="*50)
    print(f"测试插件列表API (featured={featured})")
    print("="*50)
    
    url = f"{BASE_URL}/plugins/marketplace/plugins"
    if featured is not None:
        url += f"?featured={str(featured).lower()}"
    
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response)
    except Exception as e:
        print(f"请求失败: {str(e)}")

def test_marketplace_categories():
    """测试分类列表API"""
    print("\n" + "="*50)
    print("测试分类列表API")
    print("="*50)
    
    url = f"{BASE_URL}/plugins/marketplace/categories"
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response)
    except Exception as e:
        print(f"请求失败: {str(e)}")

def test_marketplace_tags():
    """测试标签列表API"""
    print("\n" + "="*50)
    print("测试标签列表API")
    print("="*50)
    
    url = f"{BASE_URL}/plugins/marketplace/tags"
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response)
    except Exception as e:
        print(f"请求失败: {str(e)}")

def main():
    """主函数"""
    print("开始测试API...")
    
    # 测试市场信息
    test_marketplace_info()
    
    # 测试插件列表
    test_marketplace_plugins()
    test_marketplace_plugins(featured=True)
    test_marketplace_plugins(featured=False)
    
    # 测试分类和标签
    test_marketplace_categories()
    test_marketplace_tags()

if __name__ == "__main__":
    main() 
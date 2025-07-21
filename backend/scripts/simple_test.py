#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试API并格式化输出
"""

import requests
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api"

def test_api(endpoint):
    """测试API并格式化输出"""
    url = f"{BASE_URL}{endpoint}"
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {str(e)}")

if __name__ == "__main__":
    # 测试市场信息API
    print("\n=== 测试市场信息API ===")
    test_api("/plugins/marketplace/info")
    
    # 测试精选插件API
    print("\n=== 测试精选插件API ===")
    test_api("/plugins/marketplace/plugins?featured=true")
    
    # 测试非精选插件API
    print("\n=== 测试非精选插件API ===")
    test_api("/plugins/marketplace/plugins?featured=false") 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试插件市场API功能
"""

import os
import sys
import json

# 将项目根目录添加到路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.lat_lab.api.marketplace import get_marketplace_info, get_plugins, MarketplaceInfo
from src.lat_lab.services.marketplace import marketplace_service

def main():
    """测试插件市场API功能"""
    print("\n" + "="*50)
    print("插件市场API测试")
    print("="*50)
    
    # 测试市场信息API
    print("\n测试市场信息API:")
    try:
        # 这里我们直接调用API函数，而不是通过HTTP请求
        # 实际中FastAPI会自动处理依赖注入，这里我们跳过了用户认证部分
        info = marketplace_service.get_marketplace_info()
        print(f"原始市场信息: {json.dumps(info, indent=2)}")
        
        # 验证能否创建Pydantic模型
        info_model = MarketplaceInfo(**info)
        print(f"验证后市场信息: {info_model}")
    except Exception as e:
        print(f"获取市场信息失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    # 测试插件列表API
    print("\n测试插件列表API:")
    try:
        # 获取精选插件
        featured_plugins = marketplace_service.get_plugins(featured=True)
        print(f"精选插件数量: {len(featured_plugins)}")
        
        # 获取非精选插件
        non_featured_plugins = marketplace_service.get_plugins(featured=False)
        print(f"非精选插件数量: {len(non_featured_plugins)}")
        
        # 总数应该等于全部插件
        all_plugins = marketplace_service.get_plugins()
        print(f"全部插件数量: {len(all_plugins)}")
        assert len(featured_plugins) + len(non_featured_plugins) == len(all_plugins)
        print("数量验证通过")
    except Exception as e:
        print(f"获取插件列表失败: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 
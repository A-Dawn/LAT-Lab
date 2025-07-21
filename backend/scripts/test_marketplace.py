#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试插件市场功能
"""

import os
import sys
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 将项目根目录添加到路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.lat_lab.services.marketplace import marketplace_service
from src.lat_lab.core.config import settings

def main():
    """测试插件市场功能"""
    print("\n" + "="*50)
    print("插件市场测试")
    print("="*50)
    
    # 显示配置信息
    print("\n配置信息:")
    print(f"插件市场数据源: {settings.PLUGIN_MARKETPLACE_SOURCE}")
    print(f"本地配置文件路径: {settings.PLUGIN_MARKETPLACE_LOCAL_PATH}")
    print(f"配置文件是否存在: {os.path.exists(settings.PLUGIN_MARKETPLACE_LOCAL_PATH)}")
    
    # 尝试直接读取配置文件
    print("\n尝试直接读取配置文件:")
    try:
        config_path = os.path.abspath(settings.PLUGIN_MARKETPLACE_LOCAL_PATH)
        print(f"绝对路径: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"成功读取配置文件")
            print(f"版本: {data.get('marketplace_info', {}).get('version')}")
            print(f"插件数量: {len(data.get('plugins', []))}")
            print(f"分类数量: {len(data.get('categories', []))}")
    except Exception as e:
        print(f"读取失败: {str(e)}")
    
    # 通过服务获取数据
    print("\n通过服务获取插件市场数据:")
    try:
        data = marketplace_service.get_marketplace_data(force_refresh=True)
        print(f"通过服务获取数据{'成功' if data else '失败'}")
        if data:
            info = data.get('marketplace_info', {})
            plugins = data.get('plugins', [])
            categories = data.get('categories', [])
            print(f"市场信息: {info}")
            print(f"插件数量: {len(plugins)}")
            print(f"分类数量: {len(categories)}")
    except Exception as e:
        print(f"服务获取失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    # 测试筛选功能
    print("\n测试插件筛选功能:")
    try:
        # 获取精选插件
        featured_plugins = marketplace_service.get_plugins(featured=True)
        print(f"精选插件数量: {len(featured_plugins)}")
        for plugin in featured_plugins:
            print(f"- {plugin.get('name')} (ID: {plugin.get('id')})")
        
        # 获取标签
        tags = marketplace_service.get_tags()
        print(f"\n标签列表: {tags}")
        
        # 获取分类
        categories = marketplace_service.get_categories()
        print(f"\n分类列表:")
        for category in categories:
            print(f"- {category.get('name')} (ID: {category.get('id')})")
    except Exception as e:
        print(f"筛选测试失败: {str(e)}")

if __name__ == "__main__":
    main() 
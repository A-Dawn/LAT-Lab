#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试从Git仓库获取插件的功能
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
    """测试从Git仓库获取插件的功能"""
    print("\n" + "="*50)
    print("测试从Git仓库获取插件")
    print("="*50)
    
    # 保存原始设置
    original_source = settings.PLUGIN_MARKETPLACE_SOURCE
    original_repo = settings.PLUGIN_MARKETPLACE_GIT_REPO
    
    try:
        # 显示当前设置
        print("\n当前设置:")
        current_settings = marketplace_service.get_source_settings()
        print(json.dumps(current_settings, indent=2))
        
        # 切换到Git仓库源
        git_repo = "https://github.com/A-Dawn/LAT-Lab-marketplace"
        print(f"\n切换到Git仓库源: {git_repo}")
        
        updated_settings = marketplace_service.update_source_settings(
            source="git",
            git_repo=git_repo
        )
        print("更新后的设置:")
        print(json.dumps(updated_settings, indent=2))
        
        # 获取插件列表
        print("\n获取插件列表:")
        data = marketplace_service.get_marketplace_data(force_refresh=True)
        
        if not data:
            print("获取插件市场数据失败")
            return
        
        # 显示市场信息
        print("\n市场信息:")
        print(json.dumps(data.get("marketplace_info", {}), indent=2))
        
        # 显示插件列表
        plugins = data.get("plugins", [])
        print(f"\n找到 {len(plugins)} 个插件:")
        
        for i, plugin in enumerate(plugins, 1):
            print(f"\n插件 {i}: {plugin.get('name')} (ID: {plugin.get('id')})")
            print(f"  描述: {plugin.get('description')}")
            print(f"  版本: {plugin.get('version')}")
            print(f"  作者: {plugin.get('author')}")
            print(f"  标签: {', '.join(plugin.get('tags', []))}")
        
        # 测试筛选功能
        featured_plugins = marketplace_service.get_plugins(featured=True)
        print(f"\n精选插件数量: {len(featured_plugins)}")
        
        # 测试搜索功能
        if plugins:
            # 使用第一个插件名称的一部分作为搜索词
            search_term = plugins[0].get('name', '').split()[0]
            search_results = marketplace_service.get_plugins(search_term=search_term)
            print(f"\n搜索 '{search_term}' 的结果: {len(search_results)} 个插件")
    
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    finally:
        # 恢复原始设置
        print("\n恢复原始设置")
        marketplace_service.update_source_settings(
            source=original_source,
            git_repo=original_repo
        )
        
        # 验证设置已恢复
        restored_settings = marketplace_service.get_source_settings()
        print("恢复后的设置:")
        print(json.dumps(restored_settings, indent=2))

if __name__ == "__main__":
    main() 
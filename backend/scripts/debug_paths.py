#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试路径问题
"""

import os
import sys
from pathlib import Path

# 将项目根目录添加到路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.lat_lab.core.config import settings, BASE_DIR

def main():
    """调试路径问题"""
    print("\n" + "="*50)
    print("路径调试")
    print("="*50)
    
    print(f"\n当前工作目录: {os.getcwd()}")
    print(f"脚本目录: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"项目根目录 (BASE_DIR): {BASE_DIR}")
    
    print("\n插件市场配置:")
    print(f"PLUGIN_MARKETPLACE_CONFIG: {settings.PLUGIN_MARKETPLACE_CONFIG}")
    print(f"PLUGIN_MARKETPLACE_LOCAL_PATH: {settings.PLUGIN_MARKETPLACE_LOCAL_PATH}")
    
    # 检查文件是否存在
    config_path = settings.PLUGIN_MARKETPLACE_LOCAL_PATH
    abs_config_path = os.path.abspath(config_path)
    print(f"\n配置文件路径: {config_path}")
    print(f"配置文件绝对路径: {abs_config_path}")
    print(f"配置文件是否存在: {os.path.exists(config_path)}")
    
    # 列出项目根目录中的文件
    print("\n项目根目录中的文件:")
    for item in os.listdir(BASE_DIR):
        print(f"- {item}")
    
    # 尝试不同的路径组合
    possible_paths = [
        BASE_DIR / "marketplace_config.json",
        Path("marketplace_config.json"),
        Path(os.getcwd()) / "marketplace_config.json",
        Path(__file__).parent.parent / "marketplace_config.json"
    ]
    
    print("\n尝试不同的路径组合:")
    for path in possible_paths:
        print(f"路径: {path}")
        print(f"是否存在: {os.path.exists(path)}")

if __name__ == "__main__":
    main() 
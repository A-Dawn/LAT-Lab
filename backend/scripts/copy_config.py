#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复制配置文件到多个可能的位置
"""

import os
import sys
import shutil
from pathlib import Path

# 将项目根目录添加到路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

def main():
    """复制配置文件到多个可能的位置"""
    print("\n" + "="*50)
    print("复制配置文件")
    print("="*50)
    
    # 源文件路径
    source_path = os.path.join(PROJECT_ROOT, "marketplace_config.json")
    
    if not os.path.exists(source_path):
        print(f"错误: 源配置文件不存在: {source_path}")
        return
    
    print(f"源配置文件: {source_path}")
    print(f"文件大小: {os.path.getsize(source_path)} 字节")
    
    # 目标路径列表
    target_paths = [
        # 项目根目录 (已存在)
        source_path,
        
        # src目录
        os.path.join(PROJECT_ROOT, "src", "marketplace_config.json"),
        
        # src/lat_lab目录
        os.path.join(PROJECT_ROOT, "src", "lat_lab", "marketplace_config.json"),
        
        # 当前工作目录
        os.path.join(os.getcwd(), "marketplace_config.json") if os.getcwd() != PROJECT_ROOT else None
    ]
    
    # 过滤掉None值
    target_paths = [p for p in target_paths if p]
    
    # 复制文件到每个目标路径
    for target_path in target_paths:
        if target_path == source_path:
            print(f"跳过源文件: {target_path}")
            continue
        
        try:
            # 确保目标目录存在
            target_dir = os.path.dirname(target_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # 复制文件
            shutil.copy2(source_path, target_path)
            print(f"已复制到: {target_path}")
        except Exception as e:
            print(f"复制到 {target_path} 失败: {str(e)}")
    
    print("\n配置文件已复制到多个可能的位置")
    
    # 列出所有复制的文件
    print("\n验证文件:")
    for target_path in target_paths:
        if os.path.exists(target_path):
            print(f"- {target_path}: {os.path.getsize(target_path)} 字节")
        else:
            print(f"- {target_path}: 不存在")

if __name__ == "__main__":
    main() 
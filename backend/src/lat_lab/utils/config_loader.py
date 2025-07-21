#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件加载器
用于查找和加载配置文件
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# 配置日志
logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置文件加载器"""
    
    def __init__(self):
        """初始化配置加载器"""
        self.last_found_path = None
    
    def get_last_found_path(self) -> Optional[str]:
        """获取最后一次找到的配置文件路径"""
        return self.last_found_path
    
    def find_config_file(self, filename: str, search_paths: Optional[List[str]] = None) -> Optional[str]:
        """
        查找配置文件
        
        Args:
            filename: 配置文件名
            search_paths: 搜索路径列表
            
        Returns:
            Optional[str]: 找到的配置文件路径，如果未找到则返回None
        """
        # 默认搜索路径
        if search_paths is None:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 项目根目录 (假设utils是src/lat_lab/utils)
            project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
            
            search_paths = [
                os.getcwd(),  # 当前工作目录
                project_root,  # 项目根目录
                os.path.join(project_root, "src"),  # src目录
                os.path.join(project_root, "src", "lat_lab"),  # src/lat_lab目录
                os.path.dirname(current_dir),  # utils的父目录
                current_dir,  # 当前目录
            ]
        
        # 搜索配置文件
        for path in search_paths:
            config_path = os.path.join(path, filename)
            if os.path.exists(config_path):
                logger.info(f"找到配置文件: {config_path}")
                # 存储最后找到的配置文件路径
                self.last_found_path = config_path
                return config_path
        
        logger.warning(f"未找到配置文件: {filename}")
        return None
    
    def load_json_config(self, filename: str, search_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        加载JSON配置文件
        
        Args:
            filename: 配置文件名
            search_paths: 搜索路径列表
            
        Returns:
            Dict[str, Any]: 配置数据
        """
        # 查找配置文件
        config_path = self.find_config_file(filename, search_paths)
        if not config_path:
            logger.error(f"无法找到配置文件: {filename}")
            return {}
        
        # 存储找到的配置文件路径
        self.last_found_path = config_path
        
        # 加载JSON文件
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"成功加载配置文件: {config_path}")
            return data
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

# 导出实例
config_loader = ConfigLoader() 
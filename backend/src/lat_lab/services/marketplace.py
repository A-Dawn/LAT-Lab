#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件市场服务
负责从不同来源获取插件市场数据
"""

import os
import json
import time
import logging
import requests
import re
from typing import Dict, List, Any, Optional
from src.lat_lab.core.config import settings
from src.lat_lab.utils.config_loader import config_loader

# 配置日志
logger = logging.getLogger(__name__)

class MarketplaceService:
    """插件市场服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.cache = {}
        self.cache_time = 0
        self.cache_ttl = settings.PLUGIN_MARKETPLACE_CACHE_TTL
        
        # 记录初始化时的路径信息
        logger.info(f"插件市场服务初始化")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"配置文件路径: {settings.PLUGIN_MARKETPLACE_LOCAL_PATH}")
        logger.info(f"配置文件是否存在: {os.path.exists(settings.PLUGIN_MARKETPLACE_LOCAL_PATH)}")
    
    def get_marketplace_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        获取插件市场数据
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            Dict[str, Any]: 插件市场数据
        """
        # 检查缓存是否有效
        current_time = time.time()
        if (not force_refresh and 
            self.cache and 
            current_time - self.cache_time < self.cache_ttl):
            logger.debug("使用缓存的插件市场数据")
            return self.cache
        
        # 根据配置选择数据源
        source = settings.PLUGIN_MARKETPLACE_SOURCE.lower()
        
        if source == "git":
            data = self._get_data_from_git()
        else:  # 默认使用本地文件
            data = self._get_data_from_local()
        
        # 更新缓存
        if data:
            self.cache = data
            self.cache_time = current_time
            logger.info(f"成功加载插件市场数据，共{len(data.get('plugins', []))}个插件")
        else:
            logger.error("加载插件市场数据失败")
        
        return data
    
    def _get_data_from_local(self) -> Dict[str, Any]:
        """从本地文件获取插件市场数据"""
        try:
            # 记录详细的路径信息
            logger.info(f"尝试读取本地配置文件")
            logger.info(f"配置文件路径: {settings.PLUGIN_MARKETPLACE_LOCAL_PATH}")
            logger.info(f"当前工作目录: {os.getcwd()}")
            
            # 首先尝试使用配置中的路径
            local_path = os.path.abspath(settings.PLUGIN_MARKETPLACE_LOCAL_PATH)
            
            # 检查文件是否存在
            if not os.path.exists(local_path):
                logger.warning(f"配置文件不存在: {local_path}，尝试使用配置加载器")
                
                # 使用配置加载器查找配置文件
                data = config_loader.load_json_config("marketplace_config.json")
                if data:
                    # 从加载器获取找到的配置路径
                    found_path = config_loader.get_last_found_path()
                    if found_path:
                        logger.info(f"配置加载器找到配置文件: {found_path}")
                        # 更新配置路径
                        settings.PLUGIN_MARKETPLACE_LOCAL_PATH = found_path
                    return data
                
                # 如果配置加载器也失败，尝试使用data目录
                data_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "marketplace_config.json")
                if os.path.exists(data_config_path):
                    logger.info(f"在data目录找到配置文件: {data_config_path}")
                    # 更新配置路径
                    settings.PLUGIN_MARKETPLACE_LOCAL_PATH = data_config_path
                    
                    # 读取配置文件
                    with open(data_config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return data
                
                # 如果配置文件仍然不存在，则创建默认配置
                logger.warning("未找到配置文件，将创建默认配置")
                data = self._create_default_config()
                if data:
                    return data
                    
                logger.error("无法创建或加载配置文件")
                return {}
            
            # 读取JSON文件
            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 输出一些调试信息
            logger.info(f"从本地文件加载了插件市场数据: {local_path}")
            logger.info(f"市场版本: {data.get('marketplace_info', {}).get('version', '未知')}")
            logger.info(f"插件数量: {len(data.get('plugins', []))}")
            
            return data
        
        except Exception as e:
            logger.error(f"从本地文件加载插件市场数据失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # 尝试创建默认配置
            logger.warning("尝试创建并加载默认配置...")
            try:
                return self._create_default_config()
            except Exception as e2:
                logger.error(f"创建默认配置失败: {str(e2)}")
                return {}
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置文件"""
        try:
            # 默认配置
            default_config = {
                "marketplace_info": {
                    "version": "1.0.0",
                    "last_updated": time.strftime("%Y-%m-%d"),
                    "description": "LAT-LAB插件市场默认配置"
                },
                "categories": [
                    {"id": 1, "name": "工具", "description": "实用工具类插件"},
                    {"id": 2, "name": "增强", "description": "增强博客功能的插件"},
                    {"id": 3, "name": "数据分析", "description": "数据处理和分析类插件"}
                ],
                "tags": ["工具", "增强", "数据分析", "UI增强"],
                "plugins": [
                    {
                        "id": "hello_world",
                        "name": "Hello World",
                        "description": "简单示例插件",
                        "version": "1.0.0",
                        "category_id": 1,
                        "tags": ["工具"],
                        "author": "LAT-LAB",
                        "featured": True,
                        "readme": "# Hello World Plugin\n\n简单示例插件"
                    }
                ]
            }
            
            # 尝试将配置保存到数据目录
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
            os.makedirs(data_dir, exist_ok=True)
            config_path = os.path.join(data_dir, "marketplace_config.json")
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            # 更新配置路径
            settings.PLUGIN_MARKETPLACE_LOCAL_PATH = config_path
            logger.info(f"已创建默认配置文件: {config_path}")
            
            return default_config
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {str(e)}")
            return {}
    
    def _get_data_from_git(self) -> Dict[str, Any]:
        """从Git仓库获取插件市场数据"""
        try:
            repo = settings.PLUGIN_MARKETPLACE_GIT_REPO
            branch = settings.PLUGIN_MARKETPLACE_GIT_BRANCH
            token = settings.PLUGIN_MARKETPLACE_GIT_TOKEN
            
            # 移除可能的前缀
            if repo.startswith('@'):
                repo = repo[1:]
            
            if not repo:
                logger.error("未配置Git仓库地址")
                return {}
            
            # 构建基本数据结构
            marketplace_data = {
                "marketplace_info": {
                    "version": "1.0.0",
                    "last_updated": time.strftime("%Y-%m-%d"),
                    "description": f"从Git仓库 {repo} 加载的插件市场数据"
                },
                "categories": [
                    {"id": 1, "name": "工具", "description": "实用工具类插件"},
                    {"id": 2, "name": "增强", "description": "增强博客功能的插件"},
                    {"id": 3, "name": "数据分析", "description": "数据处理和分析类插件"},
                    {"id": 4, "name": "AI 与机器学习", "description": "人工智能和机器学习相关插件"},
                    {"id": 5, "name": "外部集成", "description": "与外部服务集成的插件"},
                    {"id": 6, "name": "SEO", "description": "搜索引擎优化相关插件"}
                ],
                "tags": [
                    "ai", "seo", "数据可视化", "文件管理", "社交媒体",
                    "安全", "性能优化", "内容处理", "UI增强", "工具",
                    "编辑器", "图像处理", "音频", "视频", "统计",
                    "备份", "导入导出", "通知", "评论增强", "搜索"
                ],
                "plugins": []
            }
            
            # 支持GitHub仓库
            from urllib.parse import urlparse
            
            # 解析URL并验证主机名
            parsed_url = urlparse(repo)
            if parsed_url.hostname == "github.com":
                # 从GitHub URL提取owner和repo
                parts = parsed_url.path.rstrip('/').split('/')
                owner = parts[-2]
                repo_name = parts[-1]
                
                # 先获取仓库内容列表
                api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
                
                # 设置请求头
                headers = {
                    "Accept": "application/vnd.github.v3+json"
                }
                if token:
                    headers["Authorization"] = f"token {token}"
                
                # 发送请求获取仓库内容
                response = requests.get(api_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # 解析仓库内容
                repo_contents = response.json()
                plugin_files = []
                
                # 查找插件文件
                for item in repo_contents:
                    if item["type"] == "file" and item["name"].endswith(".json"):
                        plugin_files.append(item)
                
                logger.info(f"在GitHub仓库中找到 {len(plugin_files)} 个插件文件")
                
                # 加载每个插件文件
                for plugin_file in plugin_files:
                    try:
                        # 获取文件内容
                        file_url = plugin_file["download_url"]
                        file_response = requests.get(file_url, headers=headers, timeout=10)
                        file_response.raise_for_status()
                        
                        # 解析插件数据
                        plugin_data = file_response.json()
                        
                        # 验证插件数据格式
                        if isinstance(plugin_data, dict) and "id" in plugin_data and "name" in plugin_data:
                            # 添加到插件列表
                            marketplace_data["plugins"].append(plugin_data)
                            logger.info(f"加载了插件: {plugin_data.get('name')} (ID: {plugin_data.get('id')})")
                        else:
                            logger.warning(f"插件文件格式不正确: {plugin_file['name']}")
                    
                    except Exception as e:
                        logger.error(f"加载插件文件 {plugin_file['name']} 失败: {str(e)}")
                
                # 如果没有找到单独的插件文件，尝试查找marketplace_config.json
                if not marketplace_data["plugins"]:
                    try:
                        config_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/marketplace_config.json"
                        config_response = requests.get(config_url, headers=headers, timeout=10)
                        config_response.raise_for_status()
                        
                        config_data = config_response.json()
                        if "plugins" in config_data:
                            logger.info(f"从marketplace_config.json加载了 {len(config_data['plugins'])} 个插件")
                            return config_data
                    
                    except Exception as e:
                        logger.error(f"加载marketplace_config.json失败: {str(e)}")
                
                # 返回收集到的插件数据
                logger.info(f"从GitHub仓库加载了 {len(marketplace_data['plugins'])} 个插件")
                return marketplace_data
            
            else:
                logger.error(f"不支持的Git仓库类型: {repo}")
                return {}
        
        except Exception as e:
            logger.error(f"从Git仓库加载插件市场数据失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
    
    def get_plugins(self, category_id: Optional[int] = None, 
                   tags: Optional[List[str]] = None,
                   search_term: Optional[str] = None,
                   featured: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        获取插件列表，支持筛选
        
        Args:
            category_id: 分类ID
            tags: 标签列表
            search_term: 搜索关键词
            featured: 是否精选
            
        Returns:
            List[Dict[str, Any]]: 插件列表
        """
        data = self.get_marketplace_data()
        if not data or "plugins" not in data:
            logger.warning("未找到插件数据或格式不正确")
            return []
        
        plugins = data["plugins"]
        logger.debug(f"筛选前插件数量: {len(plugins)}")
        
        # 应用筛选
        if category_id is not None:
            plugins = [p for p in plugins if p.get("category_id") == category_id]
        
        if tags:
            plugins = [p for p in plugins if any(tag in p.get("tags", []) for tag in tags)]
        
        if featured is not None:
            plugins = [p for p in plugins if p.get("featured") == featured]
        
        if search_term:
            search_term = search_term.lower()
            plugins = [p for p in plugins if 
                      search_term in p.get("name", "").lower() or 
                      search_term in p.get("description", "").lower()]
        
        logger.debug(f"筛选后插件数量: {len(plugins)}")
        return plugins
    
    def get_plugin_by_id(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        通过ID获取插件详情
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            Optional[Dict[str, Any]]: 插件详情，如果不存在则返回None
        """
        data = self.get_marketplace_data()
        if not data or "plugins" not in data:
            return None
        
        for plugin in data["plugins"]:
            if plugin.get("id") == plugin_id:
                return plugin
        
        return None
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        获取所有分类
        
        Returns:
            List[Dict[str, Any]]: 分类列表
        """
        data = self.get_marketplace_data()
        return data.get("categories", [])
    
    def get_tags(self) -> List[str]:
        """
        获取所有标签
        
        Returns:
            List[str]: 标签列表
        """
        data = self.get_marketplace_data()
        return data.get("tags", [])
    
    def get_marketplace_info(self) -> Dict[str, Any]:
        """
        获取市场信息
        
        Returns:
            Dict[str, Any]: 市场信息
        """
        data = self.get_marketplace_data()
        return data.get("marketplace_info", {})
    
    def update_source_settings(self, source: str, git_repo: Optional[str] = None) -> Dict[str, Any]:
        """
        更新插件市场数据源设置
        
        Args:
            source: 数据源类型 ('local' 或 'git')
            git_repo: Git仓库地址 (仅当source为'git'时需要)
            
        Returns:
            Dict[str, Any]: 更新后的设置
        """
        # 验证参数
        if source not in ['local', 'git']:
            raise ValueError("数据源类型必须为 'local' 或 'git'")
        
        if source == 'git' and not git_repo:
            raise ValueError("选择Git数据源时必须提供仓库地址")
        
        # 更新设置
        settings.PLUGIN_MARKETPLACE_SOURCE = source
        
        if source == 'git' and git_repo:
            settings.PLUGIN_MARKETPLACE_GIT_REPO = git_repo
        
        # 清除缓存，强制重新加载
        self.cache = {}
        self.cache_time = 0
        
        # 返回当前设置
        return {
            "source": settings.PLUGIN_MARKETPLACE_SOURCE,
            "git_repo": settings.PLUGIN_MARKETPLACE_GIT_REPO if settings.PLUGIN_MARKETPLACE_SOURCE == 'git' else None,
            "local_path": str(settings.PLUGIN_MARKETPLACE_LOCAL_PATH) if settings.PLUGIN_MARKETPLACE_SOURCE == 'local' else None
        }
    
    def get_source_settings(self) -> Dict[str, Any]:
        """
        获取当前插件市场数据源设置
        
        Returns:
            Dict[str, Any]: 当前设置
        """
        return {
            "source": settings.PLUGIN_MARKETPLACE_SOURCE,
            "git_repo": settings.PLUGIN_MARKETPLACE_GIT_REPO if settings.PLUGIN_MARKETPLACE_SOURCE == 'git' else None,
            "local_path": str(settings.PLUGIN_MARKETPLACE_LOCAL_PATH) if settings.PLUGIN_MARKETPLACE_SOURCE == 'local' else None
        }

# 创建服务实例
marketplace_service = MarketplaceService() 
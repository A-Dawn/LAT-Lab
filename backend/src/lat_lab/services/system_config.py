"""
系统配置服务层
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.lat_lab.models.system import SystemConfig
from src.lat_lab.schemas.system import AboutSectionSchema, SystemConfigCreate, SystemConfigUpdate
from src.lat_lab.core.security import SecurityError

logger = logging.getLogger(__name__)


class SystemConfigService:
    """系统配置服务"""
    
    def __init__(self):
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = timedelta(minutes=5)  # 缓存5分钟
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._cache_timestamps:
            return False
        return datetime.now() - self._cache_timestamps[key] < self._cache_ttl
    
    def _set_cache(self, key: str, value: Any):
        """设置缓存"""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if self._is_cache_valid(key):
            return self._cache.get(key)
        return None
    
    def _clear_cache(self, key: str = None):
        """清除缓存"""
        if key:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
    
    def get_config(self, db: Session, key: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """获取配置"""
        try:
            # 尝试从缓存获取
            if use_cache:
                cached_value = self._get_cache(key)
                if cached_value is not None:
                    return cached_value
            
            # 从数据库查询
            config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
            if not config:
                return None
            
            # 解析JSON值
            try:
                value = json.loads(config.value)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON for config key: {key}")
                raise SecurityError("配置数据格式错误")
            
            # 设置缓存
            if use_cache:
                self._set_cache(key, value)
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting config {key}: {str(e)}")
            raise SecurityError("获取配置失败")
    
    def set_config(self, db: Session, key: str, value: Any, description: str = None) -> bool:
        """设置配置"""
        try:
            # 验证和序列化值
            if isinstance(value, dict) and key == "about_section":
                # 验证关于博主配置
                AboutSectionSchema(**value)
            
            json_value = json.dumps(value, ensure_ascii=False)
            
            # 查询现有配置
            config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
            
            if config:
                # 更新现有配置
                config.value = json_value
                config.updated_at = datetime.utcnow()
                if description:
                    config.description = description
            else:
                # 创建新配置
                config = SystemConfig(
                    key=key,
                    value=json_value,
                    description=description
                )
                db.add(config)
            
            db.commit()
            
            # 清除缓存
            self._clear_cache(key)
            
            logger.info(f"Config {key} updated successfully")
            return True
            
        except IntegrityError:
            db.rollback()
            logger.error(f"Integrity error when setting config {key}")
            raise SecurityError("配置键已存在")
        except Exception as e:
            db.rollback()
            logger.error(f"Error setting config {key}: {str(e)}")
            raise SecurityError("设置配置失败")
    
    def get_about_section(self, db: Session) -> Dict[str, Any]:
        """获取关于博主配置"""
        config = self.get_config(db, "about_section")
        
        if not config:
            # 返回默认配置
            default_config = {
                "title": "关于博主",
                "description": "欢迎来到我的博客！这里记录了我的学习、思考和分享。",
                "social_links": [
                    {"name": "GitHub", "url": "https://github.com", "icon": "github"},
                    {"name": "邮箱", "url": "mailto:example@email.com", "icon": "email"}
                ]
            }
            return default_config
        
        # 数据兼容性处理：支持旧的socialLinks字段
        if "socialLinks" in config and "social_links" not in config:
            config["social_links"] = config["socialLinks"]
            del config["socialLinks"]
        
        return config
    
    def update_about_section(self, db: Session, about_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新关于博主配置"""
        # 数据兼容性处理
        if "socialLinks" in about_data and "social_links" not in about_data:
            about_data["social_links"] = about_data["socialLinks"]
            del about_data["socialLinks"]
        
        # 验证数据
        validated_data = AboutSectionSchema(**about_data).dict()
        
        # 保存配置
        self.set_config(db, "about_section", validated_data, "关于博主区域配置")
        
        return validated_data
    
    def delete_config(self, db: Session, key: str) -> bool:
        """删除配置"""
        try:
            config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
            if not config:
                return False
            
            db.delete(config)
            db.commit()
            
            # 清除缓存
            self._clear_cache(key)
            
            logger.info(f"Config {key} deleted successfully")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting config {key}: {str(e)}")
            raise SecurityError("删除配置失败")


# 创建全局服务实例
system_config_service = SystemConfigService() 
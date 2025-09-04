"""
系统配置相关数据模型
"""

from src.lat_lab.core.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, index=True, nullable=False, comment="配置键")
    value = Column(Text, nullable=False, comment="配置值（JSON格式）")
    description = Column(String(255), nullable=True, comment="配置描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间") 
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .user import Base

class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    code = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False)
    
    # 版本管理
    version = Column(String(20), default="0.1.0")  # 语义化版本号
    
    # 可见性控制
    is_public = Column(Boolean, default=True)  # 是否公开
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 外键
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 关联关系
    creator = relationship("User", back_populates="plugins")

# 保留以下字段注释，这些是数据库中已存在但在代码中不再使用的字段
# Plugin 表的其他字段:
# - category_id = Column(Integer, ForeignKey("plugin_categories.id"))
# - downloads = Column(Integer, default=0)
# - rating = Column(Float, default=0.0)
# - ratings_count = Column(Integer, default=0)
# - config_schema = Column(Text)
# - featured = Column(Boolean, default=False)
# - icon = Column(Text)
# - repository_url = Column(String(255))
# - dependency_info = Column(Text)
#
# 不再使用的相关表:
# - plugin_tags (关联表)
# - plugin_categories
# - plugin_tag_definitions
# - plugin_reviews 
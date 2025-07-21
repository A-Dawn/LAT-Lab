from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.lat_lab.core.config import settings
import os

# 确保data目录存在
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
os.makedirs(data_dir, exist_ok=True)

# 数据库连接
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    """创建数据库和表"""
    # 导入所有模型以便创建表
    from src.lat_lab.models import user, article, category, comment, tag, plugin
    Base.metadata.create_all(bind=engine) 
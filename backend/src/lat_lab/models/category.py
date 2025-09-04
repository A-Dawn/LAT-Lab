from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.lat_lab.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200))
    
    # 关联关系
    articles = relationship("Article", back_populates="category") 
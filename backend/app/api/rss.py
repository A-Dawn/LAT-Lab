from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime
import xml.etree.ElementTree as ET
from app.core.deps import get_db
from app.crud.article import get_articles
from app.core.config import settings

router = APIRouter(prefix="/rss", tags=["rss"])

@router.get("/feed", response_class=Response)
def get_rss_feed(request: Request, db: Session = Depends(get_db)):
    """获取RSS订阅源"""
    # 获取最新文章
    articles = get_articles(db, limit=20, pinned_first=False)
    
    # 创建RSS XML
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    # 频道信息
    ET.SubElement(channel, "title").text = f"{settings.PROJECT_NAME} RSS Feed"
    ET.SubElement(channel, "link").text = str(request.base_url)
    ET.SubElement(channel, "description").text = "个人博客最新文章"
    ET.SubElement(channel, "language").text = "zh-cn"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")
    
    # 添加文章
    for article in articles:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article.title
        ET.SubElement(item, "link").text = f"{request.base_url}articles/{article.id}"
        ET.SubElement(item, "description").text = article.summary or article.content[:200]
        ET.SubElement(item, "pubDate").text = article.created_at.strftime("%a, %d %b %Y %H:%M:%S +0800")
        ET.SubElement(item, "guid").text = f"{request.base_url}articles/{article.id}"
        
        # 添加分类
        if article.category:
            ET.SubElement(item, "category").text = article.category.name
    
    # 转换为XML字符串
    xml_str = ET.tostring(rss, encoding="utf-8", method="xml")
    
    # 返回XML响应
    return Response(
        content=xml_str,
        media_type="application/rss+xml"
    ) 
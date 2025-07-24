from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.lat_lab.schemas.article import Article, ArticleCreate, ArticleUpdate, ArticleDetail, Tag, ArticleStatus, ArticleVisibility
from src.lat_lab.crud.article import get_article, get_articles, create_article, update_article, delete_article, increment_view_count, update_like_count
from src.lat_lab.core.deps import get_db, get_current_user, get_current_author_or_admin
from src.lat_lab.models.user import User, RoleEnum
from src.lat_lab.models.tag import Tag as TagModel
from sqlalchemy import func
from pydantic import BaseModel

router = APIRouter(prefix="/articles", tags=["articles"])

@router.post("/", response_model=Article)
def create_new_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建文章（需要用户登录）"""
    # 检查用户权限（访客不能发布文章）
    if current_user.role == RoleEnum.visitor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="访客不能发布文章"
        )
    
    return create_article(db, article, current_user.id)

@router.get("/", response_model=List[Article])
def read_articles(
    skip: int = 0,
    limit: int = 10,
    author_id: Optional[int] = None,
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    pinned_first: bool = True,
    status: Optional[ArticleStatus] = None,
    visibility: Optional[ArticleVisibility] = None,
    include_drafts: bool = False,
    include_future: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取文章列表，支持分页、按作者/分类/标签筛选、搜索"""
    # 获取当前用户ID（如果已登录）
    current_user_id = current_user.id if current_user else None
    
    # 处理status过滤
    if status:
        # 如果请求草稿文章，确保include_drafts为True
        if status == ArticleStatus.draft:
            include_drafts = True
    
    # 如果当前用户是管理员，可以获取所有可见性的文章
    if current_user and current_user.role == RoleEnum.admin:
        pass  # 管理员可以看到所有文章
    
    # 获取文章列表
    articles = get_articles(
        db, 
        skip=skip, 
        limit=limit, 
        author_id=author_id,
        category_id=category_id,
        tag_name=tag,
        search_query=search,
        pinned_first=pinned_first,
        current_user_id=current_user_id,
        include_drafts=include_drafts,
        include_future=include_future
    )
    return articles

# 定义一个简单的标签响应模型
class TagResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

@router.get("/tags", response_model=List[TagResponse])
def get_all_tags(db: Session = Depends(get_db)):
    """获取所有标签"""
    try:
        tags = db.query(TagModel).all()
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取标签失败: {str(e)}"
        )

@router.get("/me", response_model=List[Article])
def read_user_articles(
    status: Optional[ArticleStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的文章列表，包括草稿"""
    try:
        # 获取当前用户的文章，包括草稿
        articles = get_articles(
            db, 
            author_id=current_user.id, 
            include_drafts=True, 
            include_future=True,
            current_user_id=current_user.id
        )
        
        # 如果指定了状态，进行过滤
        if status:
            articles = [a for a in articles if a.status == status]
        
        # 转换为响应格式
        result = []
        for article in articles:
            article_data = {
                "id": article.id,
                "title": article.title,
                "content": article.content,
                "summary": article.summary,
                "is_pinned": article.is_pinned,
                "category_id": article.category_id,
                "author_id": article.author_id,
                "view_count": article.view_count,
                "likes_count": article.likes_count if article.likes_count is not None else 0,
                "created_at": article.created_at,
                "updated_at": article.updated_at,
                "tags": article.tags,
                "category": article.category,
                "status": article.status,
                "published_at": article.published_at,
                "visibility": article.visibility,
                # 不返回密码
            }
            result.append(article_data)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户文章失败: {str(e)}"
        )

@router.get("/drafts", response_model=List[Article])
def read_user_drafts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的草稿文章"""
    try:
        # 获取当前用户的草稿文章
        articles = get_articles(
            db, 
            author_id=current_user.id, 
            include_drafts=True,
            include_future=True,
            current_user_id=current_user.id
        )
        
        # 仅保留草稿文章
        articles = [a for a in articles if a.status == ArticleStatus.draft]
        
        return articles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取草稿文章失败: {str(e)}"
        )

@router.get("/{article_id}", response_model=ArticleDetail)
def read_article(
    article_id: int,
    password: Optional[str] = None,
    password_hash: Optional[str] = None,
    client_hash: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取文章详情
    
    支持两种密码验证方式：
    1. 传统明文密码 (password参数)
    2. 客户端哈希 (password_hash + client_hash=True)
    """
    article = get_article(db, article_id, current_user.id if current_user else None)
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查是否需要密码
    if article.visibility == ArticleVisibility.password:
        # 检查是否为作者或管理员
        is_author = current_user and current_user.id == article.author_id
        is_admin = current_user and current_user.role == 'admin'
        
        if not (is_author or is_admin):
            # 验证密码
            if not password and not password_hash:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="此文章需要密码访问"
                )
            
            # 处理两种验证方式
            password_correct = False
            
            # 1. 客户端哈希模式
            if password_hash and client_hash:
                # 在服务器端也计算密码哈希
                import hashlib
                import base64
                
                # 计算密码的SHA-256哈希
                server_hash = hashlib.sha256(article.password.encode()).digest()
                server_hash_b64 = base64.b64encode(server_hash).decode()
                
                # 比较哈希值
                password_correct = password_hash == server_hash_b64
            
            # 2. 传统明文密码模式
            elif password:
                password_correct = password == article.password
            
            if not password_correct:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="密码错误"
                )
    
    # 增加浏览量
    increment_view_count(db, article_id, current_user.id if current_user else None)
    
    return article

@router.put("/{article_id}", response_model=Article)
def update_article_by_id(
    article_id: int,
    article_update: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新文章（需要作者或管理员权限）"""
    # 使用修改后的get_article函数，传入当前用户ID以检查权限
    db_article = get_article(db, article_id, current_user.id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="文章不存在或您没有权限查看")
    
    # 检查权限
    if current_user.role != RoleEnum.admin and db_article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有文章作者或管理员可以编辑文章"
        )
    
    # 传递current_user_id参数
    updated_article = update_article(db, article_id, article_update, current_user.id)
    
    # 如果更新失败，抛出500错误
    if updated_article is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新文章失败"
        )
    
    return updated_article

@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article_by_id(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除文章（需要作者或管理员权限）"""
    # 使用修改后的get_article函数，传入当前用户ID以检查权限
    db_article = get_article(db, article_id, current_user.id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="文章不存在或您没有权限查看")
    
    # 检查权限
    if current_user.role != RoleEnum.admin and db_article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有文章作者或管理员可以删除文章"
        )
    
    # 传递current_user_id参数
    success = delete_article(db, article_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除文章失败"
        )
        
    return None

@router.post("/{article_id}/like", response_model=Dict[str, Any])
def like_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """点赞或取消点赞文章（需要用户登录）"""
    # 使用修改后的get_article函数，传入当前用户ID以检查权限
    db_article = get_article(db, article_id, current_user.id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="文章不存在或您没有权限查看")
    
    try:
        # 使用CRUD函数更新点赞数，传递current_user_id参数
        updated_article = update_like_count(db, article_id, increment=True, current_user_id=current_user.id)
        
        if updated_article is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="处理点赞失败"
            )
        
        return {
            "success": True,
            "likes_count": updated_article.likes_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理点赞失败: {str(e)}"
        ) 

@router.post("/{article_id}/publish", response_model=Article)
def publish_article(
    article_id: int,
    publish_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """将草稿文章转为已发布状态（需要作者或管理员权限）"""
    # 使用修改后的get_article函数，传入当前用户ID以检查权限
    db_article = get_article(db, article_id, current_user.id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="文章不存在或您没有权限查看")
    
    # 检查权限
    if current_user.role != RoleEnum.admin and db_article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有文章作者或管理员可以发布文章"
        )
    
    # 如果已经是已发布状态，返回错误
    if db_article.status == ArticleStatus.published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该文章已经是发布状态"
        )
    
    # 更新文章状态为已发布，并设置发布时间
    article_update = ArticleUpdate(
        status=ArticleStatus.published,
        published_at=publish_time or datetime.now()
    )
    
    # 传递current_user_id参数
    updated_article = update_article(db, article_id, article_update, current_user.id)
    
    # 如果更新失败，抛出500错误
    if updated_article is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发布文章失败"
        )
    
    return updated_article 
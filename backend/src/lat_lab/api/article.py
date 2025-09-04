from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.lat_lab.schemas.article import Article, ArticleCreate, ArticleUpdate, ArticleDetail, Tag, ArticleStatus, ArticleVisibility
from src.lat_lab.crud.article import get_article, get_articles, create_article, update_article, delete_article, increment_view_count, update_like_count
from src.lat_lab.core.deps import get_db, get_current_user, get_current_author_or_admin, get_optional_user
from src.lat_lab.models.user import User, RoleEnum
from src.lat_lab.models.tag import Tag as TagModel
from src.lat_lab.models.article import Article as ArticleModel
from sqlalchemy import func, desc
from pydantic import BaseModel

router = APIRouter(prefix="/articles", tags=["articles"])

@router.post("/", response_model=Article)
def create_new_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建文章（需要用户登录且邮箱已验证）"""
    # 检查用户权限（访客不能发布文章）
    if current_user.role == RoleEnum.visitor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="访客不能发布文章"
        )
    
    # 检查邮箱验证状态（未验证邮箱的用户不能发布文章）
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="请先验证您的邮箱后再发布文章"
        )
    
    # 根据用户角色决定是否自动审核通过
    auto_approve = current_user.role == RoleEnum.admin
    
    return create_article(db, article, current_user.id, auto_approve=auto_approve)

@router.get("/", response_model=List[Article], response_model_exclude={"password"})
def read_articles(
    request: Request,
    skip: int = Query(0, ge=0, description="跳过的文章数量"),
    limit: int = Query(10, ge=1, le=1000, description="返回的文章数量"),
    author_id: Optional[int] = Query(None, description="作者ID"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    tag: Optional[str] = Query(None, description="标签名称"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    pinned_first: bool = Query(True, description="是否优先显示置顶文章"),
    status: Optional[ArticleStatus] = Query(None, description="文章状态"),
    visibility: Optional[ArticleVisibility] = Query(None, description="文章可见性"),
    include_drafts: bool = Query(False, description="是否包含草稿"),
    include_future: bool = Query(False, description="是否包含定时发布文章"),
    include_pending: bool = Query(False, description="是否包含待审核文章"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """获取文章列表，支持分页、按作者/分类/标签筛选、搜索"""
    # 获取当前用户ID（如果已登录）
    current_user_id = current_user.id if current_user else None
    
    # 处理status过滤
    if status:
        # 如果请求草稿文章，确保include_drafts为True
        if status == ArticleStatus.draft:
            include_drafts = True
    
    # 仅作者或管理员可以查看草稿列表；其他情况强制不包含草稿
    if not current_user or (current_user.role != RoleEnum.admin and (author_id is None or author_id != current_user.id)):
        include_drafts = False
    
    # 仅管理员可以查看待审核文章列表
    if include_pending and (not current_user or current_user.role != RoleEnum.admin):
        include_pending = False
    
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
        include_future=include_future,
        include_pending=include_pending
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
        from src.lat_lab.utils.security import SecurityError
        SecurityError.log_error_safe(e, "获取标签")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取标签失败"
        )

@router.get("/me", response_model=List[Article], response_model_exclude={"password"})
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
        from src.lat_lab.utils.security import SecurityError
        SecurityError.log_error_safe(e, "获取用户文章", {"user_id": current_user.id if current_user else None})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户文章失败"
        )

@router.get("/drafts", response_model=List[Article], response_model_exclude={"password"})
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
        from src.lat_lab.utils.security import SecurityError
        SecurityError.log_error_safe(e, "获取草稿文章", {"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取草稿文章失败"
        )

# 文章审核相关API端点
@router.get("/pending", response_model=List[Article])
def get_pending_articles(
    skip: int = Query(0, ge=0, description="跳过的文章数量"),
    limit: int = Query(10, ge=1, le=1000, description="返回的文章数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取待审核文章列表（仅管理员）"""
    # 检查管理员权限
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看待审核文章"
        )
    
    # 查询待审核文章
    query = db.query(ArticleModel).filter(ArticleModel.is_approved == False)
    articles = query.order_by(desc(ArticleModel.created_at)).offset(skip).limit(limit).all()
    
    return articles

@router.get("/{article_id}", response_model=ArticleDetail, response_model_exclude={"password"})
def read_article(
    article_id: int,
    request: Request,
    password: Optional[str] = None,
    password_hash: Optional[str] = None,
    client_hash: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
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
    
    # 获取客户端IP地址
    client_ip = request.client.host if request.client else "unknown"
    
    # 增加浏览量
    increment_view_count(db, article_id, current_user.id if current_user else None, client_ip)
    
    # 直接处理author属性，确保它是字典而不是ORM对象
    try:
        if hasattr(article, 'author') and article.author is not None:
            # 创建author字典
            author_obj = article.author
            author_dict = {
                "id": author_obj.id,
                "username": author_obj.username,
                "email": author_obj.email,
                "role": author_obj.role
            }
            
            # 添加可选字段
            if hasattr(author_obj, 'avatar') and author_obj.avatar is not None:
                author_dict["avatar"] = author_obj.avatar
            
            if hasattr(author_obj, 'bio') and author_obj.bio is not None:
                author_dict["bio"] = author_obj.bio
                
            # 替换原始author对象
            article_dict = article.__dict__.copy()
            article_dict['author'] = author_dict
            
            # 移除SQLAlchemy特有属性
            if '_sa_instance_state' in article_dict:
                del article_dict['_sa_instance_state']
                
            # 创建自定义响应对象
            from fastapi.encoders import jsonable_encoder
            from fastapi.responses import JSONResponse
            
            # 在返回前移除敏感字段
            if 'password' in article_dict:
                del article_dict['password']
            
            # 返回自定义JSON响应
            return JSONResponse(content=jsonable_encoder(article_dict))
    except Exception as e:
        print(f"处理author字段时出错: {str(e)}")
    
    # 如果上面的处理失败，尝试正常返回
    return article

@router.put("/{article_id}", response_model=Article)
def update_article_by_id(
    article_id: int,
    article_update: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新文章（需要作者或管理员权限且邮箱已验证）"""
    # 检查邮箱验证状态（未验证邮箱的用户不能编辑文章）
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="请先验证您的邮箱后再编辑文章"
        )
    
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
    """删除文章（需要作者或管理员权限且邮箱已验证）"""
    # 检查邮箱验证状态（未验证邮箱的用户不能删除文章）
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="请先验证您的邮箱后再删除文章"
        )
    
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
    action: Optional[str] = "toggle",  # 'toggle', 'like', 'unlike'
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """点赞或取消点赞文章（需要用户登录）
    
    Args:
        article_id: 文章ID
        action: 
            - toggle: 自动切换点赞状态（默认）
            - like: 强制点赞
            - unlike: 强制取消点赞
    
    Returns:
        点赞状态信息和点赞数量
    """
    # 使用修改后的get_article函数，传入当前用户ID以检查权限
    db_article = get_article(db, article_id, current_user.id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="文章不存在或您没有权限查看")
    
    try:
        # 检查用户是否已点赞该文章
        from src.lat_lab.models.article import article_likes
        has_liked = db.query(article_likes).filter(
            article_likes.c.user_id == current_user.id,
            article_likes.c.article_id == article_id
        ).first() is not None
        
        # 根据action参数决定是点赞还是取消点赞
        increment = False
        if action == "toggle":
            increment = not has_liked  # 如果已点赞则取消，未点赞则添加
        elif action == "like":
            increment = True  # 强制点赞
        elif action == "unlike":
            increment = False  # 强制取消点赞
        
        # 使用CRUD函数更新点赞数，传递current_user_id参数
        updated_article = update_like_count(db, article_id, increment=increment, current_user_id=current_user.id)
        
        if updated_article is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="处理点赞失败"
            )
        
        # 获取更新后的点赞状态
        is_liked = getattr(updated_article, 'current_user_liked', has_liked)
        
        return {
            "success": True,
            "likes_count": updated_article.likes_count,
            "is_liked": is_liked
        }
    except Exception as e:
        db.rollback()
        from src.lat_lab.utils.security import SecurityError
        SecurityError.log_error_safe(e, "处理点赞", {"article_id": article_id, "user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理点赞失败"
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

@router.get("/{article_id}/like-status", response_model=Dict[str, Any])
def get_like_status(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取当前用户对文章的点赞状态
    
    Args:
        article_id: 文章ID
        
    Returns:
        点赞状态信息和点赞数量
    """
    # 获取文章
    db_article = get_article(db, article_id, current_user.id if current_user else None)
    if db_article is None:
        raise HTTPException(status_code=404, detail="文章不存在或您没有权限查看")
    
    # 默认未点赞
    is_liked = False
    
    # 如果用户已登录，检查点赞状态
    if current_user:
        from src.lat_lab.models.article import article_likes
        is_liked = db.query(article_likes).filter(
            article_likes.c.user_id == current_user.id,
            article_likes.c.article_id == article_id
        ).first() is not None
    
    # 返回点赞状态
    return {
        "likes_count": db_article.likes_count or 0,
        "is_liked": is_liked
    }



@router.put("/{article_id}/approve", response_model=Article)
def approve_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """审核通过文章（仅管理员）"""
    # 检查管理员权限
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以审核文章"
        )
    
    # 获取文章
    db_article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查是否已经审核过
    if db_article.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该文章已经审核通过"
        )
    
    # 更新审核状态
    db_article.is_approved = True
    db.commit()
    db.refresh(db_article)
    
    return db_article

@router.put("/{article_id}/reject", response_model=Dict[str, Any])
def reject_article(
    article_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """拒绝文章（仅管理员）"""
    # 检查管理员权限
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以审核文章"
        )
    
    # 获取文章
    db_article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查是否已经审核过
    if db_article.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该文章已经审核通过"
        )
    
    # 删除文章（拒绝即删除）
    db.delete(db_article)
    db.commit()
    
    return {
        "success": True,
        "message": "文章已拒绝",
        "reason": reason
    }

@router.get("/stats/approval", response_model=Dict[str, Any])
def get_approval_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文章审核统计信息（仅管理员）"""
    try:
        # 检查管理员权限
        if current_user.role != RoleEnum.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看审核统计"
            )
        
        # 统计各种状态的文章数量
        total_articles = db.query(ArticleModel).count()
        approved_articles = db.query(ArticleModel).filter(ArticleModel.is_approved == True).count()
        pending_articles = db.query(ArticleModel).filter(ArticleModel.is_approved == False).count()
        
        # 计算审核率，避免除零错误
        approval_rate = 0
        if total_articles > 0:
            approval_rate = round(approved_articles / total_articles * 100, 2)
        
        return {
            "total": total_articles,
            "approved": approved_articles,
            "pending": pending_articles,
            "approval_rate": approval_rate
        }
    except Exception as e:
        # 记录详细错误信息
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"获取审核统计失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"用户ID: {current_user.id if current_user else 'None'}")
        logger.error(f"用户角色: {current_user.role if current_user else 'None'}")
        
        # 返回通用错误信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取审核统计信息失败，请稍后重试"
        ) 
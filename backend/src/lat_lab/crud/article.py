from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from typing import List, Optional
from datetime import datetime
from src.lat_lab.models.article import Article, ArticleStatus, article_likes, ArticleView
from src.lat_lab.models.tag import Tag, article_tags
from src.lat_lab.models.category import Category
from src.lat_lab.schemas.article import ArticleCreate, ArticleUpdate
from src.lat_lab.models.user import User

def get_article(db: Session, article_id: int, current_user_id: Optional[int] = None):
    """
    获取文章详情，添加可见性权限控制
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    
    # 如果文章不存在，直接返回None
    if not article:
        return None
    
    # 确保likes_count有值
    if article and article.likes_count is None:
        article.likes_count = 0
        db.commit()
    
    # 可见性权限控制
    # 如果是草稿，只有作者可以查看
    if article.status == ArticleStatus.draft and (current_user_id is None or article.author_id != current_user_id):
        return None
    
    # 如果是私密文章，只有作者可以查看
    if article.visibility == "private" and (current_user_id is None or article.author_id != current_user_id):
        return None
    
    # 如果文章设置了发布时间，且发布时间在将来，则视为未发布
    if article.published_at and article.published_at > datetime.now() and (current_user_id is None or article.author_id != current_user_id):
        return None
        
    return article

def get_articles(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    author_id: Optional[int] = None,
    category_id: Optional[int] = None,
    tag_name: Optional[str] = None,
    search_query: Optional[str] = None,
    pinned_first: bool = True,
    current_user_id: Optional[int] = None,
    include_drafts: bool = False,
    include_future: bool = False,
    include_pending: bool = False,  # 新增参数：是否包含待审核文章
):
    """
    获取文章列表，添加权限控制和草稿状态过滤
    """
    query = db.query(Article)
    
    # 根据作者过滤
    if author_id:
        query = query.filter(Article.author_id == author_id)
    
    # 根据分类过滤
    if category_id:
        query = query.filter(Article.category_id == category_id)
    
    # 根据标签过滤
    if tag_name:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if tag:
            query = query.join(article_tags).filter(article_tags.c.tag_id == tag.id)
    
    # 搜索功能
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Article.title.like(search_term)) | 
            (Article.content.like(search_term)) |
            (Article.summary.like(search_term))
        )
    
    # 审核状态处理
    if not include_pending:
        # 仅显示已审核文章，除非是作者查看自己的文章
        if current_user_id:
            # 当前用户可以看到自己的待审核文章
            query = query.filter(
                or_(
                    Article.is_approved == True,
                    Article.author_id == current_user_id
                )
            )
        else:
            # 未登录用户只能看到已审核的文章
            query = query.filter(Article.is_approved == True)
    
    # 草稿文章处理
    if not include_drafts:
        # 仅显示已发布文章，除非是作者查看自己的文章
        if current_user_id:
            # 当前用户可以看到自己的草稿
            query = query.filter(
                or_(
                    Article.status == ArticleStatus.published,
                    Article.author_id == current_user_id
                )
            )
        else:
            # 未登录用户只能看到已发布的文章
            query = query.filter(Article.status == ArticleStatus.published)
    
    # 定时发布文章处理
    if not include_future:
        # 仅显示已发布或发布时间早于当前时间的文章，除非是作者
        now = datetime.now()
        if current_user_id:
            # 当前用户可以看到自己的定时发布文章
            query = query.filter(
                or_(
                    Article.published_at == None,
                    Article.published_at <= now,
                    Article.author_id == current_user_id
                )
            )
        else:
            # 未登录用户只能看到已发布的文章
            query = query.filter(
                or_(
                    Article.published_at == None,
                    Article.published_at <= now
                )
            )
    
    # 可见性处理：公开的文章所有人可见，私密或密码保护的文章只有作者可见
    if current_user_id:
        # 登录用户可以看到自己的所有文章和其他人的公开文章
        query = query.filter(
            or_(
                Article.visibility == "public",
                Article.author_id == current_user_id
            )
        )
    else:
        # 未登录用户只能看到公开文章
        query = query.filter(Article.visibility == "public")
    
    # 排序
    if pinned_first:
        query = query.order_by(desc(Article.is_pinned), desc(Article.created_at))
    else:
        query = query.order_by(desc(Article.created_at))
    
    # 获取文章列表
    articles = query.offset(skip).limit(limit).all()
    
    # 确保每篇文章的likes_count都有值
    for article in articles:
        if article.likes_count is None:
            article.likes_count = 0
    
    # 如果有更改，提交到数据库
    if any(article.likes_count is None for article in articles):
        db.commit()
    
    return articles

def create_article(db: Session, article: ArticleCreate, author_id: int, auto_approve: bool = False):
    # 处理发布时间逻辑
    published_at = None
    if article.status == ArticleStatus.published:
        # 如果是发布状态，但没有指定发布时间，则使用当前时间
        published_at = article.published_at or datetime.now()
    else:
        # 如果是草稿状态，发布时间为None
        published_at = article.published_at
    
    # Create article
    db_article = Article(
        title=article.title,
        content=article.content,
        summary=article.summary,
        is_pinned=article.is_pinned,
        category_id=article.category_id,
        author_id=author_id,
        status=article.status,
        published_at=published_at,
        visibility=article.visibility,
        password=article.password,
        is_approved=auto_approve  # 根据auto_approve参数设置审核状态
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    # Add tags
    if article.tags:
        for tag_name in article.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            db_article.tags.append(tag)
        db.commit()
    
    return db_article

def update_article(db: Session, article_id: int, article_update: ArticleUpdate, current_user_id: Optional[int] = None):
    """
    更新文章
    
    Args:
        db: 数据库会话
        article_id: 文章ID
        article_update: 更新数据
        current_user_id: 当前用户ID，用于权限检查
        
    Returns:
        更新后的文章对象，如果文章不存在或无权访问则返回None
    """
    # 使用传入的current_user_id获取文章，同时进行权限检查
    db_article = get_article(db, article_id, current_user_id)
    if not db_article:
        return None
    
    # 处理发布时间逻辑
    if article_update.status is not None:
        if article_update.status == ArticleStatus.published:
            # 如果从草稿变为已发布，且没有设置发布时间，则设为当前时间
            if db_article.status == ArticleStatus.draft and article_update.published_at is None:
                article_update.published_at = datetime.now()
    
    # Update article fields
    update_data = article_update.dict(exclude_unset=True, exclude={"tags"})
    for key, value in update_data.items():
        setattr(db_article, key, value)
    
    # Update tags if provided
    if article_update.tags is not None:
        # Clear existing tags
        db_article.tags = []
        
        # Add new tags
        for tag_name in article_update.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            db_article.tags.append(tag)
    
    try:
        db.commit()
        db.refresh(db_article)
        return db_article
    except Exception as e:
        db.rollback()
        print(f"更新文章失败: {str(e)}")
        return None

def delete_article(db: Session, article_id: int, current_user_id: Optional[int] = None):
    """
    删除文章
    
    Args:
        db: 数据库会话
        article_id: 文章ID
        current_user_id: 当前用户ID，用于权限检查
        
    Returns:
        删除成功返回True，否则返回False
    """
    db_article = get_article(db, article_id, current_user_id)
    if not db_article:
        return False
    
    try:
        db.delete(db_article)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"删除文章失败: {str(e)}")
        return False

def increment_view_count(db: Session, article_id: int, current_user_id: Optional[int] = None, ip_address: str = "unknown"):
    """
    增加文章浏览量（防重复计算）
    
    通过用户ID+IP地址的组合来防止重复计算，确保每个特定的用户+IP组合只计算一次阅读量
    
    Args:
        db: 数据库会话
        article_id: 文章ID
        current_user_id: 当前用户ID，用于权限检查
        ip_address: 客户端IP地址
        
    Returns:
        更新后的文章对象，如果文章不存在或无权访问则返回None
    """
    db_article = get_article(db, article_id, current_user_id)
    if not db_article:
        return None
    
    try:
        # 检查是否已经有相同的用户+IP组合的浏览记录
        existing_view = db.query(ArticleView).filter(
            ArticleView.article_id == article_id,
            ArticleView.user_id == current_user_id,
            ArticleView.ip_address == ip_address
        ).first()
        
        # 如果没有找到相同的记录，则创建新的浏览记录并增加浏览量
        if not existing_view:
            # 创建新的浏览记录
            new_view = ArticleView(
                article_id=article_id,
                user_id=current_user_id,
                ip_address=ip_address
            )
            db.add(new_view)
            
            # 增加文章浏览量
            db_article.view_count += 1
            
            db.commit()
            db.refresh(db_article)
        
        return db_article
    except Exception as e:
        db.rollback()
        print(f"更新浏览量失败: {str(e)}")
        return None

def update_like_count(db: Session, article_id: int, increment: bool = True, current_user_id: Optional[int] = None):
    """
    更新文章点赞数量
    
    Args:
        db: 数据库会话
        article_id: 文章ID  
        increment: True表示点赞，False表示取消点赞
        current_user_id: 当前用户ID，用于权限检查
    
    Returns:
        更新后的文章对象，如果文章不存在或无权访问则返回None
        如果用户已经点过赞，则返回文章对象但不增加点赞数
    """
    db_article = get_article(db, article_id, current_user_id)
    if not db_article or not current_user_id:
        return None
    
    # 获取当前用户对象
    current_user = db.query(User).filter(User.id == current_user_id).first()
    if not current_user:
        return None
    
    # 检查用户是否已点赞
    # 通过查询article_likes表
    like_exists = db.query(article_likes).filter(
        article_likes.c.user_id == current_user_id,
        article_likes.c.article_id == article_id
    ).first() is not None
    
    try:
        # 确保likes_count字段至少为0
        if db_article.likes_count is None:
            db_article.likes_count = 0
        
        # 根据increment参数和当前点赞状态处理
        if increment:
            if not like_exists:  # 如果用户未点赞，添加点赞记录
                # 在article_likes表中添加记录
                stmt = article_likes.insert().values(
                    user_id=current_user_id,
                    article_id=article_id
                )
                db.execute(stmt)
                
                # 更新文章点赞计数
                db_article.likes_count += 1
        else:
            if like_exists:  # 如果用户已点赞，删除点赞记录
                # 从article_likes表中删除记录
                stmt = article_likes.delete().where(
                    article_likes.c.user_id == current_user_id,
                    article_likes.c.article_id == article_id
                )
                db.execute(stmt)
                
                # 更新文章点赞计数，避免负数
                db_article.likes_count = max(0, db_article.likes_count - 1)
        
        db.commit()
        
        # 获取用户是否已点赞此文章的状态
        user_has_liked = db.query(article_likes).filter(
            article_likes.c.user_id == current_user_id,
            article_likes.c.article_id == article_id
        ).first() is not None
        
        # 为文章对象添加临时属性，表示用户是否已点赞
        setattr(db_article, 'current_user_liked', user_has_liked)
        
        return db_article
    except Exception as e:
        db.rollback()
        print(f"更新点赞数失败: {str(e)}")
        return None 
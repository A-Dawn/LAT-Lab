from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from src.lat_lab.schemas.comment import Comment, CommentCreate, CommentUpdate, CommentLike
from src.lat_lab.crud.comment import (
    get_comment, get_comments_by_article, get_comment_replies,
    create_comment, update_comment, delete_comment, like_comment
)
from src.lat_lab.crud.article import get_article
from src.lat_lab.core.deps import get_db, get_current_user, get_current_admin_user, get_optional_user
from src.lat_lab.models.user import User, RoleEnum
from src.lat_lab.models.comment import Comment as CommentModel

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/article/{article_id}", response_model=List[Comment])
def read_article_comments(
    article_id: int,
    request: Request,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """获取文章的评论"""
    # 检查文章是否存在
    article = get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 管理员可以看到未审核的评论
    include_unapproved = current_user and current_user.role == RoleEnum.admin
    
    # 获取评论列表
    comments = get_comments_by_article(
        db, 
        article_id=article_id, 
        skip=skip, 
        limit=limit,
        include_unapproved=include_unapproved
    )
    
    # 构造符合响应模型的数据
    result = []
    for comment in comments:
        # 获取评论回复
        replies_db = get_comment_replies(db, comment.id, include_unapproved)
        
        # 构造回复数据
        replies = []
        for reply in replies_db:
            replies.append({
                "id": reply.id,
                "content": reply.content,
                "article_id": reply.article_id,
                "parent_id": reply.parent_id,
                "user_id": reply.user_id,
                "likes": reply.likes,
                "is_approved": reply.is_approved,
                "created_at": reply.created_at,
                "user": {
                    "id": reply.user.id,
                    "username": reply.user.username,
                    "email": reply.user.email,
                    "role": reply.user.role
                },
                "replies": []
            })
        
        # 构造评论数据
        comment_data = {
            "id": comment.id,
            "content": comment.content,
            "article_id": comment.article_id,
            "parent_id": comment.parent_id,
            "user_id": comment.user_id,
            "likes": comment.likes,
            "is_approved": comment.is_approved,
            "created_at": comment.created_at,
            "user": {
                "id": comment.user.id,
                "username": comment.user.username,
                "email": comment.user.email,
                "role": comment.user.role
            },
            "replies": replies
        }
        
        result.append(comment_data)
    
    return result

@router.get("/{comment_id}/replies", response_model=List[Comment])
def read_comment_replies(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取评论的回复"""
    # 检查评论是否存在
    comment = get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 管理员可以看到未审核的评论
    include_unapproved = current_user.role == RoleEnum.admin
    
    # 获取评论回复
    replies = get_comment_replies(
        db, 
        comment_id=comment_id,
        include_unapproved=include_unapproved
    )
    
    # 构造符合响应模型的数据
    result = []
    for reply in replies:
        reply_data = {
            "id": reply.id,
            "content": reply.content,
            "article_id": reply.article_id,
            "parent_id": reply.parent_id,
            "user_id": reply.user_id,
            "likes": reply.likes,
            "is_approved": reply.is_approved,
            "created_at": reply.created_at,
            "user": {
                "id": reply.user.id,
                "username": reply.user.username,
                "email": reply.user.email,
                "role": reply.user.role
            },
            "replies": []
        }
        result.append(reply_data)
    
    return result

@router.post("/", response_model=Comment)
def create_new_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建评论或回复（需要邮箱已验证）"""
    # 检查邮箱验证状态（未验证邮箱的用户不能创建评论）
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="请先验证您的邮箱后再创建评论"
        )
    
    # 检查文章是否存在
    article = get_article(db, comment.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 如果是回复，检查父评论是否存在
    if comment.parent_id:
        parent_comment = get_comment(db, comment.parent_id)
        if not parent_comment:
            raise HTTPException(status_code=404, detail="父评论不存在")
        
        # 确保父评论属于同一篇文章
        if parent_comment.article_id != comment.article_id:
            raise HTTPException(status_code=400, detail="父评论不属于该文章")
    
    # 管理员和文章作者的评论自动审核通过
    auto_approve = current_user.role == RoleEnum.admin or current_user.id == article.author_id
    
    # 创建评论
    db_comment = create_comment(db, comment, current_user.id, auto_approve=auto_approve)
    
    # 构造符合响应模型的数据
    result = {
        "id": db_comment.id,
        "content": db_comment.content,
        "article_id": db_comment.article_id,
        "parent_id": db_comment.parent_id,
        "user_id": db_comment.user_id,
        "likes": db_comment.likes,
        "is_approved": db_comment.is_approved,
        "created_at": db_comment.created_at,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        },
        "replies": []
    }
    
    return result

@router.put("/{comment_id}", response_model=Comment)
def update_comment_by_id(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新评论（仅评论作者或管理员）"""
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 检查权限（只有评论作者和管理员可以编辑）
    if current_user.id != db_comment.user_id and current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有评论作者或管理员可以编辑评论"
        )
    
    # 普通用户不能修改审核状态
    if comment_update.is_approved is not None and current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以修改评论审核状态"
        )
    
    # 更新评论
    updated_comment = update_comment(db, comment_id, comment_update)
    
    # 构造符合响应模型的数据
    result = {
        "id": updated_comment.id,
        "content": updated_comment.content,
        "article_id": updated_comment.article_id,
        "parent_id": updated_comment.parent_id,
        "user_id": updated_comment.user_id,
        "likes": updated_comment.likes,
        "is_approved": updated_comment.is_approved,
        "created_at": updated_comment.created_at,
        "user": {
            "id": updated_comment.user.id,
            "username": updated_comment.user.username,
            "email": updated_comment.user.email,
            "role": updated_comment.user.role
        },
        "replies": []
    }
    
    return result

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment_by_id(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除评论（仅评论作者或管理员）"""
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 检查权限（只有评论作者和管理员可以删除）
    if current_user.id != db_comment.user_id and current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有评论作者或管理员可以删除评论"
        )
    
    delete_comment(db, comment_id)
    return None

@router.post("/{comment_id}/like", response_model=Comment)
def like_comment_by_id(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """点赞评论"""
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 点赞评论
    liked_comment = like_comment(db, comment_id)
    
    # 构造符合响应模型的数据
    result = {
        "id": liked_comment.id,
        "content": liked_comment.content,
        "article_id": liked_comment.article_id,
        "parent_id": liked_comment.parent_id,
        "user_id": liked_comment.user_id,
        "likes": liked_comment.likes,
        "is_approved": liked_comment.is_approved,
        "created_at": liked_comment.created_at,
        "user": {
            "id": liked_comment.user.id,
            "username": liked_comment.user.username,
            "email": liked_comment.user.email,
            "role": liked_comment.user.role
        },
        "replies": []
    }
    
    return result

@router.get("/", response_model=List[Comment])
def read_all_comments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有评论（仅管理员）"""
    # 查询所有评论，按创建时间倒序排列
    comments = db.query(CommentModel).order_by(CommentModel.created_at.desc()).offset(skip).limit(limit).all()
    
    # 构造符合响应模型的数据
    result = []
    for comment in comments:
        comment_data = {
            "id": comment.id,
            "content": comment.content,
            "article_id": comment.article_id,
            "parent_id": comment.parent_id,
            "user_id": comment.user_id,
            "likes": comment.likes,
            "is_approved": comment.is_approved,
            "created_at": comment.created_at,
            "user": {
                "id": comment.user.id,
                "username": comment.user.username,
                "email": comment.user.email,
                "role": comment.user.role
            },
            "replies": []  # 不加载回复，避免数据量过大
        }
        result.append(comment_data)
    
    return result 
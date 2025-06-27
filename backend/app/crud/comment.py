from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate

def get_comment(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()

def get_comments_by_article(
    db: Session, 
    article_id: int, 
    skip: int = 0, 
    limit: int = 50,
    include_unapproved: bool = False
):
    query = db.query(Comment).filter(
        Comment.article_id == article_id,
        Comment.parent_id == None  # Only get top-level comments
    )
    
    if not include_unapproved:
        query = query.filter(Comment.is_approved == True)
    
    return query.order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()

def get_comment_replies(
    db: Session, 
    comment_id: int, 
    include_unapproved: bool = False
):
    query = db.query(Comment).filter(Comment.parent_id == comment_id)
    
    if not include_unapproved:
        query = query.filter(Comment.is_approved == True)
    
    return query.order_by(Comment.created_at).all()

def create_comment(db: Session, comment: CommentCreate, user_id: int, auto_approve: bool = False):
    db_comment = Comment(
        content=comment.content,
        article_id=comment.article_id,
        user_id=user_id,
        parent_id=comment.parent_id,
        is_approved=auto_approve
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def update_comment(db: Session, comment_id: int, comment_update: CommentUpdate):
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        return None
    
    update_data = comment_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_comment, key, value)
    
    db.commit()
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        return False
    
    db.delete(db_comment)
    db.commit()
    return True

def like_comment(db: Session, comment_id: int):
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        return None
    
    db_comment.likes += 1
    db.commit()
    db.refresh(db_comment)
    return db_comment 
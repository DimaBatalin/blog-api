from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.core.logging import get_logger
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate

logger = get_logger(__name__)


def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
    return (
        db.query(Comment)
        .options(joinedload(Comment.user))
        .filter(Comment.id == comment_id)
        .first()
    )


def get_comments_for_post(
    db: Session, post_id: int, skip: int = 0, limit: int = 50
) -> list[Comment]:
    return (
        db.query(Comment)
        .options(joinedload(Comment.user))
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_comment(
    db: Session, data: CommentCreate, post_id: int, user_id: int
) -> Comment:
    comment = Comment(post_id=post_id, user_id=user_id, text=data.text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    logger.info(
        "Created comment id=%d post_id=%d user_id=%d",
        comment.id, post_id, user_id,
    )
    return comment


def update_comment(db: Session, comment: Comment, data: CommentUpdate) -> Comment:
    comment.text = data.text
    db.commit()
    db.refresh(comment)
    logger.info("Updated comment id=%d", comment.id)
    return comment


def delete_comment(db: Session, comment: Comment) -> None:
    db.delete(comment)
    db.commit()
    logger.info("Deleted comment id=%d", comment.id)

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.like import Like

logger = get_logger(__name__)


def get_like(db: Session, user_id: int, post_id: int) -> Optional[Like]:
    return (
        db.query(Like)
        .filter(Like.user_id == user_id, Like.post_id == post_id)
        .first()
    )


def count_likes(db: Session, post_id: int) -> int:
    return db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar() or 0


def add_like(db: Session, user_id: int, post_id: int) -> Like:
    like = Like(user_id=user_id, post_id=post_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    logger.info("User id=%d liked post id=%d", user_id, post_id)
    return like


def remove_like(db: Session, like: Like) -> None:
    db.delete(like)
    db.commit()
    logger.info("User id=%d unliked post id=%d", like.user_id, like.post_id)

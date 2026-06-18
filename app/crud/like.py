from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.crud.action_log import log_action
from app.models.action_log import ActionType, EntityType
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
    db.flush()
    log_action(
        db,
        entity_type=EntityType.LIKE,
        entity_id=like.id,
        action=ActionType.CREATE,
        user_id=user_id,
        details=f"post_id={post_id}",
    )
    db.commit()
    db.refresh(like)
    logger.info("User id=%d liked post id=%d", user_id, post_id)
    return like


def remove_like(db: Session, like: Like) -> None:
    like_id, user_id, post_id = like.id, like.user_id, like.post_id
    db.delete(like)
    log_action(
        db,
        entity_type=EntityType.LIKE,
        entity_id=like_id,
        action=ActionType.DELETE,
        user_id=user_id,
        details=f"post_id={post_id}",
    )
    db.commit()
    logger.info("User id=%d unliked post id=%d", user_id, post_id)

from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import hash_password, verify_password
from app.crud.action_log import log_action
from app.models.action_log import ActionType, EntityType
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = get_logger(__name__)


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.flush()  # получаем user.id до записи в историю
    log_action(
        db,
        entity_type=EntityType.USER,
        entity_id=user.id,
        action=ActionType.CREATE,
        user_id=user.id,
        details=f"username={user.username}, role={user.role.value}",
    )
    db.commit()
    db.refresh(user)
    logger.info("Created user id=%d username=%s role=%s", user.id, user.username, user.role)
    return user


def update_user(db: Session, user: User, data: UserUpdate, actor_id: int) -> User:
    changes = []
    if data.username is not None:
        changes.append(f"username: {user.username} -> {data.username}")
        user.username = data.username
    if data.password is not None:
        changes.append("password changed")
        user.password_hash = hash_password(data.password)
    if data.role is not None:
        changes.append(f"role: {user.role.value} -> {data.role.value}")
        user.role = data.role

    log_action(
        db,
        entity_type=EntityType.USER,
        entity_id=user.id,
        action=ActionType.UPDATE,
        user_id=actor_id,
        details="; ".join(changes) if changes else None,
    )
    db.commit()
    db.refresh(user)
    logger.info("Updated user id=%d", user.id)
    return user


def delete_user(db: Session, user: User, actor_id: int) -> None:
    user_id, username = user.id, user.username
    db.delete(user)
    log_action(
        db,
        entity_type=EntityType.USER,
        entity_id=user_id,
        action=ActionType.DELETE,
        user_id=actor_id,
        details=f"username={username}",
    )
    db.commit()
    logger.info("Deleted user id=%d", user_id)


def authenticate_user(
    db: Session, username: str, password: str
) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

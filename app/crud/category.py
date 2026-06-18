from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.crud.action_log import log_action
from app.models.action_log import ActionType, EntityType
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = get_logger(__name__)


def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.get(Category, category_id)


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[Category]:
    return db.query(Category).offset(skip).limit(limit).all()


def create_category(db: Session, data: CategoryCreate, actor_id: int) -> Category:
    category = Category(name=data.name)
    db.add(category)
    db.flush()
    log_action(
        db,
        entity_type=EntityType.CATEGORY,
        entity_id=category.id,
        action=ActionType.CREATE,
        user_id=actor_id,
        details=f"name={category.name}",
    )
    db.commit()
    db.refresh(category)
    logger.info("Created category id=%d name=%s", category.id, category.name)
    return category


def update_category(
    db: Session, category: Category, data: CategoryUpdate, actor_id: int
) -> Category:
    old_name = category.name
    category.name = data.name
    log_action(
        db,
        entity_type=EntityType.CATEGORY,
        entity_id=category.id,
        action=ActionType.UPDATE,
        user_id=actor_id,
        details=f"name: {old_name} -> {category.name}",
    )
    db.commit()
    db.refresh(category)
    logger.info("Updated category id=%d", category.id)
    return category


def delete_category(db: Session, category: Category, actor_id: int) -> None:
    category_id, name = category.id, category.name
    db.delete(category)
    log_action(
        db,
        entity_type=EntityType.CATEGORY,
        entity_id=category_id,
        action=ActionType.DELETE,
        user_id=actor_id,
        details=f"name={name}",
    )
    db.commit()
    logger.info("Deleted category id=%d", category_id)

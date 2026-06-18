from typing import Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = get_logger(__name__)


def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.get(Category, category_id)


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[Category]:
    return db.query(Category).offset(skip).limit(limit).all()


def create_category(db: Session, data: CategoryCreate) -> Category:
    category = Category(name=data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    logger.info("Created category id=%d name=%s", category.id, category.name)
    return category


def update_category(db: Session, category: Category, data: CategoryUpdate) -> Category:
    category.name = data.name
    db.commit()
    db.refresh(category)
    logger.info("Updated category id=%d", category.id)
    return category


def delete_category(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()
    logger.info("Deleted category id=%d", category.id)

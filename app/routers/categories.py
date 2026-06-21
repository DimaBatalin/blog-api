from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.category import (
    create_category,
    delete_category,
    get_categories,
    get_category,
    get_category_by_name,
    update_category,
)
from app.models.user import User, UserRole
from app.routers.deps import require_role
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Категории"])


@router.get("/", response_model=list[CategoryResponse], summary="Список категорий")
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse, summary="Категория по ID")
def get_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    cat = get_category(db, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    return cat


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание категории (только Moderator)",
)
def create_category_endpoint(
    data: CategoryCreate,
    current_user: User = Depends(require_role(UserRole.MODERATOR)),
    db: Session = Depends(get_db),
):
    if get_category_by_name(db, data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким названием уже существует",
        )
    return create_category(db, data, actor_id=current_user.id)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Обновление категории (только Moderator)",
)
def update_category_endpoint(
    category_id: int,
    data: CategoryUpdate,
    current_user: User = Depends(require_role(UserRole.MODERATOR)),
    db: Session = Depends(get_db),
):
    cat = get_category(db, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    existing = get_category_by_name(db, data.name)
    if existing and existing.id != category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким названием уже существует",
        )
    return update_category(db, cat, data, actor_id=current_user.id)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление категории (только Moderator)",
)
def delete_category_endpoint(
    category_id: int,
    current_user: User = Depends(require_role(UserRole.MODERATOR)),
    db: Session = Depends(get_db),
):
    cat = get_category(db, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    delete_category(db, cat, actor_id=current_user.id)

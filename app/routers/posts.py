from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.crud.like import count_likes
from app.crud.post import create_post, delete_post, get_post, get_posts, update_post
from app.models.post import PostStatus
from app.models.user import User, UserRole
from app.routers.deps import get_current_user, require_role
from app.schemas.post import (
    PaginatedPostsResponse,
    PostCreate,
    PostDetailResponse,
    PostResponse,
    PostUpdate,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/posts", tags=["Статьи"])


@router.get(
    "/",
    response_model=PaginatedPostsResponse,
    summary="Список статей с пагинацией, фильтрацией и сортировкой",
)
def list_posts(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    category: Optional[str] = Query(None, description="Фильтр по названию категории"),
    status: Optional[PostStatus] = Query(None, description="Фильтр по статусу"),
    sort_by: Optional[str] = Query(
        None, pattern="^(popular|newest)$", description="Сортировка: 'popular' или 'newest'"
    ),
    db: Session = Depends(get_db),
):
    result = get_posts(
        db,
        page=page,
        limit=limit,
        category=category,
        status=status,
        sort_by=sort_by,
    )
    return result


@router.get(
    "/{post_id}",
    response_model=PostDetailResponse,
    summary="Статья по ID",
)
def get_post_endpoint(post_id: int, db: Session = Depends(get_db)):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена")
    post.likes_count = count_likes(db, post_id)
    return post


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание статьи (только Author)",
)
def create_post_endpoint(
    data: PostCreate,
    current_user: User = Depends(require_role(UserRole.AUTHOR, UserRole.MODERATOR)),
    db: Session = Depends(get_db),
):
    return create_post(db, data, author_id=current_user.id)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Обновление статьи (Author — только своя, Moderator — любая)",
)
def update_post_endpoint(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена")
    _check_post_ownership(current_user, post)
    return update_post(db, post, data, actor_id=current_user.id)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление статьи (Author — только своя, Moderator — любая)",
)
def delete_post_endpoint(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена")
    _check_post_ownership(current_user, post)
    delete_post(db, post, actor_id=current_user.id)


def _check_post_ownership(current_user: User, post) -> None:
    """Модератору разрешено всё; автору — только собственные статьи."""
    if current_user.role == UserRole.MODERATOR:
        return
    if current_user.role == UserRole.AUTHOR and post.author_id == current_user.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав для изменения этой статьи",
    )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.comment import (
    create_comment,
    delete_comment,
    get_comment,
    get_comments_for_post,
    update_comment,
)
from app.crud.post import get_post
from app.models.user import User, UserRole
from app.routers.deps import get_current_user
from app.schemas.comment import CommentCreate, CommentDetailResponse, CommentUpdate

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["Комментарии"])


def _get_existing_post(post_id: int, db: Session):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена")
    return post


@router.get(
    "/",
    response_model=list[CommentDetailResponse],
    summary="Список комментариев к статье",
)
def list_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    _get_existing_post(post_id, db)
    return get_comments_for_post(db, post_id, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=CommentDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавление комментария к статье (для аутентифицированных)",
)
def add_comment(
    post_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_existing_post(post_id, db)
    comment = create_comment(db, data, post_id=post_id, user_id=current_user.id)
    return get_comment(db, comment.id)


@router.put(
    "/{comment_id}",
    response_model=CommentDetailResponse,
    summary="Изменение комментария (автор — только свой, Moderator — любой)",
)
def edit_comment(
    post_id: int,
    comment_id: int,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_existing_post(post_id, db)
    comment = get_comment(db, comment_id)
    if not comment or comment.post_id != post_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден")
    _check_comment_ownership(current_user, comment)
    return update_comment(db, comment, data, actor_id=current_user.id)


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление комментария (автор — только свой, Moderator — любой)",
)
def remove_comment(
    post_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_existing_post(post_id, db)
    comment = get_comment(db, comment_id)
    if not comment or comment.post_id != post_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден")
    _check_comment_ownership(current_user, comment)
    delete_comment(db, comment, actor_id=current_user.id)


def _check_comment_ownership(current_user: User, comment) -> None:
    if current_user.role == UserRole.MODERATOR:
        return
    if comment.user_id == current_user.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав для изменения этого комментария",
    )

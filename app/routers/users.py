from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.crud.user import delete_user, get_user, get_users, update_user
from app.models.user import User, UserRole
from app.routers.deps import get_current_user, require_role
from app.schemas.user import UserResponse, UserUpdate

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Профиль текущего пользователя",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Список всех пользователей (только Moderator)",
    dependencies=[Depends(require_role(UserRole.MODERATOR))],
)
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Пользователь по ID",
)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Обновление пользователя (сам пользователь или Moderator)",
)
def patch_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    # Изменять чужой профиль или роль может только модератор
    if current_user.id != user_id and current_user.role != UserRole.MODERATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    if data.role is not None and current_user.role != UserRole.MODERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Изменять роль может только Moderator",
        )
    return update_user(db, user, data, actor_id=current_user.id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление пользователя (сам пользователь или Moderator)",
)
def remove_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if current_user.id != user_id and current_user.role != UserRole.MODERATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
    delete_user(db, user, actor_id=current_user.id)

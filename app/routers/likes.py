from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.like import add_like, count_likes, get_like, remove_like
from app.crud.post import get_post
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.like import LikeStatusResponse

router = APIRouter(prefix="/posts/{post_id}/likes", tags=["Likes"])


@router.post(
    "/",
    response_model=LikeStatusResponse,
    summary="Like a post (toggle: like if not liked, unlike if already liked)",
)
def toggle_like(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing = get_like(db, user_id=current_user.id, post_id=post_id)
    if existing:
        remove_like(db, existing)
        liked = False
    else:
        try:
            add_like(db, user_id=current_user.id, post_id=post_id)
            liked = True
        except IntegrityError:
            db.rollback()
            liked = True  # race condition – already liked

    return LikeStatusResponse(liked=liked, likes_count=count_likes(db, post_id))


@router.get(
    "/",
    response_model=LikeStatusResponse,
    summary="Get like status for current user on a post",
)
def like_status(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    existing = get_like(db, user_id=current_user.id, post_id=post_id)
    return LikeStatusResponse(
        liked=existing is not None,
        likes_count=count_likes(db, post_id),
    )

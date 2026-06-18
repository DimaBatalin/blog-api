import math
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.logging import get_logger
from app.models.category import Category
from app.models.like import Like
from app.models.post import Post, PostStatus
from app.schemas.post import PostCreate, PostUpdate

logger = get_logger(__name__)


def get_post(db: Session, post_id: int) -> Optional[Post]:
    return (
        db.query(Post)
        .options(joinedload(Post.author), joinedload(Post.category))
        .filter(Post.id == post_id)
        .first()
    )


def get_posts(
    db: Session,
    page: int = 1,
    limit: int = 10,
    category: Optional[str] = None,
    status: Optional[PostStatus] = None,
    sort_by: Optional[str] = None,
    author_id: Optional[int] = None,
) -> dict:
    query = db.query(Post).options(
        joinedload(Post.author), joinedload(Post.category)
    )

    if category:
        query = query.join(Category).filter(Category.name == category)
    if status:
        query = query.filter(Post.status == status)
    if author_id is not None:
        query = query.filter(Post.author_id == author_id)

    # Sorting
    if sort_by == "popular":
        likes_subq = (
            db.query(Like.post_id, func.count(Like.id).label("likes_count"))
            .group_by(Like.post_id)
            .subquery()
        )
        query = query.outerjoin(
            likes_subq, Post.id == likes_subq.c.post_id
        ).order_by(func.coalesce(likes_subq.c.likes_count, 0).desc())
    else:
        query = query.order_by(Post.created_at.desc())

    total = query.count()
    pages = max(1, math.ceil(total / limit))
    items = query.offset((page - 1) * limit).limit(limit).all()

    # Attach likes_count to each post instance manually
    post_ids = [p.id for p in items]
    likes_counts = {}
    if post_ids:
        rows = (
            db.query(Like.post_id, func.count(Like.id))
            .filter(Like.post_id.in_(post_ids))
            .group_by(Like.post_id)
            .all()
        )
        likes_counts = {row[0]: row[1] for row in rows}

    for post in items:
        post.likes_count = likes_counts.get(post.id, 0)

    return {"total": total, "page": page, "limit": limit, "pages": pages, "items": items}


def create_post(db: Session, data: PostCreate, author_id: int) -> Post:
    published_at = None
    if data.status == PostStatus.PUBLISHED:
        published_at = datetime.now(timezone.utc)

    post = Post(
        author_id=author_id,
        title=data.title,
        content=data.content,
        status=data.status,
        category_id=data.category_id,
        published_at=published_at,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    post.likes_count = 0
    logger.info("Created post id=%d author_id=%d", post.id, author_id)
    return post


def update_post(db: Session, post: Post, data: PostUpdate) -> Post:
    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content
    if data.status is not None:
        if data.status == PostStatus.PUBLISHED and post.status == PostStatus.DRAFT:
            post.published_at = datetime.now(timezone.utc)
        post.status = data.status
    if data.category_id is not None:
        post.category_id = data.category_id

    post.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(post)
    # Re-fetch likes count
    post.likes_count = (
        db.query(func.count(Like.id)).filter(Like.post_id == post.id).scalar() or 0
    )
    logger.info("Updated post id=%d", post.id)
    return post


def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()
    logger.info("Deleted post id=%d", post.id)

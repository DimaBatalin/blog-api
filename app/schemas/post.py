from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.post import PostStatus
from app.schemas.category import CategoryResponse
from app.schemas.user import UserResponse


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    content: str = Field(..., min_length=1)
    status: PostStatus = PostStatus.DRAFT
    category_id: Optional[int] = None


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    content: Optional[str] = Field(None, min_length=1)
    status: Optional[PostStatus] = None
    category_id: Optional[int] = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    status: PostStatus
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    author_id: int
    category_id: Optional[int]
    likes_count: int = 0


class PostDetailResponse(PostResponse):
    author: UserResponse
    category: Optional[CategoryResponse] = None


class PaginatedPostsResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    items: list[PostResponse]

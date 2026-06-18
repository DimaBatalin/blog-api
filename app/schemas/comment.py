from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    user_id: int
    text: str
    created_at: datetime


class CommentDetailResponse(CommentResponse):
    user: UserResponse

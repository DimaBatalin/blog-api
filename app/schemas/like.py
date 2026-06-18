from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    post_id: int
    created_at: datetime


class LikeStatusResponse(BaseModel):
    liked: bool
    likes_count: int

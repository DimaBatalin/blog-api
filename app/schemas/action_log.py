from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.action_log import ActionType, EntityType


class ActionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: EntityType
    entity_id: int
    action: ActionType
    user_id: Optional[int]
    details: Optional[str]
    created_at: datetime


class PaginatedActionLogsResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    items: list[ActionLogResponse]

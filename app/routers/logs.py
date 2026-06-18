from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.action_log import get_logs
from app.models.action_log import ActionType, EntityType
from app.models.user import UserRole
from app.routers.deps import require_role
from app.schemas.action_log import PaginatedActionLogsResponse

router = APIRouter(prefix="/logs", tags=["Action Logs"])


@router.get(
    "/",
    response_model=PaginatedActionLogsResponse,
    summary="История действий над сущностями (Moderator only)",
    dependencies=[Depends(require_role(UserRole.MODERATOR))],
)
def list_action_logs(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    entity_type: Optional[EntityType] = Query(
        None, description="Фильтр по типу сущности"
    ),
    action: Optional[ActionType] = Query(
        None, description="Фильтр по типу действия"
    ),
    user_id: Optional[int] = Query(
        None, description="Фильтр по ID пользователя-инициатора"
    ),
    db: Session = Depends(get_db),
):
    return get_logs(
        db,
        page=page,
        limit=limit,
        entity_type=entity_type,
        action=action,
        user_id=user_id,
    )

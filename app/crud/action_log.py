import math
from typing import Optional

from sqlalchemy.orm import Session

from app.models.action_log import ActionLog, ActionType, EntityType


def log_action(
    db: Session,
    entity_type: EntityType,
    entity_id: int,
    action: ActionType,
    user_id: Optional[int] = None,
    details: Optional[str] = None,
) -> ActionLog:
    """
    Добавляет запись в постоянную историю действий.

    Намеренно НЕ вызывает db.commit() — запись добавляется в ту же
    транзакцию, что и изменение самой сущности (через db.add), чтобы
    операция и запись в историю были атомарны: либо сохраняются обе,
    либо обе откатываются при ошибке.
    """
    entry = ActionLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id=user_id,
        details=details,
    )
    db.add(entry)
    return entry


def get_logs(
    db: Session,
    page: int = 1,
    limit: int = 20,
    entity_type: Optional[EntityType] = None,
    action: Optional[ActionType] = None,
    user_id: Optional[int] = None,
) -> dict:
    query = db.query(ActionLog)

    if entity_type:
        query = query.filter(ActionLog.entity_type == entity_type)
    if action:
        query = query.filter(ActionLog.action == action)
    if user_id is not None:
        query = query.filter(ActionLog.user_id == user_id)

    query = query.order_by(ActionLog.created_at.desc())

    total = query.count()
    pages = max(1, math.ceil(total / limit))
    items = query.offset((page - 1) * limit).limit(limit).all()

    return {"total": total, "page": page, "limit": limit, "pages": pages, "items": items}

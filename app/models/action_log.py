import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ActionType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class EntityType(str, enum.Enum):
    USER = "User"
    CATEGORY = "Category"
    POST = "Post"
    COMMENT = "Comment"
    LIKE = "Like"


class ActionLog(Base):
    """
    Постоянная история действий над основными сущностями платформы.

    В отличие от вывода модуля `logging` (который пишется в stdout/файл и
    теряется при перезапуске, если не примонтирован отдельный volume), эта
    таблица хранится в той же БД, что и сами сущности, и доступна для
    просмотра через защищённый эндпоинт GET /api/logs.
    """

    __tablename__ = "action_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType), nullable=False, index=True
    )
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    action: Mapped[ActionType] = mapped_column(
        Enum(ActionType), nullable=False, index=True
    )
    # SET NULL, а не CASCADE: если пользователь-инициатор будет удалён,
    # сама запись истории не должна пропадать — теряется только привязка к автору.
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    user = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<ActionLog {self.action} {self.entity_type}#{self.entity_id} "
            f"by user_id={self.user_id}>"
        )

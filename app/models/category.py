from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )

    # Relationships
    posts = relationship("Post", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name}>"

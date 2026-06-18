from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user import UserRole


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.READER

    @field_validator("username")
    @classmethod
    def username_lower(cls, v: str) -> str:
        return v.lower()

    @field_validator("role")
    @classmethod
    def forbid_self_assigned_moderator(cls, v: UserRole) -> UserRole:
        """
        Привилегированную роль Moderator нельзя получить через публичную
        регистрацию — иначе любой пользователь мог бы выдать себе полные
        права на управление платформой. Повысить пользователя до Moderator
        может только существующий Moderator через PATCH /users/{id}.
        """
        if v == UserRole.MODERATOR:
            raise ValueError(
                "Роль 'Moderator' недоступна при самостоятельной регистрации. "
                "Она выдаётся существующим модератором через PATCH /users/{id}."
            )
        return v


class UserUpdate(BaseModel):
    username: str | None = Field(
        None, min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_]+$"
    )
    password: str | None = Field(None, min_length=6, max_length=128)
    role: UserRole | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str

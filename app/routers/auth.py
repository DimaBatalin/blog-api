from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import create_access_token
from app.crud.user import authenticate_user, create_user, get_user_by_username
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Это имя пользователя уже занято",
        )
    user = create_user(db, data)
    logger.info("Зарегистрирован пользователь username=%s", user.username)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Получение JWT-токена",
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    logger.info("Пользователь id=%d вошёл в систему", user.id)
    return TokenResponse(access_token=token)

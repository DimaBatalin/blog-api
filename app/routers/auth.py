from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import create_access_token
from app.crud.user import authenticate_user, create_user, get_user_by_username
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    user = create_user(db, data)
    logger.info("Registered user username=%s", user.username)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtain JWT access token",
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    logger.info("User id=%d logged in", user.id)
    return TokenResponse(access_token=token)
